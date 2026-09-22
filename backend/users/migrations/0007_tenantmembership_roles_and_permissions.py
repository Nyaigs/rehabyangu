from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('authorization', '0001_initial'), ('users', '0006_tenantmembership_tenant_user_id')]

    operations = [
        migrations.AddField(model_name='tenantmembership', name='roles', field=models.ManyToManyField(blank=True, related_name='memberships', to='authorization.role')),
        migrations.AddField(model_name='tenantmembership', name='extra_permissions', field=models.ManyToManyField(blank=True, related_name='membership_grants', to='authorization.permission')),
    ]
