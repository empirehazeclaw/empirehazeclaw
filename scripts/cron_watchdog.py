#!/usr/bin/env python3
"""
Sir HazeClaw Cron Watchdog
Überwacht Cron Jobs und meldet wenn welche fehlschlagen.

Usage:
    python3 cron_watchdog.py
"""

import os
import sys
import json
from datetime import datetime, timedelta

CRON_JOBS_PATH = "/home/clawbot/.openclaw/cron/jobs.json"
ALERT_LOG = "/home/clawbot/.openclaw/workspace/logs/cron_watchdog.log"

def load_jobs():
    with open(CRON_JOBS_PATH) as f:
        data = json.load(f)
    return data.get('jobs', [])

def check_jobs(jobs):
    """Prüft Jobs auf Probleme."""
    issues = []
    
    for job in jobs:
        if not job.get('enabled', True):
            continue
        
        name = job.get('name', 'unnamed')
        state = job.get('state', {})
        
        # Check consecutive errors
        consecutive_errors = state.get('consecutiveErrors', 0)
        if consecutive_errors >= 2:
            issues.append(f"⚠️  {name}: {consecutive_errors} consecutive errors")
        
        # Check last run status
        last_status = state.get('lastRunStatus', 'unknown')
        if last_status == 'error':
            issues.append(f"❌ {name}: last run failed")
        
        # Check if next run is overdue (more than 25 hours for daily jobs)
        next_run = state.get('nextRunAtMs')
        if next_run:
            next_run_dt = datetime.fromtimestamp(next_run / 1000)
            now = datetime.now()
            if next_run_dt < now - timedelta(hours=25):
                issues.append(f"⏰ {name}: next run overdue")
    
    return issues

def main():
    print(f"Cron Watchdog — {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    jobs = load_jobs()
    enabled = [j for j in jobs if j.get('enabled', True)]
    
    print(f"Monitoring {len(enabled)} enabled cron jobs...")
    print()
    
    issues = check_jobs(jobs)
    
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  {issue}")
        
        # Log issues
        os.makedirs(os.path.dirname(ALERT_LOG), exist_ok=True)
        with open(ALERT_LOG, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            f.write(f"[{timestamp}]\n")
            for issue in issues:
                f.write(f"  {issue}\n")
            f.write("\n")
        
        print()
        return 1
    else:
        print("✅ All cron jobs healthy")
        return 0

if __name__ == "__main__":
    sys.exit(main())