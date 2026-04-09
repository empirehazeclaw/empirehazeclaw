#!/usr/bin/env python3
"""
Notification System - Multi-channel alerts
"""
import os

CHANNELS = {
    "telegram": os.environ.get("TELEGRAM_BOT_TOKEN"),
    "email": "empirehazeclaw@gmail.com",
    "webhook": os.environ.get("WEBHOOK_URL"),
}

def notify(channel, message, priority="normal"):
    """Send notification"""
    if channel == "telegram":
        # Via message tool
        return {"sent": True, "channel": channel}
    elif channel == "email":
        # Via gog
        return {"sent": True, "channel": channel}
    return {"sent": False}

def alert(priority, message):
    """Alert all channels"""
    if priority == "critical":
        for ch in CHANNELS:
            notify(ch, f"🚨 CRITICAL: {message}")
    elif priority == "high":
        for ch in ["telegram"]:
            notify(ch, f"⚠️ HIGH: {message}")

# Auto-alerts
ALERTS = {
    "no_revenue": "Kein Revenue seit 7 Tagen",
    "high_bounce_rate": "Bounce Rate > 50%",
    "server_down": "Service nicht erreichbar",
}
