#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Memory Cleaner Skill
Automatically cleans up memory files based on rules.

Rules:
- Archive: Files older than 30 days in main memory/
- Keep: INDEX.md, goals.json, latest 3 daily notes
- Report: What was archived, what remains

Run via cron or on-demand.
Triggered by: memory_cleaner skill

Usage:
    python3 memory_cleaner.py          # Dry run
    python3 memory_cleaner.py --fix   # Actually clean
"""

import os
import re
import sys
import json
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MEMORY_DIR = WORKSPACE / "memory"
ARCHIVE_DIR = MEMORY_DIR / "ARCHIVE"
LOG_FILE = WORKSPACE.parent / "logs" / "memory_cleaner.log"

# Rules
MAX_AGE_DAYS = 30
KEEP_FILES = ["INDEX.md", "goals.json", "heartbeat-state.json"]
KEEP_DAYS = 5  # Keep last 5 days of daily notes

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def get_memory_stats():
    """Get current memory stats."""
    all_files = list(MEMORY_DIR.glob("*.md")) + list(MEMORY_DIR.glob("*.json"))
    total_size = sum(f.stat().st_size for f in all_files if f.is_file())
    
    by_age = {"<7d": 0, "7-30d": 0, ">30d": 0, "archived": 0}
    
    for f in MEMORY_DIR.glob("*.md"):
        if f.name in KEEP_FILES:
            continue
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        if age_days <= 7:
            by_age["<7d"] += 1
        elif age_days <= 30:
            by_age["7-30d"] += 1
        else:
            by_age[">30d"] += 1
    
    archived = len(list(ARCHIVE_DIR.glob("**/*.md"))) if ARCHIVE_DIR.exists() else 0
    
    return {
        "total_files": len(all_files),
        "total_size_kb": total_size / 1024,
        "by_age": by_age,
        "archived": archived
    }

def should_keep(f: Path) -> bool:
    """Check if file should be kept."""
    name = f.name
    
    # Always keep these
    if name in KEEP_FILES:
        return True
    
    # Keep daily notes from last KEEP_DAYS days
    if re.match(r'\d{4}-\d{2}-\d{2}\.md', name):
        age_days = (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days
        if age_days <= KEEP_DAYS:
            return True
    
    return False

def archive_old_files(fix: bool = False):
    """Archive files older than MAX_AGE_DAYS."""
    archived = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=MAX_AGE_DAYS)
    
    for md_file in MEMORY_DIR.glob("*.md"):
        if should_keep(md_file):
            continue
        
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if mtime.replace(tzinfo=timezone.utc) < cutoff:
            if fix:
                # Archive it
                year = mtime.strftime("%Y-%m")
                target_dir = ARCHIVE_DIR / year
                target_dir.mkdir(parents=True, exist_ok=True)
                
                target = target_dir / md_file.name
                shutil.move(str(md_file), str(target))
                archived.append(str(target))
            else:
                archived.append(f"[DRY RUN] Would archive: {md_file.name}")
    
    return archived

def main():
    dry_run = "--fix" not in sys.argv
    
    log("Memory Cleaner START")
    
    # Get stats before
    stats_before = get_memory_stats()
    log(f"Before: {stats_before['total_files']} files, {stats_before['by_age']}")
    
    # Archive
    archived = archive_old_files(fix=not dry_run)
    
    # Get stats after
    stats_after = get_memory_stats()
    
    if archived:
        log(f"Archived: {len(archived)} files")
        for a in archived[:5]:
            log(f"  - {a}")
        if len(archived) > 5:
            log(f"  ... and {len(archived) - 5} more")
    else:
        log("No files to archive")
    
    log(f"After: {stats_after['total_files']} files")
    log("Memory Cleaner END")
    
    print(f"\n✅ Memory Cleaner: {len(archived)} files archived")
    print(f"   Before: {stats_before['total_files']} files")
    print(f"   After: {stats_after['total_files']} files")
    
    return 0 if archived else 0

if __name__ == "__main__":
    sys.exit(main())