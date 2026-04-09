#!/usr/bin/env python3
"""Session Cleanup - Delete sessions older than 7 days."""
import os
import time
import shutil
from pathlib import Path

# Sessions stored per agent
SESSIONS_DIRS = [
    Path("/home/clawbot/.openclaw/agents/ceo/sessions"),
    Path("/home/clawbot/.openclaw/agents/builder/sessions"),
    Path("/home/clawbot/.openclaw/agents/main/sessions"),
]
MAX_AGE_DAYS = 7
CUTOFF = time.time() - (MAX_AGE_DAYS * 86400)

deleted = 0
kept = 0

for sessions_base in SESSIONS_DIRS:
    if not sessions_base.exists():
        continue
    for session_file in sessions_base.glob("*.jsonl"):
        # Skip deleted files
        if ".deleted." in session_file.name:
            continue
        try:
            mtime = session_file.stat().st_mtime
            session_key = session_file.stem
            # Keep very recent and active sessions
            if mtime > CUTOFF:
                kept += 1
                continue
            # Delete old sessions
            session_file.unlink()
            deleted += 1
            print(f"  Deleted: {session_file.name}")
        except Exception as e:
            print(f"  Error: {e}")

print(f"Session cleanup: deleted={deleted}, kept={kept}")
