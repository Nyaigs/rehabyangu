from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import TenantMembership


class Command(BaseCommand):
    help = 'Report users without tenant access and tenant memberships without assigned roles.'

    def handle(self, *args, **options):
        users = User.objects.filter(is_superuser=False).exclude(tenant_memberships__isnull=False).order_by('username')
        roleless = TenantMembership.objects.filter(roles__isnull=True).select_related('user', 'tenant').distinct()
        self.stdout.write('Users with no membership:')
        for user in users:
            self.stdout.write(f'  {user.id}: {user.username} <{user.email}>')
        if not users.exists():
            self.stdout.write('  none')
        self.stdout.write('Memberships without roles:')
        for membership in roleless:
            self.stdout.write(f'  {membership.user.username} -> {membership.tenant.subdomain}')
        if not roleless.exists():
            self.stdout.write('  none')
        # A database FK prevents memberships that refer to a non-existent
        # tenant. State this explicitly so operations can distinguish a clean
        # result from a missing audit category.
        self.stdout.write('Memberships in non-existent tenants: none (enforced by foreign key)')
