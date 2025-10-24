# 🎯 Subdomain Takeover Scanner - Main Menu

## Quick Navigation

- [🚀 Current Scan Status](#current-scan-status)
- [📖 How to Use](#how-to-use)
- [📊 What's Being Detected](#whats-being-detected)
- [📁 Results & Output](#results--output)
- [🔧 Troubleshooting](#troubleshooting)
- [📚 Documentation](#documentation)

---

## 🚀 Current Scan Status

### Check Scanner Status
```bash
# Progress percentage
cat scan_progress.txt

# Recent activity (last 20 lines)
tail -20 scan_status.txt

# Is scanner running?
ps aux | grep aggressive_scanner | grep -v grep
```

### Live Monitoring
```bash
# Watch in real-time (updates every 5 seconds)
./monitor_scan.sh

# Or manually watch logs
tail -f scan_status.txt
```

---

## 📖 How to Use

### Run Scanner (3 Simple Ways)

#### 1. **Quick Scan** (Top 1000 domains)
```bash
python3 aggressive_scanner.py 1 1000
```

#### 2. **Better Results** (Lower-ranked domains, more vulnerabilities)
```bash
python3 aggressive_scanner.py 5000 1000
```

#### 3. **Quick Test** (100 domains only)
```bash
python3 aggressive_scanner.py 1 100
```

### Advanced Options

**Filter by Domain Extension:**
```bash
# Only .gov and .edu domains
python3 aggressive_scanner.py 1 1000 ".gov,.edu"
```

**Faster Scanning (More Workers):**
```bash
# 20 enumeration + 50 scan workers
python3 aggressive_scanner.py 1 1000 ALL 20 50
```

**Run in Background:**
```bash
# Keeps running even if you close terminal
nohup python3 aggressive_scanner.py 1 1000 > scanner.log 2>&1 &
```

---

## 📊 What's Being Detected

### ✅ Vulnerable Services (43 Total)

Scanner detects vulnerabilities from the **official can-i-take-over-xyz list**:

**Cloud Providers (4)**
- AWS S3
- AWS Elastic Beanstalk  
- Microsoft Azure (all services)
- Digital Ocean

**Development Platforms (6)**
- GitHub, Bitbucket
- JetBrains, Ngrok
- Pantheon, Readthedocs

**CMS/Blogging (4)**
- Ghost, Wordpress
- HatenaBlog, Worksites

**Marketing/Landing Pages (5)**
- LaunchRock, Smugsmug
- Strikingly, Surge.sh, Uberflip

**Support/Help Desk (6)**
- Cargo Collective, Help Juice
- Help Scout, Helprace
- Pingdom, Readme.io

**Business/CRM (8)**
- Agile CRM, Campaign Monitor
- Canny, Gemfury, Getresponse
- SmartJobBoard, SurveySparrow
- Uptimerobot

**Other Services (4)**
- Airee.ru, Anima
- Discourse, Short.io

### ❌ Excluded (NOT Vulnerable)

These are **automatically filtered out**:

**CDNs (Not vulnerable)**
- Fastly, CloudFront, Cloudflare, Akamai

**Fixed by Vendors**
- Unbounce, Instapage, Statuspage
- UserVoice, Zendesk

**Never Vulnerable**
- Firebase, Gitlab, Kinsta
- And 20+ others

---

## 📁 Results & Output

### Where Results Are Saved

```
~/Desktop/Subdomain_Takeover_Results/Scans/
├── subdomain_takeover_detailed.csv   ← All vulnerabilities
└── subdomain_takeover_results.txt    ← Summary report
```

### View Results

**Count vulnerabilities found:**
```bash
wc -l ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

**View all results:**
```bash
cat ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

**View summary:**
```bash
cat ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_results.txt
```

**Filter by service (e.g., only AWS):**
```bash
grep "AWS" ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

---

## 🔧 Troubleshooting

### Scanner Not Running?

**Check if it's actually running:**
```bash
ps aux | grep aggressive_scanner | grep -v grep
```

**Start it:**
```bash
python3 aggressive_scanner.py 1 1000
```

### "Module not found" Error?

**Install dependencies:**
```bash
pip3 install --break-system-packages tranco requests
```

### Scanner Too Slow?

**Increase workers:**
```bash
# Default: 10 enum, 30 scan
# Faster: 20 enum, 50 scan
python3 aggressive_scanner.py 1 1000 ALL 20 50
```

### No Results Found?

**Try these:**
1. Scan lower-ranked domains (more vulnerabilities):
   ```bash
   python3 aggressive_scanner.py 5000 1000
   ```

2. Increase domain count:
   ```bash
   python3 aggressive_scanner.py 1 2000
   ```

3. Check scan status for errors:
   ```bash
   tail -50 scan_status.txt
   ```

### Stop Scanner

**Find and kill process:**
```bash
# Find PID
ps aux | grep aggressive_scanner

# Kill it (replace XXXX with PID)
kill XXXX
```

---

## 📚 Documentation

### Complete Guides

1. **RUN_SCANNER.md** - Detailed terminal usage guide
2. **SCANNER_UPDATE_SUMMARY.md** - What changed in latest update
3. **SCAN_RUNNING.md** - Current scan status and monitoring

### View Guides
```bash
cat RUN_SCANNER.md                # How to run scanner
cat SCANNER_UPDATE_SUMMARY.md    # Latest changes
cat SCAN_RUNNING.md              # Current scan info
```

---

## 🎓 Scanner Workflow

```
1. ENUMERATION (15-50%)
   └─ Finds all subdomains using subfinder
   
2. SCANNING (50-95%)
   └─ Uses Subdominator to check for vulnerabilities
   
3. FILTERING (95-100%)
   └─ Removes false positives
   └─ Matches against can-i-take-over-xyz list
   
4. SAVE RESULTS (100%)
   └─ Saves to Desktop
   └─ Creates CSV and TXT reports
```

---

## 💡 Pro Tips

1. **Lower-ranked domains** (5000-15000) have MORE vulnerabilities
2. **Run overnight** - Scanning 1000 domains takes 45-90 minutes  
3. **Use background mode** for long scans
4. **Check Desktop folder** for results when complete
5. **Review CSV file** for easy sorting and filtering

---

## 📞 Need Help?

Check these files:
- **TROUBLESHOOTING.md** - Common issues
- **RUN_SCANNER.md** - Usage examples
- **scan_status.txt** - Current scan logs

---

**Last Updated:** October 24, 2024  
**Source:** https://github.com/EdOverflow/can-i-take-over-xyz
