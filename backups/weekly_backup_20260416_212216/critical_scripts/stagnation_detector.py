#!/usr/bin/env python3
"""
Stagnation Detector — CEO System Health Monitor
==============================================
Monitors the event bus for stagnation patterns:
- Same gene selected repeatedly by Evolver
- Same improvement validated repeatedly
- KG not growing
- No new patterns discovered

Usage:
  python3 stagnation_detector.py --check evolver
  python3 stagnation_detector.py --check learning_loop
  python3 stagnation_detector.py --check kg

Phase 3 of System Integration Plan
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
EVENT_BUS = WORKSPACE / "data" / "events" / "events.jsonl"

def get_recent_events(minutes: int = 240) -> list:
    """Get events from last N minutes."""
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

def check_evolvers_stagnation(events: list) -> dict:
    """Check if Evolver is selecting the same gene repeatedly."""
    evolver_events = [e for e in events if e.get("source") == "capability_evolver"]
    
    # Group by gene/pattern
    gene_counts = Counter()
    for evt in evolver_events:
        data = evt.get("data", {})
        gene = data.get("gene", data.get("selected_gene", "unknown"))
        gene_counts[gene] += 1
    
    stagnant_genes = {g: c for g, c in gene_counts.items() if c >= 3}
    
    return {
        "stagnant": len(stagnant_genes) > 0,
        "stagnant_genes": stagnant_genes,
        "total_evolver_events": len(evolver_events),
        "recommendation": "Switch gene strategy" if stagnant_genes else "OK"
    }

def check_learning_loop_stagnation(events: list) -> dict:
    """Check if Learning Loop is producing same improvements."""
    pattern_events = [e for e in events if e.get("type") == "pattern_discovered"]
    improvement_events = [e for e in events if e.get("type") == "improvement_applied"]
    
    # Check for repeated patterns
    pattern_ids = [e.get("data", {}).get("pattern_id") for e in pattern_events]
    repeated_patterns = {p: c for p, c in Counter(pattern_ids).items() if c >= 3 and p}
    
    # Check for repeated improvements
    improvement_titles = [e.get("data", {}).get("title", "")[:50] for e in improvement_events]
    repeated_improvements = {t: c for t, c in Counter(improvement_titles).items() if c >= 3 and t}
    
    return {
        "stagnant": len(repeated_patterns) > 0 or len(repeated_improvements) > 0,
        "repeated_patterns": repeated_patterns,
        "repeated_improvements": repeated_improvements,
        "total_pattern_events": len(pattern_events),
        "total_improvement_events": len(improvement_events),
        "recommendation": "Increase mutation rate" if repeated_patterns else "OK"
    }

def check_kg_growth(events: list) -> dict:
    """Check if KG is growing."""
    kg_events = [e for e in events if e.get("type") == "kg_update"]
    
    growth_events = [e for e in kg_events if e.get("data", {}).get("action") in ["add", "merge", "sync"]]
    prune_events = [e for e in kg_events if e.get("data", {}).get("action") == "prune"]
    
    return {
        "kg_events_24h": len(kg_events),
        "growth_events": len(growth_events),
        "prune_events": len(prune_events),
        "stagnant": len(growth_events) == 0 and len(kg_events) > 0,
        "recommendation": "Trigger KG update" if len(growth_events) == 0 and len(kg_events) > 0 else "OK"
    }

def check_event_diversity(events: list) -> dict:
    """Check if events are diverse or repetitive."""
    event_types = [e.get("type") for e in events]
    sources = [e.get("source") for e in events]
    
    type_counter = Counter(event_types)
    source_counter = Counter(sources)
    
    # If >50% of events are same type, it's not diverse
    total = len(events)
    most_common_type_pct = type_counter.most_common(1)[0][1] / total if total > 0 else 0
    most_common_source_pct = source_counter.most_common(1)[0][1] / total if total > 0 else 0
    
    return {
        "unique_types": len(type_counter),
        "unique_sources": len(source_counter),
        "type_diversity": len(type_counter) / total if total > 0 else 0,
        "low_diversity": most_common_type_pct > 0.8 if total > 0 else False,
        "recommendation": "Add more event sources" if most_common_type_pct > 0.8 else "OK"
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=["evolver", "learning_loop", "kg", "diversity", "all"], default="all")
    parser.add_argument("--minutes", type=int, default=240)
    args = parser.parse_args()
    
    events = get_recent_events(args.minutes)
    print(f"Checking last {args.minutes} minutes: {len(events)} events\n")
    
    if args.check in ["evolver", "all"]:
        r = check_evolvers_stagnation(events)
        print(f"[Evolver Stagnation] {'⚠️ STAGNANT' if r['stagnant'] else '✅ OK'}")
        if r['stagnant']:
            print(f"  Repeated genes: {r['stagnant_genes']}")
        print(f"  Recommendation: {r['recommendation']}\n")
    
    if args.check in ["learning_loop", "all"]:
        r = check_learning_loop_stagnation(events)
        print(f"[Learning Loop Stagnation] {'⚠️ STAGNANT' if r['stagnant'] else '✅ OK'}")
        if r['stagnant']:
            print(f"  Repeated patterns: {r.get('repeated_patterns', {})}")
            print(f"  Repeated improvements: {r.get('repeated_improvements', {})}")
        print(f"  Recommendation: {r['recommendation']}\n")
    
    if args.check in ["kg", "all"]:
        r = check_kg_growth(events)
        print(f"[KG Growth] {'⚠️ STAGNANT' if r['stagnant'] else '✅ Growing'}")
        print(f"  Growth events: {r['growth_events']}, Prune events: {r['prune_events']}")
        print(f"  Recommendation: {r['recommendation']}\n")
    
    if args.check in ["diversity", "all"]:
        r = check_event_diversity(events)
        print(f"[Event Diversity] {'⚠️ Low' if r['low_diversity'] else '✅ Good'}")
        print(f"  Unique types: {r['unique_types']}, Unique sources: {r['unique_sources']}")
        print(f"  Recommendation: {r['recommendation']}\n")
