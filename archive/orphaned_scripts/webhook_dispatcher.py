#!/usr/bin/env python3
"""
Webhook Dispatcher - Event-based triggers
"""
import requests

WEBHOOKS = {
    "sale": "https://api.example.com/sale",
    "signup": "https://api.example.com/signup",
    "error": "https://api.example.com/error",
}

def dispatch(event_type, payload):
    """Send webhook"""
    if event_type in WEBHOOKS:
        try:
            r = requests.post(WEBHOOKS[event_type], json=payload, timeout=5)
            return {"sent": True, "status": r.status_code}
        except:
            return {"sent": False}
    return {"sent": False}
