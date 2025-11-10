#!/usr/bin/env python3
"""
Automated Nightly Bug Bounty Scanner
Runs every night at 2-3 AM, ready by 8-9 AM

Usage:
    python automated_nightly_scanner.py

Schedule with cron:
    0 2 * * * cd /Users/nishchalasri && /Users/nishchalasri/venv/bin/python automated_nightly_scanner.py
"""

import subprocess
import csv
import time
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp
import aiodns
from concurrent.futures import ThreadPoolExecutor
import json

# Configuration
RESULTS_FOLDER = Path.home() / "Desktop" / "Subdomain_Takeover_Results"
NIGHTLY_FOLDER = RESULTS_FOLDER / "Nightly_Scans"
NIGHTLY_FOLDER.mkdir(parents=True, exist_ok=True)

# Bug bounty programs to scan
BUG_BOUNTY_DOMAINS = Path.home() / "bug_bounty_domains.txt"

# Today's output files
TODAY = datetime.now().strftime('%Y-%m-%d')
TODAY_FOLDER = NIGHTLY_FOLDER / TODAY
TODAY_FOLDER.mkdir(exist_ok=True)

SCAN_OUTPUT = TODAY_FOLDER / f"scan_results_{TODAY}.csv"
VERIFIED_OUTPUT = TODAY_FOLDER / f"verified_vulnerabilities_{TODAY}.csv"
SUMMARY_OUTPUT = TODAY_FOLDER / f"summary_{TODAY}.txt"

# Common subdomain patterns
SUBDOMAIN_PATTERNS = [
    'www', 'mail', 'ftp', 'smtp', 'pop', 'webmail',
    'test', 'staging', 'dev', 'qa', 'prod', 'demo',
    'old', 'legacy', 'backup', 'archive', 'beta', 'alpha',
    'api', 'api-v1', 'api-v2', 'api-staging', 'api-prod',
    'app', 'mobile', 'web', 'cdn', 'static', 'assets',
    'm', 'blog', 'shop', 'store', 'admin', 'portal',
    'docs', 'help', 'support', 'status', 'monitor',
    'jenkins', 'ci', 'build', 'deploy', 'release',
    'sandbox', 'lab', 'research', 'internal', 'vpn',
    # Add more based on your findings
]

# Cloud service patterns to check for takeovers
TAKEOVER_PATTERNS = {
    'AWS S3': ['.s3.amazonaws.com', '.s3-website'],
    'AWS Elastic Beanstalk': ['.elasticbeanstalk.com'],
    'Azure App Service': ['.azurewebsites.net'],
    'Azure Blob Storage': ['.blob.core.windows.net'],
    'Azure CDN': ['.azureedge.net'],
    'Azure Cloud Services': ['.cloudapp.net', '.cloudapp.azure.com'],
    'Azure Container Instances': ['.azurecontainer.io'],
    'GitHub Pages': ['.github.io'],
    'Heroku': ['.herokuapp.com'],
    'Shopify': ['.myshopify.com'],
    'Tumblr': ['.tumblr.com'],
    'WordPress': ['.wordpress.com'],
}


class NightlyScanner:
    def __init__(self):
        self.found_subdomains = []
        self.potential_takeovers = []
        self.verified_vulns = []

    async def check_subdomain(self, subdomain, domain, session, resolver):
        """Check if subdomain exists and has CNAME pointing to vulnerable service"""
        full_domain = f"{subdomain}.{domain}"

        try:
            # DNS lookup for CNAME
            result = await resolver.query(full_domain, 'CNAME')
            cname = str(result.cname)

            # Check if CNAME matches takeover patterns
            for service, patterns in TAKEOVER_PATTERNS.items():
                for pattern in patterns:
                    if pattern in cname.lower():
                        self.potential_takeovers.append({
                            'subdomain': full_domain,
                            'cname': cname,
                            'service': service,
                            'found_at': datetime.now().isoformat()
                        })
                        print(f"  🎯 Potential takeover: {full_domain} → {cname}")
                        return

        except aiodns.error.DNSError:
            # No CNAME or doesn't exist
            pass
        except Exception as e:
            pass

    async def scan_domain(self, domain):
        """Scan all subdomains of a single domain"""
        print(f"\n🔍 Scanning: {domain}")

        resolver = aiodns.DNSResolver(timeout=5)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            tasks = []

            for subdomain in SUBDOMAIN_PATTERNS:
                task = self.check_subdomain(subdomain, domain, session, resolver)
                tasks.append(task)

            # Run all subdomain checks concurrently
            await asyncio.gather(*tasks, return_exceptions=True)

    async def scan_all_domains(self, domains):
        """Scan all bug bounty domains"""
        print(f"\n{'='*80}")
        print(f"🌙 NIGHTLY SCAN STARTED")
        print(f"📅 Date: {TODAY}")
        print(f"🎯 Target domains: {len(domains)}")
        print(f"🔍 Subdomain patterns: {len(SUBDOMAIN_PATTERNS)}")
        print(f"📊 Total checks: {len(domains) * len(SUBDOMAIN_PATTERNS):,}")
        print(f"{'='*80}")

        start_time = time.time()

        # Scan all domains
        for domain in domains:
            await self.scan_domain(domain)

        elapsed = time.time() - start_time

        print(f"\n{'='*80}")
        print(f"✅ SCANNING COMPLETE")
        print(f"⏱️  Time: {elapsed/60:.1f} minutes")
        print(f"🎯 Potential takeovers found: {len(self.potential_takeovers)}")
        print(f"{'='*80}")

    def save_scan_results(self):
        """Save scan results to CSV"""
        if not self.potential_takeovers:
            print("\n❌ No potential takeovers found")
            return

        with open(SCAN_OUTPUT, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['subdomain', 'cname', 'service', 'found_at'])
            writer.writeheader()
            writer.writerows(self.potential_takeovers)

        print(f"\n💾 Scan results saved: {SCAN_OUTPUT}")

    def verify_vulnerabilities(self):
        """Deep verification: Check if CNAME target exists (dangling DNS)"""
        print(f"\n{'='*80}")
        print(f"🔬 DEEP VERIFICATION STARTED")
        print(f"📊 Checking {len(self.potential_takeovers)} potential takeovers...")
        print(f"⏱️  This may take 1-2 hours...")
        print(f"{'='*80}")

        import requests
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def verify_single(vuln):
            """Verify a single vulnerability"""
            try:
                subdomain = vuln['subdomain']
                cname = vuln['cname']
                service = vuln['service']

                # Check if the CNAME target exists
                is_vulnerable, evidence = self.check_if_vulnerable(cname, service)

                if is_vulnerable:
                    vuln['vulnerable'] = True
                    vuln['verified_at'] = datetime.now().isoformat()
                    vuln['evidence'] = evidence
                    print(f"   ✅ VULNERABLE: {subdomain}")
                    return vuln
                else:
                    print(f"   ❌ Active: {subdomain}")
                    return None

            except Exception as e:
                print(f"   ⚠️  Error checking {vuln['subdomain']}: {e}")
                return None

        # Verify in parallel (50 threads)
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(verify_single, vuln): vuln for vuln in self.potential_takeovers}

            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.verified_vulns.append(result)

        print(f"\n{'='*80}")
        print(f"✅ DEEP VERIFICATION COMPLETE")
        print(f"🎉 High-confidence vulnerabilities: {len(self.verified_vulns)}")
        print(f"📋 Total potential takeovers: {len(self.potential_takeovers)}")
        print(f"{'='*80}")

    def check_if_vulnerable(self, cname, service):
        """
        Check if the CNAME target actually exists (dangling DNS)
        Returns: (is_vulnerable: bool, evidence: str)
        """
        import requests

        try:
            # S3 Bucket checks
            if 's3.amazonaws.com' in cname or 's3-website' in cname:
                try:
                    response = requests.get(f"http://{cname}", timeout=10)

                    if response.status_code == 404 and 'NoSuchBucket' in response.text:
                        return True, "S3 bucket does not exist (NoSuchBucket)"
                    elif response.status_code == 403 and 'AccessDenied' in response.text:
                        return False, "S3 bucket exists but is private"
                except:
                    pass

            # Azure App Service
            elif 'azurewebsites.net' in cname:
                try:
                    response = requests.get(f"https://{cname}", timeout=10)

                    if response.status_code == 404:
                        if 'Web App - Unavailable' in response.text or 'Error 404' in response.text:
                            return True, "Azure App Service does not exist"
                except:
                    pass

            # AWS Elastic Beanstalk
            elif 'elasticbeanstalk.com' in cname:
                try:
                    response = requests.get(f"http://{cname}", timeout=10)

                    if response.status_code == 404:
                        return True, "Elastic Beanstalk environment does not exist"
                except requests.exceptions.ConnectionError:
                    return True, "Elastic Beanstalk CNAME does not resolve"
                except:
                    pass

            # Azure Traffic Manager
            elif 'trafficmanager.net' in cname:
                try:
                    response = requests.get(f"http://{cname}", timeout=10)

                    if response.status_code == 404:
                        return True, "Traffic Manager endpoint does not exist"
                except requests.exceptions.ConnectionError:
                    return True, "Traffic Manager CNAME does not resolve (DANGLING)"
                except:
                    pass

            # Azure Cloud Services
            elif 'cloudapp.net' in cname or 'cloudapp.azure.com' in cname:
                try:
                    response = requests.get(f"http://{cname}", timeout=10)

                    if response.status_code == 404:
                        return True, "Azure Cloud Service does not exist"
                except requests.exceptions.ConnectionError:
                    return True, "Cloud Service CNAME does not resolve (DANGLING)"
                except:
                    pass

            # GitHub Pages
            elif 'github.io' in cname:
                try:
                    response = requests.get(f"https://{cname}", timeout=10)

                    if response.status_code == 404:
                        if 'There isn\'t a GitHub Pages site here' in response.text:
                            return True, "GitHub Pages site does not exist"
                except:
                    pass

            # Heroku
            elif 'herokuapp.com' in cname:
                try:
                    response = requests.get(f"https://{cname}", timeout=10)

                    if 'no such app' in response.text.lower():
                        return True, "Heroku app does not exist"
                except:
                    pass

            # Azure Container Instances
            elif 'azurecontainer.io' in cname:
                try:
                    response = requests.get(f"http://{cname}", timeout=10)
                except requests.exceptions.ConnectionError:
                    return True, "Azure Container Instance does not resolve (DANGLING)"
                except:
                    pass

            # Generic check for connection errors (likely dangling)
            try:
                response = requests.get(f"http://{cname}", timeout=10)
            except requests.exceptions.ConnectionError:
                return True, "CNAME does not resolve - likely dangling DNS"
            except:
                pass

        except Exception as e:
            return False, f"Error checking: {str(e)}"

        return False, "Resource appears to be active"

    def save_results_multi_sheet(self):
        """Save results to CSV with multiple sheets using pandas"""
        import pandas as pd

        # Prepare high-confidence vulnerabilities
        high_confidence = []
        for vuln in self.verified_vulns:
            high_confidence.append({
                'Subdomain': vuln['subdomain'],
                'CNAME': vuln['cname'],
                'Service': vuln['service'],
                'Status': '🚨 DANGLING - HIGH PRIORITY',
                'Verified': vuln.get('verified_at', ''),
                'Evidence': vuln.get('evidence', 'Resource does not exist')
            })

        # Prepare all potential takeovers
        all_potential = []
        for vuln in self.potential_takeovers:
            all_potential.append({
                'Subdomain': vuln['subdomain'],
                'CNAME': vuln['cname'],
                'Service': vuln['service'],
                'Status': 'Active (verify manually)',
                'Found At': vuln.get('found_at', ''),
                'Notes': 'Requires manual verification'
            })

        # Create Excel file with multiple sheets
        excel_output = TODAY_FOLDER / f"scan_results_{TODAY}.xlsx"

        with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
            # Sheet 1: High-confidence vulnerabilities
            if high_confidence:
                df_high = pd.DataFrame(high_confidence)
                df_high.to_excel(writer, sheet_name='High_Priority_Vulns', index=False)

            # Sheet 2: All potential takeovers
            if all_potential:
                df_all = pd.DataFrame(all_potential)
                df_all.to_excel(writer, sheet_name='All_Potential_Takeovers', index=False)

        print(f"\n💾 Results saved to Excel: {excel_output}")
        print(f"   📋 Sheet 1: High Priority ({len(high_confidence)} verified)")
        print(f"   📋 Sheet 2: All Potential ({len(all_potential)} total)")

        # Also save simple CSV for compatibility
        if self.verified_vulns:
            with open(VERIFIED_OUTPUT, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'subdomain', 'cname', 'service', 'status', 'verified_at'
                ])
                writer.writeheader()
                for vuln in self.verified_vulns:
                    writer.writerow({
                        'subdomain': vuln['subdomain'],
                        'cname': vuln['cname'],
                        'service': vuln['service'],
                        'status': 'DANGLING',
                        'verified_at': vuln.get('verified_at', '')
                    })

        print(f"   📄 CSV backup: {VERIFIED_OUTPUT}")

    def generate_summary(self):
        """Generate human-readable summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║          NIGHTLY SCAN SUMMARY - {TODAY}                ║
╚══════════════════════════════════════════════════════════════╝

📊 STATISTICS:
├── Domains scanned: {len(self.found_subdomains) if hasattr(self, 'domains_scanned') else 'N/A'}
├── Potential takeovers found: {len(self.potential_takeovers)}
├── Verified vulnerabilities: {len(self.verified_vulns)}
└── Success rate: {len(self.verified_vulns)/max(len(self.potential_takeovers), 1)*100:.1f}%

🎯 VERIFIED VULNERABILITIES:

"""

        if self.verified_vulns:
            # Group by service
            by_service = {}
            for vuln in self.verified_vulns:
                service = vuln['service']
                if service not in by_service:
                    by_service[service] = []
                by_service[service].append(vuln)

            for service, vulns in by_service.items():
                summary += f"\n{service}: {len(vulns)}\n"
                for vuln in vulns:
                    summary += f"  • {vuln['subdomain']}\n"
                    summary += f"    CNAME: {vuln['cname']}\n"
        else:
            summary += "No verified vulnerabilities found.\n"

        summary += f"""
{'='*80}

📁 FILES GENERATED:
├── Scan results: {SCAN_OUTPUT.name}
├── Verified vulns: {VERIFIED_OUTPUT.name}
└── This summary: {SUMMARY_OUTPUT.name}

💡 NEXT STEPS:
1. Review verified vulnerabilities in CSV
2. Run: python automated_deployer.py (deploys 100/day)
3. Generate bug bounty reports
4. Submit to HackerOne/Bugcrowd

🎉 Scan complete! Ready for bug bounty submissions.
"""

        # Save summary
        with open(SUMMARY_OUTPUT, 'w') as f:
            f.write(summary)

        print(summary)

        # Send notification
        try:
            from notification_helper import send_notification
            send_notification(
                title="🌙 Nightly Scan Complete",
                message=f"Found {len(self.verified_vulns)} verified vulnerabilities",
                sound=True
            )
        except:
            pass


def load_bug_bounty_domains():
    """Load list of bug bounty domains to scan"""

    # Create default list if doesn't exist
    if not BUG_BOUNTY_DOMAINS.exists():
        default_domains = """# Bug Bounty Programs to Scan
# Add one domain per line
# Updated: {date}

# HackerOne Programs
shopify.com
uber.com
gitlab.com
rockstarconsultancy.com
mail.ru
yelp.com
twitter.com
github.com
reddit.com
slack.com

# Bugcrowd Programs
tesla.com
fitbit.com
square.com
pinterest.com
motorola.com

# Universities (.edu domains are gold!)
mit.edu
stanford.edu
harvard.edu
umich.edu
berkeley.edu
cornell.edu
columbia.edu
yale.edu
princeton.edu
upenn.edu

# Add more domains here...
""".format(date=TODAY)

        with open(BUG_BOUNTY_DOMAINS, 'w') as f:
            f.write(default_domains)

        print(f"📝 Created default domains list: {BUG_BOUNTY_DOMAINS}")
        print(f"💡 Edit this file to add more bug bounty programs!")

    # Read domains
    domains = []
    with open(BUG_BOUNTY_DOMAINS) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                domains.append(line)

    return domains


async def main():
    """Main nightly scan workflow"""

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     AUTOMATED NIGHTLY BUG BOUNTY SCANNER                     ║
╚══════════════════════════════════════════════════════════════╝

⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📁 Output folder: {TODAY_FOLDER}
""")

    # Load domains to scan
    domains = load_bug_bounty_domains()

    if not domains:
        print("❌ No domains to scan! Add domains to bug_bounty_domains.txt")
        return

    # Initialize scanner
    scanner = NightlyScanner()

    # Step 1: Scan all domains (2-3 hours)
    await scanner.scan_all_domains(domains)

    # Step 2: Save scan results
    scanner.save_scan_results()

    # Step 3: Auto-run deep verification (1-2 hours)
    print(f"\n🔬 Starting automatic deep verification...")
    scanner.verify_vulnerabilities()

    # Step 4: Save results to multi-sheet Excel
    scanner.save_results_multi_sheet()

    # Step 5: Generate summary
    scanner.generate_summary()

    print(f"\n⏰ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🎉 DONE! Check {TODAY_FOLDER} for results")


if __name__ == "__main__":
    asyncio.run(main())
