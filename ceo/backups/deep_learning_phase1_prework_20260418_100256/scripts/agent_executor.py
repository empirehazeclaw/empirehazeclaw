#!/usr/bin/env python3
"""
Agent Executor — Sir HazeClaw Multi-Agent Architecture
====================================================
Executes tasks from the orchestrator queue.

This is the MISSING PIECE that makes multi-agent delegation actually work.
The orchestrator queues tasks, this executor runs them.

Usage:
    python3 agent_executor.py --poll         # Poll once and execute pending tasks
    python3 agent_executor.py --daemon     # Run continuously as daemon
    python3 agent_executor.py --test       # Test mode
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path('/home/clawbot/.openclaw/workspace/ceo')
AGENT_BASE = Path('/home/clawbot/.openclaw/workspace/SCRIPTS/automation')
ORCHESTRATOR_STATE = WORKSPACE / 'memory/evaluations/orchestrator_state.json'
EXECUTOR_LOG = WORKSPACE / 'logs/agent_executor.log'

AGENT_SCRIPTS = {
    'health_agent': str(AGENT_BASE / 'health_agent.py'),
    'research_agent': str(AGENT_BASE / 'research_agent.py'),
    'data_agent': str(AGENT_BASE / 'data_agent.py'),
}

TASK_TYPE_MAP = {
    'health_check': ['health_agent'],
    'research': ['research_agent'],
    'learning_sync': ['data_agent'],
    'data_analysis': ['data_agent'],
}

TIMEOUT_SECONDS = 60


def log(msg):
    """Log to file + print."""
    ts = datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    EXECUTOR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(EXECUTOR_LOG, 'a') as f:
        f.write(line + '\n')


def load_state():
    """Load orchestrator state."""
    if ORCHESTRATOR_STATE.exists():
        with open(ORCHESTRATOR_STATE, 'r') as f:
            return json.load(f)
    return {
        'delegated_tasks': [],
        'completed_tasks': [],
        'failed_tasks': [],
        'agent_last_seen': {},
        'delegation_count': 0
    }


def save_state(state):
    """Save orchestrator state."""
    with open(ORCHESTRATOR_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def execute_agent_task(agent_name, task_data):
    """Execute a single agent task."""
    if agent_name not in AGENT_SCRIPTS:
        return {'success': False, 'error': f'Unknown agent: {agent_name}'}
    
    script = AGENT_SCRIPTS[agent_name]
    if not os.path.exists(script):
        return {'success': False, 'error': f'Script not found: {script}'}
    
    task_type = task_data.get('type', 'unknown')
    
    try:
        if task_type == 'health_check':
            cmd = [sys.executable, script, '--check']
        elif task_type == 'research':
            topic = task_data.get('data', {}).get('topic', '')
            cmd = [sys.executable, script, '--topic', topic]
        elif task_type == 'learning_sync':
            cmd = [sys.executable, script, '--collect']
        elif task_type == 'data_analysis':
            cmd = [sys.executable, script, '--analyze']
        else:
            cmd = [sys.executable, script]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=str(WORKSPACE)
        )
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout[:500],
            'stderr': result.stderr[:500],
            'returncode': result.returncode,
            'error': result.stderr[:200] if result.returncode != 0 else None
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': f'Timeout after {TIMEOUT_SECONDS}s'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def poll_and_execute():
    """Poll queue and execute pending tasks."""
    state = load_state()
    
    pending = [t for t in state.get('delegated_tasks', []) if t.get('status') == 'pending']
    
    if not pending:
        log("No pending tasks")
        return
    
    log(f"Found {len(pending)} pending tasks")
    
    executed = 0
    for task in pending:
        task_id = task.get('task_id')
        delegated_to = task.get('delegated_to')
        task_type = task.get('type')
        
        log(f"Executing task {task_id} ({task_type}) -> {delegated_to}")
        
        result = execute_agent_task(delegated_to, task)
        
        if result.get('success'):
            task['status'] = 'completed'
            task['completed_at'] = datetime.now().isoformat()
            task['result'] = result
            
            state['completed_tasks'].append(task)
            state['agent_last_seen'][delegated_to] = datetime.now().isoformat()
            log(f"Task {task_id} completed successfully")
        else:
            task['status'] = 'failed'
            task['failed_at'] = datetime.now().isoformat()
            task['error'] = result.get('error', 'Unknown error')
            
            state['failed_tasks'].append(task)
            log(f"Task {task_id} FAILED: {result.get('error')}")
        
        executed += 1
    
    # Remove completed/failed from delegated_tasks
    state['delegated_tasks'] = [
        t for t in state.get('delegated_tasks', []) 
        if t.get('status') == 'pending'
    ]
    
    save_state(state)
    log(f"Executor cycle complete: {executed} tasks processed")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Agent Executor')
    parser.add_argument('--poll', action='store_true', help='Poll once')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--test', action='store_true', help='Test mode')
    
    args = parser.parse_args()
    
    if args.test:
        log("Test mode - running single poll")
        poll_and_execute()
    elif args.poll:
        poll_and_execute()
    elif args.daemon:
        log("Running as daemon (5 min interval)")
        while True:
            poll_and_execute()
            import time
            time.sleep(300)
    else:
        parser.print_help()