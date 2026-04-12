#!/usr/bin/env python3
"""
SELF_IMPROVEMENT_ORCHESTRATOR.py — Phase 5 Consolidation
=========================================================
Single entry point for all self-improvement activities.

Modes:
    --hourly      : Learning Coordinator + Continuous Improver (combined)
    --overnight   : Autonomous Improvement experiments
    --weekly      : Meta-Improver experience extraction
    --full        : All of the above
    --status      : Show current status of all improvement systems

Usage:
    python3 SELF_IMPROVEMENT_ORCHESTRATOR.py --hourly
    python3 SELF_IMPROVEMENT_ORCHESTRATOR.py --overnight
    python3 SELF_IMPROVEMENT_ORCHESTRATOR.py --weekly
    python3 SELF_IMPROVEMENT_ORCHESTRATOR.py --full
    python3 SELF_IMPROVEMENT_ORCHESTRATOR.py --status

Consolidates:
    - learning_coordinator.py (hourly learning loop)
    - continuous_improver.py (hourly autonomous improvements)
    - autonomous_improvement.py (overnight experiments)
    - meta_improver.py (weekly experience extraction)
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
IMPROVEMENT_LOG = WORKSPACE / "logs" / "orchestrator.log"

# Individual scripts
LEARNING_COORDINATOR = SCRIPTS_DIR / "learning_coordinator.py"
CONTINUOUS_IMPROVER = SCRIPTS_DIR / "continuous_improver.py"
AUTONOMOUS_IMPROVEMENT = SCRIPTS_DIR / "autonomous_improvement.py"
META_IMPROVER = SCRIPTS_DIR / "meta_improver.py"


def log(msg: str, emoji: str = "  "):
    """Log to file and print."""
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {emoji} {msg}"
    print(line)
    IMPROVEMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENT_LOG, "a") as f:
        f.write(line + "\n")


def run_script(script_path: Path, args: list = None, timeout: int = 300) -> tuple:
    """Run a script and return (success, output)."""
    cmd = ["python3", str(script_path)] + (args or [])
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(WORKSPACE)
        )
        return result.returncode == 0, result.stdout[-500:] if result.stdout else ""
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, str(e)


def status() -> dict:
    """Get status of all improvement systems."""
    state = {
        "learning_coordinator": {"exists": LEARNING_COORDINATOR.exists()},
        "continuous_improver": {"exists": CONTINUOUS_IMPROVER.exists()},
        "autonomous_improvement": {"exists": AUTONOMOUS_IMPROVEMENT.exists()},
        "meta_improver": {"exists": META_IMPROVER.exists()},
    }
    
    # Check recent activity
    log_file = WORKSPACE / "logs" / "continuous_improvement.json"
    if log_file.exists():
        try:
            data = json.load(open(log_file))
            state["last_improvement"] = data.get("last_improvement", "unknown")
        except:
            pass
    
    return state


def run_hourly():
    """Run hourly combined: Learning Coordinator + Continuous Improver."""
    log("🚀 Starting HOURLY improvement cycle", "⏰")
    
    # 1. Learning Coordinator (main loop)
    log("📚 Running Learning Coordinator...", "📚")
    success, output = run_script(LEARNING_COORDINATOR, ["--full"], timeout=300)
    log(f"   Learning Coordinator: {'✅' if success else '❌'} {output[:200]}", "📚")
    
    # 2. Continuous Improver (autonomous improvements)
    log("⚡ Running Continuous Improver...", "⚡")
    success, output = run_script(CONTINUOUS_IMPROVER, [], timeout=120)
    log(f"   Continuous Improver: {'✅' if success else '❌'} {output[:200]}", "⚡")
    
    log("✅ Hourly cycle complete", "✅")


def run_overnight():
    """Run overnight autonomous experiments."""
    log("🌙 Starting OVERNIGHT improvement cycle", "🌙")
    
    log("🧪 Running Autonomous Improvement...", "🧪")
    success, output = run_script(AUTONOMOUS_IMPROVEMENT, ["--review"], timeout=600)
    log(f"   Autonomous Improvement: {'✅' if success else '❌'} {output[:200]}", "🧪")
    
    log("✅ Overnight cycle complete", "✅")


def run_weekly():
    """Run weekly meta-improvement extraction."""
    log("📅 Starting WEEKLY improvement cycle", "📅")
    
    log("🧠 Running Meta-Improver...", "🧠")
    success, output = run_script(META_IMPROVER, ["--analyze"], timeout=300)
    log(f"   Meta-Improver: {'✅' if success else '❌'} {output[:200]}", "🧠")
    
    log("✅ Weekly cycle complete", "✅")


def run_full():
    """Run all improvement cycles."""
    log("🚀 Starting FULL improvement marathon", "🚀")
    
    run_hourly()
    run_overnight()
    run_weekly()
    
    log("🏆 FULL improvement complete", "🏆")


def show_status():
    """Show status of all improvement systems."""
    print("=" * 60)
    print("📊 SELF-IMPROVEMENT ORCHESTRATOR — Status")
    print("=" * 60)
    
    state = status()
    
    for name, info in state.items():
        exists = "✅" if info.get("exists") else "❌"
        last = info.get("last_improvement", "unknown")
        print(f"  {exists} {name}: exists={info.get('exists')}")
    
    print(f"  Last improvement: {state.get('last_improvement', 'unknown')}")
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    
    mode = sys.argv[1]
    
    modes = {
        "--hourly": run_hourly,
        "--overnight": run_overnight,
        "--weekly": run_weekly,
        "--full": run_full,
        "--status": show_status,
    }
    
    if mode not in modes:
        print(f"Unknown mode: {mode}")
        print(f"Available: {', '.join(modes.keys())}")
        return 1
    
    modes[mode]()
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)