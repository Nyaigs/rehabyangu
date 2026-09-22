from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from tenants.models import Tenant

User = get_user_model()

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('registered', 'Registered / New'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discharged', 'Discharged'),
        ('transferred', 'Transferred'),
    ]
    CARE_TYPE_CHOICES = [
        ('inpatient', 'Inpatient'),
        ('outpatient', 'Outpatient'),
        ('day_patient', 'Day Patient'),
        ('new_referral', 'New Referral'),
    ]
    
    # Demographics
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=200, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True, null=True)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    # Highly sensitive. Never return this to a caller without the dedicated
    # clinical.sensitive.read permission.
    hiv_status = models.CharField(max_length=30, blank=True, null=True)
    
    # Rehab specific
    intake_date = models.DateField(auto_now_add=True)
    # Care setting and treatment lifecycle deliberately remain independent.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    care_type = models.CharField(max_length=20, choices=CARE_TYPE_CHOICES, default='new_referral')
    preferred_visit_days = models.JSONField(default=list, blank=True)
    expected_frequency = models.CharField(max_length=100, blank=True)
    referral_source = models.CharField(max_length=200, blank=True)
    referring_doctor = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Multi-tenant support
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="patients", default=1)
    patient_id = models.CharField(max_length=20, blank=True, null=True)
    
    # Discharge tracking
    discharged_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients_created')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['-intake_date']

# ----- NEW: DischargeRequest Model -----
    def save(self, *args, **kwargs):
        if not self.patient_id and self.tenant_id:
            abbreviation = self.tenant.subdomain[:3].upper()
            prefix = f'{abbreviation}-PT-'
            count = Patient.objects.filter(
                tenant=self.tenant,
                patient_id__startswith=prefix
            ).count()
            next_num = count + 1
            self.patient_id = f'{prefix}{next_num:03d}'
        super().save(*args, **kwargs)
class DischargeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='discharge_requests')
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='initiated_discharges')
    requested_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    is_force = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_discharges')
    approved_at = models.DateTimeField(null=True, blank=True)
    approval_reason = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Discharge request for {self.patient} - {self.status}"


class Admission(models.Model):
    """A tenant-scoped inpatient episode. A patient may have many episodes."""
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='admissions')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='admissions')
    admission_number = models.CharField(max_length=32, unique=True, editable=False)
    intake_date = models.DateTimeField()
    discharge_date = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('admitted', 'Admitted'), ('discharged', 'Discharged')], default='admitted')
    length_of_stay_days = models.PositiveIntegerField(default=0)
    room = models.CharField(max_length=100, blank=True)
    bed = models.CharField(max_length=100, blank=True)
    primary_diagnosis = models.TextField(blank=True)
    psychiatric_diagnosis = models.TextField(blank=True)
    substance_use_history = models.JSONField(default=dict, blank=True)
    medical_history = models.TextField(blank=True)
    allergies = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='admissions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-intake_date']
        constraints = [models.UniqueConstraint(fields=['patient'], condition=Q(discharge_date__isnull=True), name='one_open_admission_per_patient')]

    def save(self, *args, **kwargs):
        if not self.admission_number and self.tenant_id:
            prefix = f'{self.tenant.subdomain[:3].upper()}-ADM-'
            count = Admission.objects.filter(tenant=self.tenant, admission_number__startswith=prefix).count() + 1
            self.admission_number = f'{prefix}{count:04d}'
        super().save(*args, **kwargs)

    def refresh_stay_length(self):
        end = self.discharge_date or timezone.now()
        self.length_of_stay_days = max(0, (end.date() - self.intake_date.date()).days)


class TreatmentPlan(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='treatment_plans')
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='treatment_plans')
    admission = models.ForeignKey(Admission, on_delete=models.PROTECT, related_name='treatment_plans', blank=True, null=True)
    title = models.CharField(max_length=255)
    diagnosis_summary = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    start_date = models.DateField()
    target_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='treatment_plans_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class TreatmentGoal(models.Model):
    STATUS_CHOICES = [('not_started', 'Not started'), ('in_progress', 'In progress'), ('achieved', 'Achieved'), ('discontinued', 'Discontinued')]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='treatment_goals')
    treatment_plan = models.ForeignKey(TreatmentPlan, on_delete=models.CASCADE, related_name='goals')
    description = models.TextField()
    target_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    progress_percent = models.PositiveSmallIntegerField(default=0)
    progress_note = models.TextField(blank=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='treatment_goals_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date', 'created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        if not 0 <= self.progress_percent <= 100:
            raise ValidationError({'progress_percent': 'Progress must be between 0 and 100.'})
