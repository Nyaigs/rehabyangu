from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from .models import Admission, Patient, DischargeRequest, TreatmentGoal, TreatmentPlan
from .serializers import AdmissionSerializer, PatientSerializer, TreatmentGoalSerializer, TreatmentPlanSerializer
from billing.models import PatientBill
from subscriptions.models import Notification
from authorization.permissions import HasPermission
from users.permissions import IsInTenant
from users.services import audit
from users.models import TenantMembership

class PatientPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsInTenant]
    pagination_class = PatientPagination
    # Clinical records are retained; this API deliberately has no DELETE.
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_permissions(self):
        action_permissions = {
            'list': 'patient.read',
            'retrieve': 'patient.read',
            'create': 'patient.write',
            'update': 'patient.write',
            'partial_update': 'patient.write',
        }
        codename = action_permissions.get(self.action, 'patient.read')
        return [IsAuthenticated(), IsInTenant(), HasPermission(codename)]

    def get_queryset(self):
        queryset = self.queryset.filter(tenant=self.request.tenant)
        search = self.request.query_params.get('search', '').strip()
        workflow = self.request.query_params.get('filter', '').strip()
        if search:
            terms = search.split()
            query = (Q(first_name__icontains=search) | Q(last_name__icontains=search) |
                     Q(patient_id__icontains=search) | Q(phone__icontains=search) |
                     Q(national_id__icontains=search))
            if len(terms) > 1:
                query |= Q(first_name__icontains=terms[0], last_name__icontains=' '.join(terms[1:]))
            queryset = queryset.filter(query)
        filters = {
            'admitted': Q(admissions__status='admitted'),
            'outpatient': Q(care_type='outpatient') & ~Q(status__in=['discharged', 'transferred', 'inactive']),
            'day_patient': Q(care_type='day_patient') & ~Q(status__in=['discharged', 'transferred', 'inactive']),
            'discharged': Q(status='discharged'),
            'registered': Q(status='registered'),
            'transferred': Q(status='transferred'),
        }
        if workflow in filters:
            queryset = queryset.filter(filters[workflow]).distinct()
        return queryset
    def perform_create(self, serializer):
        user = self.request.user
        patient = serializer.save(created_by=user, tenant=self.request.tenant)
        audit(actor=user, tenant=self.request.tenant, action='CREATE', request=self.request, instance=patient, description=f'Created patient {patient.id}.')

    def perform_update(self, serializer):
        patient = serializer.save()
        audit(actor=self.request.user, tenant=self.request.tenant, action='UPDATE', request=self.request, instance=patient, description=f'Updated patient {patient.id}.')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, description='Read patient demographics list.')
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, instance=self.get_object(), description=f'Read patient {kwargs["pk"]} demographics and permitted sensitive fields.')
        return response


class TenantScopedClinicalViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsInTenant]
    # Retention is mandatory for EMR data. Corrections are new writes, not deletes.
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    permission_read = 'clinical.read'
    permission_write = 'clinical.write'

    def get_permissions(self):
        codename = self.permission_write if self.action in ('create', 'update', 'partial_update') else self.permission_read
        return [IsAuthenticated(), IsInTenant(), HasPermission(codename)]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, description=f'Read {self.basename.replace("-", " ")} list.')
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        audit(actor=request.user, tenant=request.tenant, action='READ', request=request, description=f'Read {self.basename.replace("-", " ")} {kwargs["pk"]}.')
        return response


class AdmissionViewSet(TenantScopedClinicalViewSet):
    serializer_class = AdmissionSerializer

    def get_queryset(self):
        queryset = Admission.objects.filter(tenant=self.request.tenant).select_related('patient')
        patient_id = self.request.query_params.get('patient')
        status_filter = self.request.query_params.get('status')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if status_filter in ('admitted', 'discharged'):
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        admission = serializer.save(tenant=self.request.tenant, created_by=self.request.user)
        if admission.patient.status == 'discharged':
            admission.patient.status = 'active'
            admission.patient.discharged_at = None
            admission.patient.save(update_fields=['status', 'discharged_at', 'updated_at'])
        audit(actor=self.request.user, tenant=self.request.tenant, action='CREATE', request=self.request, instance=admission, description=f'Created admission {admission.admission_number} for patient {admission.patient_id}.')

    def perform_update(self, serializer):
        admission = serializer.save()
        audit(actor=self.request.user, tenant=self.request.tenant, action='UPDATE', request=self.request, instance=admission, description=f'Updated admission {admission.admission_number}.')

    @action(detail=False, methods=['get'], url_path='bed-availability')
    def bed_availability(self, request):
        room, bed = request.query_params.get('room'), request.query_params.get('bed')
        occupied = Admission.objects.filter(tenant=request.tenant, discharge_date__isnull=True)
        if room:
            occupied = occupied.filter(room=room)
        if bed:
            occupied = occupied.filter(bed=bed)
        return Response({'room': room, 'bed': bed, 'available': not occupied.exists(), 'occupied_by': occupied.values_list('patient__first_name', 'patient__last_name')[:1]})

    @action(detail=True, methods=['post'], url_path='discharge')
    def discharge(self, request, pk=None):
        admission = self.get_object()
        if admission.discharge_date:
            return Response({'detail': 'This admission is already discharged.'}, status=status.HTTP_400_BAD_REQUEST)
        reason = str(request.data.get('reason', '')).strip()
        if not reason:
            return Response({'reason': 'A discharge reason is required.'}, status=status.HTTP_400_BAD_REQUEST)
        admission.discharge_date = timezone.now()
        admission.status = 'discharged'
        admission.refresh_stay_length()
        admission.save(update_fields=['discharge_date', 'status', 'length_of_stay_days', 'updated_at'])
        patient = admission.patient
        patient.status, patient.discharged_at = 'discharged', admission.discharge_date
        patient.notes = f"{patient.notes or ''}\n--- Admission discharge ---\nReason: {reason}\n"
        patient.save(update_fields=['status', 'discharged_at', 'notes', 'updated_at'])
        audit(actor=request.user, tenant=request.tenant, action='UPDATE', request=request, instance=admission, description=f'Discharged admission {admission.admission_number}: {reason}')
        return Response(self.get_serializer(admission).data)


class TreatmentPlanViewSet(TenantScopedClinicalViewSet):
    serializer_class = TreatmentPlanSerializer

    def get_queryset(self):
        queryset = TreatmentPlan.objects.filter(tenant=self.request.tenant).select_related('patient', 'admission').prefetch_related('goals')
        patient_id = self.request.query_params.get('patient')
        return queryset.filter(patient_id=patient_id) if patient_id else queryset

    def perform_create(self, serializer):
        plan = serializer.save(tenant=self.request.tenant, created_by=self.request.user)
        audit(actor=self.request.user, tenant=self.request.tenant, action='CREATE', request=self.request, instance=plan, description=f'Created treatment plan {plan.id} for patient {plan.patient_id}.')

    def perform_update(self, serializer):
        plan = serializer.save()
        audit(actor=self.request.user, tenant=self.request.tenant, action='UPDATE', request=self.request, instance=plan, description=f'Updated treatment plan {plan.id}.')


class TreatmentGoalViewSet(TenantScopedClinicalViewSet):
    serializer_class = TreatmentGoalSerializer

    def get_queryset(self):
        queryset = TreatmentGoal.objects.filter(tenant=self.request.tenant).select_related('treatment_plan')
        plan_id = self.request.query_params.get('treatment_plan')
        return queryset.filter(treatment_plan_id=plan_id) if plan_id else queryset

    def perform_create(self, serializer):
        plan_id = self.request.data.get('treatment_plan')
        plan = TreatmentPlan.objects.filter(id=plan_id, tenant=self.request.tenant).first()
        if not plan:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'treatment_plan': 'Treatment plan is outside this tenant.'})
        goal = serializer.save(tenant=self.request.tenant, treatment_plan=plan, updated_by=self.request.user)
        audit(actor=self.request.user, tenant=self.request.tenant, action='CREATE', request=self.request, instance=goal, description=f'Created treatment goal {goal.id} for plan {plan.id}.')

    def perform_update(self, serializer):
        goal = serializer.save(updated_by=self.request.user)
        audit(actor=self.request.user, tenant=self.request.tenant, action='UPDATE', request=self.request, instance=goal, description=f'Updated treatment goal {goal.id}.')

class RequestDischargeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('discharge.request')]

    def post(self, request, pk):
        user = request.user
        if not request.tenant_membership:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        try:
            patient = Patient.objects.get(id=pk, tenant=request.tenant)
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
        audit(actor=user, tenant=request.tenant, action='CREATE', request=request, instance=discharge_request, description=f'Created discharge request {discharge_request.id} for patient {patient.id}.')

        admin_profiles = TenantMembership.objects.filter(tenant=request.tenant, is_rehab_admin=True)
        for membership in admin_profiles:
            Notification.objects.create(
                tenant=patient.tenant,
                recipient=membership.user,
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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('discharge.approve')]

    def post(self, request, pk):
        user = request.user
        if not request.tenant_membership or not request.tenant_membership.is_rehab_admin:
            return Response({'error': 'Only rehab admins can approve discharges'}, status=status.HTTP_403_FORBIDDEN)

        try:
            discharge_request = DischargeRequest.objects.get(id=pk, patient__tenant=request.tenant)
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
        audit(actor=user, tenant=request.tenant, action='UPDATE', request=request, instance=patient, description=f'Discharged patient {patient.id}.')

        discharge_request.status = 'approved'
        discharge_request.approved_by = user
        discharge_request.approved_at = timezone.now()
        discharge_request.approval_reason = approval_reason
        discharge_request.save()
        audit(actor=user, tenant=request.tenant, action='UPDATE', request=request, instance=discharge_request, description=f'Approved discharge request {discharge_request.id}.')

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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('discharge.approve')]

    def post(self, request, pk):
        user = request.user
        if not request.tenant_membership or not request.tenant_membership.is_rehab_admin:
            return Response({'error': 'Only rehab admins can reject discharges'}, status=status.HTTP_403_FORBIDDEN)

        try:
            discharge_request = DischargeRequest.objects.get(id=pk, patient__tenant=request.tenant)
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
        audit(actor=user, tenant=request.tenant, action='UPDATE', request=request, instance=discharge_request, description=f'Rejected discharge request {discharge_request.id}.')

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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('discharge.approve')]

    def get(self, request):
        user = request.user
        if not request.tenant_membership or not request.tenant_membership.is_rehab_admin:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        pending = DischargeRequest.objects.filter(
            patient__tenant=request.tenant,
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
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasPermission('patient.read')]

    def get(self, request):
        if not request.tenant_membership:
            return Response({'error': 'User not associated with a tenant'}, status=status.HTTP_403_FORBIDDEN)

        patients = Patient.objects.filter(
            tenant=request.tenant,
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
