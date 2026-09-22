from rest_framework import serializers

from .models import SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'name', 'code', 'description', 'price_monthly', 'max_users', 'feature_flags', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_feature_flags(self, value):
        if not isinstance(value, dict) or any(not isinstance(key, str) or not isinstance(enabled, bool) for key, enabled in value.items()):
            raise serializers.ValidationError('Feature flags must be an object with boolean values.')
        return value

    def validate_price_monthly(self, value):
        if value < 0:
            raise serializers.ValidationError('Monthly price cannot be negative.')
        return value
