#!/usr/bin/env python3
"""
Quick Commands - Shortcuts für häufige Aktionen
"""

import os
import subprocess

COMMANDS = {
    "status": {
        "desc": "System Status anzeigen",
        "action": lambda: subprocess.run(["curl", "-s", "http://127.0.0.1:18789/health"])
    },
    "backup": {
        "desc": "Backup starten",
        "action": lambda: subprocess.Popen(["/home/clawbot/.openclaw/scripts/unified_backup.sh"])
    },
    "restart": {
        "desc": "Gateway neustarten",
        "action": lambda: subprocess.run(["openclaw", "gateway", "restart"])
    },
    "logs": {
        "desc": "Letzte Logs anzeigen",
        "action": lambda: subprocess.run(["tail", "-20", "/home/clawbot/.openclaw/logs/gateway.log"])
    },
    "cron": {
        "desc": "Cron Jobs anzeigen",
        "action": lambda: subprocess.run(["openclaw", "cron", "list"])
    },
    "memory": {
        "desc": "Memory Info",
        "action": lambda: subprocess.run(["free", "-h"])
    },
    "disk": {
        "desc": "Disk Info",
        "action": lambda: subprocess.run(["df", "-h", "/"])
    },
    "ollama": {
        "desc": "Ollama Status",
        "action": lambda: subprocess.run(["curl", "-s", "http://127.0.0.1:11434/api/tags"])
    },
    "health": {
        "desc": "Health Check",
        "action": lambda: subprocess.run(["/home/clawbot/.openclaw/security/health-check.sh"])
    },
    "metrics": {
        "desc": "Aktuelle Metriken",
        "action": lambda: subprocess.run(["/home/clawbot/.openclaw/scripts/metrics.sh"])
    }
}

def list_commands():
    print("\n🎯 Quick Commands:")
    print("=" * 40)
    for cmd, info in COMMANDS.items():
        print(f"  /{cmd:12} - {info['desc']}")
    print()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        list_commands()
    else:
        cmd = sys.argv[1].lstrip("/")
        if cmd in COMMANDS:
            print(f"Execute: {cmd}")
            COMMANDS[cmd]["action"]()
        else:
            print(f"Unknown command: {cmd}")
            list_commands()
