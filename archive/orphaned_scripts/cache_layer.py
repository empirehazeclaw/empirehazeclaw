#!/usr/bin/env python3
"""
💾 CACHE LAYER
=============
Simple file-based caching (fallback if Redis unavailable)
"""

import json
import os
import time
from pathlib import Path

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(exist_ok=True, parents=True)

def get(key, max_age_seconds=3600):
    """Get cached value if not expired"""
    file = CACHE_DIR / f"{key}.json"
    if not file.exists():
        return None
    
    try:
        data = json.load(open(file))
        if time.time() - data["timestamp"] < max_age_seconds:
            return data["value"]
        else:
            # Expired
            file.unlink()
            return None
    except:
        return None

def set(key, value):
    """Set cached value"""
    file = CACHE_DIR / f"{key}.json"
    json.dump({
        "timestamp": time.time(),
        "value": value
    }, open(file, "w"))

def clear(key=None):
    """Clear cache"""
    if key:
        (CACHE_DIR / f"{key}.json").unlink(missing_ok=True)
    else:
        for f in CACHE_DIR.glob("*.json"):
            f.unlink()

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Cache Layer")
        print("  get <key>")
        print("  set <key> <value>")
        print("  clear [key]")
    elif sys.argv[1] == "get":
        print(get(sys.argv[2] if len(sys.argv) > 2 else ""))
    elif sys.argv[1] == "set":
        set(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "")
    elif sys.argv[1] == "clear":
        clear(sys.argv[2] if len(sys.argv) > 2 else None)
