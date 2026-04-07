#!/usr/bin/env python3
"""Simple memory search - MUST use before answering"""
import sys
from pathlib import Path

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/memory")
QUICK_FACTS = MEMORY_DIR / "QUICK_FACTS.md"

def check_facts():
    """Print quick facts - MUST do this before answering"""
    if QUICK_FACTS.exists():
        print("⚡ QUICK FACTS:")
        print(QUICK_FACTS.read_text()[:500])
    else:
        print("⚠️ NO QUICK FACTS!")

def search(query):
    """Search memory"""
    results = []
    for f in MEMORY_DIR.glob("*.md"):
        if "QUICK" in f.name:
            continue
        content = f.read_text().lower()
        if query.lower() in content:
            results.append(f.name)
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            check_facts()
        else:
            results = search(sys.argv[1])
            print(f"Found in: {results}")
    else:
        check_facts()
