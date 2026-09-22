from django.db import migrations


REMAINING_LEGACY_PERMISSIONS = {
    'appointment:manage': 'appointment.write',
    'clinical:view': 'clinical.read',
    'invoice:generate': 'invoice.write',
}

EMR_ROLE_PERMISSIONS = {
    'nurse': {'patient.read', 'clinical.read', 'mfa.manage_self'},
    'psychiatrist': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'mfa.manage_self'},
    'rehab admin': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'discharge.request', 'discharge.approve', 'role.read', 'mfa.manage_self'},
    'rehab administrator': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'discharge.request', 'discharge.approve', 'role.read', 'mfa.manage_self'},
}


def forwards(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.is_platform_admin', 'true', true)")
    Permission = apps.get_model('authorization', 'Permission')
    Role = apps.get_model('authorization', 'Role')

    for legacy_codename, canonical_codename in REMAINING_LEGACY_PERMISSIONS.items():
        legacy = Permission.objects.filter(codename=legacy_codename).first()
        if not legacy:
            continue
        canonical = Permission.objects.get(codename=canonical_codename)
        for role in legacy.role_set.all():
            role.permissions.add(canonical)
        for membership in legacy.membership_grants.all():
            membership.extra_permissions.add(canonical)
        legacy.delete()

    for role in Role.objects.all().prefetch_related('permissions'):
        codenames = EMR_ROLE_PERMISSIONS.get(role.name.strip().lower())
        if codenames:
            role.permissions.add(*Permission.objects.filter(codename__in=codenames))


class Migration(migrations.Migration):
    dependencies = [('authorization', '0004_canonical_permissions_and_emr_roles')]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
