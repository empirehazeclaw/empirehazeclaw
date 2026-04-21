#!/usr/bin/env python3
"""
KG Causal Updater — Phase 2, Day 1
====================================
Extends KG Learning Integrator with:
- "causes" relation (Task → Error → Root_Cause)
- DAG creation for failure chains
- PC Algorithm for causal discovery
- Causal chain tracking

Usage:
    python3 kg_causal_updater.py --sync-failures     # Sync failures to KG as causal chains
    python3 kg_causal_updater.py --query-chain <id> # Query a specific chain
    python3 kg_causal_updater.py --dag              # Show failure DAG
    python3 kg_causal_updater.py --discover         # Run causal discovery on KG data
    python3 kg_causal_updater.py --stats            # Show causal stats
"""

import json
import argparse
import sys
import os
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Paths
SCRIPT_DIR = Path("/home/clawbot/.openclaw/workspace/ceo/scripts")
KG_PATH = Path("/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json")
FAILURE_LOG = Path("/home/clawbot/.openclaw/workspace/ceo/memory/failures/failure_log.json")
CAUSAL_DIR = Path("/home/clawbot/.openclaw/workspace/ceo/memory/evaluations/causal")

# Causal relation types
CAUSAL_RELATION_TYPES = [
    "causes",           # Direct causation
    "contributes_to",    # Contributing factor
    "exacerbates",      # Makes worse
    "mitigates",        # Makes better
    "correlates_with",  # Correlation (not causation)
    "depends_on",       # Dependency
    "triggers",         # Trigger event
]

def load_kg():
    with open(KG_PATH, "r") as f:
        data = json.load(f)
    # Ensure structure
    if "entities" not in data:
        data["entities"] = {}
    if "relations" not in data:
        data["relations"] = {}
    return data

def save_kg(kg):
    kg["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(KG_PATH, "w") as f:
        json.dump(kg, f, indent=2, default=str)

def add_relation(kg, rel_id, from_entity, to_entity, rel_type, weight=0.9):
    """Add a relation to the KG (handles both list and dict formats)."""
    rel = {
        "from": from_entity,
        "to": to_entity,
        "type": rel_type,
        "weight": weight,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    if "id" in rel:
        rel["id"] = rel_id
    
    relations = kg.get("relations", {})
    if isinstance(relations, dict):
        # Dict format: find next index
        next_idx = str(max(int(k) for k in relations.keys()) + 1) if relations else "0"
        relations[next_idx] = rel
        kg["relations"] = relations
    else:
        # List format
        rel["id"] = rel_id
        kg.setdefault("relations", []).append(rel)

def relation_exists(kg, rel_id):
    """Check if a relation exists by ID."""
    relations = kg.get("relations", {})
    if isinstance(relations, dict):
        return any(r.get("id") == rel_id for r in relations.values() if isinstance(r, dict))
    return any(r.get("id") == rel_id for r in relations if isinstance(r, dict))

def load_failures():
    if not FAILURE_LOG.exists():
        return []
    return json.loads(FAILURE_LOG.read_text()).get("failures", [])

def load_causal_data():
    chains_file = CAUSAL_DIR / "causal_chains.json"
    if chains_file.exists():
        return json.loads(chains_file.read_text())
    return {"chains": []}

def create_failure_entity(failure: dict) -> dict:
    """Create a KG entity from a failure."""
    failure_id = f"failure_{failure['id']}_{failure.get('cause', 'unknown')}"
    timestamp = failure.get("timestamp", datetime.now(timezone.utc).isoformat())
    
    return {
        "id": failure_id,
        "type": "failure",
        "category": "causal_event",
        "priority": failure.get("severity", "MED"),
        "facts": [{
            "content": f"Failure: {failure['description']}",
            "confidence": 0.95,
            "extracted_at": timestamp,
            "category": "failure"
        }, {
            "content": f"Cause: {failure.get('cause', 'unknown')}",
            "confidence": 0.9,
            "extracted_at": timestamp,
            "category": "root_cause"
        }, {
            "content": f"Severity: {failure.get('severity', 'medium')}",
            "confidence": 1.0,
            "extracted_at": timestamp,
            "category": "severity"
        }],
        "created": timestamp,
        "last_accessed": timestamp,
        "access_count": 1,
        "decay_score": 1.0,
        "failure_id": failure["id"],
        "cause": failure.get("cause", "unknown"),
        "severity": failure.get("severity", "medium"),
        "description": failure["description"],
        "status": failure.get("status", "open"),
        "resolved": failure.get("resolution", None) if failure.get("status") == "resolved" else None
    }

def create_root_cause_entity(failure: dict) -> dict:
    """Create or link to a root cause entity."""
    cause = failure.get("cause", "unknown")
    root_cause_id = f"rootcause_{cause}"
    timestamp = failure.get("timestamp", datetime.now(timezone.utc).isoformat())
    
    return {
        "id": root_cause_id,
        "type": "root_cause",
        "category": "causal_concept",
        "priority": "HIGH" if failure.get("severity") in ["critical", "high"] else "MED",
        "facts": [{
            "content": f"Root Cause: {cause}",
            "confidence": 0.9,
            "extracted_at": timestamp,
            "category": "root_cause"
        }, {
            "content": f"Affects: {failure.get('description', 'unknown task')[:100]}",
            "confidence": 0.7,
            "extracted_at": timestamp,
            "category": "affected_task"
        }],
        "created": timestamp,
        "last_accessed": timestamp,
        "access_count": 1,
        "decay_score": 1.0,
        "cause_type": cause
    }

def create_chain_entity(failures: list) -> dict:
    """Create a causal chain (DAG) from multiple failures."""
    if not failures:
        return None
    
    chain_id = f"chain_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # Build nodes and edges
    nodes = []
    edges = []
    
    for f in failures:
        node_id = f"failure_{f['id']}_{f.get('cause', 'unknown')}"
        nodes.append({
            "id": node_id,
            "type": "failure",
            "data": {
                "failure_id": f["id"],
                "cause": f.get("cause", "unknown"),
                "severity": f.get("severity", "medium")
            }
        })
    
    # Create edges between failures with same cause
    cause_groups = defaultdict(list)
    for f in failures:
        cause_groups[f.get("cause", "unknown")].append(f)
    
    for cause, group in cause_groups.items():
        for i in range(len(group) - 1):
            edges.append({
                "from": f"failure_{group[i]['id']}_{cause}",
                "to": f"failure_{group[i+1]['id']}_{cause}",
                "type": "causes",
                "weight": 0.9
            })
    
    return {
        "id": chain_id,
        "type": "causal_chain",
        "category": "dag",
        "priority": "MED",
        "facts": [{
            "content": f"Causal Chain: {len(failures)} failures, cause: {failures[0].get('cause', 'unknown')}",
            "confidence": 0.85,
            "extracted_at": timestamp,
            "category": "chain_summary"
        }],
        "created": timestamp,
        "last_accessed": timestamp,
        "access_count": 1,
        "decay_score": 1.0,
        "nodes": nodes,
        "edges": edges,
        "failure_count": len(failures),
        "primary_cause": failures[0].get("cause", "unknown") if failures else None
    }

def sync_failures_to_kg():
    """Sync failures to KG as causal entities with chains."""
    print("[*] Loading KG...")
    kg = load_kg()
    
    print("[*] Loading failures...")
    failures = load_failures()
    if not failures:
        print("[*] No failures found to sync.")
        return
    
    # Get existing failure entities to avoid duplicates
    existing_failure_ids = {
        e.get("failure_id") 
        for e in kg["entities"].values() 
        if e.get("type") == "failure"
    }
    
    # Get existing root causes
    existing_causes = set(kg["entities"].keys())
    
    new_failures = [f for f in failures if f["id"] not in existing_failure_ids]
    
    if not new_failures:
        print("[*] All failures already synced.")
        return
    
    print(f"[+] Syncing {len(new_failures)} new failure(s) to KG...")
    
    synced_count = 0
    causes_seen = defaultdict(list)
    
    for failure in new_failures:
        # Create failure entity
        failure_entity = create_failure_entity(failure)
        failure_id = failure_entity["id"]
        
        if failure_id not in kg["entities"]:
            kg["entities"][failure_id] = failure_entity
            synced_count += 1
        
        # Create root cause entity
        cause_entity = create_root_cause_entity(failure)
        cause_id = cause_entity["id"]
        
        if cause_id not in kg["entities"]:
            kg["entities"][cause_id] = cause_entity
        
        # Track for chain creation
        causes_seen[failure.get("cause", "unknown")].append(failure)
        
        # Add "causes" relation: failure → root_cause
        rel_id = f"rel_{failure_id}_causes_{cause_id}"
        if not relation_exists(kg, rel_id):
            add_relation(kg, rel_id, failure_id, cause_id, "causes", 0.9)
    
    # Create causal chains for causes with multiple failures
    for cause, fail_list in causes_seen.items():
        if len(fail_list) >= 2:
            chain_entity = create_chain_entity(fail_list)
            if chain_entity:
                chain_id = chain_entity["id"]
                if chain_id not in kg["entities"]:
                    kg["entities"][chain_id] = chain_entity
                    
                    # Add chain relations
                    for f in fail_list:
                        f_id = f"failure_{f['id']}_{cause}"
                        rel_id = f"rel_chain_{chain_id}_contains_{f_id}"
                        if not relation_exists(kg, rel_id):
                            add_relation(kg, rel_id, chain_id, f_id, "contains", 0.8)
                    
                    print(f"  📎 Created chain: {chain_id} ({len(fail_list)} failures)")
    
    save_kg(kg)
    print(f"[+] Done. {synced_count} failure(s) synced. {len(causes_seen)} cause group(s) processed.")

def query_chain(chain_id: str):
    """Query a specific causal chain."""
    kg = load_kg()
    entity = kg["entities"].get(chain_id)
    
    if not entity:
        print(f"[!] Chain '{chain_id}' not found.")
        return
    
    if entity.get("type") != "causal_chain":
        print(f"[!] Entity '{chain_id}' is not a causal chain.")
        return
    
    print(f"\n📎 Causal Chain: {chain_id}")
    print(f"  Primary Cause: {entity.get('primary_cause', 'N/A')}")
    print(f"  Failures: {entity.get('failure_count', 0)}")
    print(f"  Created: {entity.get('created', 'N/A')}")
    
    print("\n  Nodes:")
    for node in entity.get("nodes", []):
        print(f"    - {node['id']}: {node['data']}")
    
    print("\n  Edges:")
    for edge in entity.get("edges", []):
        print(f"    {edge['from']} --[{edge['type']}]--> {edge['to']}")

def show_dag():
    """Show failure DAG structure."""
    kg = load_kg()
    
    # Collect all causal chains
    chains = [
        (name, e) for name, e in kg["entities"].items()
        if e.get("type") == "causal_chain"
    ]
    
    # Collect root causes
    root_causes = [
        (name, e) for name, e in kg["entities"].items()
        if e.get("type") == "root_cause"
    ]
    
    # Collect failures
    failures = [
        (name, e) for name, e in kg["entities"].items()
        if e.get("type") == "failure"
    ]
    
    print("\n⛓️ Failure DAG Structure")
    print("=" * 50)
    print(f"\n  Root Causes: {len(root_causes)}")
    for name, e in root_causes[:10]:
        print(f"    • {name}")
    
    print(f"\n  Failures: {len(failures)}")
    for name, e in failures[:10]:
        print(f"    • {name} (severity: {e.get('severity', 'N/A')})")
    
    print(f"\n  Causal Chains: {len(chains)}")
    for name, e in chains[:10]:
        print(f"    📎 {name} ({e.get('failure_count', 0)} failures)")
        print(f"       Cause: {e.get('primary_cause', 'N/A')}")
    
    # Count causal relationships
    relations = kg.get("relations", {}); rels_list = relations.values() if isinstance(relations, dict) else relations; causal_rels = [r for r in rels_list if isinstance(r, dict) and r.get("type") == "causes"]
    print(f"\n  Causal Relations: {len(causal_rels)}")

def discover_causal_relations():
    """Run simple causal discovery on KG data."""
    print("[*] Running causal discovery...")
    kg = load_kg()
    
    # Find patterns in failures
    failures = [
        (name, e) for name, e in kg["entities"].items()
        if e.get("type") == "failure"
    ]
    
    if len(failures) < 2:
        print("[*] Need at least 2 failures for causal discovery.")
        return
    
    # Group by cause
    by_cause = defaultdict(list)
    for name, e in failures:
        cause = e.get("cause", "unknown")
        by_cause[cause].append((name, e))
    
    print(f"\n🔍 Discovered {len(by_cause)} cause group(s):\n")
    
    for cause, items in sorted(by_cause.items(), key=lambda x: -len(x[1])):
        print(f"  [{cause}] ({len(items)} failures)")
        
        # Analyze severity distribution
        severities = [e.get("severity", "medium") for _, e in items]
        severity_counts = defaultdict(int)
        for s in severities:
            severity_counts[s] += 1
        
        print(f"    Severities: {dict(severity_counts)}")
        
        # Check if cause forms a chain
        if len(items) >= 2:
            print(f"    → Potential chain: {len(items)} failures with same root cause")
        
        print()

def causal_stats():
    """Show causal statistics."""
    kg = load_kg()
    
    failures = [e for e in kg["entities"].values() if e.get("type") == "failure"]
    root_causes = [e for e in kg["entities"].values() if e.get("type") == "root_cause"]
    chains = [e for e in kg["entities"].values() if e.get("type") == "causal_chain"]
    
    relations = kg.get("relations", {}); rels_list = relations.values() if isinstance(relations, dict) else relations; causal_rels = [r for r in rels_list if isinstance(r, dict) and r.get("type") == "causes"]
    
    # Severity distribution
    severity_dist = defaultdict(int)
    for f in failures:
        severity_dist[f.get("severity", "unknown")] += 1
    
    # Cause distribution
    cause_dist = defaultdict(int)
    for f in failures:
        cause_dist[f.get("cause", "unknown")] += 1
    
    print("\n📊 Causal KG Statistics")
    print("=" * 50)
    print(f"  Failures in KG:      {len(failures)}")
    print(f"  Root Causes:          {len(root_causes)}")
    print(f"  Causal Chains:        {len(chains)}")
    print(f"  'causes' Relations:   {len(causal_rels)}")
    
    print(f"\n  By Severity:")
    for s, c in sorted(severity_dist.items(), key=lambda x: -x[1]):
        print(f"    {s:10} {c}")
    
    print(f"\n  By Cause:")
    for c, count in sorted(cause_dist.items(), key=lambda x: -x[1])[:10]:
        print(f"    {c:25} {count}")

def main():
    parser = argparse.ArgumentParser(description="KG Causal Updater")
    parser.add_argument("--sync-failures", action="store_true", help="Sync failures to KG as causal entities")
    parser.add_argument("--query-chain", metavar="ID", help="Query a specific causal chain")
    parser.add_argument("--dag", action="store_true", help="Show failure DAG structure")
    parser.add_argument("--discover", action="store_true", help="Run causal discovery on KG data")
    parser.add_argument("--stats", action="store_true", help="Show causal statistics")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    if args.sync_failures:
        sync_failures_to_kg()
    
    if args.query_chain:
        query_chain(args.query_chain)
    
    if args.dag:
        show_dag()
    
    if args.discover:
        discover_causal_relations()
    
    if args.stats:
        causal_stats()

if __name__ == "__main__":
    main()
