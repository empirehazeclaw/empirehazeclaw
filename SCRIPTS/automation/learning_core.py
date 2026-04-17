#!/usr/bin/env python3
"""
Learning Core — Sir HazeClaw
============================
Consolidated hourly learning: Loop + Sync + Memory

Replaces:
- Learning Loop Hourly (:00)
- Memory Sync (:05)
- Learning Loop → KG Sync (:10)

Schedule: Hourly at :00
"""

import subprocess
import sys
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/workspace/logs/learning_core.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run_step(name, cmd, timeout=180):
    log(f"Running: {name}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            log(f"  ✓ {name}")
            return True, result.stdout[:300]
        else:
            log(f"  ✗ {name}: {result.stderr[:200]}")
            return False, result.stderr[:200]
    except Exception as e:
        log(f"  ✗ {name}: {e}")
        return False, str(e)[:200]

def main():
    log("="*50)
    log("Learning Core START")
    
    results = {}
    
    # 1. Learning Loop
    ok, out = run_step("Learning Loop", "python3 /home/clawbot/.openclaw/workspace/scripts/learning_loop_v3.py")
    results["loop"] = "OK" if ok else "FAILED"
    if "Score:" in out:
        score = [l for l in out.split("\n") if "Score:" in l]
        if score:
            log(f"  Loop Score: {score[0].strip()}")
    
    # 2. Memory Sync
    ok, out = run_step("Memory Sync", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/memory_sync.py")
    results["sync"] = "OK" if ok else "FAILED"
    
    # 3. KG Sync
    ok, out = run_step("KG Sync", "python3 /home/clawbot/.openclaw/workspace/scripts/learning_to_kg_sync.py --apply")
    results["kg_sync"] = "OK" if ok else "FAILED"
    
    # 4. Pattern Learning (from evaluation feedback)
    ok, out = run_step("Pattern Learning", "python3 /home/clawbot/.openclaw/workspace/ceo/scripts/pattern_learning_engine.py")
    results["pattern_learning"] = "OK" if ok else "FAILED"
    
    # 5. Signal Bridge (translate Learning Loop signals → Evolver signals)
    ok, out = run_step("Signal Bridge", "python3 /home/clawbot/.openclaw/workspace/ceo/scripts/signal_bridge.py --inject")
    results["signal_bridge"] = "OK" if ok else "FAILED"
    
    log(f"Learning Core END: {results}")
    
    summary = "🔄 Learning Core\n"
    for k, v in results.items():
        summary += f"  {k}: {v}\n"
    print(summary)

if __name__ == "__main__":
    main()
