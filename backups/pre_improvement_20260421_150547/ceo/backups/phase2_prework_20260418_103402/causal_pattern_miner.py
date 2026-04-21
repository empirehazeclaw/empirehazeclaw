#!/usr/bin/env python3
"""
Causal Pattern Miner — Phase 1, Day 4
======================================
Entdeckt kausale Zusammenhänge zwischen Context-Faktoren und Outcomes.

Usage:
    python3 causal_pattern_miner.py --mine
    python3 causal_pattern_miner.py --chains [--limit 20]
    python3 causal_pattern_miner.py --query "<factor>"
    python3 causal_pattern_miner.py --stats
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict, Counter
from typing import Optional, List, Dict
import math

WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo")
MEMORY_DIR = WORKSPACE / "memory"
FAILURE_LOG = MEMORY_DIR / "failures" / "failure_log.json"
KG_DIR = MEMORY_DIR / "kg"
CAUSAL_DIR = MEMORY_DIR / "evaluations" / "causal"
CHAINS_FILE = CAUSAL_DIR / "causal_chains.json"
PATTERNS_FILE = CAUSAL_DIR / "causal_patterns.json"
STATS_FILE = CAUSAL_DIR / "causal_stats.json"

# Factor categories to analyze
FACTORS = [
    "time_bucket", "severity", "cause", "has_context", 
    "attempt", "user", "tags_count", "day_of_week"
]

def init_dirs():
    CAUSAL_DIR.mkdir(parents=True, exist_ok=True)
    if not CHAINS_FILE.exists():
        CHAINS_FILE.write_text(json.dumps({"chains": [], "version": "1.0"}))
    if not PATTERNS_FILE.exists():
        PATTERNS_FILE.write_text(json.dumps({"patterns": [], "version": "1.0"}))
    if not STATS_FILE.exists():
        STATS_FILE.write_text(json.dumps({
            "total_chains": 0, "total_patterns": 0, 
            "causal_accuracy": 0.0, "last_mine": None
        }))

def load_failures():
    if not FAILURE_LOG.exists():
        return []
    data = json.loads(FAILURE_LOG.read_text())
    return data.get("failures", [])

def load_chains():
    init_dirs()
    return json.loads(CHAINS_FILE.read_text())

def save_chains(data):
    CHAINS_FILE.write_text(json.dumps(data, indent=2))

def load_patterns():
    init_dirs()
    return json.loads(PATTERNS_FILE.read_text())

def save_patterns(data):
    PATTERNS_FILE.write_text(json.dumps(data, indent=2))

def load_stats():
    init_dirs()
    return json.loads(STATS_FILE.read_text())

def save_stats(data):
    STATS_FILE.write_text(json.dumps(data, indent=2))

def get_time_bucket(timestamp: str) -> str:
    """Bucket timestamp into time-of-day categories."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return f"{dt.hour:02d}:00"  # Hour bucket
    except:
        return "unknown"

def get_day_of_week(timestamp: str) -> str:
    """Get day of week."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[dt.weekday()]
    except:
        return "unknown"

def extract_factors(failure: dict) -> dict:
    """Extract causal factors from a failure."""
    ts = failure.get("timestamp", "")
    return {
        "time_bucket": get_time_bucket(ts),
        "day_of_week": get_day_of_week(ts),
        "severity": failure.get("severity", "unknown"),
        "cause": failure.get("cause", "unknown"),
        "has_context": bool(failure.get("context")),
        "attempt": failure.get("attempt", 1),
        "user": failure.get("context", {}).get("user", "system") if failure.get("context") else "system",
        "tags_count": len(failure.get("tags", [])),
        "resolution": "resolved" if failure.get("status") == "resolved" else "open"
    }

def extract_success_factors(task: dict) -> dict:
    """Extract factors from a successful task."""
    ts = task.get("timestamp", "")
    return {
        "time_bucket": get_time_bucket(ts),
        "day_of_week": get_day_of_week(ts),
        "severity": "none",
        "cause": "none",
        "has_context": bool(task.get("context")),
        "attempt": task.get("attempt", 1),
        "user": task.get("context", {}).get("user", "system") if task.get("context") else "system",
        "tags_count": len(task.get("tags", [])),
        "resolution": "success"
    }

def calculate_correlation(failures: list, factor: str) -> Dict[str, float]:
    """
    Calculate correlation between a factor and failure.
    Returns: {value: failure_rate}
    """
    factor_values = defaultdict(lambda: {"failures": 0, "total": 0})
    
    # Count failures by factor value
    for f in failures:
        factors = extract_factors(f)
        val = factors.get(factor, "unknown")
        factor_values[val]["failures"] += 1
        factor_values[val]["total"] += 1
    
    # Calculate failure rate
    result = {}
    for val, counts in factor_values.items():
        result[val] = counts["failures"] / max(counts["total"], 1)
    
    return result

def point_biserial_correlation(values: list, binary_outcome: list) -> float:
    """Calculate point-biserial correlation coefficient."""
    if len(values) != len(binary_outcome) or len(values) < 2:
        return 0.0
    
    mean_1 = sum(v for v, o in zip(values, binary_outcome) if o == 1) / max(sum(1 for o in binary_outcome if o == 1), 1)
    mean_0 = sum(v for v, o in zip(values, binary_outcome) if o == 0) / max(sum(1 for o in binary_outcome if o == 0), 1)
    
    n_1 = sum(1 for o in binary_outcome if o == 1)
    n_0 = sum(1 for o in binary_outcome if o == 0)
    n = len(values)
    
    if n_1 == 0 or n_0 == 0:
        return 0.0
    
    # Simplified: just return difference of means normalized
    std = math.sqrt(sum((v - (mean_1 + mean_0) / 2) ** 2 for v in values) / n)
    if std == 0:
        return 0.0
    
    return abs(mean_1 - mean_0) / std

def mine_causal_chains():
    """Mine causal chains from failure data."""
    print("🔍 Mining kausale Patterns...")
    
    failures = load_failures()
    if not failures:
        print("   ⚠️ Keine Failures gefunden. Causal Mining bringt nichts ohne Daten.")
        return
    
    chains_data = load_chains()
    patterns_data = load_patterns()
    
    # Calculate correlations for each factor
    all_factors = {}
    for factor in FACTORS:
        correlations = calculate_correlation(failures, factor)
        all_factors[factor] = correlations
        
        # Find significant patterns (failure rate > 50%)
        for val, rate in correlations.items():
            if rate > 0.5 and len(failures) >= 3:  # Only if we have enough data
                # Check if this is a real pattern or just noise
                pattern = {
                    "id": f"PAT-{len(patterns_data['patterns']) + 1:04d}",
                    "factor": factor,
                    "value": val,
                    "failure_rate": rate,
                    "sample_size": len(failures),
                    "confidence": min(rate, 1.0) * math.sqrt(len(failures) / 10),  # Rough confidence
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "examples": [
                        {"id": f["id"], "description": f["description"][:50]} 
                        for f in failures[:3]
                        if extract_factors(f).get(factor) == val
                    ]
                }
                
                # Only add if not duplicate
                existing = [p for p in patterns_data["patterns"] 
                           if p["factor"] == factor and p["value"] == val]
                if not existing:
                    patterns_data["patterns"].append(pattern)
    
    # Build causal chains (factor → outcome relationships)
    chains = []
    
    # Time-based chains
    time_rates = all_factors.get("time_bucket", {})
    if time_rates:
        max_time = max(time_rates.items(), key=lambda x: x[1])
        min_time = min(time_rates.items(), key=lambda x: x[1])
        
        if max_time[1] > min_time[1] * 1.5:  # Significant difference
            chains.append({
                "chain_id": f"CHAIN-{len(chains_data['chains']) + 1:04d}",
                "type": "temporal",
                "cause": f"time_bucket={max_time[0]}",
                "effect": "higher_failure_rate",
                "cause_value": max_time[1],
                "effect_value": f"{max_time[1]:.1%} failure rate",
                "comparison": f"{max_time[0]} ({max_time[1]:.1%}) vs {min_time[0]} ({min_time[1]:.1%})",
                "confidence": abs(max_time[1] - min_time[1]) * math.sqrt(len(failures)),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
    
    # Cause-based chains
    cause_rates = all_factors.get("cause", {})
    if cause_rates:
        top_causes = sorted(cause_rates.items(), key=lambda x: -x[1])[:3]
        for cause, rate in top_causes:
            if rate > 0.3:
                chains.append({
                    "chain_id": f"CHAIN-{len(chains_data['chains']) + 1:04d}",
                    "type": "cause_distribution",
                    "cause": f"cause={cause}",
                    "effect": "failure_contribution",
                    "cause_value": rate,
                    "effect_value": f"{rate:.1%} of all failures",
                    "comparison": f"Top 3: {', '.join([f'{c}({r:.1%})' for c, r in top_causes])}",
                    "confidence": rate * math.sqrt(len(failures)),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    # Add new chains
    existing_chain_ids = {c["chain_id"] for c in chains_data["chains"]}
    for chain in chains:
        if chain["chain_id"] not in existing_chain_ids:
            chains_data["chains"].append(chain)
    
    save_chains(chains_data)
    save_patterns(patterns_data)
    
    # Update stats
    stats = load_stats()
    stats["total_chains"] = len(chains_data["chains"])
    stats["total_patterns"] = len(patterns_data["patterns"])
    
    # Calculate causal accuracy (based on pattern confidence)
    if patterns_data["patterns"]:
        avg_confidence = sum(p["confidence"] for p in patterns_data["patterns"]) / len(patterns_data["patterns"])
        stats["causal_accuracy"] = min(avg_confidence, 1.0)
    
    stats["last_mine"] = datetime.now(timezone.utc).isoformat()
    save_stats(stats)
    
    print(f"   ✅ {len(chains)} neue Chains, {len(patterns_data['patterns'])} totale Patterns")
    print(f"   📊 Causal Accuracy: {stats['causal_accuracy']:.1%}")

def show_chains(limit: int = 20):
    """Show causal chains."""
    data = load_chains()
    chains = sorted(data["chains"], key=lambda x: x.get("confidence", 0), reverse=True)[:limit]
    
    if not chains:
        print("📭 Keine Causal Chains gefunden. Starte --mine zuerst.")
        return
    
    print(f"\n⛓️ Causal Chains ({len(chains)} von {len(data['chains'])} angezeigt)\n")
    for c in chains:
        conf = c.get("confidence", 0)
        bar = "█" * int(conf * 10) if conf else "░"
        print(f"  [{c.get('type', 'unknown'):15}] {c.get('chain_id', 'N/A')}")
        print(f"     Cause: {c.get('cause', 'N/A')}")
        print(f"     Effect: {c.get('effect', 'N/A')}")
        print(f"     Comparison: {c.get('comparison', 'N/A')}")
        print(f"     Confidence: {conf:.2f} {bar}")
        print()

def query_factor(factor: str):
    """Query patterns for a specific factor."""
    patterns = load_patterns()
    matching = [p for p in patterns["patterns"] if factor.lower() in p.get("factor", "").lower()]
    
    if not matching:
        print(f"📭 Keine Patterns für Factor '{factor}' gefunden.")
        return
    
    print(f"\n🔍 Patterns für '{factor}':\n")
    for p in sorted(matching, key=lambda x: -x.get("failure_rate", 0)):
        print(f"  [{p['factor']}:{p['value']}]")
        print(f"     Failure Rate: {p.get('failure_rate', 0):.1%}")
        print(f"     Confidence: {p.get('confidence', 0):.2f}")
        print(f"     Examples: {len(p.get('examples', []))}")
        print()

def show_stats():
    """Show causal mining statistics."""
    stats = load_stats()
    
    print("\n📊 Causal Mining Stats")
    print("=" * 40)
    print(f"  Total Chains:     {stats['total_chains']}")
    print(f"  Total Patterns:    {stats['total_patterns']}")
    print(f"  Causal Accuracy:  {stats['causal_accuracy']:.1%}")
    print(f"  Last Mine:         {stats.get('last_mine', 'Never')}")
    
    # Factor breakdown
    patterns = load_patterns()
    by_factor = defaultdict(int)
    for p in patterns["patterns"]:
        by_factor[p.get("factor", "unknown")] += 1
    
    if by_factor:
        print("\n  By Factor:")
        for f, c in sorted(by_factor.items(), key=lambda x: -x[1]):
            print(f"    {f:15} {c}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Causal Pattern Miner")
    parser.add_argument("--mine", action="store_true", help="Mine causal patterns")
    parser.add_argument("--chains", action="store_true", help="Show causal chains")
    parser.add_argument("--query", help="Query patterns for a factor")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--limit", type=int, default=20, help="Limit for --chains")
    
    args = parser.parse_args()
    
    if args.mine:
        mine_causal_chains()
    elif args.chains:
        show_chains(args.limit)
    elif args.query:
        query_factor(args.query)
    elif args.stats:
        show_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
