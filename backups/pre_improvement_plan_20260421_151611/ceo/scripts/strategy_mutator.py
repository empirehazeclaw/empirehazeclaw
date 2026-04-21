#!/usr/bin/env python3
"""
Strategy Mutator — Phase 3, Day 2
==================================
Mutates existing meta-patterns and strategies to create variations for exploration.

Mutations:
- Change execution strategy
- Change timeout values
- Change delegation patterns
- Modify context handling
- Adjust retry logic

Usage:
    python3 strategy_mutator.py --list              # List available strategies
    python3 strategy_mutator.py --mutate <name>  # Create mutation of strategy
    python3 strategy_mutator.py --test <mut_id>  # Test a mutation
    python3 strategy_mutator.py --report          # Mutation performance report
    python3 strategy_mutator.py --baseline       # Set baseline for comparison
"""

import json
import argparse
import sys
import random
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MUTATIONS_DIR = WORKSPACE / "memory" / "evaluations" / "strategy_mutations"
BASELINE_FILE = MUTATIONS_DIR / "baseline.json"
MUTATIONS_FILE = MUTATIONS_DIR / "mutations.json"
MUTATION_LOG = MUTATIONS_DIR / "mutation_log.json"

# Mutation types
MUTATION_TYPES = [
    "timeout_adjust",
    "delegation_change",
    "context_expansion",
    "context_truncation",
    "retry_increase",
    "retry_decrease",
    "parallel_execution",
    "sequential_execution",
    "aggressive_optimization",
    "conservative_approach"
]

# Default strategies to mutate
DEFAULT_STRATEGIES = {
    "default_execution": {
        "type": "execution",
        "timeout": 30,
        "retries": 3,
        "delegation": "auto",
        "context_mode": "full",
        "parallel": False
    },
    "quick_task": {
        "type": "execution",
        "timeout": 10,
        "retries": 1,
        "delegation": "none",
        "context_mode": "minimal",
        "parallel": False
    },
    "complex_task": {
        "type": "execution",
        "timeout": 120,
        "retries": 5,
        "delegation": "full",
        "context_mode": "full",
        "parallel": True
    },
    "delegation_only": {
        "type": "delegation",
        "timeout": 60,
        "retries": 2,
        "delegation": "forced",
        "context_mode": "full",
        "parallel": False
    },
    "direct_execution": {
        "type": "execution",
        "timeout": 45,
        "retries": 3,
        "delegation": "none",
        "context_mode": "full",
        "parallel": False
    }
}

def init_dirs():
    MUTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not BASELINE_FILE.exists():
        BASELINE_FILE.write_text(json.dumps({"baseline": {}, "set_at": datetime.now(timezone.utc).isoformat()}))
    
    if not MUTATIONS_FILE.exists():
        MUTATIONS_FILE.write_text(json.dumps({"mutations": [], "version": "1.0"}))
    
    if not MUTATION_LOG.exists():
        MUTATION_LOG.write_text(json.dumps({"tests": [], "version": "1.0"}))

def load_mutations():
    init_dirs()
    return json.loads(MUTATIONS_FILE.read_text())

def save_mutations(data):
    MUTATIONS_FILE.write_text(json.dumps(data, indent=2))

def load_baseline():
    init_dirs()
    return json.loads(BASELINE_FILE.read_text())

def save_baseline(data):
    BASELINE_FILE.write_text(json.dumps(data, indent=2))

def load_mutation_log():
    init_dirs()
    return json.loads(MUTATION_LOG.read_text())

def save_mutation_log(data):
    MUTATION_LOG.write_text(json.dumps(data, indent=2))

def mutate_strategy(strategy_name: str, mutation_type: str = None) -> dict:
    """Create a mutated version of a strategy."""
    mutations = load_mutations()
    baseline = load_baseline()
    
    # Get base strategy
    if strategy_name in baseline.get("baseline", {}):
        base = baseline["baseline"][strategy_name]
    elif strategy_name in DEFAULT_STRATEGIES:
        base = DEFAULT_STRATEGIES[strategy_name]
    else:
        print(f"[!] Strategy '{strategy_name}' not found.")
        return None
    
    # If no mutation type specified, pick one intelligently
    if not mutation_type:
        # Pick based on current strategy properties
        if base.get("timeout", 30) < 30:
            mutation_type = random.choice(["timeout_adjust", "retry_increase", "context_expansion"])
        elif base.get("timeout", 30) > 60:
            mutation_type = random.choice(["timeout_adjust", "conservative_approach"])
        elif base.get("parallel"):
            mutation_type = random.choice(["sequential_execution", "context_truncation"])
        else:
            mutation_type = random.choice(MUTATION_TYPES)
    
    # Create mutation
    mutation = apply_mutation(base, mutation_type)
    
    # Add metadata
    mutation_id = f"MUT-{len(mutations['mutations']) + 1:04d}"
    mutation_record = {
        "id": mutation_id,
        "parent": strategy_name,
        "mutation_type": mutation_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "strategy": mutation,
        "test_results": [],
        "status": "pending"
    }
    
    mutations["mutations"].append(mutation_record)
    save_mutations(mutations)
    
    print(f"[*] Created mutation {mutation_id}: {strategy_name} + {mutation_type}")
    print(f"    New strategy: {mutation}")
    
    return mutation_record

def apply_mutation(strategy: dict, mutation_type: str) -> dict:
    """Apply a specific mutation to a strategy."""
    mutated = strategy.copy()
    
    if mutation_type == "timeout_adjust":
        # Adjust timeout by ±50%
        current = mutated.get("timeout", 30)
        factor = random.choice([0.5, 0.75, 1.5, 2.0])
        mutated["timeout"] = max(5, int(current * factor))
        mutated["timeout_note"] = f"Adjusted from {current}s by factor {factor}"
    
    elif mutation_type == "delegation_change":
        options = ["auto", "none", "forced", "adaptive"]
        current = mutated.get("delegation", "auto")
        options.remove(current)
        mutated["delegation"] = random.choice(options)
        mutated["delegation_note"] = f"Changed from {current}"
    
    elif mutation_type == "context_expansion":
        mode = mutated.get("context_mode", "full")
        if mode == "minimal":
            mutated["context_mode"] = "full"
        elif mode == "full":
            mutated["context_mode"] = "expanded"
        mutated["context_expanded"] = True
    
    elif mutation_type == "context_truncation":
        mode = mutated.get("context_mode", "full")
        if mode == "expanded":
            mutated["context_mode"] = "full"
        elif mode == "full":
            mutated["context_mode"] = "minimal"
        mutated["context_truncated"] = True
    
    elif mutation_type == "retry_increase":
        current = mutated.get("retries", 3)
        mutated["retries"] = min(current + 2, 10)
        mutated["retry_note"] = f"Increased from {current}"
    
    elif mutation_type == "retry_decrease":
        current = mutated.get("retries", 3)
        mutated["retries"] = max(current - 1, 0)
        mutated["retry_note"] = f"Decreased from {current}"
    
    elif mutation_type == "parallel_execution":
        mutated["parallel"] = True
        mutated["parallel_max"] = random.randint(2, 5)
        mutated["execution_note"] = "Made parallel"
    
    elif mutation_type == "sequential_execution":
        mutated["parallel"] = False
        mutated["sequential"] = True
        mutated["execution_note"] = "Made sequential"
    
    elif mutation_type == "aggressive_optimization":
        mutated["timeout"] = int(mutated.get("timeout", 30) * 0.7)
        mutated["retries"] = max(mutated.get("retries", 3) - 1, 1)
        mutated["optimization"] = "aggressive"
        mutated["optimization_note"] = "Aggressive optimization applied"
    
    elif mutation_type == "conservative_approach":
        mutated["timeout"] = int(mutated.get("timeout", 30) * 1.5)
        mutated["retries"] = mutated.get("retries", 3) + 1
        mutated["optimization"] = "conservative"
        mutated["optimization_note"] = "Conservative approach applied"
    
    return mutated

def list_strategies():
    """List available strategies."""
    baseline = load_baseline()
    mutations = load_mutations()
    
    print("\n📋 Available Strategies\n" + "=" * 50)
    
    print("\nDefault Strategies:")
    for name, strat in DEFAULT_STRATEGIES.items():
        print(f"  • {name}: timeout={strat.get('timeout')}s, retries={strat.get('retries')}, delegation={strat.get('delegation')}")
    
    if baseline.get("baseline"):
        print("\nBaseline Strategies (from KG):")
        for name, strat in baseline["baseline"].items():
            print(f"  • {name}: {strat}")
    
    if mutations["mutations"]:
        print(f"\nMutations ({len(mutations['mutations'])} total):")
        pending = sum(1 for m in mutations["mutations"] if m["status"] == "pending")
        tested = sum(1 for m in mutations["mutations"] if m["status"] == "tested")
        print(f"  Pending: {pending} | Tested: {tested}")
        
        for m in mutations["mutations"][-5:]:
            status_icon = "⏳" if m["status"] == "pending" else "✅" if m["status"] == "success" else "❌"
            print(f"  {status_icon} {m['id']}: {m['parent']} + {m['mutation_type']}")
            if m.get("test_results"):
                avg = sum(m["test_results"]) / len(m["test_results"])
                print(f"       Avg score: {avg:.2f}")

def log_test_result(mutation_id: str, success: bool, score: float = None, metrics: dict = None):
    """Log the result of testing a mutation."""
    mutations = load_mutations()
    mutation_log = load_mutation_log()
    
    for m in mutations["mutations"]:
        if m["id"] == mutation_id:
            m["test_results"].append(score if score is not None else (1.0 if success else 0.0))
            m["status"] = "tested"
            if success:
                m["status"] = "success"
            
            # Add to log
            mutation_log["tests"].append({
                "mutation_id": mutation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": success,
                "score": score,
                "metrics": metrics or {}
            })
            
            save_mutations(mutations)
            save_mutation_log(mutation_log)
            
            print(f"[*] Logged test result for {mutation_id}: success={success}, score={score}")
            return
    
    print(f"[!] Mutation {mutation_id} not found.")

def set_baseline(strategy_name: str = None, from_kg: bool = False):
    """Set baseline strategies for comparison."""
    baseline = load_baseline()
    
    if from_kg:
        # Load strategies from KG
        kg_path = WORKSPACE / "memory" / "kg" / "knowledge_graph.json"
        if kg_path.exists():
            kg = json.loads(kg_path.read_text())
            strategies = {}
            
            for name, entity in kg.get("entities", {}).items():
                if entity.get("type") in ["strategy", "meta_pattern", "execution_strategy"]:
                    strategies[name] = entity.get("facts", [{}])[0] if entity.get("facts") else {}
            
            baseline["baseline"] = strategies
            baseline["set_at"] = datetime.now(timezone.utc).isoformat()
            baseline["source"] = "kg"
            save_baseline(baseline)
            print(f"[*] Loaded {len(strategies)} strategies from KG as baseline.")
            return
    
    if strategy_name:
        if strategy_name in DEFAULT_STRATEGIES:
            baseline["baseline"][strategy_name] = DEFAULT_STRATEGIES[strategy_name]
            save_baseline(baseline)
            print(f"[*] Added {strategy_name} to baseline.")
        else:
            print(f"[!] Strategy {strategy_name} not found in defaults.")
    else:
        # Use defaults as baseline
        baseline["baseline"] = DEFAULT_STRATEGIES.copy()
        baseline["set_at"] = datetime.now(timezone.utc).isoformat()
        baseline["source"] = "defaults"
        save_baseline(baseline)
        print(f"[*] Set default strategies as baseline ({len(DEFAULT_STRATEGIES)} strategies).")

def compare_to_baseline(mutation_id: str) -> dict:
    """Compare a mutation's performance to baseline."""
    mutations = load_mutations()
    baseline = load_baseline()
    
    mutation = next((m for m in mutations["mutations"] if m["id"] == mutation_id), None)
    if not mutation:
        return None
    
    parent_name = mutation["parent"]
    if parent_name not in baseline["baseline"]:
        return {"error": f"Parent strategy '{parent_name}' not in baseline"}
    
    parent_strat = baseline["baseline"][parent_name]
    mutation_strat = mutation["strategy"]
    
    # Calculate average score
    scores = mutation.get("test_results", [])
    avg_score = sum(scores) / len(scores) if scores else 0.5
    
    # Compare key properties
    comparison = {
        "mutation_id": mutation_id,
        "parent": parent_name,
        "mutation_type": mutation["mutation_type"],
        "avg_score": avg_score,
        "test_count": len(scores),
        "changes": {
            "timeout": f"{parent_strat.get('timeout')} -> {mutation_strat.get('timeout')}",
            "retries": f"{parent_strat.get('retries')} -> {mutation_strat.get('retries')}",
            "delegation": f"{parent_strat.get('delegation')} -> {mutation_strat.get('delegation')}",
        }
    }
    
    return comparison

def generate_report():
    """Generate mutation performance report."""
    mutations = load_mutations()
    baseline = load_baseline()
    
    if not mutations["mutations"]:
        print("[*] No mutations yet.")
        return
    
    print("\n📈 Strategy Mutation Report\n" + "=" * 50)
    
    # Aggregate stats
    total = len(mutations["mutations"])
    pending = sum(1 for m in mutations["mutations"] if m["status"] == "pending")
    tested = sum(1 for m in mutations["mutations"] if m["status"] == "tested")
    successful = sum(1 for m in mutations["mutations"] if m["status"] == "success")
    
    print(f"\nOverview:")
    print(f"  Total Mutations: {total}")
    print(f"  Pending: {pending}")
    print(f"  Tested: {tested}")
    print(f"  Successful: {successful}")
    
    # Best mutations
    mutations_with_scores = [m for m in mutations["mutations"] if m.get("test_results")]
    if mutations_with_scores:
        print(f"\nTop 5 Mutations (by avg score):")
        for m in sorted(mutations_with_scores, key=lambda x: -sum(x["test_results"])/len(x["test_results"]))[:5]:
            avg = sum(m["test_results"]) / len(m["test_results"])
            print(f"  {m['id']}: {avg:.2f} ({m['parent']} + {m['mutation_type']})")
    
    # By mutation type
    by_type = defaultdict(list)
    for m in mutations_with_scores:
        avg = sum(m["test_results"]) / len(m["test_results"])
        by_type[m["mutation_type"]].append(avg)
    
    print(f"\nBy Mutation Type:")
    for mtype, scores in sorted(by_type.items(), key=lambda x: -sum(x[1])/len(x[1])):
        avg = sum(scores) / len(scores)
        print(f"  {mtype}: {avg:.2f} avg ({len(scores)} tests)")
    
    # Save report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_mutations": total,
        "pending": pending,
        "tested": tested,
        "successful": successful,
        "top_mutations": [
            {
                "id": m["id"],
                "avg_score": sum(m["test_results"]) / len(m["test_results"]),
                "parent": m["parent"],
                "mutation_type": m["mutation_type"]
            }
            for m in sorted(mutations_with_scores, key=lambda x: -sum(x["test_results"])/len(x["test_results"]))[:5]
        ],
        "by_mutation_type": {
            mtype: sum(scores) / len(scores)
            for mtype, scores in by_type.items()
        }
    }
    
    report_file = WORKSPACE / "docs" / "mutation_report.json"
    report_file.write_text(json.dumps(report, indent=2))
    print(f"\n📄 Report saved: {report_file}")
    
    return report

def main():
    parser = argparse.ArgumentParser(description="Strategy Mutator")
    parser.add_argument("--list", action="store_true", help="List available strategies and mutations")
    parser.add_argument("--mutate", metavar="NAME", help="Create mutation of a strategy")
    parser.add_argument("--mutation-type", metavar="TYPE", help="Specify mutation type")
    parser.add_argument("--test", metavar="ID", help="Log test result for mutation")
    parser.add_argument("--success", metavar="ID", help="Mark mutation as successful")
    parser.add_argument("--score", type=float, help="Score for mutation test")
    parser.add_argument("--report", action="store_true", help="Generate mutation report")
    parser.add_argument("--baseline", action="store_true", help="Set default strategies as baseline")
    parser.add_argument("--baseline-kg", action="store_true", help="Load baseline from KG")
    
    args = parser.parse_args()
    
    init_dirs()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.list:
        list_strategies()
    
    if args.mutate:
        mutate_strategy(args.mutate, args.mutation_type)
    
    if args.test:
        log_test_result(args.test, args.success is not None, args.score)
    
    if args.report:
        generate_report()
    
    if args.baseline:
        set_baseline()
    
    if args.baseline_kg:
        set_baseline(from_kg=True)

if __name__ == "__main__":
    main()
