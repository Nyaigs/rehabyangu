from django.core.cache import cache

def get_user_permissions(user):
    """
    Return a set of permission codenames for the user (cached).
    """
    if not user.is_authenticated:
        return set()
    cache_key = f"user_perms_{user.id}"
    perms = cache.get(cache_key)
    if perms is None:
        perms = set()
        # Permission from roles
        if hasattr(user, 'profile'):
            for role in user.profile.roles.all():
                perms.update(role.permissions.values_list('codename', flat=True))
            # Extra permissions
            perms.update(user.profile.extra_permissions.values_list('codename', flat=True))
        cache.set(cache_key, perms, timeout=300)  # 5 minutes
    return perms

def has_permission(user, permission_codename, resource=None):
    """
    Check if user has a specific permission, optionally on a resource.
    """
    if not user.is_authenticated:
        return False
    # Superuser bypass (Weiraro)
    if user.is_superuser:
        return True
    # Tenant isolation for resource
    if resource and hasattr(resource, 'tenant'):
        if resource.tenant != user.profile.tenant:
            return False
    perms = get_user_permissions(user)
    return permission_codename in perms
