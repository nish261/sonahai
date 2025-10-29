# 🌍 Country Filter - Quick Guide

## What This Does
Filters your subdomain scan to **ONLY find domains from specific countries** based on their TLD (Top-Level Domain).

## How to Use

### Step 1: Open Scanner UI
Your scanner is already running at: http://localhost:8501

### Step 2: Enable Country Filter
1. In the left sidebar, find **"🌍 Country/Region Filter"**
2. Check the box: **"Filter by country/region"**
3. Select countries from the dropdown (multi-select)

### Step 3: Choose Countries
**Default:** USA, Australia

**Available Countries:**
- 🇺🇸 USA (.us, .gov, .mil)
- 🇦🇺 Australia (.au, .com.au, .gov.au, .edu.au)
- 🇬🇧 UK (.uk, .co.uk, .gov.uk, .ac.uk)
- 🇨🇦 Canada (.ca)
- 🇩🇪 Germany (.de)
- 🇫🇷 France (.fr)
- 🇳🇱 Netherlands (.nl)
- 🇪🇸 Spain (.es)
- 🇮🇹 Italy (.it)
- 🇯🇵 Japan (.jp, .co.jp)
- 🇨🇳 China (.cn, .com.cn)
- 🇮🇳 India (.in, .co.in)
- 🇧🇷 Brazil (.br, .com.br)
- 🇷🇺 Russia (.ru)
- 🇸🇬 Singapore (.sg, .com.sg)
- 🇳🇿 New Zealand (.nz, .co.nz)
- 🇰🇷 South Korea (.kr, .co.kr)

### Step 4: Run Scan
Click **"🎯 Run Complete Scan"** or **"🔍 Scan Only"**

The scanner will **ONLY** find subdomains ending with the selected country TLDs.

## Example

### Filter for USA Only:
```
✅ Selected: USA (.us, .gov, .mil)

Will scan:
- example.us ✓
- test.gov ✓
- subdomain.mil ✓

Will skip:
- example.com ✗
- test.au ✗
- site.uk ✗
```

### Filter for USA + Australia:
```
✅ Selected: USA, Australia

Will scan:
- example.us ✓
- test.gov ✓
- site.com.au ✓
- app.au ✓

Will skip:
- example.com ✗
- test.uk ✗
```

## Why Use This?

### 1. **Target High-Value Countries**
USA and Australia = highest CPA payouts
- Dating: $30-150 CPA
- Finance: $50-500 CPA
- Gambling: $100-1000+ CPA

### 2. **Language Targeting**
- USA/UK/Australia = English (easy)
- Germany = German required
- Japan = Japanese required

### 3. **Legal Compliance**
- USA = FTC compliance
- EU = GDPR compliance
- Different countries = different rules

### 4. **Faster Scans**
Fewer domains to scan = faster results

## Priority Order

If you enable BOTH filters:
1. **Country Filter** (wins)
2. Extension Filter
3. All domains

Country filter overrides extension filter!

## Pro Tips

### Best for USA Money 💰
Select: **USA only**
- Highest payouts
- English language
- Huge market

### Best for English Markets 🌏
Select: **USA, UK, Australia, Canada**
- All English-speaking
- Tier 1 countries
- No translation needed

### Best for Volume 📈
Select: **All countries**
- Maximum domains
- Diverse geo-targeting
- More opportunities

### Best for Gambling 🎰
Select: **UK, Australia, Netherlands**
- Liberal gambling laws
- High payouts
- Less restrictions

## Common Combos

```
🇺🇸 USA Only
└─ Best for: Max payouts, FTC compliance training

🇺🇸🇦🇺 USA + Australia  
└─ Best for: English markets, high value

🇺🇸🇬🇧🇦🇺🇨🇦 English Tier 1
└─ Best for: No translation needed, all Tier 1

🇪🇸🇮🇹🇫🇷 European Mix
└─ Best for: GDPR compliance, EU targeting
```

## After Scan

When you run **Niche Analysis**, you'll also get:
- Geographic distribution stats
- CPA notes per region
- Region-specific filtering in results

Now you can focus on the countries that pay the most! 💰
