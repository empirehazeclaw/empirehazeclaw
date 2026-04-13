#!/usr/bin/env python3
"""
Discord Reporter - Erweitert mit Alerting
Mehrere Channels für verschiedene Alert-Typen
"""

import sys
import os

# Discord Channel IDs
CHANNELS = {
    "status": "1478772224029626450",    # #status
    "pod": "1478833313224593478",       # POD Updates
    "social": "1478833343326978059",   # Social Media
    "trading": "1478833357228363776",  # Trading
    "errors": "1478832433037181145",    # Errors/Warnings
    "coder": "1478506849941590149",    # Code/Dev
    "alerts": "1479011848887205969"    # BI Council
}

def send_alert(message, channel="status", level="info"):
    """Send alert to specific channel"""
    
    emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "critical": "🔴"
    }.get(level, "ℹ️")
    
    formatted = f"{emoji} {message}"
    
    # Use discord reporter script
    os.system(f'python3 ~/.openclaw/workspace/scripts/discord_reporter.py "{formatted}" {CHANNELS.get(channel, channel)} 2>/dev/null')
    
    print(f"✅ Alert gesendet: {channel} - {level}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 discord_alerts.py <message> [channel] [level]")
        print(f"Channels: {list(CHANNELS.keys())}")
        sys.exit(1)
    
    message = sys.argv[1]
    channel = sys.argv[2] if len(sys.argv) > 2 else "status"
    level = sys.argv[3] if len(sys.argv) > 3 else "info"
    
    send_alert(message, channel, level)
