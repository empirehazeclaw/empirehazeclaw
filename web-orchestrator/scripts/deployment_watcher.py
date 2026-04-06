#!/usr/bin/env python3
"""
🚀 Web Orchestrator - Deployment Watcher
Überwacht Vercel Deployments und checkt auf Fehler
"""
import requests
import json
import time
from datetime import datetime, timedelta

VERCEL_TOKEN = "vcp_REDACTED"
HEADERS = {"Authorization": f"Bearer {VERCEL_TOKEN}"}

PROJECTS = [
    {"name": "de", "id": "prj_EwPW6e09BwlZSu4bWpOqSiN2NDrM"},
    {"name": "com", "id": "prj_bQ2cnIwN1G76yYrfv7slHGRHET4q"},
    {"name": "info", "id": "prj_4O3asMj2WsgAiNooTfFQjWAyia60"},
    {"name": "store", "id": "prj_XHTLM6fR6riltk7Ggk1xP7AXrlU5"},
]

DEPLOY_LOG = "/home/clawbot/.openclaw/workspace/web-orchestrator/deployments/deploy_log.json"
ERROR_LOG = "/home/clawbot/.openclaw/workspace/web-orchestrator/deployments/errors.json"

def get_recent_deployments(project_id, hours=24):
    """Hole Deployments der letzten X Stunden"""
    since = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
    
    url = f"https://api.vercel.com/v13/deployments?projectId={project_id}&since={since}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json().get('deployments', [])
        return []
    except Exception as e:
        print(f"API Error: {e}")
        return []

def check_deployment_status(deployment):
    """Analysiere Deployment Status"""
    d = deployment
    status = d.get('state', 'UNKNOWN')
    
    result = {
        "url": d.get('url'),
        "state": status,
        "created": datetime.fromtimestamp(d.get('createdAt', 0)/1000).isoformat(),
        "target": d.get('target'),
        "ready": d.get('ready'),
        "errors": []
    }
    
    # Check for errors
    if status == "ERROR":
        # Try to get error log
        deploy_id = d.get('id')
        if deploy_id:
            log_url = f"https://api.vercel.com/v13/deployments/{deploy_id}/events"
            try:
                r = requests.get(log_url, headers=HEADERS, timeout=10)
                if r.status_code == 200:
                    events = r.json()
                    for event in events:
                        if 'log' in event.get('type', '').lower() or event.get('type') == 'error':
                            result['errors'].append(event.get('payload', {}).get('text', str(event)))
            except:
                pass
    
    return result

def load_log():
    if __import__('os').path.exists(DEPLOY_LOG):
        with open(DEPLOY_LOG) as f:
            return json.load(f)
    return []

def save_log(log):
    with open(DEPLOY_LOG, 'w') as f:
        json.dump(log[-100:], f, indent=2)

def load_errors():
    if __import__('os').path.exists(ERROR_LOG):
        with open(ERROR_LOG) as f:
            return json.load(f)
    return []

def save_errors(errors):
    with open(ERROR_LOG, 'w') as f:
        json.dump(errors[-50:], f, indent=2)

def main():
    print("🚀 Web Orchestrator - Deployment Watcher")
    print("=" * 50)
    print(f"Checking deployments since last 24 hours...\n")
    
    all_deployments = []
    errors_found = []
    
    for project in PROJECTS:
        print(f"Checking {project['name']}...", end=" ")
        
        deploys = get_recent_deployments(project['id'])
        
        if not deploys:
            print("No deployments")
            continue
        
        print(f"{len(deploys)} deployment(s)")
        
        for d in deploys:
            status = check_deployment_status(d)
            all_deployments.append({
                "project": project['name'],
                **status
            })
            
            if status['state'] == 'ERROR':
                errors_found.append({
                    "project": project['name'],
                    **status
                })
    
    # Save deployment log
    log = load_log()
    log.append({
        "timestamp": datetime.now().isoformat(),
        "deployments": all_deployments,
        "error_count": len(errors_found)
    })
    save_log(log)
    
    # Save errors
    if errors_found:
        errors = load_errors()
        errors.extend(errors_found)
        save_errors(errors)
        
        print(f"\n⚠️ {len(errors_found)} ERROR(S) FOUND:")
        for e in errors_found:
            print(f"  ❌ {e['project']}: {e['url']}")
            for err in e['errors'][:3]:
                print(f"     {err[:100]}")
    else:
        print("\n✅ No errors in recent deployments")
    
    return 0 if not errors_found else 1

if __name__ == "__main__":
    exit(main())
