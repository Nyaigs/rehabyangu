from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    tenant_name = serializers.CharField(source='profile.tenant.name', read_only=True)
    is_rehab_admin = serializers.BooleanField(source='profile.is_rehab_admin', read_only=True)
    
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
