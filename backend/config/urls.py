from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from patients.views import PatientViewSet
from sponsors.views import SponsorViewSet
from appointments.views import AppointmentViewSet
from clinical.views import ClinicalNoteViewSet
from .views import UserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'patients', PatientViewSet)
router.register(r'sponsors', SponsorViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'clinical-notes', ClinicalNoteViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/users/', UserListView.as_view(), name='user-list'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
