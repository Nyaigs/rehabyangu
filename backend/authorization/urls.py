from django.urls import path
from .views import UserPermissionsView, PermissionListView, RoleListView, RoleDetailView

urlpatterns = [
    path('user/permissions/', UserPermissionsView.as_view(), name='user-permissions'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', RoleDetailView.as_view(), name='role-detail'),
]
