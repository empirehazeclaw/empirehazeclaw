#!/usr/bin/env python3
"""
📱 Telegram Alert Script
Sendet Alerts nur bei PROBLEMEN/WARNUNGEN

Usage:
    python3 telegram_alert.py "Deine Warnung hier"
"""

import os
import sys
import requests
from pathlib import Path

def load_secrets():
    """Load secrets from .secrets/secrets.env"""
    secrets_file = Path.home() / ".secrets" / "secrets.env"
    if secrets_file.exists():
        with open(secrets_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def send_alert(message: str):
    """Send Telegram alert"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = "5392634979"
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN nicht gefunden")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": f"⚠️ ALERT\n\n{message}",
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print(f"✅ Alert gesendet")
            return True
        else:
            print(f"❌ Telegram Error: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: telegram_alert.py <message>")
        sys.exit(1)
    
    message = " ".join(sys.argv[1:])
    
    load_secrets()
    send_alert(message)

if __name__ == "__main__":
    main()
