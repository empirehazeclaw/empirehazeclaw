#!/usr/bin/env python3
"""
Context Compressor — Sir HazeClaw
Analyzes and compresses large session files to save storage.

Usage:
    python3 context_compressor.py --scan     # Scan session sizes
    python3 context_compressor.py --compress # Compress large sessions
    python3 context_compressor.py --limit 50000 # Only show sessions >50KB
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SESSIONS_DIR = Path("/home/clawbot/.openclaw/agents/ceo/sessions")
TARGET_SIZE_KB = 500  # Compress sessions > 500KB
MAX_STORED_SIZE_KB = 200  # Keep only last 200KB

def get_session_size(filepath: Path) -> int:
    """Returns file size in KB."""
    try:
        return filepath.stat().st_size // 1024
    except:
        return 0

def scan_sessions(limit_kb: int = 0) -> list:
    """Scans sessions, returns list of (filepath, size_kb, modified) tuples."""
    sessions = []
    for f in SESSIONS_DIR.glob("*.jsonl"):
        if f.name.endswith(".deleted."):
            continue
        size_kb = get_session_size(f)
        if limit_kb == 0 or size_kb > limit_kb:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            sessions.append((str(f), size_kb, mtime))
    return sorted(sessions, key=lambda x: -x[1])

def compress_session(filepath: Path, max_keep_kb: int = MAX_STORED_SIZE_KB) -> dict:
    """Compresses a session by keeping only recent entries."""
    result = {
        "original_size_kb": get_session_size(filepath),
        "compressed": False,
        "entries_removed": 0
    }
    
    try:
        # Read current content
        with open(filepath) as f:
            lines = f.readlines()
        
        if len(lines) <= 10:
            return {"compressed": False, "reason": "Too few entries"}
        
        # Calculate target lines (keep last ~max_keep_kB worth)
        avg_line_size = sum(len(l) for l in lines[-100:]) / min(100, len(lines))
        target_lines = int(max_keep_kb * 1024 / avg_line_size)
        target_lines = max(target_lines, 50)  # Keep at least 50 lines
        
        if len(lines) <= target_lines:
            return {"compressed": False, "reason": "Already small enough"}
        
        # Keep only recent lines
        entries_to_remove = len(lines) - target_lines
        compressed_lines = lines[-target_lines:]
        
        # Write back
        with open(filepath, 'w') as f:
            f.writelines(compressed_lines)
        
        result["compressed"] = True
        result["entries_removed"] = entries_to_remove
        result["new_size_kb"] = get_session_size(filepath)
        
    except Exception as e:
        return {"compressed": False, "error": str(e)}
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Context Compressor for Sessions")
    parser.add_argument("--scan", action="store_true", help="Scan session sizes")
    parser.add_argument("--compress", action="store_true", help="Compress large sessions")
    parser.add_argument("--limit", type=int, default=0, help="Only show > limit KB")
    args = parser.parse_args()
    
    if args.scan:
        print("📊 SESSION SIZE SCAN")
        print("=" * 60)
        sessions = scan_sessions(limit_kb=args.limit)
        total_size = sum(s[1] for s in sessions)
        print(f"Total sessions: {len(sessions)}")
        print(f"Total size: {total_size} KB ({total_size/1024:.1f} MB)")
        print()
        for path, size, mtime in sessions[:30]:
            print(f"{size:6} KB  {mtime.strftime('%Y-%m-%d %H:%M')}  {Path(path).name[:40]}")
        if len(sessions) > 30:
            print(f"... and {len(sessions)-30} more")
    
    elif args.compress:
        print("🗜️ SESSION COMPRESSION")
        print("=" * 60)
        sessions = scan_sessions(limit_kb=TARGET_SIZE_KB)
        print(f"Sessions to compress: {len(sessions)}")
        print()
        
        compressed_count = 0
        for path, size, mtime in sessions:
            result = compress_session(Path(path))
            if result.get("compressed"):
                compressed_count += 1
                print(f"✅ {Path(path).name[:40]} - removed {result['entries_removed']} entries, {result['original_size_kb']}→{result['new_size_kb']} KB")
        
        print()
        print(f"Compressed {compressed_count} sessions")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()