#!/usr/bin/env python3
"""
Research Cache Cleanup - Clears old research data
"""

import os
import shutil
from datetime import datetime, timedelta

CACHE_DIRS = [
    "/home/clawbot/.openclaw/workspace/.cache",
    "/home/clawbot/.openclaw/workspace/__pycache__",
    "/home/clawbot/.openclaw/workspace/scripts/__pycache__",
]

def cleanup_cache():
    """Remove old cache files"""
    total_removed = 0
    
    for cache_dir in CACHE_DIRS:
        if not os.path.exists(cache_dir):
            continue
            
        count = 0
        for item in os.listdir(cache_dir):
            path = os.path.join(cache_dir, item)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    count += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    count += 1
            except Exception:
                pass
        
        total_removed += count
        print(f"🗑️ {cache_dir}: {count} items removed")
    
    print(f"\n✅ Total: {total_removed} cache files cleaned")

if __name__ == "__main__":
    print(f"📦 Research Cache Cleanup - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    cleanup_cache()
