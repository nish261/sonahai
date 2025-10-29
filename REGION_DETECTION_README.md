# 🌍 Geographic Region Detection

## Overview
The subdomain takeover scanner now includes **automatic geographic region detection** for all vulnerable subdomains. This helps you target region-specific CPA offers and understand the geographic distribution of your findings.

## Features

### 1. **Automatic Region Detection**
Each subdomain is analyzed to determine its geographic location using:
- **TLD Analysis** (95% confidence): `.us`, `.au`, `.uk`, `.de`, etc.
- **Domain Pattern Matching** (75% confidence): Keywords like "australia", "canada", etc.
- **IP Geolocation** (60% confidence): For generic TLDs like `.com`, `.net`

### 2. **Supported Regions**

#### Tier 1 Countries (Highest CPA Payouts)
- 🇺🇸 USA - Highest payouts, strict compliance
- 🇨🇦 Canada - High payouts, bilingual (EN/FR)
- 🇬🇧 UK - High payouts, GDPR compliance
- 🇩🇪 Germany - High payouts, strict compliance  
- 🇫🇷 France - High payouts, French required
- 🇳🇱 Netherlands - High payouts, liberal regulations
- 🇦🇺 Australia - High payouts, strict regulations
- 🇳🇿 New Zealand - High payouts
- 🇯🇵 Japan - High payouts, Japanese required
- 🇸🇬 Singapore - High payouts, English friendly
- 🇰🇷 South Korea - High payouts, Korean required

#### Tier 2 Countries (Medium Payouts)
- 🇪🇸 Spain - Medium-high payouts, Spanish required
- 🇮🇹 Italy - Medium payouts, Italian required
- 🇧🇷 Brazil - Medium payouts, Portuguese required
- 🇨🇳 China - Special regulations, Chinese required
- 🇮🇳 India - Lower payouts, massive volume potential
- 🇷🇺 Russia - Special considerations, Russian required

### 3. **CSV Columns Added**
- `region_country`: Country name (e.g., "USA", "Australia")
- `region_continent`: Continent (e.g., "North America", "Oceania")
- `region_cpa_notes`: Region-specific CPA marketing notes
- `region_confidence`: Detection confidence percentage

### 4. **UI Features**
- **Filter by Region**: Dropdown to show only specific countries
- **Geographic Distribution Stats**: See breakdown by country and continent
- **CPA Notes**: Region-specific marketing guidance in the CSV

## Usage Example

After running niche analysis, you'll see:

```csv
subdomain,region_country,region_continent,region_cpa_notes,trust_score
app.example.com,USA,North America,"Tier 1 - Highest payouts, strict compliance",85
shop.example.com.au,Australia,Oceania,"Tier 1 - High payouts, strict regulations",78
```

## Filtering in UI

1. Run a subdomain scan
2. Run niche analysis
3. In results table, use the **"Filter by Region"** dropdown
4. Select specific country (e.g., "USA", "Australia")
5. View only domains from that region

## CPA Marketing Strategy by Region

### USA 🇺🇸
- **Best Niches**: Finance, Insurance, Health, Dating, Gambling
- **Networks**: MaxBounty, Perform[cb], A4D
- **Notes**: Highest payouts but strict FTC compliance required

### Australia 🇦🇺  
- **Best Niches**: Gambling, Finance, Dating, Insurance
- **Networks**: MaxBounty, CPA networks with AU offers
- **Notes**: High payouts, English-speaking, strict ACCC regulations

### UK 🇬🇧
- **Best Niches**: Gambling, Finance, Dating
- **Networks**: European CPA networks
- **Notes**: GDPR compliance required, high payouts

### International (.com/.net)
- **Strategy**: Geo-target campaigns based on actual traffic
- **Notes**: Use analytics to determine visitor location

## Technical Details

The detection logic is in `niche_analyzer.py`:
- Uses `REGION_PATTERNS` dictionary for TLD/pattern matching
- Falls back to `ipapi.co` for IP-based geolocation
- Cached results to avoid repeated API calls

## Benefits

1. **Target Region-Specific Offers**: Show US dating offers to US domains
2. **Compliance Planning**: Know which regulations apply (GDPR, FTC, etc.)
3. **Language Requirements**: Identify domains requiring specific languages
4. **Payout Optimization**: Focus on Tier 1 countries for maximum revenue
5. **Volume vs. Quality**: Balance high-payout regions vs. high-volume regions
