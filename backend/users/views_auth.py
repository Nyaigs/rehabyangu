from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from tenants.models import Tenant
from .models import TenantMembership


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        tenant = self.context.get('tenant')
        membership = self.context.get('membership')
        if tenant and membership:
            refresh = self.get_token(self.user)
            refresh['tenant_id'] = tenant.id
            refresh['role'] = membership.role
            refresh['is_rehab_admin'] = membership.is_rehab_admin
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            data['tenant'] = {
                'id': tenant.id,
                'name': tenant.name,
                'subdomain': tenant.subdomain,
                'status': tenant.status,
                'plan': tenant.plan,
            }
            data['role'] = membership.role
        elif tenant and not membership:
            # Superuser: no membership, but still include tenant info
            refresh = self.get_token(self.user)
            refresh['tenant_id'] = tenant.id
            refresh['role'] = 'super_admin'
            refresh['is_rehab_admin'] = False
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            data['tenant'] = {
                'id': tenant.id,
                'name': tenant.name,
                'subdomain': tenant.subdomain,
                'status': tenant.status,
                'plan': tenant.plan,
            }
            data['role'] = 'super_admin'
        return data


class TenantTokenObtainPairView(TokenObtainPairView):
    serializer_class = TenantTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        tenant = self.get_tenant(request)
        if not tenant:
            return Response(
                {'error': 'Tenant not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Block login if tenant is suspended or overdue
        if not tenant.is_active:
            return Response(
                {
                    'error': 'Account suspended',
                    'detail': 'Your account has been suspended. Please contact support to reactivate.',
                },
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
        if tenant.status in ['suspended', 'overdue']:
            return Response(
                {
                    'error': 'Account suspended',
                    'detail': f'Your account has been {tenant.status}. Please contact support.',
                },
                status=status.HTTP_402_PAYMENT_REQUIRED
            )

        # Step 1 – authenticate username/password
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.user
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Step 2 – verify membership (superusers bypass)
        membership = None
        if not user.is_superuser:
            try:
                membership = TenantMembership.objects.get(user=user, tenant=tenant)
            except TenantMembership.DoesNotExist:
                return Response(
                    {'error': 'User is not a member of this tenant'},
                    status=status.HTTP_403_FORBIDDEN
                )

        # Step 3 – generate token with claims
        serializer_with_claims = self.get_serializer(
            data=request.data,
            context={'tenant': tenant, 'membership': membership}
        )
        try:
            serializer_with_claims.is_valid(raise_exception=True)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer_with_claims.validated_data, status=status.HTTP_200_OK)

    def get_tenant(self, request):
        subdomain = request.headers.get('X-Tenant')
        if not subdomain:
            host = request.META.get('HTTP_HOST', '')
            host = host.split(':')[0]
            parts = host.split('.')
            if len(parts) >= 3 and parts[0] not in ['www', 'localhost', '127']:
                subdomain = parts[0]

        if subdomain:
            try:
                return Tenant.objects.get(subdomain=subdomain)
            except Tenant.DoesNotExist:
                pass
        return None
