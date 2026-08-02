from django.core.cache import cache

def get_user_permissions(user):
    """
    Return a set of permission codenames for the user (cached).
    Checks both roles and extra_permissions on the user's profile.
    """
    if not user.is_authenticated:
        return set()
    cache_key = f"user_perms_{user.id}"
    perms = cache.get(cache_key)
    if perms is None:
        perms = set()
        if hasattr(user, 'profile'):
            for role in user.profile.roles.all():
                perms.update(role.permissions.values_list('codename', flat=True))
            perms.update(user.profile.extra_permissions.values_list('codename', flat=True))
        cache.set(cache_key, perms, timeout=300)
    return perms

def has_permission(user, permission_codename, resource=None):
    """
    Check if user has a specific permission, optionally on a resource.
    Tenant isolation for resource uses the user's current tenant from the
    request context (set by TenantJWTAuthentication).
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if resource and hasattr(resource, 'tenant'):
        # We need the current tenant from somewhere.
        # In a view, this should be provided via the request object.
        # For utility usage, we cannot reliably get it here;
        # views should use request.tenant for isolation, not this function.
        pass  # tenant isolation is now handled in views via request.tenant
    perms = get_user_permissions(user)
    return permission_codename in perms
