from django.db import IntegrityError, transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authorization.permissions import HasPermission
from users.permissions import IsInTenant
from users.services import audit
from .models import ClinicalNote
from .serializers import ClinicalNoteCorrectionSerializer, ClinicalNoteSerializer


class ClinicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicalNoteSerializer
    permission_classes = [IsAuthenticated, IsInTenant]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        codename = 'clinical.write' if self.action in ('create', 'correct') else 'clinical.read'
        return [IsAuthenticated(), IsInTenant(), HasPermission(codename)]

    def get_queryset(self):
        queryset = ClinicalNote.objects.filter(tenant=self.request.tenant).select_related('patient', 'admission', 'clinician', 'supersedes')
        patient_id = self.request.query_params.get('patient')
        return queryset.filter(patient_id=patient_id) if patient_id else queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, description='Read clinical note list.')
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, instance=self.get_object(), description=f'Read clinical note {kwargs["pk"]}.')
        return response

    def perform_create(self, serializer):
        note = serializer.save(tenant=self.request.tenant, clinician=self.request.user)
        audit(actor=self.request.user, tenant=self.request.tenant, action='CREATE', request=self.request, instance=note, description=f'Created clinical note {note.id} for patient {note.patient_id}.')

    @action(detail=True, methods=['post'], url_path='corrections')
    def correct(self, request, pk=None):
        original = self.get_object()
        serializer = ClinicalNoteCorrectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        # Lock the latest version, not merely the URL's version, so a
        # correction always extends one immutable record chain.
        with transaction.atomic():
            latest = ClinicalNote.objects.select_for_update().filter(
                tenant=request.tenant, record_id=original.record_id
            ).order_by('-version').first()
            try:
                note = ClinicalNote.objects.create(
                    tenant=request.tenant, patient=latest.patient, admission=latest.admission, clinician=request.user,
                    record_id=latest.record_id, version=latest.version + 1, supersedes=latest,
                    subjective=values['subjective'], objective=values['objective'],
                    assessment=values['assessment'], plan=values['plan'], correction_reason=values['correction_reason'],
                )
            except IntegrityError:
                # The unique record/version constraint remains the final
                # protection if another writer races this request.
                return Response({'detail': 'A correction was just recorded; retry against the latest version.'}, status=status.HTTP_409_CONFLICT)
        audit(actor=request.user, tenant=request.tenant, action='CREATE', request=request, instance=note, description=f'Created correction v{note.version} for clinical note {latest.id}.')
        return Response(ClinicalNoteSerializer(note, context={'request': request}).data, status=status.HTTP_201_CREATED)
