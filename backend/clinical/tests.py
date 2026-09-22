from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from authorization.models import Permission, Role
from patients.models import Patient
from tenants.models import Tenant
from users.models import AuditLog, AuthSession, TenantMembership
from users.rls import set_rls_context


class ClinicalNoteApiTests(TestCase):
    """Regression coverage for the append-only and audit requirements."""

    def setUp(self):
        self.tenant = Tenant.objects.create(name='Clinical Test', subdomain='clinical-test', status='active')
        set_rls_context(self.tenant.id, is_platform_admin=True)
        self.clinician = User.objects.create_user('clinician', 'clinician@example.test', 'test-pass-12345')
        self.nurse = User.objects.create_user('nurse', 'nurse@example.test', 'test-pass-12345')
        clinical_read, _ = Permission.objects.get_or_create(codename='clinical.read', defaults={'name': 'View clinical records', 'category': 'clinical'})
        clinical_write, _ = Permission.objects.get_or_create(codename='clinical.write', defaults={'name': 'Write clinical records', 'category': 'clinical'})
        clinician_role = Role.objects.create(name='Clinical test clinician', tenant=self.tenant)
        clinician_role.permissions.add(clinical_read, clinical_write)
        nurse_role = Role.objects.create(name='Clinical test nurse', tenant=self.tenant)
        nurse_role.permissions.add(clinical_read)
        clinician_membership = TenantMembership.objects.create(user=self.clinician, tenant=self.tenant)
        clinician_membership.roles.add(clinician_role)
        nurse_membership = TenantMembership.objects.create(user=self.nurse, tenant=self.tenant)
        nurse_membership.roles.add(nurse_role)
        self.patient = Patient.objects.create(
            tenant=self.tenant, created_by=self.clinician, first_name='Amina', last_name='Otieno',
            date_of_birth='1990-01-01', gender='F', phone='+254700000001',
        )

    def client_for(self, user):
        """Use a real tenant JWT so TenantJWTAuthentication establishes RLS."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        session = AuthSession.objects.create(
            user=user, tenant=self.tenant, refresh_jti=str(refresh['jti']),
            expires_at=timezone.now() + timedelta(days=1),
        )
        refresh['tenant_id'] = self.tenant.id
        refresh['session_id'] = str(session.id)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        return client

    def create_note(self):
        response = self.client_for(self.clinician).post('/api/clinical-notes/', {
            'patient': self.patient.id, 'subjective': 'Reports improved sleep.',
            'objective': 'Calm and cooperative.', 'assessment': 'Improving.', 'plan': 'Continue group therapy.',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        return response.data['id']

    def test_nurse_can_read_but_cannot_edit_and_read_is_audited(self):
        note_id = self.create_note()
        audit_count_before_read = AuditLog.objects.filter(tenant=self.tenant, actor=self.nurse, action='READ').count()
        response = self.client_for(self.nurse).get(f'/api/clinical-notes/{note_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AuditLog.objects.filter(tenant=self.tenant, actor=self.nurse, action='READ', object_id=note_id).count(), audit_count_before_read + 1)
        response = self.client_for(self.nurse).patch(f'/api/clinical-notes/{note_id}/', {'plan': 'Changed'}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_correction_creates_a_new_immutable_version(self):
        note_id = self.create_note()
        response = self.client_for(self.clinician).post(f'/api/clinical-notes/{note_id}/corrections/', {
            'subjective': 'Clarification: sleep improved over two nights.',
            'objective': 'Calm and cooperative.', 'assessment': 'Improving.', 'plan': 'Continue group therapy.',
            'correction_reason': 'Clarified timing stated in the original note.',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['version'], 2)
        self.assertEqual(response.data['supersedes'], note_id)
