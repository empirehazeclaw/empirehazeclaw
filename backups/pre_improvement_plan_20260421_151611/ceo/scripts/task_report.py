#!/usr/bin/env python3
"""
Unified Task Report Generator
==============================
Generiert vollständige Reports aus dem unified task logger.

Usage:
    python3 task_report.py
    python3 task_report.py --full
    python3 task_report.py --tsr
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"
LNEW_METRICS = f"{WORKSPACE}/memory/evaluations/lnew_metrics.json"


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}


def calculate_tsr(unified):
    """Calculate true task success rate."""
    all_tasks = unified.get('tasks', [])
    
    if not all_tasks:
        return {'total': 0, 'successes': 0, 'failures': 0, 'rate': 0.0}
    
    # Count by outcome
    outcomes = {'success': 0, 'failure': 0, 'partial': 0, 'skipped': 0}
    by_type = {}
    
    for task in all_tasks:
        outcome = task.get('outcome', 'unknown')
        t_type = task.get('type', 'unknown')
        sub_type = task.get('subtype', 'unknown')
        
        if outcome in outcomes:
            outcomes[outcome] += 1
        
        key = f"{t_type}.{sub_type}"
        if key not in by_type:
            by_type[key] = {'success': 0, 'failure': 0, 'total': 0}
        by_type[key]['total'] += 1
        if outcome == 'success':
            by_type[key]['success'] += 1
        elif outcome == 'failure':
            by_type[key]['failure'] += 1
    
    total = sum(outcomes.values())
    successes = outcomes['success']
    failures = outcomes['failure']
    rate = successes / total if total > 0 else 0.0
    
    return {
        'total': total,
        'successes': successes,
        'failures': failures,
        'partial': outcomes['partial'],
        'skipped': outcomes['skipped'],
        'rate': rate,
        'by_type': by_type
    }


def generate_full_report():
    """Generate comprehensive report."""
    unified = load_json(UNIFIED_TASKS, {'tasks': [], 'last_task_id': 0})
    
    # Calculate TSR
    tsr_data = calculate_tsr(unified)
    
    # Analyze by source
    orchestrator_tasks = [t for t in unified['tasks'] if t.get('type') == 'subagent_task']
    main_session_tasks = [t for t in unified['tasks'] if t.get('type') == 'main_session']
    
    # By day
    by_day = {}
    for task in unified['tasks']:
        day = task.get('timestamp', '')[:10]
        if day:
            by_day[day] = by_day.get(day, 0) + 1
    
    # Recent activity
    recent = unified['tasks'][-20:] if unified['tasks'] else []
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_tasks': tsr_data['total'],
        'task_success_rate': {
            'successes': tsr_data['successes'],
            'failures': tsr_data['failures'],
            'rate': tsr_data['rate'],
            'breakdown': {
                'main_session': len(main_session_tasks),
                'subagent': len(orchestrator_tasks),
                'other': tsr_data['total'] - len(main_session_tasks) - len(orchestrator_tasks)
            }
        },
        'by_day': dict(sorted(by_day.items())[-7:]),
        'recent_tasks': [
            {
                'id': t['task_id'],
                'timestamp': t.get('timestamp', '')[:19],
                'type': t.get('type'),
                'subtype': t.get('subtype'),
                'outcome': t.get('outcome'),
                'details': t.get('details', '')[:60]
            }
            for t in recent
        ],
        'coverage': {
            'main_session_tracked': len(main_session_tasks) > 0,
            'subagent_tracked': len(orchestrator_tasks) > 0,
            'all_sources_covered': len(unified['tasks']) > 0
        }
    }
    
    return report


def print_report(report):
    """Print formatted report."""
    print("\n📊 UNIFIED TASK REPORT")
    print("=" * 60)
    print(f"Generated: {report['generated_at']}")
    
    tsr = report['task_success_rate']
    print(f"\n🎯 TASK SUCCESS RATE (TSR)")
    print(f"   Total Tasks: {tsr['successes'] + tsr['failures']}")
    print(f"   Successes: {tsr['successes']}")
    print(f"   Failures: {tsr['failures']}")
    print(f"   TSR: {tsr['rate']*100:.1f}%")
    
    bd = tsr['breakdown']
    print(f"\n📋 BREAKDOWN:")
    print(f"   Main Session: {bd['main_session']}")
    print(f"   Subagent: {bd['subagent']}")
    print(f"   Other: {bd['other']}")
    
    cov = report['coverage']
    print(f"\n🎯 COVERAGE:")
    print(f"   Main Session tracked: {'✅' if cov['main_session_tracked'] else '❌'}")
    print(f"   Subagent tracked: {'✅' if cov['subagent_tracked'] else '❌'}")
    
    days = report['by_day']
    if days:
        print(f"\n📅 LAST 7 DAYS:")
        for day, count in sorted(days.items()):
            print(f"   {day}: {count} tasks")
    
    recent = report['recent_tasks']
    if recent:
        print(f"\n📝 RECENT TASKS:")
        for t in recent[-10:]:
            print(f"   #{t['id']} | {t['subtype']} | {t['outcome']} | {t['details'][:40]}")
    
    # Recommendations
    print(f"\n🔍 ANALYSIS:")
    if tsr['rate'] < 0.8:
        print(f"   ⚠️ TSR below 80% target")
    else:
        print(f"   ✅ TSR on track")
    
    if not cov['main_session_tracked']:
        print(f"   ⚠️ Main session not being tracked")
    
    if not cov['subagent_tracked']:
        print(f"   ⚠️ Subagent tasks not being tracked")


def update_lnew_metrics(report):
    """Update lnew_metrics.json with unified data."""
    lnew_path = LNEW_METRICS
    lnew = load_json(lnew_path, {})
    
    tsr = report['task_success_rate']
    lnew['task_success'] = {
        'successes': tsr['successes'],
        'failures': tsr['failures'],
        'rate': tsr['rate']
    }
    lnew['last_updated'] = datetime.now().isoformat()
    
    os.makedirs(os.path.dirname(lnew_path), exist_ok=True)
    with open(lnew_path, 'w') as f:
        json.dump(lnew, f, indent=2)
    
    print(f"✅ Updated lnew_metrics.json with TSR: {tsr['rate']*100:.1f}%")


if __name__ == '__main__':
    report = generate_full_report()
    
    if '--tsr' in sys.argv:
        tsr = report['task_success_rate']
        print(f"TSR: {tsr['rate']*100:.1f}% ({tsr['successes']}/{tsr['successes']+tsr['failures']})")
    elif '--full' in sys.argv:
        print_report(report)
    else:
        print_report(report)
        update_lnew_metrics(report)