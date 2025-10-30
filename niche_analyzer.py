#!/usr/bin/env python3
"""
Niche Analyzer for Subdomain Takeovers
Analyzes subdomains and suggests affiliate marketing niches
SIMPLIFIED VERSION - Removed external API dependencies for reliability
"""

import re
import csv
from pathlib import Path
from urllib.parse import urlparse

# High-value CPA offer verticals
# Focused on performance marketing & CPA networks (MaxBounty, CrakRevenue, etc.)
CPA_VERTICALS = {
    'nutra': {
        'keywords': ['diet', 'weight', 'loss', 'slim', 'fitness', 'supplement', 'pill', 'health', 'keto', 'detox', 'muscle', 'burn', 'fat', 'nutrition', 'protein', 'vitamin'],
        'value': '💰 VERY HIGH ($50-300 CPA)',
        'offers': 'Weight loss, diet pills, supplements, muscle building, detox',
        'networks': 'MaxBounty, CrakRevenue, A4D, ClickDealer',
        'difficulty': 'Medium',
        'priority': 10
    },
    'dating': {
        'keywords': ['dating', 'match', 'meet', 'singles', 'love', 'romance', 'hookup', 'date', 'flirt', 'chat', 'relationship', 'partner', 'marry'],
        'value': '💰 VERY HIGH ($1-10 SOI, $30-150 DOI)',
        'offers': 'Dating sites, hookup apps, matchmaking, adult dating',
        'networks': 'CrakRevenue, MaxBounty, AdCombo, Dating.com',
        'difficulty': 'Easy',
        'priority': 10
    },
    'gambling': {
        'keywords': ['casino', 'bet', 'betting', 'poker', 'slot', 'jackpot', 'gamble', 'wager', 'odds', 'sports-bet', 'lottery', 'game', 'stake', 'win'],
        'value': '💰 EXTREME ($100-1000+ CPA)',
        'offers': 'Online casinos, sports betting, poker rooms, slots',
        'networks': 'RevenueGiants, Income Access, Gambling Affiliation',
        'difficulty': 'Hard (legal compliance)',
        'priority': 10
    },
    'sweepstakes': {
        'keywords': ['win', 'prize', 'sweeps', 'giveaway', 'contest', 'free', 'gift', 'reward', 'enter', 'chance'],
        'value': '💰 HIGH ($1-5 SOI, $10-40 CPA)',
        'offers': 'Free iPhone, gift card sweeps, prize giveaways',
        'networks': 'MaxBounty, AdGate, CPAlead, AdWork Media',
        'difficulty': 'Easy',
        'priority': 9
    },
    'finance': {
        'keywords': ['loan', 'credit', 'debt', 'money', 'cash', 'payday', 'finance', 'bank', 'invest', 'trading', 'forex', 'crypto', 'wallet', 'card'],
        'value': '💰 VERY HIGH ($30-500 CPA)',
        'offers': 'Payday loans, credit cards, forex, crypto trading, debt relief',
        'networks': 'MaxBounty, Perform[cb], FlexOffers, Commission Junction',
        'difficulty': 'Hard (compliance)',
        'priority': 9
    },
    'insurance': {
        'keywords': ['insurance', 'quote', 'coverage', 'policy', 'auto', 'car', 'life', 'health', 'home', 'premium'],
        'value': '💰 VERY HIGH ($5-200 CPA)',
        'offers': 'Auto insurance, life insurance, health insurance quotes',
        'networks': 'QuinStreet, MediaAlpha, EverQuote, LeadGeneration',
        'difficulty': 'Medium',
        'priority': 8
    },
    'adult': {
        'keywords': ['adult', 'xxx', 'porn', 'cam', 'webcam', 'sexy', 'nsfw', 'mature', 'girls', 'live'],
        'value': '💰 HIGH ($1-50 CPA, RevShare)',
        'offers': 'Cam sites, adult dating, premium content',
        'networks': 'CrakRevenue, AdultForce, AWEmpire, TrafficJunky',
        'difficulty': 'Easy',
        'priority': 8
    },
    'tech-trials': {
        'keywords': ['trial', 'antivirus', 'vpn', 'cleaner', 'software', 'app', 'download', 'install', 'pc', 'security'],
        'value': '💰 MEDIUM ($0.50-10 CPA)',
        'offers': 'Free trials, antivirus, VPN, PC cleaners, software downloads',
        'networks': 'MaxBounty, CPAlead, AdWork Media, OGAds',
        'difficulty': 'Easy',
        'priority': 7
    },
    'mobile-apps': {
        'keywords': ['app', 'mobile', 'game', 'download', 'install', 'android', 'ios', 'play'],
        'value': '💰 MEDIUM ($0.50-5 CPI)',
        'offers': 'App installs, mobile games, utility apps',
        'networks': 'AppLovin, IronSource, Unity Ads, AdMob',
        'difficulty': 'Easy',
        'priority': 7
    },
    'education': {
        'keywords': ['edu', 'school', 'college', 'university', 'degree', 'online', 'course', 'learn', 'training', 'certification'],
        'value': '💰 HIGH ($10-150 CPA)',
        'offers': 'Online degrees, courses, certifications, student loans',
        'networks': 'QuinStreet, EduPath, Commission Junction',
        'difficulty': 'Medium',
        'priority': 7
    },
    'travel': {
        'keywords': ['travel', 'hotel', 'flight', 'vacation', 'booking', 'resort', 'cruise', 'trip', 'tour'],
        'value': '💰 MEDIUM ($5-50 CPA)',
        'offers': 'Hotel bookings, flights, vacation packages, travel insurance',
        'networks': 'Booking.com, Expedia, TravelPayouts',
        'difficulty': 'Medium',
        'priority': 6
    },
    'leadgen': {
        'keywords': ['quote', 'estimate', 'contact', 'inquiry', 'request', 'form', 'lead', 'call'],
        'value': '💰 MEDIUM ($2-50 CPL)',
        'offers': 'Lead generation (any vertical)',
        'networks': 'MaxBounty, Perform[cb], Aragon Advertising',
        'difficulty': 'Easy',
        'priority': 6
    },
    'ecommerce': {
        'keywords': ['shop', 'store', 'buy', 'product', 'retail', 'cart', 'sale', 'deal', 'coupon'],
        'value': '💸 LOW-MEDIUM (3-10% RevShare)',
        'offers': 'E-commerce products, general retail',
        'networks': 'ShareASale, CJ, Amazon Associates, Rakuten',
        'difficulty': 'Easy',
        'priority': 4
    },
    'crypto': {
        'keywords': ['crypto', 'bitcoin', 'btc', 'eth', 'blockchain', 'nft', 'defi', 'token', 'coin', 'web3'],
        'value': '💰 VERY HIGH ($50-500 CPA)',
        'offers': 'Crypto exchanges, wallets, trading platforms, NFT',
        'networks': 'Coinzilla, Bitmedia, Direct affiliate programs',
        'difficulty': 'Medium',
        'priority': 9
    },
    'utilities': {
        'keywords': ['electric', 'power', 'energy', 'solar', 'utility', 'phone', 'internet', 'cable', 'service'],
        'value': '💰 MEDIUM ($10-100 CPA)',
        'offers': 'Energy providers, solar, phone/internet comparison',
        'networks': 'QuinStreet, FlexOffers',
        'difficulty': 'Medium',
        'priority': 5
    },
    'general': {
        'keywords': [],  # Fallback
        'value': '❓ UNKNOWN',
        'offers': 'Depends on domain - check manually',
        'networks': 'Various',
        'difficulty': 'Unknown',
        'priority': 1
    }
}

# Country/Region TLD and domain patterns
REGION_PATTERNS = {
    # North America
    'USA': {
        'tlds': ['.us', '.gov', '.mil'],
        'patterns': ['usa', 'united-states', 'american', 'federal'],
        'continent': 'North America',
        'cpa_notes': 'Tier 1 - Highest payouts, strict compliance'
    },
    'Canada': {
        'tlds': ['.ca'],
        'patterns': ['canada', 'canadian', 'quebec', 'ontario'],
        'continent': 'North America',
        'cpa_notes': 'Tier 1 - High payouts, bilingual (EN/FR)'
    },
    # Europe
    'UK': {
        'tlds': ['.uk', '.co.uk', '.gov.uk', '.ac.uk'],
        'patterns': ['british', 'england', 'scotland', 'wales', 'uk-'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 1 - High payouts, strict regulations (GDPR)'
    },
    'Germany': {
        'tlds': ['.de'],
        'patterns': ['deutsch', 'germany', 'german', 'berlin'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 1 - High payouts, strict compliance'
    },
    'France': {
        'tlds': ['.fr'],
        'patterns': ['france', 'french', 'paris'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 1 - High payouts, French language required'
    },
    'Netherlands': {
        'tlds': ['.nl'],
        'patterns': ['dutch', 'netherlands', 'holland'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 1 - High payouts, liberal regulations'
    },
    'Spain': {
        'tlds': ['.es'],
        'patterns': ['spain', 'spanish', 'espana'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 2 - Medium-high payouts, Spanish required'
    },
    'Italy': {
        'tlds': ['.it'],
        'patterns': ['italy', 'italian', 'italia'],
        'continent': 'Europe',
        'cpa_notes': 'Tier 2 - Medium payouts, Italian required'
    },
    # Oceania
    'Australia': {
        'tlds': ['.au', '.com.au', '.gov.au', '.edu.au'],
        'patterns': ['australia', 'australian', 'aussie', 'sydney', 'melbourne'],
        'continent': 'Oceania',
        'cpa_notes': 'Tier 1 - High payouts, strict regulations'
    },
    'New Zealand': {
        'tlds': ['.nz', '.co.nz'],
        'patterns': ['newzealand', 'zealand', 'kiwi'],
        'continent': 'Oceania',
        'cpa_notes': 'Tier 1 - High payouts'
    },
    # Asia
    'Japan': {
        'tlds': ['.jp', '.co.jp'],
        'patterns': ['japan', 'japanese', 'tokyo'],
        'continent': 'Asia',
        'cpa_notes': 'Tier 1 - High payouts, Japanese language required'
    },
    'Singapore': {
        'tlds': ['.sg', '.com.sg'],
        'patterns': ['singapore', 'singapura'],
        'continent': 'Asia',
        'cpa_notes': 'Tier 1 - High payouts, English friendly'
    },
    'China': {
        'tlds': ['.cn', '.com.cn'],
        'patterns': ['china', 'chinese', 'beijing', 'shanghai'],
        'continent': 'Asia',
        'cpa_notes': 'Tier 2 - Special regulations, Chinese required'
    },
    'India': {
        'tlds': ['.in', '.co.in'],
        'patterns': ['india', 'indian', 'mumbai', 'delhi'],
        'continent': 'Asia',
        'cpa_notes': 'Tier 2 - Lower payouts, massive volume potential'
    },
    'South Korea': {
        'tlds': ['.kr', '.co.kr'],
        'patterns': ['korea', 'korean', 'seoul'],
        'continent': 'Asia',
        'cpa_notes': 'Tier 1 - High payouts, Korean required'
    },
    # Other
    'Brazil': {
        'tlds': ['.br', '.com.br'],
        'patterns': ['brazil', 'brazilian', 'brasil'],
        'continent': 'South America',
        'cpa_notes': 'Tier 2 - Medium payouts, Portuguese required'
    },
    'Russia': {
        'tlds': ['.ru', '.su'],
        'patterns': ['russia', 'russian', 'moscow'],
        'continent': 'Europe/Asia',
        'cpa_notes': 'Tier 2 - Special considerations, Russian required'
    },
    'International': {
        'tlds': ['.com', '.net', '.org', '.io', '.co'],
        'patterns': ['global', 'international', 'world'],
        'continent': 'Global',
        'cpa_notes': 'Global - Geo-target based on content/traffic'
    }
}

def detect_region(domain):
    """
    Detect the geographic region/country of a domain (SIMPLIFIED - No external API calls)

    Returns: (country, continent, cpa_notes, confidence)
    """
    domain_lower = domain.lower()

    # First check TLDs (most reliable)
    for country, data in REGION_PATTERNS.items():
        if country == 'International':
            continue

        for tld in data['tlds']:
            if domain_lower.endswith(tld):
                return (country, data['continent'], data['cpa_notes'], 95)

    # Then check patterns in domain name
    for country, data in REGION_PATTERNS.items():
        if country == 'International':
            continue

        for pattern in data['patterns']:
            if pattern in domain_lower:
                return (country, data['continent'], data['cpa_notes'], 75)

    # Default to International (removed slow IP geolocation)
    return ('International', 'Global', 'Geo-target based on content/traffic', 40)

def detect_niche(subdomain, parent_domain):
    """
    Detect the CPA vertical of a subdomain based on keywords

    Returns: (vertical, confidence, suggested_offers, cpa_value, networks, priority)
    """
    # Combine subdomain and domain for analysis
    full_text = f"{subdomain} {parent_domain}".lower()

    matches = []

    for vertical, data in CPA_VERTICALS.items():
        if vertical == 'general':
            continue

        keyword_matches = 0
        matched_keywords = []

        for keyword in data['keywords']:
            if keyword in full_text:
                keyword_matches += 1
                matched_keywords.append(keyword)

        if keyword_matches > 0:
            # Calculate confidence based on number of matches and priority
            base_confidence = min(95, keyword_matches * 25)
            # Boost confidence for high-priority verticals
            priority_boost = data.get('priority', 5) * 2
            confidence = min(100, base_confidence + priority_boost)

            matches.append({
                'vertical': vertical,
                'confidence': confidence,
                'matched_keywords': matched_keywords,
                'value': data['value'],
                'offers': data['offers'],
                'networks': data['networks'],
                'difficulty': data['difficulty'],
                'priority': data.get('priority', 5)
            })

    # Sort by priority first, then confidence
    matches.sort(key=lambda x: (x['priority'], x['confidence']), reverse=True)

    if matches:
        best = matches[0]
        return (
            best['vertical'].upper(),
            best['confidence'],
            best['offers'],
            best['value'],
            best['networks'],
            best['priority']
        )
    else:
        # Fallback to general
        return ('GENERAL', 50, 'Check domain manually', '❓ UNKNOWN', 'Various CPA networks', 1)

def analyze_domain_authority(parent_domain):
    """
    Estimate domain authority based on TLD and common patterns (SIMPLIFIED)
    Returns: estimated DA score (0-100)
    """
    # High authority TLDs
    high_authority = ['.gov', '.edu', '.mil']
    medium_authority = ['.org', '.com', '.net']

    # Check TLD
    for tld in high_authority:
        if parent_domain.endswith(tld):
            return 80  # High authority estimate

    for tld in medium_authority:
        if parent_domain.endswith(tld):
            # Domain length heuristic
            domain_name = parent_domain.split('.')[0]
            if len(domain_name) <= 8:  # Short domains tend to be more authoritative
                return 60
            else:
                return 45

    return 35  # Default low authority

def get_historical_content(subdomain):
    """
    Check for historical content indicators (SIMPLIFIED - no API calls)
    Returns: simple indicator based on subdomain name patterns
    """
    subdomain_lower = subdomain.lower()

    # Check for patterns that suggest old/archived content
    old_patterns = ['old', 'legacy', 'archive', 'backup', 'deprecated', 'v1', 'v2', 'v3', 'beta', 'staging']

    for pattern in old_patterns:
        if pattern in subdomain_lower:
            return f"Likely archived (contains '{pattern}')"

    return "No archive indicators"

def estimate_seo_value(subdomain, parent_domain, niche, domain_authority):
    """
    Estimate SEO value for affiliate marketing (SIMPLIFIED)
    domain_authority should now be a number 0-100
    Returns: Low/Medium/High/Very High
    """
    score = 0

    # Domain authority contribution (now expects numeric DA)
    if isinstance(domain_authority, int):
        if domain_authority >= 70:
            score += 40
        elif domain_authority >= 50:
            score += 30
        elif domain_authority >= 30:
            score += 20
        else:
            score += 10
    else:
        # Fallback for old string format
        if 'High' in str(domain_authority):
            score += 40
        elif 'Medium' in str(domain_authority):
            score += 20
        else:
            score += 10

    # Niche contribution
    high_value_niches = ['NUTRA', 'DATING', 'GAMBLING', 'FINANCE', 'INSURANCE', 'CRYPTO']
    if niche.upper() in high_value_niches:
        score += 30
    elif niche != 'GENERAL':
        score += 15

    # Subdomain length (shorter = better)
    subdomain_parts = subdomain.split('.')[0]
    if len(subdomain_parts) < 10:
        score += 20
    elif len(subdomain_parts) < 15:
        score += 10

    # Age indicator (if it's a common pattern like "old-", "legacy-", "archive-")
    old_patterns = ['old', 'legacy', 'archive', 'backup', 'deprecated', 'v1', 'v2']
    if any(pattern in subdomain.lower() for pattern in old_patterns):
        score += 10  # Likely has historical backlinks

    # Convert score to rating
    if score >= 70:
        return 'Very High'
    elif score >= 50:
        return 'High'
    elif score >= 30:
        return 'Medium'
    else:
        return 'Low'

def analyze_verified_results(input_csv, output_csv):
    """
    Analyze verified vulnerabilities and add niche information
    """
    if not Path(input_csv).exists():
        print(f"❌ Input file not found: {input_csv}")
        return

    # Create progress files
    progress_file = Path("niche_progress.txt")
    status_file = Path("niche_status.txt")

    progress_file.write_text("0")
    status_file.write_text("Starting niche analysis...")

    results = []

    print("🔍 Analyzing niches for verified vulnerabilities...")
    print("✓ Using simplified analysis (no external API dependencies)")

    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        original_rows = list(reader)

    total = len(original_rows)

    for idx, row in enumerate(original_rows, 1):
        subdomain = row.get('subdomain', '')
        service = row.get('service', '')
        cname = row.get('cname', '')
        status = row.get('status', '')

        # Update progress
        progress = int((idx / total) * 100)
        progress_file.write_text(str(progress))
        status_file.write_text(f"Analyzing {idx}/{total}: {subdomain}")

        # Extract parent domain
        parts = subdomain.split('.')
        if len(parts) >= 2:
            parent_domain = '.'.join(parts[-2:])
        else:
            parent_domain = subdomain

        print(f"[{idx}/{len(original_rows)}] Analyzing: {subdomain}")

        # Detect CPA vertical
        vertical, confidence, offers, cpa_value, networks, priority = detect_niche(subdomain, parent_domain)

        # Detect geographic region
        print(f"  → Detecting region for {parent_domain}...")
        region_country, region_continent, region_cpa_notes, region_confidence = detect_region(parent_domain)

        # Estimate domain authority (simplified, no external API)
        print(f"  → Estimating domain authority...")
        actual_da = analyze_domain_authority(parent_domain)

        # Estimate backlinks based on DA (heuristic)
        if actual_da >= 70:
            actual_backlinks = 5000
            linking_domains = 500
            domain_authority = f'High ({actual_da}/100)'
        elif actual_da >= 50:
            actual_backlinks = 1000
            linking_domains = 100
            domain_authority = f'Medium-High ({actual_da}/100)'
        elif actual_da >= 30:
            actual_backlinks = 100
            linking_domains = 20
            domain_authority = f'Medium ({actual_da}/100)'
        else:
            actual_backlinks = 10
            linking_domains = 5
            domain_authority = f'Low ({actual_da}/100)'

        spam_score = 0  # Default to 0 (can't check without API)
        dr_source = 'Estimated'

        # Get historical content
        historical = get_historical_content(subdomain)

        # Estimate SEO value
        seo_value = estimate_seo_value(subdomain, parent_domain, vertical, actual_da)

        # Build result
        result = {
            'subdomain': subdomain,
            'parent_domain': parent_domain,
            'service': service,
            'cname': cname,
            'status': status,
            'region_country': region_country,
            'region_continent': region_continent,
            'region_cpa_notes': region_cpa_notes,
            'region_confidence': f"{region_confidence}%",
            'cpa_vertical': vertical,
            'vertical_confidence': f"{confidence}%",
            'cpa_offers': offers,
            'cpa_value': cpa_value,
            'cpa_networks': networks,
            'priority_score': priority,
            'domain_authority': domain_authority,
            'actual_da': actual_da,
            'total_backlinks': actual_backlinks,
            'linking_domains': linking_domains,
            'spam_score': spam_score,
            'dr_source': dr_source,
            'seo_value': seo_value,
            'historical_content': historical,
        }

        results.append(result)

    # Calculate trust/priority scores for each result
    for result in results:
        # Trust Score (0-100) based on multiple factors
        trust_score = 0

        # DA contribution (max 40 points)
        da = result.get('actual_da', 0)
        trust_score += min(40, da * 0.4)

        # Backlinks contribution (max 30 points)
        backlinks = result.get('total_backlinks', 0)
        if backlinks >= 10000:
            trust_score += 30
        elif backlinks >= 1000:
            trust_score += 20
        elif backlinks >= 100:
            trust_score += 10
        elif backlinks >= 10:
            trust_score += 5

        # Niche value contribution (max 20 points)
        high_value_niches = ['FINANCE', 'NUTRA', 'GAMBLING', 'INSURANCE', 'DATING', 'CRYPTO']
        vertical = result.get('cpa_vertical', 'GENERAL').upper()
        if vertical in high_value_niches:
            trust_score += 20
        elif vertical != 'GENERAL':
            trust_score += 10

        # Spam score penalty (max -10 points)
        spam = result.get('spam_score', 0)
        trust_score -= min(10, spam * 0.1)

        # SEO value boost (max 10 points)
        if result['seo_value'] == 'Very High':
            trust_score += 10
        elif result['seo_value'] == 'High':
            trust_score += 5

        result['trust_score'] = max(0, min(100, int(trust_score)))
        result['priority_rank'] = 0  # Will be set after sorting

    # Sort by trust score (highest first)
    results_sorted = sorted(results, key=lambda x: (
        x['trust_score'],
        x.get('actual_da', 0),
        x.get('total_backlinks', 0)
    ), reverse=True)

    # Assign priority ranks
    for idx, result in enumerate(results_sorted, 1):
        result['priority_rank'] = idx

    # Write to CSV (sorted by priority)
    if results_sorted:
        fieldnames = [
            'priority_rank', 'trust_score', 'subdomain', 'parent_domain', 'service', 'cname', 'status',
            'region_country', 'region_continent', 'region_cpa_notes', 'region_confidence',
            'cpa_vertical', 'vertical_confidence', 'cpa_offers', 'cpa_value', 'cpa_networks', 'priority_score',
            'domain_authority', 'actual_da', 'total_backlinks', 'linking_domains',
            'spam_score', 'dr_source', 'seo_value', 'historical_content'
        ]

        with open(output_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results_sorted)

        # Also create a "top targets" CSV with only high-value results
        desktop = Path.home() / "Desktop"
        niche_folder = desktop / "Subdomain_Takeover_Results" / "Niche_Analysis"
        niche_folder.mkdir(parents=True, exist_ok=True)
        top_targets_csv = niche_folder / "top_priority_targets.csv"

        high_priority = [r for r in results_sorted if r['trust_score'] >= 60]
        if high_priority:
            with open(top_targets_csv, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(high_priority)
            print(f"🎯 High-priority targets saved to: {top_targets_csv}")

        print(f"\n✅ Niche analysis complete!")
        print(f"📊 Results saved to: {output_csv}")
        if high_priority:
            print(f"🎯 Top priority targets saved to: {top_targets_csv}")

        print(f"\n📈 Summary:")

        # Print summary statistics
        niche_counts = {}
        for r in results_sorted:
            niche = r.get('cpa_vertical', 'UNKNOWN')
            niche_counts[niche] = niche_counts.get(niche, 0) + 1

        print("\nNiche Distribution:")
        for niche, count in sorted(niche_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {niche}: {count}")

        # Trust score distribution
        high_trust = [r for r in results_sorted if r['trust_score'] >= 80]
        medium_trust = [r for r in results_sorted if 60 <= r['trust_score'] < 80]
        low_trust = [r for r in results_sorted if r['trust_score'] < 60]

        print(f"\n🎯 Trust Score Distribution:")
        print(f"  High Trust (80-100): {len(high_trust)}")
        print(f"  Medium Trust (60-79): {len(medium_trust)}")
        print(f"  Low Trust (0-59): {len(low_trust)}")

        # Top 10 by priority
        print(f"\n🏆 TOP 10 PRIORITY TARGETS (by Trust Score):")
        print("="*100)
        for i, r in enumerate(results_sorted[:10], 1):
            da = r.get('actual_da', 0)
            backlinks = r.get('total_backlinks', 0)
            trust = r['trust_score']
            print(f"  #{i} [Trust: {trust}/100] {r['subdomain']}")
            print(f"      Service: {r['service']} | Niche: {r.get('cpa_vertical', 'UNKNOWN')} | DA: {da}/100 | Backlinks: {backlinks:,}")
            print(f"      Value: {r.get('cpa_value', 'Unknown')} | SEO: {r['seo_value']}")
            print()

    else:
        print("❌ No results to analyze")

    # Clean up progress files
    progress_file = Path("niche_progress.txt")
    status_file = Path("niche_status.txt")
    if progress_file.exists():
        progress_file.unlink()
    if status_file.exists():
        status_file.unlink()

if __name__ == "__main__":
    import sys

    # Default paths
    desktop = Path.home() / "Desktop"
    results_folder = desktop / "Subdomain_Takeover_Results"
    verified_folder = results_folder / "Verified_Vulnerabilities"
    niche_folder = results_folder / "Niche_Analysis"

    # Create folders if they don't exist
    for folder in [results_folder, verified_folder, niche_folder]:
        folder.mkdir(parents=True, exist_ok=True)

    input_file = verified_folder / "verified_vulnerabilities.csv"
    output_file = niche_folder / "niche_analysis.csv"

    # Allow custom input/output
    if len(sys.argv) > 1:
        input_file = Path(sys.argv[1])
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])

    analyze_verified_results(input_file, output_file)
