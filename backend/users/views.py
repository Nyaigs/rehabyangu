from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from authorization.models import Permission, Role
from authorization.permissions import HasPermission
from .models import AuditLog, TenantMembership
from .services import audit, create_invitation
from .permissions import IsInTenant
from .serializers import AuditLogSerializer


def can_manage_staff(request):
    membership = getattr(request, 'tenant_membership', None)
    return request.user.is_superuser or bool(membership and membership.is_rehab_admin)


def invalidate_permissions(user_id, tenant_id):
    cache.delete(f'user_perms_{user_id}_{tenant_id}')
    cache.delete(f'user_perms_{user_id}_global')


def serialize_membership(membership):
    user = membership.user
    roles = list(membership.roles.prefetch_related('permissions').all())
    role_permissions = sorted({codename for role in roles for codename in role.permissions.values_list('codename', flat=True)})
    extra = sorted(membership.extra_permissions.values_list('codename', flat=True))
    return {
        'id': user.id, 'membership_id': membership.id, 'tenant_user_id': membership.tenant_user_id,
        'username': user.username, 'email': user.email, 'first_name': user.first_name,
        'last_name': user.last_name, 'full_name': f'{user.first_name} {user.last_name}'.strip(),
        'role': membership.role, 'roles': [{'id': role.id, 'name': role.name} for role in roles],
        'role_permissions': role_permissions, 'extra_permissions': extra,
        'effective_permissions': sorted(set(role_permissions) | set(extra)),
        'is_rehab_admin': membership.is_rehab_admin, 'is_active': user.is_active,
    }


def resolve_roles(value, tenant):
    """Accept role ids, role names, or the legacy role slug from the invite UI."""
    if not value:
        return []
    values = value if isinstance(value, list) else [value]
    resolved = []
    for item in values:
        query = Q(id=item) if isinstance(item, int) or (isinstance(item, str) and item.isdigit()) else Q(name__iexact=str(item).replace('_', ' '))
        role = Role.objects.filter(query).filter(Q(tenant=tenant) | Q(tenant__isnull=True)).first()
        if not role:
            raise ValueError(f'Role "{item}" was not found for this tenant.')
        resolved.append(role)
    return resolved


def resolve_permissions(value):
    if value is None:
        return None
    values = value if isinstance(value, list) else [value]
    permissions = list(Permission.objects.filter(Q(id__in=values) | Q(codename__in=values)))
    if len(permissions) != len(set(map(str, values))):
        raise ValueError('One or more extra permissions are invalid.')
    return permissions


class StaffListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('staff.read')]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({'error': 'No tenant context'}, status=status.HTTP_403_FORBIDDEN)
        memberships = TenantMembership.objects.filter(tenant=tenant).select_related('user').prefetch_related('roles__permissions', 'extra_permissions')
        return Response([serialize_membership(membership) for membership in memberships])


class CreateStaffView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('staff.invite')]

    def post(self, request):
        tenant = request.tenant
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'email': ['Email is required.']}, status=status.HTTP_400_BAD_REQUEST)
        try:
            roles = resolve_roles(request.data.get('roles') or request.data.get('role'), tenant)
            extras = resolve_permissions(request.data.get('extra_permissions', []))
        except ValueError as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        if not roles:
            default_role = Role.objects.filter(tenant=tenant, name='Staff Member').first()
            if not default_role:
                return Response({'error': 'Tenant roles have not been provisioned.'}, status=status.HTTP_409_CONFLICT)
            roles = [default_role]
        if extras:
            return Response({'error': 'Extra permissions can be assigned after the invitation is accepted.'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            invitation = create_invitation(tenant=tenant, email=email, invited_by=request.user, roles=roles,
                legacy_role=request.data.get('role', 'other'), first_name=request.data.get('first_name', ''), last_name=request.data.get('last_name', ''))
            audit(actor=request.user, tenant=tenant, action='CREATE', request=request, description=f'Invited staff member {email}.')
        return Response({'message': 'Staff invitation sent successfully.', 'invitation_id': invitation.id, 'email': invitation.email}, status=status.HTTP_201_CREATED)


class StaffDetailView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('staff.manage')]

    def put(self, request, pk):
        try:
            membership = TenantMembership.objects.select_related('user').get(tenant=request.tenant, user_id=pk)
        except TenantMembership.DoesNotExist:
            return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            roles = resolve_roles(request.data.get('roles') or request.data.get('role'), request.tenant) if ('roles' in request.data or 'role' in request.data) else None
            extras = resolve_permissions(request.data.get('extra_permissions'))
        except ValueError as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for field in ('email', 'first_name', 'last_name'):
                if field in request.data:
                    setattr(membership.user, field, request.data[field])
            if 'is_active' in request.data:
                membership.user.is_active = bool(request.data['is_active'])
            membership.user.save()
            if 'role' in request.data:
                membership.role = request.data['role']
                membership.save(update_fields=['role'])
            if roles is not None:
                membership.roles.set(roles)
            if extras is not None:
                membership.extra_permissions.set(extras)
        invalidate_permissions(membership.user_id, request.tenant.id)
        membership.refresh_from_db()
        return Response({'message': 'Staff member updated successfully', 'user': serialize_membership(membership)})


class TenantAuditLogView(ListAPIView):
    serializer_class = AuditLogSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('role.read')]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        return AuditLog.objects.filter(tenant=tenant).order_by('-timestamp')[:1000] if tenant else AuditLog.objects.none()
