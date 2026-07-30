from django.db import models
from patients.models import Patient
from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

class VitalSign(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='vitals')
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recorded_vitals')
    recorded_at = models.DateTimeField(auto_now_add=True)
    date_measured = models.DateTimeField()  # when the vitals were actually taken (can be backdated)
    
    # Vitals
    systolic_bp = models.IntegerField(null=True, blank=True)  # mmHg
    diastolic_bp = models.IntegerField(null=True, blank=True)  # mmHg
    heart_rate = models.IntegerField(null=True, blank=True)  # bpm
    respiratory_rate = models.IntegerField(null=True, blank=True)  # breaths/min
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # °C
    oxygen_saturation = models.IntegerField(null=True, blank=True)  # %
    blood_sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # mmol/L
    pain_score = models.IntegerField(null=True, blank=True)  # 0-10
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # kg
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # cm
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # calculated
    notes = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate BMI if weight and height are provided
        if self.weight and self.height and self.height > 0:
            height_m = self.height / 100  # convert cm to m
            self.bmi = self.weight / (height_m ** 2)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.patient} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-recorded_at']