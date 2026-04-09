#!/usr/bin/env python3
"""
Auto-Archive Script
Archiviert alte Memory-Files automatisch nach 7 Tagen
"""
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")
ARCHIVE_DIR = MEMORY_DIR / "archive"
KEEP_DAYS = 7

# Files die IMMER behalten werden
KEEP_FILES = {
    "MEMORY.md", "INDEX.md", "TODO.md", "QUICK_FACTS.md",
    "SOUL.md", "AGENTS.md", "TOOLS.md"
}

def should_archive(filename):
    """Prüft ob File archiviert werden soll"""
    # IMMER behalten
    if filename in KEEP_FILES:
        return False
    
    # Nur .md files
    if not filename.endswith('.md'):
        return False
    
    # Check age
    filepath = MEMORY_DIR / filename
    if not filepath.exists():
        return False
    
    age_days = (time.time() - filepath.stat().st_mtime) / 86400
    return age_days > KEEP_DAYS

def archive_old_files():
    """Archiviert alte Files"""
    print(f"🔍 Prüfe Files älter als {KEEP_DAYS} Tage...")
    
    archived = 0
    for filename in os.listdir(MEMORY_DIR):
        if should_archive(filename):
            src = MEMORY_DIR / filename
            # Monats-Ordner erstellen
            month = datetime.now().strftime("%Y-%m")
            month_dir = ARCHIVE_DIR / month
            month_dir.mkdir(exist_ok=True)
            
            dst = month_dir / filename
            shutil.move(str(src), str(dst))
            print(f"   📦 Archiviert: {filename}")
            archived += 1
    
    if archived == 0:
        print("   ✅ Keine Files zu archivieren")
    else:
        print(f"   ✅ {archived} Files archiviert")
    
    return archived

if __name__ == "__main__":
    print(f"{'='*50}")
    print(f"📦 AUTO-ARCHIVE - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")
    archive_old_files()
