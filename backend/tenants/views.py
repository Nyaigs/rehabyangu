from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Tenant, TenantConfig
from .serializers import TenantSerializer, TenantStatsSerializer, CreateTenantSerializer, TenantConfigSerializer
from users.models import TenantMembership
from users.services import audit, create_invitation, provision_default_roles
from users.rls import set_rls_context
from patients.models import Patient
from authorization.permissions import HasPermission
from users.permissions import IsInTenant
from appointments.models import Appointment
from billing.models import Invoice


class DashboardStatsView(APIView):
    """Small tenant-scoped summary payload for the authenticated home screen."""
    permission_classes = [IsAuthenticated, IsInTenant]

    def get(self, request):
        tenant = request.tenant
        today = timezone.localdate()
        invoices = Invoice.objects.filter(bill__tenant=tenant)
        outstanding = sum(
            max(invoice.total_amount - invoice.amount_paid, 0)
            for invoice in invoices.only('total_amount', 'amount_paid')
        )
        return Response({
            'total_patients': Patient.objects.filter(tenant=tenant).count(),
            'active_patients': Patient.objects.filter(tenant=tenant, status='active').count(),
            'staff_count': TenantMembership.objects.filter(tenant=tenant, user__is_active=True).count(),
            'appointments_today': Appointment.objects.filter(tenant=tenant, start_time__date=today).count(),
            'outstanding_invoice_value': outstanding,
        })

class TenantListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def get(self, request):
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)

class TenantStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def get(self, request):
        data = {
            'total_tenants': Tenant.objects.count(),
            'active_tenants': Tenant.objects.filter(status='active').count(),
            'overdue_tenants': Tenant.objects.filter(status='overdue').count(),
            'suspended_tenants': Tenant.objects.filter(status='suspended').count(),
            'total_patients': Patient.objects.count(),
            'total_users': User.objects.count(),
        }
        serializer = TenantStatsSerializer(data)
        return Response(serializer.data)

class ToggleTenantStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def patch(self, request, pk):
        try:
            tenant = Tenant.objects.get(id=pk)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ['active', 'suspended', 'overdue', 'trial']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        tenant.status = new_status
        if new_status == 'active':
            tenant.grace_period_end = None
        tenant.save()
        return Response({'message': f'Tenant status updated to {new_status}'})

class ExtendTrialView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def post(self, request, pk):
        try:
            tenant = Tenant.objects.get(id=pk)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        days = request.data.get('days', 7)
        new_trial_end = timezone.now() + timezone.timedelta(days=days)
        tenant.trial_ends_at = new_trial_end
        tenant.status = 'trial'
        tenant.save()
        return Response({'message': f'Trial extended by {days} days', 'new_trial_end': new_trial_end})

class TenantStaffListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def get(self, request, pk):
        try:
            tenant = Tenant.objects.get(id=pk)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        memberships = TenantMembership.objects.filter(tenant=tenant).select_related('user')
        data = [{
            'id': m.user.id,
            'username': m.user.username,
            'email': m.user.email,
            'role': m.role,
            'is_rehab_admin': m.is_rehab_admin,
            'full_name': f"{m.user.first_name} {m.user.last_name}".strip()
        } for m in memberships]
        return Response(data)

class CreateTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), HasPermission('tenant.manage')]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only the platform superadmin can provision tenants.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CreateTenantSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        with transaction.atomic():
            tenant = Tenant.objects.create(
                name=data['tenant_name'],
                subdomain=data['subdomain'].lower(),
                is_active=True,
                status='trial',
                trial_ends_at=timezone.now() + timezone.timedelta(days=14)
            )
            TenantConfig.objects.create(
                tenant=tenant, company_name=tenant.name,
                footer_text=f'{tenant.name} – Powered by RehabYangu',
            )
            roles = provision_default_roles(tenant)
            create_invitation(
                tenant=tenant, email=data['admin_email'], invited_by=request.user,
                first_name=data['admin_name'], roles=[roles['Rehab Administrator']],
                legacy_role='rehab_admin', is_rehab_admin=True,
            )
            audit(actor=request.user, tenant=tenant, action='CREATE', request=request,
                  description='Provisioned tenant, default roles, and initial administrator invitation.')

        return Response({
            'message': 'Tenant provisioned and administrator invitation sent.',
            'tenant': TenantSerializer(tenant).data,
            'admin': {'email': data['admin_email']}
        }, status=status.HTTP_201_CREATED)

class TenantConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated()]

    @staticmethod
    def serialize_config(config):
        return {
            'primary_color': config.primary_color,
            'secondary_color': config.secondary_color,
            'accent_color': config.accent_color,
            'sidebar_color': config.sidebar_color,
            'font_family': config.font_family,
            'company_name': config.company_name,
            'tagline': config.tagline,
            'footer_text': config.footer_text,
            'logo_url': config.logo.url if config.logo else None,
            'letterhead_url': config.letterhead.url if config.letterhead else None,
            'favicon_url': config.favicon.url if config.favicon else None,
            'onboarding_completed_at': config.onboarding_completed_at,
        }

    @staticmethod
    def get_config(tenant):
        # Tenants created before TenantConfig was introduced do not receive the
        # post-save signal retroactively. Create their default config on first
        # access instead of failing the post-login bootstrap with a 500.
        return TenantConfig.objects.get_or_create(
            tenant=tenant,
            defaults={
                'company_name': tenant.name,
                'footer_text': f'{tenant.name} – Powered by RehabYangu',
            },
        )[0]

    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({'error': 'No tenant context'}, status=status.HTTP_403_FORBIDDEN)
        return Response(self.serialize_config(self.get_config(tenant)))

    def put(self, request):
        tenant = getattr(request, 'tenant', None)
        if not tenant:
            return Response({'error': 'No tenant context'}, status=status.HTTP_403_FORBIDDEN)
        membership = getattr(request, 'tenant_membership', None)
        if not (request.user.is_superuser or (membership and membership.is_rehab_admin)):
            return Response(
                {'error': 'Only rehab administrators can update facility branding.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        config = self.get_config(tenant)
        serializer = TenantConfigSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.serialize_config(config))


class TenantLoginBrandingView(APIView):
    """Return the small, safe branding payload needed before authentication."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        tenant_slug = (request.headers.get('X-Tenant') or '').strip().lower()
        if not tenant_slug:
            return Response({'detail': 'Workspace is required.'}, status=status.HTTP_400_BAD_REQUEST)

        tenant = Tenant.objects.filter(subdomain=tenant_slug, is_active=True).first()
        if not tenant or tenant.status in ('suspended', 'overdue'):
            return Response({'detail': 'Workspace not found.'}, status=status.HTTP_404_NOT_FOUND)

        set_rls_context(tenant.id)
        config = TenantConfigView.get_config(tenant)
        return Response({
            'company_name': config.company_name or tenant.name,
            'logo_url': config.logo.url if config.logo else None,
        })
