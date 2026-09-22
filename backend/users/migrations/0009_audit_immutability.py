from django.db import migrations

FORWARD_SQL = '''
CREATE OR REPLACE FUNCTION public.reject_auditlog_mutation()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'audit log is append-only: % operation not allowed', TG_OP;
END;
$$;
CREATE TRIGGER auditlog_no_update BEFORE UPDATE ON public.users_auditlog
    FOR EACH ROW EXECUTE FUNCTION public.reject_auditlog_mutation();
CREATE TRIGGER auditlog_no_delete BEFORE DELETE ON public.users_auditlog
    FOR EACH ROW EXECUTE FUNCTION public.reject_auditlog_mutation();
'''

REVERSE_SQL = '''
DROP TRIGGER IF EXISTS auditlog_no_update ON public.users_auditlog;
DROP TRIGGER IF EXISTS auditlog_no_delete ON public.users_auditlog;
DROP FUNCTION IF EXISTS public.reject_auditlog_mutation();
'''

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0008_mfapolicy_authsession_invitation_totpdevice'),
    ]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL)]
