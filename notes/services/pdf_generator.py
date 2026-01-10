# notes/services/pdf_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from django.core.files.base import ContentFile
from io import BytesIO
from datetime import datetime


def generate_news_pdf(report):
    """Generate professional news report PDF"""
    
    buffer = BytesIO()
    
    # Create PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for elements
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        leading=14
    )
    
    meta_style = ParagraphStyle(
        'MetaInfo',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Header
    elements.append(Paragraph("NEWS VERIFICATION REPORT", title_style))
    elements.append(Paragraph(report.title, heading_style))
    
    # Meta information
    meta_text = f"""
    Generated: {report.generated_at.strftime('%B %d, %Y at %H:%M')}<br/>
    Language: {report.get_language_display()}<br/>
    Total Claims: {report.claims.count()}
    """
    elements.append(Paragraph(meta_text, meta_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    
    claims = report.claims.all()
    status_counts = {
        'verified': 0,
        'false': 0,
        'misleading': 0,
        'pending': 0
    }
    
    for claim in claims:
        status_counts[claim.status] = status_counts.get(claim.status, 0) + 1
    
    summary_text = f"""
    This report analyzes {claims.count()} claims extracted from various sources.
    Verified: {status_counts['verified']} | 
    False: {status_counts['false']} | 
    Misleading: {status_counts['misleading']} | 
    Pending: {status_counts['pending']}
    """
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Claims Section
    elements.append(Paragraph("Detailed Claims Analysis", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    for i, claim in enumerate(claims, 1):
        # Claim number and title
        claim_title_style = ParagraphStyle(
            'ClaimTitle',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(f"Claim {i}: {claim.title}", claim_title_style))
        
        # Status badge
        status_colors = {
            'verified': colors.HexColor('#27ae60'),
            'false': colors.HexColor('#e74c3c'),
            'misleading': colors.HexColor('#f39c12'),
            'pending': colors.HexColor('#3498db')
        }
        
        status_data = [[f"Status: {claim.get_status_display()}"]]
        status_table = Table(status_data, colWidths=[2*inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), status_colors.get(claim.status, colors.grey)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(status_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Content
        elements.append(Paragraph("<b>Content:</b>", body_style))
        elements.append(Paragraph(claim.content, body_style))
        
        # Source
        if claim.source_url:
            elements.append(Paragraph(
                f"<b>Source:</b> <link href='{claim.source_url}'>{claim.source_url}</link>",
                body_style
            ))
        
        # Verification notes
        if claim.verification_notes:
            elements.append(Paragraph("<b>Verification Notes:</b>", body_style))
            elements.append(Paragraph(claim.verification_notes, body_style))
        
        # Tags
        if claim.tags:
            elements.append(Paragraph(
                f"<b>Tags:</b> {claim.tags}",
                body_style
            ))
        
        elements.append(Spacer(1, 0.2*inch))
        
        # Add page break after every 3 claims
        if i % 3 == 0 and i < claims.count():
            elements.append(PageBreak())
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(
        "This report was automatically generated by the Credible News Verification System",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create filename
    filename = f"{report.title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Save to model
    report.pdf_file.save(
        filename,
        ContentFile(pdf_data),
        save=True
    )
    
    return report.pdf_file