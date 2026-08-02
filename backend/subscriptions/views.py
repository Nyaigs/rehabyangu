from users.permissions import IsInTenant
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Subscription, PaymentRecord, Notification
from tenants.models import Tenant

class RecordPaymentView(APIView):
    permission_classes = IsAuthenticated

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Only Weiraro admins can record payments'}, status=status.HTTP_403_FORBIDDEN)

        tenant_id = request.data.get('tenant_id')
        amount = request.data.get('amount')
        method = request.data.get('method')
        reference = request.data.get('reference', '')
        notes = request.data.get('notes', '')
        paid_through_date = request.data.get('paid_through_date')  # ISO date string

        if not all([tenant_id, amount, method, paid_through_date]):
            return Response({'error': 'tenant_id, amount, method, paid_through_date are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            return Response({'error': 'Tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create payment record
        payment = PaymentRecord.objects.create(
            tenant=tenant,
            amount=amount,
            method=method,
            reference=reference,
            notes=notes,
            recorded_by=request.user,
            paid_through_date=paid_through_date
        )

        # Update subscription status to active, update next billing date
        subscription, created = Subscription.objects.get_or_create(tenant=tenant)
        subscription.status = 'active'
        subscription.next_billing_date = paid_through_date
        subscription.grace_period_end = None
        subscription.save()

        # Also update tenant status
        tenant.status = 'active'
        tenant.save()

        # Send notification to tenant admin about payment received
        Notification.objects.create(
            tenant=tenant,
            notification_type='reactivated',
            title='Payment Received',
            message=f'A payment of KES {amount} has been recorded. Your subscription is now active until {paid_through_date}.',
        )

        return Response({'message': 'Payment recorded and subscription updated.'}, status=status.HTTP_200_OK)

class NotificationListView(APIView):
    permission_classes = IsAuthenticated

    def get(self, request):
        # For tenant admins: see their tenant's notifications
        if request.user.is_superuser:
            # For superuser, show all notifications across all tenants (optional)
            notifications = Notification.objects.all().order_by('-created_at')
        else:
            # Tenant admin/staff: only see their tenant's notifications
            if hasattr(request.user, 'profile') and request.tenant:
                notifications = Notification.objects.filter(tenant=request.tenant).order_by('-created_at')
            else:
                return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        data = [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'type': n.notification_type,
            'is_read': n.is_read,
            'created_at': n.created_at,
        } for n in notifications]
        return Response(data)

class MarkNotificationReadView(APIView):
    permission_classes = IsAuthenticated

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check permissions: only tenant admin or superuser can mark
        if not request.user.is_superuser:
            if hasattr(request.user, 'profile') and request.tenant:
                if notification.tenant != request.tenant:
                    return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
