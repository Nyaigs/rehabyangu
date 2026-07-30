from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tenant, TenantConfig

@receiver(post_save, sender=Tenant)
def create_tenant_config(sender, instance, created, **kwargs):
    if created:
        TenantConfig.objects.create(
            tenant=instance,
            company_name=instance.name,
            primary_color="#2563EB",
            secondary_color="#10B981",
            footer_text=f"{instance.name} – Powered by RehabYangu"
        )
