#!/usr/bin/env python3
"""
Auto Memory Logger
Trägt wichtige Decisions automatisch ins Memory ein
"""
import sys
from datetime import datetime

def log_decision(decision, category="general"):
    """Loggt eine wichtige Decision"""
    with open("/home/clawbot/.openclaw/workspace/memory/TODO.md", "a") as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d')} - {category}\n- {decision}\n")
    print(f"✓ Logged: {decision}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_decision(" ".join(sys.argv[1:]))
