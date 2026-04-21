#!/usr/bin/env python3
"""
Sir HazeClaw Skill Creator
Erstellt neue Skills aus wiederkehrenden Tasks.

Basierend auf OpenSpace Pattern: "Jeder Task macht alle Agents klüger"
46% Token Reduction durch Pattern Reuse.

Usage:
    python3 skill_creator.py --create <task_name>
    python3 skill_creator.py --list
    python3 skill_creator.py --extract <task_description>
"""

import sys
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
SKILLS_DIR = WORKSPACE / "skills"
SKILL_LOG = WORKSPACE / "data/skill_creation_log.json"

def load_log():
    if SKILL_LOG.exists():
        with open(SKILL_LOG) as f:
            return json.load(f)
    return {"created": [], "templates": {}}

def save_log(log):
    SKILL_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SKILL_LOG, 'w') as f:
        json.dump(log, f, indent=2)

def get_skill_template(skill_name, description):
    """Generiert Skill Template basierend auf OpenSpace Pattern."""
    
    template = f"""---
name: {skill_name.lower().replace(' ', '-')}
description: Auto-created skill from recurring task pattern.
tags: [auto-created, {skill_name.lower()}]
permissions: [network, shell]
---

# {skill_name.title()}

**Created:** {datetime.now().strftime('%Y-%m-%d')}  
**Source:** Skill Creator (OpenSpace Pattern)  
**Purpose:** {description}

## Usage

```bash
python3 $WORKSPACE/scripts/{skill_name.lower().replace(' ', '_')}.py
```

## Implementation

<!-- TODO: Implement the skill logic -->

## Patterns Learned

<!-- Document reusable patterns here -->

---

*Auto-created by Sir HazeClaw Skill Creator*
*Part of: Learning Loop v3 Innovation Phase*
"""
    return template

def create_skill(skill_name, description):
    """Erstellt einen neuen Skill."""
    
    # Validate name
    safe_name = skill_name.lower().replace(' ', '-').replace('_', '-')
    
    # Check if exists
    skill_path = SKILLS_DIR / safe_name
    if skill_path.exists():
        print(f"⚠️ Skill '{safe_name}' exists already")
        return False
    
    # Create directory
    skill_path.mkdir(parents=True, exist_ok=True)
    
    # Create SKILL.md
    skill_md = skill_path / "SKILL.md"
    skill_md.write_text(get_skill_template(safe_name, description))
    
    # Create index.py (placeholder)
    index_py = skill_path / "index.js" if skill_path.name.startswith('auto-') else skill_path / "index.py"
    
    # Log
    log = load_log()
    log["created"].append({
        "name": safe_name,
        "description": description,
        "created": datetime.now().isoformat()
    })
    save_log(log)
    
    print(f"✅ Skill created: {safe_name}")
    print(f"   Path: {skill_path}")
    return True

def extract_pattern(task_description):
    """Extrahiert Pattern aus Task-Beschreibung."""
    
    print(f"🔍 **Pattern Extraction**")
    print(f"   Task: {task_description}")
    print()
    
    # Analyze task
    keywords = {
        "repeat": ["loop", "repeated", " recurring"],
        "automate": ["script", "schedule", "cron"],
        "analyze": ["parse", "extract", "search"],
        "communicate": ["message", "notify", "alert"],
        "optimize": ["improve", "reduce", "enhance"]
    }
    
    detected = []
    task_lower = task_description.lower()
    for category, words in keywords.items():
        for word in words:
            if word in task_lower:
                detected.append(category)
    
    print(f"   Detected patterns: {', '.join(detected) if detected else 'None'}")
    print()
    
    # Generate recommendation
    if "repeat" in detected or "automate" in detected:
        print("💡 Recommendation: Create a script that runs on schedule")
        print("   → Use cron + script + notification")
    
    if "analyze" in detected:
        print("💡 Recommendation: Create parsing/extraction skill")
        print("   → Use regex, structured output, KG storage")
    
    if "communicate" in detected:
        print("💡 Recommendation: Create notification/messaging skill")
        print("   → Use message tool, Telegram integration")
    
    if "optimize" in detected:
        print("💡 Recommendation: Create optimization loop")
        print("   → Use metrics tracking, incremental improvements")
    
    return detected

def list_skills():
    """Listet alle Skills auf."""
    print("📦 **Skills Overview**")
    print()
    
    if not SKILLS_DIR.exists():
        print("   No skills directory")
        return
    
    skills = []
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            skills.append(item.name)
    
    print(f"   Total: {len(skills)}")
    print()
    
    for skill in sorted(skills):
        print(f"   • {skill}")

def main():
    if len(sys.argv) < 2:
        list_skills()
        return 0
    
    cmd = sys.argv[1]
    
    if cmd == "--create" and len(sys.argv) > 3:
        skill_name = sys.argv[2]
        description = sys.argv[3]
        return 0 if create_skill(skill_name, description) else 1
    
    elif cmd == "--extract" and len(sys.argv) > 2:
        task = ' '.join(sys.argv[2:])
        extract_pattern(task)
        return 0
    
    elif cmd == "--list":
        list_skills()
        return 0
    
    else:
        print("Usage:")
        print("  skill_creator.py --list")
        print("  skill_creator.py --create <name> <description>")
        print("  skill_creator.py --extract <task_description>")
        return 1

if __name__ == "__main__":
    sys.exit(main())
