from rest_framework import serializers

from authorization.utils import get_user_permissions
from .models import Admission, Patient, TreatmentGoal, TreatmentPlan


def can_access_sensitive(request):
    return bool(request and (request.user.is_superuser or 'clinical.sensitive.read' in get_user_permissions(request.user, request.tenant)))


def can_write_sensitive(request):
    return bool(request and (request.user.is_superuser or 'clinical.sensitive.write' in get_user_permissions(request.user, request.tenant)))


def can_read_clinical(request):
    return bool(request and (request.user.is_superuser or 'clinical.read' in get_user_permissions(request.user, request.tenant)))


def can_write_clinical(request):
    return bool(request and (request.user.is_superuser or 'clinical.write' in get_user_permissions(request.user, request.tenant)))


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ('tenant', 'patient_id', 'created_at', 'updated_at', 'created_by')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if not can_access_sensitive(request):
            data.pop('hiv_status', None)
        # This legacy free-text field may contain clinical information. Keep
        # reception users on the demographics-only side of the EMR boundary.
        if not can_read_clinical(request):
            data.pop('notes', None)
        return data

    def validate(self, attrs):
        if 'hiv_status' in attrs and not can_write_sensitive(self.context.get('request')):
            raise serializers.ValidationError({'hiv_status': 'You do not have permission to edit this sensitive field.'})
        request = self.context.get('request')
        if 'notes' in attrs and not can_write_clinical(request):
            raise serializers.ValidationError({'notes': 'Use the clinical-notes endpoint to write clinical information.'})
        care_type = attrs.get('care_type', getattr(self.instance, 'care_type', 'new_referral'))
        visit_days = attrs.get('preferred_visit_days', getattr(self.instance, 'preferred_visit_days', []))
        valid_days = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
        if not isinstance(visit_days, list) or any(not isinstance(day, str) or day.lower() not in valid_days for day in visit_days):
            raise serializers.ValidationError({'preferred_visit_days': 'Choose valid days from Monday through Sunday.'})
        if care_type not in ('outpatient', 'day_patient') and visit_days:
            raise serializers.ValidationError({'preferred_visit_days': 'Visit days apply only to outpatient and day-patient care.'})
        return attrs


class AdmissionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    length_of_stay_days = serializers.SerializerMethodField()

    class Meta:
        model = Admission
        fields = '__all__'
        read_only_fields = ('tenant', 'admission_number', 'created_by', 'created_at', 'updated_at', 'status', 'length_of_stay_days', 'discharge_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not can_access_sensitive(self.context.get('request')):
            data.pop('psychiatric_diagnosis', None)
            data.pop('substance_use_history', None)
        return data

    def get_length_of_stay_days(self, instance):
        if instance.discharge_date:
            return instance.length_of_stay_days
        from django.utils import timezone
        return max(0, (timezone.now().date() - instance.intake_date.date()).days)

    def validate(self, attrs):
        sensitive_fields = {'psychiatric_diagnosis', 'substance_use_history'} & set(attrs)
        if sensitive_fields and not can_write_sensitive(self.context.get('request')):
            raise serializers.ValidationError({field: 'You do not have permission to edit this sensitive field.' for field in sensitive_fields})
        request = self.context['request']
        patient = attrs.get('patient') or getattr(self.instance, 'patient', None)
        if patient and patient.tenant_id != request.tenant.id:
            raise serializers.ValidationError({'patient': 'Patient is outside this tenant.'})
        room = attrs.get('room', getattr(self.instance, 'room', ''))
        bed = attrs.get('bed', getattr(self.instance, 'bed', ''))
        if room and bed:
            occupied = Admission.objects.filter(tenant=request.tenant, room=room, bed=bed, discharge_date__isnull=True)
            if self.instance:
                occupied = occupied.exclude(pk=self.instance.pk)
            if occupied.exists():
                raise serializers.ValidationError({'bed': 'This room and bed are currently occupied.'})
        return attrs


class TreatmentGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentGoal
        fields = '__all__'
        read_only_fields = ('tenant', 'treatment_plan', 'updated_by', 'created_at', 'updated_at')

    def validate_progress_percent(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError('Progress must be between 0 and 100.')
        return value


class TreatmentPlanSerializer(serializers.ModelSerializer):
    goals = TreatmentGoalSerializer(many=True, read_only=True)

    class Meta:
        model = TreatmentPlan
        fields = '__all__'
        read_only_fields = ('tenant', 'created_by', 'created_at', 'updated_at')

    def validate(self, attrs):
        request = self.context['request']
        patient = attrs.get('patient') or getattr(self.instance, 'patient', None)
        admission = attrs.get('admission') or getattr(self.instance, 'admission', None)
        if patient and patient.tenant_id != request.tenant.id:
            raise serializers.ValidationError({'patient': 'Patient is outside this tenant.'})
        if admission and (admission.tenant_id != request.tenant.id or (patient and admission.patient_id != patient.id)):
            raise serializers.ValidationError({'admission': 'Admission must belong to this patient and tenant.'})
        return attrs
