#!/usr/bin/env python3
"""
Humanized Outreach Email - After Humanizer
Target: Non-IT businesses (restaurants, handwerk, fitness, etc.)
"""
import subprocess
import os

TOKEN = os.environ.get("GOG_ACCESS_TOKEN", "")

# Humanized version (after running through humanizer skill)
SUBJECT = "Mal was anderes: AI-Hosting fürs deutsche Handwerk"

BODY = """Hallo,

kurze Frage: Haben Sie schonmal drüber nachgedacht, eigene AI-Tools auf deutschen Servern zu nutzen?

Ich bin dabei, deutschen Handwerkern, Restaurants und Kleinunternehmern zu helfen, ihre eigene AI-Infrastruktur aufzusetzen - ohne dass sie sich um Server, Updates oder US-Cloud kümmern müssen.

Warum das interessant sein könnte:
- Ihre Daten bleiben in Deutschland (DSGVO)
- Kein Stress mit IT-Administration
- Fixe Kosten, kein Technik-Gedöns

Falls Sie interesse haben, schicke ich Ihnen gerne mehr Details.

Viele Grüße
Nico

P.S. Falls das nicht passt - kein Problem, dann einfach ignore."""

def send_humanized(email, company):
    """Send humanized outreach"""
    result = subprocess.run([
        "gog", "gmail", "send",
        "--to", email,
        "--subject", SUBJECT,
        "--body", BODY,
        "--access-token", TOKEN,
        "--account", "empirehazeclaw@gmail.com"
    ], capture_output=True, text=True)
    
    if "message_id" in result.stdout:
        return True, result.stdout.split()[1]
    return False, result.stderr

# Test
if __name__ == "__main__":
    print("=== HUMANIZED OUTREACH ===")
    print("")
    print("Subject:", SUBJECT)
    print("")
    print("Body:")
    print(BODY)
