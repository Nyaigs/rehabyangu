from django.conf import settings
from django.db import models
from django.utils import timezone
from patients.models import Patient
from tenants.models import Tenant


class Medication(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=200)
    strength = models.CharField(max_length=100)
    form = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    is_controlled_substance = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'strength']
        constraints = [models.UniqueConstraint(fields=['tenant', 'name', 'strength', 'form'], name='unique_tenant_medication')]

    def __str__(self):
        return f'{self.name} {self.strength}'.strip()


class Prescription(models.Model):
    STATUS = [('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='prescriptions')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT, related_name='prescriptions')
    dose = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100, help_text='For example: every 8 hours')
    duration_days = models.PositiveIntegerField()
    start_at = models.DateTimeField(default=timezone.now)
    instructions = models.TextField(blank=True)
    prescribing_clinician = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='prescriptions_written')
    status = models.CharField(max_length=20, choices=STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_at']

    @property
    def ends_at(self):
        return self.start_at + timezone.timedelta(days=self.duration_days)


class MedicationAdministrationRecord(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT, related_name='administrations')
    administered_at = models.DateTimeField(default=timezone.now)
    dose = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    given_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='medications_given')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-administered_at']
