#!/usr/bin/env python3
"""
🐕 WATCHDOG CLIENT
==================
Läuft auf dem Kunden-Server und funkt alle 60s nach Hause.
"""

import sys
import os
import json
import requests
import psutil
from datetime import datetime
import time

COMMANDER_URL = "http://188.124.11.27:5010/heartbeat"
CUSTOMER_ID = "cx_demo_123"

def check_agent_alive():
    # Prüft, ob der `openclaw` Prozess auf dem Host läuft
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] == 'openclaw' or 'openclaw' in ''.join(proc.info['cmdline'] or []):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def ping():
    try:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        alive = check_agent_alive()
        
        payload = {
            "customer_id": CUSTOMER_ID,
            "status": "online" if alive else "agent_dead",
            "agent_process_alive": alive,
            "cpu_usage": cpu,
            "ram_usage": ram,
            "errors_last_5m": 0 # TODO: Parse logs
        }
        
        res = requests.post(COMMANDER_URL, json=payload, timeout=5)
        print(f"[{datetime.now().isoformat()}] Ping gesendet. Antwort: {res.status_code}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ Fehler beim Pingen des Commanders: {e}")

if __name__ == '__main__':
    # Dieser Loop wird per Systemd-Service auf dem Kunden-Server am Leben gehalten.
    while True:
        ping()
        time.sleep(60)
