#!/usr/bin/env python3
"""
Simple Subdomain Scanner UI - Works reliably
"""

import streamlit as st
import subprocess
import os
import time
from pathlib import Path
import pandas as pd
from datetime import datetime
import poc_generators as poc
import credentials_manager as creds_mgr

st.set_page_config(
    page_title="Subdomain Takeover Scanner",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"  # Start with sidebar collapsed to save space
)

# Organized output folders
DESKTOP_PATH = Path.home() / "Desktop"
RESULTS_FOLDER = DESKTOP_PATH / "Subdomain_Takeover_Results"
SCANS_FOLDER = RESULTS_FOLDER / "Scans"
VERIFIED_FOLDER = RESULTS_FOLDER / "Verified_Vulnerabilities"
NICHE_FOLDER = RESULTS_FOLDER / "Niche_Analysis"
POCS_FOLDER = RESULTS_FOLDER / "PoC_Files"

# Create folders if they don't exist
for folder in [RESULTS_FOLDER, SCANS_FOLDER, VERIFIED_FOLDER, NICHE_FOLDER, POCS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# Output files
OUTPUT_FILE = SCANS_FOLDER / "subdomain_takeover_results.txt"
DETAILED_FILE = SCANS_FOLDER / "subdomain_takeover_detailed.csv"
VERIFIED_FILE = VERIFIED_FOLDER / "verified_vulnerabilities.txt"
VERIFIED_CSV = VERIFIED_FOLDER / "verified_vulnerabilities.csv"
NICHE_CSV = NICHE_FOLDER / "niche_analysis.csv"
PROGRESS_FILE = Path("scan_progress.txt")
STATUS_FILE = Path("scan_status.txt")
VERIFY_PROGRESS = Path("verify_progress.txt")
VERIFY_STATUS = Path("verify_status.txt")
NICHE_PROGRESS = Path("niche_progress.txt")
NICHE_STATUS = Path("niche_status.txt")
PIPELINE_PROGRESS = Path("pipeline_progress.txt")
PIPELINE_STATUS = Path("pipeline_status.txt")

# Compact Header
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("🔍 Subdomain Takeover Scanner")
    st.caption("Bug Bounty Tool | [can-i-take-over-xyz](https://github.com/EdOverflow/can-i-take-over-xyz) (Oct 2024)")

# Show current scan status if running (compact version)
if Path("scan_progress.txt").exists():
    try:
        progress = int(open("scan_progress.txt").read().strip())
        if progress < 100:
            with col_h2:
                st.metric("Scan Progress", f"{progress}%", delta="Running")
            st.progress(progress / 100, text=f"🚀 Scanner running: {progress}% complete")
    except:
        pass

# Quick Start - Super Compact
with st.expander("📖 Quick Start", expanded=False):
    st.markdown("""
    **🎯 Scans for subdomain takeovers** across 43 services (AWS, Azure, GitHub, etc.)
    - Configure scan settings in tabs below → Run scan → Results auto-save to Desktop
    - Tip: Ranks 5000-15000 give best results | Takes ~45-90min for 1000 domains
    """)

# Check scanner engine status
import subprocess as sp
subdominator_available = False
subdominator_paths = [
    Path.home() / 'subdominator',
    Path.home() / 'subdominator-bin' / 'Subdominator',
]
for path in subdominator_paths:
    if path.exists() and path.is_file():
        subdominator_available = True
        break

if subdominator_available:
    st.success("🚀 **Scanner Engine:** Subdominator (Fast + Accurate | 97 fingerprints)")
else:
    st.info("⚙️ **Scanner Engine:** Python + dig (Standard | 68 fingerprints) - Install Subdominator for 8x speed boost!")

# Sidebar
st.sidebar.header("⚙️ Configuration")

# Load saved credentials
if 'creds' not in st.session_state:
    st.session_state.creds = creds_mgr.load_credentials()
    if not st.session_state.creds:
        st.session_state.creds = creds_mgr.get_default_creds()

# User Profile Section
st.sidebar.subheader("👤 Platform Credentials")
with st.sidebar.expander("Credential Manager", expanded=False):
    st.markdown("### 👤 Basic Info")
    st.session_state.creds['profile']['researcher_name'] = st.text_input(
        "Your Name",
        value=st.session_state.creds['profile'].get('researcher_name', ''),
        placeholder="researcher123"
    )
    st.session_state.creds['profile']['researcher_email'] = st.text_input(
        "Your Email",
        value=st.session_state.creds['profile'].get('researcher_email', ''),
        placeholder="you@example.com"
    )

    st.markdown("---")
    st.markdown("### 🪣 AWS")
    st.session_state.creds['aws']['access_key_id'] = st.text_input(
        "Access Key ID",
        value=st.session_state.creds['aws'].get('access_key_id', ''),
        type="password"
    )
    st.session_state.creds['aws']['secret_access_key'] = st.text_input(
        "Secret Access Key",
        value=st.session_state.creds['aws'].get('secret_access_key', ''),
        type="password"
    )
    st.session_state.creds['aws']['default_region'] = st.selectbox(
        "Default Region",
        ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"],
        index=["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"].index(
            st.session_state.creds['aws'].get('default_region', 'us-east-1')
        ) if st.session_state.creds['aws'].get('default_region') in ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1", "ap-southeast-1"] else 0
    )

    st.markdown("---")
    st.markdown("### ☁️ Azure")
    st.session_state.creds['azure']['username'] = st.text_input(
        "Username/Email",
        value=st.session_state.creds['azure'].get('username', ''),
        key="azure_user"
    )
    st.session_state.creds['azure']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['azure'].get('password', ''),
        type="password",
        key="azure_pass"
    )
    st.session_state.creds['azure']['subscription_id'] = st.text_input(
        "Subscription ID",
        value=st.session_state.creds['azure'].get('subscription_id', ''),
        key="azure_sub"
    )
    st.session_state.creds['azure']['default_location'] = st.selectbox(
        "Default Location",
        ["eastus", "westus", "westus2", "northeurope", "westeurope"],
        index=["eastus", "westus", "westus2", "northeurope", "westeurope"].index(
            st.session_state.creds['azure'].get('default_location', 'eastus')
        ) if st.session_state.creds['azure'].get('default_location') in ["eastus", "westus", "westus2", "northeurope", "westeurope"] else 0,
        key="azure_loc"
    )

    st.markdown("---")
    st.markdown("### 📄 GitHub")
    st.session_state.creds['github']['username'] = st.text_input(
        "Username",
        value=st.session_state.creds['github'].get('username', ''),
        key="gh_user"
    )
    st.session_state.creds['github']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['github'].get('password', ''),
        type="password",
        key="gh_pass"
    )
    st.session_state.creds['github']['personal_access_token'] = st.text_input(
        "Personal Access Token",
        value=st.session_state.creds['github'].get('personal_access_token', ''),
        type="password",
        key="gh_token"
    )

    st.markdown("---")
    st.markdown("### 🚀 Heroku")
    st.session_state.creds['heroku']['email'] = st.text_input(
        "Email",
        value=st.session_state.creds['heroku'].get('email', ''),
        key="heroku_email"
    )
    st.session_state.creds['heroku']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['heroku'].get('password', ''),
        type="password",
        key="heroku_pass"
    )
    st.session_state.creds['heroku']['api_key'] = st.text_input(
        "API Key",
        value=st.session_state.creds['heroku'].get('api_key', ''),
        type="password",
        key="heroku_key"
    )

    st.markdown("---")
    st.markdown("### 💧 DigitalOcean")
    st.session_state.creds['digitalocean']['email'] = st.text_input(
        "Email",
        value=st.session_state.creds['digitalocean'].get('email', ''),
        key="do_email"
    )
    st.session_state.creds['digitalocean']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['digitalocean'].get('password', ''),
        type="password",
        key="do_pass"
    )
    st.session_state.creds['digitalocean']['api_token'] = st.text_input(
        "API Token",
        value=st.session_state.creds['digitalocean'].get('api_token', ''),
        type="password",
        key="do_token"
    )

    st.markdown("---")
    st.markdown("### 🛍️ Shopify")
    st.session_state.creds['shopify']['email'] = st.text_input(
        "Email",
        value=st.session_state.creds['shopify'].get('email', ''),
        key="shopify_email"
    )
    st.session_state.creds['shopify']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['shopify'].get('password', ''),
        type="password",
        key="shopify_pass"
    )
    st.session_state.creds['shopify']['partner_api_key'] = st.text_input(
        "Partner API Key",
        value=st.session_state.creds['shopify'].get('partner_api_key', ''),
        type="password",
        key="shopify_api_key"
    )

    st.markdown("---")
    st.markdown("### 📝 WordPress")
    st.session_state.creds['wordpress']['username'] = st.text_input(
        "Username",
        value=st.session_state.creds['wordpress'].get('username', ''),
        key="wp_user"
    )
    st.session_state.creds['wordpress']['password'] = st.text_input(
        "Password",
        value=st.session_state.creds['wordpress'].get('password', ''),
        type="password",
        key="wp_pass"
    )
    st.session_state.creds['wordpress']['email'] = st.text_input(
        "Email",
        value=st.session_state.creds['wordpress'].get('email', ''),
        key="wp_email"
    )

    st.markdown("---")
    st.markdown("### 🔶 Cloudflare")
    st.session_state.creds['cloudflare']['email'] = st.text_input(
        "Email",
        value=st.session_state.creds['cloudflare'].get('email', ''),
        key="cf_email"
    )
    st.session_state.creds['cloudflare']['api_key'] = st.text_input(
        "Global API Key",
        value=st.session_state.creds['cloudflare'].get('api_key', ''),
        type="password",
        key="cf_api_key"
    )
    st.session_state.creds['cloudflare']['api_token'] = st.text_input(
        "API Token",
        value=st.session_state.creds['cloudflare'].get('api_token', ''),
        type="password",
        key="cf_token"
    )

    st.markdown("---")
    st.markdown("### 📊 Moz API (for DR/Backlink Data)")
    st.info("Get free tier at: https://moz.com/products/api (50 lookups/month)")
    st.session_state.creds.setdefault('moz', {})
    st.session_state.creds['moz']['access_id'] = st.text_input(
        "Access ID",
        value=st.session_state.creds['moz'].get('access_id', ''),
        key="moz_id"
    )
    st.session_state.creds['moz']['secret_key'] = st.text_input(
        "Secret Key",
        value=st.session_state.creds['moz'].get('secret_key', ''),
        type="password",
        key="moz_key"
    )

    st.markdown("---")
    col_save, col_delete = st.columns(2)
    with col_save:
        if st.button("💾 Save Credentials", use_container_width=True):
            creds_mgr.save_credentials(st.session_state.creds)
            st.success("Saved!")
            st.rerun()

    with col_delete:
        if st.button("🗑️ Clear All", use_container_width=True):
            creds_mgr.delete_credentials()
            st.session_state.creds = creds_mgr.get_default_creds()
            st.success("Cleared!")
            st.rerun()

    # Status
    if st.session_state.creds['profile'].get('researcher_name'):
        st.success(f"✓ {st.session_state.creds['profile']['researcher_name']}")

        configured = []
        if st.session_state.creds['aws'].get('access_key_id'): configured.append("AWS")
        if st.session_state.creds['azure'].get('username'): configured.append("Azure")
        if st.session_state.creds['github'].get('username'): configured.append("GitHub")
        if st.session_state.creds['heroku'].get('email'): configured.append("Heroku")
        if st.session_state.creds['digitalocean'].get('email'): configured.append("DO")
        if st.session_state.creds['shopify'].get('email'): configured.append("Shopify")
        if st.session_state.creds['wordpress'].get('username'): configured.append("WP")
        if st.session_state.creds['cloudflare'].get('email'): configured.append("CF")
        if st.session_state.creds.get('moz', {}).get('access_id'): configured.append("Moz")

        if configured:
            st.info(f"✓ {', '.join(configured)}")

st.sidebar.markdown("---")

# Scanner Engine Info
if not subdominator_available:
    st.sidebar.subheader("⚡ Upgrade to Subdominator")
    with st.sidebar.expander("Install Subdominator (8x faster)", expanded=False):
        st.markdown("""
        **Subdominator** is 8x faster and has 97 service fingerprints!

        **To install:**
        ```bash
        # Run the install script
        chmod +x install_scanner_deps.sh
        ./install_scanner_deps.sh
        ```

        Or manually:
        ```bash
        # Install .NET SDK
        curl -sSL https://dot.net/v1/dotnet-install.sh | \\
          bash -s -- --channel 9.0

        # Build Subdominator
        cd ~/Subdominator/Subdominator
        ~/.dotnet/dotnet publish -c Release \\
          -r osx-arm64 --self-contained \\
          -o ~/subdominator-bin
        ```

        After installing, restart the app to use Subdominator!
        """)
    st.sidebar.markdown("---")

# Scan Configuration
st.sidebar.subheader("🎯 Scan Configuration")
with st.sidebar.expander("Scan Settings", expanded=True):
    start_rank = st.number_input(
        "Start Rank",
        min_value=1,
        max_value=1000000,
        value=5000,
        step=100,
        help="Starting position in Tranco rankings (1 = google.com, etc.)"
    )

    num_domains = st.number_input(
        "Number of Domains",
        min_value=10,
        max_value=5000,
        value=100,
        step=10
    )

    st.markdown("---")
    st.markdown("**🔍 Domain Extension Filter** (Optional)")

    use_extension_filter = st.checkbox(
        "Filter by extension",
        value=False,
        help="Only scan subdomains with specific extensions"
    )

    target_extensions = ""
    if use_extension_filter:
        target_extensions = st.text_input(
            "Extensions (comma-separated)",
            value=".com, .net, .org",
            placeholder=".com, .co.uk, .io",
            help="Only scan subdomains ending with these extensions. Example: .com, .io, .ai"
        )

        st.info(f"""
        **Target:** Ranks {start_rank:,} - {start_rank + num_domains:,}
        **Extensions:** {target_extensions if target_extensions else 'All'}
        """)
    else:
        st.info(f"""
        **Target:** Ranks {start_rank:,} - {start_rank + num_domains:,}
        **Extensions:** All
        """)

# Service Filter
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Service Filter")
with st.sidebar.expander("Select Services to Scan", expanded=False):
    st.markdown("**Choose which services to look for:**")

    # Organize by category
    st.markdown("### ☁️ Cloud Platforms")
    aws_services = st.checkbox("AWS (S3, Elastic Beanstalk)", value=True, key="aws")
    azure_services = st.checkbox("Microsoft Azure (All services)", value=True, key="azure")
    do_services = st.checkbox("Digital Ocean", value=True, key="do")

    st.markdown("### 💻 Development & Hosting")
    github_services = st.checkbox("GitHub Pages", value=True, key="github")
    heroku_services = st.checkbox("Heroku", value=True, key="heroku")
    netlify_services = st.checkbox("Netlify", value=True, key="netlify")
    vercel_services = st.checkbox("Vercel", value=True, key="vercel")

    st.markdown("### 🛒 E-commerce & CMS")
    shopify_services = st.checkbox("Shopify", value=True, key="shopify")
    wordpress_services = st.checkbox("WordPress", value=True, key="wordpress")
    webflow_services = st.checkbox("Webflow", value=True, key="webflow")
    ghost_services = st.checkbox("Ghost", value=True, key="ghost")

    st.markdown("### 📱 Other Services")
    other_services = st.checkbox("All Other Services (43 total)", value=True, key="other")

    # Build service filter string
    selected_services = []
    if aws_services:
        selected_services.extend(["AWS/S3", "AWS/Elastic Beanstalk"])
    if azure_services:
        selected_services.append("Azure")
    if do_services:
        selected_services.append("Digital Ocean")
    if github_services:
        selected_services.append("Github")
    if heroku_services:
        selected_services.append("Heroku")
    if netlify_services:
        selected_services.append("Netlify")
    if vercel_services:
        selected_services.append("Vercel")
    if shopify_services:
        selected_services.append("Shopify")
    if wordpress_services:
        selected_services.append("WordPress.com")
    if webflow_services:
        selected_services.append("Webflow")
    if ghost_services:
        selected_services.append("Ghost")

    # Store in session state
    if 'service_filter' not in st.session_state:
        st.session_state.service_filter = "ALL"

    if len(selected_services) == 0:
        st.warning("⚠️ No services selected! Scanner will find nothing.")
        st.session_state.service_filter = "NONE"
    elif not other_services and len(selected_services) > 0:
        st.session_state.service_filter = ",".join(selected_services)
        st.info(f"✅ Scanning {len(selected_services)} specific services only")
    else:
        st.session_state.service_filter = "ALL"
        st.success(f"✅ Scanning all 43 vulnerable services")

with st.sidebar.expander("⚡ Performance Settings", expanded=False):
    enum_workers = st.number_input(
        "Enumeration Workers",
        min_value=5,
        max_value=50,
        value=10,
        step=5,
        help="Parallel workers for subfinder"
    )

    scan_workers = st.number_input(
        "Scanning Workers",
        min_value=10,
        max_value=100,
        value=30,
        step=10,
        help="Parallel workers for vulnerability checks"
    )

st.sidebar.markdown("---")

# PoC Generator in Sidebar
if OUTPUT_FILE.exists() or VERIFIED_FILE.exists():
    st.sidebar.subheader("🎯 PoC Generator")

    # Load results for auto-population
    available_results = []
    if DETAILED_FILE.exists():
        import csv
        with open(DETAILED_FILE, 'r') as f:
            reader = csv.DictReader(f)
            available_results = list(reader)

    with st.sidebar.expander("Generate PoCs", expanded=False):
        st.write(f"**Found {len(available_results)} results**")

        if st.session_state.creds['profile'].get('researcher_name'):
            if available_results:
                # Bulk generation option
                if st.button("🚀 Generate All PoCs", use_container_width=True):
                    st.session_state.bulk_generate = True
                    st.rerun()

                st.markdown("---")
                st.write("**Or select one:**")

                # Select specific result
                result_options = [f"{r['subdomain']} ({r['service']})" for r in available_results[:20]]
                selected = st.selectbox("Choose subdomain", ["Select..."] + result_options)

                if selected != "Select...":
                    idx = result_options.index(selected)
                    st.session_state.selected_result = available_results[idx]
                    if st.button("Generate PoC for Selected", use_container_width=True):
                        st.session_state.show_poc_form = True
                        st.rerun()
            else:
                st.info("No results yet. Run a scan first!")
        else:
            st.warning("⚠️ Set your profile first!")

st.sidebar.markdown("---")

# Check if any scan is running
scan_running = PROGRESS_FILE.exists()
pipeline_running = PIPELINE_PROGRESS.exists()
any_running = scan_running or pipeline_running

# Status display
col1, col2, col3 = st.columns(3)

status_text = "Ready"
phase_text = "Idle"
progress_val = 0

# Check pipeline status first (takes priority)
if PIPELINE_STATUS.exists():
    with open(PIPELINE_STATUS) as f:
        lines = f.readlines()
        if lines:
            phase_text = lines[0].strip()
            if len(lines) > 1:
                status_text = lines[1].strip()

    if PIPELINE_PROGRESS.exists():
        try:
            with open(PIPELINE_PROGRESS) as f:
                progress_val = int(f.read().strip())
        except:
            progress_val = 0
# Fall back to individual scan status
elif STATUS_FILE.exists():
    with open(STATUS_FILE) as f:
        lines = f.readlines()
        if lines:
            status_text = lines[0].strip()
            if len(lines) > 1:
                phase_text = lines[1].strip()

    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE) as f:
                progress_val = int(f.read().strip())
        except:
            progress_val = 0

with col1:
    st.metric("Phase", phase_text)

with col2:
    st.metric("Status", status_text)

with col3:
    # Count results
    vuln_count = 0
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            vuln_count = len([l for l in f if l.strip() and not l.startswith(('=', 'Generated', 'Total', 'Subdomain'))])
    st.metric("Vulnerabilities", vuln_count)

# Progress bar
if any_running:
    st.progress(progress_val / 100)

# Buttons
st.markdown("### 🚀 Quick Actions")

col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])

with col_btn1:
    if st.button("🎯 Run Complete Scan (Scan → Verify → Analyze)", disabled=any_running, type="primary", use_container_width=True):
        # Clean old files
        for f in [OUTPUT_FILE, DETAILED_FILE, VERIFIED_FILE, VERIFIED_CSV, NICHE_CSV,
                  PROGRESS_FILE, STATUS_FILE, VERIFY_PROGRESS, VERIFY_STATUS,
                  NICHE_PROGRESS, NICHE_STATUS, PIPELINE_PROGRESS, PIPELINE_STATUS]:
            if f.exists():
                f.unlink()

        # Create runner script
        extensions_str = target_extensions if use_extension_filter and target_extensions else 'ALL'
        service_filter_str = st.session_state.get('service_filter', 'ALL')
        runner_script = Path("run_complete_bg.sh")
        runner_script.write_text(f"""#!/bin/bash
source venv/bin/activate
python complete_pipeline.py {start_rank} {num_domains} "{extensions_str}" {enum_workers} {scan_workers} "{service_filter_str}"
""")
        runner_script.chmod(0o755)

        # Start complete pipeline in background
        subprocess.Popen(['./run_complete_bg.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(1)
        st.rerun()

with col_btn2:
    if st.button("🔍 Scan Only", disabled=any_running, type="secondary", use_container_width=True):
        # Clean old files
        for f in [OUTPUT_FILE, DETAILED_FILE, PROGRESS_FILE, STATUS_FILE]:
            if f.exists():
                f.unlink()

        # Create runner script
        extensions_str = target_extensions if use_extension_filter and target_extensions else 'ALL'
        service_filter_str = st.session_state.get('service_filter', 'ALL')
        runner_script = Path("run_scan_bg.sh")
        runner_script.write_text(f"""#!/bin/bash
source venv/bin/activate
python aggressive_scanner.py {start_rank} {num_domains} "{extensions_str}" {enum_workers} {scan_workers} "{service_filter_str}"
""")
        runner_script.chmod(0o755)

        # Start scan in background
        subprocess.Popen(['./run_scan_bg.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        time.sleep(1)
        st.rerun()

with col_btn3:
    if st.button("⏹️ Stop", disabled=not any_running, type="secondary", use_container_width=True):
        # Kill all processes
        subprocess.run(['pkill', '-f', 'complete_pipeline.py'], capture_output=True)
        subprocess.run(['pkill', '-f', 'aggressive_scanner.py'], capture_output=True)
        subprocess.run(['pkill', '-f', 'verify_results.py'], capture_output=True)
        subprocess.run(['pkill', '-f', 'niche_analyzer.py'], capture_output=True)
        subprocess.run(['pkill', '-f', 'run_scan_bg.sh'], capture_output=True)
        subprocess.run(['pkill', '-f', 'run_complete_bg.sh'], capture_output=True)
        subprocess.run(['pkill', '-f', 'subfinder'], capture_output=True)

        # Clean up progress files
        for f in [PROGRESS_FILE, STATUS_FILE, VERIFY_PROGRESS, VERIFY_STATUS,
                  NICHE_PROGRESS, NICHE_STATUS, PIPELINE_PROGRESS, PIPELINE_STATUS]:
            if f.exists():
                f.unlink()
        st.rerun()

# Live log
st.markdown("---")
with st.expander("📜 Activity Log", expanded=False):
    if STATUS_FILE.exists():
        with open(STATUS_FILE) as f:
            all_lines = f.readlines()
            if len(all_lines) > 2:
                for line in all_lines[2:]:  # Skip first 2 lines (status/phase)
                    st.text(line.strip())
    else:
        st.info("No activity. Click 'Start Scan' to begin.")

# Results
if OUTPUT_FILE.exists():
    st.markdown("---")
    st.subheader(f"🚨 Results")

    # Check if niche analysis is available
    niche_df = None
    if NICHE_CSV.exists():
        try:
            niche_df = pd.read_csv(NICHE_CSV)
            st.info(f"📊 **SEO Ratings Available!** {len(niche_df)} subdomains rated 1-9 based on value")
        except:
            pass

    # Load and display CSV if available (with ratings if we have them)
    if DETAILED_FILE.exists():
        import csv
        results_df = pd.read_csv(DETAILED_FILE)

        # Merge with niche ratings if available
        if niche_df is not None:
            # Merge on subdomain
            results_df = results_df.merge(
                niche_df[['subdomain', 'trust_score', 'priority_rank', 'cpa_vertical', 'cpa_value', 'seo_value']],
                on='subdomain',
                how='left'
            )
            # Convert trust_score to 1-9 scale for display
            def trust_to_rating(trust):
                if pd.isna(trust):
                    return '—'
                if trust >= 80:
                    return 9
                elif trust >= 70:
                    return 8
                elif trust >= 60:
                    return 7
                elif trust >= 50:
                    return 6
                elif trust >= 40:
                    return 5
                elif trust >= 30:
                    return 4
                elif trust >= 20:
                    return 3
                elif trust >= 10:
                    return 2
                else:
                    return 1

            results_df['rating'] = results_df['trust_score'].apply(trust_to_rating)
        else:
            results_df['rating'] = '—'

        # Single unified table with all info
        st.markdown("### 📊 All Results")

        # Add rating filter
        if niche_df is not None:
            rating_filter = st.selectbox(
                "Filter by Rating",
                ["All Ratings", "🔥 High (7-9)", "⚡ Medium (4-6)", "⚠️ Low (1-3)", "❓ Not Rated"],
                key="rating_filter"
            )

            # Apply filter
            display_df = results_df.copy()
            if rating_filter == "🔥 High (7-9)":
                display_df = display_df[display_df['rating'].isin([7, 8, 9])]
            elif rating_filter == "⚡ Medium (4-6)":
                display_df = display_df[display_df['rating'].isin([4, 5, 6])]
            elif rating_filter == "⚠️ Low (1-3)":
                display_df = display_df[display_df['rating'].isin([1, 2, 3])]
            elif rating_filter == "❓ Not Rated":
                display_df = display_df[display_df['rating'] == '—']
        else:
            display_df = results_df.copy()

        # Show everything in one table
        if len(display_df) > 0:
            st.dataframe(
                display_df,
                use_container_width=True,
                height=600
            )
            st.caption(f"Showing {len(display_df)} of {len(results_df)} total results")
        else:
            st.warning("No results match the selected filter")
    else:
        # Fallback to text display
        with open(OUTPUT_FILE) as f:
            content = f.read()
        st.text_area("Findings", content, height=400)

    # Download buttons
    col_dl1, col_dl2, col_dl3 = st.columns(3)

    with col_dl1:
        with open(OUTPUT_FILE, 'rb') as f:
            st.download_button(
                label="📥 Download TXT Report",
                data=f,
                file_name=OUTPUT_FILE.name,
                mime="text/plain",
                use_container_width=True
            )

    with col_dl2:
        if DETAILED_FILE.exists():
            with open(DETAILED_FILE, 'rb') as f:
                st.download_button(
                    label="📥 Download CSV",
                    data=f,
                    file_name=DETAILED_FILE.name,
                    mime="text/csv",
                    use_container_width=True
                )

    with col_dl3:
        if NICHE_CSV.exists():
            with open(NICHE_CSV, 'rb') as f:
                st.download_button(
                    label="📊 Download Ratings CSV",
                    data=f,
                    file_name="seo_ratings.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    st.success(f"""
    ✅ **Results saved to Desktop:**
    - `{OUTPUT_FILE.name}`
    - `{DETAILED_FILE.name}` (CSV)
    {'- `' + NICHE_CSV.name + '` (SEO Ratings)' if NICHE_CSV.exists() else ''}

    Use the download buttons above to get copies!
    """)

    # Check if there are "Active" results to verify
    if DETAILED_FILE.exists():
        import csv
        with open(DETAILED_FILE, 'r') as f:
            reader = csv.DictReader(f)
            results = list(reader)
            active_count = len([r for r in results if 'Active' in r.get('status', '')])

        if active_count > 0:
            st.markdown("---")
            st.subheader("🔬 Deep Verification")
            st.info(f"""
            Found **{active_count}** subdomains marked as "Active (verify manually)".

            Run deep verification to check if these are actually vulnerable by testing HTTP responses for takeover signatures.
            """)

            verify_running = VERIFY_PROGRESS.exists()

            col_verify1, col_verify2 = st.columns([1, 1])

            with col_verify1:
                if st.button("🔬 Run Deep Verification", disabled=verify_running, type="primary", use_container_width=True):
                    # Clean old verification files
                    for f in [VERIFIED_FILE, VERIFIED_CSV, VERIFY_PROGRESS, VERIFY_STATUS]:
                        if f.exists():
                            f.unlink()

                    # Create verification runner
                    verify_script = Path("run_verify_bg.sh")
                    verify_script.write_text("""#!/bin/bash
source venv/bin/activate
python verify_results.py
""")
                    verify_script.chmod(0o755)

                    # Start verification in background
                    subprocess.Popen(['./run_verify_bg.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    time.sleep(1)
                    st.rerun()

            with col_verify2:
                if st.button("⏹️ Stop Verification", disabled=not verify_running, type="secondary", use_container_width=True):
                    subprocess.run(['pkill', '-f', 'verify_results.py'], capture_output=True)
                    for f in [VERIFY_PROGRESS, VERIFY_STATUS]:
                        if f.exists():
                            f.unlink()
                    st.rerun()

            # Show verification progress
            if verify_running:
                st.markdown("### 🔄 Verification in Progress...")
                if VERIFY_STATUS.exists():
                    with open(VERIFY_STATUS) as f:
                        verify_lines = f.readlines()
                        if verify_lines:
                            for line in verify_lines:
                                st.text(line.strip())

# Display verified results
if VERIFIED_FILE.exists():
    st.markdown("---")
    st.subheader("✅ Verified Vulnerabilities")

    with open(VERIFIED_FILE) as f:
        verified_content = f.read()

    st.text_area("Verified High-Confidence Takeovers", verified_content, height=400)

    # Download verified results
    col_ver1, col_ver2 = st.columns(2)

    with col_ver1:
        with open(VERIFIED_FILE, 'rb') as f:
            st.download_button(
                label="📥 Download Verified TXT",
                data=f,
                file_name=VERIFIED_FILE.name,
                mime="text/plain",
                use_container_width=True
            )

    with col_ver2:
        if VERIFIED_CSV.exists():
            with open(VERIFIED_CSV, 'rb') as f:
                st.download_button(
                    label="📥 Download Verified CSV",
                    data=f,
                    file_name=VERIFIED_CSV.name,
                    mime="text/csv",
                    use_container_width=True
                )

    st.success(f"""
    🎯 **Verified results saved to Desktop:**
    - `{VERIFIED_FILE.name}`
    - `{VERIFIED_CSV.name}` (CSV)

    These are high-confidence subdomain takeover vulnerabilities!
    """)

    niche_running = NICHE_PROGRESS.exists()

    col_niche1, col_niche2 = st.columns([1, 1])

    with col_niche1:
        if st.button("🎯 Analyze Niches", disabled=niche_running, type="primary", use_container_width=True):
            # Clean old niche files
            for f in [NICHE_CSV, NICHE_PROGRESS, NICHE_STATUS]:
                if f.exists():
                    f.unlink()

            # Create niche analysis runner
            niche_script = Path("run_niche_bg.sh")
            niche_script.write_text("""#!/bin/bash
source venv/bin/activate
python niche_analyzer.py
""")
            niche_script.chmod(0o755)

            # Start niche analysis in background
            subprocess.Popen(['./run_niche_bg.sh'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
            st.rerun()

    with col_niche2:
        if st.button("⏹️ Stop Analysis", disabled=not niche_running, type="secondary", use_container_width=True):
            subprocess.run(['pkill', '-f', 'niche_analyzer.py'], capture_output=True)
            for f in [NICHE_PROGRESS, NICHE_STATUS]:
                if f.exists():
                    f.unlink()
            st.rerun()

    # Show niche analysis progress
    if niche_running:
        st.markdown("### 🔄 Analyzing Niches...")
        if NICHE_STATUS.exists():
            with open(NICHE_STATUS) as f:
                niche_lines = f.readlines()
                if niche_lines:
                    for line in niche_lines:
                        st.text(line.strip())

# Niche analysis complete - ratings already merged into main table above
if NICHE_CSV.exists():
    # Ratings already shown in main table above - just show download
    st.info(f"✅ SEO ratings complete - all data merged into main results table above")

    with open(NICHE_CSV, 'rb') as f:
        st.download_button(
            label="📥 Download Full Niche Analysis CSV",
            data=f,
            file_name=NICHE_CSV.name,
            mime="text/csv"
        )

# Bulk PoC Generation
if st.session_state.get('bulk_generate'):
    st.markdown("---")
    st.subheader("🚀 Bulk PoC Generation")

    if not st.session_state.creds['profile'].get('researcher_name'):
        st.error("Please set your profile in the sidebar first!")
        st.session_state.bulk_generate = False
    else:
        # Load all results
        import csv
        import zipfile
        import io

        with open(DETAILED_FILE, 'r') as f:
            reader = csv.DictReader(f)
            all_results = list(reader)

        st.info(f"Generating PoCs for {len(all_results)} vulnerabilities...")

        # Group by service
        by_service = {}
        for result in all_results:
            service = result['service'].lower()
            if service not in by_service:
                by_service[service] = []
            by_service[service].append(result)

        # Generate all PoCs
        all_files = []
        researcher_name = st.session_state.creds['profile']['researcher_name']

        for service, results in by_service.items():
            st.write(f"**{service.title()}**: {len(results)} found")

            for result in results:
                subdomain = result['subdomain']
                cname = result.get('cname', '')

                # Extract service-specific info and use saved credentials
                if 's3' in service:
                    bucket_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
                    region = st.session_state.creds['aws'].get('default_region', 'us-east-1')
                    poc_data = poc.gen_s3(subdomain, bucket_name, region, researcher_name)

                    # Add AWS credentials to commands if set
                    aws_key = st.session_state.creds['aws'].get('access_key_id', '')
                    aws_secret = st.session_state.creds['aws'].get('secret_access_key', '')
                    if aws_key and aws_secret:
                        poc_data['commands'] = f"""# AWS Credentials (configured)
export AWS_ACCESS_KEY_ID={aws_key}
export AWS_SECRET_ACCESS_KEY={aws_secret}
export AWS_DEFAULT_REGION={region}

""" + poc_data['commands']

                elif 'azure' in service:
                    app_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
                    location = st.session_state.creds['azure'].get('default_location', 'eastus')
                    poc_data = poc.gen_azure(subdomain, app_name, location, researcher_name)

                    # Add Azure subscription if set
                    azure_sub = st.session_state.creds['azure'].get('subscription_id', '')
                    if azure_sub:
                        poc_data['commands'] = f"az account set --subscription {azure_sub}\n\n" + poc_data['commands']

                elif 'github' in service:
                    github_cname = cname.replace('.github.io', '') if cname else subdomain.split('.')[0]
                    github_user = st.session_state.creds['github'].get('username', 'your-github')
                    poc_data = poc.gen_github(subdomain, github_cname, github_user, researcher_name)

                    # Add GitHub token auth if set
                    github_token = st.session_state.creds['github'].get('personal_access_token', '')
                    if github_token:
                        poc_data['commands'] = f"export GITHUB_TOKEN={github_token}\n\n" + poc_data['commands']

                elif 'heroku' in service:
                    app_name = cname.replace('.herokuapp.com', '') if cname else subdomain.split('.')[0]
                    poc_data = poc.gen_heroku(subdomain, app_name, researcher_name)

                    # Add Heroku API key if set
                    heroku_key = st.session_state.creds['heroku'].get('api_key', '')
                    if heroku_key:
                        poc_data['commands'] = f"export HEROKU_API_KEY={heroku_key}\n\n" + poc_data['commands']

                else:
                    continue  # Skip unsupported services for now

                # Add files to collection
                for filename, content in poc_data.get('files', []):
                    safe_subdomain = subdomain.replace('.', '_')
                    all_files.append((f"{safe_subdomain}/{filename}", content))

        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in all_files:
                zip_file.writestr(filename, content)

        zip_buffer.seek(0)

        st.success(f"✅ Generated {len(all_files)} files for {len(all_results)} vulnerabilities!")

        st.download_button(
            label="📥 Download All PoCs (ZIP)",
            data=zip_buffer,
            file_name=f"pocs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            use_container_width=True
        )

        if st.button("Done"):
            st.session_state.bulk_generate = False
            st.rerun()

# Single PoC Generation
elif st.session_state.get('show_poc_form'):
    st.markdown("---")
    st.subheader("📝 Generate Single PoC")

    result = st.session_state.selected_result
    subdomain = result['subdomain']
    service_name = result['service']
    cname = result.get('cname', '')
    researcher_name = st.session_state.creds['profile']['researcher_name']

    st.info(f"**Subdomain:** {subdomain}\n**Service:** {service_name}\n**CNAME:** {cname}")

    # Auto-extract service-specific details
    if 's3' in service_name.lower():
        bucket_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
        default_region = st.session_state.creds['aws'].get('default_region', 'us-east-1')
        region = st.selectbox("AWS Region", ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"],
                             index=["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"].index(default_region) if default_region in ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"] else 0)

        if st.button("Generate S3 PoC"):
            poc_data = poc.gen_s3(subdomain, bucket_name, region, researcher_name)

            # Add AWS credentials
            aws_key = st.session_state.creds['aws'].get('access_key_id', '')
            aws_secret = st.session_state.creds['aws'].get('secret_access_key', '')
            if aws_key and aws_secret:
                poc_data['commands'] = f"""# AWS Credentials (configured)
export AWS_ACCESS_KEY_ID={aws_key}
export AWS_SECRET_ACCESS_KEY={aws_secret}
export AWS_DEFAULT_REGION={region}

""" + poc_data['commands']

            st.success("✅ PoC Generated!")
            st.code(poc_data['commands'], language='bash')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 HTML", poc_data['html'], f"poc_{bucket_name}.html", "text/html")
            with col2:
                st.download_button("📥 Commands", poc_data['commands'], f"poc_{bucket_name}.sh", "text/plain")
            with col3:
                st.download_button("📥 CNAME", poc_data['cname'], "CNAME", "text/plain")

    elif 'azure' in service_name.lower():
        app_name = cname.split('.')[0] if cname else subdomain.split('.')[0]
        default_location = st.session_state.creds['azure'].get('default_location', 'eastus')
        location = st.selectbox("Azure Location", ["eastus", "westus", "westus2", "northeurope", "westeurope"],
                               index=["eastus", "westus", "westus2", "northeurope", "westeurope"].index(default_location) if default_location in ["eastus", "westus", "westus2", "northeurope", "westeurope"] else 0)

        if st.button("Generate Azure PoC"):
            poc_data = poc.gen_azure(subdomain, app_name, location, researcher_name)

            # Add Azure subscription
            azure_sub = st.session_state.creds['azure'].get('subscription_id', '')
            if azure_sub:
                poc_data['commands'] = f"az account set --subscription {azure_sub}\n\n" + poc_data['commands']

            st.success("✅ PoC Generated!")
            st.code(poc_data['commands'], language='bash')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 HTML", poc_data['html'], f"poc_{app_name}.html", "text/html")
            with col2:
                st.download_button("📥 Commands", poc_data['commands'], f"poc_{app_name}.sh", "text/plain")
            with col3:
                st.download_button("📥 CNAME", poc_data['cname'], "CNAME", "text/plain")

    elif 'github' in service_name.lower():
        github_cname = cname.replace('.github.io', '') if cname else subdomain.split('.')[0]
        github_user = st.session_state.creds['github'].get('username', 'your-github')

        if st.button("Generate GitHub PoC"):
            poc_data = poc.gen_github(subdomain, github_cname, github_user, researcher_name)

            # Add GitHub token if set
            github_token = st.session_state.creds['github'].get('personal_access_token', '')
            if github_token:
                poc_data['commands'] = f"export GITHUB_TOKEN={github_token}\n\n" + poc_data['commands']

            st.success("✅ PoC Generated!")
            st.code(poc_data['commands'], language='bash')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 HTML", poc_data['html'], f"poc_{github_cname}.html", "text/html")
            with col2:
                st.download_button("📥 Commands", poc_data['commands'], f"poc_{github_cname}.sh", "text/plain")
            with col3:
                st.download_button("📥 CNAME", poc_data['cname'], "CNAME", "text/plain")

    elif 'heroku' in service_name.lower():
        app_name = cname.replace('.herokuapp.com', '') if cname else subdomain.split('.')[0]

        if st.button("Generate Heroku PoC"):
            poc_data = poc.gen_heroku(subdomain, app_name, researcher_name)

            # Add Heroku API key if set
            heroku_key = st.session_state.creds['heroku'].get('api_key', '')
            if heroku_key:
                poc_data['commands'] = f"export HEROKU_API_KEY={heroku_key}\n\n" + poc_data['commands']

            st.success("✅ PoC Generated!")
            st.code(poc_data['commands'], language='bash')

            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 HTML", poc_data['html'], f"poc_{app_name}.html", "text/html")
            with col2:
                st.download_button("📥 Commands", poc_data['commands'], f"poc_{app_name}.sh", "text/plain")
            with col3:
                st.download_button("📥 CNAME", poc_data['cname'], "CNAME", "text/plain")

    else:
        st.warning(f"PoC generator for {service_name} coming soon!")

    if st.button("← Back"):
        st.session_state.show_poc_form = False
        st.rerun()

# Auto-refresh
verify_running = VERIFY_PROGRESS.exists()
niche_running = NICHE_PROGRESS.exists()
if scan_running or verify_running or niche_running or pipeline_running:
    time.sleep(2)
    st.rerun()
