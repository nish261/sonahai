#!/usr/bin/env python3
"""
Fetch top 1000 domains by country and enumerate subdomains using subfinder.

Note: Tranco doesn't provide built-in country filtering. This script uses the global
Tranco list as a base. For true country-specific rankings, you would need to:
1. Use commercial services like SimilarWeb or Alexa (discontinued)
2. Configure a custom Tranco list via their web interface (requires account)
3. Use alternative data sources like Chrome User Experience Report

This script fetches the global top domains from Tranco and optionally runs subfinder
to enumerate subdomains.
"""

import sys
import subprocess
import shutil
import socket
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    from tranco import Tranco
except ImportError:
    print("Error: tranco package not installed.")
    print("Please install it with: pip install tranco")
    sys.exit(1)


SUPPORTED_COUNTRIES = {
    'usa': 'United States',
    'uk': 'United Kingdom',
    'au': 'Australia',
    'ca': 'Canada',
    'nz': 'New Zealand'
}

# Thread lock for safe file writing
write_lock = threading.Lock()

# Infrastructure fingerprint patterns
INFRASTRUCTURE_PATTERNS = {
    'aws_elasticbeanstalk': {
        'cname_patterns': [
            r'\.elasticbeanstalk\.com$',
            r'\.eb\.amazonaws\.com$',
            r'awseb-.*\.elb\.amazonaws\.com$',
        ],
        'description': 'AWS Elastic Beanstalk'
    },
    'aws_s3': {
        'cname_patterns': [
            r'\.s3\.amazonaws\.com$',
            r'\.s3-website[-.]',
            r'\.s3[-.].*\.amazonaws\.com$',
            r's3\.amazonaws\.com$',
        ],
        'description': 'AWS S3'
    },
    'digitalocean': {
        'cname_patterns': [
            r'\.digitaloceanspaces\.com$',
            r'\.ondigitalocean\.app$',
            r'\.do\.direct$',
        ],
        'ip_patterns': [
            # DigitalOcean IP ranges (examples - not exhaustive)
            r'^159\.65\.',
            r'^157\.230\.',
            r'^167\.99\.',
            r'^178\.128\.',
            r'^188\.166\.',
            r'^206\.189\.',
        ],
        'description': 'DigitalOcean'
    },
    'wordpress': {
        'cname_patterns': [
            r'\.wordpress\.com$',
            r'\.wp\.com$',
            r'\.wpcomstaging\.com$',
            r'\.wpengine\.com$',
            r'\.wpenginepowered\.com$',
            r'\.pantheonsite\.io$',
            r'\.kinsta\.cloud$',
            r'\.getflywheel\.com$',
        ],
        'description': 'WordPress Hosting'
    }
}


def fetch_top_domains(country_code, num_domains=1000):
    """
    Fetch top domains for a country.

    Args:
        country_code: Country code (usa, uk, au, ca, nz)
        num_domains: Number of domains to fetch (default: 1000)

    Returns:
        List of domain names
    """
    print(f"Fetching top {num_domains} domains for {SUPPORTED_COUNTRIES[country_code]}...")
    print("Note: Using global Tranco list (country-specific filtering not available)")

    # Initialize Tranco with caching
    t = Tranco(cache=True, cache_dir='.tranco')

    # Get the latest list
    print("Downloading latest Tranco list...")
    latest_list = t.list()

    # Get top N domains
    top_domains = latest_list.top(num_domains)

    return top_domains


def save_to_file(domains, country_code):
    """Save domains to a text file."""
    filename = f"top_domains_{country_code}.txt"
    filepath = Path(filename)

    with open(filepath, 'w') as f:
        for domain in domains:
            f.write(f"{domain}\n")

    print(f"\n✓ Saved {len(domains)} domains to {filename}")
    return filename


def check_subfinder():
    """Check if subfinder is installed."""
    return shutil.which("subfinder") is not None


def get_dns_records(subdomain, timeout=3):
    """
    Get DNS records (CNAME and A records) for a subdomain.

    Args:
        subdomain: Subdomain to lookup
        timeout: DNS lookup timeout in seconds

    Returns:
        Dict with 'cnames' and 'ips' lists
    """
    result = {'cnames': [], 'ips': []}

    try:
        # Try to get CNAME records using dig
        dig_result = subprocess.run(
            ['dig', '+short', 'CNAME', subdomain],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if dig_result.returncode == 0 and dig_result.stdout.strip():
            cnames = [line.strip().rstrip('.') for line in dig_result.stdout.strip().split('\n') if line.strip()]
            result['cnames'] = cnames

        # Get A records (IP addresses)
        try:
            socket.setdefaulttimeout(timeout)
            ips = socket.gethostbyname_ex(subdomain)[2]
            result['ips'] = ips
        except (socket.gaierror, socket.timeout):
            pass

    except (subprocess.TimeoutExpired, Exception):
        pass

    return result


def check_infrastructure(subdomain, dns_records):
    """
    Check if a subdomain is hosted on target infrastructure.

    Args:
        subdomain: Subdomain name
        dns_records: DNS records dict from get_dns_records()

    Returns:
        Tuple of (is_match, infrastructure_type, matched_value)
    """
    # Check CNAME patterns
    for cname in dns_records['cnames']:
        for infra_type, patterns in INFRASTRUCTURE_PATTERNS.items():
            if 'cname_patterns' in patterns:
                for pattern in patterns['cname_patterns']:
                    if re.search(pattern, cname, re.IGNORECASE):
                        return (True, infra_type, f"CNAME: {cname}")

    # Check IP patterns (mainly for DigitalOcean)
    for ip in dns_records['ips']:
        for infra_type, patterns in INFRASTRUCTURE_PATTERNS.items():
            if 'ip_patterns' in patterns:
                for pattern in patterns['ip_patterns']:
                    if re.search(pattern, ip):
                        return (True, infra_type, f"IP: {ip}")

    return (False, None, None)


def filter_subdomain(subdomain):
    """
    Filter a single subdomain to check if it's on target infrastructure.

    Args:
        subdomain: Subdomain to check

    Returns:
        Tuple of (subdomain, is_match, infrastructure_type, matched_value)
    """
    dns_records = get_dns_records(subdomain)
    is_match, infra_type, matched_value = check_infrastructure(subdomain, dns_records)

    return (subdomain, is_match, infra_type, matched_value)


def run_subfinder(domain, verbose=False):
    """
    Run subfinder on a single domain.

    Args:
        domain: Domain to enumerate subdomains for
        verbose: Show subfinder output

    Returns:
        Tuple of (domain, subdomains_list, success)
    """
    try:
        cmd = ["subfinder", "-d", domain, "-silent"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per domain
        )

        if result.returncode == 0:
            subdomains = [s.strip() for s in result.stdout.strip().split('\n') if s.strip()]
            return (domain, subdomains, True)
        else:
            return (domain, [], False)

    except subprocess.TimeoutExpired:
        return (domain, [], False)
    except Exception as e:
        if verbose:
            print(f"Error with {domain}: {e}")
        return (domain, [], False)


def enumerate_subdomains(domains, country_code, max_workers=10, filter_workers=20):
    """
    Enumerate subdomains for all domains using subfinder and filter by infrastructure.

    Args:
        domains: List of domains to enumerate
        country_code: Country code for output filename
        max_workers: Number of parallel subfinder processes
        filter_workers: Number of parallel DNS filtering workers
    """
    all_subdomains_file = f"subdomains_all_{country_code}.txt"
    filtered_subdomains_file = f"subdomains_filtered_{country_code}.txt"
    detailed_results_file = f"subdomains_detailed_{country_code}.txt"

    # Clear/create output files
    Path(all_subdomains_file).write_text("")
    Path(filtered_subdomains_file).write_text("")
    Path(detailed_results_file).write_text("")

    print(f"\n{'='*60}")
    print("PHASE 1: Subdomain Enumeration")
    print(f"{'='*60}")
    print(f"Enumerating subdomains for {len(domains)} domains...")
    print(f"Running with {max_workers} parallel workers")
    print("-" * 60)

    all_subdomains = []
    completed = 0
    failed = 0

    # Phase 1: Enumerate all subdomains
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_domain = {
            executor.submit(run_subfinder, domain): domain
            for domain in domains
        }

        for future in as_completed(future_to_domain):
            domain, subdomains, success = future.result()
            completed += 1

            if success:
                all_subdomains.extend(subdomains)
                status = f"[{completed}/{len(domains)}] {domain}: {len(subdomains)} subdomains"
            else:
                failed += 1
                status = f"[{completed}/{len(domains)}] {domain}: FAILED"

            print(status)

    # Save all subdomains
    with open(all_subdomains_file, 'w') as f:
        for subdomain in all_subdomains:
            f.write(f"{subdomain}\n")

    print("-" * 60)
    print(f"\n✓ Enumeration complete!")
    print(f"  Total domains processed: {len(domains)}")
    print(f"  Total subdomains found: {len(all_subdomains)}")
    print(f"  Failed: {failed}")
    print(f"  All results saved to: {all_subdomains_file}")

    if not all_subdomains:
        print("\nNo subdomains found to filter.")
        return all_subdomains_file, 0

    # Phase 2: Filter subdomains
    print(f"\n{'='*60}")
    print("PHASE 2: Infrastructure Filtering")
    print(f"{'='*60}")
    print(f"Filtering {len(all_subdomains)} subdomains for target infrastructure...")
    print(f"Target: AWS (EBS, S3), DigitalOcean, WordPress hosting")
    print(f"Running with {filter_workers} parallel DNS lookup workers")
    print("-" * 60)

    filtered_results = []
    processed = 0

    with ThreadPoolExecutor(max_workers=filter_workers) as executor:
        future_to_subdomain = {
            executor.submit(filter_subdomain, subdomain): subdomain
            for subdomain in all_subdomains
        }

        for future in as_completed(future_to_subdomain):
            subdomain, is_match, infra_type, matched_value = future.result()
            processed += 1

            if is_match:
                filtered_results.append({
                    'subdomain': subdomain,
                    'type': infra_type,
                    'match': matched_value
                })

                # Show matches in real-time
                infra_desc = INFRASTRUCTURE_PATTERNS[infra_type]['description']
                print(f"[{processed}/{len(all_subdomains)}] ✓ {subdomain} -> {infra_desc}")

            # Show progress every 50 subdomains
            if processed % 50 == 0:
                print(f"[{processed}/{len(all_subdomains)}] Processed... ({len(filtered_results)} matches)")

    # Save filtered results
    with open(filtered_subdomains_file, 'w') as f:
        for result in filtered_results:
            f.write(f"{result['subdomain']}\n")

    # Save detailed results
    with open(detailed_results_file, 'w') as f:
        f.write("Subdomain,Infrastructure Type,Match Details\n")
        for result in filtered_results:
            infra_desc = INFRASTRUCTURE_PATTERNS[result['type']]['description']
            f.write(f"{result['subdomain']},{infra_desc},{result['match']}\n")

    print("-" * 60)
    print(f"\n✓ Filtering complete!")
    print(f"  Total subdomains checked: {len(all_subdomains)}")
    print(f"  Matching infrastructure: {len(filtered_results)}")
    print(f"  Match rate: {len(filtered_results)/len(all_subdomains)*100:.2f}%")
    print(f"\nOutput files:")
    print(f"  All subdomains: {all_subdomains_file}")
    print(f"  Filtered list: {filtered_subdomains_file}")
    print(f"  Detailed CSV: {detailed_results_file}")

    # Show breakdown by infrastructure type
    if filtered_results:
        print(f"\nBreakdown by infrastructure:")
        type_counts = {}
        for result in filtered_results:
            infra_desc = INFRASTRUCTURE_PATTERNS[result['type']]['description']
            type_counts[infra_desc] = type_counts.get(infra_desc, 0) + 1

        for infra_desc, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {infra_desc}: {count}")

    return filtered_subdomains_file, len(filtered_results)


def main():
    """Main function to run the script."""
    print("=" * 60)
    print("Top Domains Fetcher + Subdomain Enumerator")
    print("=" * 60)
    print("\nSupported countries:")
    for code, name in SUPPORTED_COUNTRIES.items():
        print(f"  - {code}: {name}")
    print()

    # Get country from user
    while True:
        country_code = input("Enter country code (usa/uk/au/ca/nz): ").strip().lower()

        if country_code in SUPPORTED_COUNTRIES:
            break
        else:
            print(f"Invalid country code. Please choose from: {', '.join(SUPPORTED_COUNTRIES.keys())}")

    # Optional: Ask for number of domains
    while True:
        num_input = input("\nNumber of domains to fetch [default: 1000]: ").strip()
        if not num_input:
            num_domains = 1000
            break
        try:
            num_domains = int(num_input)
            if num_domains <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    # Check if subfinder is available
    subfinder_available = check_subfinder()

    # Ask if user wants subdomain enumeration
    enumerate_subs = False
    max_workers = 10

    if subfinder_available:
        print("\n✓ subfinder detected!")
        while True:
            choice = input("Enumerate subdomains? (yes/no) [default: yes]: ").strip().lower()
            if choice in ['', 'y', 'yes']:
                enumerate_subs = True
                break
            elif choice in ['n', 'no']:
                enumerate_subs = False
                break
            else:
                print("Please answer 'yes' or 'no'")

        if enumerate_subs:
            while True:
                worker_input = input("Number of parallel workers [default: 10]: ").strip()
                if not worker_input:
                    max_workers = 10
                    break
                try:
                    max_workers = int(worker_input)
                    if max_workers <= 0:
                        print("Please enter a positive number.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
    else:
        print("\n⚠ subfinder not found. Subdomain enumeration will be skipped.")
        print("Install subfinder: https://github.com/projectdiscovery/subfinder")

    print()

    try:
        # Fetch domains
        domains = fetch_top_domains(country_code, num_domains)

        # Save to file
        filename = save_to_file(domains, country_code)

        print(f"\nFirst 10 domains:")
        for i, domain in enumerate(domains[:10], 1):
            print(f"  {i}. {domain}")

        if len(domains) > 10:
            print(f"  ... and {len(domains) - 10} more")

        # Enumerate subdomains if requested
        if enumerate_subs:
            print("\n" + "=" * 60)
            print("Starting subdomain enumeration...")
            print("=" * 60)
            enumerate_subdomains(domains, country_code, max_workers)

        print("\n" + "=" * 60)
        print("Complete!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
