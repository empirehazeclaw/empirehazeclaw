#!/usr/bin/env python3
"""
Sir HazeClaw Auto Backup — IMPROVED
Automatischer Workspace Backup mit Verifizierung.

Features:
- Backup Erstellung mit Kompression
- Git Commit (wenn Änderungen)
- Alte Backups aufräumen (Retention)
- Backup Verifizierung
- Detailliertes Reporting

Usage:
    python3 auto_backup.py
    python3 auto_backup.py --dry-run
    python3 auto_backup.py --verify
"""

import os
import sys
import tarfile
import json
import subprocess
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
RETENTION_DAYS = 7

def get_backup_stats():
    """Holt Backup Statistiken."""
    backups = sorted(BACKUP_DIR.glob("backup_*.tar.gz"))
    
    if not backups:
        return {'count': 0, 'total_size_mb': 0, 'latest': None}
    
    total_size = sum(b.stat().st_size for b in backups)
    latest = max(backups, key=lambda x: x.stat().st_mtime)
    
    return {
        'count': len(backups),
        'total_size_mb': total_size / (1024*1024),
        'latest': latest.name,
        'latest_age_hours': (datetime.now().timestamp() - latest.stat().st_mtime) / 3600
    }

def create_backup():
    """Erstellt Workspace Backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    backup_name = f"backup_{timestamp}.tar.gz"
    backup_path = BACKUP_DIR / backup_name
    
    # Files to include/exclude
    include_dirs = ['workspace']
    
    # Create archive
    print(f"📦 Creating backup: {backup_name}")
    
    try:
        with tarfile.open(backup_path, "w:gz", compresslevel=6) as tar:
            # Add workspace directory
            tar.add(WORKSPACE_DIR, arcname="workspace")
        
        size_mb = os.path.getsize(backup_path) / (1024*1024)
        print(f"  ✅ Backup created: {size_mb:.1f}MB")
        
        return backup_path, size_mb, None
    except Exception as e:
        return None, 0, str(e)

def verify_backup(backup_path):
    """Verifiziert Backup Integrity."""
    if not backup_path or not backup_path.exists():
        return False, "Backup not found"
    
    try:
        # Test tar integrity
        with tarfile.open(backup_path, "r:gz") as tar:
            # Try reading first 10 members
            count = 0
            for member in tar:
                count += 1
                if count > 10:
                    break
        
        return True, f"Verified ({count} files)"
    except Exception as e:
        return False, f"Verification failed: {e}"

def get_git_status():
    """Prüft Git Status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except:
        return ""

def git_backup():
    """Macht Git Commit wenn Änderungen."""
    status = get_git_status()
    
    if not status:
        print("  ℹ️  No changes to commit")
        return True, "No changes"
    
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
        
        # Add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            timeout=10
        )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", f"Auto backup: {timestamp}"],
            cwd=str(WORKSPACE_DIR),
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("  ✅ Git backup committed")
            return True, "Committed"
        else:
            error = result.stderr.decode() if result.stderr else "Unknown error"
            if "nothing to commit" in error.lower():
                print("  ℹ️  No changes to commit")
                return True, "No changes"
            print(f"  ⚠️  Git commit failed: {error[:100]}")
            return False, error[:100]
    except Exception as e:
        print(f"  ⚠️  Git backup failed: {e}")
        return False, str(e)

def cleanup_old_backups():
    """Entfernt alte Backups."""
    count = 0
    freed_mb = 0
    
    for backup in BACKUP_DIR.glob("backup_*.tar.gz"):
        age_days = (datetime.now().timestamp() - backup.stat().st_mtime) / 86400
        
        if age_days > RETENTION_DAYS:
            try:
                size_mb = backup.stat().st_size / (1024*1024)
                backup.unlink()
                count += 1
                freed_mb += size_mb
                print(f"  🗑️  Removed: {backup.name} ({size_mb:.1f}MB)")
            except Exception as e:
                print(f"  ⚠️  Could not delete {backup.name}: {e}")
    
    return count, freed_mb

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sir HazeClaw Auto Backup - Improved')
    parser.add_argument('--dry-run', action='store_true', help='Dry run only')
    parser.add_argument('--verify', action='store_true', help='Verify latest backup')
    args = parser.parse_args()
    
    print(f"=== Sir HazeClaw Auto Backup ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Show current stats
    stats = get_backup_stats()
    print(f"📊 Current backups: {stats['count']}")
    if stats['count'] > 0:
        print(f"   Total size: {stats['total_size_mb']:.1f}MB")
        print(f"   Latest: {stats['latest']} ({stats['latest_age_hours']:.1f}h ago)")
    print()
    
    if args.verify:
        print("🔍 Verifying latest backup...")
        if stats['latest']:
            latest = BACKUP_DIR / stats['latest']
            ok, msg = verify_backup(latest)
            print(f"  {'✅' if ok else '❌'} {msg}")
        else:
            print("  ⚠️  No backups to verify")
        return
    
    if args.dry_run:
        print("🧪 DRY RUN - No changes made")
        print()
        print("Would:")
        print("  1. Create new backup archive")
        print("  2. Git commit if changes exist")
        print("  3. Clean backups older than 7 days")
        return
    
    # 1. Create backup
    print("📦 Step 1: Creating backup...")
    backup_path, size_mb, error = create_backup()
    
    if error:
        print(f"  ❌ Backup failed: {error}")
    else:
        # Verify
        print("  🔍 Verifying backup...")
        ok, msg = verify_backup(backup_path)
        print(f"  {'✅' if ok else '⚠️'} {msg}")
    
    print()
    
    # 2. Git backup
    print("📝 Step 2: Git backup...")
    git_ok, git_msg = git_backup()
    
    print()
    
    # 3. Cleanup old backups
    print("🧹 Step 3: Cleaning old backups...")
    cleaned, freed_mb = cleanup_old_backups()
    if cleaned > 0:
        print(f"  🗑️  Cleaned {cleaned} backups, freed {freed_mb:.1f}MB")
    else:
        print("  ℹ️  No old backups to clean")
    
    print()
    
    # Summary
    print("=== Summary ===")
    print(f"  Backup: {'✅ Created' if backup_path else '❌ Failed'}")
    print(f"  Git: {'✅' if git_ok else '⚠️'}")
    print(f"  Cleaned: {cleaned} old backups")
    
    # Show new stats
    new_stats = get_backup_stats()
    print()
    print(f"📊 New backup count: {new_stats['count']}")
    
    print()
    print("=== Done ===")

if __name__ == "__main__":
    main()