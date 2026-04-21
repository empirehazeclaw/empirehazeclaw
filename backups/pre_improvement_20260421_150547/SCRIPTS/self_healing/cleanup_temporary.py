#!/usr/bin/env python3
"""
cleanup_temporary.py - Auto-cleanup for TEMPORARY directory
Sir HazeClaw - 2026-04-12

Runs via cron to clean old temporary files.
Retention:
- logs/: 14 days
- memory/: 30 days
- task_reports/: 7 days
- audio/: 7 days
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
TEMPORARY = WORKSPACE / "TEMPORARY"

RETENTION = {
    "logs": 14,
    "memory": 30,
    "task_reports": 7,
    "audio": 7,
    "logs_ceo": 14,
    "memory_ceo": 30,
    "task_reports_ceo": 7,
}

def cleanup_folder(folder: Path, days: int) -> int:
    """Delete files older than `days`. Returns count deleted."""
    if not folder.exists():
        return 0
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for item in folder.rglob("*"):
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                item.unlink()
                deleted += 1
                print(f"🗑️  Deleted: {item.relative_to(WORKSPACE)}")
    
    return deleted

def main():
    print(f"🧹 TEMPORARY CLEANUP - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)
    
    total_deleted = 0
    
    for folder, days in RETENTION.items():
        folder_path = TEMPORARY / folder
        if folder_path.exists():
            deleted = cleanup_folder(folder_path, days)
            total_deleted += deleted
            if deleted > 0:
                print(f"   {folder}/: {deleted} files deleted")
    
    print()
    if total_deleted > 0:
        print(f"✅ Total: {total_deleted} old files cleaned up")
    else:
        print("✅ Nothing to clean")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
