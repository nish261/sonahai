#!/usr/bin/env python3
"""
Desktop Notification Helper for Subdomain Takeover Scanner
Sends macOS notifications for important events
"""

import subprocess
import os
from pathlib import Path

def send_notification(title, message, sound=True):
    """
    Send a macOS desktop notification

    Args:
        title (str): Notification title
        message (str): Notification message
        sound (bool): Whether to play sound (default: True)
    """
    try:
        # Try using pync first (better notifications)
        try:
            import pync
            pync.notify(
                message,
                title=title,
                sound='default' if sound else None,
                group='SubdomainTakeover'
            )
            return
        except ImportError:
            pass

        # Fallback to osascript (built-in macOS)
        sound_param = 'with sound name "default"' if sound else ''
        script = f'''
        display notification "{message}" with title "{title}" {sound_param}
        '''

        subprocess.run(
            ['osascript', '-e', script],
            check=False,
            capture_output=True
        )
    except Exception as e:
        # Silent fail - don't interrupt the scanner
        print(f"⚠️  Notification failed: {e}")


def notify_scan_started(domain, mode="simple"):
    """Notify when scan starts"""
    send_notification(
        title="🔍 Scan Started",
        message=f"Scanning {domain} ({mode} mode)",
        sound=True
    )


def notify_scan_complete(vulnerabilities_found, total_subdomains):
    """Notify when scan completes"""
    if vulnerabilities_found > 0:
        send_notification(
            title="✅ Scan Complete - Vulnerabilities Found!",
            message=f"Found {vulnerabilities_found} vulnerable subdomains out of {total_subdomains} scanned",
            sound=True
        )
    else:
        send_notification(
            title="✅ Scan Complete",
            message=f"Scanned {total_subdomains} subdomains - no vulnerabilities found",
            sound=False
        )


def notify_verification_started(total_results):
    """Notify when verification starts"""
    send_notification(
        title="🔬 Verification Started",
        message=f"Deep verification of {total_results} potential vulnerabilities",
        sound=False
    )


def notify_verification_complete(verified_count, total_checked):
    """Notify when verification completes"""
    if verified_count > 0:
        send_notification(
            title="✅ Verification Complete - Real Vulnerabilities!",
            message=f"Confirmed {verified_count} real vulnerabilities out of {total_checked} checked",
            sound=True
        )
    else:
        send_notification(
            title="✅ Verification Complete",
            message=f"Checked {total_checked} results - no confirmed vulnerabilities",
            sound=False
        )


def notify_niche_analysis_complete(high_priority_count, total_analyzed):
    """Notify when niche analysis completes"""
    if high_priority_count > 0:
        send_notification(
            title="💰 Niche Analysis Complete - High-Value Targets!",
            message=f"Found {high_priority_count} high-priority CPA targets out of {total_analyzed} analyzed",
            sound=True
        )
    else:
        send_notification(
            title="💰 Niche Analysis Complete",
            message=f"Analyzed {total_analyzed} domains",
            sound=False
        )


def notify_error(error_message):
    """Notify on error"""
    send_notification(
        title="❌ Scanner Error",
        message=error_message[:100],  # Limit message length
        sound=True
    )


def notify_vulnerability_found(subdomain, service, cpa_vertical=None):
    """Notify when a single vulnerability is found during scan"""
    if cpa_vertical:
        msg = f"{subdomain}\n{service}\n{cpa_vertical} vertical"
    else:
        msg = f"{subdomain}\n{service}"

    send_notification(
        title="🎯 Vulnerability Found!",
        message=msg,
        sound=True
    )


def notify_high_value_target(subdomain, cpa_vertical, cpa_value, trust_score):
    """Notify when a high-value CPA target is found"""
    send_notification(
        title=f"💎 HIGH-VALUE TARGET: {cpa_vertical}",
        message=f"{subdomain}\n{cpa_value}\nTrust Score: {trust_score}/100",
        sound=True
    )


# Test function
if __name__ == "__main__":
    print("Testing notifications...")

    send_notification(
        title="🧪 Test Notification",
        message="Subdomain Takeover Scanner notification system is working!",
        sound=True
    )

    print("✅ Test notification sent!")
    print("If you didn't see a notification, check System Preferences → Notifications")
