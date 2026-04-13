#!/usr/bin/env python3
"""
KG Enhancer - Fügt wichtige Entries zum Knowledge Graph hinzu.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
KG_PATH = WORKSPACE / "core_ultralight/memory/knowledge_graph.json"

# Neue Entries für den KG
NEW_ENTITIES = {
    "Sir-HazeClaw-Scripts": {
        "type": "category",
        "facts": [
            {"content": "Test Framework: 62 Tests, alle passing", "source": "test_framework.py"},
            {"content": "Fast Test Runner: 17 tests in 30s, 10s timeout, threaded", "source": "fast_test.py"},
            {"content": "Morning Check: Quick morning status", "source": "morning_check.py"},
            {"content": "Habit Tracker: 8 habits, streak tracking", "source": "habit_tracker.py"},
            {"content": "Morning Routine: Automatisiert 6 morning checks", "source": "morning_routine.py"},
            {"content": "Evening Routine: Automatisiert evening workflow", "source": "evening_routine.py"},
            {"content": "Self-Evaluation: Trackt goals vs current state (Score 84/100)", "source": "self_eval.py"},
            {"content": "Quality Metrics: Commit/Backup tracking", "source": "quality_metrics.py"},
            {"content": "Deep Reflection: 10 deep questions für improvement", "source": "deep_reflection.py"},
            {"content": "Reflection Loop: Analysiert patterns, self-corrects", "source": "reflection_loop.py"},
            {"content": "Security Audit: Prüft auf code injection risks", "source": "security_audit.py"},
        ]
    },
    "AI-Agent-Prompt-Patterns": {
        "type": "pattern",
        "facts": [
            {"content": "Pattern 1: Role + Constraints - Definiere wer und was NICHT", "source": "research 2026-04-10"},
            {"content": "Pattern 2: Chain of Verification - Output vor Aktion prüfen", "source": "research 2026-04-10"},
            {"content": "Pattern 3: Structured Output - Klare Kommunikation", "source": "research 2026-04-10"},
            {"content": "Pattern 4: Error Recovery - Explizite Fehlerbehandlung", "source": "research 2026-04-10"},
            {"content": "Pattern 5: Guard Rails - Sicherheitsgrenzen", "source": "research 2026-04-10"},
        ]
    },
    "Research-Skill": {
        "type": "skill",
        "facts": [
            {"content": "Web Search: Brave Search API integration", "source": "skills/research"},
            {"content": "Web Fetch: URL content extraction", "source": "skills/research"},
            {"content": "Pattern: Quick Research -> Deep Research -> Document", "source": "skills/research"},
        ]
    },
    "Self-Improvement-Patterns": {
        "type": "pattern",
        "facts": [
            {"content": "Test Coverage: Ziel >80%, aktuell 29%", "source": "self_eval.py"},
            {"content": "Quality Score: 70/100 - Test Coverage ist Schwachstelle", "source": "self_eval.py"},
            {"content": "Commit Rhythm: 100+ commits/Tag möglich bei Fokus", "source": "quality_metrics.py"},
            {"content": "Habit Streaks: Automatisch getrackt seit 2026-04-10", "source": "habit_tracker.py"},
        ]
    },
    "Sir-HazeClaw-Capabilities": {
        "type": "category",
        "facts": [
            {"content": "Solo Fighter Mode: CEO als Hauptagent", "source": "AGENTS.md"},
            {"content": "Proaktiv: Handelt ohne zu warten", "source": "SOUL.md"},
            {"content": "Ehrlichkeit: Fehler sind OK, Lügen nicht", "source": "SOUL.md"},
            {"content": "Prävention: Probleme verhindern BEVOR sie passieren", "source": "SOUL.md"},
        ]
    },
    "System-Architektur": {
        "type": "knowledge",
        "facts": [
            {"content": "Gateway: Port 18789, OpenClaw service", "source": "HEARTBEAT.md"},
            {"content": "Memory: KG mit 175 entities, 4649 relations", "source": "KG stats"},
            {"content": "Crons: 8 aktiv, 24 deaktiviert", "source": "cron_monitor.py"},
            {"content": "Scripts: 61 total, 18 getestet (29% coverage)", "source": "test_framework.py"},
        ]
    },
    "Bad-Patterns-SirHazeClaw": {
        "type": "pattern",
        "facts": [
            {"content": "Loop Prevention: Niemals denselben Task 2x starten", "source": "LOOP_PREVENTION.md"},
            {"content": "Quality über Quantität: Nicht mehr Commits um der Commits willen", "source": "SOUL.md"},
            {"content": "NIEMALS ClawHub Skills installieren - selbst bauen", "source": "SOUL.md"},
        ]
    },
    "Good-Patterns-SirHazeClaw": {
        "type": "pattern",
        "facts": [
            {"content": "Morning/Evening Routines: Automatisiert", "source": "morning_routine.py"},
            {"content": "Test-Framework: 18 tests, alle passend", "source": "test_framework.py"},
            {"content": "Self-Evaluation: Täglich aktuell", "source": "self_eval.py"},
            {"content": "HEARTBEAT.md: Aktiver Stand der Tasks", "source": "HEARTBEAT.md"},
        ]
    }
}

NEW_RELATIONS = [
    {"from": "Sir-HazeClaw", "to": "Sir-HazeClaw-Scripts", "type": "created"},
    {"from": "Sir-HazeClaw", "to": "Self-Improvement-Patterns", "type": "uses"},
    {"from": "Sir-HazeClaw", "to": "System-Architektur", "type": "manages"},
    {"from": "Sir-HazeClaw", "to": "Good-Patterns-SirHazeClaw", "type": "follows"},
    {"from": "Sir-HazeClaw", "to": "Bad-Patterns-SirHazeClaw", "type": "avoids"},
    {"from": "Test-Framework", "to": "Sir-HazeClaw-Scripts", "type": "tests"},
    {"from": "Self-Evaluation", "to": "Self-Improvement-Patterns", "type": "tracks"},
    {"from": "Habit-Tracker", "to": "Sir-HazeClaw", "type": "supports"},
    {"from": "Morning-Routine", "to": "Sir-HazeClaw", "type": "supports"},
    {"from": "Evening-Routine", "to": "Sir-HazeClaw", "type": "supports"},
]

def load_kg():
    """Lädt KG."""
    with open(KG_PATH) as f:
        return json.load(f)

def save_kg(kg):
    """Speichert KG."""
    with open(KG_PATH, 'w') as f:
        json.dump(kg, f, indent=2)

def add_entries():
    """Fügt neue Entries zum KG hinzu."""
    kg = load_kg()
    
    entities = kg.get('entities', {})
    relations = kg.get('relations', [])
    
    added_entities = 0
    added_relations = 0
    
    # Add entities
    for entity_name, entity_data in NEW_ENTITIES.items():
        if entity_name not in entities:
            entities[entity_name] = entity_data
            added_entities += 1
        else:
            # Update facts
            existing = entities[entity_name]
            if 'facts' not in existing:
                existing['facts'] = []
            existing_facts = set(f['content'] for f in existing.get('facts', []))
            for fact in entity_data.get('facts', []):
                if fact['content'] not in existing_facts:
                    existing['facts'].append(fact)
                    added_entities += 1
    
    # Add relations
    existing_relations = set((r['from'], r['to'], r['type']) for r in relations)
    for rel in NEW_RELATIONS:
        if (rel['from'], rel['to'], rel['type']) not in existing_relations:
            relations.append(rel)
            added_relations += 1
    
    kg['entities'] = entities
    kg['relations'] = relations
    
    save_kg(kg)
    
    return added_entities, added_relations

def generate_report():
    """Generiert Report."""
    kg = load_kg()
    
    lines = []
    lines.append("📊 **KG ENHANCER REPORT**")
    lines.append(f"_Generated: {datetime.now().strftime('%H:%M UTC')}_")
    lines.append("")
    lines.append(f"**KG Stats:**")
    lines.append(f"  - Entities: {len(kg.get('entities', {}))}")
    lines.append(f"  - Relations: {len(kg.get('relations', []))}")
    lines.append("")
    lines.append("**Added Categories:**")
    for entity_name in NEW_ENTITIES.keys():
        lines.append(f"  - {entity_name}")
    lines.append("")
    lines.append("**New Relations:**")
    for rel in NEW_RELATIONS[:5]:
        lines.append(f"  - {rel['from']} → {rel['to']}")
    if len(NEW_RELATIONS) > 5:
        lines.append(f"  - ... and {len(NEW_RELATIONS) - 5} more")
    
    return "\n".join(lines)

def main():
    print("🔄 Adding entries to Knowledge Graph...")
    added_e, added_r = add_entries()
    print(f"   ✅ Added {added_e} entity updates, {added_r} new relations")
    print()
    print(generate_report())

if __name__ == "__main__":
    main()
