#!/usr/bin/env python3
"""
Adventure Engine für OpenClaw University
Interaktive Scenario-basierte Learning Adventures

Usage:
    python adventure_engine.py list                    # Zeigt alle Adventures
    python adventure_engine.py start <id>              # Startet ein Adventure
    python adventure_engine.py choice <nummer>          # Macht einen Choice
    python adventure_engine.py status                   # Zeigt aktuellen Stand
    python adventure_engine.py reset                    # Setzt Adventure zurück
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# === CONFIG ===
WORKSPACE = Path("/home/clawbot/.openclaw/workspace/ceo/university")
SCENARIOS_FILE = WORKSPACE / "adventure_scenarios.json"
STATE_FILE = WORKSPACE / "adventure_state.json"
USER_ID = "5392634979"  # Nico's Telegram ID


def load_scenarios():
    """Lädt alle Adventures"""
    with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    """Lädt den aktuellen Adventure-State"""
    if not STATE_FILE.exists():
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    """Speichert den Adventure-State"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def format_scene(scenario, step):
    """Formatiert eine Scene für Telegram"""
    scene = step.get("scene", "")
    choices = step.get("choices", [])
    
    msg = f"\n{scene}\n\n"
    
    if choices:
        msg += "**Wähle eine Option:**\n"
        for i, choice in enumerate(choices, 1):
            msg += f"\n{i}. {choice['text']}"
    
    return msg


def format_end(scenario, success, points_earned, total_points):
    """Formatiert das Ende eines Adventures"""
    ending_key = "success_ending" if success else "fail_ending"
    ending = scenario.get(ending_key, "Adventure beendet.")
    
    rating = "⭐⭐⭐ Excellent!" if points_earned >= total_points * 0.8 else "⭐⭐ Good!" if points_earned >= total_points * 0.5 else "⭐ Keep practicing!"
    
    msg = f"\n{'='*40}\n"
    msg += f"🏁 Adventure beendet!\n"
    msg += f"{'='*40}\n\n"
    msg += f"📊 **Ergebnis:** {points_earned}/{total_points} Punkte\n"
    msg += f"🏅 **Bewertung:** {rating}\n\n"
    msg += f"{ending}\n"
    msg += f"\n{'='*40}\n"
    msg += "🔄 Um ein neues Adventure zu starten: `adventure start <id>`"
    
    return msg


def cmd_list():
    """Listet alle verfügbaren Adventures auf"""
    data = load_scenarios()
    scenarios = data.get("scenarios", {})
    
    if not scenarios:
        print("📭 Keine Adventures verfügbar!")
        return
    
    print("🎮 **OpenClaw University — Adventures**\n")
    print("Verfügbare Szenarien:\n")
    
    for key, scenario in scenarios.items():
        title = scenario.get("title", "Unnamed")
        desc = scenario.get("description", "")
        diff = scenario.get("difficulty", "⭐")
        time = scenario.get("estimated_time", "? min")
        steps = len(scenario.get("steps", []))
        
        print(f"🎮 **{title}**")
        print(f"   ID: `{key}`")
        print(f"   📝 {desc}")
        print(f"   ⏱️  {time} | {diff} | {steps} Steps")
        print()
    
    print("Starten mit: `adventure start <id>`")


def cmd_start(scenario_id):
    """Startet ein neues Adventure"""
    data = load_scenarios()
    scenarios = data.get("scenarios", {})
    
    if scenario_id not in scenarios:
        print(f"❌ Adventure '{scenario_id}' nicht gefunden!")
        print("Verfügbare Adventures:")
        for key in scenarios:
            print(f"  - {key}")
        return
    
    scenario = scenarios[scenario_id]
    first_step = scenario.get("steps", [{}])[0]
    
    state = {
        "scenario_id": scenario_id,
        "current_step": first_step.get("id", "step_1"),
        "points_earned": 0,
        "started_at": datetime.utcnow().isoformat(),
        "last_activity": datetime.utcnow().isoformat(),
        "completed": False,
        "choices_made": []
    }
    
    save_state(state)
    
    print(f"\n🎮 **Adventure gestartet!**")
    print(f"📌 **{scenario.get('title', 'Unnamed')}**\n")
    print(format_scene(scenario, first_step))
    print("\n" + "─"*40)
    print("Antworte mit `adventure choice <nummer>` um zu wählen.")
    print("z.B.: `adventure choice 1`")


def cmd_choice(choice_num):
    """Macht einen Choice in einem Adventure"""
    state = load_state()
    
    if not state:
        print("❌ Kein Adventure aktiv! Starte mit `adventure start <id>`")
        return
    
    if state.get("completed"):
        print("❌ Adventure bereits abgeschlossen! Starte ein neues mit `adventure start <id>`")
        return
    
    data = load_scenarios()
    scenarios = data.get("scenarios", {})
    scenario = scenarios.get(state["scenario_id"], {})
    
    # Finde aktuelle Step
    current_step_id = state["current_step"]
    steps = scenario.get("steps", [])
    current_step = None
    step_index = 0
    
    for i, step in enumerate(steps):
        if step.get("id") == current_step_id:
            current_step = step
            step_index = i
            break
    
    if not current_step:
        print("❌ Step nicht gefunden!")
        return
    
    # Parse choice number
    try:
        choice_num = int(choice_num)
    except ValueError:
        print("❌ Ungültige Choice-Nummer! Bitte eine Zahl eingeben.")
        return
    
    choices = current_step.get("choices", [])
    if choice_num < 1 or choice_num > len(choices):
        print(f"❌ Ungültige Choice-Nummer! Bitte zwischen 1 und {len(choices)} wählen.")
        return
    
    selected_choice = choices[choice_num - 1]
    
    # Record choice
    state["choices_made"].append({
        "step": current_step_id,
        "choice_id": selected_choice.get("id"),
        "choice_num": choice_num,
        "result": selected_choice.get("result", "unknown")
    })
    
    # Add points
    points = selected_choice.get("points", 0)
    state["points_earned"] += points
    
    # Show feedback
    result = selected_choice.get("result", "unknown")
    feedback = selected_choice.get("feedback", "")
    
    emoji = "✅" if result == "success" else "⚠️" if result == "partial" else "❌"
    print(f"\n{emoji} **{feedback}**\n")
    
    if result == "fail":
        print("⚠️ Das war nicht optimal, aber lass dich nicht entmutigen!")
        print()
    
    # Calculate total possible points
    total_points = sum(sum(c.get("points", 0) for c in step.get("choices", [])) for step in steps)
    
    # Determine next step
    if result == "fail":
        # Fail endings go to the fail ending
        print(format_end(scenario, False, state["points_earned"], total_points))
        state["completed"] = True
    elif step_index < len(steps) - 1:
        # More steps available
        next_step = steps[step_index + 1]
        state["current_step"] = next_step.get("id")
        state["last_activity"] = datetime.utcnow().isoformat()
        
        print("─" * 40)
        print(f"\n📍 **Next Scene:**\n")
        print(format_scene(scenario, next_step))
        print("\n" + "─" * 40)
        print("Antworte mit `adventure choice <nummer>` um zu wählen.")
    else:
        # Final step completed - check if success or fail based on last result
        is_success = result in ["success", "partial"]
        print(format_end(scenario, is_success, state["points_earned"], total_points))
        state["completed"] = True
    
    save_state(state)


def cmd_status():
    """Zeigt den aktuellen Adventure-Stand"""
    state = load_state()
    
    if not state:
        print("📭 Kein Adventure aktiv.")
        print("Starte mit `adventure list` um verfügbare Adventures zu sehen.")
        return
    
    if state.get("completed"):
        print("🏁 **Adventure abgeschlossen!**")
        print(f"   Scenario: {state.get('scenario_id')}")
        print(f"   Punkte: {state.get('points_earned')}")
        print(f"   Choices: {len(state.get('choices_made', []))}")
        print("\nStarte ein neues Adventure mit `adventure start <id>`")
        return
    
    data = load_scenarios()
    scenarios = data.get("scenarios", {})
    scenario = scenarios.get(state["scenario_id"], {})
    
    current_step_id = state["current_step"]
    steps = scenario.get("steps", [])
    
    current_index = 0
    for i, step in enumerate(steps):
        if step.get("id") == current_step_id:
            current_index = i
            break
    
    print("🎮 **Adventure Status**\n")
    print(f"📌 **{scenario.get('title', 'Unnamed')}**")
    print(f"📍 Step {current_index + 1} von {len(steps)}")
    print(f"⭐ Punkte: {state.get('points_earned', 0)}")
    print(f"⏱️  Gestartet: {state.get('started_at', '?')}")
    print(f"🕐 Letzte Aktivität: {state.get('last_activity', '?')}")
    print("\n" + "─" * 40)
    print(f"\n{scenario.get('description', '')}\n")
    print("Antworte mit `adventure choice <nummer>` um fortzufahren.")


def cmd_reset():
    """Setzt das Adventure zurück"""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
        print("✅ Adventure-State zurückgesetzt!")
    else:
        print("📭 Kein Adventure-State vorhanden.")


# === MAIN ===

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        cmd_list()
    elif command == "start" and len(sys.argv) >= 3:
        cmd_start(sys.argv[2])
    elif command == "choice" and len(sys.argv) >= 3:
        cmd_choice(sys.argv[2])
    elif command == "status":
        cmd_status()
    elif command == "reset":
        cmd_reset()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
