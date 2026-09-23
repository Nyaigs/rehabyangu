from decimal import Decimal
from django.test import SimpleTestCase
from subscriptions.services import compute_plan_diff


class ComputePlanDiffTests(SimpleTestCase):
    def test_returns_feature_price_and_user_limit_changes(self):
        old = type('Plan', (), {'feature_flags': {'patients': True, 'inventory': True}, 'price_monthly': Decimal('5000.00'), 'max_users': 5})()
        new = type('Plan', (), {'feature_flags': {'patients': True, 'hr': True}, 'price_monthly': Decimal('20000.00'), 'max_users': 25})()
        self.assertEqual(compute_plan_diff(old, new), {
            'features_added': ['hr'], 'features_removed': ['inventory'],
            'price_change': Decimal('15000.00'), 'user_limit_change': 20,
        })
