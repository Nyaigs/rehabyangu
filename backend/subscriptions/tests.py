from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from subscriptions.models import Notification, SubscriptionPlan
from subscriptions.services import current_mrr, process_tenant_subscription, tenant_has_feature
from tenants.models import Tenant


class SubscriptionLifecycleTests(TestCase):
    def setUp(self):
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter', 'price_monthly': Decimal('5000.00'),
                'max_users': 5, 'feature_flags': {'vitals': True},
            },
        )
        # Seed migrations can create the starter record before this test.
        self.plan.feature_flags = {'vitals': True}
        self.plan.price_monthly = Decimal('5000.00')
        self.plan.max_users = 5
        self.plan.save(update_fields=['feature_flags', 'price_monthly', 'max_users', 'updated_at'])
        self.tenant = Tenant.objects.create(name='Test Facility', subdomain='test-facility', plan_fk=self.plan, status='trial', trial_ends_at=timezone.now() - timedelta(minutes=1))

    def test_expired_trial_moves_to_overdue_then_suspended_idempotently(self):
        now = timezone.now()
        self.assertTrue(process_tenant_subscription(self.tenant, now))
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.status, 'overdue')
        self.assertTrue(self.tenant.is_active)
        first_count = Notification.objects.count()
        self.assertFalse(process_tenant_subscription(self.tenant, now))
        self.assertEqual(Notification.objects.count(), first_count)
        self.assertTrue(process_tenant_subscription(self.tenant, self.tenant.grace_period_end + timedelta(seconds=1)))
        self.tenant.refresh_from_db()
        self.assertEqual(self.tenant.status, 'suspended')
        self.assertFalse(self.tenant.is_active)

    def test_feature_and_mrr_use_plan_relationship(self):
        self.assertTrue(tenant_has_feature(self.tenant, 'vitals'))
        self.tenant.status, self.tenant.is_active = 'active', True
        self.tenant.save(update_fields=['status', 'is_active'])
        self.assertEqual(current_mrr(), Decimal('5000.00'))
