#!/usr/bin/env python3
"""
🧠 AUTONOMOUS SKILL MANAGER
===========================
Analysiert System-Fehler, Engpässe und Todos, um selbstständig
neue Skills (Fähigkeiten) vorzuschlagen oder zu erstellen.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

WORKSPACE_DIR = Path('/home/clawbot/.openclaw/workspace')
SKILLS_DIR = WORKSPACE_DIR / 'skills'
LOGS_DIR = WORKSPACE_DIR / 'logs'
TODO_FILE = WORKSPACE_DIR / 'TODO.md'

def analyze_gaps():
    print(f"[{datetime.now().isoformat()}] 🔍 Analysiere fehlende Fähigkeiten...")
    gaps = []
    
    # 1. Check TODO.md for stuck items
    if TODO_FILE.exists():
        with open(TODO_FILE, 'r') as f:
            content = f.read()
            if "Gmail" in content or "OAuth" in content:
                gaps.append("gmail-automation")
            if "Traffic" in content or "TikTok" in content:
                gaps.append("shortform-video-marketing")
    
    # 2. Check Logs for recurring errors
    for log_file in LOGS_DIR.glob('*.log'):
        try:
            with open(log_file, 'r') as f:
                tail = f.readlines()[-50:]
                text = "".join(tail)
                if "403 Forbidden" in text and "xurl" in text:
                    gaps.append("twitter-api-recovery")
                if "Stripe" in text and "Error" in text:
                    gaps.append("stripe-debugger")
        except:
            pass

    # Deduplicate
    gaps = list(set(gaps))
    print(f"   🚨 Gefundene Lücken/Engpässe: {gaps}")
    return gaps

def create_skill_draft(gap_name):
    print(f"   🏗️ Erstelle Skill-Entwurf für: {gap_name}")
    skill_dir = SKILLS_DIR / gap_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    skill_file = skill_dir / 'SKILL.md'
    if not skill_file.exists():
        content = f"""---
name: {gap_name}
version: 1.0.0
description: |
  Automatisch generierter Skill zur Behebung des Engpasses '{gap_name}'.
  Dieser Skill wird kontinuierlich durch den Auto Optimizer verbessert.
allowed-tools:
  - exec
  - read
  - write
---

# {gap_name.replace('-', ' ').title()} Skill

## Problemstellung
Das System hat erkannt, dass die Fähigkeit für {gap_name} fehlt oder fehlerhaft ist.
Dieser Skill dient als Anleitung, wie Agenten dieses Problem zukünftig selbstständig lösen.

## Auto-Generierte Lösungsansätze
1. Analysiere die Fehlermeldungen in den Logs.
2. Recherchiere via `web_search` nach Workarounds für {gap_name}.
3. Implementiere ein robustes Python-Skript als Fallback.
"""
        with open(skill_file, 'w') as f:
            f.write(content)
        print(f"   ✅ Skill {gap_name} erfolgreich angelegt unter {skill_file}")

def run():
    print("🧠 Starte Autonomous Skill Manager...")
    gaps = analyze_gaps()
    for gap in gaps:
        create_skill_draft(gap)
    print("✅ Skill-Management abgeschlossen.")

if __name__ == "__main__":
    run()
