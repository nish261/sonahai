# Subdomain Takeover Scanner

**Bug Bounty Tool** - Find dangling DNS and unclaimed cloud resources

## 🚀 New Hybrid Architecture

### Workflow

```
Tranco Top Domains
        ↓
    Subfinder (Enumeration)
        ↓
   Subdominator (Validation) ← 8x faster, 97 fingerprints
        OR
   Python + dig (Fallback) ← Works without Subdominator
        ↓
     Results
```

## ⚙️ Scanner Engines

### Option 1: Subdominator (Recommended)
- **Speed:** 8x faster (~2-3 min vs ~20 min)
- **Fingerprints:** 97 services
- **Accuracy:** Recursive DNS + auto-validation
- **False Positives:** Much lower

### Option 2: Python + dig (Fallback)
- **Speed:** Standard (~20 min for 1000 domains)
- **Fingerprints:** 68 services
- **Accuracy:** Basic CNAME checks
- **False Positives:** Higher

## 📦 Installation

### Quick Start (Uses Python scanner)
```bash
# Start the app
streamlit run simple_scanner_ui.py
```

### Install Subdominator (8x speed boost)
```bash
# Option A: Use install script
chmod +x install_scanner_deps.sh
./install_scanner_deps.sh

# Option B: Manual install
# 1. Install .NET SDK 9.0
curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0
export PATH="$HOME/.dotnet:$PATH"

# 2. Build Subdominator
cd ~/Subdominator/Subdominator
~/.dotnet/dotnet publish -c Release -r osx-arm64 --self-contained -o ~/subdominator-bin

# 3. Create symlink
ln -sf ~/subdominator-bin/Subdominator ~/subdominator
```

## 🎯 Usage

1. **Start the app:**
   ```bash
   streamlit run simple_scanner_ui.py
   ```

2. **Configure scan settings:**
   - Start Rank (e.g., 5000)
   - Number of Domains (e.g., 100)
   - Optional: Filter by extension (.com, .io, etc.)

3. **Run scan:**
   - Click "🎯 Run Complete Scan" for full pipeline
   - Or "🔍 Scan Only" for just vulnerability detection

4. **Review results:**
   - View in UI
   - Download TXT/CSV reports
   - Generate PoCs for verified vulnerabilities

## 🔧 Scanner Detection

The app automatically detects which scanner engine to use:

- ✅ **Subdominator found** → Uses Subdominator (fast)
- ⚠️ **Subdominator not found** → Falls back to Python + dig (works but slower)

## 📊 Features

- **Subdomain Enumeration:** Uses subfinder to discover subdomains
- **Takeover Detection:** Checks for dangling DNS and unclaimed services
- **Deep Verification:** HTTP signature matching for high-confidence results
- **Niche Analysis:** Identifies affiliate marketing value
- **PoC Generation:** Auto-generates proof-of-concept for AWS, Azure, GitHub, Heroku
- **Extension Filtering:** Filter subdomains by TLD (.com, .io, etc.)

## 🐛 Supported Services

**Current (Python scanner):** 68 services including:
- AWS S3, Elastic Beanstalk
- Azure (App Service, Blob, CDN, etc.)
- GitHub Pages, Heroku, Shopify, WordPress
- DigitalOcean, Tumblr, Bitbucket, etc.

**With Subdominator:** 97 services (all of the above + 29 more)

## 📁 Output Files

Results saved to `~/Desktop/Subdomain_Takeover_Results/`:
- `Scans/subdomain_takeover_results.txt` - Text report
- `Scans/subdomain_takeover_detailed.csv` - CSV export
- `Verified_Vulnerabilities/` - High-confidence takeovers
- `Niche_Analysis/` - Affiliate marketing value
- `PoC_Files/` - Proof-of-concept HTML/commands

## 🔑 Credentials

Configure platform credentials in the sidebar for PoC generation:
- AWS (Access Key, Secret Key)
- Azure (Username, Password, Subscription)
- GitHub (Token)
- Heroku (API Key)
- And more...

## 🎯 Workflow Stages

1. **Scan:** Find vulnerable subdomains
2. **Verify:** Deep HTTP signature validation
3. **Analyze:** Assess affiliate marketing value
4. **Generate PoC:** Create exploitation proof

## 🚨 Ethical Use

This tool is for **authorized security testing only**:
- Bug bounty programs
- Authorized penetration testing
- Your own infrastructure

**Do not use on systems you don't have permission to test.**

## 📝 License

See LICENSE.md
