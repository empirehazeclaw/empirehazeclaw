"""
📊 MONITORING SYSTEM
====================
Automatic health checks and monitoring
"""

import requests
import time
from logger import log, warn

# Services to monitor
SERVICES = {
    "website": "https://empirehazeclaw.de",
    "store": "https://empirehazeclaw.store",
    "blog": "https://empirehazeclaw.info",
    "chatbot": "http://188.124.11.27:8896",
    "trading": "http://188.124.11.27:8001",
}

def check_service(name, url):
    """Check if service is up"""
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return {"status": "UP", "code": 200}
        else:
            return {"status": "DOWN", "code": r.status_code}
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def health_check():
    """Run full health check"""
    log("INFO", "monitoring", "Running health check...")
    
    results = []
    
    for name, url in SERVICES.items():
        result = check_service(name, url)
        results.append((name, result))
        
        if result["status"] != "UP":
            warn("monitoring", f"{name} is {result['status']}")
    
    up = sum(1 for _, r in results if r["status"] == "UP")
    total = len(results)
    
    log("INFO", "monitoring", f"Health: {up}/{total} services UP")
    
    return results

if __name__ == "__main__":
    health_check()
