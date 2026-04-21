#!/usr/bin/env python3
"""
Cron Health Check — Testet alle Cron-Scripts direkt (nicht via cron).
Läuft alle payload commands sequentiell und reportet Resultate.

Usage:
    python3 cron_health_check.py              # Full check
    python3 cron_health_check.py --fast      # Nur quick-fails (30s timeout)
    python3 cron_health_check.py --cron "Goal Alerts Daily"  # Einzelner Cron
"""

import json
import sys
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CRON_JOBS = Path("/home/clawbot/.openclaw/cron/jobs.json")

# Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def load_crons():
    with open(CRON_JOBS) as f:
        data = json.load(f)
    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    return jobs

def extract_command(message: str) -> tuple[str, str]:
    """Extrahiert script path + args aus cron message."""
    # Pattern: python3 /path/to/script.py --arg
    match = re.search(r"(python3|python|bash|sh)\s+(.+?)(?:\n|$)", message)
    if match:
        return match.group(1), match.group(2).strip()
    
    # Fallback: shell command
    lines = message.strip().split("\n")
    return "python3", lines[0].strip()

def run_script(cmd_type: str, cmd: str, timeout: int = 60) -> tuple[bool, str, float]:
    """Führt ein Script aus, gibt (success, output, duration_ms) zurück."""
    start = datetime.now()
    try:
        if cmd_type == "bash":
            shell_cmd = f"bash {cmd}"
            result = subprocess.run(
                shell_cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
        else:
            result = subprocess.run(
                [cmd_type] + cmd.split(), capture_output=True, text=True, timeout=timeout
            )
        duration = (datetime.now() - start).total_seconds() * 1000
        success = result.returncode == 0
        output = result.stdout[:500] if result.stdout else ""
        if result.stderr:
            output += f"\nSTDERR: {result.stderr[:200]}"
        return success, output, duration
    except subprocess.TimeoutExpired:
        duration = (datetime.now() - start).total_seconds() * 1000
        return False, f"TIMEOUT after {timeout}s", duration
    except Exception as e:
        duration = (datetime.now() - start).total_seconds() * 1000
        return False, f"ERROR: {e}", duration

def check_script_path(cmd_type: str, cmd: str) -> tuple[bool, str]:
    """Check ob Script existiert."""
    parts = cmd.split()
    script_path = parts[0]
    
    # Resolve relative paths
    if not script_path.startswith("/"):
        script_path = WORKSPACE / script_path
    
    if Path(script_path).exists():
        return True, "exists"
    
    # Try common variations
    for variant in [
        script_path,
        str(WORKSPACE / script_path),
    ]:
        if Path(variant).exists():
            return True, f"found at {variant}"
    
    return False, f"NOT FOUND: {script_path}"

def test_cron(cron, fast=False):
    """Testet einen Cron-Job."""
    name = cron.get("name", "unknown")
    message = cron.get("payload", {}).get("message", "")
    enabled = cron.get("enabled", True)
    
    if not enabled:
        return {"name": name, "status": "SKIP", "reason": "disabled", "duration": 0}
    
    if not message.strip():
        return {"name": name, "status": "SKIP", "reason": "empty payload", "duration": 0}
    
    # Extract command
    cmd_type, cmd = extract_command(message)
    if not cmd:
        return {"name": name, "status": "SKIP", "reason": "no command found", "duration": 0}
    
    # Check path
    path_ok, path_msg = check_script_path(cmd_type, cmd)
    if not path_ok:
        return {"name": name, "status": "PATH_ERROR", "reason": path_msg, "duration": 0, "cmd": f"{cmd_type} {cmd}"}
    
    # Run
    timeout = 60 if fast else 120
    success, output, duration = run_script(cmd_type, cmd, timeout=timeout)
    
    return {
        "name": name,
        "status": "OK" if success else "FAIL",
        "reason": output[:200] if not success else "OK",
        "duration": round(duration, 0),
        "cmd": f"{cmd_type} {cmd[:80]}"
    }

def main():
    fast = "--fast" in sys.argv
    
    # Single cron mode
    cron_name = None
    for i, arg in enumerate(sys.argv):
        if arg == "--cron" and i+1 < len(sys.argv):
            cron_name = sys.argv[i+1]
    
    crons = load_crons()
    print(f"{BOLD}=== Cron Health Check ==={RESET}")
    print(f"Testing {len(crons)} crons {'(FAST MODE)' if fast else ''}")
    print()
    
    results = []
    
    if cron_name:
        # Single cron mode
        for c in crons:
            if cron_name.lower() in c.get("name", "").lower():
                result = test_cron(c, fast=fast)
                results.append(result)
                break
    else:
        # All crons
        for c in crons:
            result = test_cron(c, fast=fast)
            results.append(result)
    
    # Print results
    print(f"{'='*70}")
    for r in results:
        name = r["name"][:45]
        
        if r["status"] == "SKIP":
            icon = f"{YELLOW}⏭{RESET}"
            print(f"{icon} {name:<45} | {r['reason']}")
        elif r["status"] == "OK":
            icon = f"{GREEN}✅{RESET}"
            print(f"{icon} {name:<45} | {r['duration']:.0f}ms")
        elif r["status"] == "FAIL":
            icon = f"{RED}❌{RESET}"
            print(f"{icon} {name:<45} | {r['reason'][:50]}")
        elif r["status"] == "PATH_ERROR":
            icon = f"{RED}🚨{RESET}"
            print(f"{icon} {name:<45} | PATH: {r['reason']}")
            print(f"   Command: {r['cmd']}")
    
    # Summary
    print()
    print(f"{'='*70}")
    ok = sum(1 for r in results if r["status"] == "OK")
    fail = sum(1 for r in results if r["status"] == "FAIL")
    path_err = sum(1 for r in results if r["status"] == "PATH_ERROR")
    skip = sum(1 for r in results if r["status"] == "SKIP")
    
    print(f"{BOLD}Summary:{RESET} {GREEN}✅ {ok} OK{RESET} | {RED}❌ {fail} FAIL{RESET} | {RED}🚨 {path_err} PATH_ERROR{RESET} | {YELLOW}⏭ {skip} SKIP{RESET}")
    
    if fail > 0 or path_err > 0:
        print(f"\n{RED}⚠️  {fail + path_err} crons need attention{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}🎉 All crons healthy{RESET}")

if __name__ == "__main__":
    main()
