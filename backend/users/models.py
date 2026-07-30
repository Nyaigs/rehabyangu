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
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.CharField(max_length=50, choices=ROLES, default='other')
    is_rehab_admin = models.BooleanField(default=False)
    is_super_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New zero‑trust authorization fields
    roles = models.ManyToManyField(Role, blank=True)
    extra_permissions = models.ManyToManyField(Permission, blank=True, related_name='granted_to_users')

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.tenant.name if self.tenant else 'Super Admin'})"
