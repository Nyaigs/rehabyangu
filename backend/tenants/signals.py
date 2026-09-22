from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from .models import Tenant, TenantConfig
from users.rls import set_rls_context

@receiver(post_save, sender=Tenant)
def create_tenant_config(sender, instance, created, **kwargs):
    if created:
        # Provisioning can happen from management commands as well as an HTTP
        # request. Establish an isolated transaction-local RLS context before
        # writing the tenant-scoped config in either case.
        with transaction.atomic():
            set_rls_context(instance.id)
            TenantConfig.objects.create(
                tenant=instance,
                company_name=instance.name,
                primary_color="#2563EB",
                secondary_color="#10B981",
                footer_text=f"{instance.name} – Powered by RehabYangu"
            )
