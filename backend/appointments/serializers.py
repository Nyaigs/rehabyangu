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

    def validate(self, attrs):
        request = self.context['request']
        start, end = attrs.get('start_time', getattr(self.instance, 'start_time', None)), attrs.get('end_time', getattr(self.instance, 'end_time', None))
        clinician = attrs.get('clinician', getattr(self.instance, 'clinician', None))
        room = attrs.get('room', getattr(self.instance, 'room', ''))
        if start and end and end <= start:
            raise serializers.ValidationError({'end_time': 'End time must be after start time.'})
        conflicts = Appointment.objects.filter(tenant=request.tenant, start_time__lt=end, end_time__gt=start).exclude(status__in=['cancelled', 'no_show'])
        if self.instance: conflicts = conflicts.exclude(pk=self.instance.pk)
        if conflicts.filter(clinician=clinician).exists():
            raise serializers.ValidationError({'clinician': 'This clinician is already booked for that time.'})
        if room and conflicts.filter(room=room).exists():
            raise serializers.ValidationError({'room': 'This room is already booked for that time.'})
        return attrs
