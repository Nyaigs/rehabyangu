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
    abnormality_level = models.CharField(max_length=20, choices=[('normal', 'Normal'), ('low', 'Low'), ('moderate', 'Moderate'), ('critical', 'Critical')], default='normal')
    abnormal_values = models.JSONField(default=list, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate BMI if weight and height are provided
        if self.weight and self.height and self.height > 0:
            height_m = self.height / 100  # convert cm to m
            self.bmi = self.weight / (height_m ** 2)
        self.abnormality_level, self.abnormal_values = self.evaluate_ranges()
        super().save(*args, **kwargs)

    def evaluate_ranges(self):
        defaults = {
            'temperature': (36.0, 37.5, 35.0, 39.0), 'heart_rate': (60, 100, 45, 130),
            'respiratory_rate': (12, 20, 8, 30), 'oxygen_saturation': (95, 100, 90, 100),
            'systolic_bp': (90, 140, 70, 180), 'diastolic_bp': (60, 90, 40, 120),
        }
        ranges = {}
        if self.tenant_id:
            # Apply shared defaults first, then tenant-specific overrides.
            for vital_range in VitalNormalRange.objects.filter(tenant__isnull=True):
                ranges[vital_range.metric] = vital_range
            for vital_range in VitalNormalRange.objects.filter(tenant_id=self.tenant_id):
                ranges[vital_range.metric] = vital_range
        findings, level = [], 'normal'
        rank = {'normal': 0, 'low': 1, 'moderate': 2, 'critical': 3}
        for metric, default in defaults.items():
            value = getattr(self, metric)
            if value is None: continue
            r = ranges.get(metric)
            low, high, critical_low, critical_high = (r.low, r.high, r.critical_low, r.critical_high) if r else default
            if value < critical_low or value > critical_high: severity = 'critical'
            elif value < low: severity = 'low'
            elif value > high: severity = 'moderate'
            else: continue
            findings.append({'metric': metric, 'value': str(value), 'severity': severity})
            if rank[severity] > rank[level]: level = severity
        return level, findings
    
    def __str__(self):
        return f"{self.patient} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-recorded_at']


class VitalNormalRange(models.Model):
    """Tenant overrides; a null tenant is a global default range."""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True, related_name='vital_ranges')
    metric = models.CharField(max_length=40)
    low = models.DecimalField(max_digits=7, decimal_places=2)
    high = models.DecimalField(max_digits=7, decimal_places=2)
    critical_low = models.DecimalField(max_digits=7, decimal_places=2)
    critical_high = models.DecimalField(max_digits=7, decimal_places=2)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['tenant', 'metric'], name='unique_vital_range_per_tenant')]
