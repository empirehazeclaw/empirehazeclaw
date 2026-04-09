#!/usr/bin/env python3
"""
Auto-Repair Script for OpenClaw Gateway
Prüft Gateway & kritische Dienste, startet bei Bedarf neu.
"""

import subprocess
import requests
import logging
import sys
import os
from datetime import datetime

# Konfiguration
GATEWAY_URL = "http://localhost:18789/status"
GATEWAY_RESTART_CMD = ["openclaw", "gateway", "restart"]
LOG_FILE = "/home/clawbot/.openclaw/logs/auto_repair.log"

# Kritische Dienste, die geprüft werden sollen
CRITICAL_SERVICES = {
    "ollama": "http://localhost:11434/api/tags",
    # Weitere Dienste bei Bedarf hinzufügen
}

# Logging einrichten
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


def log(msg: str, level: str = "info"):
    """Loggt Nachricht zu Console und Datei."""
    print(f"{msg}")
    getattr(logger, level)(msg)


def check_gateway() -> bool:
    """Prüft ob Gateway erreichbar ist."""
    try:
        response = requests.get(GATEWAY_URL, timeout=5)
        if response.status_code == 200:
            log("✅ Gateway ist erreichbar")
            return True
        else:
            log(f"⚠️ Gateway antwortet mit Status {response.status_code}", "warning")
            return False
    except requests.exceptions.RequestException as e:
        log(f"❌ Gateway nicht erreichbar: {e}", "error")
        return False


def check_critical_services() -> dict:
    """Prüft kritische Dienste."""
    results = {}
    for service_name, url in CRITICAL_SERVICES.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                log(f"✅ {service_name} läuft")
                results[service_name] = True
            else:
                log(f"⚠️ {service_name} antwortet mit {response.status_code}", "warning")
                results[service_name] = False
        except requests.exceptions.RequestException as e:
            log(f"❌ {service_name} nicht verfügbar: {e}", "error")
            results[service_name] = False
    return results


def restart_gateway() -> bool:
    """Startet den Gateway neu."""
    log("🔄 Starte Gateway neu...", "warning")
    try:
        result = subprocess.run(
            GATEWAY_RESTART_CMD,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            log("✅ Gateway erfolgreich neu gestartet")
            return True
        else:
            log(f"❌ Gateway Neustart fehlgeschlagen: {result.stderr}", "error")
            return False
    except subprocess.TimeoutExpired:
        log("❌ Gateway Neustart Timeout", "error")
        return False
    except Exception as e:
        log(f"❌ Fehler beim Gateway Neustart: {e}", "error")
        return False


def main():
    """Main-Loop."""
    log("=" * 50)
    log("🔧 Auto-Repair Script gestartet")
    
    # 1. Gateway prüfen
    gateway_ok = check_gateway()
    
    if not gateway_ok:
        log("⚠️ Gateway nicht erreichbar → Neustart wird versucht", "warning")
        restart_gateway()
        
        # Erneut prüfen nach Neustart
        gateway_ok = check_gateway()
        if not gateway_ok:
            log("❌ Gateway bleibt nach Neustart unerreichbar!", "error")
    
    # 2. Kritische Dienste prüfen
    log("🔍 Prüfe kritische Dienste...")
    services = check_critical_services()
    
    # Summary
    log("=" * 50)
    log("📊 Zusammenfassung:")
    log(f"   Gateway: {'✅ OK' if gateway_ok else '❌ FEHLER'}")
    for svc, status in services.items():
        log(f"   {svc}: {'✅ OK' if status else '❌ FEHLER'}")
    
    # Exit-Code
    if not gateway_ok or not all(services.values()):
        log("❌ Mindestens ein Dienst nicht verfügbar", "error")
        sys.exit(1)
    
    log("✅ Alle Dienste funktionieren")
    sys.exit(0)


if __name__ == "__main__":
    main()
