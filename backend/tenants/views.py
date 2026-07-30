from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from .models import Tenant
from .serializers import TenantSerializer, TenantStatsSerializer, CreateTenantSerializer
from users.models import UserProfile
from patients.models import Patient
from authorization.permissions import HasPermission

class TenantListView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

    def get(self, request):
        tenants = Tenant.objects.all()
        serializer = TenantSerializer(tenants, many=True)
        return Response(serializer.data)

class TenantStatsView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

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
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

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
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

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
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

    def get(self, request, pk):
        try:
            tenant = Tenant.objects.get(id=pk)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
        data = [{
            'id': p.user.id,
            'username': p.user.username,
            'email': p.user.email,
            'role': p.role,
            'is_rehab_admin': p.is_rehab_admin,
            'full_name': f"{p.user.first_name} {p.user.last_name}".strip()
        } for p in profiles]
        return Response(data)

class CreateTenantView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('tenant:manage')]

    def post(self, request):
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

            username = data['admin_email'].split('@')[0] + '_admin'
            admin_user = User.objects.create_user(
                username=username,
                email=data['admin_email'],
                password=data['admin_password']
            )
            admin_user.is_staff = True
            admin_user.save()

            profile = UserProfile.objects.get(user=admin_user)
            profile.tenant = tenant
            profile.role = 'rehab_admin'
            profile.is_rehab_admin = True
            profile.is_super_admin = False
            profile.save()

        return Response({
            'message': 'Tenant and Admin created successfully.',
            'tenant': TenantSerializer(tenant).data,
            'admin': {
                'username': username,
                'email': data['admin_email']
            }
        }, status=status.HTTP_201_CREATED)

class TenantConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'profile') or not request.user.profile.tenant:
            return Response({'error': 'No tenant associated'}, status=status.HTTP_403_FORBIDDEN)
        config = request.user.profile.tenant.config
        return Response({
            'primary_color': config.primary_color,
            'secondary_color': config.secondary_color,
            'accent_color': config.accent_color,
            'sidebar_color': config.sidebar_color,
            'font_family': config.font_family,
            'company_name': config.company_name,
            'tagline': config.tagline,
            'footer_text': config.footer_text,
            'logo_url': config.logo.url if config.logo else None,
            'favicon_url': config.favicon.url if config.favicon else None,
        })
