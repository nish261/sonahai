#!/bin/bash
# Deep verification of potential subdomain takeovers

echo "🔍 Starting Deep Verification..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Run verification
python3 verify_results.py

# Deactivate when done
deactivate
