from django.db import models
from patients.models import Patient
from inventory.models import InventoryItem
from tenants.models import Tenant
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()

class PatientBill(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name='bill')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    total_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

class BillItem(models.Model):
    bill = models.ForeignKey(PatientBill, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    charged_at = models.DateTimeField(auto_now_add=True)
    administered_by = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)

class Payment(models.Model):
    PAYMENT_METHODS = [('MPESA', 'M-Pesa'), ('CASH', 'Cash'), ('BANK', 'Bank Transfer')]
    bill = models.ForeignKey(PatientBill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=100)
    paid_at = models.DateTimeField(auto_now_add=True)

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    bill = models.ForeignKey(PatientBill, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=20, unique=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    period_start = models.DateField()
    period_end = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    cover_letter_text = models.TextField(blank=True, null=True)
    sponsor_email = models.EmailField(blank=True, null=True)
    sponsor_name = models.CharField(max_length=200, blank=True, null=True)
    sponsor_phone = models.CharField(max_length=20, blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    # NO UNIQUE – we'll add later
    download_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    token_expiry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"INV-{self.invoice_number} - {self.bill.patient}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last = Invoice.objects.filter(
                invoice_number__startswith=f"INV-{year}-{month}-"
            ).count() + 1
            self.invoice_number = f"INV-{year}-{month}-{last:04d}"
        if not self.download_token:
            self.download_token = uuid.uuid4()
        if not self.token_expiry:
            self.token_expiry = timezone.now() + timezone.timedelta(days=30)
        super().save(*args, **kwargs)
