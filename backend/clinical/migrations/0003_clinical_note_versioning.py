import uuid

from django.db import migrations, models
import django.db.models.deletion


def backfill_record_ids(apps, schema_editor):
    ClinicalNote = apps.get_model('clinical', 'ClinicalNote')
    # Existing tables already have FORCE RLS enabled. Migration work is an
    # explicit platform-admin operation, never a tenant request.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.is_platform_admin', 'true', true)")
    for note in ClinicalNote.objects.filter(record_id__isnull=True).iterator():
        note.record_id = uuid.uuid4()
        note.version = 1
        note.save(update_fields=['record_id', 'version'])


APPEND_ONLY_SQL = '''
CREATE OR REPLACE FUNCTION public.rehabyangu_reject_clinical_note_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  RAISE EXCEPTION 'clinical notes are append-only; create a correction version instead';
END;
$$;
CREATE TRIGGER clinical_note_append_only
BEFORE UPDATE OR DELETE ON public.clinical_clinicalnote
FOR EACH ROW EXECUTE FUNCTION public.rehabyangu_reject_clinical_note_mutation();
'''


class Migration(migrations.Migration):
    dependencies = [('clinical', '0002_clinicalnote_tenant')]

    operations = [
        migrations.AddField(model_name='clinicalnote', name='record_id', field=models.UUIDField(blank=True, editable=False, null=True)),
        migrations.AddField(model_name='clinicalnote', name='version', field=models.PositiveIntegerField(default=1)),
        migrations.AddField(model_name='clinicalnote', name='correction_reason', field=models.TextField(blank=True)),
        migrations.AddField(model_name='clinicalnote', name='supersedes', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='corrections', to='clinical.clinicalnote')),
        migrations.RunPython(backfill_record_ids, migrations.RunPython.noop),
        migrations.AlterField(model_name='clinicalnote', name='record_id', field=models.UUIDField(default=uuid.uuid4, editable=False)),
        migrations.AddConstraint(model_name='clinicalnote', constraint=models.UniqueConstraint(fields=('record_id', 'version'), name='unique_clinical_note_version')),
        migrations.RunSQL(APPEND_ONLY_SQL, '''DROP TRIGGER IF EXISTS clinical_note_append_only ON public.clinical_clinicalnote; DROP FUNCTION IF EXISTS public.rehabyangu_reject_clinical_note_mutation();'''),
    ]
