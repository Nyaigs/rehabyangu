from django.db import models
from tenants.models import Tenant

class InventoryItem(models.Model):
    CATEGORIES = [
        ('DRUG', 'Drug/Medication'),
        ('CONSUMABLE', 'Consumable'),
        ('EQUIPMENT', 'Medical Equipment'),
        ('SERVICE', 'Rehab Service'),  # <-- NEW
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='inventory')
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
