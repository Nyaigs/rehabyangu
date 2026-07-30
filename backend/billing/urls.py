from django.urls import path
from .views import (
    ChargePatientView,
    PatientBillView,
    InvoiceListView,
    GenerateInvoiceView,
    DownloadInvoiceView,
    SendInvoiceEmailView,
    InvoiceDownloadByTokenView,
)

urlpatterns = [
    path('charge/', ChargePatientView.as_view(), name='charge-patient'),
    path('patient-bill/<int:patient_id>/', PatientBillView.as_view(), name='patient-bill'),
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/generate/', GenerateInvoiceView.as_view(), name='generate-invoice'),
    path('invoices/<int:invoice_id>/download/', DownloadInvoiceView.as_view(), name='download-invoice'),
    path('invoices/<int:invoice_id>/send-email/', SendInvoiceEmailView.as_view(), name='send-invoice-email'),
    path('invoice/download/<uuid:token>/', InvoiceDownloadByTokenView.as_view(), name='download-invoice-token'),
]
