#!/usr/bin/env python3
"""
Sir HazeClaw Backup Verification Script
Prüft ob Backups existieren und validiert sie.

Usage:
    python3 backup_verify.py
    python3 backup_verify.py --fix  # Erstellt backups wenn fehlen
"""

import os
import sys
import tarfile
import json
from datetime import datetime, timedelta
from pathlib import Path

# Config
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")
GITHUB_DIR = Path("/home/clawbot/.openclaw/workspace/.git")
RETENTION_DAYS = 7

def check_server_backup():
    """Prüft ob Server Backup existiert."""
    today = datetime.now().strftime("%Y%m%d")
    
    # Check for today's backup
    pattern = f"backup_{today}_*.tar.gz"
    backups = list(BACKUP_DIR.glob(pattern))
    
    if backups:
        latest = max(backups, key=os.path.getmtime)
        size = os.path.getsize(latest) / (1024*1024)
        age_hours = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(latest))).seconds / 3600
        
        return True, f"✅ Server Backup: {latest.name} ({size:.1f}MB, {age_hours:.1f}h alt)"
    else:
        return False, f"❌ Kein Server Backup heute (Pattern: {pattern})"

def check_github_backup():
    """Prüft ob GitHub Commit heute existiert."""
    if not GITHUB_DIR.exists():
        return False, "❌ GitHub nicht initialisiert"
    
    # Check git log for today's commit
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "-1", "--since='today 00:00'"],
        cwd=GITHUB_DIR.parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout.strip():
        return True, f"✅ GitHub Backup: {result.stdout.strip()[:60]}"
    else:
        return False, "❌ Kein GitHub Commit heute"

def check_backup_size():
    """Prüft ob Backup sinnvolle Größe hat."""
    today = datetime.now().strftime("%Y%m%d")
    pattern = f"backup_{today}_*.tar.gz"
    backups = list(BACKUP_DIR.glob(pattern))
    
    if not backups:
        return None, "No backup to check"
    
    latest = max(backups, key=os.path.getmtime)
    size_mb = os.path.getsize(latest) / (1024*1024)
    
    # Minimum reasonable size for workspace backup
    MIN_SIZE_MB = 1
    
    if size_mb < MIN_SIZE_MB:
        return False, f"⚠️  Backup zu klein: {size_mb:.1f}MB (erwartet >{MIN_SIZE_MB}MB)"
    
    return True, f"✅ Backup Size OK: {size_mb:.1f}MB"

def verify_backup_integrity():
    """Verifiziert Backup Integrity."""
    today = datetime.now().strftime("%Y%m%d")
    pattern = f"backup_{today}_*.tar.gz"
    backups = list(BACKUP_DIR.glob(pattern))
    
    if not backups:
        return None, "No backup to verify"
    
    latest = max(backups, key=os.path.getmtime)
    
    try:
        with tarfile.open(latest, 'r:gz') as tar:
            # Just test that it's a valid tar
            tar.getmembers()
        return True, f"✅ Backup Integrity OK"
    except Exception as e:
        return False, f"❌ Backup Corrupt: {e}"

def cleanup_old_backups():
    """Entfernt alte Backups."""
    count = 0
    for backup in BACKUP_DIR.glob("backup_*.tar.gz"):
        age_days = (datetime.now() - datetime.fromtimestamp(backup.stat().st_mtime)).days
        
        if age_days > RETENTION_DAYS:
            try:
                backup.unlink()
                count += 1
            except Exception as e:
                print(f"⚠️  Could not delete {backup.name}: {e}")
    
    return count

def generate_report():
    """Generiert Backup Report."""
    print("=" * 60)
    print("Sir HazeClaw Backup Verification")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    # Server Backup
    ok, msg = check_server_backup()
    print(f"SERVER: {msg}")
    
    # GitHub Backup
    ok, msg = check_github_backup()
    print(f"GITHUB: {msg}")
    print()
    
    # Size Check
    ok, msg = check_backup_size()
    if ok is not None:
        print(f"SIZE:   {msg}")
    
    # Integrity
    ok, msg = verify_backup_integrity()
    if ok is not None:
        print(f"CHECK:  {msg}")
    
    print()
    
    # Cleanup
    cleaned = cleanup_old_backups()
    if cleaned > 0:
        print(f"CLEANUP: ✅ {cleaned} old backups removed")
    else:
        print(f"CLEANUP: ℹ️  Keine alten Backups (Retention: {RETENTION_DAYS} Tage)")
    
    print()
    print("=" * 60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup Verification')
    parser.add_argument('--fix', action='store_true', help='Create backup if missing')
    args = parser.parse_args()
    
    if args.fix:
        # Create backup if missing
        ok, msg = check_server_backup()
        if not ok:
            print("Creating backup...")
            import subprocess
            result = subprocess.run([
                'tar', '-czf', 
                f'/home/clawbot/.openclaw/backups/backup_{datetime.now().strftime("%Y%m%d_%H%M")}.tar.gz',
                'workspace/'
            ], cwd='/home/clawbot/.openclaw', capture_output=True)
            
            if result.returncode == 0:
                print("✅ Backup created")
            else:
                print(f"❌ Backup failed: {result.stderr.decode()}")
    
    generate_report()

if __name__ == "__main__":
    main()