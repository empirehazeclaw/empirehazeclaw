#!/usr/bin/env python3
"""
Pattern Detector — CEO Autonomous System
Läuft: Nach Self-Review (Montags) + manuell
Erkennt: Wiederholende Task-Patterns → Skill-Vorschläge
Output: /workspace/ceo/PATTERN_ANALYSIS.md
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

WORKSPACE = "/home/clawbot/.openclaw/workspace"
PATTERN_OUTPUT = f"{WORKSPACE}/ceo/PATTERN_ANALYSIS.md"
SKILL_SUGGESTIONS = f"{WORKSPACE}/ceo/SKILL_SUGGESTIONS.md"
SOURCES = [
    f"{WORKSPACE}/ceo/TODO_IMPROVEMENTS.md",
    f"{WORKSPACE}/shared/TASK_BOARD.md",
    f"{WORKSPACE}/ceo/HEARTBEAT.md"
]

# Task type keywords to look for
TASK_KEYWORDS = [
    "security", "audit", "scan", "build", "code", "script",
    "data", "memory", "knowledge", "config", "cron", "heartbeat",
    "discord", "report", "validation", "test", "review"
]

def extract_tasks(content):
    """Extrahiert Task-Types aus Dokument."""
    tasks = []
    
    # Look for task-like patterns
    lines = content.split("\n")
    for line in lines:
        line_lower = line.lower()
        for keyword in TASK_KEYWORDS:
            if keyword in line_lower and ("task" in line_lower or "-" in line or "#" in line):
                tasks.append(keyword)
    
    return tasks

def analyze_patterns():
    """Analysiert alle Sources für Patterns."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    all_tasks = defaultdict(int)
    
    for source in SOURCES:
        if not os.path.exists(source):
            continue
        
        with open(source, "r") as f:
            content = f.read()
        
        tasks = extract_tasks(content)
        for task in tasks:
            all_tasks[task] += 1
    
    # Filter: nur Tasks die >2x vorkommen
    patterns = {k: v for k, v in all_tasks.items() if v > 2}
    
    return patterns, timestamp

def generate_skill_suggestions(patterns):
    """Generiert Skill-Vorschläge basierend auf Patterns."""
    suggestions = []
    
    for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
        if count >= 3:
            suggestions.append({
                "pattern": pattern,
                "occurrences": count,
                "skill_name": f"{pattern.capitalize()} Automation Skill",
                "description": f"Automatisierung für häufige {pattern}-Tasks",
                "priority": "high" if count >= 5 else "medium"
            })
    
    return suggestions

def generate_report(patterns, suggestions, timestamp):
    """Generiert das Pattern-Analyse-Report."""
    
    report = f"""# Pattern Analysis Report
**Datum:** {timestamp}
**CEO:** ClawMaster

---

## Gefundene Patterns

| Pattern | Häufigkeit | Status |
|---------|------------|--------|
"""
    
    for pattern, count in sorted(patterns.items(), key=lambda x: -x[1]):
        status = "🔴 HIGH" if count >= 5 else "🟡 MEDIUM" if count >= 3 else "🟢 LOW"
        report += f"| {pattern} | {count}x | {status} |\n"
    
    report += f"\n## Skill-Vorschläge\n\n"
    
    if suggestions:
        report += "| Pattern | Skill-Name | Priorität |\n"
        report += "|---------|------------|----------|\n"
        for s in suggestions:
            report += f"| {s['pattern']} | {s['skill_name']} | {s['priority']} |\n"
    else:
        report += "_Keine Patterns mit genug Häufigkeit für Skill-Vorschläge._\n"
    
    return report

def run():
    patterns, timestamp = analyze_patterns()
    suggestions = generate_skill_suggestions(patterns)
    report = generate_report(patterns, suggestions, timestamp)
    
    # Save Pattern Analysis
    with open(PATTERN_OUTPUT, "w") as f:
        f.write(report)
    
    # Save Skill Suggestions if any
    if suggestions:
        suggestions_content = f"# Skill Suggestions\n**Datum:** {timestamp}\n\n"
        suggestions_content += "## Vorschläge\n\n"
        for s in suggestions:
            suggestions_content += f"### {s['skill_name']}\n"
            suggestions_content += f"- **Pattern:** {s['pattern']} ({s['occurrences']}x)\n"
            suggestions_content += f"- **Beschreibung:** {s['description']}\n"
            suggestions_content += f"- **Priorität:** {s['priority']}\n\n"
        
        with open(SKILL_SUGGESTIONS, "w") as f:
            f.write(suggestions_content)
    
    print(f"✅ Pattern Detector: {len(patterns)} Patterns, {len(suggestions)} Skill-Vorschläge")
    return report

if __name__ == "__main__":
    run()