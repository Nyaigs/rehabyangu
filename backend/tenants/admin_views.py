from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from subscriptions.models import Subscription, SubscriptionPlan
from subscriptions.serializers import SubscriptionPlanSerializer
from subscriptions.services import current_mrr, send_payment_reminder, compute_plan_diff
from users.models import TenantMembership
from inventory.models import InventoryItem
from users.permissions import IsSuperAdmin
from users.services import audit, create_invitation, provision_default_roles
from .admin_serializers import AdminTenantCreateSerializer, AdminTenantSerializer, AdminTenantUpdateSerializer
from .models import Tenant


class PlatformAdminView(APIView):
    """Explicitly global boundary: membership permissions are never enough."""
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class PlatformStatsView(PlatformAdminView):
    def get(self, request):
        tenants = Tenant.objects.all()
        return Response({
            'total_tenants': tenants.count(), 'active_tenants': tenants.filter(status='active', is_active=True).count(),
            'trial_tenants': tenants.filter(status='trial', is_active=True).count(), 'overdue_tenants': tenants.filter(status='overdue').count(),
            'suspended_tenants': tenants.filter(status='suspended').count(),
            'new_tenants_this_month': tenants.filter(created_at__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)).count(),
            'total_users': User.objects.filter(tenant_memberships__isnull=False, is_active=True).distinct().count(),
            # Trials are excluded: MRR means paying, currently active subscriptions.
            'mrr': current_mrr(),
        })


class AdminTenantPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class PlatformTenantListCreateView(PlatformAdminView):
    def get(self, request):
        tenants = Tenant.objects.select_related('plan_fk').annotate(member_count=Count('memberships'))
        search = request.query_params.get('search', '').strip()
        if search:
            tenants = tenants.filter(Q(name__icontains=search) | Q(subdomain__icontains=search))
        status_filter = request.query_params.get('status')
        if status_filter:
            tenants = tenants.filter(status=status_filter)
        plan_filter = request.query_params.get('plan')
        if plan_filter:
            tenants = tenants.filter(plan_fk__code=plan_filter)
        paginator = AdminTenantPagination()
        page = paginator.paginate_queryset(tenants.order_by('name'), request)
        serializer = AdminTenantSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = AdminTenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        now = timezone.now()
        with transaction.atomic():
            tenant = Tenant.objects.create(
                name=values['tenant_name'].strip(), subdomain=values['subdomain'], plan_fk=values['subscription_plan'],
                plan={'starter': 'basic', 'professional': 'pro', 'enterprise': 'enterprise'}.get(values['subscription_plan'].code, 'basic'),
                monthly_fee=values['subscription_plan'].price_monthly, status='trial', is_active=True,
                trial_ends_at=now + timedelta(days=30),
            )
            # TenantConfig is created once by the existing post-save signal.
            Subscription.objects.create(tenant=tenant, plan=values['subscription_plan'].code,
                amount=values['subscription_plan'].price_monthly, status='trial', next_billing_date=tenant.trial_ends_at,
                trial_ends_at=tenant.trial_ends_at)
            roles = provision_default_roles(tenant)
            invitation = create_invitation(tenant=tenant, email=values['admin_email'], invited_by=request.user,
                first_name=values['admin_first_name'], last_name=values['admin_last_name'], roles=[roles['Rehab Administrator']],
                legacy_role='rehab_admin', is_rehab_admin=True)
            audit(actor=request.user, tenant=tenant, action='CREATE', request=request, instance=tenant,
                  description='Provisioned tenant, 30-day trial, subscription plan, and administrator invitation.')
        return Response({'tenant': AdminTenantSerializer(tenant).data, 'invitation_id': str(invitation.id),
                         'message': 'Tenant created. An administrator invitation has been sent.'}, status=status.HTTP_201_CREATED)


class PlatformTenantDetailView(PlatformAdminView):
    def get_object(self, pk):
        try:
            return Tenant.objects.select_related('plan_fk', 'config').get(pk=pk)
        except Tenant.DoesNotExist:
            raise NotFound('Tenant not found.')

    def get(self, request, pk):
        tenant = self.get_object(pk)
        data = AdminTenantSerializer(tenant).data
        admin = tenant.memberships.filter(is_rehab_admin=True).select_related('user').first()
        data['administrator'] = None if not admin else {'name': admin.user.get_full_name() or admin.user.username, 'email': admin.user.email}
        data['members'] = [{
            'name': membership.user.get_full_name() or membership.user.username,
            'email': membership.user.email, 'role': membership.role,
            'is_rehab_admin': membership.is_rehab_admin, 'tenant_user_id': membership.tenant_user_id,
            'is_active': membership.user.is_active, 'last_login': membership.user.last_login,
        } for membership in TenantMembership.objects.filter(tenant=tenant).select_related('user').order_by('user__first_name', 'user__username')]
        data['recent_audit_events'] = [{
            'actor': event.actor.get_full_name() or event.actor.username if event.actor else 'System',
            'action': event.action, 'description': event.description, 'timestamp': event.timestamp,
        } for event in tenant.audit_logs.select_related('actor').all()[:25]]
        return Response(data)

    def patch(self, request, pk):
        tenant = self.get_object(pk)
        serializer = AdminTenantUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        updates = []
        warnings = []
        if plan := values.get('subscription_plan'):
            if tenant.plan_fk_id == plan.id:
                raise serializers.ValidationError({'subscription_plan': 'This tenant is already assigned to that plan.'})
            previous_plan_obj = tenant.plan_fk
            previous_plan = previous_plan_obj.name if previous_plan_obj else tenant.plan
            previous_monthly_fee = tenant.monthly_fee
            diff = compute_plan_diff(previous_plan_obj, plan)
            active_users = TenantMembership.objects.filter(tenant=tenant, user__is_active=True).count()
            if plan.max_users is not None and active_users > plan.max_users:
                message = f'This tenant has {active_users} active users, but {plan.name} allows {plan.max_users}. Deactivate {active_users - plan.max_users} users before downgrading.'
                return Response({'error': message, 'current_user_count': active_users, 'target_max_users': plan.max_users, 'blocked_reason': 'user_limit_exceeded'}, status=status.HTTP_400_BAD_REQUEST)
            removed = set(diff['features_removed'])
            if 'inventory' in removed:
                count = InventoryItem.objects.filter(tenant=tenant).count()
                if count: warnings.append(f'This tenant has {count} inventory items that will become inaccessible.')
            if 'hr' in removed:
                count = TenantMembership.objects.filter(tenant=tenant, role='hr_manager').count()
                if count: warnings.append(f'This tenant has {count} staff HR records that will become inaccessible.')
            if warnings and not values.get('acknowledge_warnings', False):
                return Response({'warnings': warnings, 'acknowledge_required': True}, status=status.HTTP_400_BAD_REQUEST)
            tenant.plan_fk = plan
            tenant.plan = {'starter': 'basic', 'professional': 'pro', 'enterprise': 'enterprise'}.get(plan.code, tenant.plan)
            tenant.monthly_fee = plan.price_monthly
            updates.extend(['plan_fk', 'plan', 'monthly_fee'])
            Subscription.objects.filter(tenant=tenant).update(plan=plan.code, amount=plan.price_monthly)
            audit(actor=request.user, tenant=tenant, action='UPDATE', request=request, instance=tenant,
                  description=f'Changed subscription plan from {previous_plan} to {plan.name}; old monthly fee {previous_plan_obj.price_monthly if previous_plan_obj else previous_monthly_fee}; new monthly fee {plan.price_monthly}; features added {diff["features_added"]}; features removed {diff["features_removed"]}; platform admin {request.user.username}.')
        if 'next_billing_date' in values:
            tenant.next_billing_date = values['next_billing_date']
            updates.append('next_billing_date')
            Subscription.objects.filter(tenant=tenant).update(next_billing_date=values['next_billing_date'])
        action = values.get('action')
        if action:
            if action in ('suspend', 'deactivate'):
                if tenant.status == 'suspended' and not tenant.is_active:
                    raise serializers.ValidationError({'action': 'This tenant is already suspended.'})
                tenant.status, tenant.is_active = 'suspended', False
                description, audit_action = ('Deactivated tenant account.' if action == 'deactivate' else 'Suspended tenant account.'), 'SUSPEND'
            elif action in ('activate', 'restore'):
                if tenant.is_active and tenant.status == 'active':
                    raise serializers.ValidationError({'action': 'This tenant is already active.'})
                tenant.status, tenant.is_active, tenant.grace_period_end = 'active', True, None
                description, audit_action = 'Activated tenant account.', 'REACTIVATE'
            elif action == 'archive':
                if tenant.archived_at:
                    raise serializers.ValidationError({'action': 'This tenant is already archived.'})
                tenant.archived_at, tenant.is_active, tenant.status = timezone.now(), False, 'suspended'
                description, audit_action = 'Archived tenant account; data retained.', 'SUSPEND'
            else:
                raise serializers.ValidationError({'action': 'Unsupported action.'})
            updates.extend(['status', 'is_active', 'grace_period_end', 'archived_at'])
            Subscription.objects.filter(tenant=tenant).update(status=tenant.status, grace_period_end=tenant.grace_period_end)
            audit(actor=request.user, tenant=tenant, action=audit_action, request=request, instance=tenant, description=description)
        if updates:
            tenant.save(update_fields=list(dict.fromkeys(updates)))
        data = AdminTenantSerializer(tenant).data
        if warnings:
            data['warnings'] = warnings
        return Response(data)


class PlatformTenantPaymentReminderView(PlatformAdminView):
    def post(self, request, pk):
        tenant = PlatformTenantDetailView().get_object(pk)
        if tenant.archived_at:
            raise serializers.ValidationError({'detail': 'Archived tenants cannot receive payment reminders.'})
        _, created = send_payment_reminder(tenant)
        audit(actor=request.user, tenant=tenant, action='UPDATE', request=request, instance=tenant,
              description='Sent payment reminder.' if created else 'Payment reminder was already sent for this billing period.')
        return Response({'message': 'Payment reminder sent.' if created else 'A payment reminder was already sent for this billing period.', 'sent': created})


class PlatformPlanListCreateView(PlatformAdminView):
    def get(self, request):
        return Response(SubscriptionPlanSerializer(SubscriptionPlan.objects.all(), many=True).data)

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()
        audit(actor=request.user, tenant=None, action='CREATE', request=request, instance=plan, description=f'Created subscription plan {plan.code}.')
        return Response(SubscriptionPlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class PlatformPlanDetailView(PlatformAdminView):
    def patch(self, request, pk):
        try:
            plan = SubscriptionPlan.objects.get(pk=pk)
        except SubscriptionPlan.DoesNotExist:
            raise NotFound('Subscription plan not found.')
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data.get('is_active') is False and plan.tenants.filter(is_active=True).exists():
            raise serializers.ValidationError({'is_active': 'This plan is assigned to active tenants. Reassign or deactivate those tenants before deactivating the plan.'})
        plan = serializer.save()
        audit(actor=request.user, tenant=None, action='UPDATE', request=request, instance=plan, description=f'Updated subscription plan {plan.code}.')
        return Response(SubscriptionPlanSerializer(plan).data)
