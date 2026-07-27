from django.contrib import admin
from .models import ClinicalNote

@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'clinician', 'date']
    search_fields = ['patient__first_name', 'patient__last_name']