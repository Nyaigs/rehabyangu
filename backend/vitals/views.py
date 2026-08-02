from users.permissions import IsInTenant
from rest_framework import viewsets, permissions
from .models import VitalSign
from .serializers import VitalSignSerializer
from authorization.permissions import HasPermission

class VitalSignViewSet(viewsets.ModelViewSet):
    serializer_class = VitalSignSerializer
    permission_classes = permissions.IsAuthenticated

    def get_permissions(self):
        action_permissions = {
            'list': 'vitals:view',
            'retrieve': 'vitals:view',
            'create': 'vitals:create',
            'update': 'vitals:create',
            'partial_update': 'vitals:create',
            'destroy': 'vitals:create',
        }
        codename = action_permissions.get(self.action, 'vitals:view')
        return [permissions.IsAuthenticated(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile') or not request.tenant:
            return VitalSign.objects.none()
        return VitalSign.objects.filter(tenant=request.tenant)

    def perform_create(self, serializer):
        user = self.request.user
        tenant = request.tenant
        serializer.save(recorded_by=user, tenant=tenant)
