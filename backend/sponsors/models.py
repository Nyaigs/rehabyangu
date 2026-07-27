from django.db import models
from patients.models import Patient

class Sponsor(models.Model):
    RELATIONSHIP_CHOICES = [
        ('family', 'Family Member'),
        ('employer', 'Employer'),
        ('self', 'Self'),
        ('government', 'Government'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='sponsors')
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} -> {self.patient}"