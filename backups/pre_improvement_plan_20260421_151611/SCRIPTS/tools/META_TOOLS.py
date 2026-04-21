#!/usr/bin/env python3
"""
META_TOOLS.py — Bundled Tool Sequences for Common Operations
===========================================================
Single commands that combine multiple tools.

Usage:
    python3 META_TOOLS.py health-check-all
    python3 META_TOOLS.py improvement-cycle
    python3 META_TOOLS.py backup-verify
    python3 META_TOOLS.py kg-refresh
    python3 META_TOOLS.py error-diagnose
    python3 META_TOOLS.py full-audit
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"


def log(msg, emoji="  "):
    print(f"{emoji} {msg}")


def run(script_name, args=None, timeout=120):
    """Run a script and return success."""
    cmd = ["python3", str(SCRIPTS_DIR / script_name)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(WORKSPACE))
        return result.returncode == 0, result.stdout[-300:] if result.stdout else ""
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, str(e)


def health_check_all():
    """Run full health check: health + cron + error analysis."""
    log("🏥 Starting HEALTH CHECK ALL", "🏥")
    print()
    
    checks = [
        ("health_check.py", ["--full"], "Health Check"),
        ("cron_watchdog.py", ["--report"], "Cron Watchdog"),
        ("error_rate_monitor.py", [], "Error Rate Monitor"),
    ]
    
    results = []
    for script, args, name in checks:
        log(f"Running {name}...", "⏳")
        success, output = run(script, args, timeout=60)
        emoji = "✅" if success else "❌"
        log(f"  {name}: {emoji}", emoji)
        log(f"  {output[:150]}", "  ")
        results.append((name, success))
    
    print()
    all_ok = all(r[1] for r in results)
    log(f"{'✅ ALL CHECKS PASSED' if all_ok else '⚠️  SOME CHECKS FAILED'}", "🏁")
    return 0 if all_ok else 1


def improvement_cycle():
    """Run full improvement cycle: learn + improve + validate."""
    log("🚀 Starting IMPROVEMENT CYCLE", "🚀")
    print()
    
    # Use the orchestrator
    success, output = run("SELF_IMPROVEMENT_ORCHESTRATOR.py", ["--hourly"], timeout=300)
    log(f"Orchestrator: {'✅' if success else '❌'}", "🚀")
    log(f"  {output[:200]}", "  ")
    
    return 0 if success else 1


def backup_verify():
    """Run backup + verify."""
    log("💾 Starting BACKUP + VERIFY", "💾")
    print()
    
    log("Running Auto Backup...", "⏳")
    success1, _ = run("auto_backup.py", [], timeout=120)
    log(f"  Backup: {'✅' if success1 else '❌'}", "✅" if success1 else "❌")
    
    log("Running Backup Verify...", "⏳")
    success2, output = run("backup_verify.py", ["--report"], timeout=60)
    log(f"  Verify: {'✅' if success2 else '❌'}", "✅" if success2 else "❌")
    log(f"  {output[:200]}", "  ")
    
    return 0 if (success1 and success2) else 1


def kg_refresh():
    """Refresh KG: stats + enhance + clean relations."""
    log("🧠 Starting KG REFRESH", "🧠")
    print()
    
    steps = [
        ("kg_updater.py", ["stats"], "KG Stats", 30),
        ("kg_updater.py", ["lifecycle", "--all"], "KG Lifecycle", 60),
    ]
    
    for script, args, name, timeout in steps:
        log(f"Running {name}...", "⏳")
        success, output = run(script, args, timeout=timeout)
        log(f"  {name}: {'✅' if success else '❌'}", "✅" if success else "❌")
    
    return 0


def error_diagnose():
    """Diagnose recent errors: analyze + reduce + report."""
    log("🔍 Starting ERROR DIAGNOSE", "🔍")
    print()
    
    steps = [
        ("error_rate_monitor.py", [], "Error Analysis", 60),
        ("error_reducer.py", ["--analyze"], "Error Reducer", 120),
    ]
    
    for script, args, name, timeout in steps:
        log(f"Running {name}...", "⏳")
        success, output = run(script, args, timeout=timeout)
        log(f"  {name}: {'✅' if success else '❌'}", "✅" if success else "❌")
        if output:
            log(f"  {output[:150]}", "  ")
    
    return 0


def full_audit():
    """Run full system audit."""
    log("📋 Starting FULL AUDIT", "📋")
    print()
    
    log("Health Check All...", "🏥")
    r1 = health_check_all()
    
    log("KG Refresh...", "🧠")
    r2 = kg_refresh()
    
    log("Error Diagnose...", "🔍")
    r3 = error_diagnose()
    
    print()
    overall = "✅ ALL SYSTEMS OK" if all([r1 == 0, r2 == 0, r3 == 0]) else "⚠️  ISSUES FOUND"
    log(overall, "🏁")
    
    return 0 if all([r1 == 0, r2 == 0, r3 == 0]) else 1


TOOLS = {
    "health-check-all": (health_check_all, "Run health + cron + error checks"),
    "improvement-cycle": (improvement_cycle, "Run full improvement loop"),
    "backup-verify": (backup_verify, "Run backup + verify"),
    "kg-refresh": (kg_refresh, "Refresh knowledge graph"),
    "error-diagnose": (error_diagnose, "Diagnose and reduce errors"),
    "full-audit": (full_audit, "Run full system audit"),
}


def main():
    if len(sys.argv) < 2:
        print("META_TOOLS — Bundled Tool Sequences")
        print("=" * 50)
        for name, (func, desc) in TOOLS.items():
            print(f"  {name:<20} — {desc}")
        print()
        print("Usage: python3 META_TOOLS.py <tool>")
        return 0
    
    tool = sys.argv[1]
    
    if tool not in TOOLS:
        print(f"Unknown tool: {tool}")
        print(f"Available: {', '.join(TOOLS.keys())}")
        return 1
    
    func, desc = TOOLS[tool]
    print(f"{'=' * 50}")
    print(f"🎯 {tool} — {desc}")
    print(f"{'=' * 50}")
    print()
    
    return func()


if __name__ == "__main__":
    sys.exit(main() or 0)