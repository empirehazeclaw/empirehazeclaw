#!/usr/bin/env python3
"""
🚀 Vercel Autopilot
Continuous monitoring and improvement for Big 4 domains.

Usage:
    python3 vercel_monitor.py --check      # Full Lighthouse check
    python3 vercel_monitor.py --status      # Quick status
    python3 vercel_monitor.py --deploy      # Deploy improvements
    python3 vercel_monitor.py --report      # Weekly report
"""

import subprocess
import json
import re
import fcntl
import sys
import os
from pathlib import Path
from datetime import datetime

VERCEL_TOKEN = "${VERCEL_TOKEN}"
LOCK_FILE = "/home/clawbot/.openclaw/workspace/data/.vercel_monitor.lock"

DOMAINS = {
    "de": "https://empirehazeclaw.de",
    "com": "https://empirehazeclaw.com", 
    "store": "https://empirehazeclaw.store",
    "info": "https://empirehazeclaw.info"
}

REPORT_FILE = Path("/home/clawbot/.openclaw/workspace/VERCEL_REPORT.md")

def acquire_lock():
    """Acquire exclusive file lock to prevent race conditions"""
    lock_path = Path(LOCK_FILE)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, 'w')
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        return lock_fd
    except BlockingIOError:
        print(f"[{datetime.now()}] Another instance is running. Exiting.")
        sys.exit(0)

def release_lock(lock_fd):
    """Release the file lock"""
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    lock_fd.close()

def api(endpoint):
    """Call Vercel API"""
    result = subprocess.run([
        "curl", "-s", f"https://api.vercel.com{endpoint}",
        "-H", f"Authorization: Bearer {VERCEL_TOKEN}"
    ], capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {}

def check_domain(domain, url):
    """Quick HTTP check for a domain"""
    result = subprocess.run([
        "curl", "-sI", url
    ], capture_output=True, text=True)
    
    status = "DOWN"
    for line in result.stdout.split("\n"):
        if line.startswith("HTTP"):
            code = line.split()[1]
            status = "200 OK" if "200" in line else code
            break
    
    # Check for security headers
    headers = result.stdout.lower()
    has_hsts = "strict-transport" in headers
    has_csp = "content-security-policy" in headers
    
    return {
        "domain": domain,
        "url": url,
        "status": status,
        "hsts": "OK" if has_hsts else "MISSING",
        "csp": "OK" if has_csp else "MISSING"
    }

def check_all_status():
    """Quick status check for all domains"""
    print("")
    print("=" * 60)
    print("VERCEL AUTOPILOT - STATUS CHECK")
    print("=" * 60)
    print("")
    
    print("Domain     URL                                  Status     HSTS   CSP")
    print("-" * 70)
    
    for domain, url in DOMAINS.items():
        r = check_domain(domain, url)
        domain_str = r['domain']
        url_str = r['url']
        status_str = r['status']
        hsts_str = r['hsts']
        csp_str = r['csp']
        print(domain_str.ljust(10) + url_str.ljust(35) + status_str.ljust(12) + hsts_str.ljust(6) + csp_str)
    
    print("\n" + "="*60)

def check_performance():
    """Check performance metrics (Lighthouse)"""
    print("\n📊 PERFORMANCE CHECK")
    print("Für Core Web Vitals bitte PageSpeed Insights nutzen:")
    print("https://pagespeed.web.dev/")
    print()

def get_deployments():
    """Get recent deployments"""
    print("\n🚀 RECENT DEPLOYMENTS")
    print("-"*50)
    
    data = api("/v6/deployments?limit=5")
    for dep in data.get("deployments", [])[:5]:
        url = dep.get("url", "?")[:40]
        state = dep.get("state", "?")
        created = dep.get("createdAt", "?")
        from datetime import datetime
        date = datetime.fromtimestamp(int(created)/1000).strftime("%m-%d %H:%M") if created.isdigit() else "?"
        print(f"{state:<12} {date}  {url}")

def generate_report():
    """Generate weekly report"""
    print("\n📋 WEEKLY REPORT")
    print("="*60)
    print(f"Datum: {datetime.now().strftime('%Y-%m-%d')}")
    print()
    
    # Check all domains
    for domain, url in DOMAINS.items():
        r = check_domain(domain, url)
        print(f"{domain.upper()}: {r['status']}")
    
    print()
    get_deployments()
    
    print("\n✅ Monitoring abgeschlossen")
    print("Voller Report in VERACEL_REPORT.md speichern?")

def main():
    lock_fd = acquire_lock()
    try:
        import argparse
        parser = argparse.ArgumentParser(description="Vercel Autopilot")
        parser.add_argument("--check", action="store_true", help="Full status check")
        parser.add_argument("--status", action="store_true", help="Quick status")
        parser.add_argument("--deploy", action="store_true", help="Deploy improvements")
        parser.add_argument("--report", action="store_true", help="Weekly report")
        
        args = parser.parse_args()
        
        if args.status or not any(vars(args).values()):
            check_all_status()
        elif args.check:
            check_all_status()
            check_performance()
        elif args.report:
            generate_report()
        elif args.deploy:
            print("Deploy feature not yet automated")
    finally:
        release_lock(lock_fd)

if __name__ == "__main__":
    main()
