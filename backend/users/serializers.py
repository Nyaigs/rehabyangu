from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()
    is_rehab_admin = serializers.SerializerMethodField()

    def get_membership(self, user):
        request = self.context.get('request')
        tenant = getattr(request, 'tenant', None) if request else None
        return user.tenant_memberships.filter(tenant=tenant).first() if tenant else None

    def get_role(self, user):
        membership = self.get_membership(user)
        return membership.role if membership else None

    def get_tenant_name(self, user):
        membership = self.get_membership(user)
        return membership.tenant.name if membership else None

    def get_is_rehab_admin(self, user):
        membership = self.get_membership(user)
        return bool(membership and membership.is_rehab_admin)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'role', 'tenant_name', 'is_rehab_admin']
from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)
    actor_tenant_user_id = serializers.CharField(source='actor.tenant_memberships.first.tenant_user_id', read_only=True)
    class Meta:
        model = AuditLog
        fields = ['id', 'actor', 'actor_username', 'actor_tenant_user_id', 'tenant', 'action', 'content_type', 'object_id', 'description', 'ip_address', 'timestamp']
