#!/usr/bin/env python3
"""
Evolver Signal Bridge — CEO Phase 4
===================================
Bridges our Event Bus signals to the Capability Evolver.
Reads from Event Bus, KG state, Learning Loop state → generates fresh signals for Evolver.

This breaks the stagnation loop by feeding real system data as signals.

Usage:
  python3 evolver_signal_bridge.py --check-stagnation
  python3 evolver_signal_bridge.py --run-with-signals
  python3 evolver_signal_bridge.py --post-evolver-results

Phase 4 of System Integration Plan
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
EVENT_BUS = WORKSPACE / "data/events/events.jsonl"
STATE_FILE = WORKSPACE / "data/learning_loop/kg_sync_state.json"
EVOLVER_STATE = WORKSPACE / "skills/capability-evolver/memory/evolution/evolution_solidify_state.json"
GENE_HISTORY = WORKSPACE / "data/evolver_gene_history.json"

# Gene cooldown config
GENE_COOLDOWN_RUNS = 3  # If gene selected in last 3 runs, skip it
GENE_HISTORY_SIZE = 5   # Track last 5 gene selections

def get_recent_genes_from_state() -> list:
    """Get recently selected genes from authoritative evolver state file."""
    genes = []
    if EVOLVER_STATE.exists():
        try:
            with open(EVOLVER_STATE) as f:
                state = json.load(f)
            last_run = state.get("last_run", {})
            gene = last_run.get("selected_gene_id", "unknown")
            if gene and gene != "unknown":
                genes.append(gene)
        except:
            pass
    return genes

def load_gene_history() -> list:
    """Load gene selection history."""
    history = []
    if GENE_HISTORY.exists():
        try:
            with open(GENE_HISTORY) as f:
                data = json.load(f)
            history = data.get("recent_genes", [])
        except:
            pass
    return history

def save_gene_selection(gene_id: str):
    """Save gene selection to history for cooldown tracking."""
    if not gene_id or gene_id == "unknown":
        return
    
    history = load_gene_history()
    history.insert(0, gene_id)
    history = history[:GENE_HISTORY_SIZE]
    
    with open(GENE_HISTORY, 'w') as f:
        json.dump({
            "recent_genes": history,
            "last_updated": datetime.now().isoformat()
        }, f, indent=2)

def get_genes_on_cooldown() -> set:
    """Get set of genes that are on cooldown (selected recently)."""
    history = load_gene_history()
    # If gene appears in last GENE_COOLDOWN_RUNS, it's on cooldown
    cooldown_genes = set(history[:GENE_COOLDOWN_RUNS])
    return cooldown_genes

def get_recent_events(minutes: int = 240) -> list:
    since = datetime.now() - timedelta(minutes=minutes)
    events = []
    if not EVENT_BUS.exists():
        return events
    with open(EVENT_BUS) as f:
        for line in f:
            try:
                evt = json.loads(line.strip())
                if datetime.fromisoformat(evt["timestamp"]) > since:
                    events.append(evt)
            except:
                pass
    return events

def get_kg_state() -> dict:
    with open(KG_PATH) as f:
        kg = json.load(f)
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    return {
        "entities": len(entities),
        "relations": len(relations),
        "types": list(set(e.get("type") for e in entities.values())),
    }

def get_learning_state() -> dict:
    state = {}
    state_file = WORKSPACE / "data/learning_loop_state.json"
    if state_file.exists():
        with open(state_file) as f:
            state = json.load(f)
    
    patterns_file = WORKSPACE / "data/learning_loop/patterns.json"
    patterns = []
    if patterns_file.exists():
        with open(patterns_file) as f:
            patterns = json.load(f).get("patterns", [])
    
    return {
        "iterations": state.get("iteration", 0),
        "patterns": len(patterns),
        "score": state.get("score", 0),
    }

def analyze_stagnation() -> dict:
    """Analyze if systems are stagnant and generate escape signals."""
    events = get_recent_events(240)
    kg = get_kg_state()
    learning = get_learning_state()
    
    signals = []
    recommendations = []
    
    # Check Evolver stagnation - use authoritative state file
    genes_from_state = get_recent_genes_from_state()
    if genes_from_state:
        # Count occurrences (would be 1 if we only track latest)
        gene_counts = Counter(genes_from_state)
        most_common_gene = gene_counts.most_common(1)[0]
        if most_common_gene[1] >= 3:
            signals.append("evolution_stagnation_detected")
            signals.append(f"gene_{most_common_gene[0]}_repeated_{most_common_gene[1]}x")
            recommendations.append(f"Switch from {most_common_gene[0]} to gene_gep_repair_from_errors")
    else:
        # Fallback to event bus for backward compatibility
        evolver_events = [e for e in events if e.get("source") == "capability_evolver"]
        gene_counts = Counter()
        for evt in evolver_events:
            data = evt.get("data", {})
            gene = data.get("gene", data.get("selected_gene", "unknown"))
            # Filter out buggy "unknown" entries
            if gene != "unknown":
                gene_counts[gene] += 1
        if gene_counts:
            most_common_gene = gene_counts.most_common(1)[0]
            if most_common_gene[1] >= 3:
                signals.append("evolution_stagnation_detected")
                signals.append(f"gene_{most_common_gene[0]}_repeated_{most_common_gene[1]}x")
                recommendations.append(f"Switch from {most_common_gene[0]} to gene_gep_repair_from_errors")
    
    # Gene diversity enforcement (cooldown logic)
    cooldown_genes = get_genes_on_cooldown()
    if cooldown_genes:
        signals.append("gene_diversity_enforced")
        signals.append(f"cooldown_genes: {','.join(cooldown_genes)}")
        recommendations.append(f"Genes on cooldown (skip these): {', '.join(cooldown_genes)}")
    
    # Check KG stagnation (not growing)
    kg_events = [e for e in events if e.get("type") == "kg_update"]
    growth_events = [e for e in kg_events if e.get("data", {}).get("action") in ["add", "merge", "sync"]]
    if len(growth_events) == 0 and len(kg_events) > 3:
        signals.append("kg_stagnation_detected")
        recommendations.append("KG needs new content - trigger Learning Loop sync")
    
    # Check Learning Loop stagnation
    improvement_events = [e for e in events if e.get("type") == "improvement_applied"]
    if len(improvement_events) >= 5:
        titles = [e.get("data", {}).get("title", "")[:50] for e in improvement_events]
        most_common_title = Counter(titles).most_common(1)[0]
        if most_common_title[1] >= 3:
            signals.append("learning_loop_stagnation")
            recommendations.append("Learning Loop repeating same improvements")
    
    # Check for performance bottleneck
    if learning.get("score", 1) < 0.7:
        signals.append("perf_bottleneck")
        recommendations.append("Learning Loop score low - investigate")
    
    # If KG has new types, signal capability_gap (weak signal - use as fallback only)
    if "LearningPattern" in kg.get("types", []) and "Improvement" in kg.get("types", []):
        signals.append("capability_gap")  # Fresh data available
    
    # === SMARTER FALLBACK: If no strong stagnation signals, use state-based fallbacks ===
    # capability_gap is weak - fallback runs when it's the only/primary signal
    stagnation_signals = [s for s in signals if s not in ["capability_gap", "gene_diversity_enforced"]]
    if not stagnation_signals:
        print("   [FALLBACK] No stagnation signals - using state-based fallbacks")
        
        # Get enriched KG state for orphan detection
        try:
            with open(KG_PATH) as f:
                kg_full = json.load(f)
            kg_ents = kg_full.get("entities", {})
            kg_rels = kg_full.get("relations", {})
            
            # Proper orphan detection (Top-Level relations format)
            linked = set()
            for r in kg_rels.values() if isinstance(kg_rels, dict) else []:
                if isinstance(r, dict):
                    linked.add(r.get("from"))
                    linked.add(r.get("to"))
            
            orphan_count = len(set(kg_ents.keys()) - linked) if isinstance(kg_ents, dict) else 0
            orphan_pct = orphan_count / len(kg_ents) if isinstance(kg_ents, dict) and len(kg_ents) > 0 else 0
            
            if orphan_pct > 0.35:
                signals.append("kg_relation_reconstruction")
                recommendations.append(f"KG orphan rate {orphan_pct:.1%} exceeds 35% - need relation reconstruction")
            
            # Get learning state for stagnation count
            lr_state_file = WORKSPACE / "data/learning_loop_state.json"
            if lr_state_file.exists():
                with open(lr_state_file) as f:
                    lr_state = json.load(f)
                
                stagnation_count = lr_state.get("lr_stagnation_count", 0)
                lr = lr_state.get("learning_rate", 0.1)
                score = lr_state.get("score", 0.5)
                score_history = lr_state.get("score_history", [])
                
                if stagnation_count >= 2:
                    signals.append("learning_lr_reduction")
                    recommendations.append(f"Learning stagnating ({stagnation_count}x), LR {lr:.3f} should be reduced")
                
                if len(score_history) >= 10:
                    recent_range = max(score_history[-10:]) - min(score_history[-10:])
                    if recent_range < 0.015:
                        signals.append("learning_plateau_escape")
                        recommendations.append(f"Score plateau detected (range={recent_range:.4f})")
                
                if score < 0.6:
                    signals.append("learning_low_performance")
                    recommendations.append(f"Learning score {score:.3f} below threshold - needs intervention")
        except Exception as e:
            print(f"   [FALLBACK ERROR] {e}")
        
        # Event diversity check
        event_types = set(e.get("type") for e in events)
        if len(event_types) < 5:
            signals.append("event_type_injection")
            recommendations.append(f"Low event diversity ({len(event_types)} types) - need more event sources")
        
        # If still no actionable signals, emit system diagnostic
        actionable = [s for s in signals if s not in ["capability_gap", "event_type_injection"]]
        if not actionable:
            signals.append("system_diagnostic_probe")
            recommendations.append("All metrics green - running capability probe for hidden opportunities")
    
    return {
        "signals": signals,
        "recommendations": recommendations,
        "kg_state": kg,
        "learning_state": learning,
        "event_count": len(events),
        "gene_cooldown": list(cooldown_genes),
    }

def run_evolver_with_signals():
    """Run the Evolver with fresh signals from our analysis."""
    analysis = analyze_stagnation()
    
    print("=== EVOLVER SIGNAL ANALYSIS ===")
    print(f"Events analyzed: {analysis['event_count']}")
    print(f"KG state: {analysis['kg_state']['entities']} entities, {analysis['kg_state']['relations']} relations")
    print(f"Learning Loop: iteration {analysis['learning_state'].get('iterations', 0)}, score {analysis['learning_state'].get('score', 0):.3f}")
    print(f"\nGenerated signals ({len(analysis['signals'])}):")
    for s in analysis['signals']:
        print(f"  - {s}")
    print(f"\nRecommendations:")
    for r in analysis['recommendations']:
        print(f"  - {r}")
    
    if not analysis['signals']:
        print("\n✅ No stagnation detected. Evolver would run normally.")
        return
    
    # Build signal string for Evolver
    signal_str = ",".join(analysis['signals'])
    print(f"\n=== RUNNING EVOLVER WITH SIGNALS ===")
    print(f"Signals: {signal_str}")
    
    # Run Evolver with custom strategy based on signals
    os.chdir("/home/clawbot/.openclaw/workspace/skills/capability-evolver")
    os.environ["A2A_NODE_ID"] = "node_39c27b8ba346"
    os.environ["EVOLVE_STRATEGY"] = "repair" if "evolution_stagnation_detected" in signal_str else "innovate"
    
    result = subprocess.run(
        ["node", "index.js"],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    print(f"\nEvolver output (last 50 lines):")
    lines = result.stdout.strip().split("\n")
    for line in lines[-50:]:
        print(line)
    
    if result.returncode != 0:
        print(f"\nEvolver stderr: {result.stderr[:500]}")
    
    return result.returncode == 0

def post_evolver_results():
    """After Evolver runs, post results to Event Bus."""
    # Read evolver output from memory/evolution
    evolver_state = WORKSPACE / "skills/capability-evolver/memory/evolution/evolution_solidify_state.json"
    if not evolver_state.exists():
        print("No evolver state found")
        return
    
    with open(evolver_state) as f:
        state = json.load(f)
    
    # Save gene to history for cooldown tracking
    gene_id = state.get("selected_gene_id", "unknown")
    save_gene_selection(gene_id)
    
    # Publish to event bus
    data = {
        "gene": gene_id,
        "outcome": state.get("outcome", {}).get("status", "unknown"),
        "score": state.get("outcome", {}).get("score", 0),
        "files_changed": state.get("execution_trace", {}).get("files_changed_count", 0),
    }
    
    import subprocess
    result = subprocess.run([
        "python3", str(WORKSPACE / "SCRIPTS/automation/event_bus.py"),
        "publish",
        "--type", "evolver_completed",
        "--source", "capability_evolver",
        "--severity", "info",
        "--data", json.dumps(data)
    ], capture_output=True, text=True)
    
    print(f"Published evolver result to event bus: {result.stdout.strip()}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-stagnation", action="store_true")
    parser.add_argument("--run-with-signals", action="store_true")
    parser.add_argument("--post-evolver-results", action="store_true")
    args = parser.parse_args()
    
    if args.check_stagnation:
        analysis = analyze_stagnation()
        print(json.dumps(analysis, indent=2, default=str))
    elif args.run_with_signals:
        run_evolver_with_signals()
    elif args.post_evolver_results:
        post_evolver_results()
    else:
        parser.print_help()
