from django.db import migrations, models
import django.db.models.deletion


def map_legacy_plans(apps, schema_editor):
    Tenant = apps.get_model('tenants', 'Tenant')
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    # Existing names are known legacy choices. Unknown values are deliberately
    # left unassigned for an operator to review rather than guessed.
    mapping = {'basic': 'starter', 'pro': 'professional', 'enterprise': 'enterprise'}
    plans = {plan.code: plan for plan in SubscriptionPlan.objects.filter(code__in=mapping.values())}
    for tenant in Tenant.objects.filter(plan_fk__isnull=True).iterator():
        plan = plans.get(mapping.get(tenant.plan))
        if plan:
            tenant.plan_fk = plan
            tenant.save(update_fields=['plan_fk'])


class Migration(migrations.Migration):
    dependencies = [('tenants', '0008_tenantconfig_onboarding_completed_at'), ('subscriptions', '0002_subscriptionplan_notification_event_key')]

    operations = [
        migrations.AddField(
            model_name='tenant', name='plan_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tenants', to='subscriptions.subscriptionplan'),
        ),
        migrations.RunPython(map_legacy_plans, migrations.RunPython.noop),
    ]
