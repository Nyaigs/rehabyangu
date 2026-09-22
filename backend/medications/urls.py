from rest_framework.routers import DefaultRouter
from .views import MedicationViewSet, PrescriptionViewSet, MARViewSet
router = DefaultRouter()
router.register('medications', MedicationViewSet, basename='medication')
router.register('prescriptions', PrescriptionViewSet, basename='prescription')
router.register('mar', MARViewSet, basename='mar')
urlpatterns = router.urls
