#!/bin/bash
# Launch the Subdomain Takeover Scanner UI

echo "🚀 Starting Subdomain Takeover Scanner UI..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run Streamlit
streamlit run subdomain_scanner_ui.py

# Deactivate when done
deactivate
