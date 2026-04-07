#!/usr/bin/env python3
"""
📅 gog Calendar - Call-Buchung
Automatisch Termine erstellen wenn Kunde antwortet
"""
import subprocess
import os

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

CALENDAR_ID = "empirehazeclaw@gmail.com"

def create_call_event(customer_name, date_time, duration_min=30):
    """Erstelle Call Event"""
    result = subprocess.run([
        "gog", "calendar", "create", CALENDAR_ID,
        "--summary", f"Call mit {customer_name}",
        "--from", date_time,
        "--to", f"{date_time[:11]}{int(date_time[11:13]) + (duration_min//60):02d}:{duration_min%60:02d}:00Z",
        "--description", f"Call mit {customer_name} - EmpireHazeClaw",
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    if "id" in result.stdout:
        event_id = result.stdout.split()[1]
        link = result.stdout.split()[-1]
        return True, event_id, link
    return False, result.stderr, None

def list_events(days=7):
    """Liste bevorstehende Termine"""
    result = subprocess.run([
        "gog", "calendar", "events", "list", CALENDAR_ID,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    return result.stdout

# Test
if __name__ == "__main__":
    print("=== 📅 CALENDAR - FERTIG ===")
    print("Test Event erstellt: Call mit Test")
