from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
try:  # Available in newer SimpleJWT releases; keep the configured 5.3 floor compatible.
    from rest_framework_simplejwt.exceptions import ExpiredTokenError
except ImportError:  # pragma: no cover - version compatibility path
    ExpiredTokenError = TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from tenants.models import Tenant
from .models import AuthSession, TenantMembership
from .rls import set_rls_context
from .services import audit, accept_invitation

PLATFORM_WORKSPACE_SLUG = 'weiraro'


class TenantTokenObtainPairSerializer(serializers.Serializer):
    # `username` remains accepted during migration; email is the canonical login.
    email = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(trim_whitespace=False, write_only=True)

    def validate(self, attrs):
        identifier = (attrs.get('email') or attrs.get('username') or '').strip()
        password = attrs.get('password')
        user = User.objects.filter(Q(email__iexact=identifier) | Q(username__iexact=identifier)).first()
        if not user or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed('Invalid email or password.')
        tenant = self.context.get('tenant')
        is_platform_admin = self.context.get('is_platform_admin', False)
        if is_platform_admin and not user.is_superuser:
            raise PermissionDenied('The Weiraro workspace is restricted to platform administrators.')
        set_rls_context(tenant.id if tenant else None, is_platform_admin=is_platform_admin)
        membership = None if is_platform_admin else TenantMembership.objects.filter(user=user, tenant=tenant).first()
        if not is_platform_admin and not membership:
            raise AuthenticationFailed('You are not a member of this facility.')
        refresh = RefreshToken.for_user(user)
        session = AuthSession.objects.create(user=user, tenant=tenant, refresh_jti=str(refresh['jti']), expires_at=timezone.now() + refresh.lifetime)
        refresh['tenant_id'] = tenant.id if tenant else None
        refresh['session_id'] = str(session.id)
        refresh['role'] = 'super_admin' if is_platform_admin else membership.role if membership else 'super_admin'
        refresh['is_superuser'] = bool(user.is_superuser)
        refresh['is_platform_admin'] = is_platform_admin
        refresh['is_rehab_admin'] = bool(membership and membership.is_rehab_admin)
        if is_platform_admin:
            return {
                'refresh': str(refresh), 'access': str(refresh.access_token),
                'role': 'super_admin', 'is_superuser': True, 'is_platform_admin': True,
            }
        return {
            'refresh': str(refresh), 'access': str(refresh.access_token),
            'tenant': {'id': tenant.id, 'name': tenant.name, 'subdomain': tenant.subdomain, 'status': tenant.status, 'plan': tenant.plan},
            'role': membership.role if membership else 'super_admin',
        }


class TenantTokenObtainPairView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = 'login'

    def post(self, request):
        tenant, is_platform_admin = self.get_tenant(request)
        if not tenant and not is_platform_admin:
            return Response({'error': {'code': 'tenant_not_found', 'message': 'Workspace not found.'}}, status=status.HTTP_404_NOT_FOUND)
        if tenant and (not tenant.is_active or tenant.status in ('suspended', 'overdue')):
            return Response({'error': {'code': 'account_unavailable', 'message': 'This workspace is unavailable.'}}, status=status.HTTP_402_PAYMENT_REQUIRED)
        serializer = TenantTokenObtainPairSerializer(data=request.data, context={'tenant': tenant, 'is_platform_admin': is_platform_admin})
        serializer.is_valid(raise_exception=True)
        user = User.objects.filter(Q(email__iexact=(request.data.get('email') or request.data.get('username') or '').strip()) | Q(username__iexact=(request.data.get('email') or request.data.get('username') or '').strip())).first()
        audit(actor=user, tenant=tenant, action='LOGIN', request=request, description='Created platform administrator session.' if is_platform_admin else 'Created authenticated session.')
        return Response(serializer.validated_data)

    @staticmethod
    def get_tenant(request):
        slug = (request.headers.get('X-Tenant') or '').strip().lower()
        if not slug:
            host = request.get_host().split(':')[0].split('.')
            if len(host) >= 3 and host[0] not in ('www', 'localhost', '127'):
                slug = host[0]
        if slug == PLATFORM_WORKSPACE_SLUG:
            return None, True
        return (Tenant.objects.filter(subdomain=slug).first(), False) if slug else (None, False)


class TenantTokenRefreshView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        try:
            refresh = RefreshToken(request.data.get('refresh'))
            tenant_id = refresh.get('tenant_id')
            is_platform_admin = bool(refresh.get('is_platform_admin'))
            if is_platform_admin and not tenant_id:
                set_rls_context(None, is_platform_admin=True)
                session = AuthSession.objects.get(id=refresh['session_id'], user_id=refresh['user_id'], tenant__isnull=True)
            else:
                set_rls_context(tenant_id)
                session = AuthSession.objects.get(id=refresh['session_id'], user_id=refresh['user_id'], tenant_id=tenant_id)
            if not session.is_active:
                raise AuthenticationFailed('Session expired or revoked.')
            serializer = TokenRefreshSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except (KeyError, AuthSession.DoesNotExist, AuthenticationFailed, TokenError, ExpiredTokenError, InvalidToken):
            return Response({'error': {'code': 'invalid_refresh', 'message': 'Refresh token is invalid or has expired.'}}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.validated_data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        session_id = request.auth.payload.get('session_id')
        AuthSession.objects.filter(id=session_id, user=request.user, tenant=request.tenant, revoked_at__isnull=True).update(revoked_at=timezone.now())
        refresh_value = request.data.get('refresh')
        if refresh_value:
            try:
                RefreshToken(refresh_value).blacklist()
            except Exception:
                pass
        audit(actor=request.user, tenant=request.tenant, action='LOGOUT', request=request, description='Revoked authenticated session.')
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationAcceptView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_scope = 'invitation_accept'

    def post(self, request):
        token, password = request.data.get('token', ''), request.data.get('password', '')
        if len(password) < 12:
            return Response({'error': {'code': 'validation_error', 'message': 'Use a password with at least 12 characters.'}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tenant = Tenant.objects.filter(subdomain=(request.data.get('tenant') or '').strip().lower()).first()
            if not tenant:
                raise ValueError('Workspace not found.')
            set_rls_context(tenant.id)
            user, membership = accept_invitation(raw_token=token, password=password, username=request.data.get('username'))
        except ValueError:
            return Response({'error': {'code': 'invalid_invitation', 'message': 'This invitation is invalid, expired, or has already been used.'}}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Account activated. You can now sign in.', 'email': user.email, 'tenant': membership.tenant.subdomain}, status=status.HTTP_201_CREATED)
