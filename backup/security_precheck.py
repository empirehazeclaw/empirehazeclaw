#!/usr/bin/env python3
"""
Security Filter Gateway Integration
Pre-Processor für eingehende Nachrichten
"""

import sys
import os
sys.path.insert(0, '/home/clawbot/.openclaw/workspace/scripts')

from security_filter import SecurityFilter

def check_message(prompt: str, sender_id: str = None, chat_type: str = "dm") -> dict:
    """Prüft eine Nachricht vor der Verarbeitung"""
    
    filter = SecurityFilter()
    context = {"chat_type": chat_type}
    
    result = filter.analyze(prompt, sender_id, context)
    
    # Report generieren
    report = f"""
🔒 Security Check:
- Risk: {result['emoji']} {result['risk_level']} ({result['risk_score']}/10)
- Action: {result['action']}
"""
    
    if result['findings']:
        report += "\n🔍 Findings:\n"
        for f in result['findings']:
            report += f"  • {f}\n"
    
    return {
        "allowed": result['action'] in ["ALLOW", "LOG_ALLOW"],
        "result": result,
        "report": report
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: security_precheck.py <prompt> [sender_id] [chat_type]")
        sys.exit(1)
    
    prompt = sys.argv[1]
    sender = sys.argv[2] if len(sys.argv) > 2 else None
    chat = sys.argv[3] if len(sys.argv) > 3 else "dm"
    
    result = check_message(prompt, sender, chat)
    
    print(result["report"])
    
    if not result["allowed"]:
        print(f"\n⛔ Message BLOCKED by Security Filter")
        sys.exit(1)
    else:
        print(f"\n✅ Message ALLOWED")
        sys.exit(0)
