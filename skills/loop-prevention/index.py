#!/usr/bin/env python3
"""
Loop Prevention Skill
Erkennt und verhindert repetitive Loops ohne echten Fortschritt.

Usage:
    python3 skills/loop-prevention/index.js
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

def check_progress():
    """Prüft ob echter Fortschritt gemacht wurde."""
    today = datetime.now().strftime("%Y%m%d")
    
    # Backups heute
    backups = sorted(glob.glob(f"{BACKUP_DIR}/backup_{today}_*.tar.gz"))
    
    # Commits heute
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='today 00:00'"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True
    )
    commits = [c for c in result.stdout.strip().split('\n') if c]
    
    # Commits letzte Stunde
    result2 = subprocess.run(
        ["git", "log", "--oneline", "--since='1 hour ago'"],
        cwd=WORKSPACE_DIR,
        capture_output=True,
        text=True
    )
    recent_commits = [c for c in result2.stdout.strip().split('\n') if c]
    
    return {
        'backups': len(backups),
        'commits': len(commits),
        'recent_commits': len(recent_commits)
    }

def detect_loop():
    """Erkennt ob wir in einem Loop sind."""
    progress = check_progress()
    
    issues = []
    
    # Loop 1: Viele Backups, wenige Commits
    if progress['backups'] > 8 and progress['commits'] < 5:
        if progress['recent_commits'] < 2:
            issues.append({
                'type': 'LOOP',
                'message': f"Loop erkannt: {progress['backups']} Backups, {progress['commits']} Commits, {progress['recent_commits']} in letzter Stunde",
                'action': 'STOPPEN oder Master fragen'
            })
    
    # Loop 2: Keine echte Arbeit
    if progress['backups'] > 12 and progress['commits'] < 3:
        issues.append({
            'type': 'PARANOIA',
            'message': f"Backup-Paranoia: {progress['backups']} Backups, nur {progress['commits']} Commits",
            'action': 'Echte Arbeit machen, nicht nur Backups'
        })
    
    return issues

def main():
    print(f"🔍 Loop Prevention Check — {datetime.now().strftime('%H:%M:%S UTC')}")
    print("=" * 60)
    
    issues = detect_loop()
    
    if issues:
        print("\n⚠️  LOOP ERKANNT:\n")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['message']}")
            print(f"  → {issue['action']}\n")
        print("=" * 60)
        return 1
    else:
        progress = check_progress()
        print(f"\n✅ Kein Loop erkannt")
        print(f"   Backups: {progress['backups']}")
        print(f"   Commits: {progress['commits']}")
        print(f"   Letzte Stunde: {progress['recent_commits']}")
        print("\n" + "=" * 60)
        return 0

if __name__ == "__main__":
    sys.exit(main())