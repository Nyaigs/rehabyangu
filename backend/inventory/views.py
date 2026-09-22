from users.permissions import IsInTenant
from rest_framework import viewsets, permissions
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from authorization.permissions import HasPermission

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = permissions.IsAuthenticated

    def get_permissions(self):
        action_permissions = {
            'list': 'inventory.read',
            'retrieve': 'inventory.read',
            'create': 'inventory.write',
            'update': 'inventory.write',
            'partial_update': 'inventory.write',
            'destroy': 'inventory.write',
        }
        codename = action_permissions.get(self.action, 'inventory.read')
        return [permissions.IsAuthenticated(), IsInTenant(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if getattr(self.request, 'tenant_membership', None):
            return self.queryset.filter(tenant=self.request.tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)
