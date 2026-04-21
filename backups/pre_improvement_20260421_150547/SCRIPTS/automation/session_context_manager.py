#!/usr/bin/env python3
"""
🔄 Session Context Manager — Sir HazeClaw
Auto-promotes important sessions to long-term memory.

Goals:
1. Track session importance
2. Auto-summarize stale sessions
3. Archive completed projects
4. Keep memory organized

Usage:
    python3 session_context_manager.py      # Analyze and promote
    python3 session_context_manager.py --archive  # Archive old sessions
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
LOG_FILE = WORKSPACE / "logs/session_context_manager.log"
STATE_FILE = WORKSPACE / "data/session_context_state.json"

# Thresholds
STALE_SESSION_DAYS = 7  # Session inactive for 7 days = stale
ARCHIVE_AFTER_DAYS = 30  # Archive after 30 days

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_run": None, "sessions_promoted": 0, "sessions_archived": 0}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_sessions() -> List[Dict]:
    """Get all session files."""
    sessions = []
    
    if not MEMORY_DIR.exists():
        return sessions
    
    # Check short_term, long_term, episodes
    for subdir in ["short_term", "long_term", "episodes"]:
        subdir_path = MEMORY_DIR / subdir
        if subdir_path.exists():
            for f in subdir_path.glob("*.md"):
                stat = f.stat()
                sessions.append({
                    "path": str(f),
                    "name": f.name,
                    "type": subdir,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "size": stat.st_size
                })
    
    return sessions

def analyze_sessions(sessions: List[Dict]) -> Dict:
    """Analyze sessions for promotion/archival."""
    now = datetime.now()
    
    stale = []
    archive_candidates = []
    healthy = []
    
    for session in sessions:
        days_inactive = (now - session["modified"]).days
        
        if days_inactive >= ARCHIVE_AFTER_DAYS:
            archive_candidates.append({**session, "days_inactive": days_inactive})
        elif days_inactive >= STALE_SESSION_DAYS:
            stale.append({**session, "days_inactive": days_inactive})
        else:
            healthy.append({**session, "days_inactive": days_inactive})
    
    return {
        "stale": stale,
        "archive_candidates": archive_candidates,
        "healthy": healthy
    }

def promote_session(session: Dict) -> bool:
    """Promote stale session to long_term."""
    try:
        src = Path(session["path"])
        
        if session["type"] == "long_term":
            return False  # Already promoted
        
        dest_dir = MEMORY_DIR / "long_term"
        dest_dir.mkdir(exist_ok=True)
        
        dest = dest_dir / src.name
        src.rename(dest)
        
        log(f"Promoted: {src.name} -> long_term/", "ACTION")
        return True
    except Exception as e:
        log(f"Failed to promote {session['path']}: {e}", "ERROR")
        return False

def archive_session(session: Dict) -> bool:
    """Archive old session."""
    try:
        src = Path(session["path"])
        
        archive_dir = MEMORY_DIR / "ARCHIVE"
        archive_dir.mkdir(exist_ok=True)
        
        dest = archive_dir / src.name
        src.rename(dest)
        
        log(f"Archived: {src.name}", "ACTION")
        return True
    except Exception as e:
        log(f"Failed to archive {session['path']}: {e}", "ERROR")
        return False

def main():
    log("=== Session Context Manager ===")
    
    sessions = get_sessions()
    log(f"Found {len(sessions)} sessions")
    
    analysis = analyze_sessions(sessions)
    
    log(f"Healthy: {len(analysis['healthy'])}, Stale: {len(analysis['stale'])}, Archive: {len(analysis['archive_candidates'])}")
    
    promoted = 0
    archived = 0
    
    # Auto-promote stale sessions
    if "--archive" in sys.argv or True:  # Always auto-promote for now
        for session in analysis["stale"][:5]:  # Max 5 at a time
            if promote_session(session):
                promoted += 1
        
        # Archive old ones only if --archive flag
        if "--archive" in sys.argv:
            for session in analysis["archive_candidates"]:
                if archive_session(session):
                    archived += 1
    
    # Summary
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["sessions_promoted"] += promoted
    state["sessions_archived"] += archived
    save_state(state)
    
    log(f"Done. Promoted: {promoted}, Archived: {archived}")
    
    return promoted + archived

if __name__ == "__main__":
    main()
