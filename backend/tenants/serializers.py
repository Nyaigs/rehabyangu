from rest_framework import serializers
from .models import Tenant
from users.models import TenantMembership

class TenantSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()
    patient_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'logo_url', 'primary_color',
            'is_active', 'created_at', 'status', 'plan', 'billing_cycle',
            'trial_ends_at', 'next_billing_date', 'grace_period_end',
            'user_count', 'patient_count'
        ]

    def get_user_count(self, obj):
        return TenantMembership.objects.filter(tenant=obj).count()

    def get_patient_count(self, obj):
        from patients.models import Patient
        return Patient.objects.filter(tenant=obj).count()

class TenantStatsSerializer(serializers.Serializer):
    total_tenants = serializers.IntegerField()
    active_tenants = serializers.IntegerField()
    overdue_tenants = serializers.IntegerField()
    suspended_tenants = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    total_users = serializers.IntegerField()

class CreateTenantSerializer(serializers.Serializer):
    tenant_name = serializers.CharField(max_length=200)
    subdomain = serializers.SlugField()
    admin_name = serializers.CharField(max_length=100)
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(write_only=True, min_length=6)
