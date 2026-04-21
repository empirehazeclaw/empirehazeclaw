#!/usr/bin/env python3
"""
Morning CEO Report — Sir HazeClaw
==================================
Consolidated 08:00 report: Data Kitchen results + Status + Goals + Learning

Replaces:
- Morning Summary 08:00 (Telegram report only)
- Morning Briefing 09:00 (status + goals + learning)

Schedule: 08:00 UTC daily
"""

import subprocess
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CEO = WORKSPACE / "ceo"
LOG_FILE = WORKSPACE / "logs" / "morning_ceo.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run(name, cmd, timeout=60):
    log(f"Running: {name}")
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            log(f"  ✓ {name}")
            return True, r.stdout[:300]
        else:
            log(f"  ✗ {name}: {r.stderr[:200]}")
            return False, r.stderr[:200]
    except Exception as e:
        log(f"  ✗ {name}: {e}")
        return False, str(e)[:200]

def get_data_kitchen_results():
    """Read last Morning Data Kitchen results (ran at 06h)."""
    log_file = WORKSPACE / "logs" / "morning_kitchen.log"
    if not log_file.exists():
        return None
    with open(log_file) as f:
        lines = f.readlines()
    # Find last run
    for line in reversed(lines):
        if "Morning Data Kitchen END" in line:
            # Parse: "{'short_term': 'OK', 'semantic': 'OK', ...}"
            import ast
            try:
                data = line.strip().split("END: ")[1]
                return ast.literal_eval(data)
            except:
                return None
    return None

def get_learning_loop_state():
    """Get learning loop state."""
    state_file = CEO / "memory" / "evaluations" / "learning_loop_signal.json"
    if not state_file.exists():
        return {}
    with open(state_file) as f:
        return json.load(f)

def get_goal_tracker():
    """Get goal status."""
    ok, out = run("Goal Tracker", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/goal_tracker.py status 2>&1 | head -20", timeout=30)
    return out if ok else "No goals"

def main():
    log("=" * 50)
    log("Morning CEO Report START")

    report = "🌅 Morning Report — " + datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC") + "\n\n"

    # 1. Data Kitchen Results (from 06h)
    dk = get_data_kitchen_results()
    if dk:
        report += "🧹 Data Kitchen (06h):\n"
        for k, v in dk.items():
            icon = "✅" if v == "OK" else "⚠️"
            report += f"  {icon} {k}: {v}\n"
    else:
        report += "🧹 Data Kitchen: No recent run found\n"

    # 2. Learning Loop State
    sig = get_learning_loop_state()
    metrics = sig.get("metrics", {})
    tsr = metrics.get("task_success_rate", "N/A")
    errors = metrics.get("error_rate", "N/A")
    total = metrics.get("total_tasks", "N/A")
    report += f"\n📊 Learning Loop:\n"
    report += f"  Tasks: {total} | Success: {tsr} | Errors: {errors}\n"

    # 3. KG State
    kg_file = CEO / "memory" / "kg" / "knowledge_graph.json"
    if kg_file.exists():
        with open(kg_file) as f:
            kg = json.load(f)
        report += f"  KG: {len(kg.get('entities', {}))} entities\n"

    # 4. Goal Status
    goals = get_goal_tracker()
    report += f"\n🎯 Goals:\n"
    if "No goals" in goals or not goals:
        report += "  (keine konfiguriert)\n"
    else:
        for line in goals.split("\n")[:5]:
            if line.strip():
                report += f"  {line}\n"

    # 5. System Status (quick check)
    ok, _ = run("Gateway Check", "openclaw status 2>&1 | head -3", timeout=10)
    gw_status = "✅" if ok else "❌"
    report += f"\n🏥 Gateway: {gw_status}\n"

    log("Morning CEO Report END")
    print(report)
    return report

if __name__ == "__main__":
    main()
