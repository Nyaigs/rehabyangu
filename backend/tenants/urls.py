from django.urls import path
from .views import (
    TenantListView,
    CreateTenantView,
    TenantStatsView,
    ToggleTenantStatusView,
    ExtendTrialView,
    TenantStaffListView,
    TenantConfigView,
    TenantLoginBrandingView,
    DashboardStatsView,
    TenantPlanView,
    AvailablePlansView,
)
from .admin_views import PlatformStatsView, PlatformTenantListCreateView, PlatformTenantDetailView, PlatformTenantPaymentReminderView, PlatformPlanListCreateView, PlatformPlanDetailView

urlpatterns = [
    path('admin/stats/', PlatformStatsView.as_view(), name='platform-admin-stats'),
    path('admin/tenants/', PlatformTenantListCreateView.as_view(), name='platform-admin-tenants'),
    path('admin/tenants/<int:pk>/', PlatformTenantDetailView.as_view(), name='platform-admin-tenant-detail'),
    path('admin/tenants/<int:pk>/payment-reminder/', PlatformTenantPaymentReminderView.as_view(), name='platform-admin-tenant-payment-reminder'),
    path('admin/plans/', PlatformPlanListCreateView.as_view(), name='platform-admin-plans'),
    path('admin/plans/<int:pk>/', PlatformPlanDetailView.as_view(), name='platform-admin-plan-detail'),
    path('tenants/', TenantListView.as_view(), name='tenant-list'),
    path('tenants/stats/', TenantStatsView.as_view(), name='tenant-stats'),
    path('tenants/create/', CreateTenantView.as_view(), name='create-tenant'),
    path('tenants/<int:pk>/toggle-status/', ToggleTenantStatusView.as_view(), name='toggle-status'),
    path('tenants/<int:pk>/extend-trial/', ExtendTrialView.as_view(), name='extend-trial'),
    path('tenants/<int:pk>/staff/', TenantStaffListView.as_view(), name='tenant-staff'),
    path('tenant-plan/', TenantPlanView.as_view(), name='tenant-plan'),
    path('tenant-plan/available/', AvailablePlansView.as_view(), name='available-plans'),
    path('tenant-config/', TenantConfigView.as_view(), name='tenant-config'),
    path('tenant-branding/', TenantLoginBrandingView.as_view(), name='tenant-login-branding'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
