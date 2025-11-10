#!/usr/bin/env python3
"""
NS (Nameserver) Takeover Detector
Checks if subdomains have delegated NS records pointing to unregistered/expired nameservers
"""

import dns.resolver
import dns.exception
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def check_ns_records(subdomain):
    """
    Check if subdomain has NS records

    Returns: (has_ns, nameservers, status)
    """
    try:
        # Query for NS records
        answers = dns.resolver.resolve(subdomain, 'NS')
        nameservers = [str(rdata.target).rstrip('.') for rdata in answers]

        if nameservers:
            return True, nameservers, "Has NS delegation"
        else:
            return False, [], "No NS records"

    except dns.resolver.NXDOMAIN:
        return False, [], "Domain doesn't exist"
    except dns.resolver.NoAnswer:
        return False, [], "No NS records"
    except dns.exception.Timeout:
        return False, [], "DNS timeout"
    except Exception as e:
        return False, [], f"Error: {str(e)}"

def check_nameserver_exists(nameserver):
    """
    Check if a nameserver domain is registered/active

    Returns: (exists, status)
    """
    try:
        # Try to resolve the nameserver itself
        answers = dns.resolver.resolve(nameserver, 'A')
        if answers:
            return True, "Active"
    except dns.resolver.NXDOMAIN:
        # Nameserver domain doesn't exist - VULNERABLE!
        return False, "NXDOMAIN (Unregistered)"
    except dns.resolver.NoAnswer:
        # No A record, but might still be registered
        # Check with whois
        return check_with_whois(nameserver)
    except dns.exception.Timeout:
        return None, "Timeout"
    except Exception as e:
        return None, f"Error: {str(e)}"

    return True, "Unknown"

def check_with_whois(domain):
    """
    Check if domain is registered using whois

    Returns: (registered, status)
    """
    try:
        result = subprocess.run(
            ['whois', domain],
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout.lower()

        # Check for "not found" or "no match" patterns
        if any(pattern in output for pattern in [
            'no match',
            'not found',
            'no entries found',
            'no data found',
            'domain not found',
            'status: free',
            'status: available'
        ]):
            return False, "Unregistered (whois)"

        # Check for active registration
        if any(pattern in output for pattern in [
            'registrar:',
            'creation date:',
            'registry expiry date:',
            'status: ok'
        ]):
            return True, "Registered"

        return None, "Unknown (whois inconclusive)"

    except subprocess.TimeoutExpired:
        return None, "Whois timeout"
    except FileNotFoundError:
        # whois not installed
        return None, "Whois not available"
    except Exception as e:
        return None, f"Whois error: {str(e)}"

def check_subdomain_ns_takeover(subdomain):
    """
    Complete NS takeover check for a subdomain

    Returns: dict with vulnerability info
    """
    result = {
        'subdomain': subdomain,
        'has_ns': False,
        'nameservers': [],
        'vulnerable': False,
        'vulnerable_ns': [],
        'status': 'Unknown',
        'details': ''
    }

    # Check for NS records
    has_ns, nameservers, ns_status = check_ns_records(subdomain)
    result['has_ns'] = has_ns
    result['nameservers'] = nameservers

    if not has_ns:
        result['status'] = ns_status
        return result

    # Check each nameserver
    vulnerable_ns = []
    for ns in nameservers:
        exists, ns_status = check_nameserver_exists(ns)

        if exists is False:
            # Nameserver doesn't exist - VULNERABLE!
            vulnerable_ns.append({
                'nameserver': ns,
                'status': ns_status
            })

    if vulnerable_ns:
        result['vulnerable'] = True
        result['vulnerable_ns'] = vulnerable_ns
        result['status'] = 'VULNERABLE'
        result['details'] = f"{len(vulnerable_ns)}/{len(nameservers)} nameservers unregistered"
    else:
        result['status'] = 'Safe'
        result['details'] = 'All nameservers are active'

    return result

def scan_subdomains_for_ns_takeover(subdomains, workers=10):
    """
    Scan multiple subdomains for NS takeover vulnerabilities

    Args:
        subdomains: List of subdomains to check
        workers: Number of parallel workers

    Returns: List of vulnerable subdomains
    """
    vulnerabilities = []
    total = len(subdomains)
    completed = 0

    print(f"🔍 Scanning {total} subdomains for NS takeover vulnerabilities...")
    print(f"Using {workers} parallel workers\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_subdomain = {
            executor.submit(check_subdomain_ns_takeover, subdomain): subdomain
            for subdomain in subdomains
        }

        for future in as_completed(future_to_subdomain):
            subdomain = future_to_subdomain[future]
            completed += 1

            try:
                result = future.result()

                if result['vulnerable']:
                    vulnerabilities.append(result)
                    print(f"[{completed}/{total}] ⚠️  VULNERABLE: {subdomain}")
                    print(f"    Nameservers: {', '.join(result['nameservers'])}")
                    for vns in result['vulnerable_ns']:
                        print(f"    ❌ {vns['nameserver']}: {vns['status']}")
                elif result['has_ns']:
                    print(f"[{completed}/{total}] ✅ Safe: {subdomain}")
                else:
                    print(f"[{completed}/{total}] ⊘  No NS: {subdomain}")

            except Exception as e:
                print(f"[{completed}/{total}] ❌ Error checking {subdomain}: {e}")

    return vulnerabilities

def save_results(vulnerabilities, output_file):
    """Save NS takeover vulnerabilities to file"""
    import csv

    if not vulnerabilities:
        print("\n✅ No NS takeover vulnerabilities found!")
        return

    # Save to CSV
    csv_file = Path(output_file).with_suffix('.csv')

    with open(csv_file, 'w', newline='') as f:
        fieldnames = ['subdomain', 'nameservers', 'vulnerable_nameservers', 'status', 'details']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for vuln in vulnerabilities:
            writer.writerow({
                'subdomain': vuln['subdomain'],
                'nameservers': ', '.join(vuln['nameservers']),
                'vulnerable_nameservers': ', '.join([vns['nameserver'] for vns in vuln['vulnerable_ns']]),
                'status': vuln['status'],
                'details': vuln['details']
            })

    # Save to TXT
    txt_file = Path(output_file).with_suffix('.txt')

    with open(txt_file, 'w') as f:
        f.write("="*60 + "\n")
        f.write("NS (Nameserver) Subdomain Takeover Vulnerabilities\n")
        f.write("="*60 + "\n\n")
        f.write(f"Total Vulnerabilities Found: {len(vulnerabilities)}\n\n")

        for vuln in vulnerabilities:
            f.write("-"*60 + "\n")
            f.write(f"Subdomain: {vuln['subdomain']}\n")
            f.write(f"Status: {vuln['status']}\n")
            f.write(f"Details: {vuln['details']}\n")
            f.write(f"\nNameservers:\n")
            for ns in vuln['nameservers']:
                f.write(f"  • {ns}\n")
            f.write(f"\nVulnerable Nameservers:\n")
            for vns in vuln['vulnerable_ns']:
                f.write(f"  ❌ {vns['nameserver']}: {vns['status']}\n")
            f.write("\n")

    print(f"\n✅ Results saved:")
    print(f"   • {csv_file}")
    print(f"   • {txt_file}")

if __name__ == "__main__":
    import sys

    # Example usage
    if len(sys.argv) > 1:
        # Read subdomains from file
        input_file = sys.argv[1]
        with open(input_file, 'r') as f:
            subdomains = [line.strip() for line in f if line.strip()]
    else:
        # Test with example subdomains
        subdomains = [
            'test.example.com',
            'old.example.com',
            'legacy.example.com'
        ]

    # Scan for NS takeovers
    vulnerabilities = scan_subdomains_for_ns_takeover(subdomains, workers=10)

    # Save results
    desktop = Path.home() / "Desktop"
    output_file = desktop / "ns_takeover_results"
    save_results(vulnerabilities, output_file)

    # Print summary
    print("\n" + "="*60)
    print(f"✅ Scan complete!")
    print(f"   Checked: {len(subdomains)} subdomains")
    print(f"   Vulnerable: {len(vulnerabilities)}")
    print("="*60)
