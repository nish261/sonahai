#!/bin/bash

###############################################################################
# 24/7 Subdomain Takeover Scanner - Automated Setup
# Goal: Generate 10-100 PoCs per day automatically
###############################################################################

set -e  # Exit on error

echo "=========================================="
echo "24/7 Scanner Setup - Starting Installation"
echo "=========================================="

# 1. Install system dependencies
echo ""
echo "[1/8] Installing system dependencies..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python3 go subfinder nuclei httpx dnsx
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip golang-go

    # Install Go tools
    go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
    go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

    # Add Go bin to PATH
    export PATH=$PATH:~/go/bin
    echo 'export PATH=$PATH:~/go/bin' >> ~/.bashrc
fi

# 2. Install Python dependencies
echo ""
echo "[2/8] Installing Python dependencies..."
pip3 install streamlit pandas requests dnspython boto3 azure-identity azure-mgmt-resource \
    azure-mgmt-storage selenium webdriver-manager reportlab python-whois tranco

# 3. Install browser automation dependencies
echo ""
echo "[3/8] Setting up browser automation..."
pip3 install selenium webdriver-manager

# 4. Configure credentials
echo ""
echo "[4/8] Setting up credentials..."
if [ ! -f "account_details.json" ]; then
    echo "Creating account_details.json from template..."
    if [ -f "account_details_TEMPLATE.json" ]; then
        cp account_details_TEMPLATE.json account_details.json
        echo "⚠️  IMPORTANT: Edit account_details.json with your credentials:"
        echo "   - AWS credentials (for S3/EB claiming)"
        echo "   - Azure credentials (for Azure claiming)"
        echo "   - Email/Slack for notifications"
    else
        cat > account_details.json <<'CREDENTIALS'
{
  "aws": [
    {
      "name": "AWS Account 1",
      "access_key": "YOUR_AWS_ACCESS_KEY",
      "secret_key": "YOUR_AWS_SECRET_KEY",
      "region": "us-east-1"
    }
  ],
  "azure": [
    {
      "name": "Azure Account 1",
      "subscription_id": "YOUR_SUBSCRIPTION_ID",
      "tenant_id": "YOUR_TENANT_ID",
      "client_id": "YOUR_CLIENT_ID",
      "client_secret": "YOUR_CLIENT_SECRET"
    }
  ],
  "wordpress": {
    "email": "your-wordpress-email@example.com",
    "password": "YOUR_WORDPRESS_PASSWORD"
  },
  "notifications": {
    "email": "your-email@example.com",
    "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  }
}
CREDENTIALS
        echo "✅ Created account_details.json - EDIT THIS FILE WITH YOUR CREDENTIALS"
    fi
fi

# 5. Create output directories
echo ""
echo "[5/8] Creating output directories..."
mkdir -p ~/Desktop/Subdomain_Takeover_Results/{Scans,Verified_Vulnerabilities,Niche_Analysis,PoC_Files}

# 6. Set up automated cron job (24/7 operation)
echo ""
echo "[6/8] Setting up 24/7 automation..."

# Create the main automation script
cat > run_24_7.sh <<'AUTOMATION'
#!/bin/bash
cd "$(dirname "$0")"

# Run complete pipeline with auto-claiming
# This will:
# 1. Scan 1000 domains starting from rank 500
# 2. Verify vulnerabilities
# 3. Analyze niche/SEO value
# 4. Auto-claim high-value targets (S3, Azure, WordPress)
# 5. Generate PoCs

echo "[$(date)] Starting 24/7 scan cycle..."

# Run aggressive scanner: rank 500, 1000 domains, .com/.net/.org, 20 workers
python3 aggressive_scanner.py 500 1000 "com,net,org" 20 10

# If aggressive_scanner completes successfully, run verification and claiming
if [ $? -eq 0 ]; then
    echo "[$(date)] Scan complete. Running verification..."
    python3 verify_results.py

    echo "[$(date)] Running niche analysis..."
    python3 niche_analyzer.py ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv

    echo "[$(date)] Auto-claiming vulnerabilities..."
    python3 auto_poc_claimer.py ~/Desktop/Subdomain_Takeover_Results/Verified_Vulnerabilities/verified_vulnerabilities.csv
fi

echo "[$(date)] Scan cycle completed. Results saved to ~/Desktop/Subdomain_Takeover_Results/"
AUTOMATION

chmod +x run_24_7.sh

# 7. Set up cron job (runs every 6 hours)
echo ""
echo "[7/8] Setting up cron job (every 6 hours)..."
CRON_JOB="0 */6 * * * cd $(pwd) && ./run_24_7.sh >> ~/Desktop/Subdomain_Takeover_Results/scanner.log 2>&1"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "run_24_7.sh"; echo "$CRON_JOB") | crontab -

echo "✅ Cron job added - scanner will run every 6 hours"
echo "   To check: crontab -l"
echo "   To view logs: tail -f ~/Desktop/Subdomain_Takeover_Results/scanner.log"

# 8. Test the setup
echo ""
echo "[8/8] Running initial test..."
echo "Testing scanner components..."

# Quick test run
python3 -c "import streamlit, pandas, requests, dns.resolver, boto3, azure.identity; print('✅ All Python dependencies OK')"

if command -v subfinder &> /dev/null; then
    echo "✅ Subfinder installed"
else
    echo "⚠️  Warning: subfinder not found in PATH"
fi

if command -v nuclei &> /dev/null; then
    echo "✅ Nuclei installed"
else
    echo "⚠️  Warning: nuclei not found in PATH"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Edit credentials:"
echo "   nano account_details.json"
echo ""
echo "2. Start 24/7 automated scanning:"
echo "   ./run_24_7.sh"
echo ""
echo "3. OR launch web UI for manual control:"
echo "   streamlit run simple_scanner_ui.py"
echo ""
echo "4. Monitor automated runs:"
echo "   tail -f ~/Desktop/Subdomain_Takeover_Results/scanner.log"
echo ""
echo "📊 Expected Output:"
echo "   - 10-100 PoCs per day (depending on vulnerability discovery)"
echo "   - Results saved to: ~/Desktop/Subdomain_Takeover_Results/"
echo "   - Auto-claiming enabled for high-value targets"
echo ""
echo "🔄 Automation Schedule:"
echo "   - Runs every 6 hours automatically"
echo "   - Scans 100+ domains per cycle"
echo "   - Sends notifications on successful claims"
echo ""
echo "=========================================="
