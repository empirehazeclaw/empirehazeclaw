#!/usr/bin/env python3
"""
🔄 Auto-Skill Creator & Learning Loop
Speichert gelöste Probleme als wiederverwendbare Skills
"""
import json
import os
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path("/home/clawbot/.openclaw/workspace/skills")
LEARNINGS_FILE = Path("/home/clawbot/.openclaw/workspace/memory/learnings.json")
SKILL_TEMPLATE = """# {name}

{description}

## When to Use
{when_to_use}

## How to Use
```bash
{usage}
```

## Example
{example}

---

*Auto-generated: {date}*
*Learned from: {learned_from}*
"""

def save_learnings(learnings: dict):
    """Speichert Learnings"""
    LEARNINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNINGS_FILE, "w") as f:
        json.dump(learnings, f, indent=2)

def load_learnings() -> dict:
    """Lädt Learnings"""
    if LEARNINGS_FILE.exists():
        with open(LEARNINGS_FILE, "r") as f:
            return json.load(f)
    return {"learnings": [], "skills": []}

def register_skill(name: str, description: str, when_to_use: str, 
                   usage: str, example: str, learned_from: str = "unknown"):
    """Erstellt einen neuen Skill aus einer Lösung"""
    skill_path = SKILL_DIR / f"{name.lower().replace(' ', '_')}.md"
    
    content = SKILL_TEMPLATE.format(
        name=name,
        description=description,
        when_to_use=when_to_use,
        usage=usage,
        example=example,
        date=datetime.now().isoformat(),
        learned_from=learned_from
    )
    
    skill_path.write_text(content)
    print(f"✅ Skill erstellt: {skill_path.name}")
    
    # Update learnings.json
    learnings = load_learnings()
    learnings["skills"].append({
        "name": name,
        "file": str(skill_path),
        "created": datetime.now().isoformat(),
        "learned_from": learned_from
    })
    save_learnings(learnings)
    
    return skill_path

def learn_from_problem(problem: str, solution: str, context: str = ""):
    """Lernt aus einem gelösten Problem"""
    learnings = load_learnings()
    
    entry = {
        "problem": problem,
        "solution": solution,
        "context": context,
        "solved_at": datetime.now().isoformat(),
        "skill_created": False
    }
    
    # Check ob Lösung komplex genug für Skill
    if len(solution) > 200 and len(problem) > 20:
        # Auto-Skill vorschlagen
        skill_name = f"auto_{problem[:30].lower().replace(' ', '_')}"
        register_skill(
            name=skill_name,
            description=f"Automatisch erstellt aus Problem: {problem[:100]}",
            when_to_use=f"Wenn {problem.lower()}",
            usage=f"python3 scripts/{skill_name}.py",
            example=solution[:500],
            learned_from=context or "auto_detection"
        )
        entry["skill_created"] = True
    
    learnings["learnings"].append(entry)
    save_learnings(learnings)
    
    return entry

def get_relevant_learnings(query: str) -> list:
    """Findet relevante Learnings zu einer Query"""
    learnings = load_learnings()
    query_lower = query.lower()
    
    relevant = []
    for entry in learnings.get("learnings", []):
        if query_lower in entry.get("problem", "").lower() or \
           query_lower in entry.get("solution", "").lower():
            relevant.append(entry)
    
    return relevant[-5:]  # Letzte 5

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🔄 Auto-Skill Creator")
        print("")
        print("Usage:")
        print("  python3 auto_skill_creator.py learn <problem> <solution> [context]")
        print("  python3 auto_skill_creator.py search <query>")
        print("  python3 auto_skill_creator.py register <name> <desc> <when> <usage>")
        print("  python3 auto_skill_creator.py list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "learn" and len(sys.argv) >= 4:
        problem = sys.argv[2]
        solution = sys.argv[3]
        context = sys.argv[4] if len(sys.argv) > 4 else ""
        learn_from_problem(problem, solution, context)
    
    elif cmd == "search" and len(sys.argv) >= 3:
        query = sys.argv[2]
        results = get_relevant_learnings(query)
        for r in results:
            print(f"📌 {r.get('problem', 'N/A')}")
            print(f"   → {r.get('solution', 'N/A')[:100]}...")
            print()
    
    elif cmd == "list":
        learnings = load_learnings()
        print(f"📚 {len(learnings.get('learnings', []))} Learnings")
        print(f"🔧 {len(learnings.get('skills', []))} Skills erstellt")
    
    elif cmd == "register" and len(sys.argv) >= 6:
        register_skill(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], "", "manual")
    
    else:
        print("Unbekannter Befehl")
