from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tenants', '0004_tenant_monthly_fee')]
    operations = [migrations.AddField(model_name='tenantconfig', name='letterhead', field=models.ImageField(blank=True, null=True, upload_to='letterheads/'))]
