from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('vitals', '0001_initial'), ('tenants', '0008_tenantconfig_onboarding_completed_at')]
    operations = [
        migrations.AddField(model_name='vitalsign', name='abnormality_level', field=models.CharField(choices=[('normal', 'Normal'), ('low', 'Low'), ('moderate', 'Moderate'), ('critical', 'Critical')], default='normal', max_length=20)),
        migrations.AddField(model_name='vitalsign', name='abnormal_values', field=models.JSONField(blank=True, default=list)),
        migrations.CreateModel(name='VitalNormalRange', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('metric', models.CharField(max_length=40)), ('low', models.DecimalField(decimal_places=2, max_digits=7)), ('high', models.DecimalField(decimal_places=2, max_digits=7)), ('critical_low', models.DecimalField(decimal_places=2, max_digits=7)), ('critical_high', models.DecimalField(decimal_places=2, max_digits=7)), ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vital_ranges', to='tenants.tenant'))]),
        migrations.AddConstraint(model_name='vitalnormalrange', constraint=models.UniqueConstraint(fields=('tenant', 'metric'), name='unique_vital_range_per_tenant')),
    ]
