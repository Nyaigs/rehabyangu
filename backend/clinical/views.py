from rest_framework import viewsets, permissions
from .models import ClinicalNote
from .serializers import ClinicalNoteSerializer

class ClinicalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = ClinicalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = ClinicalNote.objects.all().select_related('patient', 'clinician')
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset.order_by('-date')
