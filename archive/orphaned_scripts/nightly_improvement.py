#!/usr/bin/env python3
"""
Nightly Improvement - Combines Learning + Optimizer + Continuous Improvement
"""
import subprocess
import sys
from datetime import datetime

def run_script(name, script_path):
    """Run a script and report status"""
    print(f"📦 Running {name}...")
    try:
        result = subprocess.run(
            ["python3", script_path],
            cwd="/home/clawbot/.openclaw/workspace",
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {name}: Success")
            return True
        else:
            print(f"⚠️ {name}: {result.stderr[:100]}")
            return False
    except Exception as e:
        print(f"❌ {name}: {e}")
        return False

def main():
    print(f"=== Nightly Improvement ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
    
    results = {}
    
    # Run all three in sequence
    results['learnings'] = run_script("Auto Learnings", "scripts/auto_learnings.py")
    results['optimizer'] = run_script("Auto Optimizer", "scripts/auto_optimizer.py")
    results['improvement'] = run_script("Continuous Improvement", "scripts/continuous_improvement.py")
    
    # Summary
    success = sum(results.values())
    total = len(results)
    
    print(f"\n=== Summary: {success}/{total} successful ===")
    return 0 if success == total else 1

if __name__ == "__main__":
    sys.exit(main())
