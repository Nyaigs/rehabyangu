import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone

from authorization.models import Permission, Role
from .models import AuditLog, Invitation, MfaPolicy, TenantMembership


DEFAULT_ROLE_BUNDLES = {
    'Rehab Administrator': ['tenant.manage', 'staff.read', 'staff.invite', 'staff.manage', 'role.read', 'role.manage', 'mfa.manage_self', 'mfa.manage_policy', 'patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'discharge.request', 'discharge.approve'],
    'Clinician': ['patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'mfa.manage_self'],
    'Psychiatrist': ['patient.read', 'patient.write', 'clinical.read', 'clinical.write', 'clinical.sensitive.read', 'clinical.sensitive.write', 'mfa.manage_self'],
    'Nurse': ['patient.read', 'clinical.read', 'mfa.manage_self'],
    'Reception': ['patient.read', 'patient.write', 'appointment.read', 'appointment.write', 'mfa.manage_self'],
    'Billing': ['billing.read', 'billing.write', 'inventory.read', 'patient.read', 'mfa.manage_self'],
    'Staff Member': ['mfa.manage_self'],
}
PERMISSION_NAMES = {
    'tenant.manage': ('Manage tenants', 'tenant'), 'staff.read': ('View staff', 'staff'),
    'staff.invite': ('Invite staff', 'staff'), 'staff.manage': ('Manage staff', 'staff'),
    'role.read': ('View roles', 'role'), 'role.manage': ('Manage roles', 'role'),
    'mfa.manage_self': ('Manage own MFA', 'mfa'), 'mfa.manage_policy': ('Manage MFA policy', 'mfa'),
    'patient.read': ('View patients', 'patient'), 'patient.write': ('Manage patients', 'patient'),
    'clinical.read': ('View clinical records', 'clinical'), 'clinical.write': ('Manage clinical records', 'clinical'),
    'appointment.read': ('View appointments', 'appointment'), 'appointment.write': ('Manage appointments', 'appointment'),
    'billing.read': ('View billing', 'billing'), 'billing.write': ('Manage billing', 'billing'),
    'inventory.read': ('View inventory', 'inventory'), 'inventory.write': ('Manage inventory', 'inventory'),
    'clinical.sensitive.read': ('View highly sensitive clinical fields', 'clinical'),
    'clinical.sensitive.write': ('Edit highly sensitive clinical fields', 'clinical'),
    'discharge.request': ('Request discharge', 'discharge'), 'discharge.approve': ('Approve discharge', 'discharge'),
}


def audit(*, actor, tenant, action, description, request=None, instance=None):
    """Create an immutable audit event, optionally linked to its record."""
    values = {
        'actor': actor,
        'tenant': tenant,
        'action': action,
        'description': description,
        'ip_address': request.META.get('REMOTE_ADDR') if request else None,
    }
    if instance is not None and instance.pk is not None:
        values.update(
            content_type=ContentType.objects.get_for_model(instance, for_concrete_model=False),
            object_id=instance.pk,
        )
    return AuditLog.objects.create(**values)


def provision_default_roles(tenant):
    permissions = {}
    for codename, (name, category) in PERMISSION_NAMES.items():
        permissions[codename], _ = Permission.objects.get_or_create(codename=codename, defaults={'name': name, 'category': category})
    roles = {}
    for name, codenames in DEFAULT_ROLE_BUNDLES.items():
        role, _ = Role.objects.get_or_create(tenant=tenant, name=name)
        role.permissions.set([permissions[codename] for codename in codenames])
        roles[name] = role
    MfaPolicy.objects.get_or_create(tenant=tenant)
    return roles


def create_invitation(*, tenant, email, invited_by, roles, legacy_role='other', is_rehab_admin=False, first_name='', last_name=''):
    raw_token = secrets.token_urlsafe(32)
    invitation = Invitation.objects.create(
        tenant=tenant, email=email.strip().lower(), first_name=first_name.strip(), last_name=last_name.strip(),
        legacy_role=legacy_role, is_rehab_admin=is_rehab_admin,
        token_hash=hashlib.sha256(raw_token.encode()).hexdigest(), expires_at=timezone.now() + timedelta(hours=72), invited_by=invited_by,
    )
    invitation.roles.set(roles)
    link = f"{settings.FRONTEND_URL.rstrip('/')}/invitations/accept?tenant={tenant.subdomain}&token={raw_token}"
    transaction.on_commit(lambda: send_mail(
        subject=f'You have been invited to {tenant.name}',
        message=f'Use this single-use link within 72 hours to set your password: {link}',
        from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[invitation.email], fail_silently=False,
    ))
    return invitation


def accept_invitation(*, raw_token, password, username=None):
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    with transaction.atomic():
        invitation = Invitation.objects.select_for_update().prefetch_related('roles').filter(token_hash=token_hash).first()
        if not invitation or not invitation.is_usable:
            raise ValueError('This invitation is invalid, expired, or has already been used.')
        if User.objects.filter(email__iexact=invitation.email).exists():
            raise ValueError('An account with this email address already exists. Contact your administrator.')
        base_username = (username or invitation.email.split('@')[0]).strip()
        candidate, suffix = base_username, 1
        while User.objects.filter(username__iexact=candidate).exists():
            suffix += 1
            candidate = f'{base_username}{suffix}'
        user = User.objects.create_user(username=candidate, email=invitation.email, password=password,
            first_name=invitation.first_name, last_name=invitation.last_name, is_active=True)
        membership = TenantMembership.objects.create(user=user, tenant=invitation.tenant,
            role=invitation.legacy_role, is_rehab_admin=invitation.is_rehab_admin)
        membership.roles.set(invitation.roles.all())
        invitation.accepted_at = timezone.now()
        invitation.save(update_fields=['accepted_at'])
        audit(actor=user, tenant=invitation.tenant, action='CREATE', description='Accepted staff invitation.')
        return user, membership
