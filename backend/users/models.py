import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from tenants.models import Tenant
from authorization.models import Permission, Role

class UserProfile(models.Model):
    ROLES = [
        ('super_admin', 'Super Admin (Weiraro)'),
        ('rehab_admin', 'Rehab Admin (Director)'),
        ('psychiatrist', 'Psychiatrist'),
        ('clinical_officer', 'Clinical Officer'),
        ('nurse', 'Nurse'),
        ('counselor', 'Counselor'),
        ('pharmacist', 'Pharmacist'),
        ('receptionist', 'Receptionist'),
        ('accountant', 'Accountant'),
        ('store_manager', 'Store Manager'),
        ('hr_manager', 'HR Manager'),
        ('cook', 'Cook'),
        ('other', 'Other'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
#    role = models.CharField(max_length=50, choices=ROLES, default='other')
#    is_rehab_admin = models.BooleanField(default=False)
#    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New zero‑trust authorization fields
    roles = models.ManyToManyField(Role, blank=True)
    extra_permissions = models.ManyToManyField(Permission, blank=True, related_name='granted_to_users')

    def __str__(self):
        return self.user.username

class TenantMembership(models.Model):
    """
    Links a User to a Tenant with a specific role.
    One user can have one membership per tenant.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_memberships')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=50, choices=UserProfile.ROLES, default='other')
    is_rehab_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    tenant_user_id = models.CharField(max_length=20, blank=True, null=True)
    # Authorisation is scoped to a tenant membership. The UserProfile fields
    # remain for backwards compatibility with existing deployments.
    roles = models.ManyToManyField(Role, blank=True, related_name='memberships')
    extra_permissions = models.ManyToManyField(
        Permission, blank=True, related_name='membership_grants'
    )

    class Meta:
        unique_together = ('user', 'tenant')
        verbose_name = 'Tenant Membership'
        verbose_name_plural = 'Tenant Memberships'

    def __str__(self):
        return self.user.username


    def save(self, *args, **kwargs):
        if not self.tenant_user_id and self.tenant_id:
            abbreviation = self.tenant.subdomain[:3].upper()
            role_prefix = 'DIR' if self.is_rehab_admin else 'ST'
            prefix = f'{abbreviation}-{role_prefix}-'
            count = TenantMembership.objects.filter(
                tenant=self.tenant,
                tenant_user_id__startswith=prefix
            ).count()
            next_num = count + 1
            self.tenant_user_id = f'{prefix}{next_num:03d}'
        super().save(*args, **kwargs)
class AuditLog(models.Model):
    """
    Records actions performed by users within a tenant context.
    """
    ACTIONS = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('READ', 'Read'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('SUSPEND', 'Suspend'),
        ('REACTIVATE', 'Reactivate'),
    ]

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTIONS)
    # Generic foreign key fields
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tenant', 'action']),
            models.Index(fields=['content_type', 'object_id']),
        ]


class Invitation(models.Model):
    """A tenant-bound, single-use capability for joining a facility."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    legacy_role = models.CharField(max_length=50, choices=UserProfile.ROLES, default='other')
    is_rehab_admin = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, related_name='invitations', blank=True)
    token_hash = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='sent_invitations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['tenant', 'email']), models.Index(fields=['expires_at'])]

    @property
    def is_usable(self):
        return not self.accepted_at and not self.revoked_at and self.expires_at > timezone.now()


class AuthSession(models.Model):
    """Server-side session state referenced by otherwise stateless JWTs."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='auth_sessions')
    # Platform sessions deliberately have no tenant context.
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='auth_sessions', null=True, blank=True)
    refresh_jti = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'tenant', 'revoked_at'])]

    @property
    def is_active(self):
        return not self.revoked_at and self.expires_at > timezone.now()


class MfaPolicy(models.Model):
    tenant = models.OneToOneField('tenants.Tenant', on_delete=models.CASCADE, related_name='mfa_policy')
    required_for_all_staff = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class TotpDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='totp_devices')
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='totp_devices')
    # Never expose this field in a serializer; it contains a Fernet-encrypted TOTP secret.
    secret_encrypted = models.TextField()
    name = models.CharField(max_length=100, default='Authenticator app')
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'tenant', 'name'], name='unique_totp_device_name')]
