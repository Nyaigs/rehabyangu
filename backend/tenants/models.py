from django.db import models
from django.utils import timezone
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from base64 import urlsafe_b64encode
from hashlib import sha256


def _credential_cipher():
    """Use an explicit deployment key when supplied, with a safe key shape."""
    key = getattr(settings, 'FIELD_ENCRYPTION_KEY', '')
    if key:
        return Fernet(key.encode() if isinstance(key, str) else key)
    # SECRET_KEY is already protected deployment secret; deriving a Fernet key
    # keeps existing installations usable until FIELD_ENCRYPTION_KEY is set.
    return Fernet(urlsafe_b64encode(sha256(settings.SECRET_KEY.encode()).digest()))

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
    # Archiving retains clinical and financial history while removing a
    # facility from normal operations. Tenants are never hard-deleted.
    archived_at = models.DateTimeField(null=True, blank=True)

    # Billing & Subscription
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    billing_cycle = models.CharField(max_length=20, choices=BILLING_CYCLE_CHOICES, default='monthly')
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # `plan` and `monthly_fee` are retained for legacy integrations. New
    # platform code reads pricing and capabilities from this relationship.
    plan_fk = models.ForeignKey(
        'subscriptions.SubscriptionPlan', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='tenants',
    )
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
    letterhead = models.ImageField(upload_to='letterheads/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)
    # M-Pesa keys are Fernet-encrypted before persistence. Never expose these
    # columns directly through an API serializer.
    mpesa_shortcode = models.CharField(max_length=50, blank=True)
    mpesa_shortcode_type = models.CharField(max_length=10, choices=[('paybill', 'Paybill'), ('till', 'Till')], default='paybill')
    mpesa_consumer_key = models.TextField(blank=True)
    mpesa_consumer_secret = models.TextField(blank=True)
    mpesa_passkey = models.TextField(blank=True)
    mpesa_account_prefix = models.CharField(max_length=20, default='INV')
    kra_pin = models.CharField(max_length=30, blank=True)
    vat_registered = models.BooleanField(default=False)
    vat_number = models.CharField(max_length=30, blank=True)
    bank_name = models.CharField(max_length=150, blank=True)
    bank_account_name = models.CharField(max_length=150, blank=True)
    bank_account_number = models.CharField(max_length=100, blank=True)
    bank_branch = models.CharField(max_length=150, blank=True)
    invoice_prefix = models.CharField(max_length=20, default='INV')
    next_invoice_number = models.PositiveIntegerField(default=1)
    invoice_terms = models.TextField(blank=True)
    invoice_footer_text = models.TextField(blank=True)
    # Set only after the initial rehabilitation administrator has completed
    # the facility setup flow.  Existing tenants remain eligible for the
    # wizard until an administrator explicitly completes it.
    onboarding_completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Config for {self.tenant.name}"

    @staticmethod
    def encrypt_credential(value):
        return _credential_cipher().encrypt(value.encode()).decode() if value else ''

    @staticmethod
    def decrypt_credential(value):
        if not value:
            return ''
        try:
            return _credential_cipher().decrypt(value.encode()).decode()
        except (InvalidToken, ValueError):
            # Do not leak a malformed stored value into a payment request.
            return ''

    def mpesa_credentials(self):
        return {
            'shortcode': self.mpesa_shortcode,
            'shortcode_type': self.mpesa_shortcode_type,
            'consumer_key': self.decrypt_credential(self.mpesa_consumer_key),
            'consumer_secret': self.decrypt_credential(self.mpesa_consumer_secret),
            'passkey': self.decrypt_credential(self.mpesa_passkey),
        }
