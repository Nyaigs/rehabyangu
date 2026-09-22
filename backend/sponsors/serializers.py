from rest_framework import serializers
from .models import Sponsor

class SponsorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sponsor
        fields = '__all__'
        read_only_fields = ('tenant', 'created_at')

    def validate_patient(self, patient):
        request = self.context['request']
        if patient.tenant_id != request.tenant.id:
            raise serializers.ValidationError('Patient is outside this tenant.')
        return patient
