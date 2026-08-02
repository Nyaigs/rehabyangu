from django.urls import path
from .views import (
    TenantListView,
    CreateTenantView,
    TenantStatsView,
    ToggleTenantStatusView,
    ExtendTrialView,
    TenantStaffListView,
    TenantConfigView,
)

urlpatterns = [
    path('tenants/', TenantListView.as_view(), name='tenant-list'),
    path('tenants/stats/', TenantStatsView.as_view(), name='tenant-stats'),
    path('tenants/create/', CreateTenantView.as_view(), name='create-tenant'),
    path('tenants/<int:pk>/toggle-status/', ToggleTenantStatusView.as_view(), name='toggle-status'),
    path('tenants/<int:pk>/extend-trial/', ExtendTrialView.as_view(), name='extend-trial'),
    path('tenants/<int:pk>/staff/', TenantStaffListView.as_view(), name='tenant-staff'),
    path('tenant-config/', TenantConfigView.as_view(), name='tenant-config'),
]
