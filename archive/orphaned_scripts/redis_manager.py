#!/usr/bin/env python3
"""
Redis Cache Manager
- Central caching for all services
- State management
- Session storage
"""

import redis
import json
from datetime import timedelta

# Connect to Redis (already running on localhost:6379)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_set(key, value, ttl_seconds=3600):
    """Set a value with TTL"""
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    r.setex(key, ttl_seconds, value)

def cache_get(key):
    """Get a value"""
    value = r.get(key)
    if value:
        try:
            return json.loads(value)
        except:
            return value
    return None

def cache_delete(key):
    """Delete a key"""
    r.delete(key)

def cache_keys(pattern="*"):
    """Get all keys matching pattern"""
    return r.keys(pattern)

def state_set(service, data):
    """Set service state"""
    cache_set(f"state:{service}", data, ttl_seconds=86400)  # 24h

def state_get(service):
    """Get service state"""
    return cache_get(f"state:{service}")

def inc_counter(name):
    """Increment a counter"""
    return r.incr(f"counter:{name}")

def get_counter(name):
    """Get counter value"""
    val = r.get(f"counter:{name}")
    return int(val) if val else 0

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "test":
            # Test Redis
            r.set("test", "hello")
            print(f"✅ Redis working: {r.get('test')}")
            r.delete("test")
        
        elif cmd == "keys":
            print("Keys:", cache_keys())
        
        elif cmd == "stats":
            info = r.info()
            print(f"Redis Status:")
            print(f"  Keys: {info.get('db0', {}).get('keys', 0)}")
            print(f"  Memory: {info.get('used_memory_human', 'N/A')}")
        
        elif cmd == "inc":
            name = sys.argv[2] if len(sys.argv) > 2 else "test"
            print(f"Counter {name}: {inc_counter(name)}")
        
        else:
            print("Usage: redis_manager.py [test|keys|stats|inc <name>]")
    else:
        print("Redis Cache Manager")
        print("Commands: test, keys, stats, inc <name>")
