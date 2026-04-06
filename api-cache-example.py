#!/usr/bin/env python3
"""
🌐 API Response Cache Wrapper
Caches API responses to reduce costs and improve speed

Usage:
    from api_cache import cached_call
    
    @cached_call(ttl=300)  # 5 minutes
    def fetch_lead_data(lead_id):
        return api_call(lead_id)
"""

import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

CACHE_DIR = Path("/home/clawbot/.openclaw/workspace/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def cache_key(func_name, args, kwargs):
    """Generate a unique cache key"""
    key_data = {
        "func": func_name,
        "args": str(sorted(args)),
        "kwargs": str(sorted(kwargs.items()))
    }
    hash_str = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()[:12]
    return f"{func_name}_{hash_str}"

def get_cached(key):
    """Get cached value if exists and not expired"""
    file = CACHE_DIR / f"{key}.json"
    
    if not file.exists():
        return None
    
    with open(file) as f:
        data = json.load(f)
    
    if data["expires"]:
        expires = datetime.fromisoformat(data["expires"])
        if datetime.now() > expires:
            file.unlink()
            return None
    
    return data["value"]

def set_cached(key, value, ttl):
    """Cache a value with TTL"""
    data = {
        "key": key,
        "value": value,
        "created": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl else None
    }
    
    with open(CACHE_DIR / f"{key}.json", 'w') as f:
        json.dump(data, f)

def cached_call(ttl=300, key_prefix=None):
    """
    Decorator for caching API calls
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Optional prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            prefix = key_prefix or func.__name__
            key = cache_key(prefix, args, kwargs)
            
            # Try to get from cache
            cached = get_cached(key)
            if cached is not None:
                print(f"📦 [{func.__name__}] Cache HIT (key: {key[:20]}...)")
                return cached
            
            # Call the function
            print(f"🌐 [{func.__name__}] Cache MISS - calling API...")
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            # Cache the result
            set_cached(key, result, ttl)
            print(f"✅ [{func.__name__}] Cached for {ttl}s (took {duration:.2f}s)")
            
            return result
        return wrapper
    return decorator

# ═══════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Example: Cache a lead lookup
    @cached_call(ttl=300)  # 5 minute cache
    def fetch_lead(lead_id):
        # Simulate API call
        time.sleep(1)  # Pretend this takes time
        return {"id": lead_id, "name": f"Lead {lead_id}", "score": 85}
    
    # First call - will take ~1 second
    print("\n📱 First call (API):")
    result1 = fetch_lead("123")
    print(f"   Result: {result1}")
    
    # Second call - will be instant (cached)
    print("\n📱 Second call (Cache):")
    result2 = fetch_lead("123")
    print(f"   Result: {result2}")
    
    # Different lead - will call API again
    print("\n📱 Different lead (API):")
    result3 = fetch_lead("456")
    print(f"   Result: {result3}")
    
    # Show stats
    print("\n📊 Cache Stats:")
    import subprocess
    subprocess.run(["python3", __file__.replace(".py", ""), "stats"])
