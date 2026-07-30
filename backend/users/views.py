from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User
from django.db import transaction
from .models import UserProfile
from tenants.models import Tenant
from .serializers import UserSerializer
from authorization.permissions import HasPermission

class StaffListView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('staff:view')]

    def get(self, request):
        if not hasattr(request.user, 'profile') or not request.user.profile.tenant:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        tenant = request.user.profile.tenant
        profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
        data = [{
            'id': p.user.id,
            'username': p.user.username,
            'email': p.user.email,
            'role': p.role,
            'is_rehab_admin': p.is_rehab_admin,
            'full_name': f"{p.user.first_name} {p.user.last_name}".strip(),
            'is_active': p.user.is_active,
        } for p in profiles]
        return Response(data)

class CreateStaffView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('staff:manage')]

    def post(self, request):
        if not hasattr(request.user, 'profile') or not request.user.profile.tenant:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        if not request.user.profile.is_rehab_admin and not request.user.is_superuser:
            return Response({'error': 'Only rehab admins can create staff'}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'other')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')

        if not all([username, email, password]):
            return Response({'error': 'Username, email, and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        tenant = request.user.profile.tenant

        with transaction.atomic():
            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )

            profile = UserProfile.objects.get(user=user)
            profile.tenant = tenant
            profile.role = role
            profile.is_rehab_admin = False
            profile.save()

        return Response({
            'message': 'Staff created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': profile.role,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
            }
        }, status=status.HTTP_201_CREATED)
