#!/bin/bash
# Helper script to run the domain fetcher with the virtual environment

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing tranco..."
    pip install tranco
else
    source venv/bin/activate
fi

# Run the script
python fetch_top_domains.py

# Deactivate when done
deactivate
