from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('patients', '0007_admission_stay_workflow')]

    operations = [
        migrations.AddField(model_name='patient', name='care_type', field=models.CharField(choices=[('inpatient', 'Inpatient'), ('outpatient', 'Outpatient'), ('day_patient', 'Day Patient'), ('new_referral', 'New Referral')], default='new_referral', max_length=20)),
        migrations.AddField(model_name='patient', name='expected_frequency', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='patient', name='preferred_visit_days', field=models.JSONField(blank=True, default=list)),
        migrations.AddField(model_name='patient', name='referral_source', field=models.CharField(blank=True, max_length=200)),
        migrations.AlterField(model_name='patient', name='status', field=models.CharField(choices=[('registered', 'Registered / New'), ('active', 'Active'), ('inactive', 'Inactive'), ('discharged', 'Discharged'), ('transferred', 'Transferred')], default='registered', max_length=20)),
    ]
