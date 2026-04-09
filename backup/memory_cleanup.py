#!/usr/bin/env python3
"""Memory & Knowledge Cleanup Script"""

import os
import gzip
import shutil
from datetime import datetime, timedelta

MEMORY_PATH = "/home/clawbot/.openclaw/workspace/memory"
ARCHIVE_PATH = f"{MEMORY_PATH}/archive"

def cleanup_old_daily():
    """Move old daily files to archive, compress"""
    print("🧹 Cleanup started...")
    
    # Files older than 7 days
    cutoff = datetime.now() - timedelta(days=7)
    
    for filename in os.listdir(MEMORY_PATH):
        if not filename.startswith("2026-"):
            continue
            
        filepath = os.path.join(MEMORY_PATH, filename)
        if os.path.isfile(filepath):
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            if mtime < cutoff:
                # Compress and move
                dest = os.path.join(ARCHIVE_PATH, filename)
                with open(filepath, 'rb') as f_in:
                    with gzip.open(dest + '.gz', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                os.remove(filepath)
                print(f"  ✅ Archived: {filename}")
    
    print("✅ Cleanup done!")

if __name__ == "__main__":
    cleanup_old_daily()
