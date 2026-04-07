#!/usr/bin/env python3
"""
🎯 Managed Hosting + gog Integration
Automatisierung für Kunden-Onboarding
"""
import subprocess
import os
import requests
import json
from datetime import datetime

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

# ============ KUNDEN MANAGEMENT ============

def send_welcome_email(kunde_email, kunde_name, server_ip):
    """Sende Welcome Email an neuen Kunden"""
    subject = "Willkommen bei EmpireHazeClaw Managed AI Hosting"
    body = f"""Hallo {kunde_name},

willkommen! Dein Server ist jetzt bereit.

Server IP: {server_ip}
Zugang: Wir melden uns innerhalb von 24h für das Onboarding.

Was wir dir bieten:
- 🇩🇪Deutscher Server (Hetzner)
- 🔒 DSGVO-konform
- 🤖 OpenClaw AI vorinstalliert

Bei Fragen: empirehazeclaw@gmail.com

Viele Grüße
Nico
EmpireHazeClaw"""
    
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", kunde_email,
        "--subject", subject,
        "--body", body,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    return "message_id" in result.stdout

def schedule_onboarding_call(kunde_name, datum="2026-03-26T10:00:00Z"):
    """Erstelle Calendar Event für Onboarding"""
    result = subprocess.run([
        "gog", "calendar", "create", "empirehazeclaw@gmail.com",
        "--summary", f"Onboarding Call - {kunde_name}",
        "--from", datum,
        "--description", f"Onboarding Call mit {kunde_name} - Managed AI Hosting",
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    if "id" in result.stdout:
        event_id = result.stdout.split()[1]
        link = result.stdout.split()[-1]
        return True, event_id, link
    return False, None, None

def add_to_tracking_sheet(kunde, email, plan, status="neu"):
    """Füge Kunde zur Google Sheet hinzu"""
    SHEET_ID = "1FrGG9SR3yz8BKjsDaDxhuG39JBKoEdujEJWMghULfG0"
    from datetime import datetime
    datum = datetime.now().strftime("%Y-%m-%d")
    
    response = requests.post(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/Kunden:append?valueInputOption=USER_ENTERD",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={"values": [[kunde, email, plan, status, datum]]}
    )
    return response.status_code == 200

def create_support_ticket(kunde, issue):
    """Erstelle Google Doc für Support Ticket"""
    title = f"Support Ticket - {kunde} - {datetime.now().strftime('%Y-%m-%d')}"
    result = subprocess.run([
        "gog", "docs", "create", title,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    if "id" in result.stdout:
        doc_id = result.stdout.split()[1]
        link = result.stdout.split()[-1]
        return True, link
    return False, None

# ============ AUTOMATION ============

def onboard_kunde(kunde_name, kunde_email, plan, server_ip):
    """Komplettes Onboarding für neuen Kunden"""
    print(f"🎯 Onboarding: {kunde_name}")
    
    results = {
        "email": send_welcome_email(kunde_email, kunde_name, server_ip),
        "calendar": schedule_onboarding_call(kunde_name)[0],
        "sheet": add_to_tracking_sheet(kunde_name, kunde_email, plan),
    }
    
    return results

if __name__ == "__main__":
    print("=== 🎯 Managed Hosting + gog ===")
    print("Bereit für Kunden-Onboarding!")
