# How to Run the Subdomain Takeover Scanner

## Quick Start

Open Terminal and run:

```bash
cd ~
python3 aggressive_scanner.py 1 1000
```

This scans the **top 1000 domains** from the Tranco list.

## Command Format

```bash
python3 aggressive_scanner.py <start_rank> <num_domains> [extensions] [enum_workers] [scan_workers]
```

### Parameters:

1. **start_rank** (required): Starting position in domain rankings (1 = #1 ranked domain)
2. **num_domains** (required): How many domains to scan
3. **extensions** (optional): Filter by domain extensions (default: ALL)
4. **enum_workers** (optional): Parallel workers for enumeration (default: 10)
5. **scan_workers** (optional): Parallel workers for scanning (default: 30)

## Examples

### Scan Top 1000 Domains
```bash
python3 aggressive_scanner.py 1 1000
```

### Scan Lower-Ranked Domains (Better Results!)
```bash
# Ranks 5000-6000 (more vulnerabilities found here)
python3 aggressive_scanner.py 5000 1000
```

### Scan Specific Extensions Only
```bash
# Only .gov and .edu domains
python3 aggressive_scanner.py 1 1000 ".gov,.edu"
```

### Faster Scanning (More Workers)
```bash
# 20 enumeration workers + 50 scan workers
python3 aggressive_scanner.py 1 1000 ALL 20 50
```

### Smaller Test Scan
```bash
# Just scan 100 domains to test
python3 aggressive_scanner.py 1 100
```

## Running in Background

To run without keeping terminal open:

```bash
nohup python3 aggressive_scanner.py 1 1000 > scanner.log 2>&1 &
```

## Monitor Progress

### Check Progress Percentage
```bash
cat scan_progress.txt
```

### Watch Live Status
```bash
tail -f scan_status.txt
```

### View Scanner Log
```bash
tail -f scanner.log
```

## View Results

Results are saved to your Desktop:

```bash
# View all results
cat ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv

# Count vulnerabilities found
wc -l ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_detailed.csv

# View summary
cat ~/Desktop/Subdomain_Takeover_Results/Scans/subdomain_takeover_results.txt
```

## Stop the Scanner

If you need to stop it:

```bash
# Find the process
ps aux | grep aggressive_scanner

# Kill it (replace XXXX with the PID)
kill XXXX
```

## Tips for Best Results

1. **Lower-ranked domains** (5000-15000) have MORE vulnerabilities
2. **Run overnight** - scanning 1000 domains takes 30-60 minutes
3. **Use background mode** for long scans
4. **Check ~/Desktop** for results when complete

## Troubleshooting

### "Module not found" error?
```bash
pip3 install --break-system-packages tranco requests
```

### "Subdominator not found"?
The scanner will still work but be slower. Results will still be accurate.

### No results found?
- Try lower-ranked domains (5000+)
- Increase the number of domains scanned
- Check scan_status.txt for errors
