#!/usr/bin/env python3
"""
🤖 gog SYSTEM - Complete Google Workspace Integration
Für alle EmpireHazeClaw Operationen
"""
import subprocess
import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

# ============ CONFIG ============
CALENDAR_ID = "empirehazeclaw@gmail.com"
SHEET_ID = "1FrGG9SR3yz8BKjsDaDxhuG39JBKoEdujEJWMghULfG0"
GMAIL_ACCOUNT = "empirehazeclaw@gmail.com"

# ============ GMAIL ============
def send_email(to, subject, body):
    """Sende Email"""
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", to,
        "--subject", subject,
        "--body", body,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    if "message_id" in result.stdout:
        return True, result.stdout.split()[1]
    return False, result.stderr

def read_emails(query="in:inbox", limit=10):
    """Lese Emails"""
    result = subprocess.run([
        "gog", "gmail", "messages", "list",
        query,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    return result.stdout

def get_unread_count():
    """Anzahl ungelesener Emails"""
    result = subprocess.run([
        "gog", "gmail", "messages", "list",
        "in:inbox is:unread",
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    return len([l for l in result.stdout.split('\n') if l.startswith('19d1')])

# ============ CALENDAR ============
def create_event(title, start_time, duration_min=30, description=""):
    """Erstelle Calendar Event"""
    result = subprocess.run([
        "gog", "calendar", "create", CALENDAR_ID,
        "--summary", title,
        "--from", start_time,
        "--duration", str(duration_min),
        "--description", description,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    if "id" in result.stdout:
        return True, result.stdout.split()[-1]
    return False, None

def list_events(days=7):
    """Liste Termine"""
    result = subprocess.run([
        "gog", "calendar", "events", "list", CALENDAR_ID,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    return result.stdout

# ============ SHEETS ============
def sheet_append(sheet_name, values):
    """Füge Zeile zu Sheet hinzu"""
    try:
        response = requests.post(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_name}:append?valueInputOption=USER_ENTERED",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"values": [values]}
        )
        return response.status_code == 200
    except:
        return False

def sheet_read(sheet_name):
    """Lese Sheet"""
    try:
        response = requests.get(
            f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}/values/{sheet_name}",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        return response.json()
    except:
        return {}

# ============ DRIVE ============
def drive_upload(filename, content):
    """Upload zu Drive"""
    # Via API
    return True  # Placeholder

def drive_list():
    """Liste Drive Dateien"""
    result = subprocess.run([
        "gog", "drive", "ls",
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    return result.stdout

# ============ DOCS ============
def doc_create(title):
    """Erstelle Google Doc"""
    result = subprocess.run([
        "gog", "docs", "create", title,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    if "id" in result.stdout:
        return result.stdout.split()[-1]
    return None

# ============ TASKS ============
def task_add(tasklist, title):
    """Erstelle Task"""
    result = subprocess.run([
        "gog", "tasks", "add", tasklist,
        "--title", title,
        "--access-token", TOKEN,
        "--account", GMAIL_ACCOUNT
    ], capture_output=True, text=True)
    
    return "id" in result.stdout

# ============ AUTOMATIONS ============

def daily_report():
    """Erstelle Daily Report"""
    datum = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Check Emails
    unread = get_unread_count()
    
    # 2. Check Calendar
    events = list_events(1)
    
    # 3. Create Doc
    doc_id = doc_create(f"Daily Report - {datum}")
    
    # 4. Add to Sheet
    sheet_append("Leads", ["Daily Report", datum, f"Unread: {unread}", "", ""])
    
    return {"unread": unread, "doc": doc_id}

def customer_onboarding(kunde, email, plan):
    """Komplettes Onboarding"""
    # 1. Welcome Email
    send_email(email, "Willkommen!", f"Hallo {kunde}, willkommen bei EmpireHazeClaw!")
    
    # 2. Schedule Call
    create_event(f"Onboarding - {kunde}", "tomorrow 10:00", 30, f"Onboarding für {plan} Plan")
    
    # 3. Add to Sheet
    sheet_append("Kunden", [kunde, email, plan, "neu", datetime.now().strftime("%Y-%m-%d")])
    
    return True

def lead_tracking(lead_email, lead_company, status):
    """Track Lead in Sheet"""
    sheet_append("Leads", [lead_company, lead_email, "Outreach", status, datetime.now().strftime("%Y-%m-%d")])

# ============ MAIN ============

if __name__ == "__main__":
    print("=== 🤖 gog SYSTEM - BEREIT ===")
    print("")
    print("Verfügbare Funktionen:")
    print("  - send_email(to, subject, body)")
    print("  - create_event(title, time, duration)")
    print("  - sheet_append(sheet, values)")
    print("  - doc_create(title)")
    print("  - task_add(list, title)")
    print("  - daily_report()")
    print("  - customer_onboarding(kunde, email, plan)")
    print("  - lead_tracking(email, company, status)")
