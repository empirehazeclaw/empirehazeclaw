#!/usr/bin/env python3
"""
Ralph Maintenance Loop
=====================
Ralph Loop Pattern für System Maintenance:
- Iteriert bis alle Maintenance Tasks complete
- Completion Promise bei <promise>COMPLETE</promise>
- Learnings in ralph_learnings.md

Usage:
    python3 ralph_maintenance_loop.py              # Full Ralph Loop
    python3 ralph_maintenance_loop.py --status    # Show status
    python3 ralph_maintenance_loop.py --check     # Check completion
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RALPH_LEARNINGS = WORKSPACE / "ceo/memory/ralph_learnings.md"
RALPH_STATE = WORKSPACE / "data/ralph_maintenance_state.json"

# Ralph Loop constants
RALPH_MARKER = "<promise>COMPLETE</promise>"
MAX_ITERATIONS = 10  # Safety limit
STABLE_RUNS = 2  # 2 stable runs = complete

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[Ralph Maint] [{ts}] {msg}", file=sys.stderr)

def load_state():
    path = WORKSPACE / "data/ralph_maintenance_state.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "iterations": 0,
        "checks_passed": 0,
        "stable_runs": 0,
        "completed": False,
        "issues": []
    }

def save_state(state):
    RALPH_STATE.write_text(json.dumps(state, indent=2))

def append_learning(category, finding):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- [{timestamp}] [maintenance:{category}] {finding}"
    
    if not RALPH_LEARNINGS.exists():
        content = "# Ralph Loop Learnings\n\n"
    else:
        content = RALPH_LEARNINGS.read_text()
    
    content += entry + "\n"
    RALPH_LEARNINGS.write_text(content)
    log(f"Learning: {finding[:80]}")

def run_health_check():
    """Run health monitor check."""
    log("Running Health Check...")
    result = subprocess.run(
        ["python3", str(WORKSPACE / "monitoring/health_monitor.py"), "--check-gateway", "--check-disk", "--check-memory"],
        capture_output=True, text=True, timeout=120
    )
    return result.returncode == 0, result.stdout + result.stderr

def run_stagnation_check():
    """Run stagnation detector."""
    log("Running Stagnation Check...")
    result = subprocess.run(
        ["python3", str(WORKSPACE / "SCRIPTS/automation/stagnation_detector.py"), "--check", "all"],
        capture_output=True, text=True, timeout=60
    )
    return result.returncode == 0, result.stdout + result.stderr

def run_data_agent():
    """Run data agent full cycle."""
    log("Running Data Agent...")
    result = subprocess.run(
        ["python3", str(WORKSPACE / "SCRIPTS/automation/data_agent.py"), "--full"],
        capture_output=True, text=True, timeout=180
    )
    return result.returncode == 0, result.stdout + result.stderr

def parse_issues(output):
    """Parse issues from output."""
    issues = []
    
    # Look for CRITICAL/ERROR patterns
    if "CRITICAL" in output or "ERROR" in output:
        lines = output.split('\n')
        for line in lines:
            if "CRITICAL" in line or ("ERROR" in line and "error_rate" not in line.lower()):
                issues.append(line.strip()[:100])
    
    # Look for warning counts
    warn_match = re.search(r"(\d+)\s+(warning|warn)", output.lower())
    if warn_match:
        count = int(warn_match.group(1))
        if count > 0:
            issues.append(f"{count} warnings detected")
    
    return issues

def run_maintenance_cycle():
    """Run one maintenance cycle."""
    state = load_state()
    
    # Reset if completed (new maintenance window)
    if state["completed"]:
        log("Resetting state for new maintenance window")
        state = {
            "iterations": 0,
            "checks_passed": 0,
            "stable_runs": 0,
            "completed": False,
            "issues": []
        }
    
    if state["iterations"] >= MAX_ITERATIONS:
        log(f"MAX ITERATIONS ({MAX_ITERATIONS}) reached!")
        append_learning("safety", f"Max iterations reached, {len(state['issues'])} issues pending")
        return False, state["iterations"]
    
    state["iterations"] += 1
    issues_this_run = []
    
    # Run checks
    checks = [
        ("health", run_health_check),
        ("stagnation", run_stagnation_check),
        ("data_agent", run_data_agent),
    ]
    
    checks_passed = 0
    for name, check_fn in checks:
        success, output = check_fn()
        
        if success:
            checks_passed += 1
            log(f"  ✓ {name} OK")
        else:
            log(f"  ✗ {name} issues")
            issues = parse_issues(output)
            for issue in issues[:3]:
                issues_this_run.append(f"{name}: {issue}")
                append_learning("issue", issue)
    
    state["checks_passed"] = checks_passed
    
    if checks_passed == len(checks):
        state["stable_runs"] += 1
        log(f"Stable run {state['stable_runs']}/{STABLE_RUNS}")
        
        if state["stable_runs"] >= STABLE_RUNS:
            state["completed"] = True
            save_state(state)
            append_learning("success", f"Maintenance complete after {state['iterations']} iterations")
            print(f"\n{RALPH_MARKER}\n")
            return True, state["iterations"]
    else:
        state["stable_runs"] = 0
        log(f"Only {checks_passed}/{len(checks)} checks passed, reset stable_runs")
    
    state["issues"] = list(set(state["issues"] + issues_this_run))[-10:]  # Keep last 10 unique
    save_state(state)
    
    return False, state["iterations"]

def show_status():
    state = load_state()
    print(f"=== Ralph Maintenance Status ===")
    print(f"Iterations: {state['iterations']}/{MAX_ITERATIONS}")
    print(f"Checks Passed: {state['checks_passed']}/3")
    print(f"Stable Runs: {state['stable_runs']}/{STABLE_RUNS}")
    print(f"Completed: {state['completed']}")
    
    if state['issues']:
        print(f"\nIssues ({len(state['issues'])}):")
        for issue in state['issues'][:5]:
            print(f"  - {issue}")

def check_completion():
    """Check if maintenance is complete."""
    state = load_state()
    if state["completed"]:
        print(RALPH_MARKER)
        print("Status: COMPLETE")
        return True
    print("Status: NOT_COMPLETE")
    return False

def main():
    if "--status" in sys.argv:
        show_status()
        return
    
    if "--check" in sys.argv:
        check_completion()
        return
    
    # Full Ralph Loop
    log("Starting Ralph Maintenance Loop")
    state = load_state()
    
    success, iterations = run_maintenance_cycle()
    
    if success:
        print(f"\n{RALPH_MARKER}\n")
        print(f"Maintenance COMPLETE after {iterations} iterations!")
        sys.exit(0)
    else:
        print(f"Not yet complete after {iterations} iterations.")
        sys.exit(1)

if __name__ == "__main__":
    main()
