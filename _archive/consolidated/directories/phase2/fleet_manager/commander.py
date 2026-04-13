#!/usr/bin/env python3
"""
🐕 FLEET COMMANDER
==================
Der Master-Server für Managed AI Hosting.
Sammelt Heartbeats von Kunden-Servern und triggert bei Ausfällen Restarts.
"""

from flask import Flask, request, jsonify
import json
import os
import time
from datetime import datetime
import subprocess

app = Flask(__name__)
STATE_FILE = "/home/clawbot/.openclaw/workspace/data/fleet_state.json"
OFFLINE_THRESHOLD_SECONDS = 180 # 3 Minuten ohne Ping = Offline

def init_db():
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w') as f:
            json.dump({"servers": {}}, f)

def load_state():
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def send_alert(message):
    print(f"🚨 ALERT: {message}")
    # Integration in unser Telegram-System
    try:
        subprocess.run([
            "openclaw", "message", "send", 
            "--channel", "telegram", 
            "--target", "5392634979", 
            "--message", message
        ], capture_output=True)
    except:
        pass

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.json
    if not data or 'customer_id' not in data:
        return jsonify({"error": "Missing customer_id"}), 400
        
    cid = data['customer_id']
    state = load_state()
    
    # Update Server Status
    state['servers'][cid] = {
        "last_ping": datetime.now().isoformat(),
        "status": data.get('status', 'unknown'),
        "cpu": data.get('cpu_usage', 0),
        "ram": data.get('ram_usage', 0),
        "errors": data.get('errors_last_5m', 0),
        "agent_alive": data.get('agent_process_alive', False)
    }
    
    save_state(state)
    return jsonify({"status": "received"})

@app.route('/status', methods=['GET'])
def status():
    state = load_state()
    now = datetime.now()
    
    report = {"online": [], "offline": [], "warnings": []}
    
    for cid, s in state['servers'].items():
        last_ping = datetime.fromisoformat(s['last_ping'])
        diff = (now - last_ping).total_seconds()
        
        if diff > OFFLINE_THRESHOLD_SECONDS:
            report['offline'].append({"id": cid, "last_seen": f"{int(diff/60)} mins ago"})
            send_alert(f"⚠️ KUNDE {cid} OFFLINE! Kein Ping seit {int(diff/60)} Minuten.")
            # Hier würde der automatische SSH-Restart Code stehen (z.B. via Ansible)
        elif not s['agent_alive']:
            report['warnings'].append({"id": cid, "issue": "Agent process dead"})
            send_alert(f"⚠️ KUNDE {cid}: Server online, aber OpenClaw Agent abgestürzt!")
        else:
            report['online'].append(cid)
            
    return jsonify(report)

if __name__ == '__main__':
    init_db()
    # Der Commander läuft auf Port 5010
    app.run(host='0.0.0.0', port=5010)
