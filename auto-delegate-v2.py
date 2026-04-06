#!/usr/bin/env python3
"""
🤖 AUTO-DELEGATE - Autonomous Task Manager
==========================================
Runs hourly, finds tasks, assigns to agents.
"""

import os
import json
import subprocess
from datetime import datetime

AGENTS = {
    "research": "Recherche & Marktforschung",
    "content": "Content & Blog Posts", 
    "pod": "Print on Demand",
    "social": "Social Media",
    "outreach": "Kunden Outreach",
    "dev": "Development & Fixes"
}

TASKS = {
    "research": [
        "Recherchiere neue AI Tools",
        "Finde Competitor Updates",
        "Check Trend Keywords"
    ],
    "content": [
        "Schreibe Blog Post",
        "Update Produktbeschreibungen",
        "Erstelle Newsletter"
    ],
    "pod": [
        "Check Etsy Sales",
        "Design neue Produkte",
        "Optimiere Listings"
    ],
    "social": [
        "Twitter Post erstellen",
        "LinkedIn Update posten",
        "Analysiere Engagement"
    ],
    "outreach": [
        "Sende Outreach Emails",
        "Follow-up mit Leads",
        "Finde neue Prospects"
    ],
    "dev": [
        "Check System Health",
        "Fix Bug Reports",
        "Optimiere Performance"
    ]
}

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def check_services():
    """Check if SaaS services are running"""
    services_ok = []
    ports = [8895, 8896, 8898, 8001]
    for port in ports:
        try:
            result = subprocess.run(
                ["curl", "-sI", f"http://127.0.0.1:{port}"],
                capture_output=True, timeout=3
            )
            if "200" in str(result.returncode):
                services_ok.append(port)
        except:
            pass
    return services_ok

def check_websites():
    """Check if websites are up - local check"""
    sites = {
        "de": "/var/www/empirehazeclaw-de/index.html",
        "com": "/var/www/empirehazeclaw-com/index.html", 
        "store": "/var/www/empirehazeclaw-store/index.html",
        "info": "/var/www/empirehazeclaw-info/index.html"
    }
    for name, path in sites.items():
        if os.path.exists(path):
            log(f"   ✅ {name} OK")
        else:
            log(f"   ⚠️ {name} fehlt!")

def main():
    log("🤖 Auto-Delegate startet...")
    
    # 1. Health Check
    log("📊 Check Services...")
    services = check_services()
    log(f"   Services OK: {services}")
    
    # 2. Check Websites  
    log("🌐 Check Websites...")
    check_websites()
    
    # 3. Log current time for idle tracking
    hour = datetime.now().hour
    
    # 4. Determine priority tasks based on time
    if hour == 8:
        task = "Morning Research"
    elif hour == 10:
        task = "Content Creation"
    elif hour == 14:
        task = "Outreach"
    elif hour == 20:
        task = "Social Media"
    else:
        task = "General Tasks"
    
    log(f"   Priority Task: {task}")
    log("✅ Auto-Delegate fertig!")

if __name__ == "__main__":
    main()
