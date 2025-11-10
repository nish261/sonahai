#!/usr/bin/env python3
"""
Generate PDF Proof-of-Concept files for subdomain takeover
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

def generate_poc_pdf(subdomain, service_type, details, researcher_name, output_file):
    """
    Generate a professional PDF PoC

    Args:
        subdomain: The vulnerable subdomain (e.g., old-app.company.com)
        service_type: Service type (e.g., AWS S3, Azure, GitHub Pages)
        details: Dict with additional details (bucket_name, region, etc.)
        researcher_name: Bug bounty researcher name
        output_file: Output PDF filename
    """

    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#d9534f'),
        spaceAfter=30,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#333333'),
        spaceAfter=12,
    )

    # Title
    title = Paragraph("🔒 Subdomain Takeover - Proof of Concept", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))

    # Vulnerability Details Section
    story.append(Paragraph("Vulnerability Details", heading_style))

    details_data = [
        ['Vulnerable Subdomain:', subdomain],
        ['Service Type:', service_type],
        ['Discovered Date:', datetime.now().strftime('%Y-%m-%d')],
        ['Researcher:', researcher_name],
    ]

    # Add service-specific details
    if details.get('bucket_name'):
        details_data.append(['Bucket Name:', details['bucket_name']])
    if details.get('region'):
        details_data.append(['Region:', details['region']])
    if details.get('app_name'):
        details_data.append(['App Name:', details['app_name']])
    if details.get('cname'):
        details_data.append(['CNAME Record:', details['cname']])

    details_table = Table(details_data, colWidths=[2*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fff3cd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))

    # What is Subdomain Takeover Section
    story.append(Paragraph("What is Subdomain Takeover?", heading_style))

    explanation = """
    This subdomain was pointing to a non-existent cloud resource (e.g., S3 bucket, Azure app,
    GitHub Pages site). An attacker could have claimed this resource and hosted malicious content,
    enabling phishing attacks, brand impersonation, or malware distribution.

    By claiming the resource and hosting this proof-of-concept, I have demonstrated that:
    1. The subdomain DNS record points to an unclaimed resource
    2. Anyone can claim this resource and control the content
    3. The subdomain appears to be part of your legitimate infrastructure
    """

    story.append(Paragraph(explanation, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Proof of Concept Section
    story.append(Paragraph("Proof of Concept", heading_style))

    poc_text = """
    This PDF document serves as proof that I have successfully claimed the vulnerable subdomain.
    <b>No malicious actions have been taken.</b> The resource has been secured temporarily to prevent
    exploitation by malicious actors.
    """

    story.append(Paragraph(poc_text, styles['BodyText']))
    story.append(Spacer(1, 0.2*inch))

    # Impact Section
    story.append(Paragraph("Security Impact", heading_style))

    impact_data = [
        ['Risk Level:', 'HIGH'],
        ['CVSS Score:', '7.5 - 8.5'],
        ['Attack Vector:', 'Network'],
        ['Privileges Required:', 'None'],
    ]

    impact_table = Table(impact_data, colWidths=[2*inch, 4*inch])
    impact_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8d7da')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))

    story.append(impact_table)
    story.append(Spacer(1, 0.3*inch))

    # Recommended Fix Section
    story.append(Paragraph("Recommended Remediation", heading_style))

    remediation_text = """
    <b>Immediate Actions:</b><br/>
    1. Remove the DNS CNAME record pointing to the unclaimed resource<br/>
    2. If the resource is still needed, reclaim it in your cloud provider console<br/>
    3. Implement monitoring for dangling DNS records<br/>
    <br/>
    <b>Long-term Prevention:</b><br/>
    • Maintain an inventory of all subdomains and their associated resources<br/>
    • Automate DNS record cleanup when resources are decommissioned<br/>
    • Use cloud provider tools (e.g., AWS Config) to detect dangling CNAMEs<br/>
    • Implement subdomain monitoring and alerting<br/>
    """

    story.append(Paragraph(remediation_text, styles['BodyText']))
    story.append(Spacer(1, 0.3*inch))

    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,  # Center
    )

    footer_text = """
    This is a responsible security disclosure for bug bounty purposes only.<br/>
    Contact: {}<br/>
    Date: {}
    """.format(researcher_name, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    story.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated: {output_file}")


if __name__ == "__main__":
    # Example usage
    generate_poc_pdf(
        subdomain="old-app.company.com",
        service_type="AWS S3 Bucket",
        details={
            'bucket_name': 'old-app',
            'region': 'us-east-1',
            'cname': 'old-app.s3.amazonaws.com'
        },
        researcher_name="researcher123",
        output_file="proof-of-concept.pdf"
    )
