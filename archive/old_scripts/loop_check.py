#!/usr/bin/env python3
"""
Sir HazeClaw Loop Check
Checks for bad loops and reports status.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def check_backup_ratio():
    """Check backup ratio."""
    backup_dir = WORKSPACE.parent / "backups"
    today = datetime.now().strftime("%Y%m%d")
    
    today_backups = list(backup_dir.glob(f"backup_{today}_*.tar.gz"))
    
    result = subprocess.run(
        ["git", "log", "--oneline", f"--since='{today} 00:00:00'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    commits = len([c for c in result.stdout.strip().split('\n') if c])
    
    if commits == 0:
        return "warning", "No commits today"
    
    ratio = len(today_backups) / commits
    
    if ratio > 0.5:
        return "critical", f"Backup ratio {ratio:.2f} - TOO HIGH"
    elif ratio > 0.3:
        return "warning", f"Backup ratio {ratio:.2f} - OK but high"
    else:
        return "ok", f"Backup ratio {ratio:.2f} - OK"

def check_commit_frequency():
    """Check commits in last hour."""
    result = subprocess.run(
        ["git", "log", "--oneline", "--since='1 hour ago'"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    commits = len([c for c in result.stdout.strip().split('\n') if c])
    
    if commits < 1:
        return "warning", "No commits in last hour"
    elif commits < 5:
        return "ok", f"{commits} commits in last hour - LOW"
    else:
        return "ok", f"{commits} commits in last hour - GOOD"

def check_nothing_to_commit():
    """Check for repeated 'nothing to commit'."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(WORKSPACE),
        capture_output=True,
        text=True
    )
    changes = result.stdout.strip()
    
    if not changes:
        return "warning", "Nothing to commit - workspace clean"
    else:
        return "ok", "Changes present"

def main():
    print("🔄 **Loop Check**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    checks = [
        ("Backup Ratio", check_backup_ratio()),
        ("Commit Frequency", check_commit_frequency()),
        ("Clean Workspace", check_nothing_to_commit()),
    ]
    
    warnings = 0
    criticals = 0
    
    for name, (status, msg) in checks:
        if status == "critical":
            print(f"🔴 {name}: {msg}")
            criticals += 1
        elif status == "warning":
            print(f"🟡 {name}: {msg}")
            warnings += 1
        else:
            print(f"✅ {name}: {msg}")
    
    print()
    if criticals > 0:
        print("⚠️  LOOP DETECTED - Action needed!")
        return 1
    elif warnings > 0:
        print("🟡 Minor warnings - monitor")
        return 0
    else:
        print("✅ No loops detected")
        return 0

if __name__ == "__main__":
    sys.exit(main())
