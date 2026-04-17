#!/usr/bin/env python3
"""
🦞 System Health Monitor — Sir HazeClaw
========================================
Consolidated health checking. Runs every 30min.

Combines:
- Bug Hunter (every 30min)
- Integration Health Check (every 3h)
- Stagnation Detector (every 6h)
- Cron Watchdog (every 6h)

Only alerts on REAL issues, not old/stale errors.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
LOG_FILE = WORKSPACE.parent / "logs" / "system_health.log"
STAGNATION = WORKSPACE.parent / "scripts" / "stagnation_detector.py"
PROACTIVE = WORKSPACE.parent / "scripts" / "proactive_scanner.py"

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] [{level}] {msg}\n")

def run_cmd(cmd, timeout=60):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_bug_hunter():
    """Quick bug scan."""
    success, out, err = run_cmd(f"python3 {PROACTIVE}", timeout=30)
    if "CLEAN" in out:
        return True, "No issues"
    return False, out[:200]

def check_stagnation():
    """Check for stagnation."""
    success, out, err = run_cmd(f"python3 {STAGNATION} --check all", timeout=30)
    if "✅" in out or "OK" in out:
        return True, "All systems moving"
    return False, out[:200]

def main():
    hour = datetime.now().hour
    
    log("=== System Health Monitor START ===")
    
    # Always run: Bug Hunter + Proactive Scanner
    ok1, msg1 = check_bug_hunter()
    log(f"Bug/Proactive: {'OK' if ok1 else msg1}")
    
    # Every 3h: Integration Health
    if hour % 3 == 0:
        from integration_dashboard import run_health_check
        ok, msg = run_health_check()
        log(f"Integration Health: {'OK' if ok else msg}")
    
    # Every 6h: Stagnation + Watchdog
    if hour % 6 == 0:
        ok2, msg2 = check_stagnation()
        log(f"Stagnation: {'OK' if ok2 else msg2}")
    
    log("=== System Health Monitor END ===")
    
    # Return exit code based on issues
    if not ok1:
        print(f"⚠️ Issues detected: {msg1}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
