#!/usr/bin/env python3
"""
Comprehensive Task Logger Cron
==============================
Wird periodisch ausgeführt um ALLE Task-Typen zu erfassen:
- Subagent Tasks (aus Orchestrator)
- Main Session Tasks (aus Session Analyzer)
- Cron Tasks (aus cron logs)

Usage:
    python3 task_logger_cron.py
"""

import json
import os
import sys
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'

# Import our modules
sys.path.insert(0, f"{WORKSPACE}/scripts")

from task_data_collector import sync_from_orchestrator, get_stats
from session_activity_analyzer import analyze_and_log


def main():
    print(f"📊 Task Logger Cron - {datetime.now().isoformat()}")
    print("=" * 50)
    
    # 1. Sync from orchestrator
    result = sync_from_orchestrator()
    print(f"✅ Orchestrator: {result['synced']} new tasks synced")
    
    # 2. Analyze and log session activities
    logged = analyze_and_log()
    print(f"✅ Session Activities: {logged} new tasks logged")
    
    # 3. Show current stats
    stats = get_stats()
    print(f"\n📈 CURRENT TOTALS:")
    print(f"   Total Tasks: {stats['total']}")
    print(f"   By Type:")
    for sub, count in sorted(stats['by_subtype'].items(), key=lambda x: -x[1])[:5]:
        print(f"      {sub}: {count}")
    
    # 4. Update lnew_metrics.json
    lnew_path = f"{WORKSPACE}/memory/evaluations/lnew_metrics.json"
    lnew = {}
    if os.path.exists(lnew_path):
        try:
            with open(lnew_path, 'r') as f:
                lnew = json.load(f)
        except:
            pass
    
    success = sum(1 for t in stats['by_outcome'].values()) - stats['by_outcome'].get('failure', 0) - stats['by_outcome'].get('skipped', 0)
    total = stats['total']
    
    lnew['task_success'] = {
        'successes': stats['by_outcome'].get('success', 0),
        'failures': stats['by_outcome'].get('failure', 0),
        'rate': stats['success_rate']
    }
    lnew['last_updated'] = datetime.now().isoformat()
    
    with open(lnew_path, 'w') as f:
        json.dump(lnew, f, indent=2)
    
    print(f"\n✅ Updated lnew_metrics.json")
    print(f"   TSR: {stats['success_rate']*100:.1f}%")


if __name__ == '__main__':
    main()