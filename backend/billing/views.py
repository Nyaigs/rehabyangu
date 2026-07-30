from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, Http404  # Http404 added
from .services import charge_patient
from .models import PatientBill, Invoice
from .serializers import PatientBillSerializer, InvoiceSerializer
from patients.models import Patient
from inventory.models import InventoryItem
from .pdf_generator import generate_invoice_pdf

class ChargePatientView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        patient_id = request.data.get('patient_id')
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')

        if not all([patient_id, item_id, quantity]):
            return Response(
                {'error': 'patient_id, item_id, and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            return Response(
                {'error': 'quantity must be a positive integer'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_balance = charge_patient(
                patient_id=patient_id,
                item_id=item_id,
                quantity=quantity,
                administered_by=request.user.get_full_name() or request.user.username
            )
            return Response({
                'message': 'Charge applied successfully',
                'new_balance': str(new_balance)
            }, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except InventoryItem.DoesNotExist:
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PatientBillView(RetrieveAPIView):
    queryset = PatientBill.objects.all()
    serializer_class = PatientBillSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        patient_id = self.kwargs.get('patient_id')
        bill, created = PatientBill.objects.get_or_create(
            patient_id=patient_id,
            defaults={'tenant': self.request.user.profile.tenant}
        )
        return bill

class InvoiceListView(ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            try:
                bill = PatientBill.objects.get(
                    patient_id=patient_id,
                    tenant=self.request.user.profile.tenant
                )
                return Invoice.objects.filter(bill=bill).order_by('-generated_at')
            except PatientBill.DoesNotExist:
                return Invoice.objects.none()
        return Invoice.objects.filter(
            bill__tenant=self.request.user.profile.tenant
        ).order_by('-generated_at')

class GenerateInvoiceView(CreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        patient_id = request.data.get('patient_id')
        cover_letter = request.data.get('cover_letter', '')
        sponsor_email = request.data.get('sponsor_email', '')
        sponsor_name = request.data.get('sponsor_name', '')
        sponsor_phone = request.data.get('sponsor_phone', '')
        due_date = request.data.get('due_date')
        period_start = request.data.get('period_start')
        period_end = request.data.get('period_end')

        if not patient_id:
            return Response(
                {'error': 'patient_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            patient = Patient.objects.get(
                id=patient_id,
                tenant=self.request.user.profile.tenant
            )
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        bill, _ = PatientBill.objects.get_or_create(
            patient=patient,
            tenant=patient.tenant
        )

        total_amount = sum(item.subtotal for item in bill.items.all())
        if total_amount == 0:
            return Response(
                {'error': 'No charges to invoice. Patient balance is zero.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        invoice = Invoice.objects.create(
            bill=bill,
            due_date=due_date or (timezone.now().date() + timezone.timedelta(days=30)),
            period_start=period_start or timezone.now().date(),
            period_end=period_end or timezone.now().date(),
            total_amount=total_amount,
            cover_letter_text=cover_letter,
            sponsor_email=sponsor_email,
            sponsor_name=sponsor_name,
            sponsor_phone=sponsor_phone,
            status='draft'
        )

        generate_invoice_pdf(invoice)
        return Response(
            InvoiceSerializer(invoice).data,
            status=status.HTTP_201_CREATED
        )

class DownloadInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if invoice.bill.tenant != request.user.profile.tenant and not request.user.is_superuser:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not invoice.pdf_file:
            generate_invoice_pdf(invoice)

        response = HttpResponse(
            invoice.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="INV-{invoice.invoice_number}.pdf"'
        )
        return response

class SendInvoiceEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if invoice.bill.tenant != request.user.profile.tenant and not request.user.is_superuser:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not invoice.pdf_file:
            generate_invoice_pdf(invoice)

        recipient = invoice.sponsor_email or request.data.get('email')
        if not recipient:
            return Response(
                {'error': 'No email address provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subject = f"Invoice {invoice.invoice_number} from {invoice.bill.tenant.name}"
        body = f"""
Dear {invoice.sponsor_name or 'Sponsor'},

Please find attached your invoice {invoice.invoice_number} for patient {invoice.bill.patient.first_name} {invoice.bill.patient.last_name}.

Amount Due: KES {invoice.total_amount:.2f}
Due Date: {invoice.due_date}

Thank you for your continued support.

Regards,
{invoice.bill.tenant.name}
"""
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        email.attach(
            f"INV-{invoice.invoice_number}.pdf",
            invoice.pdf_file.read(),
            'application/pdf'
        )
        email.send()

        invoice.status = 'sent'
        invoice.sent_at = timezone.now()
        invoice.save()

        return Response({'message': 'Email sent successfully'})

# ===== NEW: Public download by token =====
class InvoiceDownloadByTokenView(APIView):
    permission_classes = []  # public access, token is secret

    def get(self, request, token):
        try:
            invoice = Invoice.objects.get(download_token=token)
        except Invoice.DoesNotExist:
            raise Http404("Invoice not found")

        if invoice.token_expiry and invoice.token_expiry < timezone.now():
            raise Http404("Link expired")

        if not invoice.pdf_file:
            generate_invoice_pdf(invoice)

        response = HttpResponse(
            invoice.pdf_file.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="INV-{invoice.invoice_number}.pdf"'
        )
        return response
