from rest_framework import serializers

from .models import ClinicalNote


class ClinicalNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='clinician.get_full_name', read_only=True)

    class Meta:
        model = ClinicalNote
        fields = '__all__'
        read_only_fields = ('tenant', 'clinician', 'date', 'record_id', 'version', 'supersedes', 'correction_reason')

    def validate_patient(self, patient):
        request = self.context['request']
        if patient.tenant_id != request.tenant.id:
            raise serializers.ValidationError('Patient is outside this tenant.')
        return patient

    def validate(self, attrs):
        admission = attrs.get('admission')
        patient = attrs.get('patient')
        if admission and (admission.tenant_id != self.context['request'].tenant.id or admission.patient_id != patient.id):
            raise serializers.ValidationError({'admission': 'Admission must belong to this patient and tenant.'})
        return attrs


class ClinicalNoteCorrectionSerializer(serializers.ModelSerializer):
    correction_reason = serializers.CharField(min_length=3)

    class Meta:
        model = ClinicalNote
        fields = ('subjective', 'objective', 'assessment', 'plan', 'correction_reason')
