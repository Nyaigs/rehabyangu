from django.contrib import admin
from .models import Permission, Role

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['codename', 'name', 'category']
    search_fields = ['codename', 'name']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant']
    filter_horizontal = ['permissions']
