from django.db import models
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['start_time']