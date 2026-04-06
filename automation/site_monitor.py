#!/usr/bin/env python3
"""
🌐 Site Monitor - Optimized
"""
import requests, subprocess
from datetime import datetime

DOMAINS = [
    ("empirehazeclaw.com", "https://empirehazeclaw.com"),
    ("empirehazeclaw.de", "https://empirehazeclaw.de"),
    ("empirehazeclaw.store", "https://empirehazeclaw.store"),
    ("empirehazeclaw.info", "https://empirehazeclaw.info"),
]

def check(name, url):
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print(f"🔍 Monitor - {datetime.now().strftime('%H:%M:%S')}")
    all_ok = True
    for name, url in DOMAINS:
        ok = check(name, url)
        print(f"  {'✅' if ok else '❌'} {name}")
        if not ok: all_ok = False
    exit(0 if all_ok else 1)
