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

        # A4-2: reject fractional doses for whole-unit forms (tablets, capsules).
        # Only validated when dose is a bare number. Doses like "500mg" represent
        # tablet strength (see Medication.strength), not unit count — outside scope.
        medication = attrs.get('medication') or getattr(self.instance, 'medication', None)
        dose = attrs.get('dose') or getattr(self.instance, 'dose', None)
        if medication and dose:
            form = (medication.form or '').strip().lower()
            if form in ('tablet', 'tablets', 'capsule', 'capsules'):
                try:
                    value = float(dose.strip())
                except (ValueError, TypeError):
                    pass  # non-numeric dose (units appended) — skip
                else:
                    if value <= 0:
                        raise serializers.ValidationError({'dose': 'Dose must be greater than zero.'})
                    if value != int(value):
                        raise serializers.ValidationError({
                            'dose': f'Dose for {form} must be a whole number (e.g., "2", not "2.5").'
                        })

        return attrs


class MARSerializer(serializers.ModelSerializer):
    given_by_name = serializers.CharField(source='given_by.username', read_only=True)
    medication_name = serializers.CharField(source='prescription.medication.__str__', read_only=True)
    patient = serializers.IntegerField(source='prescription.patient_id', read_only=True)
    class Meta:
        model = MedicationAdministrationRecord
        fields = '__all__'
        read_only_fields = ('given_by', 'created_at')
