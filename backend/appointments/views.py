from users.permissions import IsInTenant
from rest_framework import viewsets, permissions
from .models import Appointment
from .serializers import AppointmentSerializer
from authorization.permissions import HasPermission, HasFeature


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = permissions.IsAuthenticated

    def get_permissions(self):
        action_permissions = {
            'list': 'appointment.read',
            'retrieve': 'appointment.read',
            'create': 'appointment.write',
            'update': 'appointment.write',
            'partial_update': 'appointment.write',
            'destroy': 'appointment.write',
        }
        codename = action_permissions.get(self.action, 'appointment.read')
        return [permissions.IsAuthenticated(), IsInTenant(), HasFeature('appointments'), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if getattr(self.request, 'tenant_membership', None):
            return self.queryset.filter(tenant=self.request.tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
