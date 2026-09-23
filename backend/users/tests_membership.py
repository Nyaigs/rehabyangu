from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from authorization.models import Permission, Role
from tenants.models import Tenant
from users.models import TenantMembership


class MembershipEnforcementTests(APITestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name='Tenant A', subdomain='tenant-a')
        self.tenant_b = Tenant.objects.create(name='Tenant B', subdomain='tenant-b')
        self.user = User.objects.create_user('member', password='correct-horse-battery-staple')
        permission, _ = Permission.objects.get_or_create(codename='patient.read', defaults={'name': 'View patients'})
        role = Role.objects.create(name='Nurse', tenant=self.tenant_a)
        role.permissions.add(permission)
        self.membership = TenantMembership.objects.create(user=self.user, tenant=self.tenant_a, role='nurse')
        self.membership.roles.add(role)

    def login(self, tenant):
        return self.client.post('/api/token/', {'username': self.user.username, 'password': 'correct-horse-battery-staple'}, HTTP_X_TENANT=tenant.subdomain)

    def test_user_without_membership_cannot_log_in(self):
        self.membership.delete()
        self.assertEqual(self.login(self.tenant_a).status_code, 403)

    def test_user_cannot_log_into_other_tenant(self):
        self.assertEqual(self.login(self.tenant_b).status_code, 403)

    def test_deleted_membership_invalidates_active_token(self):
        response = self.login(self.tenant_a)
        self.assertEqual(response.status_code, 200)
        self.membership.delete()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        self.assertEqual(self.client.get('/api/patients/').status_code, 401)
