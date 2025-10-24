# 🤖 Automatic PoC Claimer for Bug Bounty

## Overview

**Automatically claims vulnerable subdomains and uploads proof-of-concept pages** for bug bounty research.

This tool takes your scanner results (CSV) and:
1. **Automatically claims** the vulnerable subdomain (creates S3 bucket, Azure app, GitHub Pages, etc.)
2. **Uploads a professional PoC HTML page** proving you control the subdomain
3. **Logs all actions** for your bug bounty report
4. **Provides cleanup commands** for after bounty is paid

---

## ⚠️ IMPORTANT: Ethical Usage

**This tool is for AUTHORIZED bug bounty research ONLY.**

### Legal Requirements:
- ✅ Only use on programs you're authorized to test
- ✅ Only claim subdomains you discovered through your own scanning
- ✅ Remove PoC immediately after bounty is confirmed
- ✅ Never upload malicious content - PoC is informational only
- ❌ DO NOT use for unauthorized penetration testing
- ❌ DO NOT leave PoCs deployed indefinitely

---

## 🚀 Quick Start

### 1. Configure Credentials (One-Time Setup)

Open the Streamlit UI at http://localhost:8501 and configure your platform credentials:

**AWS (for S3 takeovers):**
- Access Key ID
- Secret Access Key
- Default Region

**Azure (for Azure App Service takeovers):**
- Run `az login` in terminal first
- Or configure username/password in UI

**GitHub (for GitHub Pages takeovers):**
- Username
- Personal Access Token (with `repo` permissions)

**Your Profile:**
- Researcher Name (for PoC attribution)
- Email

### 2. Run Scanner

```bash
# Run a scan to find vulnerabilities
python3 aggressive_scanner.py 1 1000 ALL 10 30
```

This will create a CSV file at:
```
~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

### 3. Auto-Claim Vulnerabilities

```bash
# Automatically claim ALL vulnerabilities and upload PoCs
python3 auto_poc_claimer.py ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

---

## 📋 What It Does

### For Each Vulnerability:

#### **AWS S3 Buckets:**
1. Creates S3 bucket with the exact name
2. Enables static website hosting
3. Sets public-read policy
4. Uploads professional PoC HTML as `index.html`
5. Provides bucket URL: `http://bucket-name.s3-website-us-east-1.amazonaws.com`

#### **Microsoft Azure:**
1. Creates resource group (auto-named)
2. Creates App Service Plan (Free tier - no cost)
3. Creates Web App with the exact name
4. Deploys PoC HTML via ZIP deployment
5. Provides app URL: `https://app-name.azurewebsites.net`

#### **GitHub Pages:**
1. Creates repository: `repo-name.github.io`
2. Clones repo locally
3. Adds PoC HTML as `index.html`
4. Adds `CNAME` file for custom domain
5. Commits and pushes to GitHub
6. GitHub Pages auto-deploys PoC

---

## 📄 PoC HTML Features

The automatically generated PoC page includes:

- **Professional Design** - Clean, modern UI with gradient background
- **Vulnerability Details** - Subdomain, service type, CNAME, discovery date
- **Researcher Attribution** - Your name and PoC ID for tracking
- **Educational Content** - Explains what subdomain takeover is
- **Remediation Steps** - Specific fix instructions for security team
- **References** - Links to OWASP, PortSwigger, can-i-take-over-xyz
- **Ethical Notice** - "No malicious actions taken" disclaimer
- **Timestamp** - UTC timestamp for audit trail

---

## 💻 Example Usage

### Scenario 1: Claim All Vulnerabilities

```bash
# Run scanner
python3 aggressive_scanner.py 5000 500 ALL 10 30

# Wait for scan to complete (check Streamlit UI)

# Auto-claim everything
python3 auto_poc_claimer.py ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv
```

**Output:**
```
🤖 Automatic PoC Claimer - Bug Bounty Edition
============================================================
📋 Processing: subdomain_takeover_detailed.csv
👤 Researcher: YourName
============================================================

[1/12] Processing: old-app.company.com
   Service: AWS/S3
   CNAME: old-app.s3.amazonaws.com

🪣 AWS S3 Auto-Claimer: old-app
============================================================
[1/5] Creating S3 bucket: old-app
  ✓ Bucket created successfully
[2/5] Enabling static website hosting...
  ✓ Website hosting enabled
[3/5] Setting public read policy...
  ✓ Public read policy applied
[4/5] Uploading PoC HTML...
  ✓ PoC uploaded successfully
[5/5] Verifying PoC is live...

============================================================
✅ SUCCESS! Subdomain claimed and PoC deployed
============================================================
📍 Subdomain: old-app.company.com
🌐 PoC URL: http://old-app.s3-website-us-east-1.amazonaws.com
📋 Bucket: old-app
🗑️  Cleanup: aws s3 rb s3://old-app --force
============================================================

[2/12] Processing: staging.company.com
   Service: Microsoft Azure
   ...
```

### Scenario 2: Claim Specific Services Only

```bash
# Only claim AWS S3 vulnerabilities (edit CSV first or use grep)
grep "AWS/S3" subdomain_takeover_detailed.csv > aws_only.csv

# Claim only those
python3 auto_poc_claimer.py aws_only.csv
```

---

## 📊 Output Files

### 1. Auto-Claimed PoCs CSV
**Location:** `~/Desktop/Subdomain_Takeover_Results/auto_claimed_pocs.csv`

**Columns:**
- `subdomain` - Vulnerable subdomain
- `service` - Service type (AWS/S3, Azure, etc.)
- `success` - True/False
- `poc_url` - Live PoC URL (if successful)
- `error` - Error message (if failed)
- `timestamp` - ISO 8601 timestamp

**Example:**
```csv
subdomain,service,success,poc_url,error,timestamp
old-app.company.com,AWS/S3,True,http://old-app.s3-website-us-east-1.amazonaws.com,,2024-10-24T17:30:00
staging.company.com,Microsoft Azure,True,https://staging.azurewebsites.net,,2024-10-24T17:30:15
docs.company.com,Github,False,,Repository name already exists,2024-10-24T17:30:30
```

### 2. PoC HTML Files
**Temporary Location:** `/tmp/poc_*.html` (auto-deleted after upload)

**Live URLs:**
- AWS S3: `http://bucket-name.s3-website-{region}.amazonaws.com`
- Azure: `https://app-name.azurewebsites.net`
- GitHub: `https://username.github.io/repo-name.github.io`

---

## 🗑️ Cleanup After Bounty

**AWS S3:**
```bash
aws s3 rb s3://bucket-name --force
```

**Microsoft Azure:**
```bash
az group delete --name bugbounty-poc-app-name --yes
```

**GitHub Pages:**
1. Go to: https://github.com/username/repo-name.github.io/settings
2. Scroll to bottom
3. Click "Delete this repository"

---

## 🔧 Troubleshooting

### "AWS credentials not configured"
**Solution:** Configure AWS credentials in Streamlit UI sidebar → Credential Manager

### "Azure CLI not authenticated"
**Solution:** Run `az login` in your terminal first

### "GitHub token invalid"
**Solution:**
1. Go to https://github.com/settings/tokens
2. Generate new token with `repo` scope
3. Add to Streamlit UI sidebar → Credential Manager → GitHub → Personal Access Token

### "Bucket already exists"
**Meaning:** Either:
- Another researcher claimed it first
- You already claimed it previously
- It's now owned by the target company (they fixed it)

### "App name already taken" (Azure)
**Meaning:** App name is globally unique. Try:
- Adding your username as suffix
- Using a different variation of the name

---

## 📈 Best Practices

### 1. Test Small Batches First
```bash
# Test with just 1-2 vulnerabilities first
head -3 subdomain_takeover_detailed.csv > test.csv
python3 auto_poc_claimer.py test.csv
```

### 2. Filter by Severity
Only claim high-value targets:
```bash
# Get only subdomains from top-ranked domains
python3 -c "
import csv
with open('subdomain_takeover_detailed.csv') as f:
    reader = csv.DictReader(f)
    high_value = [r for r in reader if any(tld in r['subdomain'] for tld in ['.com', '.org', '.gov'])]

with open('high_value_only.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=['subdomain', 'service', 'cname', 'status'])
    writer.writeheader()
    writer.writerows(high_value)
"

python3 auto_poc_claimer.py high_value_only.csv
```

### 3. Keep Detailed Logs
The tool automatically logs everything to:
- `auto_claimed_pocs.csv` - All attempts
- Console output - Real-time progress
- Cleanup commands - For post-bounty removal

---

## 🎯 Supported Services

Currently supports **automatic claiming** for:

✅ **AWS S3** (Static Website Hosting)
✅ **Microsoft Azure** (App Service)
✅ **GitHub Pages**

Coming soon:
- Heroku
- Netlify
- Vercel
- Digital Ocean
- WordPress.com
- Shopify

For unsupported services, the tool will:
- Skip them
- Log them as "Service not supported"
- You can claim manually using the Streamlit PoC generator

---

## 🔒 Security & Ethics

### This Tool:
- ✅ Creates ONLY informational PoC pages
- ✅ No malicious code or scripts
- ✅ No data collection mechanisms
- ✅ Clear researcher attribution
- ✅ Provides cleanup instructions

### You MUST:
- ✅ Only use on authorized bug bounty programs
- ✅ Remove PoCs after bounty confirmation
- ✅ Follow program disclosure policies
- ✅ Never upload malicious content

### Report Template:

```
Title: Subdomain Takeover - {subdomain}

Severity: High

Description:
The subdomain {subdomain} is vulnerable to subdomain takeover due to a dangling DNS CNAME record pointing to {cname}.

Steps to Reproduce:
1. Check DNS record: dig CNAME {subdomain}
2. Observe CNAME points to: {cname}
3. Service does not exist or is unclaimed
4. I claimed the resource and deployed a proof-of-concept

Proof of Concept:
{poc_url}

Impact:
- Attacker could host malicious content on your domain
- Phishing attacks using your trusted domain
- Brand reputation damage
- Session hijacking if cookies are domain-scoped

Remediation:
Remove the DNS CNAME record for {subdomain}

Researcher: {your_name}
Date: {date}
```

---

## 📞 Support

If you encounter issues:
1. Check credentials are configured correctly
2. Verify you have necessary permissions (AWS IAM, Azure subscription, GitHub token scopes)
3. Check the error message in console output
4. Review `auto_claimed_pocs.csv` for detailed error logs

---

## 🎓 Learning Resources

- [OWASP Subdomain Takeover Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover)
- [Can I Take Over XYZ?](https://github.com/EdOverflow/can-i-take-over-xyz)
- [PortSwigger: Subdomain Takeover](https://portswigger.net/web-security/ssrf/subdomain-takeover)
- [Bug Bounty Bootcamp Book](https://nostarch.com/bug-bounty-bootcamp)

---

**Remember: With great power comes great responsibility. Use ethically!** 🦸‍♂️
