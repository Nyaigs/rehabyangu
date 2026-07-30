from django.contrib import admin
from .models import Tenant, TenantConfig

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'status', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['name', 'subdomain']

@admin.register(TenantConfig)
class TenantConfigAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'company_name', 'primary_color']
    search_fields = ['tenant__name']
