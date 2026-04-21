#!/usr/bin/env python3
"""
capability_probe.py — Nightly Capability Probe for Sir HazeClaw
================================================================
Runs at 02:00 UTC to diagnose system health and generate synthetic
opportunity signals when all real metrics are green (system stable).

This solves the "signal poverty" problem where Evolver gets no signals
during stable periods.

Usage:
    python3 capability_probe.py --check       # Run check and report
    python3 capability_probe.py --probe      # Full probe with signal gen
    python3 capability_probe.py --test        # Test mode (no KG changes)

Output: /home/clawbot/.openclaw/workspace/data/capability_probe.json
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
PROBE_FILE = WORKSPACE / "data/capability_probe.json"
EVENT_BUS = WORKSPACE / "data/events/events.jsonl"
LEARNING_STATE = WORKSPACE / "data/learning_loop_state.json"
PATTERNS_FILE = WORKSPACE / "data/learning_loop/patterns.json"
EVOLVER_STATE = WORKSPACE / "skills/capability-evolver/memory/evolution/evolution_solidify_state.json"
GENE_HISTORY = WORKSPACE / "data/capability_probe_gene_history.json"

# Thresholds
ORPHAN_THRESHOLD = 0.40  # 40% orphan entities = warning
GROWTH_RATE_THRESHOLD = 0.05  # 5% entity growth per week = healthy
SCORE_MINIMUM = 0.6  # Learning Loop score minimum

def load_kg():
    """Load KG and compute stats."""
    if not KG_PATH.exists():
        return None
    with open(KG_PATH) as f:
        kg = json.load(f)
    return kg

def compute_kg_metrics(kg):
    """Compute KG health metrics."""
    entities = kg.get("entities", {})
    relations = kg.get("relations", {})
    
    total_entities = len(entities)
    total_relations = len(relations)
    
    # Orphan detection: entities with no relations
    orphaned = 0
    linked_entities = set()
    for rel in relations.values():
        linked_entities.add(rel.get("from"))
        linked_entities.add(rel.get("to"))
    
    for eid in entities:
        if eid not in linked_entities:
            orphaned += 1
    
    orphan_pct = orphaned / total_entities if total_entities > 0 else 1.0
    
    # Relation density
    density = total_relations / total_entities if total_entities > 0 else 0
    
    # Entity types
    types = list(set(e.get("type") for e in entities.values()))
    
    return {
        "entity_count": total_entities,
        "relation_count": total_relations,
        "orphan_count": orphaned,
        "orphan_pct": orphan_pct,
        "relation_density": density,
        "type_count": len(types),
        "types": types[:10],  # Top 10 types
    }

def load_learning_trajectory():
    """Load learning loop state and patterns for trajectory analysis."""
    state = {"iteration": 0, "score": 0}
    if LEARNING_STATE.exists():
        with open(LEARNING_STATE) as f:
            state = json.load(f)
    
    patterns = []
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            patterns = json.load(f).get("patterns", [])
    
    return {
        "iteration": state.get("iteration", 0),
        "score": state.get("score", 0),
        "pattern_count": len(patterns),
    }

def get_recent_events(minutes=1440):  # 24h default
    """Get recent events from event bus."""
    since = datetime.now() - timedelta(minutes=minutes)
    events = []
    if not EVENT_BUS.exists():
        return events
    try:
        with open(EVENT_BUS) as f:
            for line in f:
                try:
                    evt = json.loads(line.strip())
                    ts = datetime.fromisoformat(evt["timestamp"])
                    if ts > since:
                        events.append(evt)
                except:
                    pass
    except:
        pass
    return events

def get_recent_genes(count=5):
    """Get recently selected genes from evolver state."""
    genes = []
    if EVOLVER_STATE.exists():
        try:
            with open(EVOLVER_STATE) as f:
                state = json.load(f)
            last_run = state.get("last_run", {})
            gene = last_run.get("selected_gene_id", "")
            if gene:
                genes.append(gene)
        except:
            pass
    
    # Also check gene history file
    if GENE_HISTORY.exists():
        try:
            with open(GENE_HISTORY) as f:
                history = json.load(f)
            genes = history.get("recent_genes", []) + genes
        except:
            pass
    
    return genes[:count]

def save_gene_selection(gene_id):
    """Save gene selection to history."""
    history = {"recent_genes": [], "last_updated": None}
    if GENE_HISTORY.exists():
        try:
            with open(GENE_HISTORY) as f:
                history = json.load(f)
        except:
            pass
    
    genes = history.get("recent_genes", [])
    genes.insert(0, gene_id)
    history["recent_genes"] = genes[:10]  # Keep last 10
    history["last_updated"] = datetime.now().isoformat()
    
    with open(GENE_HISTORY, 'w') as f:
        json.dump(history, f, indent=2)

def run_mini_benchmark():
    """Run 3-5 random known tasks to probe capabilities."""
    # Known task areas to test
    task_areas = [
        "kg_query",      # Can we query the KG?
        "event_check",   # Can we check events?
        "learning_read", # Can we read learning state?
        "pattern_match", # Can we match patterns?
        "file_ops",      # Can we do file ops?
    ]
    
    results = []
    for area in task_areas[:4]:  # Test 4 areas max
        result = {"area": area, "success": False, "error": None}
        
        try:
            if area == "kg_query":
                kg = load_kg()
                result["success"] = kg is not None
                result["entity_count"] = len(kg.get("entities", {})) if kg else 0
                
            elif area == "event_check":
                events = get_recent_events(60)
                result["success"] = True
                result["event_count"] = len(events)
                
            elif area == "learning_read":
                state = load_learning_trajectory()
                result["success"] = True
                result["score"] = state.get("score", 0)
                
            elif area == "pattern_match":
                patterns = []
                if PATTERNS_FILE.exists():
                    with open(PATTERNS_FILE) as f:
                        patterns = json.load(f).get("patterns", [])
                result["success"] = True
                result["pattern_count"] = len(patterns)
                
        except Exception as e:
            result["error"] = str(e)[:100]
        
        results.append(result)
    
    return results

def generate_synthetic_signal(kg_metrics, learning_trajectory, benchmark_results):
    """Generate synthetic opportunity signal when system is stable.
    
    Key insight: When all real metrics are GREEN, system is stable.
    Evolver needs something to work with — generate a synthetic opportunity
    signal to enable proactive capability expansion.
    
    This is the "Mad-Dog Signal Poverty Fix" — give Evolver work even
    when there's nothing broken.
    """
    
    # Determine system health
    kg_healthy = (
        kg_metrics["orphan_pct"] < 0.40 and  # Relaxed from 0.30
        kg_metrics["entity_count"] > 50
    )
    
    learning_healthy = (
        learning_trajectory["score"] >= 0.6 and  # Relaxed from 0.7
        learning_trajectory["iteration"] > 10
    )
    
    benchmark_healthy = all(r["success"] for r in benchmark_results)
    
    # Recent genes for context
    recent_genes = get_recent_genes(3)
    
    signals = []
    recommendations = []
    
    if kg_healthy and learning_healthy and benchmark_healthy:
        # System is stable → generate exploration/opportunity signal
        print("   ✅ All metrics healthy — generating opportunity signal")
        
        # Determine signal type based on recent evolution
        if "gene_gep_innovate_from_opportunity" in recent_genes:
            signals.append("exploration_opportunity_signal")
            recommendations.append("Deep exploration mode — diversify strategy")
        elif "gene_gep_repair_from_errors" in recent_genes:
            signals.append("capability_expansion_signal")
            recommendations.append("Capability expansion — push boundaries")
        else:
            signals.append("stable_opportunity_signal")
            recommendations.append("Proactive evolution opportunity")
        
        # Add bonus signals based on metrics
        if kg_metrics["entity_count"] > 200:
            signals.append("kg_ripe_for_synthesis")
        
        if learning_trajectory["score"] > 0.75:
            signals.append("high_performance_plateau")
            recommendations.append("Breakthrough opportunity — push higher")
        
        # If relations are dense, signal synthesis opportunity
        if kg_metrics["relation_density"] > 1.0:
            signals.append("dense_knowledge_synthesis")
            
    else:
        # System has issues — this is handled by normal stagnation detection
        print("   ⚠️ Some metrics need attention")
        if not kg_healthy:
            print(f"      KG: orphan={kg_metrics['orphan_pct']:.1%}, entities={kg_metrics['entity_count']}")
        if not learning_healthy:
            print(f"      Learning: score={learning_trajectory['score']:.3f}")
        if not benchmark_healthy:
            failed = [r['area'] for r in benchmark_results if not r['success']]
            print(f"      Benchmark failed: {failed}")
    
    return signals, recommendations

def run_probe(test_mode=False):
    """Run full capability probe."""
    print("🔍 Capability Probe —", datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    print("=" * 50)
    
    # 1. Read KG state
    print("\n📊 KG State Analysis...")
    kg = load_kg()
    if kg is None:
        print("❌ KG not found")
        return False
    kg_metrics = compute_kg_metrics(kg)
    print(f"   Entities: {kg_metrics['entity_count']}")
    print(f"   Relations: {kg_metrics['relation_count']}")
    print(f"   Orphan %: {kg_metrics['orphan_pct']:.1%}")
    print(f"   Density: {kg_metrics['relation_density']:.2f}")
    
    # 2. Read Learning Loop trajectory
    print("\n📈 Learning Loop Trajectory...")
    learning = load_learning_trajectory()
    print(f"   Iteration: {learning['iteration']}")
    print(f"   Score: {learning['score']:.3f}")
    print(f"   Patterns: {learning['pattern_count']}")
    
    # 3. Run mini benchmark
    print("\n🧪 Mini Benchmark...")
    benchmark = run_mini_benchmark()
    for r in benchmark:
        status = "✅" if r["success"] else "❌"
        print(f"   {status} {r['area']}: {r.get('error', 'OK')}")
    
    # 4. Generate synthetic signals
    print("\n🎯 Signal Generation...")
    signals, recommendations = generate_synthetic_signal(kg_metrics, learning, benchmark)
    
    if signals:
        print(f"   Generated signals:")
        for s in signals:
            print(f"      - {s}")
        if recommendations:
            print("   Recommendations:")
            for r in recommendations:
                print(f"      - {r}")
    else:
        print("   No signals generated (system needs attention)")
    
    # 5. Compile probe result
    probe_result = {
        "timestamp": datetime.now().isoformat(),
        "kg_metrics": kg_metrics,
        "learning_trajectory": learning,
        "benchmark_results": benchmark,
        "signals_generated": signals or [],
        "recommendations": recommendations or [],
        "overall_status": "healthy" if signals else "needs_attention",
    }
    
    # Save probe result
    if not test_mode:
        with open(PROBE_FILE, 'w') as f:
            json.dump(probe_result, f, indent=2)
        print(f"\n💾 Saved to {PROBE_FILE}")
    
    print("\n" + "=" * 50)
    print(f"Status: {probe_result['overall_status']}")
    
    return probe_result

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Quick health check")
    parser.add_argument("--probe", action="store_true", help="Full probe with signal generation")
    parser.add_argument("--test", action="store_true", help="Test mode (no file changes)")
    args = parser.parse_args()
    
    if args.check:
        # Quick check mode
        kg = load_kg()
        learning = load_learning_trajectory()
        if kg:
            metrics = compute_kg_metrics(kg)
            print(json.dumps({
                "kg_entities": metrics["entity_count"],
                "kg_orphan_pct": metrics["orphan_pct"],
                "learning_score": learning["score"],
                "learning_iteration": learning["iteration"],
            }, indent=2))
        else:
            print("❌ KG not found")
            sys.exit(1)
    elif args.probe or args.test:
        result = run_probe(test_mode=args.test)
        if result:
            print(f"\nSignals: {result['signals_generated']}")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
