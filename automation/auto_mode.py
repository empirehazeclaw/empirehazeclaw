#!/usr/bin/env python3
"""
Auto-Mode System - ClawBot Autonomous Operations
Automatisch arbeiten + nur bei wichtigen Entscheidungen fragen
"""

import json
import os
from datetime import datetime, timedelta
from enum import Enum

# Auto-Mode Levels
class AutoModeLevel(Enum):
    OFF = 0        # Manual mode - frage bei allem
    LOW = 1        # Nur kleine Entscheidungen selbst
    MEDIUM = 2     # Die meisten Dinge selbst
    HIGH = 3       # Fast alles selbstständig
    MAX = 4        # Vollautonom

# Configuration
CONFIG_FILE = "/home/clawbot/.openclaw/config/auto_mode.json"

# Action Categories - Was ich selbst machen darf
AUTO_ACTIONS = {
    # Level 1 (LOW) - Darf ich selbst machen
    "LOW": [
        "research",
        "summarize",
        "weather",
        "memory_search",
        "health_check",
        "system_status",
    ],
    
    # Level 2 (MEDIUM) - Zusätzlich erlaubt
    "MEDIUM": [
        "social_content_create",
        "blog_post",
        "newsletter",
        "trend_analysis",
        "competitor_analysis",
        "product_research",
        "send_reminder",
    ],
    
    # Level 3 (HIGH) - Zusätzlich erlaubt
    "HIGH": [
        "post_social",
        "create_listing",
        "update_price",
        "reply_message",
        "run_agent",
        "create_backup",
    ],
    
    # Level 4 (MAX) - Alles erlaubt
    "MAX": [
        "spend_money",
        "delete_data",
        "account_change",
        "security_change",
    ]
}

# Confirmation Required Actions - Immer nachfragen
CONFIRMATION_REQUIRED = [
    "spend_money",      # Geld ausgeben
    "delete_data",      # Daten löschen
    "account_change",   # Konto ändern
    "security_change",  # Sicherheit ändern
    "post_to_etsy",     # Auf Etsy posten
    "post_to_fiverr",   # Auf Fiverr posten
    "upload_design",    # Design hochladen
    "change_price",     # Preis ändern
    "respond_critical",  # Kritische Antworten
    "reply_message",    # Nachrichten beantworten
]

class AutoMode:
    def __init__(self, level=AutoModeLevel.MEDIUM):
        self.level = level
        self.load_config()
    
    def load_config(self):
        """Lade Konfiguration"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                self.level = AutoModeLevel(config.get("level", 2))
                self.confirm_queue = config.get("confirm_queue", [])
                self.auto_actions = config.get("auto_actions", [])
        else:
            self.confirm_queue = []
            self.auto_actions = []
    
    def save_config(self):
        """Speichere Konfiguration"""
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "level": self.level.value,
                "confirm_queue": self.confirm_queue,
                "auto_actions": self.auto_actions,
                "last_updated": datetime.now().isoformat()
            }, f, indent=2)
    
    def can_do(self, action: str) -> tuple[bool, str]:
        """Prüfe ob ich diese Aktion selbst machen darf"""
        
        # Immer nachfragen bei kritischen Aktionen
        if action in CONFIRMATION_REQUIRED:
            return False, f"Kritische Aktion: {action} - Bestätigung nötig"
        
        # Level 0 = alles nachfragen
        if self.level == AutoModeLevel.OFF:
            return False, "Auto-Mode ist aus"
        
        # Check action permissions by level
        allowed = False
        reason = ""
        
        if self.level.value >= 1:
            if action in AUTO_ACTIONS["LOW"]:
                allowed = True
                reason = "Erlaubt (LOW+)"
        
        if not allowed and self.level.value >= 2:
            if action in AUTO_ACTIONS["MEDIUM"]:
                allowed = True
                reason = "Erlaubt (MEDIUM+)"
        
        if not allowed and self.level.value >= 3:
            if action in AUTO_ACTIONS["HIGH"]:
                allowed = True
                reason = "Erlaubt (HIGH+)"
        
        if not allowed:
            reason = f"Level {self.level.value} nicht hoch genug"
        
        return allowed, reason
    
    def should_confirm(self, action: str) -> bool:
        """Soll ich bei dieser Aktion bestätigen?"""
        return action in CONFIRMATION_REQUIRED
    
    def set_level(self, level: str):
        """Setze Auto-Mode Level"""
        try:
            self.level = AutoModeLevel[level.upper()]
            self.save_config()
            return True, f"Auto-Mode gesetzt auf: {level}"
        except KeyError:
            return False, f"Unbekanntes Level: {level}"
    
    def get_status(self) -> dict:
        """Gib Status zurück"""
        return {
            "level": self.level.name,
            "level_value": self.level.value,
            "allowed_actions": self.get_allowed_actions(),
            "confirmation_required": CONFIRMATION_REQUIRED
        }
    
    def get_allowed_actions(self) -> list:
        """Liste erlaubte Aktionen auf"""
        allowed = []
        if self.level.value >= 1:
            allowed.extend(AUTO_ACTIONS["LOW"])
        if self.level.value >= 2:
            allowed.extend(AUTO_ACTIONS["MEDIUM"])
        if self.level.value >= 3:
            allowed.extend(AUTO_ACTIONS["HIGH"])
        return allowed

# Example usage
if __name__ == "__main__":
    auto = AutoMode(AutoModeLevel.MEDIUM)
    
    print("🦾 Auto-Mode Status")
    print("=" * 50)
    
    status = auto.get_status()
    print(f"Level: {status['level']} ({status['level_value']})")
    print(f"\nErlaubte Aktionen:")
    for action in status['allowed_actions']:
        print(f"  ✅ {action}")
    
    print(f"\nBestätigung erforderlich:")
    for action in status['confirmation_required']:
        print(f"  ⚠️ {action}")
