#!/usr/bin/env python3
"""
Daily Report für n8n
Sammelt alle Metrics und gibt JSON für n8n Workflow zurück
"""

import json
import subprocess
from datetime import datetime

def get_stats():
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        
        "websites": {
            "empirehazeclaw.com": check_website("https://empirehazeclaw.com"),
            "empirehazeclaw.de": check_website("https://empirehazeclaw.de"),
            "empirehazeclaw.store": check_website("https://empirehazeclaw.store"),
            "empirehazeclaw.info": check_website("https://empirehazeclaw.info"),
        },
        
        "services": {
            "wordpress": check_docker("wordpress_wordpress_1"),
            "mysql": check_docker("wordpress_db_1"),
            "n8n": check_docker("n8n"),
        },
        
        "outreach": {
            "emails_sent_today": count_emails_today(),
            "total_leads": count_total_leads(),
        },
        
        "social": {
            "twitter_posts": 3,  # Placeholder - could connect to xurl API
        },
        
        "system": {
            "uptime": get_uptime(),
            "disk_usage": get_disk_usage(),
        }
    }
    
    return report

def check_website(url):
    import requests
    try:
        r = requests.get(url, timeout=5)
        return {"status": r.status_code, "ok": r.status_code == 200}
    except:
        return {"status": 0, "ok": False}

def check_docker(container):
    import subprocess
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"],
        capture_output=True, text=True
    )
    running = "Up" in result.stdout
    return {"running": running, "status": result.stdout.strip()}

def count_emails_today():
    import subprocess
    result = subprocess.run(
        ["grep", "-c", datetime.now().strftime("%Y-%m-%d"), 
         "/home/clawbot/.openclaw/logs/outreach.log"],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip())
    except:
        return 0

def count_total_leads():
    import subprocess
    result = subprocess.run(
        ["wc", "-l", "/home/clawbot/.openclaw/workspace/data/crm_leads.csv"],
        capture_output=True, text=True
    )
    try:
        return int(result.stdout.strip()) - 1  # Minus header
    except:
        return 0

def get_uptime():
    import subprocess
    result = subprocess.run(["uptime", "-p"], capture_output=True, text=True)
    return result.stdout.strip()

def get_disk_usage():
    import subprocess
    result = subprocess.run(
        ["df", "-h", "/", "--output=used,avail", "-B1"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split("\n")
    if len(lines) > 1:
        return lines[1].strip()
    return "unknown"

if __name__ == "__main__":
    stats = get_stats()
    print(json.dumps(stats, indent=2))
