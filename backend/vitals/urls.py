from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VitalSignViewSet, VitalNormalRangeViewSet

router = DefaultRouter()
router.register(r'vitals', VitalSignViewSet, basename='vitals')
router.register(r'vital-ranges', VitalNormalRangeViewSet, basename='vital-ranges')

urlpatterns = [
    path('', include(router.urls)),
]
