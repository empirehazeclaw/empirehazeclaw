#!/usr/bin/env python3
"""
Backup Advisor Skill
Berät wann ein Backup sinnvoll ist und erkennt Backup-Paranoia.

Usage:
    python3 skills/backup-advisor/index.py should-backup
    python3 skills/backup-advisor/index.py status
    python3 skills/backup-advisor/index.py recommend
"""

import os
import sys
import glob
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Config
BACKUP_DIR = Path("/home/clawbot/.openclaw/backups")
WORKSPACE_DIR = Path("/home/clawbot/.openclaw/workspace")

def get_backup_stats():
    """Holt Backup-Statistiken."""
    today = datetime.now().strftime("%Y%m%d")
    backups = sorted(glob.glob(f"{BACKUP_DIR}/backup_{today}_*.tar.gz"))
    
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    return {
        'backups_today': len(backups),
        'commits_today': len(commits),
        'latest_backup': max(backups, key=os.path.getmtime) if backups else None,
        'latest_size': os.path.getsize(max(backups, key=os.path.getmtime)) / (1024*1024) if backups else 0
    }

def should_backup():
    """Entscheidet ob ein Backup sinnvoll ist."""
    stats = get_backup_stats()
    
    print(f"🔍 Backup Advisor — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    print(f"\nBackup-Statistiken:")
    print(f"  Backups heute: {stats['backups_today']}")
    print(f"  Commits heute: {stats['commits_today']}")
    print()
    
    # Entscheidungs-Logik
    if stats['backups_today'] == 0:
        print("📋 Empfehlung: ✅ Backup erstellen")
        print("   Begründung: Kein Backup heute vorhanden")
        return True
    
    if stats['commits_today'] > stats['backups_today']:
        print("📋 Empfehlung: ✅ Backup erstellen")
        print(f"   Begründung: {stats['commits_today']} Commits, nur {stats['backups_today']} Backups")
        return True
    
    if stats['backups_today'] >= 10:
        print("📋 Empfehlung: ❌ NICHT backupen")
        print("   Begründung: Zu viele Backups heute ({stats['backups_today']}) - Backup-Paranoia?")
        print("   Tipp: Commit und warte bis morgen")
        return False
    
    if stats['backups_today'] >= 5 and stats['commits_today'] <= 3:
        print("📋 Empfehlung: ❌ NICHT backupen")
        print(f"   Begründung: {stats['backups_today']} Backups, aber nur {stats['commits_today']} Commits")
        print("   Tipp: Mehr committen statt backuppen")
        return False
    
    if stats['commits_today'] > stats['backups_today'] * 2:
        print("📋 Empfehlung: ✅ Backup erstellen")
        print(f"   Begründung: {stats['commits_today']} Commits, {stats['backups_today']} Backups")
        return True
    
    # Default
    print("📋 Empfehlung: ℹ️  Backup optional")
    print("   Begründung: норм balance")
    return None

def show_status():
    """Zeigt Backup-Status."""
    stats = get_backup_stats()
    
    print(f"💾 Backup Status — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    print(f"\n  Backups heute: {stats['backups_today']}")
    print(f"  Commits heute: {stats['commits_today']}")
    
    if stats['latest_backup']:
        print(f"  Letztes Backup: {stats['latest_backup'].split('/')[-1]}")
        print(f"  Größe: {stats['latest_size']:.1f} MB")
    
    # Paranoia Check
    if stats['backups_today'] > 10:
        print(f"\n⚠️  WARNING: {stats['backups_today']} Backups heute - Backup-Paranoia?")
    elif stats['backups_today'] > 5 and stats['commits_today'] < 5:
        print(f"\n⚠️  WARNING: Mehr Backups ({stats['backups_today']}) als Commits ({stats['commits_today']})")
    else:
        print(f"\n✅ Backup-Verhältnis OK")
    
    print("=" * 60)

def recommend():
    """Gibt Empfehlungen für bessere Backup-Hygiene."""
    stats = get_backup_stats()
    
    print(f"💡 Backup Empfehlungen — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    if stats['backups_today'] > 10:
        print("\n🔴 Backup-Paranoia erkannt!")
        print("   Regeln für die Zukunft:")
        print("   - Backup NACH wichtigen Änderungen")
        print("   - Max 3-5 Backups pro Tag")
        print("   - Backup wenn Commits > Backups")
    
    if stats['commits_today'] > 20 and stats['backups_today'] < 3:
        print("\n🟡 Viele Commits, wenig Backups")
        print("   - Backup könnte sinnvoll sein")
    
    if stats['backups_today'] < 2:
        print("\n🟢 Wenig Backups heute")
        print("   - Backup nach nächsten Commits empfohlen")
    
    print("\n📋 Backup-Regel (2026-04-10):")
    print("   Backup WENN: Commits > Backups * 2")
    print("   Backup NICHT: Backups > Commits * 3")
    
    print("=" * 60)

def main():
    if len(sys.argv) < 2:
        print("Usage: backup-advisor.py [should-backup|status|recommend]")
        return 1
    
    cmd = sys.argv[1]
    
    if cmd == "should-backup":
        return 0 if should_backup() else 0  # 0 = OK für beide
    elif cmd == "status":
        show_status()
        return 0
    elif cmd == "recommend":
        recommend()
        return 0
    else:
        print(f"Unknown command: {cmd}")
        return 1

if __name__ == "__main__":
    sys.exit(main())