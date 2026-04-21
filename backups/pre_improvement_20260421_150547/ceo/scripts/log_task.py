#!/usr/bin/env python3
"""
Task Logging Integration
========================
Erlaubt Sir HazeClaw (main session) Tasks zu loggen.

Usage:
    python3 log_task.py <type> <outcome> [details]
    
Types:
    message_response, decision, file_operation, 
    external_action, learning_integration, health_check

Outcomes:
    success, failure, partial, skipped

Examples:
    python3 log_task.py message_response success "Reply to Nico about KG"
    python3 log_task.py decision success "Approved script changes"
    python3 log_task.py external_action skipped "Email - not authorized"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
LOG_DIR = f"{WORKSPACE}/memory/task_log"
LOG_FILE = f"{LOG_DIR}/unified_tasks.json"
STATS_FILE = f"{LOG_DIR}/task_stats.json"

TASK_TYPES = [
    'message_response',
    'decision',
    'subagent_task', 
    'cron_task',
    'script_execution',
    'learning_integration',
    'health_check',
    'research',
    'file_operation',
    'external_action'
]

OUTCOMES = ['success', 'failure', 'partial', 'skipped']


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_tasks():
    data = load_json(LOG_FILE)
    if data:
        return data
    return {'tasks': [], 'last_task_id': 0}


def save_tasks(tasks):
    save_json(LOG_FILE, tasks)


def load_stats():
    data = load_json(STATS_FILE)
    if data:
        return data
    return init_stats()


def init_stats():
    return {
        'by_type': {t: {'success': 0, 'failure': 0, 'partial': 0, 'skipped': 0, 'total': 0} for t in TASK_TYPES},
        'by_day': {},
        'total_tasks': 0,
        'total_successes': 0,
        'total_failures': 0
    }


def save_stats(stats):
    save_json(STATS_FILE, stats)


def log_task(task_type, outcome, details=''):
    """Log a single task."""
    tasks = load_tasks()
    stats = load_stats()
    
    task_id = tasks['last_task_id'] + 1
    task = {
        'task_id': task_id,
        'timestamp': datetime.now().isoformat(),
        'type': task_type,
        'outcome': outcome,
        'details': details,
        'metadata': {}
    }
    
    tasks['tasks'].append(task)
    tasks['last_task_id'] = task_id
    
    # Update stats
    if task_type in stats['by_type'] and outcome in stats['by_type'][task_type]:
        stats['by_type'][task_type][outcome] += 1
        stats['by_type'][task_type]['total'] += 1
    
    day = task['timestamp'][:10]
    if day not in stats['by_day']:
        stats['by_day'][day] = {'success': 0, 'failure': 0, 'total': 0}
    if outcome in stats['by_day'][day]:
        stats['by_day'][day][outcome] += 1
        stats['by_day'][day]['total'] += 1
    
    stats['total_tasks'] += 1
    if outcome == 'success':
        stats['total_successes'] += 1
    elif outcome == 'failure':
        stats['total_failures'] += 1
    
    save_tasks(tasks)
    save_stats(stats)
    
    return task_id


def show_stats():
    stats = load_stats()
    print("\n📊 TASK STATS")
    print("=" * 50)
    print(f"Total Tasks: {stats['total_tasks']}")
    print(f"Success Rate: {stats['total_successes']/max(stats['total_tasks'],1)*100:.1f}%")
    print("\nBy Type:")
    for t in TASK_TYPES:
        t_stats = stats['by_type'][t]
        if t_stats['total'] > 0:
            rate = t_stats['success'] / t_stats['total'] * 100
            print(f"  {t}: {t_stats['total']} ({rate:.1f}% success)")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    task_type = sys.argv[1]
    outcome = sys.argv[2]
    details = sys.argv[3] if len(sys.argv) > 3 else ''
    
    if task_type not in TASK_TYPES:
        print(f"Unknown type: {task_type}")
        print(f"Valid: {TASK_TYPES}")
        sys.exit(1)
    
    if outcome not in OUTCOMES:
        print(f"Unknown outcome: {outcome}")
        print(f"Valid: {OUTCOMES}")
        sys.exit(1)
    
    task_id = log_task(task_type, outcome, details)
    print(f"✅ Logged task #{task_id}: {task_type} = {outcome}")
    show_stats()