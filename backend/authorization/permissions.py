from rest_framework.permissions import BasePermission
from .utils import get_user_permissions


class HasPermission(BasePermission):
    """
    DRF permission class that checks if the user has a specific permission codename.
    Use this with a view's `get_permissions()` method, because it is a
    parameterised permission instance rather than a zero-argument DRF class.
    Supports object-level permissions via has_object_permission.
    """
    def __init__(self, codename):
        self.codename = codename

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return self.codename in get_user_permissions(request.user, getattr(request, 'tenant', None))

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return self.codename in get_user_permissions(request.user, getattr(request, 'tenant', None))
