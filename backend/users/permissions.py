from rest_framework.permissions import BasePermission

class IsInTenant(BasePermission):
    def has_permission(self, request, view):
        return request.tenant is not None

class IsRehabAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.tenant_membership and
            request.tenant_membership.is_rehab_admin
        )

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class HasRole(BasePermission):
    allowed_roles = []
    def has_permission(self, request, view):
        return (
            request.tenant_membership and
            request.tenant_membership.role in self.allowed_roles
        )
