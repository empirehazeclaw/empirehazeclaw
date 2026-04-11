#!/usr/bin/env python3
"""
💾 Session Memory Manager - Auto-saves important context
Integration: Called by autonomous_loop.py or manually
"""

import os
import json
from datetime import datetime
from pathlib import Path

SESSION_DIR = '/home/clawbot/.openclaw/workspace/memory/sessions'
ARCHIVE_DIR = '/home/clawbot/.openclaw/workspace/memory/archive/sessions'

def save_session_note(session_key: str, context: str, category: str = "general"):
    """Save a session note to memory"""
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    session_file = os.path.join(SESSION_DIR, f'{datetime.now().strftime("%Y-%m-%d")}.json')
    
    # Load or create
    if os.path.exists(session_file):
        with open(session_file) as f:
            data = json.load(f)
    else:
        data = {"date": datetime.now().date().isoformat(), "sessions": []}
    
    # Add session entry
    data["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "key": session_key,
        "category": category,
        "context": context[:500]  # Truncate
    })
    
    with open(session_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return session_file

def get_recent_sessions(days: int = 7):
    """Get recent session notes"""
    sessions = []
    
    if not os.path.exists(SESSION_DIR):
        return sessions
    
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.json'):
            path = os.path.join(SESSION_DIR, f)
            with open(path) as file:
                data = json.load(file)
                sessions.append(data)
    
    return sessions

def archive_old_sessions(days: int = 30):
    """Archive sessions older than N days"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    cutoff = datetime.now().timestamp() - (days * 86400)
    archived = 0
    
    for f in os.listdir(SESSION_DIR):
        if f.endswith('.json'):
            path = os.path.join(SESSION_DIR, f)
            if os.path.getmtime(path) < cutoff:
                archive_path = os.path.join(ARCHIVE_DIR, f)
                os.rename(path, archive_path)
                archived += 1
    
    return archived

def save_daily_summary(date: str, summary: str, metrics: dict = None):
    """Save daily summary"""
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    summary_file = os.path.join(SESSION_DIR, f'daily_{date}.json')
    
    data = {
        "date": date,
        "summary": summary,
        "metrics": metrics or {},
        "saved_at": datetime.now().isoformat()
    }
    
    with open(summary_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return summary_file

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  save <key> <context>  - Save session note")
        print("  recent [days]          - Get recent sessions")
        print("  archive [days]         - Archive old sessions")
        print("  summary <date> <text>  - Save daily summary")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'save':
        key = sys.argv[2] if len(sys.argv) > 2 else "manual"
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        result = save_session_note(key, context)
        print(f"✅ Saved to {result}")
    
    elif cmd == 'recent':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        sessions = get_recent_sessions(days)
        print(f"📅 Recent sessions (last {days} days): {len(sessions)}")
        for s in sessions:
            print(f"  - {s.get('date')}: {len(s.get('sessions', []))} entries")
    
    elif cmd == 'archive':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        count = archive_old_sessions(days)
        print(f"✅ Archived {count} old sessions")
    
    elif cmd == 'summary':
        if len(sys.argv) < 4:
            print("Usage: summary <date> <text>")
            sys.exit(1)
        date = sys.argv[2]
        text = sys.argv[3]
        result = save_daily_summary(date, text)
        print(f"✅ Summary saved to {result}")

if __name__ == '__main__':
    main()