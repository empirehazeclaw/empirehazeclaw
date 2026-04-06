#!/usr/bin/env python3
"""
Message Gateway Wrapper
Leitet alle Nachrichten durch Security Filter
"""

import sys
import os

# Security Filter importieren
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')
from security_filter import SecurityFilter

def preprocess_message(prompt: str, sender_id: str = None, chat_type: str = "dm") -> dict:
    """Pre-processes message through security filter"""
    
    filter = SecurityFilter()
    context = {"chat_type": chat_type}
    
    result = filter.analyze(prompt, sender_id, context)
    
    return result

# Test wenn direkt aufgerufen
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        result = preprocess_message(prompt)
        
        print(f"🔒 Security Check: {result['emoji']} {result['risk_level']} ({result['risk_score']}/10)")
        print(f"   Action: {result['action']}")
        
        for finding in result['findings']:
            print(f"   • {finding}")
        
        if result['action'] == "BLOCK":
            print("\n⛔ Message BLOCKED")
            sys.exit(1)
        else:
            print("\n✅ Message ALLOWED")
    else:
        print("Usage: message_filter.py <prompt>")
