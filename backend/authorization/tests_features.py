from types import SimpleNamespace
from django.test import SimpleTestCase
from rest_framework.exceptions import APIException
from authorization.permissions import HasFeature


class HasFeaturePermissionTests(SimpleTestCase):
    def test_missing_flag_raises_payment_required_payload(self):
        user = SimpleNamespace(is_authenticated=True, is_superuser=False)
        request = SimpleNamespace(user=user, tenant=SimpleNamespace(plan_fk=SimpleNamespace(feature_flags={'inventory': False})))
        with self.assertRaises(APIException) as caught:
            HasFeature('inventory').has_permission(request, None)
        self.assertEqual(caught.exception.status_code, 402)
        self.assertEqual(caught.exception.detail, {'error': 'This feature is not available on your plan.', 'upgrade_required': True, 'feature': 'inventory'})

    def test_superuser_bypasses_feature_flags(self):
        request = SimpleNamespace(user=SimpleNamespace(is_authenticated=True, is_superuser=True), tenant=None)
        self.assertTrue(HasFeature('inventory').has_permission(request, None))
