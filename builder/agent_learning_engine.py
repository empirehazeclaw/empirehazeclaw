#!/usr/bin/env python3
"""
Agent Learning Engine für OpenClaw University
Automatisierte Agent-Zertifizierung und Training

Usage:
    python agent_learning_engine.py status              # Zeigt alle Agent-Status
    python agent_learning_engine.py assign <agent>      # Weist nächste Lektion zu
    python agent_learning_engine.py certify <agent>     # Zertifiziert Agent (nach Quiz)
    python agent_learning_engine.py progress <agent>    # Zeigt Agent-Fortschritt
    python agent_learning_engine.py start_training <agent>  # Startet Training für Agent
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# === CONFIG ===
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo/university")
CURRICULUM_FILE = WORKSPACE / "agent_curriculum.json"
CERTIFICATIONS_FILE = WORKSPACE / "agent_certifications.json"
UNIVERSITY_DIR = WORKSPACE


def load_curriculum():
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_certifications():
    with open(CERTIFICATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_certifications(data):
    with open(CERTIFICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def cmd_status():
    """Zeigt Status aller Agents"""
    certs = load_certifications()
    curriculum = load_curriculum()
    
    print("🏫 **OpenClaw Agent University — Status**\n")
    print("=" * 50)
    
    for agent_id, agent_data in certs.get("agents", {}).items():
        name = agent_data.get("name", "?")
        cert_list = agent_data.get("certifications", [])
        in_progress = agent_data.get("in_progress", [])
        completed = agent_data.get("completed_modules", [])
        
        badges = " ".join([curriculum.get("certification_badges", {}).get(c, {}).get("emoji", "❓") for c in cert_list]) or "—"
        
        print(f"\n🤖 **{name}** (`{agent_id}`)")
        print(f"   🏅 Zertifikate: {badges}")
        print(f"   📚 In Progress: {', '.join(in_progress) if in_progress else '—'}")
        print(f"   ✅ Abgeschlossen: {len(completed)} Module")
        
        if cert_list:
            print(f"   🎓 **CERTIFIED**")
        else:
            print(f"   ⏳ Training pending")
    
    print("\n" + "=" * 50)


def cmd_assign(agent_id):
    """Weist dem Agent die nächste Lektion zu"""
    certs = load_certifications()
    curriculum = load_curriculum()
    
    if agent_id not in certs.get("agents", {}):
        print(f"❌ Agent '{agent_id}' nicht gefunden!")
        return
    
    agent = certs["agents"][agent_id]
    agent_config = curriculum.get("agents", {}).get(agent_id, {})
    
    required = agent_config.get("required_modules", [])
    
    # Finde nächste nicht-abgeschlossene Lektion
    next_module = None
    for mod in required:
        module_id = mod.get("module", "")
        lessons = mod.get("lessons", [])
        
        if isinstance(lessons, str) and lessons == "all":
            continue
        
        for lesson in lessons:
            if lesson not in agent.get("completed_modules", []):
                next_module = mod
                break
        
        if next_module:
            break
    
    if not next_module:
        print(f"✅ {agent.get('name')} hat alle erforderlichen Module abgeschlossen!")
        return
    
    # Markiere als in_progress
    if next_module.get("module") not in agent.get("in_progress", []):
        agent.setdefault("in_progress", []).append(next_module.get("module"))
        save_certifications(certs)
    
    # Zeige was der Agent lernen soll
    module_id = next_module.get("module")
    lessons = next_module.get("lessons", [])
    reason = next_module.get("reason", "")
    
    print(f"\n📚 **Training Assignment für {agent.get('name')}**\n")
    print(f"🎯 **Modul {module_id}**")
    print(f"📝 Grund: {reason}\n")
    print("Zu absolvierende Lektionen:")
    
    for lesson in lessons:
        lesson_path = UNIVERSITY_DIR / f"{lesson}.md"
        exists = "✅" if lesson_path.exists() else "❌"
        print(f"  {exists} {lesson}")
    
    quiz = next_module.get("quiz", "")
    print(f"\n📋 Abschluss mit Quiz: {quiz}")
    
    print(f"\n" + "=" * 50)
    print("Um das Training zu starten, nutze: `agent_learning_engine.py start_training {agent_id}`")


def cmd_progress(agent_id):
    """Zeigt detaillierten Fortschritt eines Agents"""
    certs = load_certifications()
    curriculum = load_curriculum()
    
    if agent_id not in certs.get("agents", {}):
        print(f"❌ Agent '{agent_id}' nicht gefunden!")
        return
    
    agent = certs["agents"][agent_id]
    agent_config = curriculum.get("agents", {}).get(agent_id, {})
    
    print(f"\n📊 **Fortschritt: {agent.get('name')}**\n")
    
    required = agent_config.get("required_modules", [])
    
    for mod in required:
        module_id = mod.get("module", "")
        lessons = mod.get("lessons", [])
        quiz = mod.get("quiz", "")
        reason = mod.get("reason", "")
        
        completed = module_id in agent.get("completed_modules", [])
        quiz_score = agent.get("quiz_scores", {}).get(module_id, None)
        
        if completed:
            status = f"✅ BESTANDEN ({quiz_score}%)" if quiz_score else "✅ ABGESCHLOSSEN"
        else:
            status = "⏳ Ausstehend"
        
        print(f"**Modul {module_id}** — {status}")
        print(f"   📝 {reason}")
        
        if not completed:
            print("   Lektionen:")
            for lesson in lessons:
                done = "✅" if lesson in agent.get("completed_modules", []) else "⬜"
                print(f"      {done} {lesson}")
        
        print()


def cmd_certify(agent_id):
    """Zertifiziert einen Agent nach bestandenen Quiz"""
    certs = load_certifications()
    curriculum = load_curriculum()
    
    if agent_id not in certs.get("agents", {}):
        print(f"❌ Agent '{agent_id}' nicht gefunden!")
        return
    
    agent = certs["agents"][agent_id]
    agent_config = curriculum.get("agents", {}).get(agent_id, {})
    
    required = agent_config.get("required_modules", [])
    
    # Prüfe ob alle Module abgeschlossen
    all_complete = True
    for mod in required:
        module_id = mod.get("module", "")
        if module_id not in agent.get("completed_modules", []):
            all_complete = False
            break
    
    if not all_complete:
        print(f"❌ {agent.get('name')} hat noch nicht alle Module abgeschlossen!")
        print("   Nutze `progress` um den Fortschritt zu sehen.")
        return
    
    # Zertifiziere
    cert_name = agent_config.get("certification", "Unknown")
    badges = curriculum.get("certification_badges", {})
    badge_info = badges.get(cert_name, {})
    
    if cert_name not in agent.get("certifications", []):
        agent.setdefault("certifications", []).append(cert_name)
        agent["last_training"] = datetime.utcnow().isoformat()
        save_certifications(certs)
    
    print(f"\n🎉 **{agent.get('name')} wurde zertifiziert!**\n")
    print(f"🏅 Zertifikat: **{cert_name}**")
    print(f"{badge_info.get('emoji', '🎓')} {badge_info.get('description', '')}")
    print(f"\nBerechtigungen: {', '.join(agent_config.get('permissions_on_certification', []))}")
    print(f"\n🎓 Zertifiziert durch: {badge_info.get('granted_by', 'OpenClaw University')}")


def cmd_start_training(agent_id):
    """Startet das Training für einen Agent"""
    certs = load_certifications()
    curriculum = load_curriculum()
    
    if agent_id not in certs.get("agents", {}):
        print(f"❌ Agent '{agent_id}' nicht gefunden!")
        return
    
    agent = certs["agents"][agent_id]
    agent_config = curriculum.get("agents", {}).get(agent_id, {})
    
    print(f"\n🚀 **Training gestartet für {agent.get('name')}**\n")
    
    # Zeige alle Module die der Agent lernen muss
    required = agent_config.get("required_modules", [])
    
    for i, mod in enumerate(required, 1):
        module_id = mod.get("module", "")
        lessons = mod.get("lessons", [])
        reason = mod.get("reason", "")
        
        completed = module_id in agent.get("completed_modules", [])
        status = "✅" if completed else "⏳"
        
        print(f"{i}. Modul {module_id} — {status}")
        print(f"   📝 {reason}")
        
        if not completed and isinstance(lessons, list):
            print("   Lektionen:")
            for lesson in lessons:
                done = "✅" if lesson in agent.get("completed_modules", []) else "📖"
                print(f"      {done} {lesson}.md")
    
    print(f"\n" + "=" * 50)
    print("Um eine spezifische Lektion zuzuweisen, nutze:")
    print(f"  `agent_learning_engine.py assign {agent_id}`")


def cmd_list_agents():
    """Listet alle verfügbaren Agents auf"""
    certs = load_certifications()
    
    print("\n👥 **Verfügbare Agents:**\n")
    for agent_id, data in certs.get("agents", {}).items():
        certs_list = data.get("certifications", [])
        in_progress = data.get("in_progress", [])
        
        cert_badges = " ".join([f"🏅{c}" for c in certs_list]) or "—"
        
        print(f"🤖 `{agent_id}` — {data.get('name', '?')}")
        print(f"   {cert_badges}")
        if in_progress:
            print(f"   📚 In Progress: {', '.join(in_progress)}")
        print()


# === MAIN ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n📌 Schnellstart:")
        print("  python agent_learning_engine.py list           # Alle Agents anzeigen")
        print("  python agent_learning_engine.py status          # Status aller Agents")
        print("  python agent_learning_engine.py progress <id>   # Fortschritt eines Agent")
        print("  python agent_learning_engine.py assign <id>     # Nächste Lektion zuweisen")
        print("  python agent_learning_engine.py certify <id>    # Agent zertifizieren")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        cmd_status()
    elif command == "list":
        cmd_list_agents()
    elif command == "assign" and len(sys.argv) >= 3:
        cmd_assign(sys.argv[2])
    elif command == "progress" and len(sys.argv) >= 3:
        cmd_progress(sys.argv[2])
    elif command == "certify" and len(sys.argv) >= 3:
        cmd_certify(sys.argv[2])
    elif command == "start_training" and len(sys.argv) >= 3:
        cmd_start_training(sys.argv[2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
