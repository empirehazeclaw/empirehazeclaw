#!/usr/bin/env python3
"""
Sync Orchestrator to Unified Logger
====================================
Überträgt alle Orchestrator-Tasks in den unified task logger.

Usage:
    python3 sync_orchestrator_to_unified.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
EVAL_DIR = f"{WORKSPACE}/memory/evaluations"
ORCHESTRATOR_STATE = f"{EVAL_DIR}/orchestrator_state.json"
TASK_LOGGER_SCRIPT = f"{WORKSPACE}/scripts/unified_task_logger.py"

# Add scripts to path
sys.path.insert(0, f"{WORKSPACE}/scripts")


def load_json(path, default=None):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return default or {}


def main():
    print("🔄 Syncing Orchestrator → Unified Task Logger")
    print("=" * 50)
    
    # Load orchestrator state
    orchestrator = load_json(ORCHESTRATOR_STATE, {'completed_tasks': [], 'failed_tasks': []})
    
    completed = orchestrator.get('completed_tasks', [])
    failed = orchestrator.get('failed_tasks', [])
    
    print(f"📥 Found {len(completed)} completed, {len(failed)} failed tasks")
    
    # Import unified logger
    try:
        from unified_task_logger import UnifiedTaskLogger
        logger = UnifiedTaskLogger()
        existing_count = logger.tasks['last_task_id']
        print(f"📋 Existing tasks in logger: {existing_count}")
    except Exception as e:
        print(f"❌ Could not load unified_task_logger: {e}")
        return
    
    # Sync completed tasks
    synced = 0
    for task in completed:
        task_type = task.get('type', 'subagent_task')
        created = task.get('created_at', '')
        completed_at = task.get('completed_at', '')
        
        # Calculate duration if we have times
        duration_ms = 0
        if created and completed_at:
            try:
                t1 = datetime.fromisoformat(created.replace('Z', '+00:00'))
                t2 = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                duration_ms = int((t2 - t1).total_seconds() * 1000)
            except:
                pass
        
        metadata = {
            'task_id': task.get('task_id'),
            'delegated_to': task.get('delegated_to'),
            'duration_ms': duration_ms,
            'priority': task.get('priority')
        }
        
        result = task.get('result', {})
        success = result.get('success', True)
        outcome = 'success' if success else 'failure'
        
        logger.log_task(
            task_type='subagent_task',
            outcome=outcome,
            details=f"{task_type} by {task.get('delegated_to')}",
            metadata=metadata
        )
        synced += 1
    
    # Sync failed tasks
    for task in failed:
        task_type = task.get('type', 'subagent_task')
        
        metadata = {
            'task_id': task.get('task_id'),
            'delegated_to': task.get('delegated_to'),
            'error': task.get('error', 'unknown')
        }
        
        logger.log_task(
            task_type='subagent_task',
            outcome='failure',
            details=f"{task_type} failed",
            metadata=metadata
        )
        synced += 1
    
    print(f"\n✅ Synced {synced} tasks to unified logger")
    
    # Show updated stats
    stats = logger.get_stats()
    print(f"\n📊 Updated Stats:")
    print(f"   Total Tasks: {stats['total_tasks']}")
    print(f"   Success Rate: {stats['total_successes']/max(stats['total_tasks'],1)*100:.1f}%")


if __name__ == '__main__':
    main()