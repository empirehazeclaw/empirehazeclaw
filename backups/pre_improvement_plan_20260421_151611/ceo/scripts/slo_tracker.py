#!/usr/bin/env python3
"""
SLO Tracker — Phase 5, Day 2
================================
Tracks SLOs (Service Level Objectives) for each task type.

Features:
- SLO definition per task type
- Actual vs SLO compliance tracking
- Breach detection and alerting
- SLO history and trends

Usage:
    python3 slo_tracker.py --define <type> <slo>  # Define SLO for task type
    python3 slo_tracker.py --log <type> <value>  # Log actual value
    python3 slo_tracker.py --check <type>        # Check SLO compliance
    python3 slo_tracker.py --status               # Show all SLOs
    python3 slo_tracker.py --breaches             # Show recent breaches
    python3 slo_tracker.py --report               # Generate SLO report
"""

import json
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
SLO_DIR = WORKSPACE / "memory" / "evaluations" / "slo_tracking"
SLO_FILE = SLO_DIR / "slo_config.json"
BREACH_FILE = SLO_DIR / "breaches.json"

# Default SLO templates
DEFAULT_SLOS = {
    "fast_task": {"target": 0.95, "metric": "success_rate", "window": "1h"},
    "complex_task": {"target": 0.85, "metric": "success_rate", "window": "24h"},
    "delegation": {"target": 0.90, "metric": "success_rate", "window": "1h"},
    "research": {"target": 0.80, "metric": "success_rate", "window": "24h"},
    "default": {"target": 0.90, "metric": "success_rate", "window": "1h"}
}

def init_dirs():
    SLO_DIR.mkdir(parents=True, exist_ok=True)
    
    if not SLO_FILE.exists():
        SLO_FILE.write_text(json.dumps({
            "slos": DEFAULT_SLOS.copy(),
            "history": [],
            "version": "1.0"
        }))
    
    if not BREACH_FILE.exists():
        BREACH_FILE.write_text(json.dumps({"breaches": [], "version": "1.0"}))

def load_slos():
    init_dirs()
    return json.loads(SLO_FILE.read_text())

def save_slos(data):
    SLO_FILE.write_text(json.dumps(data, indent=2))

def load_breaches():
    init_dirs()
    return json.loads(BREACH_FILE.read_text())

def save_breaches(data):
    BREACH_FILE.write_text(json.dumps(data, indent=2))

def define_slo(task_type, target, metric="success_rate", window="1h"):
    """Define or update SLO for a task type."""
    slos = load_slos()
    
    slos["slos"][task_type] = {
        "target": float(target),
        "metric": metric,
        "window": window,
        "defined_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    save_slos(slos)
    target_float = float(target)
    print(f"✅ SLO defined: {task_type}")
    print(f"   Target: {target_float:.0%}")
    print(f"   Metric: {metric}")
    print(f"   Window: {window}")

def log_task_result(task_type, success, duration=None, value=None):
    """Log the result of a task for SLO tracking."""
    slos = load_slos()
    breaches = load_breaches()
    
    now = datetime.now(timezone.utc).isoformat()
    
    # Add to history
    history_entry = {
        "timestamp": now,
        "task_type": task_type,
        "success": success,
        "duration": duration,
        "value": value
    }
    slos["history"].append(history_entry)
    
    # Keep only last 10000 entries
    if len(slos["history"]) > 10000:
        slos["history"] = slos["history"][-5000:]
    
    # Check SLO compliance
    if task_type in slos["slos"]:
        slo = slos["slos"][task_type]
        actual = calculate_actual(task_type, slos, slo["window"])
        target = slo["target"]
        
        if actual < target:
            # SLO breach!
            breach = {
                "timestamp": now,
                "task_type": task_type,
                "actual": actual,
                "target": target,
                "delta": target - actual,
                "window": slo["window"]
            }
            breaches["breaches"].append(breach)
            
            # Keep only last 100 breaches
            if len(breaches["breaches"]) > 100:
                breaches["breaches"] = breaches["breaches"][-50:]
            
            save_breaches(breaches)
            print(f"⚠️  SLO BREACH: {task_type}")
            print(f"    Actual: {actual:.1%} | Target: {target:.1%} | Delta: {breach['delta']:.1%}")
        else:
            print(f"✅ {task_type}: {actual:.1%} (target: {target:.1%})")
    
    save_slos(slos)
    return actual if task_type in slos["slos"] else None

def calculate_actual(task_type, slos, window):
    """Calculate actual performance for a task type over the window."""
    now = datetime.now(timezone.utc)
    
    # Parse window
    window_minutes = parse_window(window)
    cutoff = now - timedelta(minutes=window_minutes)
    
    # Filter history
    relevant = [
        h for h in slos["history"]
        if h["task_type"] == task_type
        and datetime.fromisoformat(h["timestamp"].replace("Z", "+00:00")) > cutoff
    ]
    
    if not relevant:
        return 1.0  # No data = assume success
    
    successes = sum(1 for h in relevant if h.get("success", False))
    return successes / len(relevant)

def parse_window(window):
    """Parse window string to minutes."""
    if window.endswith("h"):
        return int(window[:-1]) * 60
    elif window.endswith("m"):
        return int(window[:-1])
    elif window.endswith("d"):
        return int(window[:-1]) * 24 * 60
    return 60  # Default 1 hour

def check_slo(task_type):
    """Check SLO compliance for a task type."""
    slos = load_slos()
    
    if task_type not in slos["slos"]:
        print(f"[*] No SLO defined for {task_type}")
        return None
    
    slo = slos["slos"][task_type]
    actual = calculate_actual(task_type, slos, slo["window"])
    target = slo["target"]
    
    status = "✅" if actual >= target else "❌"
    
    print(f"\n{status} SLO Check: {task_type}")
    print(f"=" * 40)
    print(f"Target:     {target:.1%}")
    print(f"Actual:    {actual:.1%}")
    print(f"Status:    {'OK' if actual >= target else 'BREACH'}")
    print(f"Window:    {slo['window']}")
    print(f"Metric:    {slo['metric']}")
    
    if actual < target:
        delta = target - actual
        print(f"Delta:     -{delta:.1%}")
    
    return actual

def show_status():
    """Show status of all SLOs."""
    slos = load_slos()
    
    print(f"\n📊 SLO Status")
    print("=" * 50)
    
    total_slos = len(slos["slos"])
    compliant = 0
    breached = 0
    
    for task_type, slo in sorted(slos["slos"].items()):
        actual = calculate_actual(task_type, slos, slo["window"])
        target = slo["target"]
        
        if actual >= target:
            status = "✅"
            compliant += 1
        else:
            status = "❌"
            breached += 1
        
        delta = actual - target
        delta_str = f"{delta:+.1%}" if delta != 0 else "0.0%"
        
        print(f"{status} {task_type}")
        print(f"    Actual: {actual:.1%} | Target: {target:.1%} | Delta: {delta_str}")
    
    print(f"\nSummary: {compliant}/{total_slos} compliant, {breached} breached")
    
    # Recent history stats
    recent = slos["history"][-100:] if slos["history"] else []
    if recent:
        success_rate = sum(1 for h in recent if h.get("success", False)) / len(recent)
        print(f"\nRecent 100 tasks: {success_rate:.1%} success rate")

def show_breaches():
    """Show recent SLO breaches."""
    breaches = load_breaches()
    
    if not breaches["breaches"]:
        print("[*] No breaches recorded.")
        return
    
    print(f"\n⚠️  Recent SLO Breaches ({len(breaches['breaches'])} total)")
    print("=" * 50)
    
    for breach in sorted(breaches["breaches"], key=lambda x: x["timestamp"], reverse=True)[:10]:
        ts = breach["timestamp"][:16]
        print(f"  {ts} | {breach['task_type']}")
        print(f"         Actual: {breach['actual']:.1%} | Target: {breach['target']:.1%}")
        print()

def generate_report():
    """Generate SLO compliance report."""
    slos = load_slos()
    breaches = load_breaches()
    
    # Calculate overall stats
    total_tasks = len(slos["history"])
    successful_tasks = sum(1 for h in slos["history"] if h.get("success", False))
    overall_rate = successful_tasks / max(total_tasks, 1)
    
    # Per-SLO stats
    slo_stats = {}
    for task_type, slo in slos["slos"].items():
        actual = calculate_actual(task_type, slos, slo["window"])
        compliant = actual >= slo["target"]
        slo_stats[task_type] = {
            "target": slo["target"],
            "actual": actual,
            "compliant": compliant,
            "delta": actual - slo["target"]
        }
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_tasks": total_tasks,
        "successful_tasks": successful_tasks,
        "overall_success_rate": overall_rate,
        "total_breaches": len(breaches["breaches"]),
        "slo_count": len(slos["slos"]),
        "compliant_count": sum(1 for s in slo_stats.values() if s["compliant"]),
        "slo_stats": slo_stats,
        "recent_breaches": breaches["breaches"][-10:] if breaches["breaches"] else []
    }
    
    print(f"\n📊 SLO Report")
    print("=" * 50)
    print(f"Generated: {report['generated_at'][:19]}")
    print(f"\nOverall:")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Success rate: {overall_rate:.1%}")
    print(f"\nSLO Compliance: {report['compliant_count']}/{report['slo_count']}")
    
    for task_type, stats in sorted(slo_stats.items(), key=lambda x: x[1]["delta"]):
        status = "✅" if stats["compliant"] else "❌"
        print(f"  {status} {task_type}: {stats['actual']:.1%} (target: {stats['target']:.1%})")
    
    print(f"\nBreaches: {report['total_breaches']} total")
    
    report_file = WORKSPACE / "docs" / "slo_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\nReport saved: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="SLO Tracker")
    parser.add_argument("--define", nargs=3, metavar=("TYPE", "TARGET", "METRIC"), help="Define SLO")
    parser.add_argument("--log", nargs=2, metavar=("TYPE", "SUCCESS"), help="Log task result")
    parser.add_argument("--check", metavar="TYPE", help="Check SLO compliance")
    parser.add_argument("--status", action="store_true", help="Show all SLOs")
    parser.add_argument("--breaches", action="store_true", help="Show breaches")
    parser.add_argument("--report", action="store_true", help="Generate SLO report")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.define:
        define_slo(args.define[0], args.define[1], args.define[2])
    
    if args.log:
        success = args.log[1].lower() == "true" or args.log[1] == "1"
        log_task_result(args.log[0], success)
    
    if args.check:
        check_slo(args.check)
    
    if args.status:
        show_status()
    
    if args.breaches:
        show_breaches()
    
    if args.report:
        generate_report()

if __name__ == "__main__":
    main()
