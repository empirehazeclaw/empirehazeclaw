#!/usr/bin/env python3
"""
Morning Status Check — Sir HazeClaw
===================================
Consolidated morning status: Security + Opportunity + Briefing

Replaces:
- Security Audit (08h)
- Security Officer Daily Scan (10:30)
- Opportunity Scanner Daily (09h)  
- CEO Daily Briefing (11h)

Schedule: 09:00 UTC daily
"""

import subprocess
import sys
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/workspace/logs/morning_status.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run_step(name, cmd):
    log(f"Running: {name}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            log(f"  ✓ {name}")
            return True, result.stdout[:500]
        else:
            log(f"  ✗ {name}: {result.stderr[:200]}")
            return False, result.stderr[:200]
    except Exception as e:
        log(f"  ✗ {name}: {e}")
        return False, str(e)[:200]

def main():
    log("="*50)
    log("Morning Status Check START")
    
    results = {}
    
    # 1. Security Audit
    ok, out = run_step("Security Audit", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/tools/security_audit.py --check 2>&1 | tail -10")
    results["security"] = "OK" if ok else "ISSUES"
    
    # 2. Opportunity Scanner
    ok, out = run_step("Opportunity Scanner", "python3 /home/clawbot/.openclaw/workspace/system/opportunity_scanner.py")
    results["opportunity"] = "OK" if ok else "ISSUES"
    
    # 3. Integration Health (quick check)
    ok, out = run_step("Integration Health", "python3 /home/clawbot/.openclaw/workspace/scripts/integration_dashboard.py --check 2>&1 | tail -5")
    results["health"] = "OK" if "healthy" in out.lower() or "all systems" in out.lower() else "CHECK"
    
    # Summary
    log(f"Results: {results}")
    log("Morning Status Check END")
    
    # Output summary for Telegram
    summary = "☀️ Morning Status\n"
    for k, v in results.items():
        summary += f"  {k}: {v}\n"
    print(summary)

if __name__ == "__main__":
    main()
