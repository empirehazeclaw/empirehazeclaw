#!/usr/bin/env python3
"""
KG Access Updater — OPTIMIZED
=============================
Optimized version that:
- Loads KG only ONCE
- Runs all queries with cached KG
- Writes KG only ONCE at the end
- Uses simple in-memory matching (no vector lookups)

Usage:
    python3 kg_access_updater_optimized.py

Run via cron (replaces slow version):
    python3 /home/clawbot/.openclaw/workspace/scripts/kg_access_updater_optimized.py
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

# Paths
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "ceo" / "memory" / "kg" / "knowledge_graph.json"
HIT_LOG = WORKSPACE / "logs" / "kg_hit_rate.log"

# Queries to track
QUERIES = [
    "KI Mitarbeiter",
    "EmpireHazeClaw",
    "Managed AI",
    "KG",
    "OpenClaw",
    "security",
    "cron health",
    "session"
]


def load_kg():
    """Load KG once into memory."""
    if not KG_PATH.exists():
        return None
    with open(KG_PATH) as f:
        return json.load(f)


def save_kg(kg):
    """Save KG once."""
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)


def search_kg(kg, query):
    """Simple keyword search in KG entities."""
    results = []
    query_words = set(re.findall(r'\w+', query.lower()))
    
    if not kg or 'entities' not in kg:
        return results
    
    for entity_id, data in kg['entities'].items():
        entity_lower = entity_id.lower()
        entity_score = 0.0
        
        # Exact entity match
        if any(word in entity_lower for word in query_words):
            entity_score = 0.9
        else:
            # Fact content match
            for fact in data.get('facts', []):
                fact_content = fact.get('content', '').lower() if isinstance(fact, dict) else str(fact).lower()
                matched_words = sum(1 for word in query_words if word in fact_content)
                if matched_words > 0:
                    word_score = matched_words / len(query_words)
                    entity_score = max(entity_score, word_score * 0.6)
                    break
        
        if entity_score > 0:
            results.append((entity_id, entity_score))
    
    # Sort by score
    results.sort(key=lambda x: -x[1])
    return results[:10]


def update_access_counts(kg, accessed_entities):
    """Update access counts in memory."""
    now = datetime.now(timezone.utc).isoformat()
    
    for name in accessed_entities:
        if name in kg.get('entities', {}):
            entity = kg['entities'][name]
            entity['last_accessed'] = now
            entity['access_count'] = entity.get('access_count', 0) + 1


def log_hits(total_accessed, total_queried):
    """Log KG hit rate."""
    HIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(HIT_LOG, 'a') as f:
        f.write(f"[{timestamp}] KG hits: {total_accessed}/{total_queried} entities accessed\n")


def main():
    print(f"KG Access Updater — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Load KG once
    print("Loading KG...")
    kg = load_kg()
    if not kg:
        print("❌ KG not found")
        return 1
    
    entity_count = len(kg.get('entities', {}))
    print(f"✅ KG loaded: {entity_count} entities")
    
    # Run all queries with cached KG
    all_accessed = set()
    total_hits = 0
    
    print(f"\nRunning {len(QUERIES)} queries...")
    for query in QUERIES:
        results = search_kg(kg, query)
        hits = len(results)
        total_hits += hits
        for entity_id, score in results:
            all_accessed.add(entity_id)
        print(f"  '{query}': {hits} hits")
    
    # Update access counts in memory
    print(f"\nUpdating access counts for {len(all_accessed)} entities...")
    update_access_counts(kg, all_accessed)
    
    # Save KG once
    print("Saving KG...")
    save_kg(kg)
    print("✅ Done")
    
    # Log hits
    log_hits(total_hits, len(QUERIES))
    
    return 0


if __name__ == "__main__":
    exit(main())
