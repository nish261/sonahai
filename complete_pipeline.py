#!/usr/bin/env python3
"""
Complete Subdomain Takeover Pipeline
Runs: Scan → Verify → Analyze Niches - All in One
"""

import subprocess
import time
import sys
from pathlib import Path

def update_progress(stage, progress, message):
    """Update progress files for UI"""
    progress_file = Path("pipeline_progress.txt")
    status_file = Path("pipeline_status.txt")

    progress_file.write_text(str(progress))
    status_file.write_text(f"{stage}\n{message}")

    print(f"[{progress}%] {stage}: {message}")

def run_scan(start_rank, num_domains, extensions, enum_workers, scan_workers):
    """Stage 1: Run initial scan"""
    update_progress("Stage 1/3: Scanning", 0, "Starting subdomain enumeration...")

    # Run scanner
    cmd = [
        'python', 'aggressive_scanner.py',
        str(start_rank),
        str(num_domains),
        extensions,
        str(enum_workers),
        str(scan_workers)
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Monitor progress
    while True:
        # Check if process is done
        if process.poll() is not None:
            break

        # Read progress from scan_progress.txt
        progress_file = Path("scan_progress.txt")
        if progress_file.exists():
            try:
                scan_progress = int(progress_file.read_text().strip())
                # Map 0-100 scan progress to 0-33 overall progress
                overall_progress = int(scan_progress * 0.33)

                # Read status
                status_file = Path("scan_status.txt")
                if status_file.exists():
                    lines = status_file.read_text().strip().split('\n')
                    status_msg = lines[0] if lines else "Scanning..."
                else:
                    status_msg = f"Scanning... {scan_progress}%"

                update_progress("Stage 1/3: Scanning", overall_progress, status_msg)
            except:
                pass

        time.sleep(2)

    # Wait for process to finish
    process.wait()

    if process.returncode != 0:
        update_progress("Stage 1/3: Scanning", 33, "❌ Scan failed!")
        return False

    update_progress("Stage 1/3: Scanning", 33, "✅ Scan complete!")
    time.sleep(1)
    return True

def run_verification():
    """Stage 2: Deep verification"""
    update_progress("Stage 2/3: Verification", 33, "Starting deep verification...")

    # Check if there are results to verify
    detailed_file = Path.home() / "Desktop" / "subdomain_takeover_detailed.csv"
    if not detailed_file.exists():
        update_progress("Stage 2/3: Verification", 66, "⚠️ No results to verify")
        return True

    # Read to check for "Active" results
    import csv
    with open(detailed_file, 'r') as f:
        reader = csv.DictReader(f)
        results = list(reader)
        active_count = len([r for r in results if 'Active' in r.get('status', '')])

    if active_count == 0:
        update_progress("Stage 2/3: Verification", 66, "⚠️ No active results to verify")
        return True

    # Run verification
    cmd = ['python', 'verify_results.py']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Monitor progress
    while True:
        # Check if process is done
        if process.poll() is not None:
            break

        # Read progress from verify_progress.txt
        progress_file = Path("verify_progress.txt")
        if progress_file.exists():
            try:
                verify_progress = int(progress_file.read_text().strip())
                # Map 0-100 verify progress to 33-66 overall progress
                overall_progress = 33 + int(verify_progress * 0.33)

                # Read status
                status_file = Path("verify_status.txt")
                if status_file.exists():
                    lines = status_file.read_text().strip().split('\n')
                    status_msg = lines[0] if lines else "Verifying..."
                else:
                    status_msg = f"Verifying {active_count} results... {verify_progress}%"

                update_progress("Stage 2/3: Verification", overall_progress, status_msg)
            except:
                pass

        time.sleep(2)

    # Wait for process to finish
    process.wait()

    if process.returncode != 0:
        update_progress("Stage 2/3: Verification", 66, "❌ Verification failed!")
        return False

    update_progress("Stage 2/3: Verification", 66, "✅ Verification complete!")
    time.sleep(1)
    return True

def run_niche_analysis():
    """Stage 3: Niche analysis"""
    update_progress("Stage 3/3: Niche Analysis", 66, "Analyzing SEO value and ratings...")

    # Check if there are scan results
    desktop = Path.home() / "Desktop"
    results_folder = desktop / "Subdomain_Takeover_Results"
    scans_folder = results_folder / "Scans"
    detailed_csv = scans_folder / "subdomain_takeover_detailed.csv"

    if not detailed_csv.exists():
        update_progress("Stage 3/3: Niche Analysis", 100, "⚠️ No scan results to analyze")
        return True

    # Run niche analysis on scan results
    cmd = ['python', 'niche_analyzer.py', str(detailed_csv)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    # Monitor progress
    while True:
        # Check if process is done
        if process.poll() is not None:
            break

        # Read progress from niche_progress.txt
        progress_file = Path("niche_progress.txt")
        if progress_file.exists():
            try:
                niche_progress = int(progress_file.read_text().strip())
                # Map 0-100 niche progress to 66-100 overall progress
                overall_progress = 66 + int(niche_progress * 0.34)

                # Read status
                status_file = Path("niche_status.txt")
                if status_file.exists():
                    status_msg = status_file.read_text().strip()
                else:
                    status_msg = f"Analyzing niches... {niche_progress}%"

                update_progress("Stage 3/3: Niche Analysis", overall_progress, status_msg)
            except:
                pass

        time.sleep(2)

    # Wait for process to finish
    process.wait()

    if process.returncode != 0:
        update_progress("Stage 3/3: Niche Analysis", 100, "❌ Analysis failed!")
        return False

    update_progress("Stage 3/3: Niche Analysis", 100, "✅ Niche analysis complete!")
    time.sleep(1)
    return True

def run_complete_pipeline(start_rank, num_domains, extensions, enum_workers, scan_workers):
    """Run the complete pipeline"""
    print("="*60)
    print("🚀 Starting Complete Subdomain Takeover Pipeline")
    print("="*60)
    print(f"Target: Ranks {start_rank:,} - {start_rank + num_domains:,}")
    print(f"Extensions: {extensions if extensions != 'ALL' else 'All'}")
    print(f"Workers: {enum_workers} enum, {scan_workers} scan")
    print("="*60)

    # Clean old progress files
    for f in ['pipeline_progress.txt', 'pipeline_status.txt']:
        p = Path(f)
        if p.exists():
            p.unlink()

    # Stage 1: Scan
    if not run_scan(start_rank, num_domains, extensions, enum_workers, scan_workers):
        print("\n❌ Pipeline failed at Stage 1: Scanning")
        return False

    # Stage 2: Verification
    if not run_verification():
        print("\n❌ Pipeline failed at Stage 2: Verification")
        return False

    # Stage 3: Niche Analysis
    if not run_niche_analysis():
        print("\n❌ Pipeline failed at Stage 3: Niche Analysis")
        return False

    # Complete!
    update_progress("Complete", 100, "✅ All stages complete!")

    print("\n" + "="*60)
    print("✅ Complete Pipeline Finished Successfully!")
    print("="*60)
    print("\n📊 Results saved to Desktop:")
    print("  • subdomain_takeover_results.txt")
    print("  • subdomain_takeover_detailed.csv")
    print("  • verified_vulnerabilities.txt")
    print("  • verified_vulnerabilities.csv")
    print("  • niche_analysis.csv")
    print("\n🎯 Check the UI for detailed results!")
    print("="*60)

    # Clean up progress files
    time.sleep(2)
    for f in ['pipeline_progress.txt', 'pipeline_status.txt']:
        p = Path(f)
        if p.exists():
            p.unlink()

    return True

if __name__ == "__main__":
    # Get parameters from command line
    if len(sys.argv) < 6:
        print("Usage: python complete_pipeline.py <start_rank> <num_domains> <extensions> <enum_workers> <scan_workers>")
        sys.exit(1)

    start_rank = int(sys.argv[1])
    num_domains = int(sys.argv[2])
    extensions = sys.argv[3]
    enum_workers = int(sys.argv[4])
    scan_workers = int(sys.argv[5])

    success = run_complete_pipeline(start_rank, num_domains, extensions, enum_workers, scan_workers)
    sys.exit(0 if success else 1)
