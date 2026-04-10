#!/usr/bin/env python3
"""
Sir HazeClaw Cron Monitor
Prüft Status der Cron Jobs.

Usage:
    python3 cron_monitor.py
"""

import os
import sys
import json
from datetime import datetime

def get_cron_status():
    """Liest Cron Jobs aus jobs.json."""
    cron_path = "/home/clawbot/.openclaw/cron/jobs.json"
    
    if not os.path.exists(cron_path):
        return [], "Cron file not found"
    
    try:
        with open(cron_path) as f:
            data = json.load(f)
        return data.get('jobs', []), None
    except Exception as e:
        return [], str(e)

def main():
    print(f"Sir HazeClaw Cron Monitor — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    jobs, error = get_cron_status()
    
    if error:
        print(f"❌ Error: {error}")
        return 1
    
    enabled = [j for j in jobs if j.get('enabled', True)]
    disabled = [j for j in jobs if not j.get('enabled', True)]
    
    print(f"Total Jobs: {len(jobs)}")
    print(f"  ✅ Enabled: {len(enabled)}")
    print(f"  ❌ Disabled: {len(disabled)}")
    print()
    
    if enabled:
        print("Active Crons:")
        for job in enabled:
            name = job.get('name', 'unnamed')
            schedule = job.get('schedule', {})
            cron_expr = schedule.get('expr', '?')
            next_run = schedule.get('next', '?')
            print(f"  - {name}: {cron_expr}")
        print()
    
    if disabled:
        print("Disabled Crons:")
        for job in disabled:
            name = job.get('name', 'unnamed')
            print(f"  - {name}")
    
    print("=" * 60)
    
    # Check for common issues
    issues = []
    
    # No enabled crons
    if len(enabled) == 0:
        issues.append("⚠️ No enabled cron jobs!")
    
    # No jobs at all
    if len(jobs) == 0:
        issues.append("⚠️ No cron jobs configured!")
    
    if issues:
        for issue in issues:
            print(issue)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())