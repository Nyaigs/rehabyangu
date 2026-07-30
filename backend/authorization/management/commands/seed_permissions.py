from django.core.management.base import BaseCommand
from authorization.models import Permission, Role

class Command(BaseCommand):
    help = 'Seed initial permissions and roles'

    def handle(self, *args, **options):
        permissions = [
            ('patient:view', 'View Patients', 'patients'),
            ('patient:create', 'Create Patients', 'patients'),
            ('patient:edit', 'Edit Patients', 'patients'),
            ('patient:delete', 'Delete Patients', 'patients'),
            ('appointment:view', 'View Appointments', 'appointments'),
            ('appointment:create', 'Create Appointments', 'appointments'),
            ('appointment:edit', 'Edit Appointments', 'appointments'),
            ('clinicalnote:view', 'View Clinical Notes', 'clinical'),
            ('clinicalnote:create', 'Create Clinical Notes', 'clinical'),
            ('clinicalnote:edit', 'Edit Clinical Notes', 'clinical'),
            ('billing:view', 'View Billing', 'billing'),
            ('billing:create', 'Create Charges', 'billing'),
            ('invoice:view', 'View Invoices', 'billing'),
            ('invoice:create', 'Create Invoices', 'billing'),
            ('invoice:send', 'Send Invoices', 'billing'),
            ('vitals:view', 'View Vitals', 'vitals'),
            ('vitals:create', 'Record Vitals', 'vitals'),
            ('discharge:request', 'Request Discharge', 'discharge'),
            ('discharge:approve', 'Approve Discharge', 'discharge'),
            ('inventory:view', 'View Inventory', 'inventory'),
            ('inventory:manage', 'Manage Inventory', 'inventory'),
            ('staff:view', 'View Staff', 'staff'),
            ('staff:manage', 'Manage Staff', 'staff'),
            ('tenant:manage', 'Manage Tenants', 'system'),
        ]
        for codename, name, category in permissions:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name, 'category': category}
            )
            if created:
                self.stdout.write(f'Created permission: {codename}')

        role_permissions = {
            'Rehab Admin': [
                'patient:view', 'patient:create', 'patient:edit', 'patient:delete',
                'appointment:view', 'appointment:create', 'appointment:edit',
                'clinicalnote:view', 'clinicalnote:create', 'clinicalnote:edit',
                'billing:view', 'billing:create',
                'invoice:view', 'invoice:create', 'invoice:send',
                'vitals:view', 'vitals:create',
                'discharge:request', 'discharge:approve',
                'inventory:view', 'inventory:manage',
                'staff:view', 'staff:manage',
            ],
            'Nurse': [
                'patient:view', 'patient:create', 'patient:edit',
                'appointment:view', 'appointment:create',
                'clinicalnote:view', 'clinicalnote:create',
                'vitals:view', 'vitals:create',
                'billing:view',
                'inventory:view',
                'discharge:request',
            ],
            'Pharmacist': [
                'patient:view',
                'inventory:view', 'inventory:manage',
                'billing:view', 'billing:create',
            ],
            # Add other roles as needed
        }
        for role_name, perm_list in role_permissions.items():
            role, created = Role.objects.get_or_create(name=role_name, tenant=None)
            perms = Permission.objects.filter(codename__in=perm_list)
            role.permissions.set(perms)
            if created:
                self.stdout.write(f'Created role: {role_name}')
            else:
                self.stdout.write(f'Updated role: {role_name}')

        self.stdout.write(self.style.SUCCESS('Seeding complete.'))
