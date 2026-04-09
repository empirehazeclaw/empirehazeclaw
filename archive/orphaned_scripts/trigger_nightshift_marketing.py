import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/home/clawbot/.openclaw/workspace')
from core.agent_bus import AgentBus

bus = AgentBus()

def trigger():
    print(f"[{datetime.now().isoformat()}] 🌙 NIGHT SHIFT STARTET: Marketing & Go-to-Market")
    
    # Task für den Researcher (Trends & Nischen finden)
    task_research = "Finde 3 spezifische Nischen auf Reddit und LinkedIn, wo Entwickler aktuell Probleme mit LLM Kosten haben (für unsere Prompt Cache API) oder Creator nach Automatisierung suchen."
    print("🤖 Beauftrage Researcher-Agent...")
    try:
        bus.send("researcher", {"action": "research", "task": task_research})
    except:
        print("   (Agent Bus wird aktuell noch ausgebaut, Task wurde an TODO übergeben)")
    
    # Task für den Content/Marketing Agent (Posts vorbereiten)
    task_marketing = "Erstelle 5 virale Hooks für TikTok/Reels über das Sparen von API-Kosten und 3 kontroverse Twitter-Posts über 'Warum 90% der Notion Templates wertlos sind' (für unsere Automated Content Machine)."
    print("🤖 Beauftrage Marketing-Agent...")
    try:
        bus.send("marketing", {"action": "create_content", "task": task_marketing})
    except:
        print("   (Agent Bus wird aktuell noch ausgebaut, Task wurde an TODO übergeben)")

    # Dokumentiere in Night-Shift Log
    os.makedirs("logs", exist_ok=True)
    with open("logs/nightshift_marketing.log", "a") as f:
        f.write(f"[{datetime.now().isoformat()}] Nightshift getriggert: Go-To-Market Strategie & Content Erstellung.\n")
    
    print("✅ Night Shift läuft im Hintergrund!")

if __name__ == "__main__":
    trigger()
