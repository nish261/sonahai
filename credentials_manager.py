"""
Secure Credentials Manager
Encrypts and stores platform credentials
"""

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

CREDS_FILE = Path.home() / ".bugbounty_creds.enc"
KEY_FILE = Path.home() / ".bugbounty_key"

def get_or_create_key():
    """Get encryption key or create new one"""
    if KEY_FILE.exists():
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        KEY_FILE.write_bytes(key)
        KEY_FILE.chmod(0o600)  # Read/write for owner only
        return key

def encrypt_data(data):
    """Encrypt credentials data"""
    key = get_or_create_key()
    f = Fernet(key)
    json_data = json.dumps(data)
    encrypted = f.encrypt(json_data.encode())
    return encrypted

def decrypt_data():
    """Decrypt credentials data"""
    if not CREDS_FILE.exists():
        return {}

    try:
        key = get_or_create_key()
        f = Fernet(key)
        encrypted = CREDS_FILE.read_bytes()
        decrypted = f.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except:
        return {}

def save_credentials(creds):
    """Save encrypted credentials"""
    encrypted = encrypt_data(creds)
    CREDS_FILE.write_bytes(encrypted)
    CREDS_FILE.chmod(0o600)  # Read/write for owner only

def get_proxy_env():
    """Get proxy environment variables from credentials"""
    creds = load_credentials()
    if not creds or not creds.get('proxy', {}).get('enabled', False):
        return {}

    proxy_config = creds['proxy']
    env_vars = {}

    # Build proxy URLs with auth if needed
    for proto in ['http', 'https']:
        proxy_url = proxy_config.get(proto, '')
        if proxy_url:
            # Add auth if provided
            if proxy_config.get('username') and proxy_config.get('password'):
                # Parse URL and inject auth
                if '://' in proxy_url:
                    protocol, rest = proxy_url.split('://', 1)
                    proxy_url = f"{protocol}://{proxy_config['username']}:{proxy_config['password']}@{rest}"

            env_vars[f'{proto.upper()}_PROXY'] = proxy_url
            env_vars[f'{proto}_proxy'] = proxy_url  # lowercase for compatibility

    return env_vars

def load_credentials():
    """Load and decrypt credentials"""
    return decrypt_data()

def delete_credentials():
    """Delete all stored credentials"""
    if CREDS_FILE.exists():
        CREDS_FILE.unlink()
    if KEY_FILE.exists():
        KEY_FILE.unlink()

# Default credential structure
def get_default_creds():
    return {
        'profile': {
            'researcher_name': '',
            'researcher_email': '',
        },
        'proxy': {
            'enabled': False,
            'http': '',
            'https': '',
            'username': '',
            'password': '',
        },
        'aws': {
            'access_key_id': '',
            'secret_access_key': '',
            'profile_name': 'default',
            'default_region': 'us-east-1',
        },
        'azure': {
            'username': '',
            'password': '',
            'subscription_id': '',
            'tenant_id': '',
            'default_location': 'eastus',
        },
        'github': {
            'username': '',
            'password': '',
            'email': '',
            'personal_access_token': '',
        },
        'heroku': {
            'email': '',
            'password': '',
            'api_key': '',
        },
        'digitalocean': {
            'email': '',
            'password': '',
            'api_token': '',
            'default_region': 'nyc3',
        },
        'shopify': {
            'email': '',
            'password': '',
            'partner_api_key': '',
            'partner_api_secret': '',
        },
        'wordpress': {
            'username': '',
            'password': '',
            'email': '',
        },
        'cloudflare': {
            'email': '',
            'api_key': '',
            'api_token': '',
        },
        'moz': {
            'access_id': '',
            'secret_key': '',
        },
    }

def merge_creds(existing, new_data):
    """Merge new credentials with existing ones"""
    result = existing.copy()
    for platform, values in new_data.items():
        if platform not in result:
            result[platform] = {}
        result[platform].update(values)
    return result
