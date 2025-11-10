#!/bin/bash
# Monitor the aggressive scanner in real-time

clear
echo "=========================================="
echo "  SUBDOMAIN TAKEOVER SCANNER - MONITOR"
echo "=========================================="
echo ""

while true; do
    # Get progress
    PROGRESS=$(cat scan_progress.txt 2>/dev/null || echo "0")
    
    # Get latest status lines
    STATUS=$(tail -5 scan_status.txt 2>/dev/null)
    
    # Clear and display
    clear
    echo "=========================================="
    echo "  SUBDOMAIN TAKEOVER SCANNER - MONITOR"
    echo "=========================================="
    echo ""
    echo "Progress: ${PROGRESS}%"
    echo ""
    echo "Recent Activity:"
    echo "----------------------------------------"
    echo "$STATUS"
    echo "----------------------------------------"
    echo ""
    echo "Press Ctrl+C to exit (scanner keeps running)"
    echo ""
    
    # Check if done
    if [ -f "scan_progress.txt" ]; then
        if [ "$PROGRESS" -eq "100" ]; then
            echo "✅ SCAN COMPLETE!"
            echo ""
            echo "Results saved to:"
            echo "  ~/Desktop/Subdomain_Takeover_Results/Scans/"
            break
        fi
    fi
    
    sleep 5
done
