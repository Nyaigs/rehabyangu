from rest_framework import serializers
from .models import Tenant, TenantConfig
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
    # The first administrator receives a 72-hour password-set invitation.
    # Passwords must never be accepted or logged during tenant provisioning.


class TenantConfigSerializer(serializers.ModelSerializer):
    """The authenticated facility-branding contract."""
    complete_onboarding = serializers.BooleanField(write_only=True, required=False)
    logo_url = serializers.SerializerMethodField(read_only=True)
    letterhead_url = serializers.SerializerMethodField(read_only=True)
    favicon_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TenantConfig
        fields = [
            'primary_color', 'secondary_color', 'accent_color', 'sidebar_color',
            'font_family', 'company_name', 'tagline', 'footer_text', 'logo',
            'letterhead', 'favicon', 'onboarding_completed_at',
            'logo_url', 'letterhead_url', 'favicon_url',
            'complete_onboarding',
        ]
        read_only_fields = ['onboarding_completed_at']
        extra_kwargs = {
            'logo': {'write_only': True, 'required': False},
            'letterhead': {'write_only': True, 'required': False},
            'favicon': {'write_only': True, 'required': False},
        }

    def validate_primary_color(self, value): return self._validate_hex_color(value, 'primary_color')
    def validate_secondary_color(self, value): return self._validate_hex_color(value, 'secondary_color')
    def validate_accent_color(self, value): return self._validate_hex_color(value, 'accent_color')
    def validate_sidebar_color(self, value): return self._validate_hex_color(value, 'sidebar_color')

    @staticmethod
    def _validate_hex_color(value, field):
        value = value.strip()
        if len(value) != 7 or not value.startswith('#'):
            raise serializers.ValidationError(f'{field} must be a #RRGGBB colour.')
        try:
            int(value[1:], 16)
        except ValueError:
            raise serializers.ValidationError(f'{field} must be a #RRGGBB colour.')
        return value.upper()

    @staticmethod
    def _validate_image(upload, field):
        if upload.size > 2 * 1024 * 1024:
            raise serializers.ValidationError(f'{field} must be 2 MiB or smaller.')
        allowed_types = {'image/png', 'image/jpeg', 'image/webp', 'image/svg+xml', 'image/x-icon', 'image/vnd.microsoft.icon'}
        content_type = (getattr(upload, 'content_type', '') or '').lower()
        if content_type not in allowed_types:
            raise serializers.ValidationError(f'{field} must be a PNG, JPEG, WebP, SVG, or ICO image.')
        # Content-Type and filename are caller-controlled. Verify a compact
        # magic signature before accepting the file so a script renamed .png
        # cannot be stored as a facility asset.
        header = upload.read(4096)
        upload.seek(0)
        is_png = header.startswith(b'\x89PNG\r\n\x1a\n')
        is_jpeg = header.startswith(b'\xff\xd8\xff')
        is_webp = len(header) >= 12 and header[:4] == b'RIFF' and header[8:12] == b'WEBP'
        is_ico = header.startswith(b'\x00\x00\x01\x00')
        is_svg = header.lstrip().lower().startswith(b'<svg') or b'<svg' in header[:1024].lower()
        expected = {
            'image/png': is_png, 'image/jpeg': is_jpeg, 'image/webp': is_webp,
            'image/svg+xml': is_svg, 'image/x-icon': is_ico,
            'image/vnd.microsoft.icon': is_ico,
        }
        if not expected[content_type]:
            raise serializers.ValidationError(f'{field} content does not match its declared image type.')
        return upload

    def validate_logo(self, value): return self._validate_image(value, 'logo')
    def validate_letterhead(self, value): return self._validate_image(value, 'letterhead')
    def validate_favicon(self, value): return self._validate_image(value, 'favicon')

    def get_logo_url(self, obj): return obj.logo.url if obj.logo else None
    def get_letterhead_url(self, obj): return obj.letterhead.url if obj.letterhead else None
    def get_favicon_url(self, obj): return obj.favicon.url if obj.favicon else None

    def update(self, instance, validated_data):
        complete_onboarding = validated_data.pop('complete_onboarding', False)
        instance = super().update(instance, validated_data)
        if complete_onboarding and instance.onboarding_completed_at is None:
            from django.utils import timezone
            instance.onboarding_completed_at = timezone.now()
            instance.save(update_fields=['onboarding_completed_at', 'updated_at'])
        return instance
