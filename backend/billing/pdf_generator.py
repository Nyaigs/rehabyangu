import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models  # <-- Added missing import
from .models import Invoice

def generate_invoice_pdf(invoice):
    """
    Generate a PDF invoice and save it to the invoice.pdf_file field.
    Returns the invoice object with updated pdf_file.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=0.5*cm
    )
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=0.3*cm
    )
    normal_style = styles['Normal']
    right_style = ParagraphStyle('Right', parent=normal_style, alignment=TA_RIGHT)
    center_style = ParagraphStyle('Center', parent=normal_style, alignment=TA_CENTER)
    
    # Build content
    story = []
    
    # ===== Header =====
    # Logo (if available) - safely check path
    static_dir = os.path.join(settings.BASE_DIR, 'static')
    logo_path = os.path.join(static_dir, 'logo.png')
    if os.path.exists(logo_path):
        try:
            story.append(Image(logo_path, width=2*inch, height=1*inch))
            story.append(Spacer(1, 0.2*cm))
        except Exception:
            # If logo fails to load, skip it
            pass
    
    # Rehab Name
    tenant_name = invoice.bill.tenant.name
    story.append(Paragraph(f"<b>{tenant_name}</b>", title_style))
    story.append(Paragraph("Rehabilitation Centre", center_style))
    story.append(Spacer(1, 0.5*cm))
    
    # ===== Invoice Title =====
    story.append(Paragraph("INVOICE", title_style))
    story.append(Spacer(1, 0.3*cm))
    
    # ===== Invoice Details =====
    invoice_data = [
        ["Invoice Number:", invoice.invoice_number],
        ["Date:", invoice.generated_at.strftime('%Y-%m-%d')],
        ["Due Date:", invoice.due_date.strftime('%Y-%m-%d')],
        ["Period:", f"{invoice.period_start.strftime('%Y-%m-%d')} to {invoice.period_end.strftime('%Y-%m-%d')}"],
    ]
    t = Table(invoice_data, colWidths=[3*cm, 8*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    
    # ===== Patient & Sponsor =====
    patient = invoice.bill.patient
    sponsor_name = invoice.sponsor_name or "Not specified"
    sponsor_email = invoice.sponsor_email or "Not provided"
    
    party_data = [
        ["Patient:", f"{patient.first_name} {patient.last_name}"],
        ["Phone:", patient.phone],
        ["Sponsor:", sponsor_name],
        ["Sponsor Email:", sponsor_email],
    ]
    t2 = Table(party_data, colWidths=[3*cm, 8*cm])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))
    
    # ===== Cover Letter =====
    if invoice.cover_letter_text:
        story.append(Paragraph("Cover Note", heading_style))
        story.append(Paragraph(invoice.cover_letter_text, normal_style))
        story.append(Spacer(1, 0.3*cm))
    
    # ===== Items Table =====
    story.append(Paragraph("Charges", heading_style))
    bill_items = invoice.bill.items.all()
    table_data = [["#", "Description", "Quantity", "Unit Price (KES)", "Total (KES)"]]
    total = 0
    for idx, item in enumerate(bill_items, start=1):
        table_data.append([
            str(idx),
            item.item.name,
            str(item.quantity),
            f"{item.price_at_time:.2f}",
            f"{item.subtotal:.2f}",
        ])
        total += item.subtotal
    
    col_widths = [0.8*cm, 6*cm, 1.5*cm, 2.5*cm, 2.5*cm]
    t3 = Table(table_data, colWidths=col_widths)
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3*cm))
    
    # ===== Totals =====
    payments_total = invoice.bill.payments.aggregate(total=models.Sum('amount'))['total'] or 0
    balance_due = invoice.total_amount - payments_total
    
    totals_data = [
        ["Total Amount:", f"KES {invoice.total_amount:.2f}"],
        ["Payments Received:", f"KES {payments_total:.2f}"],
        ["Balance Due:", f"KES {balance_due:.2f}"],
    ]
    t4 = Table(totals_data, colWidths=[6*cm, 5*cm])
    t4.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(t4)
    story.append(Spacer(1, 0.5*cm))
    
    # ===== Footer =====
    story.append(Paragraph("Thank you for your continued support.", center_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Payment instructions:", normal_style))
    story.append(Paragraph("Bank: Equity Bank | Account: 1234567890 | Branch: Nairobi", normal_style))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("This is a computer-generated invoice.", normal_style))
    
    # Build PDF
    doc.build(story)
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Save to model
    filename = f"INV-{invoice.invoice_number}.pdf"
    invoice.pdf_file.save(filename, ContentFile(pdf_content), save=True)
    
    return invoice
