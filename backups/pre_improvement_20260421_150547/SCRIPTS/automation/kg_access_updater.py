#!/usr/bin/env python3
"""
KG Access Updater — Sir HazeClaw
Runs memory_hybrid_search with common queries to update access_count
This ensures KG entities are properly tracked when accessed.
"""

import sys
from pathlib import Path

# Add SCRIPTS dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "SCRIPTS" / "analysis"))

try:
    from memory_hybrid_search import semantic_search, update_kg_access
    
    # Business-relevant queries to "warm up" the KG
    queries = [
        "KI Mitarbeiter",
        "EmpireHazeClaw",
        "Managed AI Hosting",
        "KG retrieval",
        "OpenClaw system",
        "security audit",
        "cron health",
        "session management"
    ]
    
    print("KG Access Updater - Warming up knowledge graph...")
    
    all_accessed = []
    for query in queries:
        results = semantic_search(query, limit=10)
        accessed = [r[0].replace("entity:", "") for r in results if r[0].startswith("entity:")]
        all_accessed.extend(accessed)
        print(f"  Query '{query}': {len(accessed)} entities accessed")
    
    # Remove duplicates
    unique = list(set(all_accessed))
    print(f"\nTotal unique entities accessed: {len(unique)}")
    print("KG access tracking updated successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)