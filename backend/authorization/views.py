from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .utils import get_user_permissions

class UserPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perms = get_user_permissions(request.user)
        return Response(list(perms))
