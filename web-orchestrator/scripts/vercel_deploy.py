#!/usr/bin/env python3
"""
🚀 Web Orchestrator - Vercel Auto-Deploy
Deployt Änderungen auf Vercel
"""
import subprocess
import requests
import json
import os
from datetime import datetime

VERCEL_TOKEN = "vcp_REDACTED"
WORK_DIR = "/home/clawbot/.openclaw/workspace/website-rebuild/new"

SITES = {
    "de": f"{WORK_DIR}/de",
    "com": f"{WORK_DIR}/com", 
    "info": f"{WORK_DIR}/info",
    "store": f"{WORK_DIR}/store"
}

def deploy_site(site, branch="main"):
    """Deploy eine Site zu Vercel"""
    site_dir = SITES.get(site)
    
    if not site_dir or not os.path.exists(site_dir):
        return {"site": site, "status": "SKIP", "reason": f"Directory not found: {site_dir}"}
    
    print(f"Deploying {site} from {site_dir}...")
    
    try:
        # Use vercel CLI
        result = subprocess.run(
            ["vercel", "--prod", "--yes", "--token", VERCEL_TOKEN],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Parse output for URL
            lines = result.stdout.strip().split('\n')
            deploy_url = lines[-1] if lines else "unknown"
            return {"site": site, "status": "SUCCESS", "url": deploy_url, "output": result.stdout}
        else:
            return {"site": site, "status": "ERROR", "error": result.stderr}
    
    except subprocess.TimeoutExpired:
        return {"site": site, "status": "TIMEOUT"}
    except Exception as e:
        return {"site": site, "status": "ERROR", "error": str(e)}

def deploy_all():
    """Deploy alle Sites"""
    print("🚀 Web Orchestrator - Deploying all sites")
    print("=" * 50)
    
    results = []
    
    for site, dir_path in SITES.items():
        result = deploy_site(site)
        results.append(result)
        
        if result['status'] == 'SUCCESS':
            print(f"✅ {site}: {result.get('url', 'OK')}")
        else:
            print(f"❌ {site}: {result.get('error', result.get('status'))}")
    
    return results

def deploy_preview(site, branch="preview"):
    """Deploy Preview Branch für Test"""
    site_dir = SITES.get(site)
    
    if not site_dir:
        return {"site": site, "status": "ERROR", "reason": "Unknown site"}
    
    try:
        result = subprocess.run(
            ["vercel", "--yes", "--token", VERCEL_TOKEN, "--target", "preview"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return {"site": site, "status": "SUCCESS", "output": result.stdout}
        else:
            return {"site": site, "status": "ERROR", "error": result.stderr}
    except Exception as e:
        return {"site": site, "status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        # Deploy all
        results = deploy_all()
    else:
        site = sys.argv[1]
        if "--preview" in sys.argv:
            result = deploy_preview(site)
        else:
            result = deploy_site(site)
        
        if result['status'] == 'SUCCESS':
            print(f"✅ {result['site']} deployed!")
            if 'url' in result:
                print(f"   URL: {result['url']}")
        else:
            print(f"❌ {result['site']}: {result.get('error', result.get('status'))}")
