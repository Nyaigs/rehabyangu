from rest_framework import serializers
from .models import Medication, Prescription, MedicationAdministrationRecord


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = '__all__'
        read_only_fields = ('tenant', 'created_at')


class PrescriptionSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    medication_name = serializers.CharField(source='medication.__str__', read_only=True)
    prescribing_clinician_name = serializers.CharField(source='prescribing_clinician.username', read_only=True)
    ends_at = serializers.DateTimeField(read_only=True)
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ('tenant', 'prescribing_clinician', 'created_at')

    def validate(self, attrs):
        tenant = self.context['request'].tenant
        for field in ('patient', 'medication'):
            value = attrs.get(field) or getattr(self.instance, field, None)
            if value and value.tenant_id != tenant.id:
                raise serializers.ValidationError({field: 'Must belong to this tenant.'})
        return attrs


class MARSerializer(serializers.ModelSerializer):
    given_by_name = serializers.CharField(source='given_by.username', read_only=True)
    medication_name = serializers.CharField(source='prescription.medication.__str__', read_only=True)
    patient = serializers.IntegerField(source='prescription.patient_id', read_only=True)
    class Meta:
        model = MedicationAdministrationRecord
        fields = '__all__'
        read_only_fields = ('given_by', 'created_at')
