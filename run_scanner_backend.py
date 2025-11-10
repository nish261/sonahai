#!/usr/bin/env python3
"""
Backend scanner - writes progress to files for UI
"""

import sys
import subprocess
import socket
import re
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from tranco import Tranco

DESKTOP_PATH = Path.home() / "Desktop"
OUTPUT_FILE = DESKTOP_PATH / "subdomain_takeover_results.txt"
DETAILED_FILE = DESKTOP_PATH / "subdomain_takeover_detailed.csv"
PROGRESS_FILE = Path("scan_progress.txt")
STATUS_FILE = Path("scan_status.txt")

def update_status(status, phase, log_msg=None):
    """Update status files."""
    with open(STATUS_FILE, 'w') as f:
        f.write(f"{status}\n{phase}\n")
        if log_msg:
            # Read existing logs
            if STATUS_FILE.exists():
                with open(STATUS_FILE) as rf:
                    existing = rf.readlines()[2:] if len(rf.readlines()) > 2 else []
            else:
                existing = []

            # Write logs (keep last 100)
            with open(STATUS_FILE, 'a') as f:
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

def get_dns_records(subdomain, timeout=3):
    """Get DNS records."""
    result = {'cnames': [], 'ips': []}
    try:
        dig_result = subprocess.run(
            ['dig', '+short', 'CNAME', subdomain],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if dig_result.returncode == 0 and dig_result.stdout.strip():
            result['cnames'] = [line.strip().rstrip('.') for line in dig_result.stdout.strip().split('\n') if line.strip()]

        try:
            socket.setdefaulttimeout(timeout)
            result['ips'] = socket.gethostbyname_ex(subdomain)[2]
        except:
            pass
    except:
        pass
    return result

def check_http_response(subdomain, timeout=5):
    """Check HTTP for takeover signatures."""
    errors = []
    for protocol in ['https', 'http']:
        try:
            url = f"{protocol}://{subdomain}"
            response = requests.get(url, timeout=timeout, allow_redirects=True, verify=False)

            if 'NoSuchBucket' in response.text or 'The specified bucket does not exist' in response.text:
                errors.append('S3 Bucket - NoSuchBucket')
            elif 'does not exist' in response.text.lower():
                errors.append('Resource does not exist')
        except:
            continue
    return errors

def scan_subdomain(subdomain):
    """Scan for vulnerabilities."""
    dns_records = get_dns_records(subdomain)

    if not dns_records['cnames']:
        return None

    for cname in dns_records['cnames']:
        # Check for S3
        if re.search(r'\.s3\.amazonaws\.com$|\.s3-website', cname, re.IGNORECASE):
            http_errors = check_http_response(subdomain)
            if http_errors or not dns_records['ips']:
                return {
                    'subdomain': subdomain,
                    'type': 'S3 Bucket Takeover',
                    'cname': cname,
                    'status': 'VULNERABLE' if http_errors else 'DNS Orphan'
                }

        # Check for Elastic Beanstalk
        elif re.search(r'\.elasticbeanstalk\.com$', cname, re.IGNORECASE):
            http_errors = check_http_response(subdomain)
            if http_errors or not dns_records['ips']:
                return {
                    'subdomain': subdomain,
                    'type': 'Elastic Beanstalk Takeover',
                    'cname': cname,
                    'status': 'VULNERABLE' if http_errors else 'DNS Orphan'
                }

    return None

def main():
    """Main scanner."""
    if len(sys.argv) < 3:
        print("Usage: run_scanner_backend.py <start_rank> <num_domains>")
        sys.exit(1)

    start_rank = int(sys.argv[1])
    num_domains = int(sys.argv[2])

    try:
        # Initialize
        update_status("Initializing...", "Starting", "Cleaning old results")
        update_progress(0)

        # Fetch domains
        update_status("Downloading list...", "Fetching Domains", "Connecting to Tranco")
        update_progress(5)

        t = Tranco(cache=True, cache_dir='.tranco')
        latest_list = t.list()
        all_ranked = latest_list.top(start_rank + num_domains)
        domains = all_ranked[start_rank:]

        update_status(f"Fetched {len(domains)} domains", "Fetching Domains", f"Got {len(domains)} domains")
        update_progress(10)

        # Phase 1: Enumeration
        update_status("Running subfinder...", "Phase 1: Enumeration", "Starting subdomain enumeration")
        update_progress(15)

        all_subdomains = []
        completed = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(run_subfinder, d): d for d in domains}

            for future in as_completed(futures):
                domain, subs, success = future.result()
                completed += 1

                if subs:
                    all_subdomains.extend(subs)
                    update_status(
                        f"Enumerated {completed}/{len(domains)}",
                        "Phase 1: Enumeration",
                        f"{domain}: {len(subs)} subdomains"
                    )

                progress = 15 + int((completed / len(domains)) * 35)
                update_progress(progress)

        update_status(f"Found {len(all_subdomains)} subdomains", "Phase 1: Complete",
                     f"Total: {len(all_subdomains)} subdomains")
        update_progress(50)

        # Phase 2: Vulnerability Scanning
        update_status("Testing vulnerabilities...", "Phase 2: Scanning", "Starting vulnerability tests")
        update_progress(55)

        vulnerabilities = []
        scanned = 0

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(scan_subdomain, s): s for s in all_subdomains}

            for future in as_completed(futures):
                result = future.result()
                scanned += 1

                if result:
                    vulnerabilities.append(result)
                    update_status(
                        f"Scanned {scanned}/{len(all_subdomains)}",
                        "Phase 2: Scanning",
                        f"🚨 VULN: {result['subdomain']} - {result['type']}"
                    )

                progress = 55 + int((scanned / len(all_subdomains)) * 40)
                update_progress(progress)

        # Save results
        update_status("Saving results...", "Saving", "Writing to Desktop")
        update_progress(95)

        if vulnerabilities:
            # Save text file
            with open(OUTPUT_FILE, 'w') as f:
                f.write(f"Subdomain Takeover Vulnerabilities\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Found: {len(vulnerabilities)}\n")
                f.write("="*80 + "\n\n")

                for vuln in vulnerabilities:
                    f.write(f"{vuln['subdomain']}\n")
                    f.write(f"  Type: {vuln['type']}\n")
                    f.write(f"  CNAME: {vuln['cname']}\n")
                    f.write(f"  Status: {vuln['status']}\n")
                    f.write("\n")

            # Save CSV
            import csv
            with open(DETAILED_FILE, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['subdomain', 'type', 'cname', 'status'])
                writer.writeheader()
                writer.writerows(vulnerabilities)

        # Complete
        update_status(f"Complete! Found {len(vulnerabilities)} vulnerabilities", "Complete",
                     f"Results saved to Desktop")
        update_progress(100)

        # Clean up progress files after 5 seconds
        import time
        time.sleep(5)
        PROGRESS_FILE.unlink()

    except Exception as e:
        update_status(f"Error: {str(e)}", "Error", f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
