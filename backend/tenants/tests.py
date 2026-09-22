from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from subscriptions.models import SubscriptionPlan
from users.models import AuditLog
from .models import Tenant


class PlatformAdminAuthorizationTests(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser('platform-admin', 'platform@example.com', 'password')
        self.user = User.objects.create_user('ordinary-user', 'ordinary@example.com', 'password')
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={'name': 'Starter', 'price_monthly': '5000.00'},
        )

    def test_admin_api_requires_global_superuser(self):
        self.assertEqual(self.client.get('/api/admin/stats/').status_code, 401)
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.get('/api/admin/stats/').status_code, 403)
        self.client.force_authenticate(self.superuser)
        self.assertEqual(self.client.get('/api/admin/stats/').status_code, 200)

    def test_platform_workspace_issues_tenantless_superuser_token(self):
        response = self.client.post('/api/token/', {'username': 'platform-admin', 'password': 'password'}, HTTP_X_TENANT='weiraro')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['is_superuser'])
        self.assertTrue(response.data['is_platform_admin'])
        self.assertNotIn('tenant', response.data)
        token = AccessToken(response.data['access'])
        self.assertIsNone(token['tenant_id'])
        self.assertTrue(token['is_superuser'])
        self.assertEqual(token['role'], 'super_admin')

    def test_non_superuser_is_rejected_from_platform_workspace(self):
        response = self.client.post('/api/token/', {'username': 'ordinary-user', 'password': 'password'}, HTTP_X_TENANT='weiraro')
        self.assertEqual(response.status_code, 403)

    def test_provisioning_creates_trial_and_invitation(self):
        self.client.force_authenticate(self.superuser)
        response = self.client.post('/api/admin/tenants/', {
            'tenant_name': 'Serenity Place', 'subdomain': 'serenity-place',
            'admin_first_name': 'Amina', 'admin_last_name': 'Ali',
            'admin_email': 'amina@example.com', 'subscription_plan': self.plan.pk,
        }, format='json')
        self.assertEqual(response.status_code, 201)
        tenant = Tenant.objects.get(subdomain='serenity-place')
        self.assertEqual(tenant.status, 'trial')
        self.assertEqual(tenant.plan_fk, self.plan)
        self.assertIsNotNone(tenant.trial_ends_at)
        self.assertTrue(tenant.invitations.filter(email='amina@example.com').exists())

    def test_plan_change_preserves_dates_and_records_audit_event(self):
        upgraded, _ = SubscriptionPlan.objects.get_or_create(code='test_upgrade_plan', defaults={'name': 'Test Upgrade Plan', 'price_monthly': '9000.00'})
        tenant = Tenant.objects.create(name='Test Centre', subdomain='test-centre', plan_fk=self.plan,
            monthly_fee='5000.00', trial_ends_at='2026-12-01T00:00:00Z', next_billing_date='2027-01-01T00:00:00Z')
        original_trial, original_billing = tenant.trial_ends_at, tenant.next_billing_date
        self.client.force_authenticate(self.superuser)
        response = self.client.patch(f'/api/admin/tenants/{tenant.pk}/', {'subscription_plan': upgraded.pk}, format='json')
        self.assertEqual(response.status_code, 200)
        tenant.refresh_from_db()
        self.assertEqual(tenant.plan_fk, upgraded)
        self.assertEqual(str(tenant.monthly_fee), '9000.00')
        self.assertEqual(tenant.trial_ends_at.isoformat().replace('+00:00', 'Z'), original_trial if isinstance(original_trial, str) else original_trial.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(tenant.next_billing_date.isoformat().replace('+00:00', 'Z'), original_billing if isinstance(original_billing, str) else original_billing.isoformat().replace('+00:00', 'Z'))
        self.assertTrue(AuditLog.objects.filter(tenant=tenant, description__contains='Changed subscription plan').exists())

    def test_archive_retains_tenant_and_marks_it_inactive(self):
        tenant = Tenant.objects.create(name='Archived Centre', subdomain='archived-centre', plan_fk=self.plan)
        self.client.force_authenticate(self.superuser)
        response = self.client.patch(f'/api/admin/tenants/{tenant.pk}/', {'action': 'archive'}, format='json')
        self.assertEqual(response.status_code, 200)
        tenant.refresh_from_db()
        self.assertFalse(tenant.is_active)
        self.assertIsNotNone(tenant.archived_at)
        self.assertEqual(tenant.status, 'suspended')
