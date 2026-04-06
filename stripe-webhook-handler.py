#!/usr/bin/env python3
"""
💳 Stripe Webhook Handler - EmpireHazeClaw
Verarbeitet Stripe Payments automatisch

Usage:
    python3 stripe-webhook-handler.py --setup
    python3 stripe-webhook-handler.py --test

Endpoints:
    /webhook/stripe - Stripe Webhook
    /api/invoices - Invoice Status
"""

import json
import hmac
import hashlib
import time
from pathlib import Path
from datetime import datetime

WEBHOOK_SECRET = "whsec_dein_geheimnis"  # Von Stripe Dashboard
INVOICES_FILE = Path("/home/clawbot/.openclaw/workspace/data/invoices.json")
LOG_FILE = Path("/home/clawbot/.openclaw/workspace/data/stripe_log.txt")

def load_invoices():
    if not INVOICES_FILE.exists():
        return {}
    with open(INVOICES_FILE) as f:
        return json.load(f)

def save_invoices(invoices):
    with open(INVOICES_FILE, 'w') as f:
        json.dump(invoices, f, indent=2)

def log_event(event_type, data):
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {event_type}: {json.dumps(data)}\n")

def handle_payment_intent_succeeded(data):
    """Neue Zahlung erhalten"""
    pi = data.get("payment_intent", {})
    amount = pi.get("amount", 0) / 100  # Stripe uses cents
    
    invoices = load_invoices()
    invoice_id = f"INV-{int(time.time())}"
    
    invoices[invoice_id] = {
        "stripe_id": pi.get("id"),
        "amount": amount,
        "currency": pi.get("currency", "eur").upper(),
        "status": "paid",
        "customer_email": pi.get("receipt_email", ""),
        "description": pi.get("description", "Managed AI Hosting"),
        "created": datetime.now().isoformat(),
        "paid_at": datetime.now().isoformat()
    }
    
    save_invoices(invoices)
    log_event("PAYMENT_SUCCESS", {"invoice": invoice_id, "amount": amount})
    
    print(f"✅ Zahlung erhalten: €{amount} - Invoice: {invoice_id}")
    
    # Hier könnte eine Email-Benachrichtigung gesendet werden
    # send_email_receipt(invoice_id)
    
    return {"status": "success", "invoice_id": invoice_id}

def handle_subscription_created(data):
    """Neues Abonnement"""
    sub = data.get("subscription", {})
    
    invoices = load_invoices()
    sub_id = sub.get("id")
    
    invoices[f"sub_{sub_id}"] = {
        "stripe_id": sub_id,
        "status": "active",
        "plan": sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("nickname", "Standard"),
        "current_period_start": datetime.fromtimestamp(sub.get("current_period_start", 0)).isoformat(),
        "current_period_end": datetime.fromtimestamp(sub.get("current_period_end", 0)).isoformat(),
        "created": datetime.now().isoformat()
    }
    
    save_invoices(invoices)
    log_event("SUBSCRIPTION_CREATED", {"subscription": sub_id})
    
    print(f"✅ Neues Abo: {sub_id}")
    return {"status": "success"}

def handle_subscription_deleted(data):
    """Abo gekündigt"""
    sub = data.get("subscription", {})
    sub_id = sub.get("id")
    
    invoices = load_invoices()
    if f"sub_{sub_id}" in invoices:
        invoices[f"sub_{sub_id}"]["status"] = "canceled"
        save_invoices(invoices)
        log_event("SUBSCRIPTION_CANCELED", {"subscription": sub_id})
        print(f"⚠️ Abo gekündigt: {sub_id}")
    
    return {"status": "success"}

def verify_signature(payload, signature, secret):
    """Verify Stripe webhook signature"""
    try:
        sig_parts = dict(item.split('=') for item in signature.split(','))
        timestamp = sig_parts.get('t', '')
        expected_sig = hmac.new(
            secret.encode(),
            f"{timestamp}.".encode() + payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected_sig, sig_parts.get('v1', ''))
    except:
        return False

def process_webhook(event_type, data):
    """Route webhook to appropriate handler"""
    handlers = {
        "payment_intent.succeeded": handle_payment_intent_succeeded,
        "subscription.created": handle_subscription_created,
        "subscription.deleted": handle_subscription_deleted,
        "customer.subscription.deleted": handle_subscription_deleted,
    }
    
    handler = handlers.get(event_type)
    if handler:
        return handler(data)
    
    print(f"ℹ️ Unhandled event: {event_type}")
    return {"status": "ignored"}

def list_invoices():
    invoices = load_invoices()
    
    if not invoices:
        print("Keine Rechnungen vorhanden!")
        return
    
    print(f"\n{'='*60}")
    print(f"💳 INVOICES - {len(invoices)} Einträge")
    print(f"{'='*60}\n")
    
    total = 0
    for inv_id, inv in invoices.items():
        amount = inv.get("amount", 0)
        status = inv.get("status", "")
        status_icon = {"paid": "✅", "pending": "⏳", "canceled": "❌"}.get(status, "❓")
        
        print(f"{status_icon} {inv_id}")
        print(f"   💰 €{amount} ({inv.get('currency', 'EUR')})")
        print(f"   📧 {inv.get('customer_email', 'keine Email')}")
        print(f"   📅 {inv.get('created', '')[:10]}")
        print()
        
        if status == "paid":
            total += amount
    
    print(f"{'='*60}")
    print(f"💵 Total Revenue: €{total}")
    print(f"{'='*60}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nBefehle:")
        print("  --setup     Webhook einrichten (Anleitung)")
        print("  --test      Test-Webhook senden")
        print("  --list      Alle Rechnungen anzeigen")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--setup":
        print("""
╔═══════════════════════════════════════════════════════════════╗
║  💳 Stripe Webhook Setup                               ║
╚═══════════════════════════════════════════════════════════════╝

1. Stripe Dashboard öffnen:
   https://dashboard.stripe.com/settings/webhooks

2. Endpoint hinzufügen:
   URL: https://empirehazeclaw.com/webhook/stripe

3. Events auswählen:
   ✓ payment_intent.succeeded
   ✓ subscription.created
   ✓ subscription.deleted
   ✓ customer.subscription.deleted

4. Webhook Secret kopieren:
   whsec_...

5. Hier eintragen:
   WEBHOOK_SECRET = "whsec_dein_geheimnis"
""")
    
    elif cmd == "--test":
        # Simulate a test webhook
        test_event = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "id": "pi_test123",
                    "amount": 9900,
                    "currency": "eur",
                    "receipt_email": "test@example.com",
                    "description": "Managed AI Hosting - Starter Plan"
                }
            }
        }
        process_webhook(test_event["type"], test_event["data"])
    
    elif cmd == "--list":
        list_invoices()
    
    else:
        print(f"Unbekannter Befehl: {cmd}")

if __name__ == "__main__":
    main()
