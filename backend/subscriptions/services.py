"""Central subscription lifecycle and capability rules.

Keeping these rules outside views and management commands makes scheduled runs,
admin mutations, and future payment integrations agree on tenant state.
"""
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification, SubscriptionPlan

GRACE_PERIOD_DAYS = 3


def tenant_has_feature(tenant, feature: str) -> bool:
    return bool(tenant.plan_fk and tenant.plan_fk.feature_flags.get(feature, False))


def tenant_user_capacity(tenant):
    count = tenant.memberships.filter(user__is_active=True).count()
    maximum = tenant.plan_fk.max_users if tenant.plan_fk else None
    return count, maximum, None if maximum is None else max(maximum - count, 0)


def current_mrr():
    """Expected recurring monthly value; trials are intentionally excluded."""
    from tenants.models import Tenant
    return Tenant.objects.filter(status='active', is_active=True, plan_fk__isnull=False).aggregate(
        value=Sum('plan_fk__price_monthly')
    )['value'] or Decimal('0.00')


def _notify_once(tenant, event_key, notification_type, title, message):
    notification, created = Notification.objects.get_or_create(
        event_key=event_key,
        defaults={
            'tenant': tenant, 'notification_type': notification_type,
            'title': title, 'message': message,
        },
    )
    if created:
        # The configured console backend makes this safe in development; a
        # production backend sends the same concise operational notice.
        recipients = list(tenant.memberships.filter(is_rehab_admin=True, user__is_active=True).values_list('user__email', flat=True))
        # A just-provisioned facility may still have only its invitation. Its
        # nominated administrator should not miss trial notices meanwhile.
        recipients += list(tenant.invitations.filter(is_rehab_admin=True, accepted_at__isnull=True, revoked_at__isnull=True).values_list('email', flat=True))
        recipients = [email for email in recipients if email]
        if recipients:
            transaction.on_commit(lambda: send_mail(
                subject=f'RehabYangu: {title}', message=message,
                from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=recipients,
                fail_silently=True,
            ))
    return notification, created


def send_payment_reminder(tenant):
    """Send an administrator-requested reminder through the normal service."""
    due_date = tenant.next_billing_date or tenant.trial_ends_at
    amount = tenant.plan_fk.price_monthly if tenant.plan_fk else tenant.monthly_fee
    suffix = due_date.date().isoformat() if due_date else timezone.now().date().isoformat()
    return _notify_once(
        tenant, f'manual-payment-reminder:{tenant.pk}:{suffix}', 'payment_due',
        'Subscription payment reminder',
        f'KES {amount} is due{f" on {due_date.date()}" if due_date else ""} for {tenant.name}.',
    )


def _set_status(tenant, status, now, *, grace_end=None):
    tenant.status = status
    tenant.is_active = status != 'suspended'
    if grace_end is not None:
        tenant.grace_period_end = grace_end
    if status == 'active':
        tenant.grace_period_end = None
    tenant.save(update_fields=['status', 'is_active', 'grace_period_end'])


@transaction.atomic
def process_tenant_subscription(tenant, now=None):
    """Apply lifecycle changes for one tenant and return whether state changed."""
    now = now or timezone.now()
    # Lock only the tenant row. `plan_fk` is nullable, so PostgreSQL cannot
    # lock every table in the outer join produced by select_related().
    tenant = type(tenant).objects.select_for_update(of=('self',)).select_related('plan_fk').get(pk=tenant.pk)
    changed = False
    plan_amount = tenant.plan_fk.price_monthly if tenant.plan_fk else tenant.monthly_fee

    if tenant.status == 'trial' and tenant.trial_ends_at:
        remaining = tenant.trial_ends_at - now
        if timedelta(0) < remaining <= timedelta(days=3):
            _notify_once(tenant, f'trial-reminder:{tenant.pk}:{tenant.trial_ends_at.date()}', 'trial_ending',
                         'Trial ending soon', f'Your RehabYangu trial for {tenant.name} ends on {tenant.trial_ends_at.date()}.')
        if now >= tenant.trial_ends_at:
            grace_end = tenant.trial_ends_at + timedelta(days=GRACE_PERIOD_DAYS)
            _set_status(tenant, 'overdue', now, grace_end=grace_end)
            _notify_once(tenant, f'trial-overdue:{tenant.pk}:{tenant.trial_ends_at.date()}', 'payment_overdue',
                         'Trial ended — payment due', f'Your trial has ended. KES {plan_amount} is due; access remains available until {grace_end.date()}.')
            changed = True

    if tenant.status == 'active' and tenant.next_billing_date:
        remaining = tenant.next_billing_date - now
        if timedelta(0) < remaining <= timedelta(days=3):
            _notify_once(tenant, f'billing-reminder:{tenant.pk}:{tenant.next_billing_date.date()}', 'payment_due',
                         'Subscription payment due soon', f'KES {plan_amount} for {tenant.name} is due on {tenant.next_billing_date.date()}.')
        if now >= tenant.next_billing_date:
            grace_end = tenant.next_billing_date + timedelta(days=GRACE_PERIOD_DAYS)
            _set_status(tenant, 'overdue', now, grace_end=grace_end)
            _notify_once(tenant, f'billing-overdue:{tenant.pk}:{tenant.next_billing_date.date()}', 'payment_overdue',
                         'Subscription payment is overdue', f'KES {plan_amount} is due. Your grace period ends on {grace_end.date()}.')
            changed = True

    if tenant.status == 'overdue' and tenant.grace_period_end:
        remaining = tenant.grace_period_end - now
        if timedelta(0) < remaining <= timedelta(days=1):
            _notify_once(tenant, f'final-warning:{tenant.pk}:{tenant.grace_period_end.date()}', 'suspension_warning',
                         'Suspension warning', f'Your facility will be suspended on {tenant.grace_period_end.date()} unless payment is received.')
        if now >= tenant.grace_period_end:
            _set_status(tenant, 'suspended', now)
            _notify_once(tenant, f'suspended:{tenant.pk}:{tenant.grace_period_end.date()}', 'suspended',
                         'Account suspended', 'Your RehabYangu account has been suspended because payment was not received.')
            changed = True
    return changed


def process_all_subscriptions(now=None):
    from tenants.models import Tenant
    changes = 0
    for tenant in Tenant.objects.filter(status__in=['trial', 'active', 'overdue']).iterator():
        changes += bool(process_tenant_subscription(tenant, now=now))
    return changes
