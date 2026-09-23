from users.permissions import IsInTenant
from rest_framework import viewsets, permissions
from .models import VitalSign, VitalNormalRange
from .serializers import VitalSignSerializer, VitalNormalRangeSerializer
from authorization.permissions import HasPermission, HasFeature

from subscriptions.models import Notification
from users.models import TenantMembership

class VitalSignViewSet(viewsets.ModelViewSet):
    serializer_class = VitalSignSerializer
    permission_classes = permissions.IsAuthenticated

    def get_permissions(self):
        action_permissions = {
            'list': 'vitals.read',
            'retrieve': 'vitals.read',
            'create': 'vitals.write',
            'update': 'vitals.write',
            'partial_update': 'vitals.write',
            'destroy': 'vitals.write',
        }
        codename = action_permissions.get(self.action, 'vitals.read')
        return [permissions.IsAuthenticated(), IsInTenant(), HasFeature('vitals'), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if not getattr(self.request, 'tenant_membership', None):
            return VitalSign.objects.none()
        queryset = VitalSign.objects.filter(tenant=self.request.tenant)
        patient_id = self.request.query_params.get('patient')
        return queryset.filter(patient_id=patient_id) if patient_id else queryset

    def perform_create(self, serializer):
        user = self.request.user
        tenant = self.request.tenant
        vital = serializer.save(recorded_by=user, tenant=tenant)
        if vital.abnormality_level != 'normal':
            recipients = TenantMembership.objects.filter(tenant=tenant).filter(role__in=['nurse', 'psychiatrist', 'clinical_officer']) | TenantMembership.objects.filter(tenant=tenant, is_rehab_admin=True)
            for recipient in recipients.distinct():
                summary = ', '.join(f"{item['metric']} {item['value']}" for item in vital.abnormal_values)
                Notification.objects.create(tenant=tenant, recipient=recipient.user, notification_type='other', title=f'{vital.abnormality_level.title()} vitals alert', message=f'{vital.patient}: {summary}')


class VitalNormalRangeViewSet(viewsets.ModelViewSet):
    serializer_class = VitalNormalRangeSerializer
    def get_permissions(self):
        return [permissions.IsAuthenticated(), IsInTenant(), HasFeature('vitals'), HasPermission('clinical.write' if self.action in ('create', 'update', 'partial_update') else 'clinical.read')]
    def get_queryset(self): return VitalNormalRange.objects.filter(tenant=self.request.tenant)
    def perform_create(self, serializer): serializer.save(tenant=self.request.tenant)
