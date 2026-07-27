from rest_framework import serializers
from .models import Appointment
from patients.models import Patient
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    clinician_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def get_clinician_name(self, obj):
        return f"{obj.clinician.first_name} {obj.clinician.last_name}" if obj.clinician else None