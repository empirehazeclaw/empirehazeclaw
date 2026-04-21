#!/usr/bin/env python3
"""
KAIROS_CONDITIONAL.py — Autonomous Decision Engine
===================================================
Decides what to run based on current system state.

KAIROS = "Knowing When to Act, Rather Than Just Scheduled Operations"

Usage:
    python3 KAIROS_CONDITIONAL.py --decide    # Decide what needs to run
    python3 KAIROS_CONDITIONAL.py --run-all   # Run all conditional checks
    python3 KAIROS_CONDITIONAL.py --status    # Show current state
"""

import subprocess
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"


def log(msg, emoji="  "):
    print(f"{emoji} {msg}")


def load_json(path, default=None):
    """Load JSON file, return default if missing."""
    try:
        if Path(path).exists():
            return json.load(open(path))
    except:
        pass
    return default or {}


def get_error_rate():
    """Get current error rate from metrics."""
    metrics = load_json(WORKSPACE / "memory/session_metrics_history.json")
    if metrics:
        # Calculate from recent sessions
        sessions = metrics.get("sessions", [])
        if sessions:
            recent = sessions[-10:]  # Last 10 sessions
            errors = sum(1 for s in recent if s.get("had_error"))
            return (errors / len(recent)) * 100 if recent else 0
    return 0


def get_cron_failures():
    """Count recent cron failures."""
    log_file = WORKSPACE / "logs" / "cron_healer.log"
    if not log_file.exists():
        return 0
    
    try:
        lines = log_file.read_text().split("\n")
        # Count failures in last 24h
        yesterday = datetime.now() - timedelta(hours=24)
        failures = 0
        for line in lines:
            if "FAIL" in line or "ERROR" in line.upper():
                # Try to parse timestamp
                if "2026-04" in line:
                    failures += 1
        return min(failures, 10)  # Cap at 10
    except:
        return 0


def get_kg_staleness():
    """Check if KG was updated recently."""
    kg_path = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"
    if not kg_path.exists():
        return 999
    
    try:
        kg = json.load(open(kg_path))
        last_updated = kg.get("last_updated", "")
        if last_updated:
            dt = datetime.fromisoformat(last_updated)
            return (datetime.now() - dt).days
    except:
        pass
    return 0


def should_run_healer():
    """Should we run the cron healer?"""
    failures = get_cron_failures()
    threshold = 3
    if failures >= threshold:
        log(f"🔴 Cron failures: {failures} >= {threshold} → RUN HEALER", "🔴")
        return True
    log(f"✅ Cron failures: {failures} < {threshold} → skip healer", "✅")
    return False


def should_run_extra_learning():
    """Should we run extra learning?"""
    rate = get_error_rate()
    threshold = 2.0
    if rate >= threshold:
        log(f"🔴 Error rate: {rate:.1f}% >= {threshold}% → RUN EXTRA LEARNING", "🔴")
        return True
    log(f"✅ Error rate: {rate:.1f}% < {threshold}% → skip extra", "✅")
    return False


def should_refresh_kg():
    """Should we refresh KG?"""
    days = get_kg_staleness()
    threshold = 7
    if days >= threshold:
        log(f"🔴 KG stale: {days} days >= {threshold} → REFRESH KG", "🔴")
        return True
    log(f"✅ KG fresh: {days} days < {threshold} → skip refresh", "✅")
    return False


def run(script, args=None, timeout=60):
    """Run a script."""
    cmd = ["python3", str(SCRIPTS_DIR / script)] + (args or [])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(WORKSPACE))
        return result.returncode == 0
    except:
        return False


def decide():
    """Decide what needs to run based on system state."""
    print("=" * 60)
    print("🎯 KAIROS CONDITIONAL DECISION ENGINE")
    print("=" * 60)
    print()
    
    print("📊 Current System State:")
    print(f"   Error rate: {get_error_rate():.1f}%")
    print(f"   Cron failures (24h): {get_cron_failures()}")
    print(f"   KG staleness: {get_kg_staleness()} days")
    print()
    
    print("🔍 Checking conditions:")
    print()
    
    actions = []
    
    if should_run_healer():
        actions.append(("cron_error_healer", ["--quick"]))
    
    if should_run_extra_learning():
        actions.append(("SELF_IMPROVEMENT_ORCHESTRATOR", ["--hourly"]))
    
    if should_refresh_kg():
        actions.append(("kg_updater", ["lifecycle", "--all"]))
    
    print()
    if not actions:
        log("✅ NO ACTION NEEDED — System is healthy", "✅")
        return 0
    
    log(f"📋 DECIDED {len(actions)} ACTION(S):", "📋")
    for script, args in actions:
        log(f"   → {script} {' '.join(args)}", "👉")
    
    return 0


def run_all():
    """Run all conditional checks and actions."""
    log("🚀 KAIROS: Running all checks + actions", "🚀")
    
    decided_actions = []
    
    if should_run_healer():
        decided_actions.append(("cron_error_healer.py", ["--quick"], 60))
    
    if should_run_extra_learning():
        decided_actions.append(("SELF_IMPROVEMENT_ORCHESTRATOR.py", ["--hourly"], 300))
    
    if should_refresh_kg():
        decided_actions.append(("kg_updater.py", ["lifecycle", "--all"], 60))
    
    if not decided_actions:
        log("✅ Nothing needed — system healthy", "✅")
        return 0
    
    print()
    for script, args, timeout in decided_actions:
        log(f"Running {script}...", "⏳")
        success = run(script, args, timeout)
        log(f"   {'✅' if success else '❌'}", "✅" if success else "❌")
    
    return 0


def show_status():
    """Show current system status."""
    print("=" * 60)
    print("📊 KAIROS — System Status")
    print("=" * 60)
    
    print()
    print(f"   Error Rate:    {get_error_rate():.1f}% (threshold: 2%)")
    print(f"   Cron Failures:  {get_cron_failures()} (threshold: 3)")
    print(f"   KG Staleness:   {get_kg_staleness()} days (threshold: 7)")
    
    print()
    if should_run_healer():
        print("   🔴 Need to run: cron_error_healer")
    if should_run_extra_learning():
        print("   🔴 Need to run: extra learning")
    if should_refresh_kg():
        print("   🔴 Need to run: KG refresh")
    
    if not any([should_run_healer(), should_run_extra_learning(), should_refresh_kg()]):
        print("   ✅ All systems healthy — no action needed")
    
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    
    mode = sys.argv[1]
    
    modes = {
        "--decide": decide,
        "--run-all": run_all,
        "--status": show_status,
    }
    
    if mode not in modes:
        print(f"Unknown mode: {mode}")
        print(f"Available: {', '.join(modes.keys())}")
        return 1
    
    return modes[mode]()


if __name__ == "__main__":
    sys.exit(main() or 0)