from django.core.management.base import BaseCommand

from tenants.models import Tenant
from users.rls import set_rls_context
from users.services import provision_default_roles


class Command(BaseCommand):
    help = 'Idempotently create and update canonical roles for every tenant.'

    def handle(self, *args, **options):
        for tenant in Tenant.objects.iterator():
            # Set session-level RLS context so writes are allowed for this tenant
            set_rls_context(tenant.id, local=False)
            roles = provision_default_roles(tenant)
            self.stdout.write(f'{tenant.subdomain}: {", ".join(sorted(roles))}')
        self.stdout.write(self.style.SUCCESS('Default tenant roles are up to date.'))
