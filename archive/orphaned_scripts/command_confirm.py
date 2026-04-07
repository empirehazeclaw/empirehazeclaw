#!/usr/bin/env python3
"""
Command Confirmation System
Fragt bei riskanten Commands nach Bestätigung
"""

import sys

# Commands that need confirmation
CONFIRM_COMMANDS = {
    # File operations
    "delete": ["lösche", "delete", "remove", "rm ", "rmdir"],
    "write": ["schreibe", "write ", "create ", "new file"],
    "edit": ["editiere", "edit ", "ändere", "modify"],
    "backup": ["backup", "sicherung"],
    
    # System operations
    "restart": ["restart", "neustart", "reboot"],
    "stop": ["stop ", "beenden", "kill "],
    "install": ["install", "installiere", "apt ", "pip install"],
    
    # Security sensitive
    "security": ["security", "sicherheit", "firewall", "iptables"],
    "sudo": ["sudo ", "root", "chmod 777"],
}

RISK_THRESHOLD = 4  # Ab diesem Risiko nachfragen

def check_confirmation(prompt: str) -> dict:
    """Prüft ob Command Bestätigung braucht"""
    
    prompt_lower = prompt.lower()
    
    # Check for dangerous commands
    for category, keywords in CONFIRM_COMMANDS.items():
        for keyword in keywords:
            if keyword in prompt_lower:
                return {
                    "needs_confirmation": True,
                    "category": category,
                    "keyword": keyword,
                    "warning": f"⚠️ This command ({category}) requires confirmation!"
                }
    
    return {"needs_confirmation": False}

def confirm_action(prompt: str) -> bool:
    """Fragt nach Bestätigung"""
    
    check = check_confirmation(prompt)
    
    if not check["needs_confirmation"]:
        return True
    
    print(f"\n{'='*50}")
    print(f"⚠️  BESTÄTIGUNG NÖTIG!")
    print(f"{'='*50}")
    print(f"Command erkannt: {check['keyword']}")
    print(f"Kategorie: {check['category']}")
    print(f"\nPrompt: {prompt[:100]}...")
    print(f"\n[ja/nein]: ", end="")
    
    # In automated mode: deny by default
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = check_confirmation(prompt)
        
        if result["needs_confirmation"]:
            print(f"⚠️ Confirm needed: {result['category']}")
            sys.exit(2)  # Needs confirmation
        else:
            sys.exit(0)  # OK
