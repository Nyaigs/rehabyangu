import io
import os
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Invoice
from tenants.models import TenantConfig


def _colour(value, fallback):
    """Return a ReportLab colour from a tenant #RRGGBB value."""
    try:
        return colors.HexColor(value)
    except (TypeError, ValueError):
        return colors.HexColor(fallback)


def _logo_path(config):
    """Get a local logo path for ReportLab without relying on MEDIA_URL."""
    if not config or not config.logo:
        return None
    try:
        path = config.logo.path
        if os.path.exists(path):
            return path
    except (NotImplementedError, ValueError):
        pass
    # Non-local storage backends do not expose FieldFile.path.  ReportLab needs
    # a filename, so materialise a short-lived local copy for this render.
    try:
        with default_storage.open(config.logo.name, 'rb') as source:
            temporary = io.BytesIO(source.read())
        # Image accepts file-like objects and keeps the bytes for document build.
        temporary.seek(0)
        return temporary
    except Exception:
        return None

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
    tenant = invoice.bill.tenant
    tenant_config, _ = TenantConfig.objects.get_or_create(
        tenant=tenant,
        defaults={
            'company_name': tenant.name,
            'footer_text': f'{tenant.name} – Powered by RehabYangu',
        },
    )
    primary_colour = _colour(tenant_config.primary_color, '#2563EB')
    company_name = tenant_config.company_name or tenant.name

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
    brand_style = ParagraphStyle('Brand', parent=styles['Heading1'], fontSize=18, leading=22,
                                 textColor=primary_colour, spaceAfter=2)
    tagline_style = ParagraphStyle('Tagline', parent=normal_style, fontSize=9,
                                   textColor=colors.HexColor('#475569'))
    
    # Build content
    story = []
    
    # ===== Header =====
    logo = _logo_path(tenant_config)
    try:
        logo_cell = Image(logo, width=2.5*cm, height=2.5*cm) if logo else ''
    except Exception:
        logo_cell = ''
    brand_lines = [Paragraph(escape(company_name), brand_style)]
    if tenant_config.tagline:
        brand_lines.append(Paragraph(escape(tenant_config.tagline), tagline_style))
    header = Table([[logo_cell, brand_lines]], colWidths=[3.0*cm, 14.0*cm], hAlign='LEFT')
    header.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0)]))
    story.append(header)
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
        ('BACKGROUND', (0,0), (-1,0), primary_colour),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t3)
    story.append(Spacer(1, 0.3*cm))
    
    # ===== Totals =====
    payments_total = invoice.amount_paid
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

    # ===== Payment instructions =====
    story.append(Paragraph('PAYMENT DETAILS', heading_style))
    payment_rows = []
    if tenant_config.mpesa_shortcode:
        payment_rows.extend([
            [f'M-Pesa {tenant_config.mpesa_shortcode_type.title()}:', tenant_config.mpesa_shortcode],
            ['Account reference:', invoice.invoice_number],
        ])
    if tenant_config.bank_name:
        account = ' · '.join(part for part in [tenant_config.bank_account_name, tenant_config.bank_account_number, tenant_config.bank_branch] if part)
        payment_rows.append(['Bank:', f'{tenant_config.bank_name}{(" — " + account) if account else ""}'])
    if tenant_config.kra_pin:
        payment_rows.append(['KRA PIN:', tenant_config.kra_pin])
    if payment_rows:
        payment_table = Table(payment_rows, colWidths=[4*cm, 10*cm])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(payment_table)
    else:
        story.append(Paragraph('Contact the facility for payment instructions.', normal_style))
    if tenant_config.invoice_terms:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(escape(tenant_config.invoice_terms).replace('\n', '<br/>'), normal_style))
    if tenant_config.invoice_footer_text:
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(escape(tenant_config.invoice_footer_text).replace('\n', '<br/>'), normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # ===== Footer =====
    if tenant_config.footer_text:
        story.append(Paragraph(escape(tenant_config.footer_text), center_style))
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
