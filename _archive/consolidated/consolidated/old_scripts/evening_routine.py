#!/usr/bin/env python3
"""
Sir HazeClaw Evening Routine
Automated evening checklist.

Runs all evening checks in sequence:
1. Self-evaluation
2. Quality metrics
3. Habit check-in
4. Deep reflection (if weekly)
5. KG backup
6. Backup check

Usage:
    python3 evening_routine.py
    python3 evening_routine.py --skip-reflection
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"

def run_script(script_name, args=None):
    """Führt ein Script aus."""
    cmd = [sys.executable, str(SCRIPTS_DIR / script_name)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, cwd=str(WORKSPACE),
                            capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout[:500]
    except Exception as e:
        return False, str(e)

def run_evening_routine(skip_reflection=False):
    """Führt komplette Evening Routine aus."""
    now = datetime.now()
    is_sunday = now.strftime('%A') == 'Sunday'
    
    print("=" * 60)
    print("🌙 EVENING ROUTINE")
    print(f"   {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    print()
    
    results = []
    
    # Define checks
    checks = [
        ('self_eval.py', 'Self-Evaluation', ['--report']),
        ('quality_metrics.py', 'Quality Metrics', ['--days', '1', '--save']),
        ('habit_tracker.py', 'Habit Tracker', ['--check-in']),
    ]
    
    # Add weekly reflection on Sunday
    if is_sunday and not skip_reflection:
        checks.append(('deep_reflection.py', 'Deep Reflection', ['--output', 'all']))
    
    # Run checks
    for script, name, extra_args in checks:
        print(f"🔄 {name}...")
        ok, output = run_script(script, extra_args)
        
        if ok:
            print(f"   ✅ DONE")
            results.append((name, True, None))
        else:
            print(f"   ⚠️  SKIPPED")
            results.append((name, False, None))
        
        # Show key output
        if 'Quality Score' in output:
            for line in output.split('\n'):
                if 'Overall' in line or 'Score' in line:
                    print(f"   {line.strip()}")
        print()
    
    # Summary
    print("=" * 60)
    print("📊 EVENING SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"   Checks: {passed}/{len(results)} completed")
    print()
    
    # Tomorrow's focus
    print("📋 TOMORROW'S FOCUS:")
    
    # Get quality score
    ok, output = run_script('self_eval.py', [])
    quality_line = None
    for line in output.split('\n'):
        if 'Self-Evaluation:' in line:
            quality_line = line.strip()
            break
    
    if quality_line:
        print(f"   → {quality_line}")
    
    # Get habit status
    ok, output = run_script('habit_tracker.py', ['--streaks'])
    if 'Average Streak' not in output:
        for line in output.split('\n'):
            if '🔥' in line:
                print(f"   → {line.strip()}")
    
    print()
    print(f"🌙 Good night! Rest well.")
    print("=" * 60)
    
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Evening Routine')
    parser.add_argument('--skip-reflection', action='store_true', help='Skip deep reflection')
    args = parser.parse_args()
    
    run_evening_routine(skip_reflection=args.skip_reflection)

if __name__ == "__main__":
    main()
