#!/usr/bin/env python3
"""
Universal Credentials Loader
Loads all credentials from account_details.json for automated PoC claiming
"""

import json
import os
from pathlib import Path

def load_all_credentials():
    """
    Load credentials from account_details.json

    Returns:
        dict: All credentials, or None if file doesn't exist
    """
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent / "account_details.json",
        Path.home() / ".subdomain_scanner" / "account_details.json",
        Path.home() / "Desktop" / "scanner-app" / "account_details.json",
    ]

    for creds_file in possible_paths:
        if creds_file.exists():
            try:
                with open(creds_file) as f:
                    creds = json.load(f)
                print(f"✓ Loaded credentials from: {creds_file}")
                return creds
            except Exception as e:
                print(f"⚠️  Error loading credentials from {creds_file}: {e}")
                continue

    print("❌ No account_details.json found!")
    print("   Create one using: cp account_details_TEMPLATE.json account_details.json")
    return None

def get_aws_credentials():
    """Get AWS credentials."""
    creds = load_all_credentials()
    if not creds:
        return None, None, None

    aws = creds.get('aws', {})
    return (
        aws.get('access_key_id'),
        aws.get('secret_access_key'),
        aws.get('default_region', 'us-east-1')
    )

def get_azure_credentials():
    """Get Azure credentials."""
    creds = load_all_credentials()
    if not creds:
        return None

    return creds.get('azure', {})

def get_github_credentials():
    """Get GitHub credentials."""
    creds = load_all_credentials()
    if not creds:
        return None, None

    github = creds.get('github', {})
    return (
        github.get('username'),
        github.get('personal_access_token')
    )

def get_researcher_profile():
    """Get researcher profile information."""
    creds = load_all_credentials()
    if not creds:
        return None, None

    profile = creds.get('researcher_profile', {})
    return (
        profile.get('name', 'Anonymous Researcher'),
        profile.get('email', '')
    )

def get_proxy_settings():
    """Get proxy settings if enabled."""
    creds = load_all_credentials()
    if not creds:
        return None

    proxy = creds.get('proxy', {})
    if not proxy.get('enabled', False):
        return None

    return proxy

def setup_aws_environment():
    """Set up AWS environment variables from credentials."""
    access_key, secret_key, region = get_aws_credentials()

    if access_key and secret_key:
        os.environ['AWS_ACCESS_KEY_ID'] = access_key
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        os.environ['AWS_DEFAULT_REGION'] = region
        print(f"✓ AWS credentials loaded (region: {region})")
        return True
    else:
        print("⚠️  AWS credentials not found in account_details.json")
        return False

def setup_proxy_environment():
    """Set up proxy environment variables."""
    proxy = get_proxy_settings()

    if proxy:
        if proxy.get('http_proxy'):
            os.environ['HTTP_PROXY'] = proxy['http_proxy']
            os.environ['http_proxy'] = proxy['http_proxy']

        if proxy.get('https_proxy'):
            os.environ['HTTPS_PROXY'] = proxy['https_proxy']
            os.environ['https_proxy'] = proxy['https_proxy']

        print("✓ Proxy settings loaded")
        return True

    return False

def validate_credentials():
    """
    Validate that required credentials are present.

    Returns:
        dict: Status of each platform's credentials
    """
    creds = load_all_credentials()
    if not creds:
        return {}

    status = {}

    # Check AWS
    aws = creds.get('aws', {})
    status['aws'] = bool(aws.get('access_key_id') and aws.get('secret_access_key'))

    # Check Azure
    azure = creds.get('azure', {})
    # Azure can work with just CLI login
    status['azure'] = True  # Assume CLI is configured

    # Check GitHub
    github = creds.get('github', {})
    status['github'] = bool(github.get('username') and github.get('personal_access_token'))

    # Check profile
    profile = creds.get('researcher_profile', {})
    status['researcher_profile'] = bool(profile.get('name'))

    return status

def print_credentials_status():
    """Print a nice status summary of loaded credentials."""
    status = validate_credentials()

    if not status:
        print("❌ No credentials loaded")
        return

    print("\n" + "="*60)
    print("📋 CREDENTIALS STATUS")
    print("="*60)

    print(f"AWS:               {'✅ Configured' if status.get('aws') else '❌ Not configured'}")
    print(f"Azure:             {'✅ CLI login (run az login)' if status.get('azure') else '❌ Not configured'}")
    print(f"GitHub:            {'✅ Configured' if status.get('github') else '❌ Not configured'}")
    print(f"Researcher Profile: {'✅ Configured' if status.get('researcher_profile') else '❌ Not configured'}")

    print("="*60 + "\n")

if __name__ == "__main__":
    # Test the credentials loader
    print("Testing credentials loader...\n")

    creds = load_all_credentials()
    if creds:
        print_credentials_status()

        # Test loading specific credentials
        name, email = get_researcher_profile()
        print(f"Researcher: {name}")
        if email:
            print(f"Email: {email}")

        print("\n✅ Credentials loader working correctly!")
    else:
        print("\n❌ No credentials file found.")
        print("   1. Copy the template: cp account_details_TEMPLATE.json account_details.json")
        print("   2. Fill in your credentials")
        print("   3. Run this script again to verify")
