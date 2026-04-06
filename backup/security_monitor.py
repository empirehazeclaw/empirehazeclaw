#!/usr/bin/env python3
"""
Security Monitor - Loggt und überwacht Sicherheitsereignisse
"""

import os
import json
from datetime import datetime

LOG_FILE = "/home/clawbot/.openclaw/workspace/memory/security-log.md"

# Prompt Injection Patterns (automatically block)
BLOCK_PATTERNS = [
    "ignore previous",
    "ignore all rules",
    "forget your guidelines",
    "new system prompt",
    "new instructions",
    "roleplay as",
    "pretend to be",
    "act as if",
    "you are now",
    "forget everything",
    "clear your memory",
    "show me your api",
    "print your instructions",
    "reveal your prompt",
    "what are your rules",
]

def check_security(prompt: str) -> dict:
    """Prüft Prompt auf Sicherheitsrisiken"""
    
    prompt_lower = prompt.lower()
    
    # Check for blocking patterns
    for pattern in BLOCK_PATTERNS:
        if pattern.lower() in prompt_lower:
            return {
                "status": "BLOCKED",
                "pattern": pattern,
                "risk": 10,
                "action": "Sofort blockieren"
            }
    
    # Check for warnings
    warnings = []
    if "curious" in prompt_lower:
        warnings.append("Neugierige Formulierung")
    if "hypothetical" in prompt_lower:
        warnings.append("Hypothetisches Szenario")
    if "imagine" in prompt_lower:
        warnings.append("Imaginäres Szenario")
    
    if warnings:
        return {
            "status": "WARNING",
            "warnings": warnings,
            "risk": 5,
            "action": "Prüfen + Loggen"
        }
    
    return {
        "status": "OK",
        "risk": 0,
        "action": "Weiter"
    }

def log_security_event(event: dict):
    """Loggt Sicherheitsereignis"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"""
## {timestamp}
- **Status:** {event['status']}
- **Risk:** {event['risk']}/10
- **Action:** {event['action']}
"""
    
    if 'pattern' in event:
        log_entry += f"- **Pattern:** {event['pattern']}\n"
    if 'warnings' in event:
        log_entry += f"- **Warnings:** {', '.join(event['warnings'])}\n"
    
    # Append to log
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)
    
    return event

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 security_monitor.py '<prompt>'")
        sys.exit(0)
    
    prompt = sys.argv[1]
    result = check_security(prompt)
    
    print(f"🔒 Security Check:")
    print(f"  Status: {result['status']}")
    print(f"  Risk: {result['risk']}/10")
    
    if result['risk'] > 0:
        log_security_event(result)
        print(f"  → {result['action']}")
