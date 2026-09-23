from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from authorization.models import Permission, Role
from subscriptions.models import SubscriptionPlan
from tenants.models import Tenant
from users.models import TenantMembership


class ReportsEndpointTests(APITestCase):
    def setUp(self):
        plan, _ = SubscriptionPlan.objects.update_or_create(
            code='enterprise',
            defaults={
                'name': 'Enterprise',
                'price_monthly': '50000.00',
                'max_users': None,
                'feature_flags': {
                    'patients': True, 'clinical_notes': True, 'vitals': True,
                    'appointments': True, 'billing': True, 'advanced_billing': True,
                    'inventory': True, 'hr': True, 'branches': True,
                    'analytics': True, 'mfa': True, 'priority_support': True,
                },
            },
        )
        self.tenant = Tenant.objects.create(name='Reports Centre', subdomain='reports-centre', plan_fk=plan)
        self.user = User.objects.create_user('reporter', password='safe-password')
        permission, _ = Permission.objects.get_or_create(codename='reports.read', defaults={'name': 'View reports'})
        role = Role.objects.create(name='Reports role', tenant=self.tenant)
        role.permissions.add(permission)
        membership = TenantMembership.objects.create(user=self.user, tenant=self.tenant)
        membership.roles.add(role)

    def test_report_routes_are_registered_and_authorised(self):
        token = self.client.post('/api/token/', {'username': 'reporter', 'password': 'safe-password'}, HTTP_X_TENANT=self.tenant.subdomain).data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        for endpoint in ('occupancy', 'census', 'admissions', 'discharges', 'revenue', 'outstanding'):
            self.assertEqual(self.client.get(f'/api/reports/{endpoint}/').status_code, 200)
