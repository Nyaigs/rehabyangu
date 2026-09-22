from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patients.views import (
    PatientViewSet,
    RequestDischargeView,
    ApproveDischargeView,
    RejectDischargeView,
    PendingDischargesView,
    DischargedPatientsView,
    AdmissionViewSet,
    TreatmentPlanViewSet,
    TreatmentGoalViewSet,
)
from sponsors.views import SponsorViewSet
from users.views import StaffListView, CreateStaffView, StaffDetailView
from appointments.views import AppointmentViewSet
from clinical.views import ClinicalNoteViewSet
from inventory.views import InventoryItemViewSet
from billing.views import ChargePatientView, PatientBillView, InvoiceDownloadByTokenView
from tenants.views import (
    TenantListView,
    CreateTenantView,
    TenantStatsView,
    ToggleTenantStatusView,
    ExtendTrialView,
    TenantStaffListView,
    TenantConfigView,
)
from .views import UserListView, CurrentUserView, TenantMediaView
from users.views_auth import TenantTokenObtainPairView, TenantTokenRefreshView, LogoutView, InvitationAcceptView
from users.views import TenantAuditLogView
from users.views_mfa import MfaSetupView, MfaConfirmView, MfaPolicyView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'admissions', AdmissionViewSet, basename='admission')
router.register(r'treatment-plans', TreatmentPlanViewSet, basename='treatment-plan')
router.register(r'treatment-goals', TreatmentGoalViewSet, basename='treatment-goal')
router.register(r'sponsors', SponsorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'clinical-notes', ClinicalNoteViewSet, basename='clinical-note')
router.register(r'inventory', InventoryItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('vitals.urls')),
    path('api/', include('medications.urls')),
    path('api/', include('billing.urls')),   # includes charge, patient-bill, invoices, etc.
    path('api/', include('subscriptions.urls')),
    path('api/', include('authorization.urls')),
    path('api/', include('tenants.urls')),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/users/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/staff/', StaffListView.as_view(), name='staff-list'),
    path('api/staff/create/', CreateStaffView.as_view(), name='staff-create'),
    path('api/staff/<int:pk>/', StaffDetailView.as_view(), name='staff-detail'),
    path('api/charge/', ChargePatientView.as_view(), name='charge-patient'),
    path('api/patient-bill/<int:patient_id>/', PatientBillView.as_view(), name='patient-bill'),
    path('api/patients/<int:pk>/request-discharge/', RequestDischargeView.as_view(), name='request-discharge'),
    path('api/discharge-requests/<int:pk>/approve/', ApproveDischargeView.as_view(), name='approve-discharge'),
    path('api/discharge-requests/<int:pk>/reject/', RejectDischargeView.as_view(), name='reject-discharge'),
    path('api/discharge-requests/pending/', PendingDischargesView.as_view(), name='pending-discharges'),
    path('api/discharged-patients/', DischargedPatientsView.as_view(), name='discharged-patients'),
    # Secure invoice download (public, token-based)
    path('invoice/download/<uuid:token>/', InvoiceDownloadByTokenView.as_view(), name='download-invoice-token'),
    # Auth
    path('api/token/', TenantTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TenantTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/invitations/accept/', InvitationAcceptView.as_view(), name='invitation-accept'),
    path('api/mfa/setup/', MfaSetupView.as_view(), name='mfa-setup'),
    path('api/mfa/devices/<int:pk>/confirm/', MfaConfirmView.as_view(), name='mfa-confirm'),
    path('api/mfa/policy/', MfaPolicyView.as_view(), name='mfa-policy'),
    path('api/audit-logs/', TenantAuditLogView.as_view(), name='tenant_audit_logs'),
    path('media/<path:path>', TenantMediaView.as_view(), name='tenant-media'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
