#!/usr/bin/env python3
"""
Main Session Task Integrator
============================
Ermöglicht dem Hauptagent (Sir HazeClaw) eigene Tasks zu loggen.

Usage:
    python3 main_session_integrator.py --log <type> <outcome> [details]

Types für main session:
    message_response, decision, file_operation, 
    learning_integration, kg_update, external_action
"""

import json
import os
import sys
from datetime import datetime, timedelta

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"
MAIN_SESSION_LOG = f"{TASK_LOG_DIR}/main_session_tasks.json"

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
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def log_task(task_type, outcome, details='', metadata=None):
    """Log a main session task to unified logger."""
    unified = load_json(UNIFIED_TASKS, {'tasks': [], 'last_task_id': 0, 'synced_sources': []})
    
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
    
    save_json(UNIFIED_TASKS, unified)
    
    return task['task_id']


def get_main_session_stats():
    """Get stats for main session tasks only."""
    unified = load_json(UNIFIED_TASKS, {'tasks': []})
    
    main_tasks = [t for t in unified['tasks'] if t.get('type') == 'main_session']
    
    by_subtype = {}
    by_outcome = {'success': 0, 'failure': 0, 'partial': 0, 'skipped': 0}
    
    for task in main_tasks:
        sub = task.get('subtype', 'unknown')
        outcome = task.get('outcome', 'unknown')
        
        by_subtype[sub] = by_subtype.get(sub, 0) + 1
        if outcome in by_outcome:
            by_outcome[outcome] += 1
    
    total = len(main_tasks)
    
    return {
        'total': total,
        'by_subtype': by_subtype,
        'by_outcome': by_outcome,
        'success_rate': by_outcome['success'] / max(total, 1)
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 main_session_integrator.py --log <type> <outcome> [details]")
        print("  python3 main_session_integrator.py --stats")
        print("")
        print("Types: message_response, decision, file_operation,")
        print("       learning_integration, kg_update, external_action")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == '--log':
        task_type = sys.argv[2]
        outcome = sys.argv[3]
        details = sys.argv[4] if len(sys.argv) > 4 else ''
        
        task_id = log_task(task_type, outcome, details)
        print(f"Logged main session task #{task_id}: {task_type} = {outcome}")
        
        stats = get_main_session_stats()
        print(f"Main session total: {stats['total']} tasks, {stats['success_rate']*100:.1f}% success")
    
    elif action == '--stats':
        stats = get_main_session_stats()
        print(f"Main Session Stats: {stats['total']} tasks, {stats['success_rate']*100:.1f}% success")
        for sub, count in sorted(stats['by_subtype'].items(), key=lambda x: -x[1]):
            print(f"  {sub}: {count}")