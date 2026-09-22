from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tenants', '0009_tenant_plan_fk')]

    operations = [
        migrations.AddField(
            model_name='tenant', name='archived_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
