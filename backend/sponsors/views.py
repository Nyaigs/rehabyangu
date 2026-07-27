from rest_framework import viewsets, permissions
from .models import Sponsor
from .serializers import SponsorSerializer

class SponsorViewSet(viewsets.ModelViewSet):
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    permission_classes = [permissions.IsAuthenticated]