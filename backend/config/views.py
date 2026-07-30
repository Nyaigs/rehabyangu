from django.contrib.auth.models import User
from rest_framework import serializers, generics, permissions
from rest_framework.response import Response
from users.models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    is_rehab_admin = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_superuser', 'role', 'is_rehab_admin', 'tenant_name']

    def get_role(self, obj):
        try:
            return obj.profile.role
        except:
            return None

    def get_is_rehab_admin(self, obj):
        try:
            return obj.profile.is_rehab_admin
        except:
            return False

    def get_tenant_name(self, obj):
        try:
            return obj.profile.tenant.name
        except:
            return None

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
