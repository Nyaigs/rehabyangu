from django.db import models
from django.utils import timezone

class Tenant(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('overdue', 'Overdue'),
        ('suspended', 'Suspended'),
    ]
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ]
    BILLING_CYCLE_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=200)
    subdomain = models.SlugField(unique=True)
    logo_url = models.URLField(blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#2563EB")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Billing & Subscription
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    next_billing_date = models.DateTimeField(null=True, blank=True)
    grace_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    def is_suspended(self):
        return self.status == 'suspended'

    def is_overdue(self):
        return self.status == 'overdue'

    def days_until_billing(self):
        if not self.next_billing_date:
            return None
        delta = self.next_billing_date - timezone.now()
        return delta.days


class TenantConfig(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='config')
    primary_color = models.CharField(max_length=7, default="#2563EB")
    secondary_color = models.CharField(max_length=7, default="#10B981")
    accent_color = models.CharField(max_length=7, default="#F59E0B")
    sidebar_color = models.CharField(max_length=7, default="#1E293B")
    font_family = models.CharField(max_length=100, default="Inter, system-ui, sans-serif")
    company_name = models.CharField(max_length=200, default="RehabYangu")
    tagline = models.CharField(max_length=200, blank=True, null=True)
    footer_text = models.CharField(max_length=200, default="RehabYangu – Powered by Weiraro Technologies")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config for {self.tenant.name}"