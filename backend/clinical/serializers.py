from rest_framework import serializers
from .models import ClinicalNote

class ClinicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = '__all__'
        read_only_fields = ('date',)