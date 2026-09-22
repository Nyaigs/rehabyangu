from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('patients', '0006_emr_admissions_treatment_plans')]
    operations = [
        migrations.AddField(model_name='admission', name='status', field=models.CharField(choices=[('admitted', 'Admitted'), ('discharged', 'Discharged')], default='admitted', max_length=20)),
        migrations.AddField(model_name='admission', name='length_of_stay_days', field=models.PositiveIntegerField(default=0)),
    ]
