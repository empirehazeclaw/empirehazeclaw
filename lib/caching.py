"""
💾 SEMANTIC CACHE
=================
Integrates semantic_cache for cost savings
"""

import sys
sys.path.insert(0, '.')

from core.semantic_cache import SemanticCache

cache = SemanticCache(ttl_seconds=3600)

def get_cached(key):
    return cache.check_cache(key)

def set_cache(key, value):
    cache.store_in_cache(key, value)

# Test
test = get_cached("test query")
print(f"💾 Cache: {test}")
