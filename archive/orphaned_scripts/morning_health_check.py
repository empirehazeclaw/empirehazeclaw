#!/usr/bin/env python3
"""
🌅 Morning Health Check
Quick health verification of all services
"""
import subprocess
import json
from datetime import datetime
from pathlib import Path

LOG = Path("/home/clawbot/.openclaw/workspace/logs/health.log")

def check_service(name, url):
    try:
        result = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url], 
                                capture_output=True, text=True, timeout=10)
        status = "✅" if result.stdout.strip() == "200" else "⚠️"
        return f"{status} {name}: {result.stdout.strip()}"
    except Exception as e:
        return f"❌ {name}: {e}"

def main():
    services = [
        ("Store", "https://empirehazeclaw.store"),
        ("DE", "https://empirehazeclaw.de"),
        ("COM", "https://empirehazeclaw.com"),
        ("Blog", "https://empirehazeclaw.info"),
    ]
    
    results = [f"🌅 Health Check {datetime.now().isoformat()}"]
    for name, url in services:
        results.append(check_service(name, url))
    
    print("\n".join(results))
    
    with open(LOG, "a") as f:
        f.write("\n".join(results) + "\n")

if __name__ == "__main__":
    main()
