#!/usr/bin/env python3
"""
Automated Backup System
- SQLite database backup
- Config backup
- Retention policy (keep 7 daily, 4 weekly, 6 monthly)
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
BACKUP_DIR = WORKSPACE / "backups"

# What to backup
BACKUP_SOURCES = [
    ("data/central.db", "database"),
    ("config", "config"),
    ("MEMORY.md", "memory"),
    ("SOUL.md", "soul"),
]

def create_backup(backup_type="daily"):
    """Create a new backup"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{backup_type}_{timestamp}"
    backup_path.mkdir(parents=True, exist_ok=True)
    
    backed_up = []
    
    for source, backup_name in BACKUP_SOURCES:
        source_path = WORKSPACE / source
        if source_path.exists():
            dest = backup_path / backup_name
            if source_path.is_file():
                shutil.copy2(source_path, dest)
            else:
                shutil.copytree(source_path, dest)
            backed_up.append(source)
    
    # Create metadata
    metadata = {
        "timestamp": timestamp,
        "type": backup_type,
        "files": backed_up,
        "created": datetime.now().isoformat()
    }
    
    with open(backup_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Clean old backups
    cleanup_old_backups()
    
    return backup_path

def cleanup_old_backups():
    """Clean up old backups based on retention policy"""
    if not BACKUP_DIR.exists():
        return
    
    backups = sorted(BACKUP_DIR.iterdir(), key=lambda x: x.name, reverse=True)
    
    # Keep: 7 daily, 4 weekly, 6 monthly
    keep = {"daily": 7, "weekly": 4, "monthly": 6}
    
    counts = {"daily": 0, "weekly": 0, "monthly": 0}
    
    for backup in backups:
        if backup.is_dir():
            # Determine type from name
            btype = backup.name.split("_")[0]
            if btype in counts:
                counts[btype] += 1
                if counts[btype] > keep[btype]:
                    shutil.rmtree(backup)
                    print(f"🗑️ Deleted old backup: {backup.name}")

def restore_backup(backup_name):
    """Restore from backup"""
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        return False, "Backup not found"
    
    metadata_path = backup_path / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        for file in metadata.get("files", []):
            source = backup_path / file
            dest = WORKSPACE / file
            if source.exists():
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        os.remove(dest)
                
                if source.is_file():
                    shutil.copy2(source, dest)
                else:
                    shutil.copytree(source, dest)
        
        return True, f"Restored from {backup_name}"
    
    return False, "No metadata found"

def list_backups():
    """List all backups"""
    if not BACKUP_DIR.exists():
        return []
    
    backups = []
    for backup in sorted(BACKUP_DIR.iterdir(), key=lambda x: x.name, reverse=True):
        if backup.is_dir():
            meta_file = backup / "metadata.json"
            if meta_file.exists():
                with open(meta_file) as f:
                    meta = json.load(f)
                backups.append({
                    "name": backup.name,
                    "type": meta.get("type"),
                    "files": len(meta.get("files", [])),
                    "created": meta.get("created")
                })
    return backups

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "backup":
            btype = sys.argv[2] if len(sys.argv) > 2 else "daily"
            path = create_backup(btype)
            print(f"✅ Backup created: {path.name}")
        
        elif cmd == "restore":
            name = sys.argv[2]
            success, msg = restore_backup(name)
            if success:
                print(f"✅ {msg}")
            else:
                print(f"❌ {msg}")
        
        elif cmd == "list":
            backups = list_backups()
            print(f"📦 Backups ({len(backups)}):")
            for b in backups:
                print(f"   {b['name']} - {b['type']} - {b['files']} files")
        
        elif cmd == "cleanup":
            cleanup_old_backups()
            print("✅ Old backups cleaned up")
    else:
        print("Backup System CLI")
        print("Usage: backup.py [backup|restore|list|cleanup]")
