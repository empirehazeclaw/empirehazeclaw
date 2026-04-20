#!/usr/bin/env python3
"""
Evolver Stagnation Breaker — CEO Phase 4
========================================
Forces gene diversity when Evolver is in stagnation.
Runs after Capability Evolver, checks for repeated genes, forces different strategy.

Usage:
  python3 evolver_stagnation_breaker.py --check
  python3 evolver_stagnation_breaker.py --force-switch

Phase 4 of System Integration Plan
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVOLVER_STATE = WORKSPACE / "skills/capability-evolver/memory/evolution/evolution_solidify_state.json"
EVENTS_FILE = WORKSPACE / "data/events/events.jsonl"

# Known genes and their "opposite" strategies
GENE_STRATEGIES = {
    "gene_gep_innovate_from_opportunity": "repair",
    "gene_gep_repair_from_errors": "innovate",
    "gene_gep_optimize_prompt_and_assets": "innovate",
    "gene_auto_default": "innovate",
}

def get_recent_genes(count: int = 10) -> list:
    """Get recently selected genes from event bus + state file."""
    genes = []
    
    # Primary: read from evolver state file (authoritative)
    if EVOLVER_STATE.exists():
        try:
            with open(EVOLVER_STATE) as f:
                state = json.load(f)
            last_run = state.get("last_run", {})
            gene = last_run.get("selected_gene_id", "unknown")
            if gene != "unknown":
                genes.append(gene)
        except:
            pass
    
    # Fallback: read from event bus (may have stale "unknown" entries)
    if not genes and EVENTS_FILE.exists():
        cutoff = datetime.now().timestamp() - (7 * 24 * 3600)  # Last 7 days
        with open(EVENTS_FILE) as f:
            for line in f:
                try:
                    evt = json.loads(line.strip())
                    ts = datetime.fromisoformat(evt["timestamp"]).timestamp()
                    if ts < cutoff:
                        continue
                    if evt.get("type") in ["evolver_completed", "gene_selected"]:
                        gene = evt.get("data", {}).get("gene", "unknown")
                        # Filter out "unknown" from old buggy events
                        if gene != "unknown":
                            genes.append(gene)
                except:
                    pass
    
    return genes

def check_stagnation() -> dict:
    """Check if Evolver is in stagnation."""
    genes = get_recent_genes(10)
    
    if not genes:
        return {"stagnant": False, "reason": "No recent gene data"}
    
    counter = Counter(genes)
    most_common = counter.most_common(1)[0]
    
    return {
        "stagnant": most_common[1] >= 3,
        "repeated_gene": most_common[0] if most_common[1] >= 3 else None,
        "repeat_count": most_common[1],
        "all_genes": dict(counter),
        "recommendation": _get_recommendation(most_common) if most_common[1] >= 3 else "OK"
    }

def _get_recommendation(most_common: tuple) -> str:
    gene, count = most_common
    strategy = GENE_STRATEGIES.get(gene, "repair")
    return f"Force switch from {gene} to {strategy} strategy"

def force_switch() -> dict:
    """Force a strategy switch by publishing a stagnation event."""
    stagnation = check_stagnation()
    
    if not stagnation["stagnant"]:
        return {"action": "none", "reason": "No stagnation detected"}
    
    gene = stagnation["repeated_gene"]
    new_strategy = GENE_STRATEGIES.get(gene, "repair")
    
    # Publish stagnation event with force signal
    result = subprocess.run([
        "python3", str(WORKSPACE / "scripts/event_bus.py"),
        "publish",
        "--type", "stagnation_escaped",
        "--source", "stagnation_breaker",
        "--severity", "warning",
        "--data", json.dumps({
            "forced_gene": gene,
            "new_strategy": new_strategy,
            "action": "force_strategy_switch"
        })
    ], capture_output=True, text=True)
    
    return {
        "action": "switch",
        "from_gene": gene,
        "to_strategy": new_strategy,
        "event_id": result.stdout.strip() if result.returncode == 0 else None
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--force-switch", action="store_true")
    args = parser.parse_args()
    
    if args.check:
        result = check_stagnation()
        print(json.dumps(result, indent=2, default=str))
    elif args.force_switch:
        result = force_switch()
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()
