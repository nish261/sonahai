#!/usr/bin/env python3
"""
Deep verification script for potential subdomain takeover vulnerabilities
Checks the "Active (verify manually)" results more thoroughly

Enhanced with fingerprints from:
- can-i-take-over-xyz (EdOverflow)
- Nuclei templates (ProjectDiscovery)
"""

import sys
import subprocess
import socket
import requests
from pathlib import Path
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import enhanced fingerprints
try:
    from enhanced_fingerprints import (
        ENHANCED_FINGERPRINTS,
        get_service_by_cname,
        check_for_false_positive,
        is_vulnerable
    )
    ENHANCED_MODE = True
    print("✅ Enhanced fingerprint database loaded (43 services)")
except ImportError:
    ENHANCED_MODE = False
    print("⚠️  Using legacy fingerprints (enhanced_fingerprints.py not found)")

# Import notifications
try:
    from notification_helper import (
        notify_verification_started,
        notify_verification_complete,
        notify_error
    )
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False
    print("⚠️  Notifications disabled (notification_helper.py not found)")

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DESKTOP_PATH = Path.home() / "Desktop"
RESULTS_FOLDER = DESKTOP_PATH / "Subdomain_Takeover_Results"
SCANS_FOLDER = RESULTS_FOLDER / "Scans"
VERIFIED_FOLDER = RESULTS_FOLDER / "Verified_Vulnerabilities"

# Create folders if they don't exist
for folder in [RESULTS_FOLDER, SCANS_FOLDER, VERIFIED_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

INPUT_FILE = SCANS_FOLDER / "subdomain_takeover_detailed.csv"
OUTPUT_FILE = VERIFIED_FOLDER / "verified_vulnerabilities.txt"
DETAILED_OUTPUT = VERIFIED_FOLDER / "verified_vulnerabilities.csv"
VERIFY_PROGRESS = Path("verify_progress.txt")
VERIFY_STATUS = Path("verify_status.txt")

# Error signatures that indicate takeover opportunities
TAKEOVER_SIGNATURES = {
    's3': [
        'NoSuchBucket',
        'The specified bucket does not exist',
        'bucket does not exist',
        '<Error><Code>NoSuchBucket</Code>'
    ],
    'azure': [
        '404 Web Site not found',
        'The resource you are looking for has been removed',
        'Error 404: Web app not found',
        'WebApp Not Found'
    ],
    'github': [
        'There isn\'t a GitHub Pages site here',
        'For root URLs (like http://example.com/) you must provide an index.html file',
        'There isn\'t a GitHub Pages'
    ],
    'heroku': [
        'No such app',
        'no-such-app.html',
        'herokucdn.com/error-pages/no-such-app.html'
    ],
    'shopify': [
        'Sorry, this shop is currently unavailable',
        'Only one step left!',
        'This shop may be coming soon'
    ],
    'wordpress': [
        'Do you want to register',
        'doesn\'t exist',
        'this blog doesn\'t exist'
    ],
    'elasticbeanstalk': [
        'Elastic Beanstalk application is not found',
        'does not exist',
        'Environment not found'
    ],
    'pantheon': [
        '404 error unknown site!',
        'The gods are wise'
    ],
    'tumblr': [
        'Whatever you were looking for doesn\'t currently exist',
        'There\'s nothing here'
    ],
    'bitbucket': [
        'Repository not found',
        'The page you have requested does not exist'
    ],
    'webflow': [
        'The page you are looking for doesn\'t exist',
        'project not found'
    ],
    'statuspage': [
        'You are being',
        'redirected',
        'Status page doesn\'t exist'
    ]
}

def check_http_deeply(subdomain, service, cname, timeout=10):
    """Deep HTTP check for takeover signatures."""
    print(f"  Checking {subdomain}...")

    results = {
        'subdomain': subdomain,
        'service': service,
        'cname': cname,
        'vulnerable': False,
        'evidence': '',
        'http_status': '',
        'resolves': True
    }

    # Check if it resolves
    try:
        socket.setdefaulttimeout(5)
        socket.gethostbyname(subdomain)
    except:
        results['resolves'] = False
        results['vulnerable'] = True
        results['evidence'] = 'DNS does not resolve (dangling DNS)'
        return results

    # Try HTTP/HTTPS
    for protocol in ['https', 'http']:
        try:
            url = f"{protocol}://{subdomain}"
            response = requests.get(
                url,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            results['http_status'] = response.status_code
            content = response.text

            # Use enhanced fingerprints if available
            if ENHANCED_MODE:
                # Find matching service from CNAME
                matches = get_service_by_cname(cname)

                for service_name, service_data in matches:
                    # First check for FALSE POSITIVES (e.g., S3 403)
                    is_fp, fp_reason = check_for_false_positive(
                        service_name,
                        response.status_code,
                        content
                    )

                    if is_fp:
                        results['vulnerable'] = False
                        results['evidence'] = f'❌ NOT VULNERABLE: {fp_reason}'
                        print(f"    ❌ False positive detected: {fp_reason}")
                        return results

                    # Check if vulnerable
                    vuln, confidence, evidence = is_vulnerable(
                        service_name,
                        response.status_code,
                        content
                    )

                    if vuln:
                        results['vulnerable'] = True
                        results['evidence'] = f'✅ VULNERABLE ({confidence}% confidence): {evidence}'
                        print(f"    ✅ VULNERABLE: {evidence}")
                        return results

            # Fallback to legacy signatures
            content_lower = content.lower()
            service_key = service.lower().split()[0]  # Get first word (e.g., "AWS" from "AWS S3")

            for key, signatures in TAKEOVER_SIGNATURES.items():
                if key in service_key or service_key in key:
                    for signature in signatures:
                        if signature.lower() in content_lower:
                            results['vulnerable'] = True
                            results['evidence'] = f'Found signature: "{signature}"'
                            return results

            # Check for generic error pages
            if response.status_code == 404:
                if 'not found' in content_lower or 'does not exist' in content_lower:
                    results['vulnerable'] = True
                    results['evidence'] = f'404 error with "not found" message'
                    return results

        except requests.exceptions.ConnectionError:
            results['vulnerable'] = True
            results['evidence'] = 'Connection refused - likely unclaimed resource'
            return results
        except requests.exceptions.Timeout:
            results['evidence'] = 'Timeout - possibly misconfigured'
        except Exception as e:
            results['evidence'] = f'Error: {str(e)[:50]}'

    return results

def update_verify_status(message):
    """Update verification status for UI."""
    with open(VERIFY_STATUS, 'a') as f:
        f.write(f"{message}\n")

def update_verify_progress():
    """Create progress marker."""
    VERIFY_PROGRESS.touch()

def main():
    """Main verification function."""
    # Clean old status
    for f in [VERIFY_PROGRESS, VERIFY_STATUS]:
        if f.exists():
            f.unlink()

    update_verify_progress()

    if not INPUT_FILE.exists():
        msg = f"❌ Error: {INPUT_FILE.name} not found! Run a scan first."
        print(msg)
        update_verify_status(msg)
        sys.exit(1)

    # Read CSV
    with open(INPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        all_results = list(reader)

    # Filter only "Active (verify manually)" ones
    to_verify = [r for r in all_results if 'Active' in r.get('status', '')]

    msg = f"🔍 Deep Verification Starting..."
    print(msg)
    update_verify_status(msg)

    msg = f"📊 Found {len(to_verify)} subdomains to verify"
    print(msg)
    update_verify_status(msg)

    msg = f"⏱️  This will take a while (checking HTTP responses)..."
    print(msg)
    update_verify_status(msg)

    # Notify verification started
    if NOTIFICATIONS_ENABLED:
        notify_verification_started(len(to_verify))

    verified_vulns = []
    not_verified = []  # Track unverified ones
    checked = 0

    # Use thread pool for parallel checking
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(
                check_http_deeply,
                r['subdomain'],
                r['service'],
                r['cname']
            ): r for r in to_verify
        }

        for future in as_completed(futures):
            result = future.result()
            checked += 1

            if result['vulnerable']:
                verified_vulns.append(result)
                msg = f"🚨 VULNERABLE: {result['subdomain']} - {result['evidence']}"
                print(msg)
                update_verify_status(msg)
            else:
                not_verified.append(result)  # Store unverified

            if checked % 10 == 0:
                msg = f"⏳ Progress: {checked}/{len(to_verify)} ({len(verified_vulns)} vulnerable found)"
                print(msg)
                update_verify_status(msg)

    # Save results
    msg = f"📝 Saving results..."
    print(f"\n{msg}")
    update_verify_status(msg)

    # Text file
    with open(OUTPUT_FILE, 'w') as f:
        f.write(f"VERIFIED Subdomain Takeover Vulnerabilities\n")
        f.write(f"{'='*80}\n\n")
        f.write(f"Total Verified: {len(verified_vulns)}\n")
        f.write(f"Total Unverified: {len(not_verified)}\n")
        f.write(f"Checked: {len(to_verify)}\n\n")

        if verified_vulns:
            f.write(f"🚨 HIGH PRIORITY - VERIFIED VULNERABILITIES ({len(verified_vulns)}):\n")
            f.write(f"{'-'*80}\n\n")

            for vuln in verified_vulns:
                f.write(f"{vuln['subdomain']}\n")
                f.write(f"  Service: {vuln['service']}\n")
                f.write(f"  CNAME: {vuln['cname']}\n")
                f.write(f"  Evidence: {vuln['evidence']}\n")
                f.write(f"  HTTP Status: {vuln['http_status']}\n")
                f.write(f"  Resolves: {vuln['resolves']}\n")
                f.write(f"\n")
        else:
            f.write("No verified vulnerabilities found.\n\n")

        # Add unverified section
        if not_verified:
            f.write(f"\n{'='*80}\n")
            f.write(f"⚠️  UNVERIFIED / NEEDS MANUAL CHECK ({len(not_verified)}):\n")
            f.write(f"{'-'*80}\n\n")
            f.write(f"These subdomains did NOT show clear takeover signatures but may still be\n")
            f.write(f"vulnerable. Recommend manual investigation.\n\n")

            for unverif in not_verified:
                f.write(f"{unverif['subdomain']}\n")
                f.write(f"  Service: {unverif['service']}\n")
                f.write(f"  CNAME: {unverif['cname']}\n")
                f.write(f"  HTTP Status: {unverif.get('http_status', 'N/A')}\n")
                f.write(f"  Resolves: {unverif.get('resolves', 'Unknown')}\n")
                if unverif.get('evidence'):
                    f.write(f"  Note: {unverif['evidence']}\n")
                f.write(f"\n")

    # CSV file
    with open(DETAILED_OUTPUT, 'w', newline='') as f:
        fieldnames = ['subdomain', 'service', 'cname', 'vulnerable', 'evidence', 'http_status', 'resolves']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(verified_vulns)

    msg = f"✅ Verification Complete!"
    print(f"\n{msg}")
    update_verify_status(msg)

    # Notify verification complete
    if NOTIFICATIONS_ENABLED:
        notify_verification_complete(len(verified_vulns), len(to_verify))

    msg = f"📊 Checked: {len(to_verify)} subdomains"
    print(msg)
    update_verify_status(msg)

    msg = f"🚨 Verified Vulnerable: {len(verified_vulns)}"
    print(msg)
    update_verify_status(msg)

    msg = f"📁 Results saved to Desktop: {OUTPUT_FILE.name}, {DETAILED_OUTPUT.name}"
    print(msg)
    update_verify_status(msg)

    if verified_vulns:
        msg = f"🎯 You found {len(verified_vulns)} VERIFIED vulnerabilities!"
        print(f"\n{msg}")
        update_verify_status(msg)
    else:
        msg = f"⚠️ No verified takeovers found. The 'active' results are likely properly configured."
        print(f"\n{msg}")
        update_verify_status(msg)

    # Clean up progress marker
    import time
    time.sleep(3)
    if VERIFY_PROGRESS.exists():
        VERIFY_PROGRESS.unlink()

if __name__ == "__main__":
    main()
