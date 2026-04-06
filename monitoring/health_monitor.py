#!/usr/bin/env python3
"""
System Health Monitor
Sendet Alerts bei Problemen
"""

import os
import requests
import subprocess
from datetime import datetime

TELEGRAM_CHAT_ID = "5392634979"
TELEGRAM_TOKEN = "8397732232:AAEK9VmvNz1gtlBfeiogP8_bDIFWnfZq-HM"

def send_alert(message, urgent=False):
    """Send Telegram Alert"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    emoji = "🚨" if urgent else "⚠️"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{emoji} *System Alert*\n\n{message}",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def check_gateway():
    """Prüfe ob Gateway läuft"""
    try:
        result = subprocess.run(
            ["curl", "-s", "localhost:18789/status"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False

def check_disk():
    """Prüfe Disk Space"""
    result = subprocess.run(
        ["df", "-h", "/"],
        capture_output=True, text=True, timeout=5
    )
    line = result.stdout.split("\n")[1]
    used = int(line.split()[4].replace("%", ""))
    return used < 90  # OK wenn unter 90%

def check_cron():
    """Prüfe Cron Jobs"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "status"],
            capture_output=True, timeout=10
        )
        return "error" not in result.stdout.lower()
    except:
        return True  # Assume OK if can't check

def run_health_check():
    """Haupt-Check"""
    issues = []
    
    # Gateway
    if not check_gateway():
        issues.append("❌ Gateway nicht erreichbar!")
    
    # Disk
    if not check_disk():
        issues.append("⚠️ Disk über 90%!")
    
    # Cron (nur wichtige)
    # Hier könnten wir mehr Checks machen
    
    if issues:
        msg = "\n".join(issues)
        send_alert(msg, urgent=True)
        print(f"ALERT: {msg}")
    else:
        print(f"✅ Alles OK - {datetime.now().isoformat()}")

if __name__ == "__main__":
    run_health_check()
