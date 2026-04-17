#!/usr/bin/env python3
"""
KG Learning Integrator
Bridges evaluation feedback → Knowledge Graph

Usage:
    python3 kg_learning_integrator.py --sync          # Sync learnings to KG
    python3 kg_learning_integrator.py --query <type>  # Query learnings by type
    python3 kg_learning_integrator.py --recent        # Show recent learnings
    python3 kg_learning_integrator.py --list          # List all learning entities
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KG_PATH = os.path.join(SCRIPT_DIR, "../memory/kg/knowledge_graph.json")
SIGNAL_PATH = os.path.join(SCRIPT_DIR, "../memory/evaluations/learning_loop_signal.json")


def load_kg():
    """Load the Knowledge Graph."""
    with open(KG_PATH, "r") as f:
        return json.load(f)


def save_kg(kg):
    """Save the Knowledge Graph."""
    kg["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2, default=str)


def load_signals():
    """Load evaluation signals — returns list of signal dicts."""
    if not os.path.exists(SIGNAL_PATH):
        print(f"[!] Signal file not found: {SIGNAL_PATH}")
        return []
    with open(SIGNAL_PATH, "r") as f:
        data = json.load(f)
    # data is a single signal object; return as single-item list
    return [data]


def extract_learning_entities(signal_data):
    """Extract learning entities from signal data."""
    # learnings can be at root level or inside 'data' block
    learnings = signal_data.get("learnings", [])
    if not learnings and "data" in signal_data:
        learnings = signal_data["data"].get("learnings", [])
    antipatterns = signal_data.get("data", {}).get("antipattern_issues", [])
    if not antipatterns:
        antipatterns = signal_data.get("antipattern_issues", [])
    
    entities = []
    timestamp = signal_data.get("timestamp", datetime.now(timezone.utc).isoformat())
    source = signal_data.get("source", "evaluation_framework")

    # Process structured learnings
    for lr in learnings:
        entity_name = f"learning_{lr.get('type', 'unknown')}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        entities.append({
            "entity_name": entity_name,
            "learning_type": lr.get("type", "unknown"),
            "priority": lr.get("priority", "MED"),
            "observation": lr.get("observation", ""),
            "action": lr.get("action", ""),
            "timestamp": timestamp,
            "source": source,
            "category": "learning",
        })

    # Process antipatterns as learnings
    for ap in antipatterns:
        entity_name = f"learning_antipattern_{ap.get('pattern_name', 'unknown')}"
        entities.append({
            "entity_name": entity_name,
            "learning_type": "antipattern",
            "priority": ap.get("severity", "MED"),
            "observation": ap.get("description", ""),
            "action": f"Fix pattern: {ap.get('pattern_name', 'unknown')} in {ap.get('file', 'unknown file')}",
            "timestamp": timestamp,
            "source": source,
            "category": "learning",
        })

    return entities


def sync_to_kg(kg, entities):
    """Sync extracted entities to the Knowledge Graph."""
    if not entities:
        print("[*] No new learnings to sync.")
        return kg

    synced = 0
    for entity in entities:
        name = entity["entity_name"]
        
        # Create entity if not exists, update if exists
        if name in kg["entities"]:
            # Update existing: merge facts
            existing = kg["entities"][name]
            new_fact = {
                "content": f"{entity['observation']} → {entity['action']}",
                "confidence": 0.9,
                "extracted_at": entity["timestamp"],
                "category": entity["category"],
            }
            # Avoid duplicate facts
            existing_facts = existing.get("facts", [])
            if not any(f.get("content") == new_fact["content"] for f in existing_facts):
                existing_facts.append(new_fact)
            existing["facts"] = existing_facts
            existing["last_accessed"] = datetime.now(timezone.utc).isoformat()
            existing["access_count"] = existing.get("access_count", 0) + 1
            # Update priority if higher
            priority_order = {"LOW": 0, "MED": 1, "HIGH": 2, "CRITICAL": 3}
            if priority_order.get(entity["priority"], 0) > priority_order.get(existing.get("priority", "MED"), 1):
                existing["priority"] = entity["priority"]
        else:
            # Create new entity
            kg["entities"][name] = {
                "type": "learning",
                "category": entity["category"],
                "priority": entity["priority"],
                "facts": [
                    {
                        "content": f"{entity['observation']} → {entity['action']}",
                        "confidence": 0.9,
                        "extracted_at": entity["timestamp"],
                        "category": entity["category"],
                    }
                ],
                "created": entity["timestamp"],
                "last_accessed": datetime.now(timezone.utc).isoformat(),
                "access_count": 1,
                "decay_score": 1,
                # Learning-specific fields
                "learning_type": entity["learning_type"],
                "observation": entity["observation"],
                "action": entity["action"],
                "source": entity["source"],
            }
            
            # Add relation: learned_from
            rel = {
                "from": name,
                "to": entity["source"],
                "type": "learned_from",
                "weight": 0.9,
                "created_at": entity["timestamp"],
            }
            kg["relationships"].append(rel)

        synced += 1

    print(f"[+] Synced {synced} learning(s) to KG.")
    return kg


def query_learnings(kg, learning_type):
    """Query learnings by type."""
    results = []
    for name, entity in kg["entities"].items():
        if entity.get("type") == "learning" and entity.get("learning_type") == learning_type:
            results.append((name, entity))
    
    if not results:
        print(f"[*] No learnings of type '{learning_type}' found.")
        return results
    
    print(f"[+] Found {len(results)} learning(s) of type '{learning_type}':\n")
    for name, entity in results:
        print(f"  📌 {name}")
        print(f"     Priority: {entity.get('priority', 'N/A')}")
        print(f"     Observed: {entity.get('observation', 'N/A')}")
        print(f"     Action:   {entity.get('action', 'N/A')}")
        print(f"     Source:   {entity.get('source', 'N/A')}")
        print()
    
    return results


def show_recent(kg, limit=10):
    """Show most recently accessed learnings."""
    learnings = [
        (name, e) for name, e in kg["entities"].items()
        if e.get("type") == "learning"
    ]
    
    # Sort by last_accessed
    learnings.sort(
        key=lambda x: x[1].get("last_accessed", ""),
        reverse=True
    )
    
    learnings = learnings[:limit]
    
    if not learnings:
        print("[*] No learnings found in KG.")
        return learnings
    
    print(f"[+] {len(learnings)} most recent learning(s):\n")
    for name, entity in learnings:
        print(f"  📌 {name}")
        print(f"     Type:     {entity.get('learning_type', 'N/A')}")
        print(f"     Priority: {entity.get('priority', 'N/A')}")
        print(f"     Observed: {entity.get('observation', 'N/A')}")
        print(f"     Action:   {entity.get('action', 'N/A')}")
        print(f"     Last accessed: {entity.get('last_accessed', 'N/A')}")
        print()
    
    return learnings


def list_all_learnings(kg):
    """List all learning entities grouped by type."""
    by_type = {}
    for name, entity in kg["entities"].items():
        if entity.get("type") == "learning":
            lt = entity.get("learning_type", "unknown")
            if lt not in by_type:
                by_type[lt] = []
            by_type[lt].append((name, entity))
    
    if not by_type:
        print("[*] No learnings in KG.")
        return by_type
    
    total = sum(len(v) for v in by_type.values())
    print(f"[+] {total} learnings across {len(by_type)} types:\n")
    for lt, items in sorted(by_type.items()):
        print(f"  [{lt}] ({len(items)})")
        for name, _ in items:
            print(f"    - {name}")
        print()
    
    return by_type


def main():
    parser = argparse.ArgumentParser(description="KG Learning Integrator")
    parser.add_argument("--sync", action="store_true", help="Sync learnings from signal file to KG")
    parser.add_argument("--query", metavar="TYPE", help="Query learnings by type (e.g. performance_gap, antipattern)")
    parser.add_argument("--recent", action="store_true", help="Show recent learnings")
    parser.add_argument("--list", action="store_true", help="List all learnings grouped by type")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)

    if args.sync:
        print("[*] Loading KG...")
        kg = load_kg()
        print("[*] Loading signals...")
        signal_data = load_signals()
        if not signal_data:
            print("[!] No learnings found in signal file.")
            sys.exit(1)
        
        # Support both list and dict formats
        if isinstance(signal_data, dict):
            signal_list = [signal_data]
        else:
            signal_list = signal_data
        
        total_synced = 0
        for sd in signal_list:
            entities = extract_learning_entities(sd)
            if entities:
                kg = sync_to_kg(kg, entities)
                total_synced += len(entities)
        
        if total_synced > 0:
            save_kg(kg)
            print(f"[+] Done. {total_synced} learning(s) synced to KG.")
        else:
            print("[*] No new learnings to sync.")
        return

    if args.query:
        kg = load_kg()
        query_learnings(kg, args.query)
        return

    if args.recent:
        kg = load_kg()
        show_recent(kg)
        return

    if args.list:
        kg = load_kg()
        list_all_learnings(kg)
        return


if __name__ == "__main__":
    main()
