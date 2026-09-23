from rest_framework import serializers

from subscriptions.models import SubscriptionPlan
from subscriptions.serializers import SubscriptionPlanSerializer
from subscriptions.services import tenant_user_capacity
from .models import Tenant


class AdminTenantSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(source='plan_fk', read_only=True)
    user_count = serializers.SerializerMethodField()
    max_users = serializers.SerializerMethodField()
    remaining_users = serializers.SerializerMethodField()
    trial_started_at = serializers.DateTimeField(source='created_at', read_only=True)
    active_user_count = serializers.SerializerMethodField()
    active_member_count = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'subdomain', 'logo_url', 'status', 'is_active', 'archived_at', 'plan', 'monthly_fee',
                  'user_count', 'active_user_count', 'active_member_count', 'max_users', 'remaining_users',
                  'trial_started_at', 'trial_ends_at', 'next_billing_date', 'grace_period_end', 'days_remaining',
                  'billing_cycle', 'created_at']

    def get_user_count(self, obj): return tenant_user_capacity(obj)[0]
    def get_max_users(self, obj): return tenant_user_capacity(obj)[1]
    def get_remaining_users(self, obj): return tenant_user_capacity(obj)[2]
    def get_active_user_count(self, obj): return obj.memberships.filter(user__is_active=True).count()
    def get_active_member_count(self, obj): return obj.memberships.filter(user__is_active=True).count()
    def get_days_remaining(self, obj):
        from django.utils import timezone
        target = obj.trial_ends_at if obj.status == 'trial' else (obj.grace_period_end if obj.status == 'overdue' else obj.next_billing_date)
        return None if not target else max((target - timezone.now()).days, 0)


class AdminTenantCreateSerializer(serializers.Serializer):
    tenant_name = serializers.CharField(max_length=200)
    subdomain = serializers.SlugField(max_length=50)
    admin_first_name = serializers.CharField(max_length=150)
    admin_last_name = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.filter(is_active=True))

    def validate_subdomain(self, value):
        value = value.lower().strip()
        if Tenant.objects.filter(subdomain__iexact=value).exists():
            raise serializers.ValidationError('This subdomain is already in use.')
        return value

    def validate_admin_email(self, value):
        from django.contrib.auth.models import User
        from users.models import Invitation
        if User.objects.filter(email__iexact=value).exists() or Invitation.objects.filter(email__iexact=value, accepted_at__isnull=True, revoked_at__isnull=True).exists():
            raise serializers.ValidationError('This email already has an account or active invitation.')
        return value.lower()


class AdminTenantUpdateSerializer(serializers.Serializer):
    subscription_plan = serializers.PrimaryKeyRelatedField(queryset=SubscriptionPlan.objects.all(), required=False)
    acknowledge_warnings = serializers.BooleanField(required=False, default=False)
    action = serializers.ChoiceField(choices=['activate', 'suspend', 'restore', 'deactivate', 'archive'], required=False)
    next_billing_date = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('Provide an action, subscription plan, or billing date.')
        if 'subscription_plan' in attrs and not attrs['subscription_plan'].is_active:
            raise serializers.ValidationError({'subscription_plan': 'Inactive plans cannot be assigned.'})
        return attrs
