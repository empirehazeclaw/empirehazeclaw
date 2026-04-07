#!/usr/bin/env python3
"""Automatic Session Cleanup - Runs daily to keep system fast"""
import os
import time
from pathlib import Path

SESSION_DIR = Path("/home/clawbot/.openclaw/agents/main/sessions")
MAX_AGE_DAYS = 1  # Delete files older than 1 day

def cleanup():
    count = 0
    for f in SESSION_DIR.glob("*.jsonl"):
        age_days = (time.time() - f.stat().st_mtime) / 86400
        if age_days > MAX_AGE_DAYS:
            f.unlink()
            count += 1
    print(f"🧹 Cleaned {count} old session files")

if __name__ == "__main__":
    cleanup()
