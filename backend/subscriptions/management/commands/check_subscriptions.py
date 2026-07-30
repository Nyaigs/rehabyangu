from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import Subscription, Notification
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Check subscription statuses and update tenant statuses, send notifications'

    def handle(self, *args, **options):
        now = timezone.now()
        subscriptions = Subscription.objects.all()

        for sub in subscriptions:
            tenant = sub.tenant
            status_changed = False

            # 1. Trial ending soon (7 days before)
            if sub.trial_ends_at and sub.status == 'trial':
                days_left = (sub.trial_ends_at - now).days
                if days_left == 7:
                    self.send_notification(tenant, 'trial_ending', 'Trial Ending Soon', 
                        f'Your trial for {tenant.name} ends in 7 days. Please upgrade to continue.')
                elif days_left <= 0:
                    # Trial ended -> move to overdue or suspend
                    sub.status = 'overdue'
                    sub.grace_period_end = now + timezone.timedelta(days=7)
                    status_changed = True
                    self.send_notification(tenant, 'payment_overdue', 'Trial Ended',
                        f'Your trial for {tenant.name} has ended. Please subscribe to continue using the system.')

            # 2. Check for payment overdue (if grace period passed)
            if sub.status == 'overdue' and sub.grace_period_end and now > sub.grace_period_end:
                sub.status = 'suspended'
                tenant.status = 'suspended'
                tenant.save()
                status_changed = True
                self.send_notification(tenant, 'suspended', 'Account Suspended',
                    f'Your account for {tenant.name} has been suspended due to non-payment. Contact Weiraro to reactivate.')

            # 3. Payment due soon (7 days before next billing)
            if sub.status == 'active' and sub.next_billing_date:
                days_until = (sub.next_billing_date - now).days
                if days_until == 7:
                    self.send_notification(tenant, 'payment_due', 'Payment Due Soon',
                        f'Your subscription for {tenant.name} is due in 7 days. Please ensure payment to avoid interruption.')

            # 4. Payment overdue (1 day after due date)
            if sub.status == 'active' and sub.next_billing_date and now > sub.next_billing_date:
                sub.status = 'overdue'
                sub.grace_period_end = now + timezone.timedelta(days=7)
                status_changed = True
                self.send_notification(tenant, 'payment_overdue', 'Payment Overdue',
                    f'Payment for {tenant.name} is overdue. Please settle within 7 days to avoid suspension.')

            if status_changed:
                sub.save()
                tenant.status = sub.status
                tenant.save()

            # Save subscription changes
            sub.save()

        self.stdout.write(self.style.SUCCESS('Subscription check completed.'))

    def send_notification(self, tenant, notif_type, title, message):
        from subscriptions.models import Notification
        Notification.objects.create(
            tenant=tenant,
            notification_type=notif_type,
            title=title,
            message=message,
            is_read=False
        )
