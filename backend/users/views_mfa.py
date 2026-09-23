import base64
import hashlib

import pyotp
from cryptography.fernet import Fernet
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.permissions import HasPermission, HasFeature

from .models import MfaPolicy, TotpDevice
from .services import audit


def cipher():
    key = getattr(settings, 'MFA_ENCRYPTION_KEY', '')
    if not key:
        if not settings.DEBUG:
            raise RuntimeError('MFA_ENCRYPTION_KEY must be configured outside development.')
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest()).decode()
    return Fernet(key.encode())


class MfaSetupView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasFeature('mfa'), HasPermission('mfa.manage_self')]

    def post(self, request):
        secret = pyotp.random_base32()
        device = TotpDevice.objects.create(user=request.user, tenant=request.tenant, secret_encrypted=cipher().encrypt(secret.encode()).decode())
        uri = pyotp.TOTP(secret).provisioning_uri(name=request.user.email, issuer_name=request.tenant.name)
        return Response({'device_id': device.id, 'provisioning_uri': uri, 'secret': secret}, status=status.HTTP_201_CREATED)


class MfaConfirmView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasFeature('mfa'), HasPermission('mfa.manage_self')]

    def post(self, request, pk):
        device = TotpDevice.objects.filter(id=pk, user=request.user, tenant=request.tenant, confirmed_at__isnull=True).first()
        if not device:
            return Response({'error': 'Pending MFA device not found.'}, status=status.HTTP_404_NOT_FOUND)
        secret = cipher().decrypt(device.secret_encrypted.encode()).decode()
        if not pyotp.TOTP(secret).verify(request.data.get('code', ''), valid_window=1):
            return Response({'code': ['Invalid authenticator code.']}, status=status.HTTP_400_BAD_REQUEST)
        device.confirmed_at = timezone.now(); device.save(update_fields=['confirmed_at'])
        audit(actor=request.user, tenant=request.tenant, action='UPDATE', request=request, description='Enabled TOTP MFA device.')
        return Response({'message': 'MFA enabled.'})


class MfaPolicyView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), HasFeature('mfa'), HasPermission('mfa.manage_policy')]

    def get(self, request):
        policy, _ = MfaPolicy.objects.get_or_create(tenant=request.tenant)
        return Response({'required_for_all_staff': policy.required_for_all_staff})

    def put(self, request):
        policy, _ = MfaPolicy.objects.get_or_create(tenant=request.tenant)
        policy.required_for_all_staff = bool(request.data.get('required_for_all_staff'))
        policy.save(update_fields=['required_for_all_staff', 'updated_at'])
        audit(actor=request.user, tenant=request.tenant, action='UPDATE', request=request, description='Updated MFA policy.')
        return Response({'required_for_all_staff': policy.required_for_all_staff})
