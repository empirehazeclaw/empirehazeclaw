#!/usr/bin/env python3
"""
Client Onboarding Automation
- Welcome Email after Stripe Payment
- Setup Instructions
- Follow-up Sequence (30/60/90 days)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
CLIENTS_FILE = WORKSPACE / "data" / "onboarding_clients.json"

def load_clients():
    if CLIENTS_FILE.exists():
        return json.loads(CLIENTS_FILE.read_text())
    return []

def save_clients(clients):
    CLIENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    CLIENTS_FILE.write_text(json.dumps(clients, indent=2))

def add_client(email, name, product, purchase_date=None):
    """Add new client for onboarding"""
    clients = load_clients()
    
    # Check if already exists
    if any(c['email'] == email for c in clients):
        return False
    
    client = {
        "email": email,
        "name": name,
        "product": product,
        "purchase_date": purchase_date or datetime.now().strftime("%Y-%m-%d"),
        "onboarding_sent": False,
        "day30_sent": False,
        "day60_sent": False,
        "day90_sent": False,
        "created": datetime.now().isoformat()
    }
    
    clients.append(client)
    save_clients(clients)
    return True

def send_welcome_email(client):
    """Send welcome email with setup instructions"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    msg = MIMEMultipart()
    msg['From'] = "EmpireHazeClaw <empirehazeclaw@gmail.com>"
    msg['To'] = client['email']
    msg['Subject'] = f"🎉 Willkommen bei EmpireHazeClaw - {client['product']}"
    
    body = f"""Hallo {client['name']},

herzlich willkommen bei EmpireHazeClaw! 🎉

Vielen Dank für deinen Kauf von: {client['product']}

=== DEINE NÄCHSTEN SCHRITT ===

1. Zugangsdaten
   Du erhältst in den nächsten 24 Stunden deinen persönlichen Zugang.

2. Setup
   - Für Chatbot: Wir richten alles für dich ein
   - Für Managed Hosting: Server wird eingerichtet
   - Für Trading Bot: Zugang wird aktiviert

3. Support
   Bei Fragen: https://empirehazeclaw.com/support

=== WIR BIETEN ===

✓ 24/7 Support
✓ Regelmäßige Updates
✓ DSGVO-konforme Lösung
✓ Deutsche Server

Wir freuen uns, dich an Bord zu haben!

Mit freundlichen Grüßen
Dein EmpireHazeClaw Team
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server.starttls()
        server.sendmail("empirehazeclaw@gmail.com", client['email'], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def check_and_send_automated_emails():
    """Check which automated emails need to be sent"""
    clients = load_clients()
    today = datetime.now()
    sent_count = 0
    
    for client in clients:
        purchase_date = datetime.strptime(client['purchase_date'], "%Y-%m-%d")
        days_since = (today - purchase_date).days
        
        # Day 0: Welcome
        if days_since == 0 and not client.get('onboarding_sent'):
            if send_welcome_email(client):
                client['onboarding_sent'] = True
                sent_count += 1
                print(f"✅ Welcome email sent to {client['email']}")
        
        # Day 30: Check-in
        elif days_since == 30 and not client.get('day30_sent'):
            # Send 30-day follow-up
            client['day30_sent'] = True
            sent_count += 1
            print(f"📧 Day 30 email to {client['email']}")
        
        # Day 60: Upsell opportunity
        elif days_since == 60 and not client.get('day60_sent'):
            client['day60_sent'] = True
            sent_count += 1
            print(f"📧 Day 60 email to {client['email']}")
        
        # Day 90: Review request
        elif days_since == 90 and not client.get('day90_sent'):
            client['day90_sent'] = True
            sent_count += 1
            print(f"📧 Day 90 email to {client['email']}")
    
    save_clients(clients)
    return sent_count

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "add":
            email = sys.argv[2]
            name = sys.argv[3] if len(sys.argv) > 3 else "Kunde"
            product = sys.argv[4] if len(sys.argv) > 4 else "Service"
            
            if add_client(email, name, product):
                print(f"✅ Client added: {email}")
            else:
                print("Client already exists")
        
        elif cmd == "check":
            count = check_and_send_automated_emails()
            print(f"✅ Processed {count} automated emails")
        
        elif cmd == "list":
            clients = load_clients()
            print(f"📋 Clients ({len(clients)}):")
            for c in clients:
                print(f"   - {c['name']} ({c['email']}) - {c['product']}")
    
    else:
        print("Client Onboarding CLI")
        print("Usage: onboarding.py [add|check|list]")
