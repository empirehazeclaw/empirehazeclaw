#!/usr/bin/env python3
"""
Exploration Budget Manager — Phase 3, Day 1
============================================
Manages the 10% exploration budget for active experimentation.

Defines:
- Exploration budget (10% of runs)
- Experimental vs exploitation modes
- Strategy mutation tracking
- Exploration success metrics

Usage:
    python3 exploration_budget.py --status          # Show current budget status
    python3 exploration_budget.py --should-explore  # Should we explore this run?
    python3 exploration_budget.py --log-run <type>  # Log a run (exploration|exploitation)
    python3 exploration_budget.py --report          # Generate exploration report
    python3 exploration_budget.py --reset          # Reset budget counters
"""

import json
import argparse
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
BUDGET_FILE = WORKSPACE / "memory" / "evaluations" / "exploration_budget.json"

# Configuration
EXPLORATION_RATE = 0.10  # 10% exploration
ADAPTIVE_DECAY = 0.95    # Decay factor for adaptive exploration
MIN_EXPLORATION_RATE = 0.02
MAX_EXPLORATION_RATE = 0.20
STAGNATION_THRESHOLD = 5  # Consecutive similar outcomes = stagnation

def load_budget():
    """Load exploration budget data."""
    if BUDGET_FILE.exists():
        return json.loads(BUDGET_FILE.read_text())
    
    # Default structure
    return {
        "config": {
            "exploration_rate": EXPLORATION_RATE,
            "adaptive_decay": ADAPTIVE_DECAY,
            "min_rate": MIN_EXPLORATION_RATE,
            "max_rate": MAX_EXPLORATION_RATE,
            "stagnation_threshold": STAGNATION_THRESHOLD
        },
        "current_period": {
            "start": datetime.now(timezone.utc).isoformat(),
            "total_runs": 0,
            "exploration_runs": 0,
            "exploitation_runs": 0,
            "exploration_successes": 0,
            "exploitation_successes": 0,
            "experimental_strategies": []
        },
        "history": [],
        "version": "1.0"
    }

def save_budget(budget):
    """Save exploration budget data."""
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_FILE.write_text(json.dumps(budget, indent=2))

def should_explore():
    """Determine if the next run should be exploration or exploitation."""
    budget = load_budget()
    config = budget["config"]
    period = budget["current_period"]
    
    # Check if period should roll over (every 100 runs or every hour)
    period_start = datetime.fromisoformat(period["start"].replace("Z", "+00:00"))
    hours_old = (datetime.now(timezone.utc) - period_start).total_seconds() / 3600
    runs = period["total_runs"]
    
    if hours_old > 1 or runs >= 100:
        # Roll over to new period
        roll_over(budget)
    
    # Calculate adaptive exploration rate
    exploration_rate = config["exploration_rate"]
    
    # Check for stagnation - if we're stuck, increase exploration
    stagnation_count = get_stagnation_count(budget)
    if stagnation_count >= config["stagnation_threshold"]:
        exploration_rate = min(exploration_rate * 1.5, config["max_rate"])
        print(f"[!] Stagnation detected ({stagnation_count}). Increasing exploration rate to {exploration_rate:.1%}")
    
    # Check success rate - if exploration is working well, keep it
    if period["exploration_runs"] > 0:
        exploration_success_rate = period["exploration_successes"] / period["exploration_runs"]
        exploitation_success_rate = period["exploitation_successes"] / max(period["exploitation_runs"], 1)
        
        if exploration_success_rate > exploitation_success_rate + 0.1:
            # Exploration is winning - increase rate
            exploration_rate = min(exploration_rate * 1.2, config["max_rate"])
        elif exploration_success_rate < exploitation_success_rate - 0.15:
            # Exploration is losing - decrease rate
            exploration_rate = max(exploration_rate * config["adaptive_decay"], config["min_rate"])
    
    # Save adjusted rate
    budget["config"]["exploration_rate"] = exploration_rate
    save_budget(budget)
    
    # Decide based on probability
    import random
    decision = random.random() < exploration_rate
    
    return {
        "should_explore": decision,
        "exploration_rate": exploration_rate,
        "total_runs": period["total_runs"],
        "exploration_runs": period["exploration_runs"]
    }

def roll_over(budget):
    """Roll over to a new period, saving history."""
    period = budget["current_period"]
    
    # Save to history
    if period["total_runs"] > 0:
        history_entry = {
            "start": period["start"],
            "end": datetime.now(timezone.utc).isoformat(),
            "total_runs": period["total_runs"],
            "exploration_runs": period["exploration_runs"],
            "exploitation_runs": period["exploitation_runs"],
            "exploration_success_rate": period["exploration_successes"] / max(period["exploration_runs"], 1),
            "exploitation_success_rate": period["exploitation_successes"] / max(period["exploitation_runs"], 1),
            "experimental_strategies": period["experimental_strategies"]
        }
        budget["history"].append(history_entry)
        
        # Keep only last 100 periods
        budget["history"] = budget["history"][-100:]
    
    # Reset period
    budget["current_period"] = {
        "start": datetime.now(timezone.utc).isoformat(),
        "total_runs": 0,
        "exploration_runs": 0,
        "exploitation_runs": 0,
        "exploration_successes": 0,
        "exploitation_successes": 0,
        "experimental_strategies": []
    }
    
    save_budget(budget)
    print(f"[*] New exploration period started.")

def get_stagnation_count(budget):
    """Count consecutive similar outcomes."""
    # Simple implementation - count how many recent runs had similar success rates
    recent = budget["history"][-5:] if budget["history"] else []
    if len(recent) < 3:
        return 0
    
    rates = [r["exploration_success_rate"] for r in recent]
    avg = sum(rates) / len(rates)
    
    # Count how many are within 5% of each other
    stagnant = sum(1 for r in rates if abs(r - avg) < 0.05)
    return stagnant

def log_run(run_type: str, strategy: str = "default", success: bool = False, metrics: dict = None):
    """Log a run as exploration or exploitation."""
    if run_type not in ["exploration", "exploitation"]:
        print(f"[!] Invalid run type: {run_type}")
        return
    
    budget = load_budget()
    period = budget["current_period"]
    
    period["total_runs"] += 1
    
    if run_type == "exploration":
        period["exploration_runs"] += 1
        if strategy not in period["experimental_strategies"]:
            period["experimental_strategies"].append(strategy)
        if success:
            period["exploration_successes"] += 1
    else:
        period["exploitation_runs"] += 1
        if success:
            period["exploitation_successes"] += 1
    
    save_budget(budget)
    
    print(f"[*] Logged {run_type} run: strategy={strategy}, success={success}")
    print(f"    Period stats: {period['total_runs']} total, {period['exploration_runs']} exploration")

def show_status():
    """Show current exploration budget status."""
    budget = load_budget()
    config = budget["config"]
    period = budget["current_period"]
    
    exploration_rate = config["exploration_rate"]
    total = period["total_runs"]
    expl = period["exploration_runs"]
    expl_success = period["exploration_successes"]
    exploit = period["exploitation_runs"]
    exploit_success = period["exploitation_successes"]
    
    expl_rate = expl_success / max(expl, 1) if expl > 0 else 0
    exploit_rate = exploit_success / max(exploit, 1) if exploit > 0 else 0
    
    print(f"""
📊 Exploration Budget Status
{'=' * 40}
Config:
  Exploration Rate:  {exploration_rate:.1%} (target: {config['exploration_rate']:.0%})
  Adaptive Decay:    {config['adaptive_decay']}
  Rate Range:        {config['min_rate']:.0%} - {config['max_rate']:.0%}
  Stagnation Thresh: {config['stagnation_threshold']}

Current Period (started {period['start'][:16]}):
  Total Runs:        {total}
  Exploration Runs:  {expl} ({expl/total*100:.1f}% if total > 0 else 0.0%)
  Exploitation Runs: {exploit} ({exploit/total*100:.1f}% if total > 0 else 0.0%)
  Exploration Success Rate: {expl_rate:.1%}
  Exploitation Success Rate: {exploit_rate:.1%}
  Experimental Strategies: {', '.join(period['experimental_strategies']) or 'none'}

Recent History: {len(budget['history'])} periods
""")

def generate_report():
    """Generate exploration performance report."""
    budget = load_budget()
    history = budget["history"]
    
    if not history:
        print("[*] No history yet for report.")
        show_status()
        return
    
    # Calculate aggregate stats
    total_runs = sum(h["total_runs"] for h in history)
    total_expl = sum(h["exploration_runs"] for h in history)
    total_exploit = sum(h["exploitation_runs"] for h in history)
    
    avg_expl_rate = sum(h["exploration_success_rate"] for h in history) / len(history)
    avg_exploit_rate = sum(h["exploitation_success_rate"] for h in history) / len(history)
    
    # Best and worst periods
    best = max(history, key=lambda h: h["exploration_success_rate"])
    worst = min(history, key=lambda h: h["exploration_success_rate"])
    
    # Strategies tried
    all_strategies = set()
    for h in history:
        all_strategies.update(h.get("experimental_strategies", []))
    
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "periods_analyzed": len(history),
        "total_runs": total_runs,
        "exploration_runs": total_expl,
        "exploitation_runs": total_exploit,
        "avg_exploration_success_rate": avg_expl_rate,
        "avg_exploitation_success_rate": avg_exploit_rate,
        "best_period": best,
        "worst_period": worst,
        "experimental_strategies_tried": list(all_strategies),
        "recommendation": "increase_exploration" if avg_expl_rate > avg_exploit_rate else "decrease_exploration"
    }
    
    print(f"""
📈 Exploration Budget Report
{'=' * 50}
Generated: {report['generated_at'][:19]}

Aggregate Stats ({len(history)} periods):
  Total Runs:        {total_runs}
  Exploration Runs:  {total_expl} ({total_expl/total_runs*100:.1f}%)
  Exploitation Runs: {total_exploit} ({total_exploit/total_runs*100:.1f}%)

Success Rates:
  Exploration: {avg_expl_rate:.1%}
  Exploitation: {avg_exploit_rate:.1%}
  Difference: {avg_expl_rate - avg_exploit_rate:+.1%}

Best Period:
  Date: {best['start'][:10]}
  Exploration Success Rate: {best['exploration_success_rate']:.1%}

Worst Period:
  Date: {worst['start'][:10]}
  Exploration Success Rate: {worst['exploration_success_rate']:.1%}

Experimental Strategies Tried: {len(all_strategies)}
  {', '.join(all_strategies) if all_strategies else 'none'}

Recommendation: {'Increase exploration' if report['recommendation'] == 'increase_exploration' else 'Decrease exploration'}
""")
    
    # Save report
    report_file = WORKSPACE / "docs" / "exploration_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"📄 Report saved: {report_file}")
    
    return report

def reset_budget():
    """Reset all budget counters."""
    budget = load_budget()
    roll_over(budget)
    print("[*] Budget reset. New period started.")

def main():
    parser = argparse.ArgumentParser(description="Exploration Budget Manager")
    parser.add_argument("--status", action="store_true", help="Show current budget status")
    parser.add_argument("--should-explore", action="store_true", help="Check if should explore")
    parser.add_argument("--log-run", metavar=("TYPE", "STRATEGY"), nargs=2, help="Log a run")
    parser.add_argument("--log-success", metavar=("TYPE"), help="Log success for last run")
    parser.add_argument("--report", action="store_true", help="Generate exploration report")
    parser.add_argument("--reset", action="store_true", help="Reset budget")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.status:
        show_status()
    
    if args.should_explore:
        result = should_explore()
        print(f"\n{'🔬 EXPLORE' if result['should_explore'] else '⚡ EXPLOIT'}")
        print(f"   Exploration Rate: {result['exploration_rate']:.1%}")
        print(f"   Period Runs: {result['total_runs']} ({result['exploration_runs']} exploration)")
    
    if args.log_run:
        log_run(args.log_run[0], args.log_run[1])
    
    if args.report:
        generate_report()
    
    if args.reset:
        reset_budget()

if __name__ == "__main__":
    main()
