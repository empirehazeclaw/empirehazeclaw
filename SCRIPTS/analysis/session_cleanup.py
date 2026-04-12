#!/usr/bin/env python3
"""
Sir HazeClaw Session Cleanup
Automatisch alte Sessions archivieren und tmp files löschen.

Usage:
    python3 session_cleanup.py              # Scan + cleanup
    python3 session_cleanup.py --dry-run  # Show what would be deleted
    python3 session_cleanup.py --archive  # Archive only, don't delete
    python3 session_cleanup.py --status    # Show cleanup status
"""

import os
import shutil
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SESSIONS_DIR = WORKSPACE / "sessions"
ARCHIVE_DIR = WORKSPACE / "archive" / "sessions"
TMP_DIR = WORKSPACE / "tmp"
LOG_FILE = WORKSPACE / "logs" / "session_cleanup.log"
STATE_FILE = WORKSPACE / "data" / "session_cleanup_state.json"

MAX_AGE_DAYS = 7  # Archive sessions older than 7 days
MAX_TMP_SIZE_MB = 100  # Alert if tmp > 100MB

def log(message, level="INFO"):
    """Log to file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")

def load_state():
    """Load cleanup state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "last_cleanup": None,
        "archived_count": 0,
        "deleted_count": 0,
        "freed_mb": 0,
        "last_error": None
    }

def save_state(state):
    """Save cleanup state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_old_sessions():
    """Find sessions older than MAX_AGE_DAYS."""
    cutoff = datetime.now() - timedelta(days=MAX_AGE_DAYS)
    old_sessions = []
    
    if not SESSIONS_DIR.exists():
        return old_sessions
    
    for session in SESSIONS_DIR.iterdir():
        if session.is_dir():
            mtime = datetime.fromtimestamp(session.stat().st_mtime)
            if mtime < cutoff:
                age_days = (datetime.now() - mtime).days
                size_mb = sum(f.stat().st_size for f in session.rglob("*") if f.is_file()) / (1024 * 1024)
                old_sessions.append({
                    "path": session,
                    "mtime": mtime.isoformat(),
                    "age_days": age_days,
                    "size_mb": round(size_mb, 2)
                })
    
    return sorted(old_sessions, key=lambda x: x["mtime"])

def get_tmp_size():
    """Calculate tmp directory size."""
    if not TMP_DIR.exists():
        return 0
    
    total = sum(f.stat().st_size for f in TMP_DIR.rglob("*") if f.is_file())
    return total / (1024 * 1024)  # MB

def archive_session(session_info):
    """Archive a single session."""
    try:
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        
        source = session_info["path"]
        dest = ARCHIVE_DIR / source.name
        
        # Move to archive
        shutil.move(str(source), str(dest))
        
        log(f"Archived: {source.name} ({session_info['size_mb']}MB, {session_info['age_days']} days old)")
        return session_info["size_mb"]
    except Exception as e:
        log(f"Failed to archive {session_info['path'].name}: {e}", "ERROR")
        return 0

def delete_tmp_files():
    """Clean up tmp directory."""
    if not TMP_DIR.exists():
        return 0, 0
    
    freed = 0
    count = 0
    
    for tmp_file in TMP_DIR.rglob("*"):
        if tmp_file.is_file():
            try:
                size = tmp_file.stat().st_size / (1024 * 1024)
                tmp_file.unlink()
                freed += size
                count += 1
            except Exception as e:
                log(f"Failed to delete {tmp_file}: {e}", "WARN")
    
    return freed, count

def run_cleanup(dry_run=False):
    """Run full cleanup."""
    state = load_state()
    log("Starting session cleanup")
    
    # Check tmp size
    tmp_size = get_tmp_size()
    print(f"📊 **Session Cleanup**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    if tmp_size > MAX_TMP_SIZE_MB:
        print(f"   ⚠️ tmp size: {tmp_size:.1f}MB (threshold: {MAX_TMP_SIZE_MB}MB)")
    else:
        print(f"   ✅ tmp size: {tmp_size:.1f}MB (OK)")
    
    # Find old sessions
    old_sessions = get_old_sessions()
    print(f"   Old sessions (>7 days): {len(old_sessions)}")
    
    if dry_run:
        print()
        print("   **Would archive:**")
        for s in old_sessions[:10]:
            print(f"     - {s['path'].name}: {s['size_mb']}MB, {s['age_days']} days old")
        if len(old_sessions) > 10:
            print(f"     ... and {len(old_sessions) - 10} more")
        return
    
    # Archive old sessions
    archived_mb = 0
    for session in old_sessions:
        archived_mb += archive_session(session)
        state["archived_count"] += 1
    
    # Clean tmp
    freed_mb, deleted_count = delete_tmp_files()
    state["deleted_count"] += deleted_count
    state["freed_mb"] += freed_mb
    state["last_cleanup"] = datetime.now().isoformat()
    
    print()
    print(f"   **Results:**")
    print(f"     Archived: {state['archived_count']} sessions ({archived_mb:.1f}MB)")
    print(f"     Deleted: {deleted_count} tmp files ({freed_mb:.1f}MB)")
    print(f"     Total freed: {archived_mb + freed_mb:.1f}MB")
    
    save_state(state)
    log(f"Cleanup complete: archived {state['archived_count']}, deleted {deleted_count}, freed {archived_mb + freed_mb:.1f}MB")
    
    return True

def show_status():
    """Show cleanup status."""
    state = load_state()
    tmp_size = get_tmp_size()
    old_sessions = get_old_sessions()
    
    print("📊 **Session Cleanup Status**")
    print(f"   Last Cleanup: {state['last_cleanup'] or 'never'}")
    print(f"   Sessions Archived: {state['archived_count']}")
    print(f"   Tmp Files Deleted: {state['deleted_count']}")
    print(f"   Total Space Freed: {state['freed_mb']:.1f}MB")
    print()
    print(f"   Current tmp size: {tmp_size:.1f}MB")
    print(f"   Old sessions waiting: {len(old_sessions)}")

def main():
    if len(sys.argv) < 2:
        return 0 if run_cleanup() else 1
    
    arg = sys.argv[1]
    
    if arg == "--dry-run":
        run_cleanup(dry_run=True)
    elif arg == "--archive":
        old_sessions = get_old_sessions()
        for session in old_sessions:
            archive_session(session)
        print(f"Archived {len(old_sessions)} sessions")
    elif arg == "--status":
        show_status()
    elif arg == "--help":
        print(__doc__)
    else:
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main() or 0)