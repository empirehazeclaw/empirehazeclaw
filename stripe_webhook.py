#!/usr/bin/env python3
"""
💳 Stripe Webhook Handler
Triggert Onboarding bei erfolgreicher Zahlung

Usage:
    python3 stripe_webhook.py [--port 5005]

Events handled:
    - checkout.session.completed → Customer bought something
    - payment_intent.succeeded → Payment confirmed

Nach Zahlung:
    1. Kunde in SYSTEM_CORE.md eintragen
    2. Onboarding Agent triggern
    3. Email Bestätigung senden
"""

import os
import sys
import json
import hmac
import hashlib
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.file_lock import locked_write, locked_read, locked_append

# Config
PORT = int(os.environ.get("STRIPE_WEBHOOK_PORT", "5005"))
STRIPE_SECRET = os.environ.get("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")  # whsec_...
LOG_FILE = Path("/home/clawbot/.openclaw/workspace/logs/stripe_webhook.log")
CUSTOMERS_FILE = Path("/home/clawbot/.openclaw/workspace/data/customers.json")
ONBOARD_QUEUE = Path("/home/clawbot/.openclaw/workspace/data/onboarding_queue.json")

def log(msg: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    locked_append(str(LOG_FILE), line)

def verify_webhook(payload: bytes, signature: str) -> bool:
    """Verify Stripe webhook signature with replay protection"""
    if not WEBHOOK_SECRET:
        log("⚠️ WEBHOOK_SECRET not set - skipping verification", "WARN")
        return True
    
    try:
        parts = dict(item.split("=") for item in signature.split(","))
        timestamp = parts.get("t", "")
        expected_sig = parts.get("v1", "")
        
        # REPLAY PROTECTION: Check timestamp is recent (within 5 minutes)
        import time
        if timestamp:
            try:
                event_time = int(timestamp)
                current_time = int(time.time())
                if abs(current_time - event_time) > 300:  # 5 minute tolerance
                    log(f"❌ Replay attack detected: timestamp {timestamp} too old", "ERROR")
                    return False
            except ValueError:
                log(f"⚠️ Invalid timestamp: {timestamp}", "WARN")
        
        signed_payload = f"{timestamp}.{payload.decode()}"
        computed = hmac.new(
            WEBHOOK_SECRET.encode(),
            signed_payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed, expected_sig)
    except Exception as e:
        log(f"Verification failed: {e}", "ERROR")
        return False

def handle_checkout_completed(event: dict):
    """Handle successful checkout"""
    session = event.get("data", {}).get("object", {})
    
    customer_email = session.get("customer_email", "")
    customer_name = session.get("customer_details", {}).get("name", "")
    amount = session.get("amount_total", 0) / 100  # Convert from cents
    currency = session.get("currency", "eur").upper()
    product = session.get("line_items", {}).get("data", [{}])[0].get("description", "Unknown")
    
    log(f"💳 Checkout completed: {customer_email} - {product} - {amount} {currency}")
    
    # Build customer record
    customer = {
        "email": customer_email,
        "name": customer_name,
        "product": product,
        "amount": amount,
        "currency": currency,
        "session_id": session.get("id", ""),
        "status": "paid",
        "created": datetime.now().isoformat(),
        "onboarding_status": "pending"
    }
    
    # Save to customers
    customers = locked_read(str(CUSTOMERS_FILE), [])
    customers.append(customer)
    locked_write(str(CUSTOMERS_FILE), customers)
    
    # Add to onboarding queue
    queue = locked_read(str(ONBOARD_QUEUE), [])
    queue.append({
        "email": customer_email,
        "name": customer_name,
        "product": product,
        "added": datetime.now().isoformat()
    })
    locked_write(str(ONBOARD_QUEUE), queue)
    
    # Trigger onboarding
    trigger_onboarding(customer)
    
    log(f"✅ Customer {customer_email} saved and onboarding queued", "INFO")

def handle_payment_intent_succeeded(event: dict):
    """Handle successful payment"""
    pi = event.get("data", {}).get("object", {})
    email = pi.get("receipt_email", "") or pi.get("metadata", {}).get("email", "")
    amount = pi.get("amount", 0) / 100
    
    log(f"💰 Payment succeeded: {email} - {amount} EUR")
    
    return {
        "email": email,
        "amount": amount,
        "status": "paid"
    }

def trigger_onboarding(customer: dict):
    """Trigger onboarding process for customer"""
    onboarding_msg = f"""
🎉 Willkommen bei EmpireHazeClaw!

Hallo {customer.get('name', 'Kunde')},

vielen Dank für deinen Kauf: **{customer.get('product', 'Unknown')}**

Wir melden uns innerhalb von 24 Stunden mit den nächsten Schritten.

Dein Team
EmpireHazeClaw
"""
    
    # Log onboarding trigger
    log(f"📧 Onboarding triggered for {customer.get('email')}", "INFO")
    
    # Create onboarding file for agent to process
    onboarding_file = Path("/home/clawbot/.openclaw/workspace/data/onboarding_pending")
    pending = locked_read(str(onboarding_file), [])
    pending.append({
        "customer": customer,
        "message": onboarding_msg,
        "created": datetime.now().isoformat()
    })
    locked_write(str(onboarding_file), pending)
    
    # TODO: Send welcome email via gog
    # For now, just log it

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default logging
    
    def do_POST(self):
        try:
            # Read body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            # Get signature
            signature = self.headers.get("Stripe-Signature", "")
            
            # Verify
            if not verify_webhook(body, signature):
                log("❌ Invalid webhook signature", "ERROR")
                self.send_response(400)
                self.end_headers()
                return
            
            # Parse event
            try:
                event = json.loads(body.decode())
            except json.JSONDecodeError:
                log("❌ Invalid JSON", "ERROR")
                self.send_response(400)
                self.end_headers()
                return
            
            # Handle by type
            event_type = event.get("type", "")
            
            if event_type == "checkout.session.completed":
                handle_checkout_completed(event)
            elif event_type == "payment_intent.succeeded":
                handle_payment_intent_succeeded(event)
            else:
                log(f"ℹ️ Unhandled event: {event_type}", "INFO")
            
            # Respond
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            
        except Exception as e:
            log(f"💥 Handler error: {e}", "ERROR")
            self.send_response(500)
            self.end_headers()

def main():
    log("="*50)
    log("💳 Stripe Webhook Server starting...")
    log(f"Listening on port {PORT}")
    log("="*50)
    
    # Ensure data files exist
    for f in [CUSTOMERS_FILE, ONBOARD_QUEUE]:
        f.parent.mkdir(parents=True, exist_ok=True)
        if not f.exists():
            locked_write(str(f), [] if "queue" in str(f) or "customers" in str(f) else {})
    
    server = HTTPServer(("0.0.0.0", PORT), WebhookHandler)
    log(f"✅ Server running on http://0.0.0.0:{PORT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()
