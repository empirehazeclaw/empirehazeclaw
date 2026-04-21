#!/usr/bin/env python3
"""
Session Activity Analyzer v2
==============================
Erfasst Sir HazeClaw's Haupt-Session Aktivitäten automatisch.

Format: {"type":"message","message":{"role":"...", "content":[...]}}

Usage:
    python3 session_activity_analyzer.py
    python3 session_activity_analyzer.py --stats
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = '/home/clawbot/.openclaw/workspace/ceo'
SESSIONS_DIR = '/home/clawbot/.openclaw/agents/ceo/sessions'
TASK_LOG_DIR = f"{WORKSPACE}/memory/task_log"
UNIFIED_TASKS = f"{TASK_LOG_DIR}/unified_tasks.json"
PROCESSED_MARKER = f"{TASK_LOG_DIR}/session_analyzer_lastrun.json"


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


def get_recent_session_files():
    if not os.path.exists(SESSIONS_DIR):
        return []
    
    files = []
    for f in os.listdir(SESSIONS_DIR):
        if f.endswith('.jsonl'):
            path = os.path.join(SESSIONS_DIR, f)
            mtime = os.path.getmtime(path)
            files.append((mtime, path))
    
    files.sort(reverse=True)
    return [f[1] for f in files[:5]]  # Last 5 sessions


def extract_messages_from_session(session_path, lookback=50):
    """Extract messages from session JSONL file."""
    messages = []
    
    if not os.path.exists(session_path):
        return messages
    
    try:
        with open(session_path, 'r') as f:
            lines = f.readlines()
        
        # Get last N lines
        recent = lines[-lookback:] if len(lines) > lookback else lines
        
        for line in recent:
            try:
                entry = json.loads(line.strip())
                if entry.get('type') == 'message':
                    msg = entry.get('message', {})
                    role = msg.get('role')
                    
                    if role in ('assistant', 'user'):
                        content = msg.get('content', [])
                        text_parts = []
                        
                        for part in content:
                            if isinstance(part, dict):
                                if part.get('type') == 'text':
                                    text_parts.append(part.get('text', ''))
                                elif part.get('type') == 'thinking':
                                    text_parts.append(part.get('thinking', ''))
                        
                        if text_parts:
                            messages.append({
                                'role': role,
                                'text': ' '.join(text_parts),
                                'timestamp': msg.get('timestamp', '')
                            })
            
            except (json.JSONDecodeError, KeyError):
                continue
    
    except Exception as e:
        print(f"Error reading {session_path}: {e}")
    
    return messages


def detect_activity_type(text):
    """Detect activity type from text."""
    text_lower = text.lower()
    
    patterns = {
        'message_response': ['reply', 'antwort', 'nachricht', 'gesendet', 'telegram'],
        'decision': ['approved', 'entschieden', 'decision', 'bestätigt'],
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


def load_unified_tasks():
    return load_json(UNIFIED_TASKS, {'tasks': [], 'last_task_id': 0, 'synced_sources': []})


def save_unified_tasks(data):
    save_json(UNIFIED_TASKS, data)


def log_activity(activity_type, details='', metadata=None):
    """Log an activity to unified tasks."""
    unified = load_unified_tasks()
    
    # Check for duplicates (same type within last 3 minutes)
    recent_cutoff = datetime.now() - timedelta(minutes=3)
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
        'metadata': metadata or {}
    }
    
    unified['tasks'].append(task)
    unified['last_task_id'] += 1
    
    save_unified_tasks(unified)
    return task['task_id']


def get_last_run_time():
    marker = load_json(PROCESSED_MARKER, {})
    last_time = marker.get('last_run')
    if last_time:
        try:
            return datetime.fromisoformat(last_time)
        except:
            pass
    return datetime.now() - timedelta(minutes=30)


def mark_run_complete():
    save_json(PROCESSED_MARKER, {'last_run': datetime.now().isoformat()})


def analyze_and_log():
    """Main analysis function."""
    session_files = get_recent_session_files()
    logged = 0
    
    for session_path in session_files:
        messages = extract_messages_from_session(session_path)
        
        for msg in messages:
            if msg['role'] != 'assistant':
                continue
            
            activity_type = detect_activity_type(msg['text'])
            if activity_type:
                task_id = log_activity(
                    activity_type=activity_type,
                    details=msg['text'][:100],
                    metadata={'source': 'session_analyzer'}
                )
                if task_id:
                    logged += 1
    
    return logged


def show_stats():
    """Show current stats."""
    unified = load_unified_tasks()
    all_tasks = unified.get('tasks', [])
    
    main_tasks = [t for t in all_tasks if t.get('type') == 'main_session']
    
    print(f"\n📊 MAIN SESSION ACTIVITY STATS")
    print("=" * 40)
    print(f"Total Main Session Tasks: {len(main_tasks)}")
    
    if main_tasks:
        by_subtype = {}
        for t in main_tasks:
            sub = t.get('subtype', 'unknown')
            by_subtype[sub] = by_subtype.get(sub, 0) + 1
        
        print("\nBy Type:")
        for sub, count in sorted(by_subtype.items(), key=lambda x: -x[1]):
            print(f"  {sub}: {count}")
        
        # Recent activity
        print("\nRecent (last 5):")
        for t in main_tasks[-5:]:
            ts = t.get('timestamp', '')[:19]
            sub = t.get('subtype', 'unknown')
            details = t.get('details', '')[:50]
            print(f"  {ts} | {sub} | {details}")


if __name__ == '__main__':
    if '--stats' in sys.argv:
        show_stats()
    else:
        print("🔍 Session Activity Analyzer")
        print("=" * 40)
        
        logged = analyze_and_log()
        print(f"✅ Logged {logged} activities")
        
        mark_run_complete()
        
        show_stats()