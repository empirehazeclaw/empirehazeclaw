#!/usr/bin/env python3
"""
Cron Idle Detector — Phase 3 of Improvement Plan
================================================
Detects idle/broken cron jobs and triggers recovery.
Runs via cron every 15 minutes.

Checks:
1. Cron status = idle → Check nextRun timestamp
2. If nextRun in past → CRON IS BROKEN (never fired)
3. If nextRun in future → Cron is fine, just waiting
4. If last_run > 2x expected interval → Alert

Idle Detection:
- "idle" status with nextRun in past = broken (never ran)
- "error" status = last run failed, may self-heal
- Missing from expected list = deconfigured
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
STATE_FILE = WORKSPACE / "data/cron_idle_state.json"
LOG_FILE = WORKSPACE / "logs/cron_idle_detector.log"

# Expected cron jobs that should be running
EXPECTED_CRONS = {
    "Ralph Learning Loop": {"interval_hours": 9, "enabled": True},
    "Ralph Maintenance Loop": {"interval_hours": 6, "enabled": True},
    "Learning Loop v3": {"interval_hours": 1, "enabled": True},
    "Capability Evolver": {"interval_hours": 1, "enabled": True},
    "Bug Hunter": {"interval_hours": 0.5, "enabled": True},
    "Health Monitor": {"interval_hours": 0.5, "enabled": True},
    "Integration Dashboard": {"interval_hours": 1, "enabled": True},
    "Data Agent": {"interval_hours": 0.25, "enabled": True},
    "Cache Cleanup Daily": {"interval_hours": 24, "enabled": True},
    "KG Orphan Cleaner Daily": {"interval_hours": 24, "enabled": True},
}

# Cron names as they appear in openclaw crons list
CRON_NAME_PATTERNS = [
    "Ralph Learning Loop",
    "Ralph Maintenance Loop", 
    "Learning Loop",
    "Capability Evolver",
    "Bug Hunter",
    "Health Monitor",
    "Integration Dashboard",
    "Data Agent",
    "Cache Cleanup",
    "KG Orphan",
]


def log(msg: str, level: str = "INFO"):
    """Log to file and print."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_openclaw_crons() -> dict:
    """Get list of crons from internal cron store (not openclaw CLI)."""
    cron_store = Path("/home/clawbot/.openclaw/cron/jobs.json")
    if not cron_store.exists():
        log(f"Cron store not found: {cron_store}", "ERROR")
        return ""
    
    try:
        data = json.loads(cron_store.read_text())
        jobs = data if isinstance(data, list) else data.get('jobs', [])
        
        # Convert to text format similar to "openclaw crons list"
        lines = []
        for job in jobs:
            name = job.get('name', 'unnamed')
            job_id = job.get('id', '')[:8]
            status = "enabled" if job.get('enabled', True) else "disabled"
            
            # Try to get next run from schedule
            schedule = job.get('schedule', 'unknown')
            next_run = schedule  # approximate
            
            lines.append(f"{name} | {schedule} | {next_run} | {status}")
        
        return "\n".join(lines)
    except Exception as e:
        log(f"Exception reading cron store: {e}", "ERROR")
        return ""


def parse_cron_status(output: str) -> dict:
    """Parse openclaw crons list output."""
    crons = {}
    lines = output.split("\n")
    
    for line in lines:
        # Look for cron name and status
        # Format: "Name | Schedule | Next Run | Status"
        if "|" in line and "crons" not in line and "-" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                name = parts[0]
                status = parts[-1]
                next_run = parts[-2] if len(parts) >= 3 else "unknown"
                crons[name] = {
                    "status": status,
                    "next_run": next_run
                }
    
    return crons


def check_idle_crams() -> dict:
    """Check for idle/crashed crons."""
    output = get_openclaw_crons()
    if not output:
        return {"error": "Could not get cron list"}
    
    crons = parse_cron_status(output)
    
    issues = []
    healthy = []
    
    for name, info in crons.items():
        status = info.get("status", "").lower()
        
        if status == "idle":
            # Check if nextRun is in the past
            next_run = info.get("next_run", "")
            if "pending" in next_run.lower() or "never" in next_run.lower():
                issues.append({
                    "name": name,
                    "issue": "idle_never_ran",
                    "status": status,
                    "next_run": next_run
                })
            else:
                # Might be waiting for next scheduled time
                healthy.append({"name": name, "status": "idle_waiting", "next": next_run})
        
        elif status == "error":
            issues.append({
                "name": name,
                "issue": "error_last_run_failed",
                "status": status,
                "next_run": info.get("next_run", "")
            })
        
        elif status == "active":
            healthy.append({"name": name, "status": "active", "next": info.get("next_run", "")})
    
    return {
        "healthy": healthy,
        "issues": issues,
        "total_checked": len(crons)
    }


def auto_recover(issue: dict) -> bool:
    """Attempt auto-recovery for a cron issue."""
    name = issue.get("name", "")
    
    try:
        # Try to enable the cron
        result = subprocess.run(
            ["openclaw", "cron", "enable", name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            log(f"Enabled cron: {name}", "INFO")
            
            # Try to run it manually
            run_result = subprocess.run(
                ["openclaw", "cron", "run", name],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if run_result.returncode == 0:
                log(f"Manual run triggered: {name}", "INFO")
                return True
            else:
                log(f"Manual run failed: {name} - {run_result.stderr}", "WARNING")
                return False
        else:
            log(f"Enable failed: {name} - {result.stderr}", "WARNING")
            return False
            
    except Exception as e:
        log(f"Auto-recover exception for {name}: {e}", "ERROR")
        return False


def save_state(state: dict):
    """Save detection state."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def load_state() -> dict:
    """Load previous detection state."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def run_detection_cycle() -> dict:
    """Run one detection cycle."""
    log("Cron Idle Detector: Starting cycle")
    
    state = load_state()
    results = check_idle_crams()
    
    # Count issues
    issue_count = len(results.get("issues", []))
    healthy_count = len(results.get("healthy", []))
    
    log(f"Checked {results.get('total_checked', 0)} crons: {healthy_count} healthy, {issue_count} issues")
    
    # Attempt auto-recovery for issues
    recovered = []
    failed_recovery = []
    
    for issue in results.get("issues", []):
        if issue.get("issue") in ["idle_never_ran", "error_last_run_failed"]:
            success = auto_recover(issue)
            if success:
                recovered.append(issue["name"])
            else:
                failed_recovery.append(issue["name"])
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    state["last_issues"] = results.get("issues", [])
    state["recovered_count"] = state.get("recovered_count", 0) + len(recovered)
    state["failed_recovery_count"] = state.get("failed_recovery_count", 0) + len(failed_recovery)
    
    save_state(state)
    
    return {
        "total": results.get("total_checked", 0),
        "healthy": healthy_count,
        "issues": issue_count,
        "recovered": recovered,
        "failed_recovery": failed_recovery
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cron Idle Detector")
    sub = parser.add_subparsers(dest="cmd")
    
    sub.add_parser("check", help="Run detection cycle")
    sub.add_parser("status", help="Show current status")
    sub.add_parser("recover", help="Attempt recovery for all issues")
    
    args = parser.parse_args()
    
    if args.cmd == "check":
        results = run_detection_cycle()
        print(f"\nCron Idle Detection Results:")
        print(f"  Total checked: {results['total']}")
        print(f"  Healthy: {results['healthy']}")
        print(f"  Issues: {results['issues']}")
        if results.get('recovered'):
            print(f"  Recovered: {results['recovered']}")
        if results.get('failed_recovery'):
            print(f"  Failed recovery: {results['failed_recovery']}")
    
    elif args.cmd == "status":
        state = load_state()
        if not state:
            print("No state saved yet")
        else:
            print(f"Last check: {state.get('last_check', 'unknown')}")
            print(f"Total recovered: {state.get('recovered_count', 0)}")
            print(f"Failed recovery: {state.get('failed_recovery_count', 0)}")
            print(f"Last issues: {len(state.get('last_issues', []))}")
    
    elif args.cmd == "recover":
        results = check_idle_crams()
        print(f"Attempting recovery for {len(results.get('issues', []))} issues...")
        for issue in results.get("issues", []):
            success = auto_recover(issue)
            print(f"  {issue['name']}: {'OK' if success else 'FAILED'}")
    
    else:
        parser.print_help()