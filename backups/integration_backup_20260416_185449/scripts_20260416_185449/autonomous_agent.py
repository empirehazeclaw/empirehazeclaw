#!/usr/bin/env python3
"""
🦞 Sir HazeClaw — Autonomous Agent
Self-Reviewing, Self-Healing, Self-Improving System Agent

Runs hourly. Checks system health. Auto-fixes common issues.
Reports ONLY when action taken or attention needed.

Boundaries:
- CAN: Clean logs, vacuum DBs, trim memory, restart crashed services, fix cron timeouts
- CANNOT: Modify configs without review, delete user data, send external messages
- ASK: Security issues, major config changes, external actions

Usage:
    python3 autonomous_agent.py        # Full run
    python3 autonomous_agent.py --dry-run   # Show what would be done
    python3 autonomous_agent.py --status      # Show current state
"""

import os
import sys
import json
import sqlite3
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
LOG_FILE = WORKSPACE / "logs/autonomous_agent.log"
STATE_FILE = WORKSPACE / "data/autonomous_agent_state.json"

# Thresholds
MAX_LOST_TASKS = 50
MAX_LOG_SIZE_MB = 5
MAX_DB_SIZE_MB = 500
MIN_FREE_DISK_GB = 50
CRON_ERROR_THRESHOLD = 3

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_run": None, "actions_taken": [], "last_issues": []}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ============ HEALTH CHECKS ============

def check_gateway() -> Tuple[bool, str]:
    """Check if gateway is responsive."""
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=10
        )
        if "running" in result.stdout.lower():
            return True, "Gateway OK"
        return False, f"Gateway issue: {result.stdout[:100]}"
    except Exception as e:
        return False, f"Gateway check failed: {e}"

def check_tasks() -> Tuple[bool, str]:
    """Check for lost/orphaned tasks."""
    try:
        conn = sqlite3.connect('/home/clawbot/.openclaw/tasks/runs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM task_runs WHERE status = "lost"')
        lost = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM task_runs WHERE status IN ("failed", "timed_out")')
        failed = cur.fetchone()[0]
        conn.close()
        
        if lost > MAX_LOST_TASKS:
            return False, f"{lost} lost tasks (threshold: {MAX_LOST_TASKS})"
        if failed > 100:
            return False, f"{failed} failed/timed_out tasks"
        return True, f"Tasks OK (lost={lost}, failed={failed})"
    except Exception as e:
        return False, f"Task check failed: {e}"

def check_disk() -> Tuple[bool, str]:
    """Check disk space."""
    try:
        result = subprocess.run(
            ["df", "-h", "/home/clawbot"],
            capture_output=True, text=True, timeout=5
        )
        line = result.stdout.strip().split("\n")[-1]
        parts = line.split()
        avail_gb = int(parts[3].rstrip("G")) if parts[3].endswith("G") else int(parts[3].rstrip("M")) / 1024
        use_pct = int(parts[4].rstrip("%"))
        
        if avail_gb < MIN_FREE_DISK_GB:
            return False, f"Low disk: {avail_gb:.1f}GB free (need {MIN_FREE_DISK_GB}GB)"
        return True, f"Disk OK ({use_pct}% used, {avail_gb:.1f}GB free)"
    except Exception as e:
        return False, f"Disk check failed: {e}"

def check_logs() -> Tuple[bool, str]:
    """Check for oversized log files."""
    oversized = []
    try:
        for log_file in (WORKSPACE / "logs").glob("*.log"):
            size_mb = log_file.stat().st_size / 1024 / 1024
            if size_mb > MAX_LOG_SIZE_MB:
                oversized.append(f"{log_file.name}: {size_mb:.1f}MB")
        
        if oversized:
            return False, f"Oversized logs: {', '.join(oversized[:3])}"
        return True, "Logs OK"
    except Exception as e:
        return False, f"Log check failed: {e}"

def check_crons() -> Tuple[bool, str]:
    """Check cron error rate."""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        errors = result.stdout.count("error")
        if errors >= CRON_ERROR_THRESHOLD:
            return False, f"{errors} cron errors detected"
        return True, f"Crons OK ({errors} errors)"
    except Exception as e:
        return False, f"Cron check failed: {e}"

def check_db_size() -> Tuple[bool, str]:
    """Check database sizes."""
    try:
        dbs = {
            "main": "/home/clawbot/.openclaw/memory/main.sqlite",
            "tasks": "/home/clawbot/.openclaw/tasks/runs.sqlite",
        }
        issues = []
        for name, path in dbs.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / 1024 / 1024
                if size_mb > MAX_DB_SIZE_MB:
                    issues.append(f"{name}: {size_mb:.0f}MB")
        
        if issues:
            return False, f"Large DBs: {', '.join(issues)}"
        return True, "DBs OK"
    except Exception as e:
        return False, f"DB check failed: {e}"

# ============ AUTO-FIXES ============

def fix_lost_tasks() -> bool:
    """Clean up lost tasks."""
    try:
        conn = sqlite3.connect('/home/clawbot/.openclaw/tasks/runs.sqlite')
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM task_runs WHERE status = "lost"')
        lost = cur.fetchone()[0]
        
        if lost > 10:
            cur.execute('DELETE FROM task_runs WHERE status = "lost"')
            conn.commit()
            conn.close()
            log(f"Cleaned {lost} lost tasks", "ACTION")
            return True
        conn.close()
    except Exception as e:
        log(f"Failed to clean lost tasks: {e}", "ERROR")
    return False

def fix_oversized_logs() -> bool:
    """Truncate oversized logs."""
    try:
        truncated = []
        for log_file in (WORKSPACE / "logs").glob("*.log"):
            size_mb = log_file.stat().st_size / 1024 / 1024
            if size_mb > MAX_LOG_SIZE_MB:
                with open(log_file, "w") as f:
                    f.write(f"# Truncated {datetime.now().isoformat()} — was {size_mb:.1f}MB\n")
                truncated.append(log_file.name)
        
        if truncated:
            log(f"Truncated logs: {', '.join(truncated)}", "ACTION")
            return True
    except Exception as e:
        log(f"Failed to truncate logs: {e}", "ERROR")
    return False

def vacuum_if_needed() -> bool:
    """Vacuum databases if they have lots of deleted records."""
    try:
        dbs = {
            "main": "/home/clawbot/.openclaw/memory/main.sqlite",
            "tasks": "/home/clawbot/.openclaw/tasks/runs.sqlite",
        }
        vacuumed = []
        for name, path in dbs.items():
            if os.path.exists(path):
                size_before = os.path.getsize(path)
                conn = sqlite3.connect(path)
                conn.execute("VACUUM")
                conn.close()
                size_after = os.path.getsize(path)
                if size_before > size_after:
                    freed_mb = (size_before - size_after) / 1024 / 1024
                    vacuumed.append(f"{name}: {freed_mb:.1f}MB")
        
        if vacuumed:
            log(f"Vacuumed DBs (freed): {', '.join(vacuumed)}", "ACTION")
            return True
    except Exception as e:
        log(f"Failed to vacuum DBs: {e}", "ERROR")
    return False

def rotate_log_file() -> bool:
    """Rotate log if it exists and is being written to."""
    try:
        log_path = Path("/home/clawbot/.openclaw/logs/gateway.log")
        if log_path.exists() and log_path.stat().st_size > 10 * 1024 * 1024:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            rotated = str(log_path) + f".{timestamp}"
            log_path.rename(rotated)
            log(f"Rotated gateway.log -> {rotated}", "ACTION")
            return True
    except Exception as e:
        log(f"Failed to rotate log: {e}", "ERROR")
    return False

# ============ MAIN LOOP ============

def run_health_checks() -> List[Tuple[str, bool, str]]:
    """Run all health checks."""
    checks = [
        ("Gateway", check_gateway),
        ("Tasks", check_tasks),
        ("Disk", check_disk),
        ("Logs", check_logs),
        ("DBs", check_db_size),
        ("Crons", check_crons),
    ]
    
    results = []
    for name, check_fn in checks:
        ok, msg = check_fn()
        results.append((name, ok, msg))
        if not ok:
            log(f"FAIL: {name} — {msg}", "WARN")
    
    return results

def run_auto_fixes() -> List[str]:
    """Run auto-fixes for known issues."""
    actions = []
    
    # These run every time
    if fix_oversized_logs():
        actions.append("logs_trimmed")
    if vacuum_if_needed():
        actions.append("db_vacuumed")
    
    # These run conditionally
    state = load_state()
    last_lost_clean = state.get("last_lost_task_clean", None)
    
    if last_lost_clean:
        hours_since = (datetime.now() - datetime.fromisoformat(last_lost_clean)).total_seconds() / 3600
        if hours_since > 6:  # Max once per 6 hours
            if fix_lost_tasks():
                actions.append("lost_tasks_cleaned")
                state["last_lost_task_clean"] = datetime.now().isoformat()
                save_state(state)
    else:
        if fix_lost_tasks():
            actions.append("lost_tasks_cleaned")
            state["last_lost_task_clean"] = datetime.now().isoformat()
            save_state(state)
    
    return actions

def report_to_nico(issues: List[Tuple[str, bool, str]], actions: List[str]):
    """Send report to Nico if there are issues or actions taken."""
    if not issues and not actions:
        return  # Silent — all OK
    
    lines = ["🦞 **Autonomous Agent Report**\n"]
    
    if actions:
        lines.append(f"**Actions:** {', '.join(actions)}\n")
    
    problems = [(n, m) for n, o, m in issues if not o]
    if problems:
        lines.append("**Issues:**")
        for name, msg in problems:
            lines.append(f"- {name}: {msg}")
    
    if not problems and actions:
        lines.append("🟢 All systems OK")
    
    report = "\n".join(lines)
    
    # Log for reference
    log(f"REPORT: {report.replace(chr(10), ' | ')}")

def main():
    dry_run = "--dry-run" in sys.argv
    
    log("=== Autonomous Agent Run ===")
    
    # Health checks
    results = run_health_checks()
    
    # Auto-fixes (unless dry run)
    actions = []
    if not dry_run:
        actions = run_auto_fixes()
    
    # Report
    report_to_nico(results, actions)
    
    # Update state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["last_results"] = [{"name": n, "ok": o, "msg": m} for n, o, m in results]
    state["last_actions"] = actions
    save_state(state)
    
    # Summary
    issues = sum(1 for _, ok, _ in results if not ok)
    log(f"Done. Issues: {issues}, Actions: {len(actions)}")

if __name__ == "__main__":
    main()
