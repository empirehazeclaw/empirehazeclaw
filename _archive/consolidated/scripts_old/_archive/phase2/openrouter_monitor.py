#!/usr/bin/env python3
"""
Sir HazeClaw OpenRouter Monitor
Überwacht ob OpenRouter API funktioniert.

Usage:
    python3 openrouter_monitor.py
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

CONFIG_PATH = "/home/clawbot/.openclaw/openclaw.json"
LOG_FILE = "/home/clawbot/.openclaw/workspace/logs/openrouter_monitor.log"

def get_openrouter_config():
    """Liest OpenRouter Config."""
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    
    models = config.get('models', {})
    providers = models.get('providers', {})
    
    return providers.get('openrouter', {})

def check_openrouter():
    """Testet OpenRouter API."""
    config = get_openrouter_config()
    if not config:
        return False, "OpenRouter not configured"
    
    base_url = config.get('baseUrl', 'https://openrouter.ai/api/v1')
    
    # Test mit einem einfachen Request
    try:
        # Einfacher Test ohne API Key
        req = urllib.request.Request(f"{base_url}/models")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                return True, "API responding"
            else:
                return False, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, "401 Unauthorized - API Key invalide"
        elif e.code == 403:
            return False, "403 Forbidden - Rate limit?"
        else:
            return False, f"HTTP {e.code}"
    except Exception as e:
        return False, f"Error: {e}"

def log_status(ok, msg):
    """Loggt Status."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        status = "OK" if ok else "FAIL"
        f.write(f"[{timestamp}] {status} {msg}\n")

def main():
    print(f"OpenRouter Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    ok, msg = check_openrouter()
    
    print(f"Status: {'OK' if ok else 'FAIL'} - {msg}")
    
    log_status(ok, msg)
    
    if not ok:
        print()
        print("ACTION NEEDED:")
        if "401" in msg:
            print("  - OpenRouter API Key ist invalide/expired")
            print("  - Master muss neuen Key generieren")
            print("  - Siehe: /workspace/ceo/OPENROUTER_ISSUE.md")
    
    print("=" * 60)
    
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
