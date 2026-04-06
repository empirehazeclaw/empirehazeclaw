#!/usr/bin/env python3
"""
Exercise Reminder Tracker - KNIE-FREUNDLICH (fortgeschritten)
Nach Unfall: Moderate Intensität, kein Aufprall, keine Explosionen
"""

import os
import json
from datetime import datetime, date

TRACKER_FILE = "/home/clawbot/.openclaw/data/exercise_tracker.json"

def get_day_index():
    return date.today().timetuple().tm_yday % 3

# Moderate intensity - still knee-friendly but more challenging
WORKOUTS = [
    # Tag 1: Kraft (mit moderater Belastung)
    {
        "name": "Kraft & Stabilität",
        "level": "mittel",
        "exercises": [
            {
                "name": "Kniebeugen ( assisted)",
                "sets": "3x12",
                "desc": "Füße schulterbreit, runter bis 90°, nicht tiefer. An Stuhl/Wand festhalten für Balance. 🪑 Kontrolliert hoch/runter."
            },
            {
                "name": "Sumo-Kniebeugen",
                "sets": "3x12",
                "desc": "Füße breit, Zehen außen. Tiefer als normale Kniebeuge, aber schonend für Knie. 🦵 Mehr Innenschenkel."
            },
            {
                "name": "Goblet Squat (mit Gewicht)",
                "sets": "3x10",
                "desc": "Kniebeuge mit schwerer Kurzhantel/Heavy Bag vor der Brust. Gewicht gibt Widerstand. 🏋️"
            }
        ]
    },
    # Tag 2: Hüfte & Rumpf
    {
        "name": "Hüfte & Rumpf",
        "level": "mittel",
        "exercises": [
            {
                "name": "Ausfallschritte (Walking)",
                "sets": "3x16 Schritte",
                "desc": "Nach vorne laufen, tiefer Ausfallschritt, aufstehen, anderes Bein. 🚶 Kein Springen!"
            },
            {
                "name": "Curtsy Lunges",
                "sets": "3x10/Seite",
                "desc": "Seitlich zurückbeugen wie beim Knicks. Bein kreuzt hinten vor dem anderen. 💃 Stabilisiert von außen."
            },
            {
                "name": "Plank (Unterarm)",
                "sets": "3x30sek",
                "desc": "Bauchlage, Unterarme auf, Körper gerade. Rumpf stabilisiert das Knie! 💪"
            }
        ]
    },
    # Tag 3: Balance & Kraftausdauer
    {
        "name": "Balance & Kraft",
        "level": "mittel",
        "exercises": [
            {
                "name": "Einbein-Kniebeuge (assisted)",
                "sets": "3x8/Bein",
                "desc": "Ein Bein anheben, anderes Bein beugen. An Wand festhalten! 🧗 Kontrolliert runter."
            },
            {
                "name": "Step-Ups (Box 20cm)",
                "sets": "3x12/Bein",
                "desc": "Auf Box (nicht springen!). Ein Bein, dann anderes. Kontrolliert. 📦 Kein Aufprall."
            },
            {
                "name": "Wall Sit",
                "sets": "3x30sek",
                "desc": "Mit dem Rücken an Wand, runterrutschen bis Knie 90°. Halten! 🔥 Quadrizeps im Endspiel."
            }
        ]
    }
]

def get_workout_text():
    day_idx = get_day_index()
    workout = WORKOUTS[day_idx]
    
    text = f"🦵 Knie-freundliches Training ({workout['name']})\n"
    text += f"📋 Level: {workout['level']} | Kein Aufprall, kein Springen\n\n"
    
    for i, ex in enumerate(workout['exercises'], 1):
        text += f"{i}. **{ex['name']}** - {ex['sets']}\n"
        text += f"   {ex['desc']}\n\n"
    
    # Tipps
    text += "💡 REGELN:\n"
    text += "• Keine harten Landungen!\n"
    text += "• Nicht explosiv springen\n"
    text += "• Bei Schmerzen: STOPP\n"
    text += "• Kühlen nach Training wenn nötig\n\n"
    
    next_idx = (day_idx + 1) % 3
    text += f"🔄 Morgen: {WORKOUTS[next_idx]['name']}"
    
    return text

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE) as f:
            return json.load(f)
    return {"last_confirmed": None, "reminders_sent": 0}

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_and_remind():
    data = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    
    if data.get("last_confirmed") == today:
        return None
    
    sent_today = data.get("reminders_sent_today", 0)
    
    if sent_today >= 5:
        return None
    
    data["reminders_sent_today"] = sent_today + 1
    save_tracker(data)
    
    return get_workout_text()

def confirm():
    data = load_tracker()
    today = datetime.now().strftime("%Y-%m-%d")
    data["last_confirmed"] = today
    data["reminders_sent_today"] = 0
    save_tracker(data)
    return "✅ Training bestätigt! Weiter so! 💪"

def status():
    day_idx = get_day_index()
    workout = WORKOUTS[day_idx]
    return f"Heute: {workout['name']}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "confirm":
            print(confirm())
        elif sys.argv[1] == "status":
            print(status())
        elif sys.argv[1] == "reset":
            data = {"last_confirmed": None, "reminders_sent_today": 0}
            save_tracker(data)
            print("Reset!")
        else:
            print("Usage: exercise_tracker.py [confirm|status|reset]")
    else:
        result = check_and_remind()
        if result:
            print(result)
        else:
            print("NO_REMINDER_NEEDED")
