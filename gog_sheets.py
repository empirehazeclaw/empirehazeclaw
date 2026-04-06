#!/usr/bin/env python3
"""
📊 gog Sheets - Lead Tracking
Google Sheet für CRM und Lead Tracking
"""
import subprocess
import os
import requests
import json

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")
SPREADSHEET_ID = "1FrGG9SR3yz8BKjsDaDxhuG39JBKoEdujEJWMghULfG0"

def add_lead(firma, email, branche, status="neu", notes=""):
    """Füge Lead zur Sheet hinzu"""
    from datetime import datetime
    datum = datetime.now().strftime("%Y-%m-%d")
    
    response = requests.post(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Leads:append?valueInputOption=USER_ENTERED",
        headers={"Authorization": f"Bearer {TOKEN}"},
        json={"values": [[firma, email, branche, status, datum, notes]]}
    )
    
    return response.status_code == 200

def get_leads():
    """Hole alle Leads"""
    response = requests.get(
        f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Leads",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

# Test
if __name__ == "__main__":
    print("=== 📊 SHEETS - FERTIG ===")
    print(f"Spreadsheet: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit")
