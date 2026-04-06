#!/usr/bin/env python3
"""
Smart Cache System - Query Caching mit Ähnlichkeitserkennung
Spart API-Calls durch intelligentes Caching mit 24h TTL
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Optional
from difflib import SequenceMatcher

# Konfiguration
CACHE_DIR = "/home/clawbot/.openclaw/cache"
CACHE_FILE = os.path.join(CACHE_DIR, "smart_cache.json")
TTL_HOURS = 24
SIMILARITY_THRESHOLD = 0.80


def _load_cache() -> dict:
    """Lädt den Cache aus der JSON-Datei."""
    if not os.path.exists(CACHE_FILE):
        return {"entries": {}, "stats": {"hits": 0, "misses": 0, "total_requests": 0}}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"entries": {}, "stats": {"hits": 0, "misses": 0, "total_requests": 0}}


def _save_cache(cache: dict) -> None:
    """Speichert den Cache in die JSON-Datei."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def _calculate_similarity(query1: str, query2: str) -> float:
    """Berechnet Ähnlichkeit zwischen zwei Queries (0.0 bis 1.0)."""
    # Normalize: lowercase, strip whitespace
    q1 = query1.lower().strip()
    q2 = query2.lower().strip()
    
    # Exact match
    if q1 == q2:
        return 1.0
    
    # Use SequenceMatcher for similarity
    return SequenceMatcher(None, q1, q2).ratio()


def _is_expired(timestamp: float) -> bool:
    """Prüft ob ein Eintrag abgelaufen ist."""
    entry_time = datetime.fromtimestamp(timestamp)
    expiry_time = entry_time + timedelta(hours=TTL_HOURS)
    return datetime.now() > expiry_time


def _clean_expired_entries(cache: dict) -> int:
    """Entfernt abgelaufene Einträge. Returns count of removed entries."""
    current_time = time.time()
    expired_keys = [
        key for key, entry in cache["entries"].items()
        if _is_expired(entry.get("cached_at", 0))
    ]
    for key in expired_keys:
        del cache["entries"][key]
    return len(expired_keys)


def cache_get(query: str) -> Optional[Any]:
    """
    Holt gecachtes Ergebnis für eine Query.
    Verwendet Ähnlichkeitserkennung (>=80%).
    
    Args:
        query: Die zu suchende Query
        
    Returns:
        Das gecachte Ergebnis oder None wenn nicht gefunden
    """
    cache = _load_cache()
    cache["stats"]["total_requests"] += 1
    
    # Clean expired entries occasionally (10% chance)
    if cache["stats"]["total_requests"] % 10 == 0:
        _clean_expired_entries(cache)
    
    query_lower = query.lower().strip()
    
    # Try exact match first
    if query_lower in cache["entries"]:
        entry = cache["entries"][query_lower]
        if not _is_expired(entry.get("cached_at", 0)):
            cache["stats"]["hits"] += 1
            entry["access_count"] = entry.get("access_count", 0) + 1
            _save_cache(cache)
            return entry["result"]
        else:
            # Remove expired exact match
            del cache["entries"][query_lower]
    
    # Try similar queries
    best_match = None
    best_similarity = 0.0
    
    for cached_query, entry in cache["entries"].items():
        if _is_expired(entry.get("cached_at", 0)):
            continue
            
        similarity = _calculate_similarity(query_lower, cached_query)
        
        if similarity >= SIMILARITY_THRESHOLD and similarity > best_similarity:
            best_similarity = similarity
            best_match = (cached_query, entry)
    
    if best_match:
        cached_query, entry = best_match
        cache["stats"]["hits"] += 1
        entry["access_count"] = entry.get("access_count", 0) + 1
        
        # Update query to track the new pattern too
        if query_lower not in cache["entries"]:
            cache["entries"][query_lower] = {
                "result": entry["result"],
                "cached_at": time.time(),
                "access_count": 1,
                "original_query": cached_query
            }
        
        _save_cache(cache)
        return entry["result"]
    
    cache["stats"]["misses"] += 1
    _save_cache(cache)
    return None


def cache_set(query: str, result: Any) -> None:
    """
    Speichert eine Query mit Ergebnis im Cache.
    
    Args:
        query: Die Query
        result: Das zu cachende Ergebnis
    """
    cache = _load_cache()
    query_lower = query.lower().strip()
    
    cache["entries"][query_lower] = {
        "result": result,
        "cached_at": time.time(),
        "access_count": 1
    }
    
    _save_cache(cache)


def cache_stats() -> dict:
    """
    Gibt Cache-Statistiken zurück.
    
    Returns:
        Dict mit hit_rate, total_requests, hits, misses, 
        top_queries, entry_count, expired_count
    """
    cache = _load_cache()
    stats = cache["stats"]
    
    # Calculate hit rate
    total = stats["total_requests"]
    hit_rate = (stats["hits"] / total * 100) if total > 0 else 0.0
    
    # Top queries by access count
    top_queries = sorted(
        [(q, e.get("access_count", 0)) for q, e in cache["entries"].items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Count expired entries
    expired_count = sum(
        1 for e in cache["entries"].values() 
        if _is_expired(e.get("cached_at", 0))
    )
    
    return {
        "hit_rate": round(hit_rate, 2),
        "total_requests": total,
        "hits": stats["hits"],
        "misses": stats["misses"],
        "entry_count": len(cache["entries"]),
        "expired_count": expired_count,
        "top_queries": [{"query": q, "accesses": c} for q, c in top_queries]
    }


def cache_clear() -> None:
    """Löscht den gesamten Cache."""
    cache = {"entries": {}, "stats": {"hits": 0, "misses": 0, "total_requests": 0}}
    _save_cache(cache)


def cache_cleanup() -> int:
    """Entfernt abgelaufene Einträge. Returns count of removed entries."""
    cache = _load_cache()
    removed = _clean_expired_entries(cache)
    _save_cache(cache)
    return removed


if __name__ == "__main__":
    # Demo usage
    print("🗃️ Smart Cache Demo")
    print("=" * 40)
    
    # Test cache_set and cache_get
    cache_set("Wie ist das Wetter in Berlin?", {"weather": "sonnig", "temp": 22})
    cache_set("Wetter Berlin", {"weather": "bewölkt", "temp": 18})
    
    # Test similarity matching
    result = cache_get("Wetter in Berlin")
    print(f"Query: 'Wetter in Berlin' → {result}")
    
    # Test exact match
    result2 = cache_get("Wie ist das Wetter in Berlin?")
    print(f"Query: 'Wie ist das Wetter in Berlin?' → {result2}")
    
    # Stats
    print("\n📊 Cache Stats:")
    stats = cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
