from rest_framework import serializers
from .models import PatientBill, BillItem, Invoice

class BillItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    category = serializers.CharField(source='item.category', read_only=True)
    class Meta:
        model = BillItem
        fields = ['id', 'item', 'item_name', 'category', 'quantity', 'price_at_time', 'subtotal', 'charged_at', 'administered_by', 'notes']

class PatientBillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)
    class Meta:
        model = PatientBill
        fields = ['id', 'patient', 'patient_name', 'total_balance', 'items', 'updated_at']

class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='bill.patient.__str__', read_only=True)
    tenant_name = serializers.CharField(source='bill.tenant.name', read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('invoice_number', 'generated_at', 'sent_at', 'download_token', 'token_expiry')
