from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VitalSignViewSet

router = DefaultRouter()
router.register(r'vitals', VitalSignViewSet, basename='vitals')

urlpatterns = [
    path('', include(router.urls)),
]