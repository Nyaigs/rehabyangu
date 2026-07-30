from django.db import models
from patients.models import Patient
from django.contrib.auth import get_user_model
from tenants.models import Tenant  # <-- Added import

User = get_user_model()

class ClinicalNote(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='notes', default=1)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_notes')
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinical_notes')
    date = models.DateTimeField(auto_now_add=True)
    subjective = models.TextField()
    objective = models.TextField()
    assessment = models.TextField()
    plan = models.TextField()
    
    def __str__(self):
        return f"Note for {self.patient} - {self.date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-date']