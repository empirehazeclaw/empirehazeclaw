#!/usr/bin/env python3
"""
🌐 Web Orchestrator - Daily Health Check
Prüft alle 4 Domains auf Erreichbarkeit und Performance
"""
import requests
import json
import time
from datetime import datetime

VERCEL_TOKEN = "vcp_REDACTED"
DOMAINS = [
    {"name": "de", "url": "https://empirehazeclaw.de", "lang": "DE"},
    {"name": "com", "url": "https://empirehazeclaw.com", "lang": "EN"},
    {"name": "info", "url": "https://empirehazeclaw.info", "lang": "DE/EN"},
    {"name": "store", "url": "https://empirehazeclaw.store", "lang": "DE/EN"},
]

LOG_FILE = "/home/clawbot/.openclaw/workspace/web-orchestrator/monitoring/health_log.json"
ALERT_LOG = "/home/clawbot/.openclaw/workspace/web-orchestrator/monitoring/alerts.json"

def check_domain(domain):
    """Prüfe einzelne Domain"""
    url = domain["url"]
    start = time.time()
    
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "WebOrchestrator/1.0"})
        latency = (time.time() - start) * 1000
        size = len(r.content)
        
        return {
            "domain": domain["name"],
            "url": url,
            "status": r.status_code,
            "latency_ms": round(latency, 1),
            "size_bytes": size,
            "ok": r.status_code == 200,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "domain": domain["name"],
            "url": url,
            "status": 0,
            "error": str(e),
            "ok": False,
            "timestamp": datetime.now().isoformat()
        }

def load_log():
    if __import__('os').path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log[-100:], f, indent=2)  # Keep last 100 entries

def check_via_vercel_api():
    """Prüfe Deployment Status via Vercel API"""
    headers = {"Authorization": f"Bearer {VERCEL_TOKEN}"}
    results = {}
    
    try:
        r = requests.get("https://api.vercel.com/v6/projects", headers=headers, timeout=10)
        if r.status_code == 200:
            projects = r.json().get('projects', [])
            our_projects = [p for p in projects if any(d in p.get('name','') for d in ['de','com','info','store'])]
            results['projects'] = len(our_projects)
            results['ok'] = True
        else:
            results['ok'] = False
            results['error'] = f"API returned {r.status_code}"
    except Exception as e:
        results['ok'] = False
        results['error'] = str(e)
    
    return results

def main():
    print("🌐 Web Orchestrator - Daily Health Check")
    print("=" * 50)
    
    all_ok = True
    results = []
    
    # Check all domains
    for domain in DOMAINS:
        print(f"Checking {domain['name']}.empirehazeclaw.{domain['name']}...", end=" ")
        result = check_domain(domain)
        results.append(result)
        
        if result['ok']:
            print(f"✅ {result['latency_ms']}ms ({result['size_bytes']} bytes)")
        else:
            status = result.get('status', '?')
            print(f"❌ HTTP {status}")
            all_ok = False
    
    # Check Vercel API
    print("\nChecking Vercel API...", end=" ")
    api_result = check_via_vercel_api()
    if api_result['ok']:
        print(f"✅ {api_result['projects']} projects")
    else:
        print(f"❌ {api_result.get('error', 'API Error')}")
        all_ok = False
    
    # Save log
    log = load_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "domains": results,
        "api": api_result,
        "all_ok": all_ok
    })
    save_log(log)
    
    # Alert if issues
    if not all_ok:
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": "HEALTH_CHECK_FAILED",
            "results": results,
            "api": api_result
        }
        alerts = []
        if __import__('os').path.exists(ALERT_LOG):
            with open(ALERT_LOG) as f:
                alerts = json.load(f)
        alerts.append(alert)
        with open(ALERT_LOG, 'w') as f:
            json.dump(alerts[-50:], f, indent=2)  # Keep last 50
        
        print(f"\n⚠️ ISSUES DETECTED - Alert logged!")
    
    print(f"\n{'✅ ALL OK' if all_ok else '❌ ISSUES FOUND'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    exit(main())
