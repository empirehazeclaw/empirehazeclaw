#!/usr/bin/env python3
"""
Task Data Collector - Fixed Version
====================================
Sammelt Task-Daten aus allen Quellen ohne Duplikate.

Usage:
    python3 task_data_collector.py --sync      # Sync from orchestrator
    python3 task_data_collector.py --report    # Full report
    python3 task_data_collector.py --stats     # Quick stats
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
ORCHESTRATOR_STATE = f"{EVAL_DIR}/orchestrator_state.json"
LNEW_METRICS = f"{EVAL_DIR}/lnew_metrics.json"
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"
MAIN_SESSION_LOG = f"{TASK_LOG_DIR}/main_session_tasks.json"

# Ensure directory exists
os.makedirs(TASK_LOG_DIR, exist_ok=True)


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_unified_tasks():
    """Get or initialize unified tasks."""
    return load_json(UNIFIED_TASKS, {'tasks': [], 'last_task_id': 0, 'synced_sources': []})


def save_unified_tasks(data):
    save_json(UNIFIED_TASKS, data)


def sync_from_orchestrator():
    """Sync tasks from orchestrator (idempotent)."""
    orchestrator = load_json(ORCHESTRATOR_STATE, {})
    completed = orchestrator.get('completed_tasks', [])
    failed = orchestrator.get('failed_tasks', [])
    
    unified = get_unified_tasks()
    
    # Track which orchestrator tasks we've already synced
    synced_ids = set()
    for task in unified['tasks']:
        meta = task.get('metadata', {})
        if 'orchestrator_task_id' in meta:
            synced_ids.add(meta['orchestrator_task_id'])
    
    new_tasks = []
    
    # Sync completed tasks
    for task in completed:
        task_id = task.get('task_id', '')
        if task_id in synced_ids:
            continue  # Already synced
        
        unified_task = {
            'task_id': unified['last_task_id'] + len(new_tasks) + 1,
            'timestamp': task.get('completed_at', datetime.now().isoformat()),
            'type': 'subagent_task',
            'subtype': task.get('type'),
            'outcome': 'success',
            'details': f"{task.get('type')} by {task.get('delegated_to')}",
            'metadata': {
                'source': 'orchestrator',
                'orchestrator_task_id': task_id,
                'delegated_to': task.get('delegated_to'),
                'created_at': task.get('created_at'),
                'duration_ms': calculate_duration(task)
            }
        }
        new_tasks.append(unified_task)
    
    # Sync failed tasks
    for task in failed:
        task_id = task.get('task_id', '')
        if task_id in synced_ids:
            continue
        
        unified_task = {
            'task_id': unified['last_task_id'] + len(new_tasks) + 1,
            'timestamp': task.get('failed_at', datetime.now().isoformat()),
            'type': 'subagent_task',
            'subtype': task.get('type'),
            'outcome': 'failure',
            'details': f"{task.get('type')} failed",
            'metadata': {
                'source': 'orchestrator',
                'orchestrator_task_id': task_id,
                'delegated_to': task.get('delegated_to'),
                'error': task.get('error', 'unknown')
            }
        }
        new_tasks.append(unified_task)
    
    # Add new tasks
    unified['tasks'].extend(new_tasks)
    unified['last_task_id'] = unified['last_task_id'] + len(new_tasks)
    
    if 'orchestrator' not in unified.get('synced_sources', []):
        unified['synced_sources'] = unified.get('synced_sources', []) + ['orchestrator']
    
    save_unified_tasks(unified)
    
    return {'synced': len(new_tasks), 'total_orchestrator': len(completed) + len(failed)}


def calculate_duration(task):
    created = task.get('created_at')
    completed = task.get('completed_at')
    if created and completed:
        try:
            t1 = datetime.fromisoformat(created.replace('Z', '+00:00'))
            t2 = datetime.fromisoformat(completed.replace('Z', '+00:00'))
            return int((t2 - t1).total_seconds() * 1000)
        except:
            pass
    return 0


def log_main_session_task(task_type, outcome, details='', metadata=None):
    """Log a main session task (Sir HazeClaw's own work)."""
    unified = get_unified_tasks()
    
    task = {
        'task_id': unified['last_task_id'] + 1,
        'timestamp': datetime.now().isoformat(),
        'type': 'main_session',
        'subtype': task_type,
        'outcome': outcome,
        'details': details,
        'metadata': metadata or {}
    }
    
    unified['tasks'].append(task)
    unified['last_task_id'] += 1
    
    save_unified_tasks(unified)
    return task['task_id']


def get_stats():
    """Get quick stats."""
    unified = get_unified_tasks()
    
    by_type = {}
    by_subtype = {}
    by_outcome = {'success': 0, 'failure': 0, 'partial': 0, 'skipped': 0}
    by_day = {}
    
    for task in unified['tasks']:
        t_type = task.get('type', 'unknown')
        t_subtype = task.get('subtype', 'unknown')
        t_outcome = task.get('outcome', 'unknown')
        t_day = task.get('timestamp', '')[:10]
        
        by_type[t_type] = by_type.get(t_type, 0) + 1
        by_subtype[t_subtype] = by_subtype.get(t_subtype, 0) + 1
        
        if t_outcome in by_outcome:
            by_outcome[t_outcome] += 1
        
        if t_day:
            by_day[t_day] = by_day.get(t_day, 0) + 1
    
    total = len(unified['tasks'])
    success_rate = by_outcome['success'] / max(total, 1)
    
    return {
        'total': total,
        'by_type': by_type,
        'by_subtype': by_subtype,
        'by_outcome': by_outcome,
        'by_day': by_day,
        'success_rate': success_rate
    }


def generate_full_report():
    """Generate comprehensive report."""
    unified = get_unified_tasks()
    stats = get_stats()
    
    orchestrator = load_json(ORCHESTRATOR_STATE, {})
    orch_total = len(orchestrator.get('completed_tasks', [])) + len(orchestrator.get('failed_tasks', []))
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_tasks': stats['total'],
        'overall_success_rate': stats['success_rate'],
        'coverage': {
            'orchestrator_tasks': orch_total,
            'unified_logger_tasks': stats['by_type'].get('subagent_task', 0),
            'main_session_tasks': stats['by_type'].get('main_session', 0)
        },
        'by_subtype': stats['by_subtype'],
        'recent_days': dict(sorted(stats['by_day'].items())[-7:]),
        'recommendations': []
    }
    
    # Recommendations
    if stats['success_rate'] < 0.8:
        report['recommendations'].append({
            'priority': 'HIGH',
            'issue': f'Success rate {stats["success_rate"]*100:.1f}% below 80% target'
        })
    
    if report['coverage']['orchestrator_tasks'] > report['coverage']['unified_logger_tasks']:
        missing = report['coverage']['orchestrator_tasks'] - report['coverage']['unified_logger_tasks']
        report['recommendations'].append({
            'priority': 'MED',
            'issue': f'{missing} orchestrator tasks not yet in unified logger'
        })
    
    return report


def print_report(report):
    print("\n📊 TASK DATA REPORT")
    print("=" * 50)
    print(f"Generated: {report['generated_at']}")
    print(f"\nTotal Tasks: {report['total_tasks']}")
    print(f"Success Rate: {report['overall_success_rate']*100:.1f}%")
    
    cov = report['coverage']
    print(f"\n📋 COVERAGE:")
    print(f"   Orchestrator: {cov['orchestrator_tasks']}")
    print(f"   Unified Logger (subagent): {cov['unified_logger_tasks']}")
    print(f"   Main Session: {cov['main_session_tasks']}")
    
    print(f"\n📈 BY SUBTYPE:")
    for sub, count in sorted(report['by_subtype'].items(), key=lambda x: -x[1]):
        print(f"   {sub}: {count}")
    
    if report['recommendations']:
        print(f"\n⚠️ RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"   [{rec['priority']}] {rec['issue']}")


if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else '--help'
    
    if action == '--sync':
        result = sync_from_orchestrator()
        print(f"✅ Synced {result['synced']} new tasks from orchestrator")
    
    elif action == '--stats':
        stats = get_stats()
        print(f"\n📊 STATS: {stats['total']} tasks, {stats['success_rate']*100:.1f}% success")
        print("\nBy subtype:")
        for sub, count in sorted(stats['by_subtype'].items(), key=lambda x: -x[1]):
            print(f"  {sub}: {count}")
    
    elif action == '--report':
        report = generate_full_report()
        print_report(report)
    
    elif action == '--log-main':
        # For main session task logging
        if len(sys.argv) < 4:
            print("Usage: task_data_collector.py --log-main <type> <outcome> [details]")
            sys.exit(1)
        task_type = sys.argv[2]
        outcome = sys.argv[3]
        details = sys.argv[4] if len(sys.argv) > 4 else ''
        task_id = log_main_session_task(task_type, outcome, details)
        print(f"✅ Logged main session task #{task_id}")
    
    else:
        print(__doc__)
        print("\nCommands:")
        print("  --sync     Sync from orchestrator")
        print("  --stats    Quick stats")
        print("  --report   Full report")
        print("  --log-main <type> <outcome> [details]  Log main session task")