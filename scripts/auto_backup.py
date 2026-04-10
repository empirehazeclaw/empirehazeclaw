#!/usr/bin/env python3
"""
Sir HazeClaw Auto Backup
Automatischer Workspace Backup.

Usage:
    python3 auto_backup.py
    python3 auto_backup.py --dry-run
"""

import os
import sys
import tarfile
import json
import shutil
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
RETENTION_DAYS = 7

def create_backup():
    """Erstellt Workspace Backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_name = f"backup_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / backup_name
    
    print(f"Creating backup: {backup_name}")
    
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(WORKSPACE_DIR, arcname="workspace")
    
    size_mb = os.path.getsize(backup_path) / (1024*1024)
    print(f"✅ Backup created: {size_mb:.1f}MB")
    
    return backup_path, size_mb

def cleanup_old_backups():
    """Entfernt alte Backups."""
    count = 0
    for backup in BACKUP_DIR.glob("backup_*.tar.gz"):
        age_days = (datetime.now() - datetime.fromtimestamp(backup.stat().st_mtime)).days
        
        if age_days > RETENTION_DAYS:
            try:
                backup.unlink()
                count += 1
                print(f"🗑️  Removed old backup: {backup.name}")
            except Exception as e:
                print(f"⚠️  Could not delete {backup.name}: {e}")
    
    return count

def git_backup():
    """Macht Git Commit."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["git", "add", "-A"],
            cwd=WORKSPACE_DIR,
            capture_output=True
        )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        result = subprocess.run(
            ["git", "commit", "-m", f"Auto backup: {timestamp}"],
            cwd=WORKSPACE_DIR,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("✅ Git backup committed")
            return True
        else:
            if "nothing to commit" in result.stdout.decode():
                print("ℹ️  No changes to commit")
            else:
                print(f"⚠️  Git commit failed: {result.stderr.decode()}")
            return False
    except Exception as e:
        print(f"⚠️  Git backup failed: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto Backup')
    parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    args = parser.parse_args()
    
    print(f"=== Sir HazeClaw Auto Backup ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    if args.dry_run:
        print("🧪 DRY RUN - No changes made")
        print()
    
    # Create backup
    if not args.dry_run:
        backup_path, size_mb = create_backup()
    else:
        print("Would create backup...")
        backup_path = None
    
    print()
    
    # Git backup
    if not args.dry_run:
        git_backup()
    else:
        print("Would commit to git...")
    
    print()
    
    # Cleanup old backups
    if not args.dry_run:
        cleaned = cleanup_old_backups()
        if cleaned > 0:
            print(f"🧹 Cleaned {cleaned} old backups")
        else:
            print("ℹ️  No old backups to clean")
    else:
        print("Would clean old backups...")
    
    print()
    print("=== Done ===")

if __name__ == "__main__":
    main()