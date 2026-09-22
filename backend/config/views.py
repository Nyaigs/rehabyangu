from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.http import FileResponse, Http404
from rest_framework import serializers, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import TenantMembership
from users.permissions import IsInTenant
from authorization.permissions import HasPermission

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_rehab_admin = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'role', 'is_rehab_admin', 'tenant_name']

    def get_role(self, obj):
        membership = getattr(self.context.get('request'), 'tenant_membership', None)
        return membership.role if membership and membership.user_id == obj.id else None

    def get_is_rehab_admin(self, obj):
        membership = getattr(self.context.get('request'), 'tenant_membership', None)
        return bool(membership and membership.user_id == obj.id and membership.is_rehab_admin)

    def get_tenant_name(self, obj):
        membership = getattr(self.context.get('request'), 'tenant_membership', None)
        return membership.tenant.name if membership and membership.user_id == obj.id else None

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsInTenant]

    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsInTenant(), HasPermission('staff.read')]

    def get_queryset(self):
        return User.objects.filter(
            tenant_memberships__tenant=self.request.tenant
        ).distinct().order_by('id')

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsInTenant]

    def get_object(self):
        return self.request.user


class TenantMediaView(APIView):
    """Serve only branding files belonging to the authenticated facility.

    Django's development ``serve`` helper is intentionally not used here: it
    authorises neither the caller nor the tenant and therefore turns a known
    media path into a cross-tenant download capability.
    """
    permission_classes = [permissions.IsAuthenticated, IsInTenant]

    def get(self, request, path):
        if path.startswith('/') or '..' in path.split('/'):
            raise Http404
        config = getattr(request.tenant, 'config', None)
        allowed = {
            field.name for field in (getattr(config, 'logo', None), getattr(config, 'letterhead', None), getattr(config, 'favicon', None))
            if field and field.name
        }
        if path not in allowed or not default_storage.exists(path):
            raise Http404
        return FileResponse(default_storage.open(path, 'rb'))
