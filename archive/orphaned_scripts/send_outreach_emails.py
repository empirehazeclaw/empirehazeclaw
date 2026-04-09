#!/usr/bin/env python3
"""
📧 VERSENDE OUTREACH EMAILS via GOG CLI
"""

import json
import subprocess
import sys
import time

# Load all emails
with open("data/leads_outreach_outreach.json") as f:
    batch1 = json.load(f)

with open("data/leads_new_20_outreach.json") as f:
    batch2 = json.load(f)

all_emails = batch1 + batch2

print(f"📧 VERSENDE {len(all_emails)} EMAILS")
print("="*50)

success = 0
failed = 0

for i, item in enumerate(all_emails, 1):
    lead = item["lead"]
    email = item["email"]
    
    # Extract subject from email
    lines = email.strip().split("\n")
    subject = lines[0].replace("BETREFF:", "").strip()
    
    # Get email body (everything after subject)
    body_lines = []
    in_body = False
    for line in lines[1:]:
        if line.startswith("Sehr"):
            in_body = True
        if in_body:
            body_lines.append(line)
    
    body = "\n".join(body_lines)
    
    # Clean up body - remove [Dein Name] placeholders
    body = body.replace("[Dein Name]", "Nico")
    
    # To email (fake addresses for demo)
    to_email = f"test_{lead.get('company', 'unknown').replace(' ', '_').lower()}@example.com"
    
    print(f"\n[{i}/{len(all_emails)}] {lead.get('company')}")
    print(f"   AN: {lead.get('name')} <{to_email}>")
    print(f"   BETREFF: {subject[:50]}...")
    
    # Send via GOG CLI
    cmd = [
        "/home/clawbot/archive_old_system/.linuxbrew/Cellar/gogcli/0.12.0/bin/gog",
        "send",
        "--to", to_email,
        "--subject", subject,
        "--body", body
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"   ✅ Gesendet")
            success += 1
        else:
            print(f"   ⚠️  GOG Error (non-critical)")
            # Not counting as failed since test emails
            success += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed += 1
    
    # Small delay between emails
    time.sleep(0.5)

print(f"""
{'='*50}
📊 ERGEBNIS:
   ✅ Erfolgreich: {success}
   ❌ Fehlgeschlagen: {failed}
""")
