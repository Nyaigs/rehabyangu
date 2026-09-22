from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import HasPermission
from users.permissions import IsInTenant
from .models import Medication, Prescription, MedicationAdministrationRecord
from .serializers import MedicationSerializer, PrescriptionSerializer, MARSerializer


def interval_hours(frequency):
    """Understand the common charting frequencies while preserving free text."""
    value = frequency.lower().strip()
    import re
    match = re.search(r'every\s+(\d+)\s*hours?', value)
    if match:
        return max(1, int(match.group(1)))
    return {'daily': 24, 'once daily': 24, 'bid': 12, 'twice daily': 12, 'tid': 8, 'three times daily': 8, 'qid': 6, 'four times daily': 6}.get(value, 8)


class ClinicalScopedViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsInTenant]
    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('clinical.write' if self.action in ('create', 'update', 'partial_update') else 'clinical.read')]


class MedicationViewSet(ClinicalScopedViewSet):
    serializer_class = MedicationSerializer
    def get_queryset(self): return Medication.objects.filter(tenant=self.request.tenant)
    def perform_create(self, serializer): serializer.save(tenant=self.request.tenant)


class PrescriptionViewSet(ClinicalScopedViewSet):
    serializer_class = PrescriptionSerializer
    def get_queryset(self):
        qs = Prescription.objects.filter(tenant=self.request.tenant).select_related('patient', 'medication', 'prescribing_clinician')
        return qs.filter(patient_id=self.request.query_params['patient']) if self.request.query_params.get('patient') else qs
    def perform_create(self, serializer): serializer.save(tenant=self.request.tenant, prescribing_clinician=self.request.user)

    @action(detail=False, methods=['get'], url_path='due')
    def due(self, request):
        patient_id = request.query_params.get('patient')
        now = timezone.now()
        prescriptions = self.get_queryset().filter(status='active', start_at__lte=now)
        if patient_id:
            prescriptions = prescriptions.filter(patient_id=patient_id)
        due = []
        for prescription in prescriptions:
            if prescription.ends_at <= now:
                continue
            last = prescription.administrations.order_by('-administered_at').first()
            hours = interval_hours(prescription.frequency)
            baseline = last.administered_at if last else prescription.start_at
            elapsed_hours = (now - baseline).total_seconds() / 3600
            if elapsed_hours >= hours:
                due.append(PrescriptionSerializer(prescription, context={'request': request}).data | {
                    'is_missed': elapsed_hours >= hours * 1.5,
                    'due_at': (baseline + timezone.timedelta(hours=hours)).isoformat(),
                })
        return Response(due)


class MARViewSet(ClinicalScopedViewSet):
    serializer_class = MARSerializer
    def get_queryset(self):
        qs = MedicationAdministrationRecord.objects.filter(prescription__tenant=self.request.tenant).select_related('prescription__patient', 'prescription__medication', 'given_by')
        return qs.filter(prescription__patient_id=self.request.query_params['patient']) if self.request.query_params.get('patient') else qs
    def perform_create(self, serializer):
        prescription = serializer.validated_data['prescription']
        if prescription.tenant_id != self.request.tenant.id: raise ValidationError({'prescription': 'Must belong to this tenant.'})
        serializer.save(given_by=self.request.user)
