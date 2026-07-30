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
    path('api/tenants/', TenantListView.as_view(), name='tenant-list'),
    path('api/tenants/stats/', TenantStatsView.as_view(), name='tenant-stats'),
    path('api/tenants/create/', CreateTenantView.as_view(), name='create-tenant'),
    path('api/tenants/<int:pk>/toggle-status/', ToggleTenantStatusView.as_view(), name='toggle-status'),
    path('api/tenants/<int:pk>/extend-trial/', ExtendTrialView.as_view(), name='extend-trial'),
    path('api/tenants/<int:pk>/staff/', TenantStaffListView.as_view(), name='tenant-staff'),
    path('api/tenant-config/', TenantConfigView.as_view(), name='tenant-config'),
]
