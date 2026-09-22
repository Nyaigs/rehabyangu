from django.core.management.base import BaseCommand

from authorization.models import Permission, Role
from users.services import DEFAULT_ROLE_BUNDLES, PERMISSION_NAMES


class Command(BaseCommand):
    help = 'Seed canonical dot-notation permissions and global default roles'

    def handle(self, *args, **options):
        permissions = {}
        for codename, (name, category) in PERMISSION_NAMES.items():
            permission, created = Permission.objects.update_or_create(
                codename=codename,
                defaults={'name': name, 'category': category},
            )
            permissions[codename] = permission
            if created:
                self.stdout.write(f'Created permission: {codename}')

        bundles = dict(DEFAULT_ROLE_BUNDLES)
        # Historic deployments used this spelling; retain the role identity
        # but give it the same canonical permissions.
        bundles['Rehab Admin'] = bundles['Rehab Administrator']
        for role_name, codenames in bundles.items():
            role, created = Role.objects.get_or_create(name=role_name, tenant=None)
            role.permissions.set([permissions[codename] for codename in codenames])
            self.stdout.write(f"{'Created' if created else 'Updated'} role: {role_name}")

        self.stdout.write(self.style.SUCCESS('Canonical permission seeding complete.'))
