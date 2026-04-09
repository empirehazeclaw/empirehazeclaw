#!/usr/bin/env python3
"""
🔧 AUTO OPTIMIZER
================
"""

import os
import subprocess
from pathlib import Path

def optimize():
    print("🔧 Running optimizations...")
    
    # Clean old logs
    log_dir = Path("logs")
    if log_dir.exists():
        for f in log_dir.glob("*.log"):
            if f.stat().st_size > 10*1024*1024:  # > 10MB
                f.unlink()
                print(f"  Removed large log: {f.name}")
    
    # Clean temp files
    tmp_count = len(list(Path("/tmp").glob("tmp*"))) if Path("/tmp").exists() else 0
    print(f"  Temp files: {tmp_count}")
    
    # Check services
    services = ["openclaw", "nginx", "docker"]
    for s in services:
        result = subprocess.run(["pgrep", "-f", s], capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ {s}: running")
        else:
            print(f"  ⚠️ {s}: not running")
    
    print("✅ Optimization complete")

if __name__ == "__main__":
    optimize()
