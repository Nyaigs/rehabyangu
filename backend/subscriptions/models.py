from django.db import models
from django.utils import timezone
from tenants.models import Tenant
from django.contrib.auth.models import User

class Subscription(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, default='basic')
    billing_cycle = models.CharField(max_length=20, default='monthly')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    next_billing_date = models.DateTimeField()
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    grace_period_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='trial')  # active, trial, overdue, suspended
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.status}"

    def is_overdue(self):
        if self.status == 'overdue':
            return True
        if self.grace_period_end and timezone.now() > self.grace_period_end:
            return True
        return False

    def days_until_billing(self):
        delta = self.next_billing_date - timezone.now()
        return delta.days

class PaymentRecord(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=[('mpesa', 'M-Pesa'), ('bank', 'Bank Transfer'), ('cash', 'Cash')])
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    paid_through_date = models.DateTimeField()  # The billing date this payment covers up to

    def __str__(self):
        return f"{self.tenant.name} - {self.amount} on {self.recorded_at}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('payment_due', 'Payment Due'),
        ('payment_overdue', 'Payment Overdue'),
        ('suspension_warning', 'Suspension Warning'),
        ('suspended', 'Suspended'),
        ('reactivated', 'Reactivated'),
        ('trial_ending', 'Trial Ending'),
        ('other', 'Other'),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='notifications')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # optional specific user
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.title}"
