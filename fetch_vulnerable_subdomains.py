#!/usr/bin/env python3
"""
Subdomain Takeover Vulnerability Scanner
Targets lower-ranked domains for bug bounty hunting.
"""

import sys
import os
import subprocess
import socket
import re
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from tranco import Tranco
except ImportError:
    print("Error: tranco package not installed.")
    sys.exit(1)

write_lock = threading.Lock()

# Vulnerability signatures
VULNERABILITY_PATTERNS = {
    's3_takeover': {
        'cname_patterns': [r'\.s3\.amazonaws\.com$', r'\.s3-website'],
        'error_signatures': [
            'NoSuchBucket',
            'The specified bucket does not exist',
            'Code: NoSuchBucket'
        ],
        'description': 'S3 Bucket Takeover'
    },
    'elasticbeanstalk_takeover': {
        'cname_patterns': [r'\.elasticbeanstalk\.com$'],
        'error_signatures': [
            'does not exist',
            'ERROR: The specified environment does not exist'
        ],
        'description': 'Elastic Beanstalk Takeover'
    },
    'digitalocean_takeover': {
        'cname_patterns': [r'\.ondigitalocean\.app$'],
        'error_signatures': [
            'Domain not found',
            'There isn\'t a GitHub Pages site here'
        ],
        'description': 'DigitalOcean App Takeover'
    }
}


def get_dns_records(subdomain, timeout=3):
    """Get DNS CNAME records."""
    result = {'cnames': [], 'ips': []}

    try:
        dig_result = subprocess.run(
            ['dig', '+short', 'CNAME', subdomain],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if dig_result.returncode == 0 and dig_result.stdout.strip():
            cnames = [line.strip().rstrip('.') for line in dig_result.stdout.strip().split('\n') if line.strip()]
            result['cnames'] = cnames

        try:
            socket.setdefaulttimeout(timeout)
            ips = socket.gethostbyname_ex(subdomain)[2]
            result['ips'] = ips
        except:
            pass

    except:
        pass

    return result


def check_http_response(subdomain, timeout=5):
    """Check HTTP response for takeover signatures."""
    errors = []

    for protocol in ['https', 'http']:
        try:
            url = f"{protocol}://{subdomain}"
            response = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)

            # Check for error signatures
            for vuln_type, patterns in VULNERABILITY_PATTERNS.items():
                if 'error_signatures' in patterns:
                    for signature in patterns['error_signatures']:
                        if signature.lower() in response.text.lower():
                            errors.append({
                                'type': vuln_type,
                                'signature': signature,
                                'status_code': response.status_code,
                                'url': url
                            })

        except requests.exceptions.SSLError:
            # SSL errors can indicate abandoned resources
            continue
        except requests.exceptions.ConnectionError:
            # Connection errors might indicate takeover potential
            continue
        except:
            continue

    return errors


def check_takeover_vulnerability(subdomain, dns_records):
    """Check if subdomain is vulnerable to takeover."""
    vulnerabilities = []

    # Check CNAME patterns
    for cname in dns_records['cnames']:
        for vuln_type, patterns in VULNERABILITY_PATTERNS.items():
            if 'cname_patterns' in patterns:
                for pattern in patterns['cname_patterns']:
                    if re.search(pattern, cname, re.IGNORECASE):
                        # Found matching CNAME, now check if resource exists
                        http_errors = check_http_response(subdomain)

                        if http_errors:
                            vulnerabilities.append({
                                'subdomain': subdomain,
                                'type': vuln_type,
                                'cname': cname,
                                'errors': http_errors,
                                'description': patterns['description']
                            })
                        elif not dns_records['ips']:
                            # CNAME exists but no IP resolution = potential takeover
                            vulnerabilities.append({
                                'subdomain': subdomain,
                                'type': vuln_type,
                                'cname': cname,
                                'errors': [{'type': 'dns_orphan', 'signature': 'No IP resolution'}],
                                'description': f"{patterns['description']} (DNS Orphan)"
                            })

    return vulnerabilities


def scan_subdomain(subdomain):
    """Scan a single subdomain for takeover vulnerabilities."""
    dns_records = get_dns_records(subdomain)

    if not dns_records['cnames']:
        return None

    vulns = check_takeover_vulnerability(subdomain, dns_records)
    return (subdomain, vulns) if vulns else None


def enumerate_and_scan(domains, country_code, max_workers=10, scan_workers=20):
    """Enumerate subdomains and scan for takeover vulnerabilities."""

    print(f"\n{'='*60}")
    print("PHASE 1: Subdomain Enumeration")
    print(f"{'='*60}")
    print(f"Targeting {len(domains)} lower-ranked domains for better vuln rates...")
    print(f"Running with {max_workers} parallel workers")
    print("-" * 60)

    all_subdomains = []
    completed = 0

    # Enumerate subdomains
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for domain in domains:
            future = executor.submit(run_subfinder, domain)
            futures[future] = domain

        for future in as_completed(futures):
            domain, subdomains, success = future.result()
            completed += 1

            if success and subdomains:
                # Filter for interesting patterns (dev, staging, test, old, etc.)
                interesting = [s for s in subdomains if any(keyword in s.lower()
                    for keyword in ['dev', 'staging', 'test', 'old', 'legacy', 'beta',
                                   'demo', 'temp', 'backup', 'archive', 'deprecated'])]

                all_subdomains.extend(subdomains)

                if interesting:
                    print(f"[{completed}/{len(domains)}] {domain}: {len(subdomains)} total ({len(interesting)} interesting)")
                else:
                    print(f"[{completed}/{len(domains)}] {domain}: {len(subdomains)} subdomains")
            else:
                print(f"[{completed}/{len(domains)}] {domain}: FAILED")

    print("-" * 60)
    print(f"\n✓ Found {len(all_subdomains)} total subdomains")

    if not all_subdomains:
        print("No subdomains found.")
        return

    # Save all subdomains
    all_file = f"subdomains_all_{country_code}.txt"
    with open(all_file, 'w') as f:
        for sub in all_subdomains:
            f.write(f"{sub}\n")
    print(f"Saved to: {all_file}")

    # Phase 2: Scan for vulnerabilities
    print(f"\n{'='*60}")
    print("PHASE 2: Vulnerability Scanning")
    print(f"{'='*60}")
    print(f"Scanning {len(all_subdomains)} subdomains for takeover vulnerabilities...")
    print(f"Running with {scan_workers} parallel workers")
    print("-" * 60)

    vulnerabilities = []
    scanned = 0

    with ThreadPoolExecutor(max_workers=scan_workers) as executor:
        futures = {executor.submit(scan_subdomain, sub): sub for sub in all_subdomains}

        for future in as_completed(futures):
            result = future.result()
            scanned += 1

            if result:
                subdomain, vulns = result
                vulnerabilities.extend(vulns)

                for vuln in vulns:
                    print(f"[{scanned}/{len(all_subdomains)}] 🚨 VULNERABLE: {subdomain}")
                    print(f"    Type: {vuln['description']}")
                    print(f"    CNAME: {vuln['cname']}")

            if scanned % 100 == 0:
                print(f"[{scanned}/{len(all_subdomains)}] Scanned... ({len(vulnerabilities)} vulnerabilities)")

    # Save results
    vuln_file = f"vulnerable_subdomains_{country_code}.txt"
    detailed_file = f"vulnerable_detailed_{country_code}.txt"

    with open(vuln_file, 'w') as f:
        for vuln in vulnerabilities:
            f.write(f"{vuln['subdomain']}\n")

    with open(detailed_file, 'w') as f:
        f.write("Subdomain,Vulnerability Type,CNAME,Error Signature\n")
        for vuln in vulnerabilities:
            errors = '; '.join([e.get('signature', 'Unknown') for e in vuln['errors']])
            f.write(f"{vuln['subdomain']},{vuln['description']},{vuln['cname']},{errors}\n")

    print("-" * 60)
    print(f"\n✓ Vulnerability scan complete!")
    print(f"  Total scanned: {len(all_subdomains)}")
    print(f"  Vulnerabilities found: {len(vulnerabilities)}")
    print(f"\nOutput files:")
    print(f"  All subdomains: {all_file}")
    print(f"  Vulnerable list: {vuln_file}")
    print(f"  Detailed CSV: {detailed_file}")

    if vulnerabilities:
        print(f"\n🚨 FOUND {len(vulnerabilities)} POTENTIAL TAKEOVER TARGETS! 🚨")


def run_subfinder(domain):
    """Run subfinder on a domain."""
    try:
        result = subprocess.run(
            ['subfinder', '-d', domain, '-silent'],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            subdomains = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            return (domain, subdomains, True)
        return (domain, [], False)
    except:
        return (domain, [], False)


def main():
    """Main function."""
    country_code = 'bounty'

    # Target ranks 5000-15000 (less security budget, more vulns)
    start_rank = 5000
    num_domains = 1000

    print("=" * 60)
    print("Subdomain Takeover Vulnerability Scanner")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Target: Ranks {start_rank}-{start_rank + num_domains}")
    print(f"  Strategy: Focus on lower-ranked domains (higher vuln rate)")
    print(f"  Looking for: Dangling DNS, unclaimed resources")
    print()

    try:
        # Fetch domains
        print("Fetching domain list...")
        t = Tranco(cache=True, cache_dir='.tranco')
        latest_list = t.list()

        # Get domains from specific rank range
        all_ranked = latest_list.top(start_rank + num_domains)
        domains = all_ranked[start_rank:]

        print(f"✓ Fetched {len(domains)} domains from rank {start_rank}-{start_rank + num_domains}")

        # Save domains
        with open(f'target_domains_{country_code}.txt', 'w') as f:
            for domain in domains:
                f.write(f"{domain}\n")

        # Enumerate and scan
        enumerate_and_scan(domains, country_code, max_workers=10, scan_workers=15)

        print("\n" + "=" * 60)
        print("Complete!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
