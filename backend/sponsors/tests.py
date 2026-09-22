from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from authorization.models import Permission, Role
from patients.models import Patient
from tenants.models import Tenant
from users.models import TenantMembership


class SponsorTenantIsolationTests(APITestCase):
    def setUp(self):
        self.tenant_a = Tenant.objects.create(name='A Clinic', subdomain='a-clinic')
        self.tenant_b = Tenant.objects.create(name='B Clinic', subdomain='b-clinic')
        self.user = User.objects.create_user('a-user', password='secure-password')
        read, _ = Permission.objects.get_or_create(codename='patient.read', defaults={'name': 'Read patients'})
        write, _ = Permission.objects.get_or_create(codename='patient.write', defaults={'name': 'Write patients'})
        role = Role.objects.create(name='Sponsor test role', tenant=self.tenant_a)
        role.permissions.add(read, write)
        membership = TenantMembership.objects.create(user=self.user, tenant=self.tenant_a)
        membership.roles.add(role)
        self.patient_b = Patient.objects.create(
            tenant=self.tenant_b, first_name='Other', last_name='Tenant',
            date_of_birth='1990-01-01', gender='F', phone='0700000000',
        )
        self.client.force_authenticate(self.user)
        # Authentication middleware sets this during normal JWT requests.
        self.client.handler._force_user = self.user

    def test_cannot_create_sponsor_for_patient_in_another_tenant(self):
        response = self.client.post('/api/sponsors/', {
            'patient': self.patient_b.pk, 'full_name': 'Cross tenant',
            'phone': '0711111111', 'relationship': 'family',
        }, format='json', HTTP_X_TENANT=self.tenant_a.subdomain)
        self.assertIn(response.status_code, (400, 403))
