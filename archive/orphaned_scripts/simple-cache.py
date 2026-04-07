#!/usr/bin/env python3
"""
💾 Simple File-Based Cache
Lightweight caching without Redis

Usage:
    python3 simple-cache.py set key value [ttl_seconds]
    python3 simple-cache.py get key
    python3 simple-cache.py delete key
    python3 simple-cache.py clear
"""

import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("/home/clawbot/.openclaw/workspace/cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def cache_file(key):
    """Get cache file path for a key"""
    # Sanitize key
    safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
    return CACHE_DIR / f"{safe_key}.json"

def set(key, value, ttl=None):
    """Set a cache value with optional TTL in seconds"""
    data = {
        "key": key,
        "value": value,
        "created": datetime.now().isoformat(),
        "expires": (datetime.now() + timedelta(seconds=ttl)).isoformat() if ttl else None
    }
    
    with open(cache_file(key), 'w') as f:
        json.dump(data, f)
    
    ttl_str = f" (TTL: {ttl}s)" if ttl else ""
    print(f"✅ Cached: {key}{ttl_str}")

def get(key):
    """Get a cached value, returns None if expired or not found"""
    file = cache_file(key)
    
    if not file.exists():
        print(f"❌ Not found: {key}")
        return None
    
    with open(file) as f:
        data = json.load(f)
    
    # Check expiration
    if data["expires"]:
        expires = datetime.fromisoformat(data["expires"])
        if datetime.now() > expires:
            file.unlink()
            print(f"⏰ Expired: {key}")
            return None
    
    print(f"✅ Hit: {key}")
    return data["value"]

def delete(key):
    """Delete a cache entry"""
    file = cache_file(key)
    if file.exists():
        file.unlink()
        print(f"🗑️ Deleted: {key}")
    else:
        print(f"❌ Not found: {key}")

def clear():
    """Clear all cache entries"""
    count = len(list(CACHE_DIR.glob("*.json")))
    for file in CACHE_DIR.glob("*.json"):
        file.unlink()
    print(f"🗑️ Cleared {count} entries")

def stats():
    """Show cache statistics"""
    files = list(CACHE_DIR.glob("*.json"))
    total_size = sum(f.stat().st_size for f in files)
    
    expired = 0
    now = datetime.now()
    for f in files:
        with open(f) as fp:
            try:
                data = json.load(fp)
                if data["expires"]:
                    if now > datetime.fromisoformat(data["expires"]):
                        expired += 1
            except:
                pass
    
    print(f"\n📊 Cache Stats:")
    print(f"   Entries: {len(files)}")
    print(f"   Expired: {expired}")
    print(f"   Size: {total_size / 1024:.1f} KB")
    print(f"   Location: {CACHE_DIR}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        stats()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "set" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        ttl = int(sys.argv[4]) if len(sys.argv) > 4 else None
        set(key, value, ttl)
    
    elif cmd == "get" and len(sys.argv) >= 3:
        result = get(sys.argv[2])
        if result:
            print(f"   Value: {result}")
    
    elif cmd == "delete" and len(sys.argv) >= 3:
        delete(sys.argv[2])
    
    elif cmd == "clear":
        clear()
    
    elif cmd == "stats":
        stats()
    
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
