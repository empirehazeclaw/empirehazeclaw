#!/usr/bin/env python3
"""
Cron Health Monitor
Checks all OpenClaw agent crons for health and alerts on failures.

Usage: python3 cron_health_monitor.py [--check-only]
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = Path("/home/clawbot/.openclaw/logs/cron_health_monitor.log")
ALERT_LOG = Path("/home/clawbot/.openclaw/logs/cron_alerts.log")

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_openclaw_crons():
    """Check OpenClaw internal crons via openclaw command."""
    try:
        result = subprocess.run(
            ["openclaw", "crons", "list", "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        log(f"Cannot list crons: {e}", "ERROR")
    return None

def check_cron_log_health(cron_name, log_path, max_age_hours=25):
    """Check if a cron log shows recent successful runs."""
    if not log_path.exists():
        return False, f"Log missing: {log_path}"
    
    try:
        with open(log_path) as f:
            lines = f.readlines()
        
        if not lines:
            return False, "Empty log"
        
        last_line = lines[-1].strip()
        # Parse timestamp from log line like [2026-04-20 06:22:07 UTC]
        try:
            if "] [" in last_line:
                ts_str = last_line.split("] [")[0].replace("[", "")
                last_run = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S UTC")
                age = datetime.now() - last_run
                if age.total_seconds() > max_age_hours * 3600:
                    return False, f"Stale: {age.total_seconds()/3600:.1f}h old"
                return True, f"OK: {age.total_seconds()/60:.0f}m ago"
        except:
            pass
        
        return True, "Recent activity"
    except Exception as e:
        return False, f"Error: {e}"

def check_user_crons():
    """Check user crontab entries."""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split("\n") 
                    if l and not l.startswith("#") and not l.startswith("SHELL") 
                    and not l.startswith("PATH") and l.strip()]
            return lines
    except:
        pass
    return []

def main():
    check_only = "--check-only" in sys.argv
    
    log("=== Cron Health Monitor ===")
    
    issues = []
    
    # 1. Check OpenClaw crons
    log("Checking OpenClaw agent crons...")
    crons = check_openclaw_crons()
    
    if crons:
        error_crons = [c for c in crons if c.get("status") == "error"]
        if error_crons:
            for c in error_crons:
                issues.append(f"OPENCLAW ERROR: {c.get('name', c.get('id', 'unknown'))} - {c.get('error', 'unknown error')}")
                log(f"  ❌ {c.get('name', 'unknown')}: {c.get('error', 'unknown')}", "ERROR")
        else:
            log(f"  ✅ All {len(crons)} OpenClaw crons OK")
    
    # 2. Check user crontab
    log("Checking user crontab...")
    user_crons = check_user_crons()
    if user_crons:
        log(f"  User crontab: {len(user_crons)} entries")
        for entry in user_crons:
            # Simple format check
            if "sqlite_vacuum" in entry or "session_cleanup" in entry or "semantic_search" in entry:
                issues.append(f"USER CRON BROKEN: {entry}")
                log(f"  ❌ Likely broken: {entry[:60]}...", "WARNING")
    else:
        log("  ✅ No user crontab entries (good - using OpenClaw only)")
    
    # 3. Check critical log files
    critical_logs = [
        ("health_agent", Path("/home/clawbot/.openclaw/logs/health_agent.log")),
        ("data_agent", Path("/home/clawbot/.openclaw/logs/data_agent.log")),
        ("research_agent", Path("/home/clawbot/.openclaw/logs/research_agent.log")),
        ("semantic_search", Path("/home/clawbot/.openclaw/logs/semantic_search.log")),
    ]
    
    log("Checking critical cron logs...")
    for name, path in critical_logs:
        healthy, msg = check_cron_log_health(name, path)
        status = "✅" if healthy else "❌"
        log(f"  {status} {name}: {msg}")
        if not healthy and "Log missing" not in msg and "Empty" not in msg:
            issues.append(f"LOG STALE: {name} - {msg}")
    
    # 4. Summary
    log(f"=== Health Check Complete ===")
    if issues:
        log(f"ISSUES FOUND: {len(issues)}", "WARNING")
        for issue in issues:
            log(f"  - {issue}", "WARNING")
        
        # Write alerts
        with open(ALERT_LOG, "a") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            for issue in issues:
                f.write(f"[{ts}] {issue}\n")
        
        if not check_only:
            print(f"\n⚠️ {len(issues)} issues found. Check {ALERT_LOG} for details.")
    else:
        log("All systems healthy ✅")
        print("\n✅ Cron health: All clear")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
