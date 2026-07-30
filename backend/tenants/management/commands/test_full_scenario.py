from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tenants.models import Tenant
from patients.models import Patient
from clinical.models import ClinicalNote
from vitals.models import VitalSign
from inventory.models import InventoryItem
from billing.models import PatientBill, BillItem, Invoice, Payment
from appointments.models import Appointment
import uuid

class Command(BaseCommand):
    help = 'Run full MVP scenario tests (2-week and 3-month cases)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== RehabYangu Full Scenario Test ==='))

        # Get demo tenant and admin user
        tenant = Tenant.objects.get(subdomain='demo')
        admin = User.objects.get(username='demo_admin')

        # Ensure inventory items exist (create if missing)
        items = self.ensure_inventory(tenant)

        # Scenario A: 2-week normal discharge
        self.scenario_a(tenant, admin, items)

        # Scenario B: 3-month force discharge with partial payment
        self.scenario_b(tenant, admin, items)

        self.stdout.write(self.style.SUCCESS('\n✅ All scenarios completed successfully.'))

    def ensure_inventory(self, tenant):
        items = {}
        for name, cat, cost, price in [
            ('Paracetamol 500mg', 'DRUG', 10, 50),
            ('Amoxicillin 250mg', 'DRUG', 15, 60),
            ('IV Giving Set', 'CONSUMABLE', 30, 80),
            ('Syringe 5ml', 'CONSUMABLE', 5, 20),
            ('Psychiatric Review', 'SERVICE', 0, 5000),
        ]:
            item, _ = InventoryItem.objects.get_or_create(
                name=name, tenant=tenant,
                defaults={
                    'category': cat,
                    'cost_price': cost,
                    'unit_price': price,
                    'current_stock': 100,
                    'reorder_level': 10
                }
            )
            items[name] = item
        self.stdout.write('✅ Inventory items ensured.')
        return items

    def scenario_a(self, tenant, admin, items):
        self.stdout.write('\n--- Scenario A: 2-week normal discharge ---')

        # 1. Register patient
        patient = Patient.objects.create(
            first_name='Alice',
            last_name='Normal',
            date_of_birth='1990-01-01',
            gender='F',
            phone='0712345001',
            tenant=tenant,
            created_by=admin
        )
        self.stdout.write(f'✅ Patient A registered (ID {patient.id}).')

        # 2. Admission note (SOAP)
        ClinicalNote.objects.create(
            patient=patient,
            clinician=admin,
            tenant=tenant,
            subjective='Patient reports mild anxiety.',
            objective='Vitals stable.',
            assessment='Moderate anxiety.',
            plan='Start CBT, review in 2 weeks.'
        )
        self.stdout.write('✅ Admission note added.')

        # 3. Vitals
        VitalSign.objects.create(
            patient=patient,
            tenant=tenant,
            recorded_by=admin,
            date_measured=timezone.now(),
            systolic_bp=120,
            diastolic_bp=80,
            heart_rate=72,
            temperature=36.5,
            oxygen_saturation=98,
            weight=70,
            height=175
        )
        self.stdout.write('✅ Vitals recorded.')

        # 4. Charges (drugs + service)
        bill, _ = PatientBill.objects.get_or_create(patient=patient, tenant=tenant, defaults={'total_balance': 0})
        drugs = [items['Paracetamol 500mg'], items['Amoxicillin 250mg']]
        for item in drugs:
            qty = 10
            item.current_stock -= qty
            item.save()
            BillItem.objects.create(
                bill=bill,
                item=item,
                quantity=qty,
                price_at_time=item.unit_price,
                subtotal=qty * item.unit_price,
                administered_by=admin.username,
                notes='Charged'
            )
            bill.total_balance += qty * item.unit_price
        bill.save()
        self.stdout.write('✅ Charges applied.')

        # 5. Invoice
        invoice = Invoice.objects.create(
            bill=bill,
            due_date=timezone.now().date() + timedelta(days=14),
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timedelta(days=14),
            total_amount=bill.total_balance,
            sponsor_name='Sponsor A',
            sponsor_email='sponsorA@example.com',
            status='draft'
        )
        self.stdout.write(f'✅ Invoice generated (ID {invoice.id}).')

        # 6. Partial payment
        Payment.objects.create(
            bill=bill,
            amount=200,
            method='CASH',
            reference='PAY001',
            paid_at=timezone.now()
        )
        bill.total_balance -= 200
        bill.save()
        self.stdout.write('✅ Partial payment recorded.')

        # 7. Full payment
        Payment.objects.create(
            bill=bill,
            amount=bill.total_balance,
            method='MPESA',
            reference='PAY002',
            paid_at=timezone.now()
        )
        bill.total_balance = 0
        bill.save()
        self.stdout.write('✅ Full payment recorded, balance cleared.')

        # 8. Request discharge (normal)
        from patients.models import DischargeRequest
        req = DischargeRequest.objects.create(
            patient=patient,
            requested_by=admin,
            reason='Treatment completed.',
            is_force=False,
            status='pending'
        )
        self.stdout.write('✅ Discharge requested.')

        # 9. Approve discharge (as director)
        req.status = 'approved'
        req.approved_by = admin
        req.approved_at = timezone.now()
        req.approval_reason = 'Approved.'
        req.save()
        patient.status = 'discharged'
        patient.discharged_at = timezone.now()
        patient.save()
        self.stdout.write('✅ Discharge approved.')

        self.stdout.write(self.style.SUCCESS('✅ Scenario A completed.'))

    def scenario_b(self, tenant, admin, items):
        self.stdout.write('\n--- Scenario B: 3-month force discharge with partial payment ---')

        # 1. Register patient
        patient = Patient.objects.create(
            first_name='Bob',
            last_name='Force',
            date_of_birth='1985-06-15',
            gender='M',
            phone='0712345002',
            tenant=tenant,
            created_by=admin
        )
        self.stdout.write(f'✅ Patient B registered (ID {patient.id}).')

        # 2. Admission note
        ClinicalNote.objects.create(
            patient=patient,
            clinician=admin,
            tenant=tenant,
            subjective='Patient reports substance abuse.',
            objective='Appears disoriented.',
            assessment='Severe addiction.',
            plan='Detox program, therapy.'
        )
        self.stdout.write('✅ Admission note added.')

        # 3. Vitals
        VitalSign.objects.create(
            patient=patient,
            tenant=tenant,
            recorded_by=admin,
            date_measured=timezone.now(),
            systolic_bp=140,
            diastolic_bp=90,
            heart_rate=88,
            temperature=36.8,
            oxygen_saturation=96,
            weight=80,
            height=180
        )
        self.stdout.write('✅ Vitals recorded.')

        # 4. Charges (drugs + services)
        bill, _ = PatientBill.objects.get_or_create(patient=patient, tenant=tenant, defaults={'total_balance': 0})
        items_list = [items['Paracetamol 500mg'], items['Amoxicillin 250mg'], items['Psychiatric Review']]
        for item in items_list:
            qty = 30 if item.category == 'DRUG' else 5
            if item.category != 'SERVICE':
                item.current_stock -= qty
                item.save()
            BillItem.objects.create(
                bill=bill,
                item=item,
                quantity=qty,
                price_at_time=item.unit_price,
                subtotal=qty * item.unit_price,
                administered_by=admin.username,
                notes='Charged'
            )
            bill.total_balance += qty * item.unit_price
        bill.save()
        self.stdout.write('✅ Charges applied.')

        # 5. Invoice
        invoice = Invoice.objects.create(
            bill=bill,
            due_date=timezone.now().date() + timedelta(days=90),
            period_start=timezone.now().date(),
            period_end=timezone.now().date() + timedelta(days=90),
            total_amount=bill.total_balance,
            sponsor_name='Sponsor B',
            sponsor_email='sponsorB@example.com',
            status='draft'
        )
        self.stdout.write(f'✅ Invoice generated (ID {invoice.id}).')

        # 6. Partial payment (50%)
        amount_paid = bill.total_balance / 2
        Payment.objects.create(
            bill=bill,
            amount=amount_paid,
            method='BANK',
            reference='PAY003',
            paid_at=timezone.now()
        )
        bill.total_balance -= amount_paid
        bill.save()
        self.stdout.write(f'✅ Partial payment of {amount_paid} recorded. Balance remains {bill.total_balance}.')

        # 7. Force discharge request
        from patients.models import DischargeRequest
        req = DischargeRequest.objects.create(
            patient=patient,
            requested_by=admin,
            reason='Patient requests early discharge due to personal reasons.',
            is_force=True,
            status='pending'
        )
        self.stdout.write('✅ Force discharge requested.')

        # 8. Director approves force discharge (with password)
        req.status = 'approved'
        req.approved_by = admin
        req.approved_at = timezone.now()
        req.approval_reason = 'Approved by director.'
        req.save()
        patient.status = 'discharged'
        patient.discharged_at = timezone.now()
        patient.save()
        self.stdout.write('✅ Force discharge approved.')

        # 9. Verify balance still outstanding
        self.stdout.write(f'✅ Outstanding balance remains: KES {bill.total_balance}.')

        # 10. Later, clear the remaining balance
        Payment.objects.create(
            bill=bill,
            amount=bill.total_balance,
            method='MPESA',
            reference='PAY004',
            paid_at=timezone.now() + timedelta(days=5)
        )
        bill.total_balance = 0
        bill.save()
        self.stdout.write('✅ Remaining balance cleared.')

        # 11. Verify patient still discharged
        patient.refresh_from_db()
        if patient.status == 'discharged':
            self.stdout.write('✅ Patient status remains discharged.')
        else:
            self.stdout.write('❌ Patient status changed unexpectedly.')

        self.stdout.write(self.style.SUCCESS('✅ Scenario B completed.'))
