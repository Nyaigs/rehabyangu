from rest_framework import serializers
from .models import VitalSign, VitalNormalRange

class VitalSignSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    
    class Meta:
        model = VitalSign
        fields = '__all__'
        read_only_fields = ('tenant', 'recorded_by', 'recorded_at', 'bmi')


class VitalNormalRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalNormalRange
        fields = '__all__'
        read_only_fields = ('tenant',)
