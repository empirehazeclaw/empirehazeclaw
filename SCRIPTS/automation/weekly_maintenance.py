#!/usr/bin/env python3
"""
Weekly System Maintenance — Sir HazeClaw
========================================
Consolidated Sunday maintenance tasks.

Replaces (all Sunday 03-04h):
- Cron Optimizer (03h)
- Smart Evolver Run (03h)  
- Nightly Maintenance (03h)
- Daily Auto Backup (04h daily → weekly)
- Memory Cleanup Weekly (04h)
- Weekly System Backup (04h)
- SQLite Vacuum Weekly (04h)
- Skills Fitness Tracker (04h)

Schedule: Sunday 04:00 UTC
"""

import subprocess
import sys
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/workspace/logs/weekly_maintenance.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run_step(name, cmd, timeout=300):
    log(f"Running: {name}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            log(f"  ✓ {name}")
            return True, result.stdout[:300]
        else:
            log(f"  ✗ {name}: {result.stderr[:200]}")
            return False, result.stderr[:200]
    except Exception as e:
        log(f"  ✗ {name}: {e}")
        return False, str(e)[:200]

def main():
    log("="*60)
    log("WEEKLY MAINTENANCE START")
    
    results = {}
    
    # 1. Nightly Maintenance (Session Cleanup + Context Manager)
    log("--- Nightly Maintenance ---")
    run_step("Session Cleanup", "python3 /home/clawbot/.openclaw/workspace/scripts/session_cleanup.py")
    run_step("Session Context Manager", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/session_context_manager.py")
    
    # 2. Smart Evolver
    ok, out = run_step("Smart Evolver", "bash /home/clawbot/.openclaw/workspace/scripts/run_smart_evolver.sh", timeout=300)
    results["evolver"] = "OK" if ok else "FAILED"
    
    # 3. Auto Backup
    ok, out = run_step("Auto Backup", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/tools/auto_backup.py", timeout=300)
    results["backup"] = "OK" if ok else "FAILED"
    
    # 4. SQLite Vacuum
    ok, out = run_step("SQLite Vacuum", "bash /home/clawbot/.openclaw/workspace/SCRIPTS/tools/sqlite_vacuum.sh", timeout=300)
    results["vacuum"] = "OK" if ok else "FAILED"
    
    # 5. Cron Optimizer
    ok, out = run_step("Cron Optimizer", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/cron_optimizer.py", timeout=180)
    results["cron_opt"] = "OK" if ok else "FAILED"
    
    # 6. Skills Fitness
    ok, out = run_step("Skills Fitness", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/skills_fitness_tracker.py", timeout=120)
    results["skills"] = "OK" if ok else "FAILED"
    
    log("="*60)
    log(f"WEEKLY MAINTENANCE END: {results}")
    
    summary = "🛠️ Weekly Maintenance\n"
    for k, v in results.items():
        summary += f"  {k}: {v}\n"
    print(summary)

if __name__ == "__main__":
    main()
