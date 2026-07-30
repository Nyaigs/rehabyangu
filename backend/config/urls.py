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
)
from sponsors.views import SponsorViewSet
from users.views import StaffListView, CreateStaffView
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
from .views import UserListView, CurrentUserView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'sponsors', SponsorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'clinical-notes', ClinicalNoteViewSet)
router.register(r'inventory', InventoryItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('vitals.urls')),
    path('api/', include('billing.urls')),   # includes charge, patient-bill, invoices, etc.
    path('api/', include('subscriptions.urls')),
    path('api/', include('authorization.urls')),
    path('api/', include('tenants.urls')),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/users/me/', CurrentUserView.as_view(), name='current-user'),
    path('api/staff/', StaffListView.as_view(), name='staff-list'),
    path('api/staff/create/', CreateStaffView.as_view(), name='staff-create'),
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
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
