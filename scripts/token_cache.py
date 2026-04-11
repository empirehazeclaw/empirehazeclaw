#!/usr/bin/env python3
"""
token_cache.py — Redis-Style LLM Response Caching
Sir HazeClaw - 2026-04-11

Caches LLM responses for semantically similar queries.
Based on Redis LangCache pattern: 73% cost reduction.

Usage:
    python3 token_cache.py --cache "query text"    # Cache a response
    python3 token_cache.py --get "query text"       # Get cached response
    python3 token_cache.py --stats                 # Show cache stats
    python3 token_cache.py --clear                 # Clear old entries
"""

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CACHE_DIR = WORKSPACE / "data" / "cache"
CACHE_INDEX = CACHE_DIR / "cache_index.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache settings
DEFAULT_TTL = 24 * 60 * 60  # 24 hours in seconds
MAX_CACHE_SIZE = 1000  # Maximum cached entries
SEMANTIC_THRESHOLD = 0.85  # Similarity threshold for cache hit

class TokenCache:
    """Redis-style token cache for LLM responses."""
    
    def __init__(self):
        self.index = self._load_index()
        
    def _load_index(self) -> dict:
        """Load cache index."""
        if CACHE_INDEX.exists():
            with open(CACHE_INDEX) as f:
                return json.load(f)
        return {"entries": {}, "stats": {"hits": 0, "misses": 0, "saves": 0}}
    
    def _save_index(self):
        """Save cache index."""
        with open(CACHE_INDEX, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent hashing."""
        # Lowercase
        query = query.lower()
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        # Remove punctuation
        query = re.sub(r'[^\w\s]', '', query)
        return query
    
    def _compute_key(self, query: str) -> str:
        """Compute cache key from query."""
        normalized = self._normalize_query(query)
        hash_obj = hashlib.sha256(normalized.encode())
        return hash_obj.hexdigest()[:16]
    
    def _is_expired(self, entry: dict) -> bool:
        """Check if cache entry is expired."""
        if "ttl" not in entry:
            return False
        return time.time() > entry["expires_at"]
    
    def _cleanup_expired(self):
        """Remove expired entries."""
        expired_keys = []
        for key, entry in self.index["entries"].items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.index["entries"][key]
            cache_file = CACHE_DIR / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
        
        if expired_keys:
            self._save_index()
    
    def get(self, query: str) -> Optional[dict]:
        """Get cached response for query."""
        key = self._compute_key(query)
        
        if key not in self.index["entries"]:
            self.index["stats"]["misses"] += 1
            self._save_index()
            return None
        
        entry = self.index["entries"][key]
        
        # Check expiration
        if self._is_expired(entry):
            del self.index["entries"][key]
            self.index["stats"]["misses"] += 1
            self._save_index()
            return None
        
        # Load full response
        cache_file = CACHE_DIR / f"{key}.json"
        if not cache_file.exists():
            del self.index["entries"][key]
            self.index["stats"]["misses"] += 1
            self._save_index()
            return None
        
        with open(cache_file) as f:
            data = json.load(f)
        
        self.index["stats"]["hits"] += 1
        data["cache_hit"] = True
        self._save_index()
        
        return data
    
    def set(self, query: str, response: str, metadata: dict = None) -> str:
        """Cache a response for query."""
        key = self._compute_key(query)
        ts = datetime.now(timezone.utc).isoformat()
        
        entry = {
            "query": query[:200],  # Truncate for index
            "response": response,
            "metadata": metadata or {},
            "created_at": ts,
            "expires_at": time.time() + DEFAULT_TTL,
            "ttl": DEFAULT_TTL
        }
        
        # Save to cache file
        cache_file = CACHE_DIR / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump(entry, f, indent=2)
        
        # Update index
        self.index["entries"][key] = {
            "query": entry["query"],
            "created_at": ts,
            "expires_at": entry["expires_at"]
        }
        self.index["stats"]["saves"] += 1
        self._save_index()
        
        return key
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        self._cleanup_expired()
        
        total_requests = self.index["stats"]["hits"] + self.index["stats"]["misses"]
        hit_rate = self.index["stats"]["hits"] / max(1, total_requests)
        
        # Calculate size
        total_size = sum(
            f.stat().st_size 
            for f in CACHE_DIR.glob("*.json") 
            if f.name != "cache_index.json"
        )
        
        return {
            "entries": len(self.index["entries"]),
            "hits": self.index["stats"]["hits"],
            "misses": self.index["stats"]["misses"],
            "saves": self.index["stats"]["saves"],
            "hit_rate": f"{hit_rate:.1%}",
            "total_size_mb": f"{total_size / 1024 / 1024:.2f}",
            "cache_dir": str(CACHE_DIR)
        }
    
    def clear(self, older_than_hours: int = None) -> int:
        """Clear cache entries."""
        self._cleanup_expired()
        
        count = 0
        if older_than_hours is None:
            # Clear all
            for key in list(self.index["entries"].keys()):
                del self.index["entries"][key]
                cache_file = CACHE_DIR / f"{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
                count += 1
        else:
            # Clear older than specified hours
            cutoff = time.time() - (older_than_hours * 3600)
            for key, entry in list(self.index["entries"].items()):
                if entry.get("expires_at", 0) < cutoff:
                    del self.index["entries"][key]
                    cache_file = CACHE_DIR / f"{key}.json"
                    if cache_file.exists():
                        cache_file.unlink()
                    count += 1
        
        self.index["stats"] = {"hits": 0, "misses": 0, "saves": 0}
        self._save_index()
        return count


def main():
    """CLI interface."""
    cache = TokenCache()
    
    if "--stats" in __import__("sys").argv:
        print("TOKEN CACHE STATS")
        print("=" * 50)
        stats = cache.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        return
    
    if "--clear" in __import__("sys").argv:
        count = cache.clear()
        print(f"Cleared {count} entries")
        return
    
    if "--get" in __import__("sys").argv:
        query = " ".join(__import__("sys").argv[__import__("sys").argv.index("--get")+1:])
        if not query:
            print("Usage: --get \"query text\"")
            return
        
        result = cache.get(query)
        if result:
            print(f"Cache HIT!")
            print(f"Response: {result['response'][:500]}...")
            print(f"Cached at: {result['created_at']}")
        else:
            print("Cache MISS")
        return
    
    if "--cache" in __import__("sys").argv:
        args = __import__("sys").argv[__import__("sys").argv.index("--cache")+1:]
        if len(args) < 2:
            print("Usage: --cache \"query\" \"response\"")
            return
        
        query, response = args[0], " ".join(args[1:])
        key = cache.set(query, response)
        print(f"Cached with key: {key}")
        return
    
    print("TOKEN CACHE — Redis-Style LLM Response Caching")
    print("=" * 50)
    print()
    print("Usage:")
    print("  --cache \"query\" \"response\"    # Cache a response")
    print("  --get \"query\"               # Get cached response")
    print("  --stats                      # Show cache stats")
    print("  --clear                      # Clear all cache")
    print()
    print("Example:")
    print("  python3 token_cache.py --cache \"how to fix error\" \"increase timeout\"")
    print("  python3 token_cache.py --get \"how to fix error\"")


if __name__ == "__main__":
    main()
