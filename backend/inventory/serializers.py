from rest_framework import serializers
from .models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'product_id', 'name', 'category', 'cost_price', 'unit_price', 'current_stock', 'reorder_level', 'expiry_date']
        read_only_fields = ['product_id']
