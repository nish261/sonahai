# 🔍 Subdomain Takeover Scanner - 24/7 Automated PoC Generator

Automated subdomain takeover detection and PoC generation system designed to find and claim 10-100 vulnerabilities per day.

## 🚀 Quick Start (24/7 Laptop Setup)

### On Your New Laptop:

```bash
# 1. Clone the repo
git clone https://github.com/nish261/subdomain-takeover-scanner.git
cd subdomain-takeover-scanner

# 2. Run automated setup (installs everything)
./24_7_setup.sh

# 3. Edit your credentials
nano account_details.json

# 4. Start automated scanning
./run_24_7.sh
```

That's it! The scanner will now run every 6 hours automatically.

---

## 📊 What You Get

### Automated Output (Every 6 Hours):
- ✅ **Vulnerability Scans**: 1000 domains per cycle (starting from rank 500)
- ✅ **Auto-Claiming**: High-value S3/Azure/AWS/WordPress targets claimed automatically
- ✅ **PoC Generation**: Professional reports with screenshots
- ✅ **Niche Analysis**: SEO metrics, CPA estimates, monetization potential
- ✅ **Notifications**: Email/Slack alerts on successful claims

### Results Location:
```
~/Desktop/Subdomain_Takeover_Results/
├── Scans/                          # Raw scan results
├── Verified_Vulnerabilities/       # Confirmed takeovers
├── Niche_Analysis/                 # SEO/CPA analysis
└── PoC_Files/                      # Generated PoCs
```

---

## 🎯 Goal: 10-100 PoCs Per Day

### How It Works:

**Every 6 hours, the scanner automatically:**

1. **Discovers Subdomains** (subfinder, chaos)
2. **Detects Vulnerabilities** (nuclei, custom fingerprints)
3. **Verifies Takeovers** (DNS + HTTP validation)
4. **Analyzes Value** (domain authority, SEO, CPA niche)
5. **Auto-Claims** (S3, Azure, AWS Elastic Beanstalk)
6. **Generates PoCs** (PDF reports with screenshots)
7. **Sends Notifications** (email/Slack on success)

### Expected Output:
- **Low activity days**: 10-20 PoCs
- **Normal days**: 30-50 PoCs
- **High activity days**: 70-100+ PoCs

---

## 🛠️ Manual Control (Web UI)

If you want manual control instead of automation:

```bash
streamlit run simple_scanner_ui.py
```

Opens web interface at `http://localhost:8501`

### Features:
- Configure scan parameters
- View real-time progress
- Filter by trust score, niche, service type
- Manual PoC generation
- Download results as CSV

---

## ⚙️ Configuration

### 1. Credentials (`account_details.json`)

```json
{
  "aws": [
    {
      "name": "AWS Account 1",
      "access_key": "AKIAXXXXXXXXXXXXXXXX",
      "secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "region": "us-east-1"
    }
  ],
  "azure": [
    {
      "name": "Azure Account 1",
      "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "client_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "client_secret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    }
  ],
  "wordpress": {
    "email": "your-wordpress-email@example.com",
    "password": "your-wordpress-password"
  },
  "notifications": {
    "email": "your-email@example.com",
    "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
```

### 2. Scan Parameters (`complete_pipeline.py`)

Edit these for your needs:

```python
--batch-size 100          # Domains per scan cycle
--auto-claim              # Enable auto-claiming
--min-trust-score 70      # Minimum quality score (1-10)
--tlds "com,net,org"      # Target TLDs
--services "s3,azure,eb"  # Services to target
```

---

## 📋 Components

### Core Scanners:
- `aggressive_scanner.py` - Fast bulk scanning engine
- `complete_pipeline.py` - Full automation pipeline
- `automated_nightly_scanner.py` - Scheduled scanning

### Auto-Claimers:
- `auto_poc_claimer.py` - Universal auto-claimer (S3, Azure, GitHub, WordPress)
- `aws_eb_auto_claimer.py` - AWS Elastic Beanstalk
- `azure_auto_claimer.py` - Azure services (Storage, Apps, etc.)

### Analysis Tools:
- `niche_analyzer.py` - SEO/CPA niche analysis
- `authority_analyzer.py` - Domain authority scoring
- `seo_scorer.py` - SEO metrics evaluation
- `verify_results.py` - Vulnerability verification

### PoC Generators:
- `poc_generators.py` - Automated PoC creation
- `generate_poc_pdf.py` - PDF report generation

### Utilities:
- `credentials_manager.py` - Unified credential system
- `notification_helper.py` - Email/Slack alerts
- `fetch_vulnerable_subdomains.py` - Vulnerability discovery

---

## 🔄 Automation Schedule

### Default (Every 6 Hours):
```
00:00 - Scan cycle 1
06:00 - Scan cycle 2
12:00 - Scan cycle 3
18:00 - Scan cycle 4
```

### Customize Schedule:

Edit crontab:
```bash
crontab -e
```

Examples:
- Every 4 hours: `0 */4 * * *`
- Every 2 hours: `0 */2 * * *`
- Once daily at 2am: `0 2 * * *`

---

## 📈 Monitoring

### View Live Logs:
```bash
tail -f ~/Desktop/Subdomain_Takeover_Results/scanner.log
```

### Check Cron Job Status:
```bash
crontab -l  # List active cron jobs
```

### View Recent Results:
```bash
# Latest vulnerabilities
cat ~/Desktop/Subdomain_Takeover_Results/Verified_Vulnerabilities/verified_vulnerabilities.txt

# Niche analysis
open ~/Desktop/Subdomain_Takeover_Results/Niche_Analysis/niche_analysis.csv
```

---

## 🎛️ Advanced Usage

### Run Manual Scan:
```bash
# Scan 1000 domains starting from rank 500
python3 aggressive_scanner.py 500 1000 "com,net,org" 20 10
```

### Generate PoC for Specific Domain:
```bash
python3 poc_generators.py vulnerable-subdomain.example.com s3
```

### Analyze Specific Niche:
```bash
python3 niche_analyzer.py ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

### Test Auto-Claiming:
```bash
python3 auto_poc_claimer.py --test-mode
```

---

## 🔧 Troubleshooting

### Scanner Not Running Automatically:
```bash
# Check if cron job exists
crontab -l

# Check logs for errors
tail -50 ~/Desktop/Subdomain_Takeover_Results/scanner.log

# Manually run to see errors
./run_24_7.sh
```

### No Results Found:
- Check internet connection
- Verify subfinder/nuclei are installed: `which subfinder nuclei`
- Try broader TLDs: `.com,.net,.org,.io,.app`
- Increase batch size in `complete_pipeline.py`

### Auto-Claiming Failing:
- Verify credentials in `account_details.json`
- Check AWS/Azure permissions
- Review logs for specific errors

### Dependencies Missing:
```bash
# Re-run setup
./24_7_setup.sh

# Or install manually
./install_scanner_deps.sh
```

---

## 📞 Support

### Logs Location:
- Main log: `~/Desktop/Subdomain_Takeover_Results/scanner.log`
- Scan progress: `scan_progress.txt`, `scan_status.txt`
- Verification: `verify_progress.txt`, `verify_status.txt`
- Niche analysis: `niche_progress.txt`, `niche_status.txt`

### Debug Mode:
```bash
# Run with verbose output
python3 complete_pipeline.py --debug --verbose
```

---

## 🚨 Important Notes

### Security:
- **Never commit `account_details.json`** - contains credentials
- Use least-privilege AWS/Azure accounts
- Rotate credentials regularly

### Ethical Use:
- Only claim abandoned/unused services
- Document all findings professionally
- Follow responsible disclosure practices

### Rate Limiting:
- Scanner respects rate limits
- Uses delays between requests
- Rotates user agents
- If blocked, add proxy in credentials manager

---

## 📦 Dependencies

### System Requirements:
- Python 3.7+
- Go 1.16+
- 2GB+ RAM
- 10GB+ storage

### Key Tools:
- subfinder - subdomain enumeration
- nuclei - vulnerability scanning
- httpx - HTTP probing
- dnsx - DNS resolution

### Python Packages:
- streamlit - web UI
- pandas - data processing
- requests - HTTP client
- dnspython - DNS queries
- boto3 - AWS SDK
- azure-identity - Azure SDK
- selenium - browser automation

---

## 🎯 Pro Tips

### Maximize PoC Output:

1. **Use Multiple Accounts**
   - Add 3-5 AWS accounts
   - Add 3-5 Azure subscriptions
   - Increases claiming success rate

2. **Target High-Value TLDs**
   - `.com, .net, .org` - highest value
   - `.io, .app, .dev` - tech startups
   - `.co, .ai` - premium domains

3. **Optimize Schedule**
   - Run every 2-4 hours for max coverage
   - Stagger scans across different TLDs

4. **Focus on High Trust Scores**
   - Set `--min-trust-score 80` for best quality
   - Lower to 60 for more quantity

5. **Enable All Notifications**
   - Get instant alerts on claims
   - Track success rate in real-time

---

## 📝 License

This tool is for educational and authorized security testing only. Use responsibly.

---

## 🔗 Repository

https://github.com/nish261/subdomain-takeover-scanner

For updates, issues, and contributions.
