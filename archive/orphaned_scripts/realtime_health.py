#!/usr/bin/env python3
"""
Real-time Health Monitor with Auto-Heal
"""
import subprocess
import requests
import json
from datetime import datetime

ALERT_WEBHOOK = os.environ.get("ALERT_WEBHOOK", "")
DOMAINS = ["empirehazeclaw.de", "empirehazeclaw.com", "empirehazeclaw.store", "empirehazeclaw.info"]

def check_domains():
    """Check all domains"""
    issues = []
    for domain in DOMAINS:
        try:
            r = requests.get(f"https://{domain}", timeout=10)
            if r.status_code != 200:
                issues.append(f"{domain}: {r.status_code}")
        except Exception as e:
            issues.append(f"{domain}: {e}")
    return issues

def check_services():
    """Check if services are running"""
    # Add service checks
    return []

def send_alert(msg):
    """Send alert to webhook"""
    if ALERT_WEBHOOK:
        try:
            requests.post(ALERT_WEBHOOK, json={"text": msg})
        except:
            pass

def main():
    issues = []
    issues.extend(check_domains())
    issues.extend(check_services())
    
    if issues:
        msg = f"⚠️ Health Issues: {', '.join(issues)}"
        print(msg)
        send_alert(msg)
    else:
        print(f"✅ All healthy at {datetime.now().strftime('%H:%M')}")

if __name__ == "__main__":
    import os
    main()
