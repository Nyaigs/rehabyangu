from rest_framework.permissions import BasePermission
from .exceptions import FeatureNotInPlan
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
        if not getattr(request, 'tenant_membership', None):
            return False
        return self.codename in get_user_permissions(request.user, request.tenant)

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if not getattr(request, 'tenant_membership', None):
            return False
        return self.codename in get_user_permissions(request.user, request.tenant)


class HasAnyPermission(BasePermission):
    """Tenant-scoped OR permission check for deliberately limited views."""
    def __init__(self, *codenames):
        self.codenames = codenames

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        if not getattr(request, 'tenant_membership', None):
            return False
        return bool(set(self.codenames) & get_user_permissions(request.user, request.tenant))


class HasFeature(BasePermission):
    def __init__(self, feature):
        self.feature = feature

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        tenant = getattr(request, 'tenant', None)
        if not tenant or not tenant.plan_fk or not (tenant.plan_fk.feature_flags or {}).get(self.feature):
            raise FeatureNotInPlan(self.feature)
        return True
