from django.db import migrations


def copy_profile_permissions(apps, schema_editor):
    UserProfile = apps.get_model('users', 'UserProfile')
    TenantMembership = apps.get_model('users', 'TenantMembership')
    for profile in UserProfile.objects.prefetch_related("roles", "extra_permissions"):
        roles = list(profile.roles.all())
        permissions = list(profile.extra_permissions.all())
        if not roles and not permissions:
            continue
        for membership in TenantMembership.objects.filter(user_id=profile.user_id):
            if roles:
                membership.roles.add(*roles)
            if permissions:
                membership.extra_permissions.add(*permissions)


class Migration(migrations.Migration):
    dependencies = [('users', '0012_authsession_platform_context')]
    operations = [migrations.RunPython(copy_profile_permissions, migrations.RunPython.noop)]
