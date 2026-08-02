from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from tenants.models import Tenant
from .models import TenantMembership

class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        tenant_id = token.payload.get('tenant_id')
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                raise AuthenticationFailed('Tenant not found or inactive.')

            # Block suspended/overdue tenants
            if tenant.status in ['suspended', 'overdue']:
                raise AuthenticationFailed(
                    f'Your account is {tenant.status}. Please contact support.'
                )

            request.tenant = tenant

            # Load membership
            try:
                request.tenant_membership = TenantMembership.objects.get(
                    user=user, tenant=tenant
                )
            except TenantMembership.DoesNotExist:
                request.tenant_membership = None
        else:
            request.tenant = None
            request.tenant_membership = None

        return (user, token)
