from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from tenants.models import Tenant
from .models import TenantMembership
from .models import AuthSession
from .rls import set_rls_context

class TenantJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result
        tenant_id = token.payload.get('tenant_id')
        is_platform_admin = bool(token.payload.get('is_platform_admin'))
        if is_platform_admin:
            if not user.is_superuser or tenant_id is not None:
                raise AuthenticationFailed('Invalid platform administrator session.')
            set_rls_context(None, is_platform_admin=True)
            session_id = token.payload.get('session_id')
            if not session_id or not AuthSession.objects.filter(id=session_id, user=user, tenant__isnull=True, revoked_at__isnull=True, expires_at__gt=timezone.now()).exists():
                raise AuthenticationFailed('Session expired or has been revoked.')
            request.tenant = None
            request.tenant_membership = None
            return (user, token)
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
            set_rls_context(tenant.id, is_platform_admin=user.is_superuser)

            session_id = token.payload.get('session_id')
            if not session_id or not AuthSession.objects.filter(
                id=session_id, user=user, tenant=tenant, revoked_at__isnull=True,
                expires_at__gt=timezone.now(),
            ).exists():
                raise AuthenticationFailed('Session expired or has been revoked.')

            # Membership is re-checked for every authenticated request. This
            # invalidates an already-issued token immediately when access is
            # removed, rather than relying on the token expiry window.
            try:
                request.tenant_membership = TenantMembership.objects.get(
                    user=user, tenant=tenant
                )
            except TenantMembership.DoesNotExist:
                raise AuthenticationFailed('You are not a member of this facility.')
        else:
            request.tenant = None
            request.tenant_membership = None

        return (user, token)
