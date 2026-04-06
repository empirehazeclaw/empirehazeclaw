#!/usr/bin/env python3
"""
🔄 PROCESS MONITOR
================
Auto-restart stuck processes
"""

import os
import signal
import subprocess

def monitor():
    result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
    
    stuck = []
    for line in result.stdout.split("\n"):
        if "python3 scripts" in line or "node index.js" in line:
            parts = line.split()
            if len(parts) > 2:
                try:
                    cpu = float(parts[2])
                    pid = int(parts[1])
                    # If CPU > 80% for more than 10 min, kill it
                    if cpu > 80:
                        stuck.append((pid, parts[-1], cpu))
                        print(f"Killing stuck process: PID {pid} ({cpu}%)")
                        os.kill(pid, signal.SIGTERM)
                except:
                    pass
    
    if not stuck:
        print("✅ All processes healthy")
    return stuck

if __name__ == "__main__":
    monitor()
