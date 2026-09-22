from django.core.cache import cache
from django.db.models import Q

def get_user_permissions(user, tenant=None):
    """
    Return a set of permission codenames for the user (cached).
    TenantMembership is the source of truth for tenant-scoped permissions.
    """
    if not user.is_authenticated:
        return set()
    if user.is_superuser:
        from .models import Permission
        return set(Permission.objects.values_list('codename', flat=True))
    cache_key = f"user_perms_{user.id}_{getattr(tenant, 'id', 'global')}"
    perms = cache.get(cache_key)
    if perms is None:
        perms = set()
        membership = user.tenant_memberships.filter(tenant=tenant).first() if tenant else None
        if membership:
            if membership.is_rehab_admin:
                from .models import Permission
                perms.update(Permission.objects.values_list('codename', flat=True))
            roles = membership.roles.filter(Q(tenant=tenant) | Q(tenant__isnull=True))
            for role in roles:
                perms.update(role.permissions.values_list('codename', flat=True))
            perms.update(membership.extra_permissions.values_list('codename', flat=True))
        cache.set(cache_key, perms, timeout=300)
    return perms
