#!/usr/bin/env python3
"""
📧 Email Processor mit Prompt Injection Shield
集成 - Integrated Shield in Email Workflow
"""
import sys
sys.path.append('/home/clawbot/.openclaw/workspace/scripts')

from prompt_injection_shield import analyze_text, check_email

def process_email(email_body: str) -> dict:
    """Process email with security check"""
    
    # First, check for prompt injection
    security = check_email(email_body)
    
    result = {
        "security": security,
        "content": email_body if security["risk_level"] == "SAFE" else security.get("sanitized", email_body),
        "proceed": security["risk_level"] == "SAFE"
    }
    
    if security["risk_level"] != "SAFE":
        print(f"⚠️ Security Alert: {security['risk_level']} - {security['details']}")
    
    return result

# Example usage
if __name__ == "__main__":
    import json
    
    # Test with normal email
    test_email = """
    Hallo,
    
    ich interessiere mich für Ihre KI-Chatbot Services.
    
    Viele Grüße
    Max Müller
    """
    
    result = process_email(test_email)
    print(json.dumps(result, indent=2))
