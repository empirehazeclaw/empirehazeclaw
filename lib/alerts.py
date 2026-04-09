"""
🚨 ALERTS SYSTEM
================
"""

import requests
import os

def send_alert(title, message):
    """Send alert to Telegram"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "5392634979")
    
    if not token:
        print("⚠️ No Telegram token configured")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": f"🚨 {title}\n\n{message}"}
    
    try:
        r = requests.post(url, json=data)
        return r.status_code == 200
    except:
        return False

if __name__ == "__main__":
    send_alert("Test", "Alert system works!")
