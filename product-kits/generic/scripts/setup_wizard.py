#!/usr/bin/env python3
"""
🚀 EmpireHazeClaw AI Employee Setup Wizard
Führt Kunden durch die Ersteinrichtung
"""
import json
import os
import sys

CONFIG_DIR = "config"
DATA_DIR = "data"

def print_header():
    print("""
╔═══════════════════════════════════════════════════════════╗
║     🦞 EmpireHazeClaw AI Employee - Setup Wizard         ║
╚═══════════════════════════════════════════════════════════╝
""")

def print_step(num, total, text):
    print(f"\n[{num}/{total}] {text}")
    print("-" * 50)

def get_input(prompt, required=True, default=None):
    if default:
        val = input(f"{prompt} [{default}]: ").strip() or default
    else:
        val = input(f"{prompt}: ").strip()
    
    if required and not val:
        print("❌ Dieses Feld ist erforderlich!")
        return get_input(prompt, required, default)
    
    return val

def setup_business_info():
    """Grundlegende Geschäftsdaten"""
    print_step(1, 5, "Geschäftsdaten")
    
    return {
        "name": get_input("Firmenname", default="Mein Unternehmen"),
        "website": get_input("Website URL", default="https://beispiel.de"),
        "email": get_input("Kontakt-Email", required=True),
        "phone": get_input("Telefonnummer", default="+49 XXX XXXXXXX"),
        "address": get_input("Adresse", default="")
    }

def setup_agents():
    """Welche Agents aktivieren"""
    print_step(2, 5, "Agents auswählen")
    
    print("Welche Agents möchten Sie aktivieren?")
    print("1 = Email Agent (auto-beantwortet Emails)")
    print("2 = Support Agent (FAQs und Tickets)")
    print("3 = Scheduler Agent (Terminbuchung)")
    print("4 = Analytics Agent (Reports)")
    print("(Mehrere möglich, z.B. 1,2,3)")
    
    choice = get_input("Auswahl", default="1,2,3,4")
    
    agents = {
        "email": "1" in choice,
        "support": "2" in choice,
        "scheduler": "3" in choice,
        "analytics": "4" in choice
    }
    
    return agents

def setup_schedule():
    """Schedule Einstellungen"""
    print_step(3, 5, "Zeitplan")
    
    print("Wie oft soll der AI Agent arbeiten?")
    print("1 = Alle 15 Minuten (schnellste Reaktion)")
    print("2 = Alle 30 Minuten (empfohlen)")
    print("3 = Stündlich (langsam)")
    
    choice = get_input("Auswahl", default="2")
    
    schedules = {
        "1": "*/15 * * * *",
        "2": "*/30 * * * *",
        "3": "0 * * * *"
    }
    
    return schedules.get(choice, "*/30 * * * *")

def setup_gmail():
    """Gmail Integration"""
    print_step(4, 5, "Gmail Einrichtung")
    
    print("Für den Email Agent benötigen Sie ein Gmail App Password.")
    print("So geht's:")
    print("1. Gehen Sie zu: https://myaccount.google.com/security")
    print("2. Aktivieren Sie '2-Schritt-Verifizierung'")
    print("3. Gehen Sie zu: https://myaccount.google.com/apppasswords")
    print("4. Erstellen Sie ein App Password für 'Mail'")
    print()
    
    app_password = get_input("App Password eingeben", required=False)
    
    return {
        "email": get_input("Gmail Adresse", required=True),
        "app_password": app_password
    }

def setup_finish():
    """Setup abschließen"""
    print_step(5, 5, "Zusammenfassung")

def main():
    print_header()
    
    # Create directories
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Run setup
    business = setup_business_info()
    agents = setup_agents()
    schedule = setup_schedule()
    gmail = setup_gmail() if agents["email"] else {}
    
    # Create config
    config = {
        "business": business,
        "agents": agents,
        "schedule": schedule,
        "gmail": gmail
    }
    
    # Save
    with open("config/setup.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ SETUP ABGESCHLOSSEN!")
    print("=" * 50)
    print()
    print("Als nächstes:")
    print("1. Crontab bearbeiten: crontab -e")
    print(f"   Agent starten alle {schedule}")
    print()
    print("2. Email Agent testen:")
    print("   python3 agents/email_agent.py")
    print()
    print("3. Support FAQ bearbeiten:")
    print("   nano data/faq.json")
    print()
    print("Viel Erfolg mit Ihrem AI Employee! 🤖")

if __name__ == "__main__":
    main()
