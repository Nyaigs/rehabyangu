from django.db import transaction
from .models import PatientBill, BillItem
from inventory.models import InventoryItem
from patients.models import Patient

def charge_patient(patient_id, item_id, quantity, administered_by):
    with transaction.atomic():
        patient = Patient.objects.select_for_update().get(id=patient_id)
        if not patient.tenant:
            from tenants.models import Tenant
            patient.tenant = Tenant.objects.first()
            patient.save()

        item = InventoryItem.objects.select_for_update().get(id=item_id)

        if item.category != 'SERVICE':
            if item.current_stock < quantity:
                raise ValueError(f"Not enough stock. Available: {item.current_stock}")
            item.current_stock -= quantity
            item.save()

        subtotal = quantity * item.unit_price

        bill, created = PatientBill.objects.select_for_update().get_or_create(
            patient=patient,
            defaults={
                'tenant': patient.tenant,
                'total_balance': 0
            }
        )
        if not bill.tenant:
            bill.tenant = patient.tenant
            bill.save()

        BillItem.objects.create(
            bill=bill,
            item=item,
            quantity=quantity,
            price_at_time=item.unit_price,
            subtotal=subtotal,
            administered_by=administered_by,
            notes=f"Charged {quantity} x {item.name} ({item.category})"
        )

        bill.total_balance += subtotal
        bill.save()

        return bill.total_balance
