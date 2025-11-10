# 🚀 Setup on New Laptop - Quick Reference

## For Your 24/7 Laptop

### Step 1: Clone Repository
```bash
git clone https://github.com/nish261/subdomain-takeover-scanner.git
cd subdomain-takeover-scanner
```

### Step 2: Run Automated Setup
```bash
./24_7_setup.sh
```

This will:
- ✅ Install Python, Go, subfinder, nuclei, httpx, dnsx
- ✅ Install all Python dependencies
- ✅ Create output directories on Desktop
- ✅ Set up cron job (runs every 6 hours)
- ✅ Create credentials template

### Step 3: Add Your Credentials
```bash
nano account_details.json
```

Add your:
- AWS access keys (for S3/Elastic Beanstalk claiming)
- Azure credentials (for Azure claiming)
- Email/Slack webhook (for notifications)

### Step 4: Start First Run (Test)
```bash
./run_24_7.sh
```

Watch the output to confirm everything works.

### Step 5: Let It Run 24/7

The cron job is now active. Your laptop will automatically:
- Scan every 6 hours
- Find vulnerable subdomains
- Verify and claim them
- Generate PoCs
- Save to `~/Desktop/Subdomain_Takeover_Results/`

---

## Expected Output

### Daily Stats:
- **10-20 PoCs** on slow days
- **30-50 PoCs** on normal days
- **70-100+ PoCs** on good days

### Where to Find Results:
```bash
# Latest vulnerabilities
cat ~/Desktop/Subdomain_Takeover_Results/Verified_Vulnerabilities/verified_vulnerabilities.txt

# All scan results
open ~/Desktop/Subdomain_Takeover_Results/

# Live logs
tail -f ~/Desktop/Subdomain_Takeover_Results/scanner.log
```

---

## Monitor from Your Main Laptop

You can check your 24/7 laptop remotely:

### Option 1: SSH + Check Logs
```bash
ssh your-laptop-username@your-laptop-ip
tail -f ~/Desktop/Subdomain_Takeover_Results/scanner.log
```

### Option 2: Auto-Sync to Cloud
Add this to your cron job:
```bash
# In crontab -e, add after the scanner line:
0 */6 * * * rsync -av ~/Desktop/Subdomain_Takeover_Results/ user@your-server:/backup/
```

### Option 3: Email Notifications
Make sure you set up email in `account_details.json` - you'll get notified on every successful claim!

---

## Optimization Tips

### 🎯 For Maximum PoCs (100/day):

1. **Run More Frequently**
   ```bash
   crontab -e
   # Change to every 2 hours:
   0 */2 * * * cd /path/to/scanner && ./run_24_7.sh >> ~/Desktop/Subdomain_Takeover_Results/scanner.log 2>&1
   ```

2. **Increase Batch Size**
   Edit `run_24_7.sh`:
   ```bash
   --batch-size 200  # Instead of 100
   ```

3. **Use Multiple Cloud Accounts**
   In `account_details.json`, add 3-5 AWS and Azure accounts for better claiming success rate.

4. **Target More TLDs**
   ```bash
   --tlds "com,net,org,io,app,dev,co,ai"
   ```

5. **Lower Quality Threshold** (more quantity)
   ```bash
   --min-trust-score 60  # Instead of 70
   ```

---

## Troubleshooting

### Scanner Not Running?
```bash
# Check cron is active
crontab -l

# Check logs for errors
tail -50 ~/Desktop/Subdomain_Takeover_Results/scanner.log

# Run manually to see errors
./run_24_7.sh
```

### No Results?
- Check internet connection
- Verify tools installed: `which subfinder nuclei`
- Try manual test: `python3 aggressive_scanner.py 1 10 "com" 5`

### Auto-Claiming Not Working?
- Double-check credentials in `account_details.json`
- Test AWS: `aws s3 ls` (should work)
- Test Azure: `az account show` (should show your account)

---

## Contact/Sync with Main Laptop

### Send Results to Main Laptop Daily:
Add to crontab:
```bash
# Email results daily at 8am
0 8 * * * cat ~/Desktop/Subdomain_Takeover_Results/Verified_Vulnerabilities/verified_vulnerabilities.txt | mail -s "Daily PoCs" your-email@example.com
```

### Or use Dropbox/Google Drive sync:
```bash
# Create symlink to cloud folder
ln -s ~/Desktop/Subdomain_Takeover_Results ~/Dropbox/Scanner_Results
```

---

## Keep Laptop Running 24/7

### macOS:
```bash
# Prevent sleep
sudo pmset -a disablesleep 1

# Or use "caffeinate" when running
caffeinate -s &
```

### Linux:
```bash
# Disable sleep
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

---

## That's It!

Your 24/7 PoC machine is ready. Check back daily for results at:
`~/Desktop/Subdomain_Takeover_Results/`

Happy hunting! 🎯
