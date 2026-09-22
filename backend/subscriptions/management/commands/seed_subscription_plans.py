from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan


PLANS = (
    ('Starter', 'starter', 'Essential care operations for small facilities.', '5000.00', 5,
     {'patients': True, 'clinical_notes': True, 'vitals': True, 'appointments': True, 'billing': True, 'inventory': False, 'hr': False, 'branches': False, 'analytics': False, 'mfa': False, 'advanced_billing': False, 'priority_support': False}),
    ('Professional', 'professional', 'Operational tools for growing rehabilitation centres.', '20000.00', 25,
     {'patients': True, 'clinical_notes': True, 'vitals': True, 'appointments': True, 'billing': True, 'inventory': True, 'hr': True, 'branches': False, 'analytics': False, 'mfa': False, 'advanced_billing': True, 'priority_support': False}),
    ('Enterprise', 'enterprise', 'Full platform capability for multi-facility operations.', '50000.00', None,
     {'patients': True, 'clinical_notes': True, 'vitals': True, 'appointments': True, 'billing': True, 'inventory': True, 'hr': True, 'branches': True, 'analytics': True, 'mfa': True, 'advanced_billing': True, 'priority_support': True}),
)


class Command(BaseCommand):
    help = 'Create or update the standard RehabYangu subscription plans.'

    def handle(self, *args, **options):
        for name, code, description, price, max_users, features in PLANS:
            SubscriptionPlan.objects.update_or_create(code=code, defaults={
                'name': name, 'description': description, 'price_monthly': price,
                'max_users': max_users, 'feature_flags': features, 'is_active': True,
            })
        self.stdout.write(self.style.SUCCESS('Subscription plans are ready.'))
