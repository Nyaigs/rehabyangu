from rest_framework import viewsets, permissions
from authorization.permissions import HasPermission
from users.permissions import IsInTenant
from .models import Sponsor
from .serializers import SponsorSerializer

class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()  # required for router basename
    serializer_class = SponsorSerializer
    permission_classes = [permissions.IsAuthenticated, IsInTenant]

    def get_permissions(self):
        codename = 'patient.write' if self.action in ('create', 'update', 'partial_update', 'destroy') else 'patient.read'
        return [permissions.IsAuthenticated(), IsInTenant(), HasPermission(codename)]

    def get_queryset(self):
        queryset = super().get_queryset().filter(tenant=self.request.tenant).select_related('patient')
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
