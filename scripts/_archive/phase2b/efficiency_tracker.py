#!/usr/bin/env python3
"""
efficiency_tracker.py — Track First-Attempt Success Rate
Sir HazeClaw - 2026-04-11

Usage:
    python3 efficiency_tracker.py
    python3 efficiency_tracker.py --report
    python3 efficiency_tracker.py --success --task "description"
    python3 efficiency_tracker.py --failure --task "description"
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
METRICS_FILE = WORKSPACE / "memory" / "efficiency_metrics.json"

def load_metrics():
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {"tasks": [], "daily": {}}

def save_metrics(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def record_task(task: str, success: bool, error_type: str = None):
    """Record a task completion."""
    metrics = load_metrics()
    today = datetime.now().strftime("%Y-%m-%d")
    
    entry = {
        "task": task[:100],
        "success": success,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat(),
        "hour": datetime.now().hour
    }
    
    metrics["tasks"].append(entry)
    
    # Keep only last 100 entries
    if len(metrics["tasks"]) > 100:
        metrics["tasks"] = metrics["tasks"][-100:]
    
    # Daily tracking
    if today not in metrics["daily"]:
        metrics["daily"][today] = {"total": 0, "success": 0, "failure": 0}
    
    metrics["daily"][today]["total"] += 1
    if success:
        metrics["daily"][today]["success"] += 1
    else:
        metrics["daily"][today]["failure"] += 1
    
    save_metrics(metrics)

def calculate_fas_rate():
    """Calculate First-Attempt Success Rate."""
    metrics = load_metrics()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if today not in metrics["daily"]:
        return 0, 0
    
    d = metrics["daily"][today]
    total = d["total"]
    success = d["success"]
    
    if total == 0:
        return 0, 0
    
    rate = (success / total) * 100
    return rate, total

def report():
    """Show efficiency report."""
    metrics = load_metrics()
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("📊 EFFICIENCY TRACKER")
    print("=" * 50)
    
    # FAS Rate
    fas_rate, total = calculate_fas_rate()
    print(f"\n📈 First-Attempt Success Rate:")
    print(f"   Today: {fas_rate:.1f}% ({total} tasks)")
    
    # Target
    target = 80
    if fas_rate >= target:
        print(f"   ✅ Target ({target}%) ACHIEVED!")
    else:
        gap = target - fas_rate
        print(f"   ⚠️ {gap:.1f}% below target ({target}%)")
    
    # Weekly trend
    if len(metrics["daily"]) >= 7:
        days = sorted(metrics["daily"].keys())[-7:]
        avg_rate = sum(
            metrics["daily"][d]["success"] / metrics["daily"][d]["total"] * 100
            for d in days
            if metrics["daily"][d]["total"] > 0
        ) / len(days)
        print(f"\n📅 7-day average: {avg_rate:.1f}%")
    
    # Recent failures
    failures = [t for t in metrics["tasks"][-20:] if not t["success"]]
    if failures:
        print(f"\n⚠️ Recent failures ({len(failures)}):")
        for f in failures[-5:]:
            print(f"   - {f['task'][:50]}... ({f.get('error_type', 'unknown')})")
    
    return fas_rate, total

def main():
    if "--report" in sys.argv:
        report()
        return
    
    if "--success" in sys.argv:
        task = ""
        for i, arg in enumerate(sys.argv):
            if arg == "--task" and i + 1 < len(sys.argv):
                task = sys.argv[i + 1]
        record_task(task, True)
        rate, total = calculate_fas_rate()
        print(f"✅ Task recorded. FAS Rate: {rate:.1f}% ({total} today)")
        return
    
    if "--failure" in sys.argv:
        task = ""
        error_type = None
        for i, arg in enumerate(sys.argv):
            if arg == "--task" and i + 1 < len(sys.argv):
                task = sys.argv[i + 1]
            if arg == "--error" and i + 1 < len(sys.argv):
                error_type = sys.argv[i + 1]
        record_task(task, False, error_type)
        rate, total = calculate_fas_rate()
        print(f"❌ Task recorded. FAS Rate: {rate:.1f}% ({total} today)")
        return
    
    # Default: show report
    report()

if __name__ == "__main__":
    main()
