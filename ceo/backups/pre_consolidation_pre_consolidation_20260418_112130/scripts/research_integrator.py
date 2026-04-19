#!/usr/bin/env python3
"""
research_integrator.py — Integrate Innovation Research into Knowledge Graph
Sir HazeClaw - 2026-04-17

Reads research findings from innovation_research_log.json,
extracts actionable insights, and adds them to the KG.
Can trigger evolver signals based on findings.

Usage:
    python3 research_integrator.py              # Integrate latest research
    python3 research_integrator.py --all        # Integrate all research
    python3 research_integrator.py --dry-run    # Show what would be integrated
    python3 research_integrator.py --signal     # Trigger evolver signals
"""

import json
import re
from datetime import datetime
from pathlib import Path
import sys

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
RESEARCH_LOG = WORKSPACE / "data" / "innovation_research_log.json"
KG_PATH = WORKSPACE / "ceo/memory/kg" / "knowledge_graph.json"
EVOLVER_SIGNAL_FILE = WORKSPACE / "data" / "evolver_signals.json"
INTEGRATION_STATE = WORKSPACE / "ceo/memory/procedural" / "research_integration_state.json"

# Innovation keywords that suggest actionable insights
ACTIONABLE_KEYWORDS = [
    "self-improv", "self-modif", "self-adapt", "autonomous",
    "evolv", "learn", "optimize", "improv",
    "multi-agent", "collaborat", "emergent",
    "反思", "recursive", "meta-learn", "hyper"
]

# High-impact patterns for evolver signals
HIGH_IMPACT_PATTERNS = [
    r"self-improving",
    r"self-evolv",
    r"autonomous.*learn",
    r"recursive.*improv",
    r"multi-agent.*emerg",
    r"meta-learn",
]


def load_research_log():
    """Load the full research log."""
    if not RESEARCH_LOG.exists():
        return {"entries": [], "last_full_research": None}
    with open(RESEARCH_LOG) as f:
        return json.load(f)


def load_kg():
    """Load the knowledge graph."""
    if not KG_PATH.exists():
        return {"entities": {}, "relations": [], "last_updated": None}
    with open(KG_PATH) as f:
        return json.load(f)


def save_kg(kg):
    """Save the knowledge graph."""
    KG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)


def load_integration_state():
    """Load state to avoid re-integrating same research."""
    if INTEGRATION_STATE.exists():
        with open(INTEGRATION_STATE) as f:
            return json.load(f)
    return {"integrated_timestamps": [], "last_integration": None}


def save_integration_state(state):
    """Save integration state."""
    INTEGRATION_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(INTEGRATION_STATE, 'w') as f:
        json.dump(state, f, indent=2)


def is_actionable(text):
    """Check if research text contains actionable insights."""
    if not text:
        return False
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in ACTIONABLE_KEYWORDS)


def extract_actionable_insights(results):
    """Extract actionable insights from research results."""
    insights = []
    for r in results:
        if 'paper' in r:
            paper = r['paper']
            title = paper.get('title', '')
            summary = paper.get('summary', '')
            url = paper.get('url', '')
            published = paper.get('published', '')
            
            full_text = f"{title} {summary}"
            if is_actionable(full_text):
                insights.append({
                    "type": "arXiv_paper",
                    "title": title,
                    "summary": summary[:300] if summary else '',
                    "url": url,
                    "published": published,
                    "query": r.get('query', ''),
                    "actionable": True
                })
        elif 'discussion' in r:
            disc = r['discussion']
            title = disc.get('title', '')
            url = disc.get('url', '')
            points = disc.get('points', 0)
            
            if is_actionable(title) or points > 10:
                insights.append({
                    "type": "HN_discussion",
                    "title": title,
                    "url": url,
                    "points": points,
                    "query": r.get('query', ''),
                    "actionable": is_actionable(title)
                })
    return insights


def add_research_to_kg(kg, insights, timestamp, mode):
    """Add research findings as KG entities."""
    # Use timestamp to create unique entity_id (not datetime.now() which causes collisions)
    # Replace colons and dashes, keep just numbers and letters
    ts_clean = timestamp.replace(':', '').replace('-', '').replace('T', '_').split('.')[0]
    entity_id = f"research_finding_{ts_clean}"
    
    facts = []
    for insight in insights:
        fact = {
            "type": insight['type'],
            "title": insight['title'],
            "query": insight.get('query', ''),
            "actionable": insight.get('actionable', False),
            "integrated_at": datetime.now().isoformat()
        }
        if insight['type'] == 'arXiv_paper':
            fact["summary"] = insight.get('summary', '')
            fact["url"] = insight.get('url', '')
            fact["published"] = insight.get('published', '')
        elif insight['type'] == 'HN_discussion':
            fact["url"] = insight.get('url', '')
            fact["points"] = insight.get('points', 0)
        facts.append(fact)
    
    entity = {
        "type": "research_finding",
        "category": "ai_agent_innovation",
        "facts": facts,
        "metadata": {
            "source_timestamp": timestamp,
            "mode": mode,
            "insights_count": len(insights),
            "actionable_count": sum(1 for i in insights if i.get('actionable'))
        },
        "created": datetime.now().isoformat(),
        "tags": ["innovation", "research", "ai_agent", "integrated"]
    }
    
    kg['entities'][entity_id] = entity
    
    # Add relation to research category
    # Handle both dict and list formats for relations
    existing_relations = kg.get('relations', {})
    if isinstance(existing_relations, dict):
        # Dict format: use next numeric key
        next_key = str(len(existing_relations))
        existing_relations[next_key] = {
            "from": entity_id,
            "to": "category_ai_agent_innovation",
            "type": "belongs_to",
            "created": datetime.now().isoformat()
        }
        kg['relations'] = existing_relations
    elif isinstance(existing_relations, list):
        # List format: append
        kg['relations'].append({
            "from": entity_id,
            "to": "category_ai_agent_innovation",
            "type": "belongs_to",
            "created": datetime.now().isoformat()
        })
    
    return entity_id, len(insights)


def generate_evolver_signals(insights):
    """Generate evolver signals from high-impact findings."""
    signals = []
    
    for insight in insights:
        if not insight.get('actionable'):
            continue
        
        title = insight.get('title', '').lower()
        summary = insight.get('summary', '').lower()
        text = f"{title} {summary}"
        
        for pattern in HIGH_IMPACT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                signals.append({
                    "type": "research_inspired",
                    "pattern_matched": pattern,
                    "source": insight.get('type', 'unknown'),
                    "title": insight.get('title', '')[:100],
                    "priority": "HIGH" if insight.get('actionable') else "MEDIUM",
                    "created": datetime.now().isoformat()
                })
                break  # One signal per insight max
    
    return signals


def add_signals_to_evolver(signals):
    """Add signals to evolver signal queue."""
    existing = []
    if EVOLVER_SIGNAL_FILE.exists():
        with open(EVOLVER_SIGNAL_FILE) as f:
            existing = json.load(f)
    
    if not isinstance(existing, list):
        existing = []
    
    existing.extend(signals)
    
    EVOLVER_SIGNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVOLVER_SIGNAL_FILE, 'w') as f:
        json.dump(existing, f, indent=2)
    
    return len(signals)


def integrate_research(all_entries=False, dry_run=False, trigger_signals=False):
    """Main integration logic."""
    log = load_research_log()
    kg = load_kg()
    state = load_integration_state()
    
    entries = log.get('entries', [])
    integrated_timestamps = set(state.get('integrated_timestamps', []))
    
    # Filter entries to integrate
    if all_entries:
        entries_to_integrate = entries
    else:
        # Only latest entry
        entries_to_integrate = [entries[-1]] if entries else []
    
    # Remove already integrated
    entries_to_integrate = [
        e for e in entries_to_integrate 
        if e['timestamp'] not in integrated_timestamps
    ]
    
    if not entries_to_integrate:
        print("✅ No new research to integrate")
        return
    
    print(f"📊 Found {len(entries_to_integrate)} entries to integrate")
    
    total_insights = 0
    total_actionable = 0
    all_signals = []
    integrated_titles = set()  # Dedupe by title
    
    for entry in entries_to_integrate:
        timestamp = entry['timestamp']
        mode = entry.get('mode', 'unknown')
        results = entry.get('results', [])
        
        # Extract actionable insights
        insights = extract_actionable_insights(results)
        
        # Deduplicate: skip insights we've already integrated (same title)
        unique_insights = []
        for i in insights:
            title = i.get('title', '')
            if title and title not in integrated_titles:
                integrated_titles.add(title)
                unique_insights.append(i)
        insights = unique_insights
        
        actionable = sum(1 for i in insights if i.get('actionable'))
        
        # Skip entries with no unique actionable insights
        if actionable == 0:
            if not dry_run:
                print(f"   ⏭ Skipping {timestamp[:19]} - 0 actionable insights")
            continue
        
        if dry_run:
            print(f"\n📄 {timestamp[:19]} | {mode}")
            print(f"   Results: {len(results)} | Actionable: {actionable}")
            for i in insights[:3]:
                print(f"   - [{i['type']}] {i.get('title','')[:60]}...")
            continue
        
        # Add to KG
        entity_id, count = add_research_to_kg(kg, insights, timestamp, mode)
        total_insights += count
        total_actionable += actionable
        
        # Generate signals
        signals = generate_evolver_signals(insights)
        all_signals.extend(signals)
        
        # Update state
        integrated_timestamps.add(timestamp)
        
        print(f"✅ {timestamp[:19]} | {mode}")
        print(f"   KG entity: {entity_id}")
        print(f"   Insights: {count} (actionable: {actionable})")
        print(f"   Signals: {len(signals)}")
    
    if dry_run:
        print(f"\n📊 Would integrate {len(entries_to_integrate)} entries")
        print(f"   Total insights: {total_insights}")
        print(f"   Total signals: {len(all_signals)}")
        return
    
    # Save KG
    kg['last_updated'] = datetime.now().isoformat()
    save_kg(kg)
    
    # Update state
    state['integrated_timestamps'] = list(integrated_timestamps)
    state['last_integration'] = datetime.now().isoformat()
    save_integration_state(state)
    
    # Add signals to evolver
    signals_added = 0
    if trigger_signals and all_signals:
        signals_added = add_signals_to_evolver(all_signals)
    
    print(f"\n{'='*50}")
    print(f"✅ Integration complete")
    print(f"   Entries processed: {len(entries_to_integrate)}")
    print(f"   Total insights: {total_insights}")
    print(f"   Actionable: {total_actionable}")
    print(f"   Signals to evolver: {signals_added}")


def main():
    all_entries = "--all" in sys.argv
    dry_run = "--dry-run" in sys.argv
    trigger_signals = "--signal" in sys.argv
    
    print("🔬 Innovation Research Integrator")
    print(f"   Mode: {'ALL' if all_entries else 'LATEST'}")
    print(f"   Dry run: {dry_run}")
    print(f"   Trigger signals: {trigger_signals}")
    print()
    
    integrate_research(all_entries=all_entries, dry_run=dry_run, trigger_signals=trigger_signals)


if __name__ == "__main__":
    main()
