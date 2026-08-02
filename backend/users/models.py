from django.conf import settings
from django.db import models
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

    class Meta:
        unique_together = ('user', 'tenant')
        verbose_name = 'Tenant Membership'
        verbose_name_plural = 'Tenant Memberships'

    def __str__(self):
        return self.user.username


    def save(self, *args, **kwargs):
        if not self.tenant_user_id and self.tenant_id:
            abbreviation = self.tenant.subdomain[:3].upper()
            from django.db.models import Max
            from django.db.models.functions import Substr
            last = TenantMembership.objects.filter(
                tenant=self.tenant,
                tenant_user_id__startswith=abbreviation
            ).annotate(
                num=Substr("tenant_user_id", len(abbreviation)+2, 3)
            ).aggregate(max_num=Max("num"))["max_num"]
            next_num = 1 if last is None else int(last) + 1
            self.tenant_user_id = f"{abbreviation}-{next_num:03d}"
        super().save(*args, **kwargs)
class AuditLog(models.Model):
    """
    Records actions performed by users within a tenant context.
    """
    ACTIONS = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
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

