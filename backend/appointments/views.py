from rest_framework import viewsets, permissions
from .models import Appointment
from .serializers import AppointmentSerializer
from authorization.permissions import HasPermission

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        action_permissions = {
            'list': 'appointment:view',
            'retrieve': 'appointment:view',
            'create': 'appointment:create',
            'update': 'appointment:edit',
            'partial_update': 'appointment:edit',
            'destroy': 'appointment:edit',
        }
        codename = action_permissions.get(self.action, 'appointment:view')
        return [permissions.IsAuthenticated(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if hasattr(user, 'profile') and user.profile.tenant:
            return self.queryset.filter(tenant=user.profile.tenant)
        return self.queryset.none()
