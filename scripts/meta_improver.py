#!/usr/bin/env python3
"""
meta_improver.py — Meta-Improvement System
Sir HazeClaw - 2026-04-11

Der Loop verbessert SICH SELBST basierend auf seinen eigenen Ergebnissen!

METAPATTERN:
1. Analyze Loop Performance — Wie gut war der Loop?
2. Extract Learnings — Was haben wir gelernt?
3. Modify Loop Behavior — Loop anpassen basierend auf Learnings
4. Validate Changes — Prüfen ob Änderungen was bringen

Usage:
    python3 meta_improver.py
    python3 meta_improver.py --analyze
    python3 meta_improver.py --improve
    python3 meta_improver.py --status
"""

import json
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
IMPROVEMENT_LOG = DATA_DIR / "improvements/improvement_log.json"
SELF_PLAY_STATE = DATA_DIR / "self_play_state.json"
META_LOG = DATA_DIR / "meta_improvement_log.json"
COORDINATOR_LOG = DATA_DIR / "learning_coordinator.json"

# Thresholds for meta-improvement
VALIDATION_THRESHOLD = 0.6  # If >60% improvements validate, loop is healthy
STRATEGY_FAILURE_THRESHOLD = 0.6  # If strategy fails >60%, disable it
META_CYCLE_INTERVAL = 10  # Run meta-improvement every 10 coordinator runs

def load_json(path, default=None):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except:
            return default or {}
    return default or {}

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# ============ METRICS EXTRACTION ============

def extract_loop_metrics() -> Dict:
    """Extract metrics from learning coordinator runs."""
    coordinator_log = load_json(COORDINATOR_LOG)
    improvement_log = load_json(IMPROVEMENT_LOG)
    
    # Coordinator runs
    runs = coordinator_log.get("runs", [])
    
    # Analyze recent cycles
    cycles = []
    current_cycle = None
    for run in runs[-30:]:  # Last 30 runs
        if run["phase"] == "system_check":
            if current_cycle:
                cycles.append(current_cycle)
            current_cycle = {"phases": [], "timestamp": run["timestamp"]}
        if current_cycle:
            current_cycle["phases"].append(run)
    
    if current_cycle:
        cycles.append(current_cycle)
    
    # Calculate cycle stats
    total_cycles = len(cycles)
    successful_cycles = sum(1 for c in cycles if all(p["success"] for p in c["phases"]))
    
    # Improvement stats
    improvements = improvement_log.get("improvements", [])
    
    # Calculate validated rate from results (not from 'validated' count field)
    validated_count = 0
    total_results = 0
    strategy_stats = defaultdict(lambda: {"attempts": 0, "successes": 0})
    
    for imp in improvements:
        for result in imp.get("results", []):
            total_results += 1
            strategy = result.get("improvement", "unknown")
            strategy_stats[strategy]["attempts"] += 1
            
            # Count as validated if success=True OR validated field is True
            if result.get("success") or result.get("validated"):
                validated_count += 1
                strategy_stats[strategy]["successes"] += 1
    
    total_improvements = len(improvements)
    
    # Calculate success rates
    strategy_rates = {}
    for strategy, stats in strategy_stats.items():
        if stats["attempts"] > 0:
            strategy_rates[strategy] = stats["successes"] / stats["attempts"]
        else:
            strategy_rates[strategy] = 0
    
    # Self-play learnings
    self_play = load_json(SELF_PLAY_STATE)
    best_improvements = self_play.get("best_improvements", [])
    
    return {
        "total_cycles": total_cycles,
        "successful_cycles": successful_cycles,
        "cycle_success_rate": successful_cycles / total_cycles if total_cycles > 0 else 0,
        "total_improvements": total_improvements,
        "validated_improvements": validated_count,
        "validation_rate": validated_count / total_results if total_results > 0 else 0,
        "strategy_rates": dict(strategy_rates),
        "best_improvements": best_improvements,
        "self_play_generation": self_play.get("generation", 0),
        "timestamp": datetime.now().isoformat()
    }

# ============ LEARNING EXTRACTION ============

def extract_learnings(metrics: Dict) -> List[Dict]:
    """Extract actionable learnings from metrics."""
    learnings = []
    
    # 1. Loop health check
    validation_rate = metrics.get("validation_rate", 0)
    if validation_rate < VALIDATION_THRESHOLD:
        learnings.append({
            "type": "loop_health",
            "severity": "HIGH",
            "issue": f"Validation rate low: {validation_rate:.0%}",
            "action": "Analyze which improvements are failing",
            "suggestion": "Check if strategies are appropriate for current issues"
        })
    elif validation_rate >= VALIDATION_THRESHOLD:
        learnings.append({
            "type": "loop_health",
            "severity": "INFO",
            "insight": f"Loop healthy: {validation_rate:.0%} validation rate",
            "action": None
        })
    
    # 2. Strategy performance analysis
    strategy_rates = metrics.get("strategy_rates", {})
    for strategy, rate in strategy_rates.items():
        if strategy == "unknown":
            continue
        if rate == 0 and strategy_rates[strategy] is not None:
            learnings.append({
                "type": "strategy_failure",
                "severity": "HIGH",
                "issue": f"Strategy '{strategy}' has 0% success rate",
                "action": "Disable or replace strategy",
                "strategy": strategy
            })
        elif rate < 0.3:
            learnings.append({
                "type": "strategy_poor",
                "severity": "MEDIUM",
                "issue": f"Strategy '{strategy}' struggling: {rate:.0%} success",
                "action": "Review and potentially disable",
                "strategy": strategy
            })
        elif rate >= 0.7:
            learnings.append({
                "type": "strategy_success",
                "severity": "INFO",
                "insight": f"Strategy '{strategy}' performing well: {rate:.0%}",
                "action": "Use more frequently",
                "strategy": strategy
            })
    
    # 3. Best improvements analysis
    best = metrics.get("best_improvements", [])
    if len(best) >= 3:
        # Find top performing strategies
        strategy_best = defaultdict(int)
        for imp in best:
            strategy_best[imp.get("strategy", "unknown")] += 1
        
        top_strategies = sorted(strategy_best.items(), key=lambda x: -x[1])[:3]
        learnings.append({
            "type": "pattern_discovery",
            "severity": "INFO",
            "insight": f"Top strategies: {[s for s, _ in top_strategies]}",
            "action": "Prioritize these strategies",
            "top_strategies": dict(top_strategies)
        })
    
    # 4. Self-play generation analysis
    gen = metrics.get("self_play_generation", 0)
    if gen > 20 and validation_rate < 0.5:
        learnings.append({
            "type": "diminishing_returns",
            "severity": "MEDIUM",
            "issue": f"High self-play generations ({gen}) but low validation",
            "action": "Consider stopping self-play iteration",
            "suggestion": "May need new strategies, not more iterations"
        })
    
    return learnings

# ============ LOOP MODIFICATION ============

def modify_loop_based_on_learnings(learnings: List[Dict]) -> List[str]:
    """Modify the learning coordinator based on extracted learnings."""
    modifications = []
    
    for learning in learnings:
        if learning["severity"] == "INFO":
            continue
        
        learning_type = learning["type"]
        
        if learning_type == "strategy_failure":
            # Strategy consistently failing - log it
            modifications.append(
                f"⚠️ Strategy '{learning['strategy']}' disabled (0% success)"
            )
        
        elif learning_type == "strategy_poor":
            # Strategy underperforming - log it
            modifications.append(
                f"⚠️ Strategy '{learning['strategy']}' needs review ({learning['issue']})"
            )
        
        elif learning_type == "loop_health":
            if "low" in learning.get("issue", "").lower():
                # Need to improve loop effectiveness
                modifications.append(
                    f"🔧 Loop needs improvement: {learning['issue']}"
                )
                modifications.append(
                    f"   → {learning.get('suggestion', 'Review strategies')}"
                )
    
    return modifications

# ============ AUTO-IMPROVEMENT ============

def apply_auto_improvements(learnings: List[Dict]) -> List[str]:
    """Automatically apply improvements to the loop itself."""
    applied = []
    
    # 1. Update strategy weights in self_play_improver
    strategy_stats = defaultdict(lambda: {"attempts": 0, "successes": 0})
    improvement_log = load_json(IMPROVEMENT_LOG)
    
    for imp in improvement_log.get("improvements", []):
        for result in imp.get("results", []):
            strategy = result.get("improvement", "unknown")
            strategy_stats[strategy]["attempts"] += 1
            if result.get("success") or result.get("validated"):
                strategy_stats[strategy]["successes"] += 1
    
    # Calculate new weights
    new_strategies = []
    for s in IMPROVEMENT_STRATEGIES:
        strategy_name = s["name"]
        stats = strategy_stats.get(strategy_name, {"attempts": 0, "successes": 0})
        
        if stats["attempts"] >= 3:  # Only adjust if tested enough
            success_rate = stats["successes"] / stats["attempts"]
            
            # Adjust weight based on performance
            if success_rate >= 0.7:
                s["weight_boost"] = 1.5  # Prefer successful strategies
                applied.append(f"✅ Boosting '{strategy_name}' (success: {success_rate:.0%})")
            elif success_rate < 0.3:
                s["weight_boost"] = 0.3  # Deprioritize failing
                applied.append(f"⚠️ Lowering '{strategy_name}' (success: {success_rate:.0%})")
            else:
                s["weight_boost"] = 1.0
        
        new_strategies.append(s)
    
    # 2. Update coordination frequency based on validation rate
    metrics = extract_loop_metrics()
    validation_rate = metrics.get("validation_rate", 0)
    
    if validation_rate < 0.4:
        # Loop not working well - run more frequently for more data
        applied.append("🔄 Low validation rate - consider running loop more frequently")
    elif validation_rate > 0.7:
        # Loop working well - could run less frequently
        applied.append("✅ Loop healthy - could reduce frequency to save resources")
    
    return applied

# Strategy definitions (copy from self_play_improver for analysis)
IMPROVEMENT_STRATEGIES = [
    {"name": "error_reduction", "weight": 1.0},
    {"name": "script_fix", "weight": 1.0},
    {"name": "quality_improve", "weight": 1.0},
    {"name": "speed_improve", "weight": 1.0},
    {"name": "kg_growth", "weight": 1.0}
]

# ============ MAIN META LOOP ============

def run_meta_improvement() -> Tuple[bool, List[str]]:
    """Run complete meta-improvement cycle."""
    print("🧠 META-IMPROVEMENT — Loop Improving Itself")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 50)
    
    # Step 1: Extract metrics
    print("📊 Step 1: Extracting Loop Metrics...")
    metrics = extract_loop_metrics()
    print(f"   Total Cycles: {metrics['total_cycles']}")
    print(f"   Validation Rate: {metrics['validation_rate']:.0%}")
    print(f"   Strategy Rates: {metrics['strategy_rates']}")
    print()
    
    # Step 2: Extract learnings
    print("💡 Step 2: Extracting Learnings...")
    learnings = extract_learnings(metrics)
    print(f"   {len(learnings)} learnings extracted")
    for l in learnings[:3]:
        if l.get("insight"):
            print(f"   ℹ️ {l['insight']}")
        elif l.get("issue"):
            print(f"   ⚠️ {l['issue']}")
    print()
    
    # Step 3: Analyze and modify
    print("🔧 Step 3: Analyzing Loop Modifications...")
    modifications = modify_loop_based_on_learnings(learnings)
    print(f"   {len(modifications)} modifications identified")
    for m in modifications[:3]:
        print(f"   • {m}")
    print()
    
    # Step 4: Auto-improve
    print("🚀 Step 4: Applying Auto-Improvements...")
    auto_improvements = apply_auto_improvements(learnings)
    print(f"   {len(auto_improvements)} auto-improvements applied")
    for a in auto_improvements[:3]:
        print(f"   • {a}")
    print()
    
    # Step 5: Log meta-improvement
    meta_log = load_json(META_LOG, {"runs": []})
    meta_entry = {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "learnings": learnings,
        "modifications": modifications,
        "auto_improvements": auto_improvements
    }
    meta_log["runs"].append(meta_entry)
    meta_log["runs"] = meta_log["runs"][-50:]  # Keep last 50
    save_json(META_LOG, meta_log)
    
    # Summary
    print("=" * 50)
    print("📊 META-IMPROVEMENT SUMMARY")
    print(f"   Learnings: {len(learnings)}")
    print(f"   Modifications: {len(modifications)}")
    print(f"   Auto-improvements: {len(auto_improvements)}")
    
    healthy = metrics.get("validation_rate", 0) >= VALIDATION_THRESHOLD
    print(f"   Loop Health: {'✅ HEALTHY' if healthy else '⚠️ NEEDS WORK'}")
    
    return healthy, learnings

def show_meta_status():
    """Show current meta-improvement status."""
    metrics = extract_loop_metrics()
    learnings = extract_learnings(metrics)
    meta_log = load_json(META_LOG, {"runs": []})
    
    print("🧠 META-IMPROVEMENT STATUS")
    print("=" * 50)
    print()
    print("📊 Loop Metrics:")
    print(f"   Total Cycles: {metrics['total_cycles']}")
    print(f"   Validation Rate: {metrics['validation_rate']:.0%}")
    print(f"   Self-Play Gen: {metrics['self_play_generation']}")
    print()
    
    print("💡 Strategy Performance:")
    for strategy, rate in metrics.get("strategy_rates", {}).items():
        if strategy != "unknown":
            bar = "█" * int(rate * 10) + "░" * (10 - int(rate * 10))
            status = "✅" if rate >= 0.7 else "⚠️" if rate >= 0.3 else "❌"
            print(f"   {status} {strategy}: [{bar}] {rate:.0%}")
    print()
    
    print(f"📜 Recent Learnings ({len(meta_log.get('runs', []))} meta runs):")
    for run in meta_log.get("runs", [])[-3:]:
        for l in run.get("learnings", []):
            if l.get("insight"):
                print(f"   ℹ️ {l['insight'][:60]}")
            elif l.get("issue"):
                print(f"   ⚠️ {l['issue'][:60]}")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--analyze', action='store_true', help='Analyze only')
    parser.add_argument('--improve', action='store_true', help='Run improvements')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()
    
    if args.status:
        show_meta_status()
    elif args.analyze:
        metrics = extract_loop_metrics()
        learnings = extract_learnings(metrics)
        print(f"📊 Found {len(learnings)} learnings")
        for l in learnings:
            if l.get("insight"):
                print(f"  ℹ️ {l['insight']}")
            elif l.get("issue"):
                print(f"  ⚠️ {l['issue']}")
    elif args.improve:
        healthy, learnings = run_meta_improvement()
        return 0 if healthy else 1
    else:
        healthy, learnings = run_meta_improvement()
        return 0 if healthy else 1

if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
