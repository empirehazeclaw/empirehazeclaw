#!/usr/bin/env python3
"""
Session Cleanup - Löscht alte Sessions automatisch
"""

import os
import glob
from datetime import datetime, timedelta

SESSION_DIR = "/home/clawbot/.openclaw/agents/main/sessions"
MAX_AGE_DAYS = 7

def cleanup_sessions():
    """Lösche alte Session-Dateien"""
    deleted = 0
    
    for session_file in glob.glob(f"{SESSION_DIR}/*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(os.path.getmtime(session_file))
            age = (datetime.now() - mtime).days
            
            if age > MAX_AGE_DAYS:
                os.remove(session_file)
                deleted += 1
                print(f"🗑️ Deleted: {os.path.basename(session_file)} ({age}d old)")
                
        except Exception as e:
            print(f"❌ Error: {session_file}: {e}")
    
    # Alte Subagent-Sessions auch
    subagent_dir = "/home/clawbot/.openclaw/agents/subagent/sessions"
    if os.path.exists(subagent_dir):
        for session_file in glob.glob(f"{subagent_dir}/*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(session_file))
                age = (datetime.now() - mtime).days
                
                if age > MAX_AGE_DAYS:
                    os.remove(session_file)
                    deleted += 1
            except:
                pass
    
    print(f"\n✅ Session-Cleanup abgeschlossen: {deleted} Sessions gelöscht")
    return deleted

if __name__ == "__main__":
    cleanup_sessions()
