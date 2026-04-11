#!/usr/bin/env python3
"""
pattern_extractor.py — Sir HazeClaw Self-Improvement
Extrahiert wiederverwendbare Patterns nach Tasks.

Usage:
    python3 pattern_extractor.py --task "Was ich getan habe" --outcome "Ergebnis"
    python3 pattern_extractor.py --auto  # Analysiert letzte Session
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
PATTERNS_FILE = WORKSPACE / "skills" / "_library" / "patterns.json"
LEARNINGS_FILE = WORKSPACE / "memory" / "learnings.json"

def ensure_dirs():
    """Erstellt notwendige Directories."""
    (WORKSPACE / "skills" / "_library").mkdir(parents=True, exist_ok=True)
    (WORKSPACE / "memory").mkdir(parents=True, exist_ok=True)

def load_patterns():
    """Lädt existierende Patterns."""
    if PATTERNS_FILE.exists():
        with open(PATTERNS_FILE) as f:
            return json.load(f)
    return {"patterns": [], "by_category": {}}

def save_patterns(data):
    """Speichert Patterns."""
    with open(PATTERNS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def extract_pattern(task: str, outcome: str, category: str = "general") -> dict:
    """Extrahiert ein Pattern aus Task/Outcome."""
    pattern = {
        "id": f"pat_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "task": task,
        "outcome": outcome,
        "category": category,
        "created": datetime.now().isoformat(),
        "success": "success" if outcome.lower().startswith("success") or outcome.lower().startswith("✅") else "partial"
    }
    return pattern

def add_pattern(pattern: dict):
    """Fügt Pattern zur Library hinzu."""
    data = load_patterns()
    data["patterns"].append(pattern)
    
    # Index by category
    cat = pattern["category"]
    if cat not in data["by_category"]:
        data["by_category"][cat] = []
    data["by_category"][cat].append(pattern["id"])
    
    save_patterns(data)
    print(f"✅ Pattern added: {pattern['id']}")

def suggest_category(task: str) -> str:
    """Schlägt Category basierend auf Task-Inhalt vor."""
    task_lower = task.lower()
    
    if any(x in task_lower for x in ["debug", "error", "fix", "crash"]):
        return "debugging"
    elif any(x in task_lower for x in ["research", "search", "find"]):
        return "research"
    elif any(x in task_lower for x in ["code", "script", "implement"]):
        return "coding"
    elif any(x in task_lower for x in ["doc", "write", "readme"]):
        return "documentation"
    elif any(x in task_lower for x in ["test", "check", "verify"]):
        return "testing"
    else:
        return "general"

def main():
    ensure_dirs()
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n📝 Letzte Patterns:")
        data = load_patterns()
        for p in data["patterns"][-5:]:
            print(f"  [{p['category']}] {p['task'][:50]}...")
        return
    
    # Parse args
    task = outcome = category = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--task" and i+1 < len(sys.argv):
            task = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--outcome" and i+1 < len(sys.argv):
            outcome = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--category" and i+1 < len(sys.argv):
            category = sys.argv[i+1]
            i += 2
        elif sys.argv[i] == "--auto":
            # Auto mode - analyze recent memory
            print("🔍 Auto-Analyse nicht implementiert (würde Sessions analysieren)")
            return
        else:
            i += 1
    
    if not task:
        print("❌ --task required")
        return
    
    if not outcome:
        outcome = "success"
    
    if not category:
        category = suggest_category(task)
    
    pattern = extract_pattern(task, outcome, category)
    add_pattern(pattern)
    
    print(f"\n📚 Pattern Library: {PATTERNS_FILE}")

if __name__ == "__main__":
    main()
