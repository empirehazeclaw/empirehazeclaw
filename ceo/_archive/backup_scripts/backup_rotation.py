#!/usr/bin/env python3
"""
💾 BACKUP ROTATION
=================
Manages backup retention
"""

import os
import glob
from datetime import datetime, timedelta

BACKUP_DIR = Path("data/backups")
MAX_DAYS = 30

def rotate():
    """Remove backups older than MAX_DAYS"""
    if not BACKUP_DIR.exists():
        return
    
    cutoff = datetime.now() - timedelta(days=MAX_DAYS)
    removed = 0
    
    for backup in BACKUP_DIR.glob("*"):
        if backup.is_file():
            mtime = datetime.fromtimestamp(backup.stat().st_mtime)
            if mtime < cutoff:
                backup.unlink()
                removed += 1
    
    print(f"✅ Removed {removed} old backups")

if __name__ == "__main__":
    from pathlib import Path
    rotate()
