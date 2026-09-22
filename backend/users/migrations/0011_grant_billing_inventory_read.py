from django.db import migrations


def grant_inventory_catalog_access(apps, schema_editor):
    """Billing staff need read-only inventory data to select chargeable items."""
    Permission = apps.get_model('authorization', 'Permission')
    Role = apps.get_model('authorization', 'Role')
    permission = Permission.objects.filter(codename='inventory.read').first()
    if not permission:
        return
    for role in Role.objects.filter(name='Billing').iterator():
        role.permissions.add(permission)


class Migration(migrations.Migration):
    dependencies = [('users', '0010_auditlog_read_action'), ('authorization', '0005_remove_remaining_legacy_permissions')]

    operations = [migrations.RunPython(grant_inventory_catalog_access, migrations.RunPython.noop)]
