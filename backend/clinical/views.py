from rest_framework import viewsets, permissions
from .models import ClinicalNote
from .serializers import ClinicalNoteSerializer

class ClinicalNoteViewSet(viewsets.ModelViewSet):
    queryset = ClinicalNote.objects.all()
    serializer_class = ClinicalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]