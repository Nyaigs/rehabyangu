from django.urls import path
from .views import UserPermissionsView

urlpatterns = [
    path('api/user/permissions/', UserPermissionsView.as_view(), name='user-permissions'),
]
