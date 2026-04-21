#!/usr/bin/env python3
"""
Orphan Task Cleaner
===================
Identifiziert und markiert orphan/lost tasks.

Usage:
    python3 orphan_task_cleaner.py --check
    python3 orphan_task_cleaner.py --cleanup
"""

import json
import os
from datetime import datetime

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
ORCHESTRATOR_STATE = f"{EVAL_DIR}/orchestrator_state.json"
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"


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


def check_orphans():
    """Check for orphan tasks."""
    orchestrator = load_json(ORCHESTRATOR_STATE, {})
    
    delegated = orchestrator.get('delegated_tasks', [])
    completed = orchestrator.get('completed_tasks', [])
    failed = orchestrator.get('failed_tasks', [])
    
    # Find task IDs that are in delegated but not in completed/failed
    delegated_ids = set(t.get('task_id') for t in delegated)
    completed_ids = set(t.get('task_id') for t in completed)
    failed_ids = set(t.get('task_id') for t in failed)
    
    orphan_ids = delegated_ids - completed_ids - failed_ids
    
    return {
        'total_delegated': len(delegated_ids),
        'total_completed': len(completed_ids),
        'total_failed': len(failed_ids),
        'orphan_count': len(orphan_ids),
        'orphan_ids': list(orphan_ids)[:20]  # First 20
    }


def analyze_orphans():
    """Analyze why tasks became orphans."""
    orchestrator = load_json(ORCHESTRATOR_STATE, {})
    
    delegated = orchestrator.get('delegated_tasks', [])
    completed = orchestrator.get('completed_tasks', [])
    
    completed_ids = set(t.get('task_id') for t in completed)
    
    # Find orphaned tasks
    orphans = [t for t in delegated if t.get('task_id') not in completed_ids]
    
    if not orphans:
        return {'orphans': [], 'analysis': 'No orphans found'}
    
    # Analyze orphan characteristics
    by_status = {}
    for task in orphans:
        status = task.get('status', 'unknown')
        by_status[status] = by_status.get(status, 0) + 1
    
    by_age = {}
    now = datetime.now()
    for task in orphans:
        created = task.get('created_at', '')
        if created:
            try:
                age = (now - datetime.fromisoformat(created.replace('Z', '+00:00'))).total_seconds()
                bucket = int(age / 3600)  # Hours
                by_age[bucket] = by_age.get(bucket, 0) + 1
            except:
                pass
    
    return {
        'orphans': len(orphans),
        'by_status': by_status,
        'by_age_hours': by_age,
        'oldest_task': min([t.get('created_at', '') for t in orphans]) if orphans else None
    }


def cleanup_orphans():
    """Clean up orphan tasks."""
    orchestrator = load_json(ORCHESTRATOR_STATE, {})
    
    delegated = orchestrator.get('delegated_tasks', [])
    completed = orchestrator.get('completed_tasks', [])
    
    completed_ids = set(t.get('task_id') for t in completed)
    
    # Find orphaned tasks
    orphans = [t for t in delegated if t.get('task_id') not in completed_ids]
    
    if not orphans:
        print("No orphans to clean")
        return {'cleaned': 0}
    
    # Archive orphans separately
    orphan_archive = load_json(f"{WORKSPACE}/memory/task_log/orphan_tasks_archive.json", [])
    
    for task in orphans:
        task['archived_at'] = datetime.now().isoformat()
        task['reason'] = 'orphaned'
        orphan_archive.append(task)
    
    # Save archive
    save_json(f"{WORKSPACE}/memory/task_log/orphan_tasks_archive.json", orphan_archive)
    
    # Keep in orchestrator state but mark as archived
    # We don't remove them to preserve history
    
    return {'cleaned': len(orphans), 'archived': len(orphan_archive)}


def main():
    import sys
    
    action = sys.argv[1] if len(sys.argv) > 1 else '--check'
    
    if action == '--check':
        print("🔍 Checking for orphan tasks...")
        result = check_orphans()
        print(f"\n📊 Orphan Status:")
        print(f"   Delegated: {result['total_delegated']}")
        print(f"   Completed: {result['total_completed']}")
        print(f"   Failed: {result['total_failed']}")
        print(f"   ⚠️ Orphans: {result['orphan_count']}")
        
        if result['orphan_ids']:
            print(f"\n   First orphan IDs: {result['orphan_ids'][:5]}")
        
        # Detailed analysis
        print("\n📋 Detailed Analysis:")
        analysis = analyze_orphans()
        if 'error' not in analysis:
            print(f"   Total orphans: {analysis.get('orphans', 0)}")
            if analysis.get('by_status'):
                print(f"   By status: {analysis.get('by_status')}")
            if analysis.get('by_age_hours'):
                print(f"   By age (hours): {analysis.get('by_age_hours')}")
        
    elif action == '--cleanup':
        print("🧹 Cleaning up orphan tasks...")
        result = cleanup_orphans()
        print(f"\n✅ Cleaned {result['cleaned']} orphans")
        print(f"   Archived total: {result.get('archived', 0)}")
    
    elif action == '--archive-only':
        print("📦 Archiving only (no removal)...")
        result = cleanup_orphans()
        print(f"✅ Archived {result['cleaned']} orphan tasks")
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()