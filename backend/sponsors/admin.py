from django.contrib import admin
from .models import Sponsor

@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'patient', 'relationship', 'phone']
    search_fields = ['full_name', 'patient__first_name', 'patient__last_name']