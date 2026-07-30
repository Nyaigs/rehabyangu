from rest_framework import viewsets, permissions
from .models import ClinicalNote
from .serializers import ClinicalNoteSerializer
from authorization.permissions import HasPermission

class ClinicalNoteViewSet(viewsets.ModelViewSet):
    queryset = ClinicalNote.objects.all()
    serializer_class = ClinicalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        action_permissions = {
            'list': 'clinicalnote:view',
            'retrieve': 'clinicalnote:view',
            'create': 'clinicalnote:create',
            'update': 'clinicalnote:edit',
            'partial_update': 'clinicalnote:edit',
            'destroy': 'clinicalnote:edit',
        }
        codename = action_permissions.get(self.action, 'clinicalnote:view')
        return [permissions.IsAuthenticated(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if hasattr(user, 'profile') and user.profile.tenant:
            return self.queryset.filter(tenant=user.profile.tenant)
        return self.queryset.none()
