#!/usr/bin/env python3
"""
Non-interactive runner for USA domains.
Fetches 1000 domains and enumerates subdomains with filtering.
"""

import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main script functions
from fetch_top_domains import (
    fetch_top_domains,
    save_to_file,
    check_subfinder,
    enumerate_subdomains
)

def main():
    """Run with preset USA parameters."""
    country_code = 'usa'
    num_domains = 1000
    max_workers = 10

    print("=" * 60)
    print("Top Domains Fetcher + Subdomain Enumerator")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Country: United States (USA)")
    print(f"  Domains to fetch: {num_domains}")
    print(f"  Parallel workers: {max_workers}")
    print()

    # Check subfinder
    if not check_subfinder():
        print("⚠ ERROR: subfinder not found!")
        print("Install with: brew install subfinder")
        sys.exit(1)

    print("✓ subfinder detected!")
    print()

    try:
        # Fetch domains
        print("Starting domain fetch...")
        domains = fetch_top_domains(country_code, num_domains)

        # Save to file
        filename = save_to_file(domains, country_code)

        print(f"\nFirst 10 domains:")
        for i, domain in enumerate(domains[:10], 1):
            print(f"  {i}. {domain}")

        if len(domains) > 10:
            print(f"  ... and {len(domains) - 10} more")

        # Enumerate and filter subdomains
        print("\n" + "=" * 60)
        print("Starting subdomain enumeration with filtering...")
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
