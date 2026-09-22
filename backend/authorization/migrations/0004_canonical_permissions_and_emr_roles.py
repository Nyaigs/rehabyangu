from django.db import migrations


CANONICAL_PERMISSIONS = {
    'tenant.manage': ('Manage tenants', 'tenant'),
    'staff.read': ('View staff', 'staff'),
    'staff.invite': ('Invite staff', 'staff'),
    'staff.manage': ('Manage staff', 'staff'),
    'role.read': ('View roles', 'role'),
    'role.manage': ('Manage roles', 'role'),
    'mfa.manage_self': ('Manage own MFA', 'mfa'),
    'mfa.manage_policy': ('Manage MFA policy', 'mfa'),
    'patient.read': ('View patients', 'patient'),
    'patient.write': ('Manage patients', 'patient'),
    'clinical.read': ('View clinical records', 'clinical'),
    'clinical.write': ('Manage clinical records', 'clinical'),
    'clinical.sensitive.read': ('View highly sensitive clinical fields', 'clinical'),
    'clinical.sensitive.write': ('Edit highly sensitive clinical fields', 'clinical'),
    'appointment.read': ('View appointments', 'appointment'),
    'appointment.write': ('Manage appointments', 'appointment'),
    'billing.read': ('View billing', 'billing'),
    'billing.write': ('Manage billing', 'billing'),
    'invoice.read': ('View invoices', 'billing'),
    'invoice.write': ('Manage invoices', 'billing'),
    'invoice.send': ('Send invoices', 'billing'),
    'vitals.read': ('View vitals', 'vitals'),
    'vitals.write': ('Record vitals', 'vitals'),
    'inventory.read': ('View inventory', 'inventory'),
    'inventory.write': ('Manage inventory', 'inventory'),
    'discharge.request': ('Request discharge', 'discharge'),
    'discharge.approve': ('Approve discharge', 'discharge'),
}

LEGACY_TO_CANONICAL = {
    'patient:view': 'patient.read', 'patient:create': 'patient.write', 'patient:edit': 'patient.write', 'patient:delete': 'patient.write',
    'clinicalnote:view': 'clinical.read', 'clinicalnote:create': 'clinical.write', 'clinicalnote:edit': 'clinical.write', 'clinical:manage': 'clinical.write',
    'appointment:view': 'appointment.read', 'appointment:create': 'appointment.write', 'appointment:edit': 'appointment.write',
    'billing:view': 'billing.read', 'billing:create': 'billing.write',
    'invoice:view': 'invoice.read', 'invoice:create': 'invoice.write', 'invoice:send': 'invoice.send',
    'vitals:view': 'vitals.read', 'vitals:create': 'vitals.write',
    'inventory:view': 'inventory.read', 'inventory:manage': 'inventory.write',
    'discharge:request': 'discharge.request', 'discharge:approve': 'discharge.approve',
    'staff:view': 'staff.read', 'staff:manage': 'staff.manage', 'tenant:manage': 'tenant.manage',
}

ROLE_PERMISSIONS = {
    'Nurse': {'patient.read', 'clinical.read', 'mfa.manage_self'},
    'Psychiatrist': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'mfa.manage_self'},
    'Rehab Admin': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'discharge.request', 'discharge.approve', 'role.read', 'mfa.manage_self'},
    'Rehab Administrator': {'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'discharge.request', 'discharge.approve', 'role.read', 'mfa.manage_self'},
}


def set_platform_admin(schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.is_platform_admin', 'true', true)")


def forwards(apps, schema_editor):
    set_platform_admin(schema_editor)
    Permission = apps.get_model('authorization', 'Permission')
    Role = apps.get_model('authorization', 'Role')
    TenantMembership = apps.get_model('users', 'TenantMembership')
    canonical = {
        codename: Permission.objects.get_or_create(codename=codename, defaults={'name': name, 'category': category})[0]
        for codename, (name, category) in CANONICAL_PERMISSIONS.items()
    }

    for legacy_codename, canonical_codename in LEGACY_TO_CANONICAL.items():
        legacy = Permission.objects.filter(codename=legacy_codename).first()
        if not legacy:
            continue
        for role in legacy.role_set.all():
            role.permissions.add(canonical[canonical_codename])
        for membership in legacy.membership_grants.all():
            membership.extra_permissions.add(canonical[canonical_codename])
        legacy.delete()

    default_roles = {}
    for role_name, codenames in ROLE_PERMISSIONS.items():
        role, _ = Role.objects.get_or_create(name=role_name, tenant=None)
        role.permissions.add(*(canonical[codename] for codename in codenames))
        default_roles[role_name] = role

    # Some deployments only populated TenantMembership.role. Attach the
    # matching global default role so Membership remains the sole authority.
    legacy_role_names = {
        'nurse': 'Nurse', 'psychiatrist': 'Psychiatrist',
        'rehab_admin': 'Rehab Admin', 'rehab administrator': 'Rehab Administrator',
    }
    for membership in TenantMembership.objects.all().iterator():
        role_name = legacy_role_names.get((membership.role or '').strip().lower())
        if role_name:
            membership.roles.add(default_roles[role_name])


def backwards(apps, schema_editor):
    # Canonical permissions are intentionally retained on rollback: removing
    # them would silently strip permissions from tenant membership records.
    pass


class Migration(migrations.Migration):
    dependencies = [('authorization', '0003_alter_permission_id_alter_role_id'), ('users', '0010_auditlog_read_action')]

    operations = [migrations.RunPython(forwards, backwards)]
