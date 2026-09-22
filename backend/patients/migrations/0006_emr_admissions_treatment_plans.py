from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


RLS_SQL = '''
DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY['patients_admission', 'patients_treatmentplan', 'patients_treatmentgoal'] LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', table_name);
    EXECUTE format('CREATE POLICY tenant_isolation ON public.%I USING (tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin()) WITH CHECK (tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())', table_name);
  END LOOP;
END $$;
'''


class Migration(migrations.Migration):
    dependencies = [
        ('patients', '0005_patient_patient_id'),
        ('tenants', '0008_tenantconfig_onboarding_completed_at'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name='patient', name='hiv_status', field=models.CharField(blank=True, max_length=30, null=True)),
        migrations.AddField(model_name='patient', name='national_id', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.AddField(model_name='patient', name='next_of_kin_relationship', field=models.CharField(blank=True, max_length=100, null=True)),
        migrations.CreateModel(
            name='Admission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admission_number', models.CharField(editable=False, max_length=32, unique=True)),
                ('intake_date', models.DateTimeField()), ('discharge_date', models.DateTimeField(blank=True, null=True)),
                ('room', models.CharField(blank=True, max_length=100)), ('bed', models.CharField(blank=True, max_length=100)),
                ('primary_diagnosis', models.TextField(blank=True)), ('psychiatric_diagnosis', models.TextField(blank=True)),
                ('substance_use_history', models.JSONField(blank=True, default=dict)), ('medical_history', models.TextField(blank=True)),
                ('allergies', models.JSONField(blank=True, default=list)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='admissions_created', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='admissions', to='patients.patient')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='admissions', to='tenants.tenant')),
            ], options={'ordering': ['-intake_date']},
        ),
        migrations.CreateModel(
            name='TreatmentPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)), ('diagnosis_summary', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='draft', max_length=20)),
                ('start_date', models.DateField()), ('target_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('admission', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='treatment_plans', to='patients.admission')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='treatment_plans_created', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='treatment_plans', to='patients.patient')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatment_plans', to='tenants.tenant')),
            ], options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='TreatmentGoal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()), ('target_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('not_started', 'Not started'), ('in_progress', 'In progress'), ('achieved', 'Achieved'), ('discontinued', 'Discontinued')], default='not_started', max_length=20)),
                ('progress_percent', models.PositiveSmallIntegerField(default=0)), ('progress_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='treatment_goals', to='tenants.tenant')),
                ('treatment_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goals', to='patients.treatmentplan')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='treatment_goals_updated', to=settings.AUTH_USER_MODEL)),
            ], options={'ordering': ['target_date', 'created_at']},
        ),
        migrations.AddConstraint(model_name='admission', constraint=models.UniqueConstraint(condition=models.Q(discharge_date__isnull=True), fields=('patient',), name='one_open_admission_per_patient')),
        migrations.RunSQL(RLS_SQL, migrations.RunSQL.noop),
    ]
