#!/usr/bin/env python3
"""
Data Agent — Sir HazeClaw Multi-Agent Architecture
=================================================
Dedicated analytics + learning support agent.

Role: Analyst — Learning Loop execution, KG quality, Metrics
Trigger: Cron (stündlich) + Event-basiert

Usage:
    python3 data_agent.py --collect      # Collect learning signals
    python3 data_agent.py --metrics     # Update metrics
    python3 data_agent.py --kg-maintain # KG quality maintenance
    python3 data_agent.py --full       # Full cycle

Phase 3 of Multi-Agent Architecture
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SCRIPTS_DIR = WORKSPACE / "SCRIPTS" / "automation"
DATA_DIR = WORKSPACE / "data"
EVENTS_DIR = DATA_DIR / "events"
LOGS_DIR = WORKSPACE / "logs"
KG_PATH = WORKSPACE / "ceo/memory/kg/knowledge_graph.json"
DATA_STATE_FILE = DATA_DIR / "data_agent_state.json"

# Config
KG_ORPHAN_THRESHOLD = 0.30  # 30% orphans = needs cleanup
LEARNING_LOG = DATA_DIR / "learning_loop" / "learning_log.json"

def log(msg: str, level: str = "INFO"):
    """Simple logging."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "data_agent.log"
    entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": msg
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def load_state() -> Dict:
    """Load data agent state."""
    if DATA_STATE_FILE.exists():
        try:
            return json.load(open(DATA_STATE_FILE))
        except:
            pass
    return {
        "last_cycle": None,
        "cycles_run": 0,
        "patterns_found": 0,
        "improvements_applied": 0,
        "kg_entities_added": 0,
        "kg_orphans_cleaned": 0,
    }

def save_state(state: Dict):
    """Save data agent state."""
    DATA_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_kg() -> Dict:
    """Load knowledge graph."""
    if KG_PATH.exists():
        try:
            return json.load(open(KG_PATH))
        except:
            return {"entities": {}, "relations": []}
    return {"entities": {}, "relations": []}

def save_kg(kg: Dict):
    """Save knowledge graph."""
    KG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2)

def collect_learning_signals() -> Dict:
    """Collect signals from various sources."""
    signals = {
        "timestamp": datetime.now().isoformat(),
        "feedback_count": 0,
        "pattern_count": 0,
        "sources": [],
    }
    
    # Check learning log
    if LEARNING_LOG.exists():
        try:
            content = json.load(open(LEARNING_LOG))
            signals['feedback_count'] = len(content.get('feedback', []))
            signals['sources'].append('learning_log')
        except:
            pass
    
    # Check event bus for learning events
    events_dir = EVENTS_DIR
    if events_dir.exists():
        recent_events = list(events_dir.glob("*.json"))[-20:]
        learning_events = [e for e in recent_events if 'learning' in e.name or 'kg_update' in e.name]
        signals['learning_events'] = len(learning_events)
        signals['sources'].append('event_bus')
    
    # Check heartbeat state for patterns
    heartbeat_state = DATA_DIR / "heartbeat-state.json"
    if heartbeat_state.exists():
        try:
            state = json.load(open(heartbeat_state))
            if 'knownIssues' in state:
                signals['known_issues'] = len(state['knownIssues'])
            if 'resolved' in state:
                signals['resolved_issues'] = len(state['resolved'])
        except:
            pass
    
    log(f"Collected {signals['feedback_count']} signals from {len(signals['sources'])} sources", "INFO")
    return signals

def find_patterns_in_signals(signals: Dict) -> List[Dict]:
    """Analyze signals for patterns."""
    patterns = []
    
    # Pattern: Many known issues = systemic problem
    if signals.get('known_issues', 0) > 5:
        patterns.append({
            "type": "systemic_issues",
            "description": f"High issue count: {signals['known_issues']} known",
            "severity": "HIGH",
            "recommendation": "Investigate root cause of recurring issues"
        })
    
    # Pattern: Many feedback but few patterns = learning gap
    if signals.get('feedback_count', 0) > 10 and signals.get('pattern_count', 0) < 2:
        patterns.append({
            "type": "learning_gap",
            "description": f"High feedback ({signals['feedback_count']}) but low pattern detection",
            "severity": "MEDIUM",
            "recommendation": "Improve pattern recognition or signal quality"
        })
    
    return patterns

def maintain_kg_quality(kg: Dict) -> Dict:
    """Maintain KG quality: orphan cleanup, consistency."""
    maintenance = {
        "timestamp": datetime.now().isoformat(),
        "orphans_found": 0,
        "orphans_cleaned": 0,
        "relations_fixed": 0,
        "entity_types": {},
    }
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    # Count entity types
    type_counts = defaultdict(int)
    for e in entities.values():
        etype = e.get('type', 'unknown')
        type_counts[etype] += 1
    maintenance['entity_types'] = dict(type_counts)
    
    # Find orphans (entities with no relations)
    entity_ids = set(entities.keys())
    related_ids = set()
    
    # Relations stored as dict with numeric keys → iterate values
    rels = relations.values() if isinstance(relations, dict) else relations
    
    for rel in rels:
        if isinstance(rel, dict):
            if rel.get('from'):
                related_ids.add(rel['from'])
            if rel.get('to'):
                related_ids.add(rel['to'])
    
    orphans = entity_ids - related_ids
    orphan_count = len(orphans)
    maintenance['orphans_found'] = orphan_count
    
    # Calculate orphan percentage
    total_entities = len(entity_ids)
    orphan_pct = orphan_count / total_entities if total_entities > 0 else 0
    maintenance['orphan_pct'] = orphan_pct
    
    # If orphan rate too high, flag for cleanup
    if orphan_pct > KG_ORPHAN_THRESHOLD:
        maintenance['needs_cleanup'] = True
        maintenance['recommendation'] = f"Orphan rate {orphan_pct:.1%} exceeds threshold {KG_ORPHAN_THRESHOLD:.1%}"
        log(f"KG Quality warning: {orphan_pct:.1%} orphans ({orphan_count}/{total_entities})", "WARN")
    else:
        maintenance['needs_cleanup'] = False
        maintenance['recommendation'] = f"Orphan rate {orphan_pct:.1%} within acceptable range"
    
    return maintenance

def get_learning_loop_score() -> float:
    """Get current Learning Loop score."""
    state_file = DATA_DIR / "learning_loop_state.json"
    if state_file.exists():
        try:
            state = json.load(open(state_file))
            return state.get('score', 0.0)
        except:
            pass
    return 0.0

def get_kg_stats() -> Dict:
    """Get KG statistics."""
    kg = load_kg()
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    return {
        'entity_count': len(entities),
        'relation_count': len(relations),
        'type_counts': defaultdict(int),
    }

def update_metrics() -> Dict:
    """Update metrics for dashboard."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "learning_loop_score": get_learning_loop_score(),
        "kg_entities": 0,
        "kg_relations": 0,
        "kg_orphan_rate": 0.0,
        "system_health": "unknown",
    }
    
    # KG stats
    kg = load_kg()
    kg_stats = get_kg_stats()
    metrics['kg_entities'] = kg_stats['entity_count']
    metrics['kg_relations'] = kg_stats['relation_count']
    
    # KG maintenance
    maint = maintain_kg_quality(kg)
    metrics['kg_orphan_rate'] = maint.get('orphan_pct', 0.0)
    
    # System health
    health_score = load_state()
    metrics['system_health'] = "healthy" if maint.get('orphan_pct', 1.0) < KG_ORPHAN_THRESHOLD else "degraded"
    
    return metrics

def run_full_cycle() -> Dict:
    """Run full data agent cycle."""
    state = load_state()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "signals_collected": 0,
        "patterns_found": 0,
        "metrics_updated": False,
        "kg_maintained": False,
    }
    
    # 1. Collect learning signals
    signals = collect_learning_signals()
    results['signals_collected'] = signals.get('feedback_count', 0)
    
    # 2. Find patterns
    patterns = find_patterns_in_signals(signals)
    results['patterns_found'] = len(patterns)
    
    # 3. Update metrics
    metrics = update_metrics()
    results['metrics_updated'] = True
    results['metrics'] = metrics
    
    # 4. KG maintenance
    kg = load_kg()
    maint = maintain_kg_quality(kg)
    results['kg_maintained'] = True
    results['kg_maintenance'] = maint
    
    # Update state
    state['last_cycle'] = datetime.now().isoformat()
    state['cycles_run'] += 1
    state['patterns_found'] += len(patterns)
    save_state(state)
    
    log(f"Data Agent cycle complete: {len(patterns)} patterns, {maint.get('orphan_pct', 0):.1%} orphans", "INFO")
    
    return results

def publish_event(event_type: str, data: Dict):
    """Publish event to event bus."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    event = {
        "type": event_type,
        "source": "data_agent",
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    event_file = EVENTS_DIR / f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(event_file, "w") as f:
        json.dump(event, f, indent=2)

def print_results(results: Dict):
    """Print data agent results."""
    print(f"\n📊 Data Agent — {results['timestamp']}")
    print("=" * 50)
    
    print(f"\n📥 Signals collected: {results['signals_collected']}")
    print(f"💡 Patterns found: {results['patterns_found']}")
    
    if 'metrics' in results:
        m = results['metrics']
        print(f"\n📈 Metrics:")
        print(f"   Learning Loop Score: {m.get('learning_loop_score', 0):.3f}")
        print(f"   KG Entities: {m.get('kg_entities', 0)}")
        print(f"   KG Relations: {m.get('kg_relations', 0)}")
        print(f"   KG Orphan Rate: {m.get('kg_orphan_rate', 0):.1%}")
        print(f"   System Health: {m.get('system_health', 'unknown')}")
    
    if 'kg_maintenance' in results:
        maint = results['kg_maintenance']
        print(f"\n🔧 KG Maintenance:")
        print(f"   Orphans found: {maint.get('orphans_found', 0)}")
        print(f"   Orphan rate: {maint.get('orphan_pct', 0):.1%}")
        print(f"   Needs cleanup: {'⚠️ YES' if maint.get('needs_cleanup') else '✅ NO'}")
        print(f"   Recommendation: {maint.get('recommendation', 'N/A')[:60]}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Data Agent')
    parser.add_argument('--collect', action='store_true', help='Collect learning signals')
    parser.add_argument('--metrics', action='store_true', help='Update metrics')
    parser.add_argument('--kg-maintain', action='store_true', help='KG quality maintenance')
    parser.add_argument('--full', action='store_true', help='Full cycle')
    args = parser.parse_args()
    
    if args.collect:
        signals = collect_learning_signals()
        print(f"📥 Collected {signals['feedback_count']} signals from {signals['sources']}")
    elif args.metrics:
        metrics = update_metrics()
        print(f"📈 Learning Loop Score: {metrics.get('learning_loop_score', 0):.3f}")
        print(f"📊 KG: {metrics.get('kg_entities', 0)} entities, {metrics.get('kg_relations', 0)} relations")
        print(f"🔧 Orphan Rate: {metrics.get('kg_orphan_rate', 0):.1%}")
    elif args.kg_maintain:
        kg = load_kg()
        maint = maintain_kg_quality(kg)
        print(f"🔧 KG Maintenance: {maint.get('orphans_found', 0)} orphans ({maint.get('orphan_pct', 0):.1%})")
        if maint.get('needs_cleanup'):
            print(f"⚠️ {maint.get('recommendation')}")
    elif args.full:
        results = run_full_cycle()
        print_results(results)
        publish_event('data_agent.completed', results)
    else:
        # Default: full cycle
        results = run_full_cycle()
        print_results(results)
        publish_event('data_agent.completed', results)

if __name__ == "__main__":
    main()
