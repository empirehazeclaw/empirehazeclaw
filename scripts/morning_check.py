#!/usr/bin/env python3
"""
Sir HazeClaw Morning Check
Quick morning status check.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")

def run_cmd(cmd, shell=False):
    """Run command without shell=True by default."""
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode

def main():
    print("🌅 **Morning Check**")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Git commits today
    stdout, _ = run_cmd("git log --oneline --since='today 00:00' | wc -l", shell=True)
    commits = int(stdout.strip()) if stdout.strip().isdigit() else 0
    print(f"📝 Commits Today: {commits}")
    
    # Git commits yesterday
    stdout, _ = run_cmd("git log --oneline --since='yesterday 00:00' --until='today 00:00' | wc -l", shell=True)
    yesterday = int(stdout.strip()) if stdout.strip().isdigit() else 0
    print(f"📝 Yesterday: {yesterday}")
    
    # Backup count today
    stdout, _ = run_cmd("ls /home/clawbot/.openclaw/backups/ | grep '$(date +%Y%m%d)' | wc -l", shell=True)
    backups = int(stdout.strip()) if stdout.strip().isdigit() else 0
    print(f"💾 Backups Today: {backups}")
    
    # Test coverage
    stdout, _ = run_cmd("grep -c \"'script': \" /home/clawbot/.openclaw/workspace/scripts/test_framework.py")
    tests = int(stdout.strip()) if stdout.strip().isdigit() else 0
    print(f"🧪 Tests: {tests}")
    
    # Score
    print()
    print("📊 **Quick Status:**")
    if commits > 0:
        ratio = backups / commits
        print(f"   Backup Ratio: {ratio:.2f} (target: <0.3)")
        if ratio < 0.3:
            print("   ✅ Ratio OK")
        else:
            print("   ⚠️  Ratio high - need more commits")
    else:
        print("   ⚠️  No commits yet today")
    
    if commits > 5:
        print("   ✅ Productivity OK")
    else:
        print("   ⚠️  Need more commits")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
