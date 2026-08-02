from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Patient, DischargeRequest
from .serializers import PatientSerializer
from billing.models import PatientBill
from subscriptions.models import Notification
from authorization.permissions import HasPermission
from users.models import UserProfile
from tenants.models import Tenant

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        action_permissions = {
            'list': 'patient:view',
            'retrieve': 'patient:view',
            'create': 'patient:create',
            'update': 'patient:edit',
            'partial_update': 'patient:edit',
            'destroy': 'patient:delete',
        }
        codename = action_permissions.get(self.action, 'patient:view')
        return [IsAuthenticated(), HasPermission(codename)]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        if hasattr(user, 'profile') and user.profile.tenant:
            return self.queryset.filter(tenant=user.profile.tenant)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        tenant = None
        if hasattr(user, 'profile') and user.profile.tenant:
            tenant = user.profile.tenant
        if not tenant:
            tenant = Tenant.objects.first()
        serializer.save(created_by=user, tenant=tenant)

class RequestDischargeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('discharge:request')]

    def post(self, request, pk):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.tenant:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        try:
            patient = Patient.objects.get(id=pk, tenant=user.profile.tenant)
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)

        if patient.status == 'discharged':
            return Response({'error': 'Patient is already discharged'}, status=status.HTTP_400_BAD_REQUEST)

        reason = request.data.get('reason', '')
        is_force = request.data.get('force', False)

        if is_force and not reason:
            return Response({'error': 'Reason is required for force discharge'}, status=status.HTTP_400_BAD_REQUEST)

        if DischargeRequest.objects.filter(patient=patient, status='pending').exists():
            return Response({'error': 'A discharge request is already pending approval'}, status=status.HTTP_400_BAD_REQUEST)

        discharge_request = DischargeRequest.objects.create(
            patient=patient,
            requested_by=user,
            reason=reason,
            is_force=is_force,
            status='pending'
        )

        admin_profiles = UserProfile.objects.filter(tenant=user.profile.tenant, is_rehab_admin=True)
        for profile in admin_profiles:
            Notification.objects.create(
                tenant=patient.tenant,
                recipient=profile.user,
                notification_type='other',
                title='New Discharge Request',
                message=f'{user.username} requested discharge for {patient.first_name} {patient.last_name}.'
            )

        return Response({
            'message': 'Discharge request submitted for approval',
            'request_id': discharge_request.id,
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)

class ApproveDischargeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('discharge:approve')]

    def post(self, request, pk):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.is_rehab_admin:
            return Response({'error': 'Only rehab admins can approve discharges'}, status=status.HTTP_403_FORBIDDEN)

        try:
            discharge_request = DischargeRequest.objects.get(id=pk, patient__tenant=user.profile.tenant)
        except DischargeRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        if discharge_request.status != 'pending':
            return Response({'error': 'This request is already processed'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        approval_reason = request.data.get('approval_reason', '')

        if not password:
            return Response({'error': 'Password required for approval'}, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

        patient = discharge_request.patient
        patient.status = 'discharged'
        patient.discharged_at = timezone.now()
        patient.save()

        discharge_request.status = 'approved'
        discharge_request.approved_by = user
        discharge_request.approved_at = timezone.now()
        discharge_request.approval_reason = approval_reason
        discharge_request.save()

        log_entry = f"\n--- Discharge Approved ---\n"
        log_entry += f"Requested by: {discharge_request.requested_by.username} at {discharge_request.requested_at}\n"
        log_entry += f"Reason: {discharge_request.reason}\n"
        log_entry += f"Force: {discharge_request.is_force}\n"
        log_entry += f"Approved by: {user.username} at {timezone.now()}\n"
        log_entry += f"Approval reason: {approval_reason}\n"
        patient.notes = (patient.notes or "") + log_entry
        patient.save()

        Notification.objects.create(
            tenant=patient.tenant,
            recipient=discharge_request.requested_by,
            notification_type='other',
            title='Discharge Approved',
            message=f'Your discharge request for {patient.first_name} {patient.last_name} has been approved.',
        )

        return Response({'message': 'Discharge approved successfully', 'patient_status': 'discharged'})

class RejectDischargeView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('discharge:approve')]

    def post(self, request, pk):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.is_rehab_admin:
            return Response({'error': 'Only rehab admins can reject discharges'}, status=status.HTTP_403_FORBIDDEN)

        try:
            discharge_request = DischargeRequest.objects.get(id=pk, patient__tenant=user.profile.tenant)
        except DischargeRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        if discharge_request.status != 'pending':
            return Response({'error': 'This request is already processed'}, status=status.HTTP_400_BAD_REQUEST)

        rejection_reason = request.data.get('rejection_reason', '')
        if not rejection_reason:
            return Response({'error': 'Rejection reason required'}, status=status.HTTP_400_BAD_REQUEST)

        discharge_request.status = 'rejected'
        discharge_request.rejection_reason = rejection_reason
        discharge_request.save()

        patient = discharge_request.patient
        Notification.objects.create(
            tenant=patient.tenant,
            recipient=discharge_request.requested_by,
            notification_type='other',
            title='Discharge Request Rejected',
            message=f'Your discharge request for {patient.first_name} {patient.last_name} was rejected. Reason: {rejection_reason}',
        )

        return Response({'message': 'Discharge request rejected'})

class PendingDischargesView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('discharge:approve')]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.is_rehab_admin:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        pending = DischargeRequest.objects.filter(
            patient__tenant=user.profile.tenant,
            status='pending'
        ).select_related('patient', 'requested_by')

        data = [{
            'id': req.id,
            'patient_name': str(req.patient),
            'requested_by': req.requested_by.username,
            'requested_at': req.requested_at,
            'reason': req.reason,
            'is_force': req.is_force,
            'patient_id': req.patient.id,
        } for req in pending]
        return Response(data)

class DischargedPatientsView(APIView):
    permission_classes = [IsAuthenticated, HasPermission('patient:view')]

    def get(self, request):
        user = request.user
        if not hasattr(user, 'profile') or not user.profile.tenant:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        patients = Patient.objects.filter(
            tenant=user.profile.tenant,
            status='discharged'
        ).order_by('-discharged_at').select_related('bill')

        data = []
        for p in patients:
            bill = getattr(p, 'bill', None)
            balance = bill.total_balance if bill else 0
            discharge_req = p.discharge_requests.filter(status='approved').order_by('-approved_at').first()
            data.append({
                'id': p.id,
                'first_name': p.first_name,
                'last_name': p.last_name,
                'phone': p.phone,
                'discharged_at': p.discharged_at,
                'balance': balance,
                'is_force': discharge_req.is_force if discharge_req else False,
                'discharge_reason': discharge_req.reason if discharge_req else '',
                'approved_by': discharge_req.approved_by.username if discharge_req and discharge_req.approved_by else None,
                'approved_at': discharge_req.approved_at if discharge_req else None,
            })
        return Response(data)
