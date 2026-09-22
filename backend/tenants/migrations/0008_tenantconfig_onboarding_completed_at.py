from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tenants', '0007_enable_tenant_rls')]

    operations = [
        migrations.AddField(
            model_name='tenantconfig',
            name='onboarding_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
