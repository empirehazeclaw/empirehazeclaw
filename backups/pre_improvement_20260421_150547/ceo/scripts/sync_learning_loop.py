#!/usr/bin/env python3
"""
Learning Loop Synchronizer
==========================
Synchronisiert den Learning Loop mit dem Unified Task Logger.

Usage:
    python3 sync_learning_loop.py
"""

import json
import os
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
UNIFIED_TASKS = f"{WORKSPACE}/memory/task_log/unified_tasks.json"
LEARNING_LOOP_STATE = f"{EVAL_DIR}/learning_loop_state.json"


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


def calculate_tsr_from_unified():
    """Calculate TSR from unified task logger."""
    unified = load_json(UNIFIED_TASKS, {'tasks': []})
    tasks = unified.get('tasks', [])
    
    if not tasks:
        return {'rate': 0, 'successes': 0, 'failures': 0, 'total': 0}
    
    successes = sum(1 for t in tasks if t.get('outcome') == 'success')
    failures = sum(1 for t in tasks if t.get('outcome') == 'failure')
    total = len(tasks)
    
    return {
        'rate': successes / max(total, 1),
        'successes': successes,
        'failures': failures,
        'total': total
    }


def analyze_by_subtype():
    """Analyze task success by subtype."""
    unified = load_json(UNIFIED_TASKS, {'tasks': []})
    tasks = unified.get('tasks', [])
    
    by_subtype = {}
    for task in tasks:
        sub = task.get('subtype', 'unknown')
        if sub not in by_subtype:
            by_subtype[sub] = {'successes': 0, 'failures': 0, 'total': 0}
        
        by_subtype[sub]['total'] += 1
        outcome = task.get('outcome', 'unknown')
        if outcome == 'success':
            by_subtype[sub]['successes'] += 1
        elif outcome == 'failure':
            by_subtype[sub]['failures'] += 1
    
    # Calculate success rates
    for sub, stats in by_subtype.items():
        stats['success_rate'] = stats['successes'] / max(stats['total'], 1)
    
    return by_subtype


def sync_learning_loop():
    """Sync unified task data to learning loop state."""
    print("🔄 Syncing Learning Loop with Unified Task Logger")
    print("=" * 50)
    
    # Get TSR from unified
    tsr_data = calculate_tsr_from_unified()
    print(f"\n📊 TSR from Unified Logger:")
    print(f"   Rate: {tsr_data['rate']*100:.1f}%")
    print(f"   Successes: {tsr_data['successes']}")
    print(f"   Failures: {tsr_data['failures']}")
    print(f"   Total: {tsr_data['total']}")
    
    # Get subtype analysis
    by_subtype = analyze_by_subtype()
    print(f"\n📋 By Subtype:")
    for sub, stats in sorted(by_subtype.items(), key=lambda x: -x[1]['total']):
        sr = stats['success_rate'] * 100
        print(f"   {sub}: {stats['total']} tasks, {sr:.1f}% success")
    
    # Load current learning loop state
    ll_state = load_json(LEARNING_LOOP_STATE, {
        'tsr_history': [],
        'task_type_stats': {},
        'failure_patterns': [],
        'last_updated': None
    })
    
    # Create new TSR entry
    new_entry = {
        'timestamp': datetime.now().isoformat(),
        'tsr': tsr_data['rate'],
        'successes': tsr_data['successes'],
        'failures': tsr_data['failures'],
        'total': tsr_data['total'],
        'source': 'unified_task_logger'
    }
    
    # Update TSR history (keep last 20)
    tsr_history = ll_state.get('tsr_history', [])
    tsr_history.append(new_entry)
    tsr_history = tsr_history[-20:]  # Keep last 20
    
    # Update task type stats
    ll_state['task_type_stats'] = by_subtype
    
    # Update timestamps
    ll_state['last_updated'] = datetime.now().isoformat()
    ll_state['last_sync'] = datetime.now().isoformat()
    
    # Calculate trend
    if len(tsr_history) >= 2:
        old_tsr = tsr_history[0].get('tsr', 0)
        new_tsr = tsr_history[-1].get('tsr', 0)
        if new_tsr > old_tsr:
            ll_state['tsr_trend'] = 'improving'
        elif new_tsr < old_tsr:
            ll_state['tsr_trend'] = 'declining'
        else:
            ll_state['tsr_trend'] = 'stable'
    
    # Clear recommendations since we're updating with fresh data
    ll_state['recommendations_generated'] = 0
    
    # Save updated state
    save_json(LEARNING_LOOP_STATE, ll_state)
    
    print(f"\n✅ Learning Loop State updated:")
    print(f"   Last updated: {ll_state['last_updated'][:19]}")
    print(f"   TSR trend: {ll_state.get('tsr_trend', 'unknown')}")
    print(f"   History entries: {len(tsr_history)}")
    
    return ll_state


def main():
    result = sync_learning_loop()
    
    print("\n" + "=" * 50)
    print("📊 SYNC COMPLETE")
    print(f"   Current TSR: {result.get('tsr_history', [{}])[-1].get('tsr', 0)*100:.1f}%")
    print(f"   Trend: {result.get('tsr_trend', 'unknown')}")


if __name__ == '__main__':
    main()