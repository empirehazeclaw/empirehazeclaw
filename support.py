#!/usr/bin/env python3
"""
Customer Support Ticket System
- Kunden können Probleme melden
- Tickets werden getrackt und priorisiert
- Automatische Antworten
"""

import json
import os
from datetime import datetime
from pathlib import Path
from enum import Enum

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
TICKETS_DIR = WORKSPACE / "data" / "support_tickets"

class Status(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING = "waiting"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

def generate_ticket_id():
    """Generiert Ticket-ID: SUP-2026-0001"""
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(TICKETS_DIR.glob("SUP-*.json"))
    if existing:
        try:
            last_num = int(existing[-1].name.split("-")[-1].split(".")[0])
            return f"SUP-{datetime.now().year}-{last_num + 1:04d}"
        except:
            pass
    return f"SUP-{datetime.now().year}-0001"

def create_ticket(customer_email, customer_name, subject, description, priority="medium"):
    """Erstellt neues Support-Ticket"""
    ticket_id = generate_ticket_id()
    
    ticket = {
        "id": ticket_id,
        "status": Status.OPEN.value,
        "priority": priority,
        "subject": subject,
        "description": description,
        "customer_email": customer_email,
        "customer_name": customer_name,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "messages": [
            {
                "from": customer_email,
                "message": description,
                "timestamp": datetime.now().isoformat()
            }
        ],
        "assigned_to": None,
        "resolution": None
    }
    
    # Save ticket
    with open(TICKETS_DIR / f"{ticket_id}.json", 'w') as f:
        json.dump(ticket, f, indent=2)
    
    # Auto-response to customer
    send_auto_response(customer_email, ticket_id, subject)
    
    return ticket

def send_auto_response(customer_email, ticket_id, subject):
    """Sendet automatische Bestätigung"""
    # TODO: Use Brevo
    print(f"📧 Auto-Response an {customer_email}: Ticket {ticket_id} erstellt")
    print(f"   Betreff: {subject}")
    return True

def add_message(ticket_id, from_email, message):
    """Fügt Nachricht zu Ticket hinzu"""
    file_path = TICKETS_DIR / f"{ticket_id}.json"
    if not file_path.exists():
        return {"error": "Ticket nicht gefunden"}
    
    with open(file_path) as f:
        ticket = json.load(f)
    
    # Add message
    ticket["messages"].append({
        "from": from_email,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    ticket["updated"] = datetime.now().isoformat()
    
    # If customer responds, set to waiting
    if from_email == ticket["customer_email"]:
        ticket["status"] = Status.WAITING.value
    
    # Save
    with open(file_path, 'w') as f:
        json.dump(ticket, f, indent=2)
    
    return ticket

def update_status(ticket_id, status):
    """Aktualisiert Ticket-Status"""
    file_path = TICKETS_DIR / f"{ticket_id}.json"
    if not file_path.exists():
        return {"error": "Ticket nicht gefunden"}
    
    with open(file_path) as f:
        ticket = json.load(f)
    
    ticket["status"] = status
    ticket["updated"] = datetime.now().isoformat()
    
    with open(file_path, 'w') as f:
        json.dump(ticket, f, indent=2)
    
    return ticket

def get_tickets(status=None, priority=None):
    """Listet alle Tickets auf"""
    TICKETS_DIR.mkdir(parents=True, exist_ok=True)
    tickets = []
    
    for file in TICKETS_DIR.glob("SUP-*.json"):
        with open(file) as f:
            t = json.load(f)
        
        # Filter
        if status and t["status"] != status:
            continue
        if priority and t["priority"] != priority:
            continue
        
        tickets.append(t)
    
    # Sort by date (newest first)
    tickets.sort(key=lambda x: x["created"], reverse=True)
    return tickets

def get_ticket(ticket_id):
    """Holt einzelnes Ticket"""
    file_path = TICKETS_DIR / f"{ticket_id}.json"
    if not file_path.exists():
        return None
    
    with open(file_path) as f:
        return json.load(f)

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "list":
            tickets = get_tickets()
            print(f"📋 Support Tickets ({len(tickets)})")
            for t in tickets:
                print(f"  [{t['priority'].upper()}] {t['id']} - {t['subject']} ({t['status']})")
        
        elif cmd == "create":
            # create <email> <name> <subject> <description>
            create_ticket(sys.argv[2], sys.argv[3], sys.argv[4], " ".join(sys.argv[5:]))
        
        elif cmd == "view":
            t = get_ticket(sys.argv[2])
            if t:
                print(f"\n=== Ticket {t['id']} ===")
                print(f"Status: {t['status']} | Priority: {t['priority']}")
                print(f"Kunde: {t['customer_name']} ({t['customer_email']})")
                print(f"Subject: {t['subject']}")
                print(f"\nNachrichten:")
                for m in t['messages']:
                    print(f"  {m['from']}: {m['message'][:100]}...")
            else:
                print("Ticket nicht gefunden")
        
        else:
            print("Usage: support.py [list|create|view]")
    else:
        # Show summary
        tickets = get_tickets()
        open_tickets = [t for t in tickets if t["status"] == "open"]
        print(f"📋 Support Dashboard")
        print(f"   Gesamt: {len(tickets)}")
        print(f"   Offen: {len(open_tickets)}")
