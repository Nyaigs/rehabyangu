import uuid

from django.db import models
from patients.models import Admission, Patient
from django.contrib.auth import get_user_model
from tenants.models import Tenant  # <-- Added import

User = get_user_model()

class ClinicalNote(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='notes', default=1)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_notes')
    admission = models.ForeignKey(Admission, on_delete=models.PROTECT, related_name='clinical_notes', blank=True, null=True)
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinical_notes')
    date = models.DateTimeField(auto_now_add=True)
    subjective = models.TextField()
    objective = models.TextField()
    assessment = models.TextField()
    plan = models.TextField()
    record_id = models.UUIDField(default=uuid.uuid4, editable=False)
    version = models.PositiveIntegerField(default=1)
    supersedes = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, related_name='corrections')
    correction_reason = models.TextField(blank=True)
    
    def __str__(self):
        return f"Note for {self.patient} - {self.date.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-date']
        constraints = [models.UniqueConstraint(fields=['record_id', 'version'], name='unique_clinical_note_version')]
