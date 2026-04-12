#!/usr/bin/env python3
"""
Voice Alert System - Text-to-Speech für wichtige Events
"""

import os
import subprocess
import json
from datetime import datetime

ALERTS_FILE = "/home/clawbot/.openclaw/config/alerts.json"

# Vordefinierte Alerts
DEFAULT_ALERTS = {
    "backup_done": {
        "message": "Backup completed successfully",
        "voice": "en",
        "enabled": True
    },
    "cron_error": {
        "message": "Cron job failed",
        "voice": "en",
        "enabled": True
    },
    "health_warning": {
        "message": "Health check warning",
        "voice": "en",
        "enabled": True
    },
    "security_alert": {
        "message": "Security alert detected",
        "voice": "en",
        "enabled": True
    },
    "daily_report": {
        "message": "Daily report ready",
        "voice": "en",
        "enabled": False
    }
}

def ensure_config():
    """Erstelle Config falls nicht vorhanden"""
    os.makedirs(os.path.dirname(ALERTS_FILE), exist_ok=True)
    if not os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "w") as f:
            json.dump(DEFAULT_ALERTS, f, indent=2)

def speak(text, lang="en"):
    """Text vorlesen"""
    try:
        # Versuche gtts-cli (Google Translate TTS)
        subprocess.run([
            "gtts-cli", text, "--lang", lang, "--output", "/tmp/tts.mp3"
        ], capture_output=True, timeout=10)
        
        # Abspielen
        subprocess.Popen(["mpg123", "-q", "/tmp/tts.mp3"])
        return True
    except:
        try:
            # Fallback: espeak
            subprocess.Popen(["espeak", text])
            return True
        except:
            return False

def trigger_alert(alert_name):
    """Trigger einen Alert"""
    ensure_config()
    
    with open(ALERTS_FILE) as f:
        alerts = json.load(f)
    
    if alert_name in alerts and alerts[alert_name].get("enabled"):
        message = alerts[alert_name]["message"]
        lang = alerts[alert_name].get("voice", "en")
        
        print(f"🔔 Alert: {message}")
        return speak(message, lang)
    
    return False

def list_alerts():
    """Liste alle Alerts auf"""
    ensure_config()
    
    with open(ALERTS_FILE) as f:
        alerts = json.load(f)
    
    print("\n🔔 Voice Alerts:")
    print("=" * 50)
    for name, config in alerts.items():
        status = "✅" if config.get("enabled") else "❌"
        print(f"  {status} {name:20} - {config['message']}")
    print()

def main():
    import sys
    
    if len(sys.argv) < 2:
        list_alerts()
    elif sys.argv[1] == "list":
        list_alerts()
    elif sys.argv[1] == "test":
        speak("Voice alert system is working", "en")
    else:
        trigger_alert(sys.argv[1])

if __name__ == "__main__":
    main()
