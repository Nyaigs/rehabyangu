from django.db import migrations


FORWARD_SQL = r'''
CREATE OR REPLACE FUNCTION public.rehabyangu_current_tenant_id()
RETURNS bigint LANGUAGE sql STABLE AS $$
    SELECT NULLIF(current_setting('app.tenant_id', true), '')::bigint
$$;
CREATE OR REPLACE FUNCTION public.rehabyangu_is_platform_admin()
RETURNS boolean LANGUAGE sql STABLE AS $$
    SELECT current_setting('app.is_platform_admin', true) = 'true'
$$;

DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'patients_patient', 'appointments_appointment', 'clinical_clinicalnote',
    'billing_patientbill', 'inventory_inventoryitem', 'vitals_vitalsign',
    'sponsors_sponsor', 'subscriptions_subscription', 'subscriptions_paymentrecord',
    'subscriptions_notification', 'tenants_tenantconfig', 'users_tenantmembership',
    'users_auditlog', 'users_invitation', 'users_authsession', 'users_mfapolicy', 'users_totpdevice'
  ] LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', table_name);
    EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON public.%I', table_name);
    EXECUTE format('CREATE POLICY tenant_isolation ON public.%I USING (tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin()) WITH CHECK (tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())', table_name);
  END LOOP;

  ALTER TABLE public.authorization_role ENABLE ROW LEVEL SECURITY;
  ALTER TABLE public.authorization_role FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON public.authorization_role;
  CREATE POLICY tenant_isolation ON public.authorization_role
    USING (tenant_id IS NULL OR tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())
    WITH CHECK (tenant_id IS NULL OR tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin());

  FOREACH table_name IN ARRAY ARRAY[
    'patients_dischargerequest', 'billing_billitem', 'billing_payment', 'billing_invoice',
    'users_tenantmembership_roles', 'users_tenantmembership_extra_permissions', 'users_invitation_roles'
  ] LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY', table_name);
    EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON public.%I', table_name);
  END LOOP;

  CREATE POLICY tenant_isolation ON public.patients_dischargerequest
    USING (EXISTS (SELECT 1 FROM public.patients_patient p WHERE p.id = public.patients_dischargerequest.patient_id AND (p.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.patients_patient p WHERE p.id = public.patients_dischargerequest.patient_id AND (p.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.billing_billitem
    USING (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_billitem.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_billitem.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.billing_payment
    USING (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_payment.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_payment.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.billing_invoice
    USING (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_invoice.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.billing_patientbill b WHERE b.id = public.billing_invoice.bill_id AND (b.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.users_tenantmembership_roles
    USING (EXISTS (SELECT 1 FROM public.users_tenantmembership m WHERE m.id = public.users_tenantmembership_roles.tenantmembership_id AND (m.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.users_tenantmembership m WHERE m.id = public.users_tenantmembership_roles.tenantmembership_id AND (m.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.users_tenantmembership_extra_permissions
    USING (EXISTS (SELECT 1 FROM public.users_tenantmembership m WHERE m.id = public.users_tenantmembership_extra_permissions.tenantmembership_id AND (m.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.users_tenantmembership m WHERE m.id = public.users_tenantmembership_extra_permissions.tenantmembership_id AND (m.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
  CREATE POLICY tenant_isolation ON public.users_invitation_roles
    USING (EXISTS (SELECT 1 FROM public.users_invitation i WHERE i.id = public.users_invitation_roles.invitation_id AND (i.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())))
    WITH CHECK (EXISTS (SELECT 1 FROM public.users_invitation i WHERE i.id = public.users_invitation_roles.invitation_id AND (i.tenant_id = public.rehabyangu_current_tenant_id() OR public.rehabyangu_is_platform_admin())));
END $$;
'''

REVERSE_SQL = r'''
DO $$
DECLARE table_name text;
BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'patients_patient', 'patients_dischargerequest', 'appointments_appointment', 'clinical_clinicalnote',
    'billing_patientbill', 'billing_billitem', 'billing_payment', 'billing_invoice', 'inventory_inventoryitem',
    'vitals_vitalsign', 'sponsors_sponsor', 'subscriptions_subscription', 'subscriptions_paymentrecord',
    'subscriptions_notification', 'tenants_tenantconfig', 'authorization_role', 'users_tenantmembership',
    'users_tenantmembership_roles', 'users_tenantmembership_extra_permissions', 'users_auditlog', 'users_invitation',
    'users_invitation_roles', 'users_authsession', 'users_mfapolicy', 'users_totpdevice'
  ] LOOP
    EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON public.%I', table_name);
    EXECUTE format('ALTER TABLE public.%I NO FORCE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', table_name);
  END LOOP;
END $$;
DROP FUNCTION IF EXISTS public.rehabyangu_is_platform_admin();
DROP FUNCTION IF EXISTS public.rehabyangu_current_tenant_id();
'''


class Migration(migrations.Migration):
    dependencies = [
        ('tenants', '0006_backfill_tenant_configs'), ('users', '0008_mfapolicy_authsession_invitation_totpdevice'),
        ('authorization', '0002_alter_permission_id_alter_role_id'), ('patients', '0005_patient_patient_id'),
        ('appointments', '0002_appointment_tenant'), ('clinical', '0002_clinicalnote_tenant'),
        ('billing', '0004_add_unique_token'), ('inventory', '0002_inventoryitem_cost_price_inventoryitem_product_id_and_more'),
        ('vitals', '0001_initial'), ('sponsors', '0002_sponsor_tenant'), ('subscriptions', '0001_initial'),
    ]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL)]
