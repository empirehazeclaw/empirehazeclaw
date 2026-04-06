#!/usr/bin/env python3
"""
🎧 Support AI Agent - Generic Version
Beantwortet FAQs und Kundenanfragen
"""
import json
import os
from datetime import datetime

CONFIG_FILE = "config/support_config.json"
FAQ_FILE = "data/faq.json"
TICKETS_FILE = "data/support_tickets.json"

DEFAULT_FAQS = [
    {"q": "wie sind eure öffnungszeiten", "a": "Unsere Öffnungszeiten finden Sie auf unserer Website."},
    {"q": "wie kann ich kontakt aufnehmen", "a": "Sie können uns per Email unter info@firma.de oder telefonisch erreichen."},
    {"q": "haben sie noch verfügbar", "a": "Ja, wir haben noch Verfügbarkeiten. Kontaktieren Sie uns für Details."},
    {"q": "was kostet", "a": "Unsere Preise finden Sie auf unserer Website oder kontaktieren Sie uns für ein Angebot."},
]

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "business_name": "Unser Unternehmen",
        "email": "info@firma.de",
        "response_tone": "professional"
    }

def load_faqs():
    if os.path.exists(FAQ_FILE):
        with open(FAQ_FILE) as f:
            return json.load(f)
    return DEFAULT_FAQS

def find_answer(question, faqs):
    """Find passende FAQ Antwort"""
    q_lower = question.lower()
    
    for faq in faqs:
        keywords = faq["q"].lower().split()
        matches = sum(1 for kw in keywords if kw in q_lower)
        if matches >= 1:
            return faq["a"]
    
    return None  # Kein Match -> Eskalation nötig

def create_ticket(question, customer_email):
    """Erstelle Support Ticket"""
    tickets = []
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE) as f:
            tickets = json.load(f)
    
    ticket = {
        "id": len(tickets) + 1,
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "customer_email": customer_email,
        "status": "open"
    }
    
    tickets.append(ticket)
    
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=2)
    
    return ticket

def answer_question(question, customer_email="unbekannt"):
    """Hauptfunktion"""
    config = load_config()
    faqs = load_faqs()
    
    # Versuche FAQ Antwort zu finden
    answer = find_answer(question, faqs)
    
    if answer:
        return {
            "status": "answered",
            "answer": answer,
            "escalate": False
        }
    else:
        # Erstelle Ticket für menschliches Follow-up
        ticket = create_ticket(question, customer_email)
        return {
            "status": "escalated",
            "answer": f"Vielen Dank für Ihre Frage. Da diese nicht automatisch beantwortet werden kann, habe ich ein Ticket erstellt (#{ticket['id']}). Wir melden uns innerhalb von 24 Stunden bei Ihnen.",
            "ticket_id": ticket["id"],
            "escalate": True
        }

def get_open_tickets():
    """Zeige offene Tickets"""
    if not os.path.exists(TICKETS_FILE):
        return []
    
    with open(TICKETS_FILE) as f:
        tickets = json.load(f)
    
    return [t for t in tickets if t["status"] == "open"]

if __name__ == "__main__":
    print("🎧 Support Agent gestartet...")
    
    # Test
    result = answer_question("Wie sind eure Öffnungszeiten?")
    print(f"Antwort: {result['answer']}")
    
    open_tickets = get_open_tickets()
    print(f"📋 Offene Tickets: {len(open_tickets)}")
    
    print("✅ Support Agent fertig")
