from django.core.management.base import BaseCommand
from django.utils import timezone
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Update tenant subscription statuses based on billing dates.'

    def handle(self, *args, **options):
        now = timezone.now()
        self.stdout.write(f'Running subscription check at {now}')

        # 1. Activate tenants whose trial has not ended
        # (if they were trial and trial_ends_at is in the future, status can stay trial)
        # Not strictly necessary but can be used to fix inconsistencies.

        # 2. Overdue: trial ended and no payment, but within grace period
        tenants = Tenant.objects.filter(
            status='trial',
            trial_ends_at__lt=now,
            grace_period_end__gt=now
        )
        count = tenants.update(status='overdue')
        self.stdout.write(f'Marked {count} tenants as overdue (trial expired, within grace).')

        # 3. Suspend: both trial and grace period have passed
        tenants = Tenant.objects.filter(
            status__in=['trial', 'overdue'],
            grace_period_end__lt=now
        )
        count = tenants.update(status='suspended', is_active=False)
        self.stdout.write(f'Suspended {count} tenants (grace period ended).')

        # 4. If tenant is active with next_billing_date in the past, mark overdue
        tenants = Tenant.objects.filter(
            status='active',
            next_billing_date__lt=now,
            next_billing_date__isnull=False
        )
        count = tenants.update(status='overdue')
        self.stdout.write(f'Marked {count} active tenants as overdue (past due).')

        # 5. For yearly plans, similar logic can be applied by checking next_billing_date

        self.stdout.write('Subscription check complete.')
