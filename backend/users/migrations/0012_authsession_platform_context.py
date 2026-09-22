from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('users', '0011_grant_billing_inventory_read')]

    operations = [
        migrations.AlterField(
            model_name='authsession', name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auth_sessions', to='tenants.tenant'),
        ),
    ]
