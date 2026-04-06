#!/usr/bin/env python3
"""
Gmail API Setup Script
Erstellt die Struktur für Gmail Automation
"""
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), ".config", "gmail_api.json")

DEFAULT_CONFIG = {
    "enabled": False,
    "credentials_path": "credentials.json",
    "token_path": "token.json",
    "scopes": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send"
    ]
}

def setup_gmail_api():
    """Richtet Gmail API Struktur ein"""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"✅ Config erstellt: {CONFIG_FILE}")
    else:
        print("⚠️ Config existiert bereits")
    
    print("\n📋 Nächste Schritte:")
    print("1. Gehe zu: https://console.cloud.google.com/")
    print("2. Erstelle Projekt → Gmail API → Credentials")
    print("3. OAuth Client ID → Desktop App")
    print("4. Download credentials.json")
    print("5. Speichere unter: .config/gmail_api/credentials.json")

if __name__ == "__main__":
    setup_gmail_api()
