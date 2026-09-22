from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('clinical', '0003_clinical_note_versioning'),
        ('patients', '0006_emr_admissions_treatment_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicalnote',
            name='admission',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clinical_notes', to='patients.admission'),
        ),
    ]
