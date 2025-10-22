#!/usr/bin/env python3
"""
AGGRESSIVE Subdomain Scanner - Flags everything suspicious
Better for bug bounty hunting - you manually verify later
"""

import sys
import subprocess
import socket
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tranco import Tranco
from notification_helper import (
    notify_scan_started,
    notify_scan_complete,
    notify_vulnerability_found,
    notify_error
)

DESKTOP_PATH = Path.home() / "Desktop"
RESULTS_FOLDER = DESKTOP_PATH / "Subdomain_Takeover_Results"
SCANS_FOLDER = RESULTS_FOLDER / "Scans"

# Create folders if they don't exist
for folder in [RESULTS_FOLDER, SCANS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = SCANS_FOLDER / "subdomain_takeover_results.txt"
DETAILED_FILE = SCANS_FOLDER / "subdomain_takeover_detailed.csv"
PROGRESS_FILE = Path("scan_progress.txt")
STATUS_FILE = Path("scan_status.txt")

# ONLY services vulnerable to takeover (based on can-i-take-over-xyz)
# CloudFront, Fastly, etc. are NOT included - they're not vulnerable
TAKEOVER_SERVICES = {
    # AWS S3 - different hosting types
    'aws_s3_website': {
        'patterns': [
            r'\.s3-website[.-]',
            r's3-website[.-]'
        ],
        'vulnerable': True,
        'description': 'AWS S3 Static Website Hosting',
        'difficulty': 'Easy'
    },
    'aws_s3_bucket': {
        'patterns': [
            r'\.s3\.amazonaws\.com',
            r's3-[a-z0-9-]+\.amazonaws\.com',
            r'\.s3\.[a-z0-9-]+\.amazonaws\.com',
            r's3\.[a-z0-9-]+\.amazonaws\.com'
        ],
        'vulnerable': True,
        'description': 'AWS S3 Bucket (Direct)',
        'difficulty': 'Easy'
    },
    'aws_elasticbeanstalk': {
        'patterns': [
            r'\.elasticbeanstalk\.com',
            r'\.eb\.amazonaws\.com'
        ],
        'vulnerable': True,
        'description': 'AWS Elastic Beanstalk',
        'difficulty': 'Easy'
    },
    # Azure - broken down by specific service
    'azure_websites': {
        'patterns': [r'\.azurewebsites\.net'],
        'vulnerable': True,
        'description': 'Azure App Service / Web Apps',
        'difficulty': 'Medium'
    },
    'azure_cloudapp': {
        'patterns': [r'\.cloudapp\.net'],
        'vulnerable': True,
        'description': 'Azure Cloud Services (Classic)',
        'difficulty': 'Medium'
    },
    'azure_cloudapp_new': {
        'patterns': [r'\.cloudapp\.azure\.com'],
        'vulnerable': True,
        'description': 'Azure Cloud Services (ARM)',
        'difficulty': 'Medium'
    },
    'azure_blob': {
        'patterns': [r'\.blob\.core\.windows\.net'],
        'vulnerable': True,
        'description': 'Azure Blob Storage',
        'difficulty': 'Easy'
    },
    'azure_api': {
        'patterns': [r'\.azure-api\.net'],
        'vulnerable': True,
        'description': 'Azure API Management',
        'difficulty': 'Medium'
    },
    'azure_hdinsight': {
        'patterns': [r'\.azurehdinsight\.net'],
        'vulnerable': True,
        'description': 'Azure HDInsight',
        'difficulty': 'Hard'
    },
    'azure_cdn': {
        'patterns': [r'\.azureedge\.net'],
        'vulnerable': True,
        'description': 'Azure CDN',
        'difficulty': 'Medium'
    },
    'azure_container': {
        'patterns': [r'\.azurecontainer\.io'],
        'vulnerable': True,
        'description': 'Azure Container Instances',
        'difficulty': 'Medium'
    },
    'azure_database': {
        'patterns': [r'\.database\.windows\.net'],
        'vulnerable': True,
        'description': 'Azure SQL Database',
        'difficulty': 'Hard'
    },
    'azure_datalake': {
        'patterns': [r'\.azuredatalakestore\.net'],
        'vulnerable': True,
        'description': 'Azure Data Lake Storage',
        'difficulty': 'Hard'
    },
    'azure_search': {
        'patterns': [r'\.search\.windows\.net'],
        'vulnerable': True,
        'description': 'Azure Cognitive Search',
        'difficulty': 'Medium'
    },
    'azure_registry': {
        'patterns': [r'\.azurecr\.io'],
        'vulnerable': True,
        'description': 'Azure Container Registry',
        'difficulty': 'Medium'
    },
    'azure_redis': {
        'patterns': [r'\.redis\.cache\.windows\.net'],
        'vulnerable': True,
        'description': 'Azure Cache for Redis',
        'difficulty': 'Medium'
    },
    'azure_servicebus': {
        'patterns': [r'\.servicebus\.windows\.net'],
        'vulnerable': True,
        'description': 'Azure Service Bus',
        'difficulty': 'Hard'
    },
    'azure_trafficmanager': {
        'patterns': [r'\.trafficmanager\.net'],
        'vulnerable': True,
        'description': 'Azure Traffic Manager',
        'difficulty': 'Medium'
    },
    'azure_devops': {
        'patterns': [r'\.visualstudio\.com'],
        'vulnerable': True,
        'description': 'Azure DevOps / Visual Studio Team Services',
        'difficulty': 'Medium'
    },
    'digitalocean': {
        'patterns': [
            r'\.digitaloceanspaces\.com'
        ],
        'vulnerable': True,
        'description': 'DigitalOcean Spaces',
        'difficulty': 'Easy'
    },
    'heroku': {
        'patterns': [
            r'\.herokuapp\.com'
        ],
        'vulnerable': True,
        'description': 'Heroku',
        'difficulty': 'Easy'
    },
    'github_pages': {
        'patterns': [
            r'\.github\.io'
        ],
        'vulnerable': True,
        'description': 'GitHub Pages',
        'difficulty': 'Easy'
    },
    'shopify': {
        'patterns': [
            r'\.myshopify\.com'
        ],
        'vulnerable': True,
        'description': 'Shopify',
        'difficulty': 'Medium'
    },
    'wordpress': {
        'patterns': [
            r'\.wordpress\.com'
        ],
        'vulnerable': True,
        'description': 'WordPress.com',
        'difficulty': 'Hard'
    },
    'tumblr': {
        'patterns': [
            r'domains\.tumblr\.com'
        ],
        'vulnerable': True,
        'description': 'Tumblr',
        'difficulty': 'Easy'
    },
    'pantheon': {
        'patterns': [
            r'\.pantheonsite\.io'
        ],
        'vulnerable': True,
        'description': 'Pantheon',
        'difficulty': 'Easy'
    },
    'bitbucket': {
        'patterns': [
            r'\.bitbucket\.io'
        ],
        'vulnerable': True,
        'description': 'Bitbucket',
        'difficulty': 'Easy'
    },
    'webflow': {
        'patterns': [
            r'\.webflow\.io'
        ],
        'vulnerable': True,
        'description': 'Webflow',
        'difficulty': 'Easy'
    },
    'cargo': {
        'patterns': [
            r'\.cargocollective\.com'
        ],
        'vulnerable': True,
        'description': 'Cargo Collective',
        'difficulty': 'Easy'
    },
    'statuspage': {
        'patterns': [
            r'\.statuspage\.io'
        ],
        'vulnerable': True,
        'description': 'Statuspage',
        'difficulty': 'Easy'
    },
    'uservoice': {
        'patterns': [
            r'\.uservoice\.com'
        ],
        'vulnerable': True,
        'description': 'UserVoice',
        'difficulty': 'Medium'
    },
    'surge': {
        'patterns': [
            r'\.surge\.sh'
        ],
        'vulnerable': True,
        'description': 'Surge.sh',
        'difficulty': 'Easy'
    }
}

def update_status(status, phase, log_msg=None):
    """Update status."""
    with open(STATUS_FILE, 'a') as f:
        if not STATUS_FILE.exists() or STATUS_FILE.stat().st_size == 0:
            f.write(f"{status}\n{phase}\n")
        if log_msg:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {log_msg}\n")

def update_progress(percent):
    """Update progress."""
    with open(PROGRESS_FILE, 'w') as f:
        f.write(str(int(percent)))

def run_subfinder(domain):
    """Run subfinder."""
    try:
        result = subprocess.run(
            ['subfinder', '-d', domain, '-silent'],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            subs = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            return (domain, subs, True)
        return (domain, [], False)
    except:
        return (domain, [], False)

def get_cname(subdomain, timeout=3):
    """Get CNAME and A records."""
    try:
        # Try CNAME first
        result = subprocess.run(
            ['dig', '+short', '+time=3', '+tries=2', 'CNAME', subdomain],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            cnames = [line.strip().rstrip('.') for line in result.stdout.strip().split('\n')
                     if line.strip() and not line[0].isdigit()]
            if cnames:
                return cnames[0]

        # If no CNAME, try A record (some services use A records)
        result = subprocess.run(
            ['dig', '+short', '+time=3', '+tries=2', 'A', subdomain],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            # Get first IP
            ips = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            if ips:
                # Reverse lookup to see if it points to cloud service
                try:
                    import socket
                    hostname = socket.gethostbyaddr(ips[0])[0]
                    return hostname
                except:
                    pass

        return None
    except:
        return None

def check_vulnerability(subdomain, cname):
    """Check if CNAME matches vulnerable patterns."""
    if not cname:
        return None

    for service, config in TAKEOVER_SERVICES.items():
        for pattern in config['patterns']:
            if re.search(pattern, cname, re.IGNORECASE):
                # Check if it resolves
                try:
                    socket.setdefaulttimeout(2)
                    socket.gethostbyname(subdomain)
                    status = "Active (verify manually)"
                except:
                    status = "⚠️ DANGLING - HIGH PRIORITY!"

                return {
                    'subdomain': subdomain,
                    'service': config['description'],
                    'cname': cname,
                    'status': status,
                    'difficulty': config['difficulty']
                }

    return None

def scan_subdomain(subdomain):
    """Scan subdomain."""
    cname = get_cname(subdomain)
    if cname:
        vuln = check_vulnerability(subdomain, cname)
        # Log ALL CNAMEs for debugging (not just vulnerable ones)
        if not vuln:
            # Save non-vulnerable CNAMEs for analysis
            with open(Path("cname_debug.txt"), 'a') as f:
                f.write(f"{subdomain} -> {cname}\n")
        return vuln
    return None

def matches_extension_filter(subdomain, target_extensions):
    """Check if subdomain matches target extensions."""
    if not target_extensions or target_extensions == ['ALL']:
        return True

    # Parse extensions (handle spaces, commas)
    extensions = [ext.strip().lower() for ext in target_extensions.split(',') if ext.strip()]

    if not extensions:
        return True

    # Check if subdomain ends with any of the target extensions
    subdomain_lower = subdomain.lower()
    for ext in extensions:
        # Add dot if not present
        if not ext.startswith('.'):
            ext = '.' + ext
        if subdomain_lower.endswith(ext):
            return True

    return False

def check_subdominator_available():
    """Check if Subdominator is available."""
    subdominator_paths = [
        Path.home() / 'subdominator',
        Path.home() / 'subdominator-bin' / 'Subdominator',
        Path('subdominator'),
    ]

    for path in subdominator_paths:
        if path.exists() and path.is_file():
            return str(path)

    return None

def run_subdominator(subdomains_file, output_file):
    """Run Subdominator on a list of subdomains."""
    subdominator_path = check_subdominator_available()

    if not subdominator_path:
        return None, "Subdominator not found"

    try:
        # Run Subdominator with validation (no timeout - can take a while for large lists)
        result = subprocess.run(
            [subdominator_path, '-l', str(subdomains_file), '-o', str(output_file),
             '--validate', '-q', '-t', '50'],
            capture_output=True,
            text=True
        )

        # Check if output file has results (Subdominator returns exit code 1 even on success)
        if output_file.exists() and output_file.stat().st_size > 0:
            return output_file, None
        else:
            return None, f"Subdominator failed: {result.stderr if result.stderr else 'No output generated'}"
    except subprocess.TimeoutExpired:
        return None, "Subdominator timed out"
    except Exception as e:
        return None, f"Subdominator error: {str(e)}"

def parse_subdominator_output(output_file):
    """Parse Subdominator output into our format."""
    vulnerabilities = []

    if not output_file or not Path(output_file).exists():
        return vulnerabilities

    # Services that are ACTUALLY vulnerable according to can-i-take-over-xyz
    # https://github.com/EdOverflow/can-i-take-over-xyz
    VULNERABLE_SERVICES = {
        'AWS/S3', 'AWS/Elastic Beanstalk', 'Unbounce', 'Wix', 'Github',
        'Instapage', 'Bitbucket', 'Heroku', 'Tumblr', 'Shopify',
        'Campaign Monitor', 'Cargo Collective', 'Webflow', 'Helpjuice',
        'HelpScout', 'Zendesk', 'Ghost', 'Uptimerobot', 'Pantheon',
        'Gemfury', 'WordPress.com', 'Readme.io', 'Surge.sh', 'Tave',
        'Statuspage', 'UserVoice', 'Netlify', 'SmartJobBoard', 'Intercom',
        'Kinsta', 'LaunchRock', 'Maxcdn', 'Proposify', 'GetResponse',
        'Tilda', 'Brightcove', 'Bigcartel',' Shortio', 'Anima',
        'Microsoft Azure', 'Agile CRM', 'Airee.ru', 'Canny', 'Discourse',
        'Digital Ocean', 'Strikingly'
    }

    try:
        with open(output_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # Subdominator actual format: [Service] subdomain - CNAME: cname
                # Example: [Microsoft Azure] portal.api.ci.eis.idi.principal.com - CNAME: ci-eis-gw.trafficmanager.net.

                # Extract service name from brackets
                service = 'Unknown'
                if line.startswith('['):
                    service_end = line.find(']')
                    if service_end > 0:
                        service = line[1:service_end]
                        line = line[service_end + 1:].strip()

                # FILTER: Only include services that are ACTUALLY vulnerable
                # Skip Fastly, Cloudfront, Akamai, etc. (not vulnerable per can-i-take-over-xyz)
                if service not in VULNERABLE_SERVICES:
                    continue

                # Split subdomain and CNAME
                subdomain = ''
                cname = ''

                if ' - CNAME: ' in line:
                    parts = line.split(' - CNAME: ')
                    subdomain = parts[0].strip()
                    cname = parts[1].strip().rstrip('.')
                elif ' - A: ' in line:
                    # Handle A record format
                    parts = line.split(' - A: ')
                    subdomain = parts[0].strip()
                    cname = parts[1].strip()  # IP addresses
                else:
                    # Fallback - just get subdomain
                    subdomain = line.split()[0] if line.split() else line

                if subdomain:
                    vuln = {
                        'subdomain': subdomain,
                        'service': service,
                        'cname': cname,
                        'status': '⚠️ DANGLING - HIGH PRIORITY!',  # Subdominator already validates
                        'difficulty': 'Easy'
                    }
                    vulnerabilities.append(vuln)
    except Exception as e:
        print(f"Error parsing Subdominator output: {e}")

    return vulnerabilities

def main():
    """Main scanner."""
    if len(sys.argv) < 3:
        print("Usage: aggressive_scanner.py <start_rank> <num_domains> [extensions] [enum_workers] [scan_workers]")
        sys.exit(1)

    start_rank = int(sys.argv[1])
    num_domains = int(sys.argv[2])
    target_extensions = sys.argv[3] if len(sys.argv) > 3 else 'ALL'
    enum_workers = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    scan_workers = int(sys.argv[5]) if len(sys.argv) > 5 else 30

    try:
        # Clean old files
        for f in [OUTPUT_FILE, DETAILED_FILE, PROGRESS_FILE, STATUS_FILE]:
            if f.exists():
                f.unlink()

        update_status("Initializing...", "Starting", "🚀 Starting aggressive scan")
        update_progress(0)

        # Notify scan started
        notify_scan_started(f"{num_domains} domains", mode="aggressive")

        # Fetch domains
        update_status("Downloading...", "Fetching Domains", "Connecting to Tranco")
        update_progress(5)

        t = Tranco(cache=True, cache_dir='.tranco')
        latest_list = t.list()
        # Fetch domains starting from start_rank (1-indexed in Tranco)
        all_ranked = latest_list.top(start_rank + num_domains)
        # Tranco list is 0-indexed, so start_rank 5000 means index 4999
        domains = all_ranked[start_rank - 1:start_rank - 1 + num_domains]

        update_status(f"Got {len(domains)} domains", "Fetching Complete",
                     f"✓ Fetched {len(domains)} domains from rank {start_rank:,}")

        update_progress(10)

        # Phase 1: Enumeration
        update_status("Running subfinder...", "Phase 1: Enumeration", "Starting subdomain discovery")
        update_progress(15)

        all_subdomains = []
        completed = 0

        update_status("Enumerating...", "Phase 1: Enumeration", f"Processing with {enum_workers} parallel workers")

        with ThreadPoolExecutor(max_workers=enum_workers) as executor:
            futures = {executor.submit(run_subfinder, d): d for d in domains}

            for future in as_completed(futures):
                domain, subs, success = future.result()
                completed += 1

                if subs:
                    all_subdomains.extend(subs)
                    update_status(
                        f"Found {len(all_subdomains)} subs",
                        "Phase 1: Enumeration",
                        f"{domain}: {len(subs)} subdomains (total: {len(all_subdomains)})"
                    )

                progress = 15 + int((completed / len(domains)) * 35)
                update_progress(progress)

        update_status(f"Found {len(all_subdomains)} total", "Phase 1: Complete",
                     f"✓ Discovered {len(all_subdomains)} subdomains total")
        update_progress(50)

        if not all_subdomains:
            update_status("No subdomains found", "Complete", "No subdomains discovered")
            update_progress(100)
            return

        # Phase 2: Apply extension filter to subdomains
        if target_extensions and target_extensions != 'ALL':
            update_status("Filtering extensions...", "Phase 2: Filtering", f"Applying extension filter: {target_extensions}")
            filtered_subdomains = [s for s in all_subdomains if matches_extension_filter(s, target_extensions)]
            update_status(f"Filtered to {len(filtered_subdomains)}", "Phase 2: Filtering",
                         f"✓ {len(filtered_subdomains)} subdomains match filter (from {len(all_subdomains)})")
            all_subdomains = filtered_subdomains

        # Phase 3: Vulnerability Scanning
        vulnerabilities = []

        # Check if Subdominator is available
        subdominator_path = check_subdominator_available()

        if subdominator_path:
            # Use Subdominator (FAST + ACCURATE)
            update_status("Using Subdominator...", "Phase 3: Scanning", f"🚀 Running Subdominator on {len(all_subdomains)} subdomains")
            update_progress(55)

            # Write subdomains to temp file
            subdomains_file = Path("temp_subdomains.txt")
            with open(subdomains_file, 'w') as f:
                for subdomain in all_subdomains:
                    f.write(f"{subdomain}\n")

            # Run Subdominator
            output_file = Path("subdominator_output.txt")
            result_file, error = run_subdominator(subdomains_file, output_file)

            if result_file:
                update_status("Parsing results...", "Phase 3: Scanning", "✓ Subdominator scan complete")
                update_progress(90)

                vulnerabilities = parse_subdominator_output(result_file)

                update_status(
                    f"Found {len(vulnerabilities)} vulns",
                    "Phase 3: Complete",
                    f"✓ Subdominator found {len(vulnerabilities)} vulnerabilities"
                )

                # Cleanup temp files
                if subdomains_file.exists():
                    subdomains_file.unlink()
            else:
                update_status("Subdominator failed", "Phase 3: Scanning", f"⚠️ {error} - falling back to Python scanner")
                subdominator_path = None  # Fall back to Python method

        if not subdominator_path:
            # Fall back to Python + dig method (SLOWER but works)
            update_status("Using Python scanner...", "Phase 3: Scanning", f"Checking {len(all_subdomains)} subdomains with {scan_workers} workers")
            update_progress(55)

            scanned = 0

            with ThreadPoolExecutor(max_workers=scan_workers) as executor:
                futures = {executor.submit(scan_subdomain, s): s for s in all_subdomains}

                for future in as_completed(futures):
                    result = future.result()
                    scanned += 1

                    if result:
                        vulnerabilities.append(result)
                        update_status(
                            f"{len(vulnerabilities)} vulns found",
                            "Phase 3: Scanning",
                            f"🚨 {result['subdomain']} → {result['service']} ({result['status']})"
                        )

                    if scanned % 50 == 0:
                        update_status(
                            f"Scanned {scanned}/{len(all_subdomains)}",
                            "Phase 3: Scanning",
                            f"Progress: {scanned}/{len(all_subdomains)} ({len(vulnerabilities)} potential vulns)"
                        )

                    progress = 55 + int((scanned / len(all_subdomains)) * 40)
                    update_progress(progress)

        # Save results
        update_status("Saving...", "Saving", f"Writing {len(vulnerabilities)} findings to Desktop")
        update_progress(95)

        if vulnerabilities:
            # Save text file
            with open(OUTPUT_FILE, 'w') as f:
                f.write(f"Subdomain Takeover - Potential Vulnerabilities\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Found: {len(vulnerabilities)}\n")
                f.write(f"\n⚠️  NOTE: These are POTENTIAL vulns - verify manually!\n")
                f.write("="*80 + "\n\n")

                # Group by priority
                dangling = [v for v in vulnerabilities if 'DANGLING' in v['status']]
                active = [v for v in vulnerabilities if 'DANGLING' not in v['status']]

                if dangling:
                    f.write(f"🚨 HIGH PRIORITY - DANGLING DNS ({len(dangling)}):\n")
                    f.write("-"*80 + "\n")
                    for vuln in dangling:
                        f.write(f"\n{vuln['subdomain']}\n")
                        f.write(f"  Service: {vuln['service']}\n")
                        f.write(f"  CNAME: {vuln['cname']}\n")
                        f.write(f"  Status: {vuln['status']}\n")

                if active:
                    f.write(f"\n\n📋 CHECK MANUALLY - Active CNAMEs ({len(active)}):\n")
                    f.write("-"*80 + "\n")
                    for vuln in active:
                        f.write(f"\n{vuln['subdomain']}\n")
                        f.write(f"  Service: {vuln['service']}\n")
                        f.write(f"  CNAME: {vuln['cname']}\n")
                        f.write(f"  Status: {vuln['status']}\n")

            # Save CSV
            import csv
            with open(DETAILED_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['subdomain', 'service', 'cname', 'status', 'difficulty'])
                writer.writeheader()
                writer.writerows(vulnerabilities)

            update_status(
                f"✓ Complete! {len(vulnerabilities)} findings",
                "Complete",
                f"✓ Saved {len(dangling)} high-priority + {len(active)} to check"
            )

            # Notify scan complete
            notify_scan_complete(len(vulnerabilities), len(all_subdomains))
        else:
            update_status("No vulnerabilities found", "Complete", "No takeover candidates found")

            # Notify no results
            notify_scan_complete(0, len(all_subdomains))

        update_progress(100)

        # Keep status visible
        import time
        time.sleep(10)
        PROGRESS_FILE.unlink()

    except Exception as e:
        update_status(f"Error: {str(e)}", "Error", f"❌ ERROR: {str(e)}")
        notify_error(f"Scan failed: {str(e)[:80]}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
