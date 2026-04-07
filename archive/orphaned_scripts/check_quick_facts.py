#!/usr/bin/env python3
"""
⚡ Quick Facts Checker
Must run before any response
"""
import os
from pathlib import Path

QUICK_FACTS = Path("/home/clawbot/.openclaw/workspace/memory/QUICK_FACTS.md")

def load_quick_facts():
    """Load quick facts"""
    if QUICK_FACTS.exists():
        return QUICK_FACTS.read_text()
    return ""

def check_before_answering():
    """Call this before answering"""
    facts = load_quick_facts()
    # Check for common phrases I forget
    if "xurl" in facts and "WORKS" in facts:
        # Don't say "need tokens" for xurl
        pass
    return facts

# Run on import
if __name__ == "__main__":
    print("⚡ Quick Facts loaded:")
    print(load_quick_facts()[:200])
