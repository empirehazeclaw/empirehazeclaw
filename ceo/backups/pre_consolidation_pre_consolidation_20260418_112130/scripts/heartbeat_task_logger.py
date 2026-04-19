#!/usr/bin/env python3
"""
Heartbeat Task Logger
=====================
Erfasst meine Aktivitäten während des Heartbeats automatisch.

Usage:
    python3 heartbeat_task_logger.py
"""

import json
import os
import sys
from datetime import datetime, timedelta

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"
SESSION_DIR = '/home/clawbot/.openclaw/agents/ceo/sessions'


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


def get_recent_activities(lookback_minutes=15):
    """Get activities from recent sessions."""
    if not os.path.exists(SESSION_DIR):
        return []
    
    activities = []
    cutoff = datetime.now() - timedelta(minutes=lookback_minutes)
    
    # Find main session
    main_session = None
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.jsonl') and 'direct' in f or '5392634979' in f:
            path = os.path.join(SESSION_DIR, f)
            mtime = os.path.getmtime(path)
            if mtime > (datetime.now() - timedelta(minutes=30)).timestamp():
                main_session = path
                break
    
    if not main_session:
        return []
    
    # Parse recent lines
    try:
        with open(main_session, 'r') as f:
            lines = f.readlines()
        
        for line in lines[-50:]:  # Last 50 lines
            try:
                entry = json.loads(line.strip())
                if entry.get('type') == 'message':
                    msg = entry.get('message', {})
                    role = msg.get('role')
                    
                    if role == 'assistant':
                        content = msg.get('content', [])
                        for part in content:
                            if isinstance(part, dict) and part.get('type') == 'text':
                                text = part.get('text', '')
                                if text.strip():
                                    activities.append({
                                        'text': text,
                                        'timestamp': msg.get('timestamp', '')
                                    })
            except:
                continue
    except:
        pass
    
    return activities


def detect_activity(text):
    """Detect activity type from text."""
    text_lower = text.lower()
    
    patterns = {
        'message_response': ['reply', 'antwort', 'nachricht', 'gesendet', 'telegram'],
        'decision': ['approved', 'entschieden', 'decision', 'bestätigt', 'confirm'],
        'file_operation': ['created', 'updated', 'written', 'edited', 'file'],
        'kg_update': ['kg_updated', 'knowledge', 'entity', 'relation'],
        'learning_integration': ['learning', 'pattern', 'learned'],
        'script_execution': ['executed', 'ran script', 'python3'],
        'health_check': ['health', 'check', 'status'],
        'research': ['research', 'search', 'web']
    }
    
    for atype, keywords in patterns.items():
        for keyword in keywords:
            if keyword in text_lower:
                return atype
    
    return None


def log_activity(activity_type, details=''):
    """Log an activity."""
    unified = load_json(UNIFIED_TASKS, {'tasks': [], 'last_task_id': 0})
    
    # Deduplicate (same type in last 5 min)
    recent_cutoff = datetime.now() - timedelta(minutes=5)
    for task in unified['tasks'][-10:]:
        if task.get('type') == 'main_session' and task.get('subtype') == activity_type:
            try:
                task_time = datetime.fromisoformat(task['timestamp'])
                if task_time > recent_cutoff:
                    return None
            except:
                pass
    
    task = {
        'task_id': unified['last_task_id'] + 1,
        'timestamp': datetime.now().isoformat(),
        'type': 'main_session',
        'subtype': activity_type,
        'outcome': 'success',
        'details': details[:150] if details else '',
        'metadata': {'source': 'heartbeat'}
    }
    
    unified['tasks'].append(task)
    unified['last_task_id'] += 1
    save_json(UNIFIED_TASKS, unified)
    
    return task['task_id']


def main():
    """Main heartbeat logging."""
    activities = get_recent_activities(lookback_minutes=15)
    
    logged = 0
    for activity in activities:
        detected = detect_activity(activity['text'])
        if detected:
            task_id = log_activity(detected, activity['text'])
            if task_id:
                logged += 1
    
    return logged


if __name__ == '__main__':
    logged = main()
    if logged > 0:
        print(f"✅ Logged {logged} activities from heartbeat")
    else:
        print("No new activities")