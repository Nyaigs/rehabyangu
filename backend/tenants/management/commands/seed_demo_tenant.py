from django.core.management.base import BaseCommand
from tenants.models import Tenant, TenantConfig
from django.contrib.auth.models import User
from users.models import TenantMembership
from users.services import provision_default_roles
from users.rls import set_rls_context
from django.utils import timezone

class Command(BaseCommand):
    help = 'Create a demo tenant with RehabYangu branding and sample data'

    def handle(self, *args, **options):
        demo_tenant, created = Tenant.objects.get_or_create(
            subdomain='demo',
            defaults={
                'name': 'RehabYangu Demo',
                'status': 'active',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write('Demo tenant created.')

        # Management commands are not wrapped by TenantRLSMiddleware. Keep
        # this command's connection in the demo tenant context while it
        # provisions tenant-scoped configuration, roles and membership rows.
        set_rls_context(demo_tenant.id, local=False)

        config, config_created = TenantConfig.objects.get_or_create(
            tenant=demo_tenant,
            defaults={
                'company_name': 'RehabYangu',
                'tagline': 'Smart Rehabilitation Management',
                'primary_color': '#2563EB',
                'secondary_color': '#10B981',
                'accent_color': '#F59E0B',
                'sidebar_color': '#1E293B',
                'footer_text': 'RehabYangu – Powered by Weiraro Technologies',
            }
        )
        if config_created:
            self.stdout.write('Demo config created.')

        roles = provision_default_roles(demo_tenant)

        demo_user, user_created = User.objects.get_or_create(
            username='demo_admin',
            defaults={
                'email': 'demo@rehabyangu.com',
                'first_name': 'Demo',
                'last_name': 'Admin',
                'is_staff': True,
            }
        )
        if user_created:
            demo_user.set_password('demo123')
            demo_user.save()
            membership, _ = TenantMembership.objects.update_or_create(
                user=demo_user,
                tenant=demo_tenant,
                defaults={'is_rehab_admin': True, 'role': 'rehab_admin'},
            )
            membership.roles.set([roles['Rehab Administrator']])
            self.stdout.write('Demo admin user created (demo_admin / demo123).')
        else:
            demo_user.set_password('demo123')
            demo_user.save()
            membership, _ = TenantMembership.objects.update_or_create(
                user=demo_user,
                tenant=demo_tenant,
                defaults={'is_rehab_admin': True, 'role': 'rehab_admin'},
            )
            membership.roles.set([roles['Rehab Administrator']])
            self.stdout.write('Demo admin user updated (demo_admin / demo123).')

        self.stdout.write(self.style.SUCCESS('Demo tenant setup complete.'))
