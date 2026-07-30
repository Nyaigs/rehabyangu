from rest_framework.permissions import BasePermission
from .utils import has_permission

class HasPermission(BasePermission):
    """
    DRF permission class that checks if the user has a specific permission codename.
    Usage: permission_classes = [HasPermission('patient:view')]
    Supports object-level permissions via has_object_permission.
    """
    def __init__(self, codename):
        self.codename = codename

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return has_permission(request.user, self.codename)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return has_permission(request.user, self.codename, resource=obj)
