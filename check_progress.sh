#!/bin/bash
# Check progress of domain fetching script

echo "=========================================="
echo "Domain Fetcher Progress"
echo "=========================================="
echo

# Check if script is running
if ps aux | grep -q "[p]ython run_fetcher_usa.py"; then
    echo "✓ Script is RUNNING"
    echo

    # Count running subfinder processes
    subfinder_count=$(ps aux | grep -c "[s]ubfinder")
    if [ $subfinder_count -gt 0 ]; then
        echo "Active subfinder workers: $subfinder_count"
        echo
    fi

    # Check what's being processed
    echo "Currently processing:"
    ps aux | grep "[s]ubfinder" | awk '{print "  - " $13}' | head -5
    if [ $(ps aux | grep -c "[s]ubfinder") -gt 5 ]; then
        echo "  ... and $(($(ps aux | grep -c '[s]ubfinder') - 5)) more"
    fi
    echo
else
    echo "✗ Script is NOT running (completed or not started)"
    echo
fi

# Check output files
echo "Output files:"
if [ -f "top_domains_usa.txt" ]; then
    domains_count=$(wc -l < top_domains_usa.txt)
    echo "  Domains fetched: $domains_count"
fi

if [ -f "subdomains_all_usa.txt" ]; then
    all_subs=$(wc -l < subdomains_all_usa.txt)
    echo "  All subdomains found: $all_subs"
fi

if [ -f "subdomains_filtered_usa.txt" ]; then
    filtered_subs=$(wc -l < subdomains_filtered_usa.txt)
    echo "  Filtered subdomains: $filtered_subs"

    if [ $all_subs -gt 0 ] && [ $filtered_subs -gt 0 ]; then
        match_rate=$(awk "BEGIN {printf \"%.2f\", ($filtered_subs/$all_subs)*100}")
        echo "  Match rate: ${match_rate}%"
    fi
fi

echo
echo "=========================================="
