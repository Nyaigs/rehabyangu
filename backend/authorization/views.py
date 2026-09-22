from django.db.models import Q
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import HasPermission

from .models import Permission, Role
from .utils import get_user_permissions
from users.services import audit


def is_rehab_admin(request):
    membership = getattr(request, 'tenant_membership', None)
    return request.user.is_superuser or bool(membership and membership.is_rehab_admin)


def invalidate_role_members(role):
    for user_id, tenant_id in role.memberships.values_list('user_id', 'tenant_id'):
        cache.delete(f'user_perms_{user_id}_{tenant_id}')


class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permissions = get_user_permissions(request.user, getattr(request, 'tenant', None))
        return Response({'permissions': sorted(permissions)})


class PermissionListView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('role.read')]

    def get(self, request):
        return Response(list(Permission.objects.order_by('category', 'name').values('id', 'codename', 'name', 'category')))


class RoleListView(APIView):
    def get_permissions(self):
        # Creating a role needs the stronger permission, while listing roles
        # is safe for users who can inspect the available access model.
        codename = 'role.manage' if self.request.method == 'POST' else 'role.read'
        return [IsAuthenticated(), HasPermission(codename)]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        roles = Role.objects.filter(Q(tenant=tenant) | Q(tenant__isnull=True)).prefetch_related('permissions')
        return Response([{
            'id': role.id,
            'name': role.name,
            'permissions': list(role.permissions.values_list('codename', flat=True)),
        } for role in roles.order_by('name')])

    def post(self, request):
        name = str(request.data.get('name', '')).strip()
        codenames = request.data.get('permissions', [])
        if not name or not isinstance(codenames, list):
            return Response({'error': 'name and permissions[] are required.'}, status=400)
        permissions = list(Permission.objects.filter(codename__in=codenames))
        if len(permissions) != len(set(codenames)):
            return Response({'error': 'One or more permission keys are invalid.'}, status=400)
        role, created = Role.objects.get_or_create(tenant=request.tenant, name=name)
        if not created:
            return Response({'error': 'A role with this name already exists.'}, status=409)
        role.permissions.set(permissions)
        invalidate_role_members(role)
        audit(actor=request.user, tenant=request.tenant, action='CREATE', request=request, description=f'Created role {name}.')
        return Response({'id': role.id, 'name': role.name, 'permissions': sorted(codenames)}, status=201)


class RoleDetailView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('role.manage')]

    def put(self, request, pk):
        role = Role.objects.filter(id=pk, tenant=request.tenant).first()
        if not role:
            return Response({'error': 'Tenant role not found.'}, status=404)
        codenames = request.data.get('permissions', [])
        if not isinstance(codenames, list):
            return Response({'error': 'permissions must be a list.'}, status=400)
        permissions = list(Permission.objects.filter(codename__in=codenames))
        if len(permissions) != len(set(codenames)):
            return Response({'error': 'One or more permission keys are invalid.'}, status=400)
        name = request.data.get('name')
        if name is not None:
            role.name = str(name).strip()
            if not role.name:
                return Response({'error': 'Role name cannot be blank.'}, status=400)
            role.save(update_fields=['name'])
        role.permissions.set(permissions)
        invalidate_role_members(role)
        audit(actor=request.user, tenant=request.tenant, action='UPDATE', request=request, description=f'Updated role {role.name}.')
        return Response({'id': role.id, 'name': role.name, 'permissions': sorted(codenames)})
