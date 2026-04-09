#!/usr/bin/env python3
"""
Browser Security Layer
Schützt vor gefährlichen Browser-Aktionen
"""

import re
import json
import os
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/logs/browser_security.log"

# Blockierte Domains (böswillige/Phishing)
BLOCKED_DOMAINS = [
    r".*\.tk$", r".*\.ml$", r".*\.ga$",  # Kostenlose TLDs oft missbraucht
    r".*bitcoin.*", r".*crypto.*scam",
    r".*phishing.*", r".*malware.*",
]

# Aktionen die Bestätigung brauchen
CONFIRM_ACTIONS = [
    r"login", r"signin", r"password", r"passwort",
    r"buy", r"purchase", r"kauf", r"bestell",
    r"pay", r"payment", r"zahl",
    r"delete", r"remove", r"löschen",
    r"submit.*form", r"send.*form",
    r"transfer", r"überweisung",
    r"download.*exe", r"download.*zip",
]

# Erlaubte Domains (Whitelist - optional)
ALLOWED_DOMAINS = [
    r"etsy\.com", r"printful\.com", r"printify\.com",
    r"github\.com", r"gitlab\.com",
    r"google\.com", r"youtube\.com",
    r"reddit\.com", r"twitter\.com", r"x\.com",
    r"instagram\.com", r"tiktok\.com",
    r"fiverr\.com", r"upwork\.com",
    r"amazon\.de", r"ebay\.de",
    r"openrouter\.ai", r"minimax\.io",
    r"discord\.com", r"telegram\.org",
]

# Browser-Einschränkungen
BROWSER_RESTRICTIONS = {
    "allow_downloads": False,      # ❌ Deaktiviert
    "allow_clipboard": False,      # ❌ Deaktiviert  
    "allow_screenshots": True,     # ✅ Erlaubt
    "auto_clear_session": True,    # ✅ Nach jeder Session löschen
}

def log_action(action: str, details: str, blocked: bool = False):
    """Logge Browser-Aktion"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        status = "🚫 BLOCKED" if blocked else "✅ ALLOWED"
        f.write(f"[{datetime.utcnow().isoformat()}] {status}: {action} - {details}\n")

def clear_browser_session():
    """Lösche Browser-Session nach jeder Nutzung"""
    import shutil
    sessions = [
        "~/.config/openclaw/browser-data",
        "~/.local/share/openclaw/playwright",
    ]
    for s in sessions:
        path = os.path.expanduser(s)
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"🗑️ Cleared: {s}")

def check_url(url: str) -> tuple[bool, str]:
    """Prüfe URL auf Sicherheit"""
    
    # Prüfe blockierte Domains
    for pattern in BLOCKED_DOMAINS:
        if re.search(pattern, url, re.IGNORECASE):
            return False, f"Domain blocked: {pattern}"
    
    return True, "OK"

def check_action(action: str, selector: str = "", text: str = "") -> tuple[bool, str]:
    """Prüfe ob Aktion bestätigt werden muss"""
    
    full_text = f"{action} {selector} {text}".lower()
    
    for pattern in CONFIRM_ACTIONS:
        if re.search(pattern, full_text):
            return True, f"Confirmation required: {pattern}"
    
    return False, "No confirmation needed"

def should_allow(url: str, action: str = "browse", selector: str = "", text: str = "") -> tuple[bool, str]:
    """
    Hauptfunktion: Prüfe ob Browser-Aktion erlaubt ist
    Returns: (is_allowed, reason)
    """
    
    # 1. URL Prüfung
    url_safe, url_reason = check_url(url)
    if not url_safe:
        log_action(action, f"URL: {url} - {url_reason}", blocked=True)
        return False, url_reason
    
    # 2. Bestätigung nötig?
    needs_confirm, confirm_reason = check_action(action, selector, text)
    if needs_confirm:
        log_action(action, f"Needs confirmation: {confirm_reason}", blocked=False)
        return True, f"CONFIRM_REQUIRED: {confirm_reason}"
    
    log_action(action, f"URL: {url} - Allowed", blocked=False)
    return True, "ALLOWED"

if __name__ == "__main__":
    import sys
    
    # Test-Modus
    test_cases = [
        ("https://etsy.com", "browse", "", ""),
        ("https://evil.tk/phishing", "browse", "", ""),
        ("https://etsy.com", "click", "login-button", ""),
        ("https://etsy.com", "type", "password", "<REDACTED>"),
    ]
    
    print("🛡️ Browser Security Layer - Test\n")
    for url, action, selector, text in test_cases:
        allowed, reason = should_allow(url, action, selector, text)
        status = "✅" if allowed else "🚫"
        print(f"{status} {action} on {url}")
        print(f"   Reason: {reason}\n")
