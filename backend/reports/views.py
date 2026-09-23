from datetime import datetime, time

from django.db.models import Sum
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.permissions import HasPermission, HasFeature

from billing.models import Invoice, Payment
from patients.models import Admission
from users.permissions import IsInTenant


class TenantReportView(APIView):
    permission_classes = [IsAuthenticated, IsInTenant]

    def get_permissions(self):
        return [IsAuthenticated(), IsInTenant(), HasFeature('analytics'), HasPermission('reports.read')]

    def date_range(self, request):
        today = timezone.localdate()
        try:
            start = datetime.fromisoformat(request.query_params.get('from', str(today))).date()
            end = datetime.fromisoformat(request.query_params.get('to', str(today))).date()
        except ValueError:
            start = end = today
        if start > end:
            start, end = end, start
        return start, end


class OccupancyReportView(TenantReportView):
    def get(self, request):
        occupied = Admission.objects.filter(tenant=request.tenant, status='admitted').exclude(bed='').count()
        # Bed capacity is not modelled yet. Do not invent a denominator: expose
        # null so the client can show an honest "not configured" state.
        return Response({'occupied_beds': occupied, 'total_beds': None, 'occupancy_percent': None})


class CensusReportView(TenantReportView):
    def get(self, request):
        return Response({'current_census': Admission.objects.filter(tenant=request.tenant, status='admitted').count()})


class AdmissionsReportView(TenantReportView):
    def get(self, request):
        start, end = self.date_range(request)
        return Response({'from': str(start), 'to': str(end), 'admissions': Admission.objects.filter(tenant=request.tenant, intake_date__date__range=(start, end)).count()})


class DischargesReportView(TenantReportView):
    def get(self, request):
        start, end = self.date_range(request)
        return Response({'from': str(start), 'to': str(end), 'discharges': Admission.objects.filter(tenant=request.tenant, discharge_date__date__range=(start, end)).count()})


class RevenueReportView(TenantReportView):
    def get(self, request):
        start, end = self.date_range(request)
        payments = Payment.objects.filter(bill__tenant=request.tenant, paid_at__date__range=(start, end))
        outstanding = Invoice.objects.filter(bill__tenant=request.tenant).aggregate(value=Sum('total_amount')).get('value') or 0
        paid = Invoice.objects.filter(bill__tenant=request.tenant).aggregate(value=Sum('amount_paid')).get('value') or 0
        return Response({'from': str(start), 'to': str(end), 'total_collected': payments.aggregate(value=Sum('amount')).get('value') or 0, 'outstanding_balance': max(outstanding - paid, 0)})


class OutstandingReportView(TenantReportView):
    def get(self, request):
        today = timezone.localdate()
        buckets = {'0_30': 0, '31_60': 0, '61_90': 0, '90_plus': 0}
        for invoice in Invoice.objects.filter(bill__tenant=request.tenant).exclude(status='paid'):
            balance = max(invoice.total_amount - invoice.amount_paid, 0)
            days = max(0, (today - invoice.due_date).days)
            key = '0_30' if days <= 30 else '31_60' if days <= 60 else '61_90' if days <= 90 else '90_plus'
            buckets[key] += balance
        return Response({'as_of': str(today), 'aging': buckets})
