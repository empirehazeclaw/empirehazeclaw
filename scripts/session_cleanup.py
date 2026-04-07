#!/usr/bin/env python3
"""Session Cleanup - Delete sessions older than 7 days."""
import os
import time
from pathlib import Path

SESSIONS_DIR = Path("/home/clawbot/.openclaw/sessions")
MAX_AGE_DAYS = 7
CUTOFF = time.time() - (MAX_AGE_DAYS * 86400)

deleted = 0
kept = 0

for session_dir in SESSIONS_DIR.iterdir():
    if not session_dir.is_dir():
        continue
    mtime = session_dir.stat().st_mtime
    if mtime < CUTOFF:
        # Check if session is currently active
        session_key = session_dir.name
        # Don't delete if it's a known active session
        if "telegram" in session_key or "ceo" in session_key:
            kept += 1
            continue
        import shutil
        shutil.rmtree(session_dir)
        deleted += 1
    else:
        kept += 1

print(f"Session cleanup: deleted={deleted}, kept={kept}")
