from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'intake_date', 'status']
    search_fields = ['first_name', 'last_name', 'phone']
    list_filter = ['status', 'gender']
    ordering = ['-intake_date']