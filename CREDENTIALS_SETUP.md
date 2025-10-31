# 🔐 Credentials Setup Guide

## Quick Setup (3 Steps)

### Step 1: Copy the Template

```bash
cd ~/Desktop/scanner-app
cp account_details_TEMPLATE.json account_details.json
```

### Step 2: Fill in Your Credentials

Edit `account_details.json` with your actual credentials:

```bash
nano account_details.json
# or
open account_details.json  # Opens in default text editor
```

### Step 3: Test It

```bash
python3 credentials_loader.py
```

You should see:
```
✓ Loaded credentials from: /Users/nishchalasri/Desktop/scanner-app/account_details.json

============================================================
📋 CREDENTIALS STATUS
============================================================
AWS:               ✅ Configured
Azure:             ✅ CLI login (run az login)
GitHub:            ✅ Configured
Researcher Profile: ✅ Configured
============================================================

✅ Credentials loader working correctly!
```

---

## 📋 What You Need to Fill In

### 🔴 **REQUIRED (for basic functionality):**

#### **Researcher Profile:**
```json
"researcher_profile": {
  "name": "Your Name",
  "email": "you@example.com"
}
```
This appears on your PoC pages for bug bounty attribution.

---

### 🟡 **OPTIONAL (based on what you want to automate):**

#### **AWS (for S3 subdomain takeovers):**

1. Go to: https://console.aws.amazon.com/iam/home#/security_credentials
2. Click "Create access key"
3. Copy Access Key ID and Secret Access Key

```json
"aws": {
  "access_key_id": "AKIAIOSFODNN7EXAMPLE",
  "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "default_region": "us-east-1"
}
```

#### **Azure (for Azure App Service takeovers):**

**Easy method (recommended):**
```bash
az login
```
That's it! Leave the Azure section as-is in the JSON.

**Alternative method (username/password):**
```json
"azure": {
  "method": "credentials",
  "username": "you@yourdomain.com",
  "password": "your-password",
  "subscription_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

#### **GitHub (for GitHub Pages takeovers):**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scope: `repo` (full control)
4. Click "Generate token"
5. Copy the token (starts with `ghp_`)

```json
"github": {
  "username": "your-github-username",
  "personal_access_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

#### **Proxy (to avoid rate limiting):**

If you have a proxy service:
```json
"proxy": {
  "enabled": true,
  "http_proxy": "http://proxy.example.com:8080",
  "https_proxy": "http://proxy.example.com:8080",
  "username": "proxy-user",
  "password": "proxy-pass"
}
```

---

## 🔒 Security Notes

### ✅ **Safe:**
- `account_details.json` is in `.gitignore` - will NOT be committed to git
- File permissions are restricted to you only
- Credentials stay on your local machine

### ⚠️ **Important:**
- **NEVER** share `account_details.json` with anyone
- **NEVER** commit it to git (already protected by .gitignore)
- **NEVER** paste credentials in screenshots or bug reports

### 🗑️ **To Delete Credentials:**
```bash
rm ~/Desktop/scanner-app/account_details.json
```

---

## ✅ How the Tools Use These Credentials

### **Auto PoC Claimer:**
```bash
python3 auto_poc_claimer.py results.csv
```
- Automatically loads credentials from `account_details.json`
- Uses AWS credentials to create S3 buckets
- Uses Azure CLI (after `az login`) to create App Services
- Uses GitHub token to create GitHub Pages repos
- Uses your researcher name on PoC pages

### **Scanner (with proxy):**
```bash
python3 aggressive_scanner.py 1 1000
```
- Automatically sets HTTP_PROXY and HTTPS_PROXY if enabled
- Helps avoid rate limiting from subfinder/nuclei

### **Niche Analyzer (optional Moz API):**
```bash
python3 niche_analyzer.py
```
- Can use Moz API credentials for real Domain Authority data
- Falls back to estimates if not configured

---

## 🧪 Testing Individual Platforms

### Test AWS:
```python
python3 -c "from credentials_loader import setup_aws_environment; setup_aws_environment()"
```

### Test GitHub:
```python
python3 -c "from credentials_loader import get_github_credentials; print(get_github_credentials())"
```

### Test Profile:
```python
python3 -c "from credentials_loader import get_researcher_profile; print(get_researcher_profile())"
```

---

## 📝 Minimal Working Example

If you ONLY want to use the scanner (no auto-claiming), you only need:

```json
{
  "researcher_profile": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

Everything else is optional!

---

## 🆘 Troubleshooting

### "No account_details.json found"
**Solution:**
```bash
cp account_details_TEMPLATE.json account_details.json
```

### "AWS credentials not configured"
**Solution:** Fill in the `aws` section in `account_details.json`

### "Azure CLI not authenticated"
**Solution:**
```bash
az login
```

### "GitHub token invalid"
**Solution:**
1. Check token has `repo` scope
2. Regenerate token at https://github.com/settings/tokens
3. Update in `account_details.json`

---

## 🎯 Ready to Go!

Once configured, all tools automatically load credentials:

```bash
# Scanner automatically uses proxy if configured
python3 aggressive_scanner.py 1 1000

# Auto claimer automatically uses all platform credentials
python3 auto_poc_claimer.py results.csv

# Streamlit UI automatically loads everything
streamlit run simple_scanner_ui.py
```

No more manual credential entry! 🎉
