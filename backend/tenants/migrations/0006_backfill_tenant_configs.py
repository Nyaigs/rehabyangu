from django.db import migrations


def create_missing_configs(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    TenantConfig = apps.get_model('tenants', 'TenantConfig')

    for tenant in Tenant.objects.iterator():
        TenantConfig.objects.get_or_create(
            tenant_id=tenant.id,
            defaults={
                'company_name': tenant.name,
                'footer_text': f'{tenant.name} – Powered by RehabYangu',
            },
        )


class Migration(migrations.Migration):
    dependencies = [('tenants', '0005_tenantconfig_letterhead')]

    operations = [migrations.RunPython(create_missing_configs, migrations.RunPython.noop)]
