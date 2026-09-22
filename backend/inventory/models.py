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
    product_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    current_stock = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

    def save(self, *args, **kwargs):
        if not self.product_id and self.tenant_id:
            abbreviation = self.tenant.subdomain[:3].upper()
            prefix = f'{abbreviation}-ITEM-'
            count = InventoryItem.objects.filter(
                tenant=self.tenant, product_id__startswith=prefix
            ).count()
            self.product_id = f'{prefix}{(count + 1):03d}'
        super().save(*args, **kwargs)
