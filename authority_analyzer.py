#!/usr/bin/env python3
"""
Domain Authority Analyzer - SIMPLIFIED VERSION
Only tracks website fame/authority - NO niche detection
"""

import csv
from pathlib import Path
import signal
from contextlib import contextmanager
from dr_backlink_checker import DRBacklinkChecker, load_credentials

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

def analyze_authority(input_csv, output_csv):
    """Analyze subdomains for domain authority ONLY"""
    results = []

    print("🔍 Analyzing domain authority...")

    try:
        access_id, secret_key = load_credentials()
        dr_checker = DRBacklinkChecker(access_id, secret_key)
        print("✓ DR checker initialized")
    except:
        dr_checker = None
        print("⚠️  No DR checker")

    try:
        with open(input_csv, 'r', encoding='utf-8', errors='ignore') as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    total = len(rows)
    print(f"📊 Analyzing {total} domains...")

    for idx, row in enumerate(rows, 1):
        try:
            subdomain = str(row.get('subdomain', '')).strip()
            if not subdomain:
                continue

            parts = subdomain.split('.')
            parent_domain = '.'.join(parts[-2:]) if len(parts) >= 2 else subdomain

            print(f"[{idx}/{total}] {subdomain}")

            da = backlinks = linking = spam = 0
            source = 'None'

            if dr_checker:
                try:
                    with time_limit(15):
                        data = dr_checker.check_domain(parent_domain, prefer_cache=True)
                        da = int(data.get('domain_authority', 0))
                        backlinks = int(data.get('total_backlinks', 0))
                        linking = int(data.get('linking_domains', 0))
                        spam = int(data.get('spam_score', 0))
                        source = str(data.get('source', 'Unknown'))
                except:
                    pass

            # Calculate trust score ONLY from authority metrics
            trust = min(50, da * 0.5)
            if backlinks >= 100000: trust += 30
            elif backlinks >= 10000: trust += 25
            elif backlinks >= 1000: trust += 15
            elif backlinks >= 100: trust += 8

            if linking >= 10000: trust += 20
            elif linking >= 1000: trust += 15
            elif linking >= 100: trust += 10

            trust -= min(20, spam * 0.2)
            trust = max(0, min(100, int(trust)))

            # Fame level 1-10
            fame = 10 if da >= 90 else 9 if da >= 80 else 8 if da >= 70 else 7 if da >= 60 else 6 if da >= 50 else 5 if da >= 40 else 4 if da >= 30 else 3 if da >= 20 else 2 if da >= 10 else 1 if da > 0 else 0

            results.append({
                'subdomain': subdomain,
                'parent_domain': parent_domain,
                'service': row.get('service', ''),
                'cname': row.get('cname', ''),
                'status': row.get('status', ''),
                'domain_authority': da,
                'fame_level': fame,
                'total_backlinks': backlinks,
                'linking_domains': linking,
                'spam_score': spam,
                'trust_score': trust,
                'dr_source': source
            })

            print(f"  → DA={da}, Fame={fame}/10, Trust={trust}/100")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    # Sort by trust score
    results.sort(key=lambda x: (-x['trust_score'], -x['domain_authority']))

    for rank, r in enumerate(results, 1):
        r['rank'] = rank

    # Write results
    if results:
        Path(output_csv).parent.mkdir(parents=True, exist_ok=True)

        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'rank', 'trust_score', 'fame_level', 'subdomain', 'parent_domain',
                'domain_authority', 'total_backlinks', 'linking_domains', 'spam_score',
                'service', 'cname', 'status', 'dr_source'
            ])
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Done! {len(results)} results saved to {output_csv}")
        print(f"\n🏆 Top 5:")
        for i, r in enumerate(results[:5], 1):
            print(f"  {i}. {r['subdomain']} - DA:{r['domain_authority']}, Trust:{r['trust_score']}/100")

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python authority_analyzer.py <input_csv> [output_csv]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else str(Path.home() / "Desktop/Subdomain_Takeover_Results/Authority_Analysis/authority_analysis.csv")

    analyze_authority(input_file, output_file)
