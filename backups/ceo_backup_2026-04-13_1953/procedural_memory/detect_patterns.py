#!/usr/bin/env python3
"""
🔍 Procedural Memory — Pattern Recognition
Erkennt repetitive Tasks und schlägt Automatisierungen vor
"""

import json
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
PATTERNS_DIR = WORKSPACE / "ceo/procedural_memory/patterns"
SUGGESTIONS_DIR = WORKSPACE / "ceo/procedural_memory/suggestions"
TASK_HISTORY = WORKSPACE / "shared/TASK_BOARD.md"
TODO_FILE = WORKSPACE / "ceo/TODO_IMPROVEMENTS.md"

# Thresholds
THRESHOLD_TASK = 3
THRESHOLD_ERROR = 2
THRESHOLD_SEQUENCE = 2

def parse_task_board():
    """Parst TASK_BOARD.md für Task-Typen"""
    tasks = []
    
    if not TASK_HISTORY.exists():
        return tasks
    
    with open(TASK_HISTORY) as f:
        content = f.read()
    
    lines = content.split("\n")
    for line in lines:
        if "|" in line and "-" not in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                tasks.append({
                    "id": parts[0],
                    "task": parts[1] if len(parts) > 1 else "",
                    "agent": parts[2] if len(parts) > 2 else "",
                    "status": parts[3] if len(parts) > 3 else ""
                })
    
    return tasks

def detect_task_patterns(tasks):
    """Erkennt Task-Typen die häufig vorkommen"""
    task_types = defaultdict(int)
    
    for task in tasks:
        # Extrahiere Task-Type aus Task-Beschreibung
        task_name = task.get("task", "").lower()
        
        # Einfache Keyword-Extraktion
        keywords = []
        for word in task_name.split():
            if len(word) > 4:  # Nur längere Wörter
                keywords.append(word)
        
        for kw in keywords:
            task_types[kw] += 1
    
    # Filter: nur die mit Threshold
    patterns = []
    for kw, count in task_types.items():
        if count >= THRESHOLD_TASK:
            patterns.append({
                "type": "task_repeat",
                "keyword": kw,
                "occurrences": count,
                "suggestion": {
                    "action": "skill",
                    "description": f"Skill für '{kw}' Tasks erstellen",
                    "priority": "high" if count >= 5 else "medium"
                }
            })
    
    return patterns

def save_patterns(patterns):
    """Speichert erkannte Patterns"""
    os.makedirs(PATTERNS_DIR, exist_ok=True)
    
    if not patterns:
        print("⚠️ No patterns detected")
        return
    
    patterns_file = PATTERNS_DIR / f"patterns_{datetime.utcnow().strftime('%Y%m%d')}.json"
    
    with open(patterns_file, "w") as f:
        json.dump(patterns, f, indent=2)
    
    print(f"✅ Saved {len(patterns)} patterns to {patterns_file.name}")

def generate_suggestions(patterns):
    """Generiert Automatisierungs-Vorschläge"""
    os.makedirs(SUGGESTIONS_DIR, exist_ok=True)
    
    high_priority = [p for p in patterns if p.get("suggestion", {}).get("priority") == "high"]
    
    if high_priority:
        suggestions_file = SUGGESTIONS_DIR / f"suggestions_{datetime.utcnow().strftime('%Y%m%d')}.md"
        
        with open(suggestions_file, "w") as f:
            f.write("# 🤖 Automatisierungs-Vorschläge\n\n")
            f.write(f"**Datum:** {datetime.utcnow().isoformat()[:10]}\n\n")
            
            for i, p in enumerate(high_priority, 1):
                f.write(f"## {i}. {p['keyword']} ( {p['occurrences']}x )\n")
                f.write(f"**Typ:** {p['type']}\n")
                f.write(f"**Vorschlag:** {p['suggestion']['description']}\n\n")
        
        print(f"✅ Generated suggestion file: {suggestions_file.name}")
    
    return high_priority

def run():
    print("🔍 Procedural Memory — Pattern Detection...")
    
    # Parse Task History
    tasks = parse_task_board()
    print(f"📊 Found {len(tasks)} tasks in history")
    
    # Detect Patterns
    patterns = detect_task_patterns(tasks)
    print(f"🔍 Detected {len(patterns)} patterns")
    
    if patterns:
        # Save Patterns
        save_patterns(patterns)
        
        # Generate Suggestions
        suggestions = generate_suggestions(patterns)
        print(f"💡 {len(suggestions)} high-priority suggestions generated")

if __name__ == "__main__":
    run()