from rest_framework import viewsets, permissions
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from authorization.permissions import HasPermission

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        action_permissions = {
            'list': 'inventory:view',
            'retrieve': 'inventory:view',
            'create': 'inventory:manage',
            'update': 'inventory:manage',
            'partial_update': 'inventory:manage',
            'destroy': 'inventory:manage',
        }
        codename = action_permissions.get(self.action, 'inventory:view')
        return [permissions.IsAuthenticated(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if hasattr(user, 'profile') and user.profile.tenant:
            return self.queryset.filter(tenant=user.profile.tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = user.profile.tenant
        serializer.save(tenant=tenant)
