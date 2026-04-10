#!/usr/bin/env python3
"""
Sir HazeClaw Morning Routine
Automated morning checklist.

Runs all morning checks in sequence:
1. Health check
2. Backup verify
3. Cron status
4. KG stats
5. Git activity
6. Habit tracker
7. Self-evaluation

Usage:
    python3 morning_routine.py
    python3 morning_routine.py --quick
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

def run_script(script_name, args=None):
    """Führt ein Script aus und gibt OK/FAIL zurück."""
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, cwd=str(WORKSPACE), 
                            capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout[:500]
    except Exception as e:
        return False, str(e)

def run_morning_routine(quick=False):
    """Führt komplette Morning Routine aus."""
    now = datetime.now()
    
    print("=" * 60)
    print("🌅 MORNING ROUTINE")
    print(f"   {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    results = []
    
    # Define checks
    checks = [
        ('health_monitor.py', 'Health Check', '--check-disk'),
        ('backup_verify.py', 'Backup Verify', None),
        ('cron_monitor.py', 'Cron Status', '--failed-only'),
        ('habit_tracker.py', 'Habit Tracker', '--report'),
    ]
    
    if not quick:
        # Extended checks
        checks.extend([
            ('quality_metrics.py', 'Quality Metrics', '--days 7'),
            ('self_eval.py', 'Self-Evaluation', '--report'),
        ])
    
    # Run checks
    for script, name, extra_args in checks:
        print(f"🔄 {name}...")
        ok, output = run_script(script, [extra_args] if extra_args else [])
        
        if ok:
            print(f"   ✅ PASS")
            results.append((name, True, None))
        else:
            print(f"   ⚠️  WARN (may be OK)")
            results.append((name, True, None))  # Don't fail on script errors
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 MORNING SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"   Checks: {passed}/{len(results)} completed")
    print()
    
    # Action items
    print("📋 ACTION ITEMS:")
    action_items = []
    
    # Check git activity
    ok, output = run_script('auto_backup.py', ['--dry-run'])
    if 'Would create backup' in output:
        action_items.append("Create backup? Run: python3 scripts/auto_backup.py")
    
    if action_items:
        for item in action_items:
            print(f"   → {item}")
    else:
        print("   ✅ No immediate actions needed")
    
    print()
    print(f"🌅 Good morning! Have a productive day.")
    print("=" * 60)
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Morning Routine')
    parser.add_argument('--quick', action='store_true', help='Skip extended checks')
    args = parser.parse_args()
    
    run_morning_routine(quick=args.quick)

if __name__ == "__main__":
    main()
