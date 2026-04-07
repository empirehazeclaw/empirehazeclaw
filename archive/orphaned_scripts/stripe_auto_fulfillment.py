import sys
import os
import json
import uuid
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Dummy/Test Stripe Webhook Secret (wird spaeter aus ENV geladen)
STRIPE_WEBHOOK_SECRET = "whsec_test123456"

# Unsere "Datenbank" fuer generierte API Keys
DB_FILE = "/home/clawbot/.openclaw/workspace/data/api_keys.json"

def init_db():
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"keys": {}}, f)

def generate_api_key(customer_email, plan):
    """Generiert einen einzigartigen API Key fuer den Kaeufer"""
    new_key = f"ehc_{uuid.uuid4().hex[:24]}"
    
    with open(DB_FILE, 'r') as f:
        db = json.load(f)
        
    db["keys"][new_key] = {
        "email": customer_email,
        "plan": plan,
        "status": "active",
        "requests_used": 0
    }
    
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)
        
    return new_key

def send_delivery_email(email, api_key):
    """Sende die Zugangsdaten via Brevo/SMTP an den Kunden"""
    # Hier wuerde der Brevo-Code stehen (via SMTP). 
    # Fuer den Moment loggen wir es nur.
    log_msg = f"📧 E-MAIL SENT TO: {email} | YOUR API KEY: {api_key}\n"
    with open("/home/clawbot/.openclaw/workspace/logs/fulfillment.log", "a") as f:
        f.write(log_msg)
    print(log_msg)

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')
    
    # In einem ECHTEN Setup wuerden wir hier die Stripe-Signatur pruefen
    # stripe.Webhook.construct_event(...)
    
    try:
        event = json.loads(payload)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    # Pruefen, ob ein Checkout erfolgreich war
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        customer_email = session.get('customer_details', {}).get('email', 'unknown@example.com')
        # In echt wuerden wir hier die line_items abrufen, um das Produkt zu identifizieren.
        # Wir gehen mal vom "Prompt Cache API" aus.
        
        print(f"💰 KAUF ERFOLGREICH: {customer_email}")
        
        # 1. API Key generieren
        new_api_key = generate_api_key(customer_email, "pro_plan")
        
        # 2. Key per E-Mail ausliefern
        send_delivery_email(customer_email, new_api_key)
        
    return jsonify(success=True)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5005)
