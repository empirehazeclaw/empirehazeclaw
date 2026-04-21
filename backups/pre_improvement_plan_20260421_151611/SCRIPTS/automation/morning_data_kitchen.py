#!/usr/bin/env python3
"""
Morning Data Kitchen — Sir HazeClaw
====================================
Consolidated morning data cleanup and generation.

Replaces:
- Short-Term Recall Cleanup (05h)
- REM Feedback Integration (06h)
- Daily Semantic Embedding Update (06h)
- Backup Verifier (06h)

Schedule: 06:00 UTC daily
"""

import subprocess
import sys
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/workspace/logs/morning_kitchen.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")

def run_step(name, cmd, timeout=120):
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
    log("Morning Data Kitchen START")
    
    results = {}
    
    # 1. Short-Term Recall Cleanup
    ok, out = run_step("Short-Term Cleanup", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/self_healing/truncate_short_term_recall.py")
    results["short_term"] = "OK" if ok else "FAILED"
    
    # 2. Semantic Embeddings Update
    ok, out = run_step("Semantic Embeddings", "python3 /home/clawbot/.openclaw/workspace/ceo/memory/semantic/embedding_generator.py --all")
    results["semantic"] = "OK" if ok else "FAILED"
    
    # 3. REM Feedback
    ok, out = run_step("REM Feedback", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/rem_feedback.py")
    results["rem"] = "OK" if ok else "FAILED"
    
    # 4. Backup Verifier
    ok, out = run_step("Backup Verifier", "python3 /home/clawbot/.openclaw/workspace/SCRIPTS/automation/backup_verifier.py")
    results["backup"] = "OK" if ok else "FAILED"
    
    log(f"Morning Data Kitchen END: {results}")
    
    summary = "🧹 Morning Data Kitchen\n"
    for k, v in results.items():
        summary += f"  {k}: {v}\n"
    print(summary)

if __name__ == "__main__":
    main()
