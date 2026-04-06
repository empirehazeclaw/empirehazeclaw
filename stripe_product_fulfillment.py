#!/usr/bin/env python3
"""
📦 STRIPE PRODUCT FULFILLMENT v2
===================================
Automatische Lieferung von digitalen Produkten nach Stripe-Kauf.

Flow:
1. Stripe Webhook → checkout.session.completed
2. Produkt-File auswählen (basierend auf metadata oder Preis)
3. ZIP erstellen ODER vorbereitetes ZIP senden
4. Email an Kunde mit Download-Link oder Attachment

Autor: OpenClaw
Datum: 2026-03-26
"""

import sys
import os
import json
import uuid
import smtplib
import zipfile
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify, send_file
from datetime import datetime

app = Flask(__name__)

# ================= CONFIG =================
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_test123")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

# Email Config (Brevo/SMTP)
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp-relay.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "empirehazeclaw@gmail.com")
SMTP_PASS = os.environ.get("SMTP_PASS", "")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "empirehazeclaw@gmail.com")
FROM_NAME = os.environ.get("FROM_NAME", "EmpireHazeClaw")

# Produkt-Konfiguration (PREIS → PRODUKT)
PRODUCTS = {
    "restaurant_ai_starter": {
        "price": 2900,  # Cent: €29
        "name": "Restaurant AI Starter Kit",
        "files_dir": "/home/clawbot/.openclaw/workspace/products/restaurant-ai-starter",
        "zip_name": "Restaurant_AI_Starter_Kit.zip",
        "premade_zip": "/home/clawbot/.openclaw/workspace/products/zips/restaurant-ai-starter-v1.zip",
        "description": "50 Prompts + 10 Scripts + Notion Template + Video Tutorial"
    },
    "automation_scripts_bundle": {
        "price": 4900,  # Cent: €49
        "name": "Automation Scripts Bundle",
        "files_dir": "/home/clawbot/.openclaw/workspace/products/automation-scripts",
        "zip_name": "Automation_Scripts_Bundle.zip",
        "description": "20 Python Scripts für Business Automation"
    },
    "notion_business_template": {
        "price": 1900,  # Cent: €19
        "name": "Notion Business Template Pack",
        "files_dir": "/home/clawbot/.openclaw/workspace/products/notion-templates",
        "zip_name": "Notion_Business_Templates.zip",
        "description": "5 Notion Templates für Business Management"
    }
}

# Fallback Produkteinordnung (wenn keine metadata)
DEFAULT_PRODUCT = "restaurant_ai_starter"

# ================= HELPERS =================
def init_db():
    """Datenbank initialisieren"""
    db_file = "/home/clawbot/.openclaw/workspace/data/fulfillment_db.json"
    os.makedirs(os.path.dirname(db_file), exist_ok=True)
    if not os.path.exists(db_file):
        with open(db_file, 'w') as f:
            json.dump({"sales": [], "pending": []}, f)
    return db_file

def save_sale(sale_data):
    """Verkauf in DB speichern"""
    db_file = init_db()
    with open(db_file, 'r') as f:
        db = json.load(f)
    db["sales"].append(sale_data)
    with open(db_file, 'w') as f:
        json.dump(db, f, indent=2)

def get_product_by_price(amount_cents):
    """Finde Produkt basierend auf Preis"""
    for product_id, product in PRODUCTS.items():
        if product["price"] == amount_cents:
            return product_id, product
    return DEFAULT_PRODUCT, PRODUCTS[DEFAULT_PRODUCT]

def create_zip_from_files(files_dir, zip_path, premade_zip=None):
    """Erstellt ein ZIP aus allen Dateien im Verzeichnis"""
    
    # Use premade zip if available
    if premade_zip and os.path.exists(premade_zip):
        if os.path.exists(zip_path):
            os.remove(zip_path)
        shutil.copy(premade_zip, zip_path)
        print(f"✅ Copied premade ZIP: {zip_path} ({os.path.getsize(zip_path)} bytes)")
        return True
    
    if not os.path.exists(files_dir):
        print(f"⚠️ Files directory not found: {files_dir}")
        return False
    
    # Deletes existing zip if present
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(files_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, files_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Created ZIP: {zip_path} ({os.path.getsize(zip_path)} bytes)")
    return True

def send_product_email(to_email, product_name, zip_path, customer_name=""):
    """Sendet Produkt-Email mit ZIP Attachment"""
    if not SMTP_PASS:
        print(f"⚠️ SMTP_PASS not set - logging instead of sending")
        print(f"📧 EMAIL TO: {to_email}")
        print(f"📦 PRODUCT: {product_name}")
        print(f"📎 ZIP: {zip_path}")
        return True
    
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        msg['Subject'] = f"🎉 Dein {product_name} - Download"

        body = f"""
Hallo {customer_name or "Kunde"}!

Vielen Dank für deinen Kauf! 🎉

Dein Produkt: **{product_name}**

Anleitung:
1. Download unten
2. Entpacken
3. Readme.md lesen
4. Loslegen!

Bei Fragen: empirehazeclaw@gmail.com

Viel Erfolg mit deinem neuen AI Kit!

Beste Grüße,
Nico & das EmpireHazeClaw Team
"""
        msg.attach(MIMEText(body, 'plain'))

        # Attachment
        with open(zip_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {os.path.basename(zip_path)}')
            msg.attach(part)

        # Senden
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ssl_yesno=True
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def send_download_link_email(to_email, product_name, download_url, customer_name=""):
    """Sendet Email mit Download-Link (Fallback)"""
    body = f"""
Hallo {customer_name or "Kunde"}!

Danke für deinen Kauf! 🎉

Dein Produkt: **{product_name}**

Download Link (gültig 24h):
{download_url}

Bei Fragen: empirehazeclaw@gmail.com

Beste Grüße,
Nico & das EmpireHazeClaw Team
"""
    print(f"📧 DOWNLOAD LINK EMAIL TO: {to_email}")
    print(f"🔗 LINK: {download_url}")
    return True

# ================= FLASK ROUTES =================
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Stripe Webhook Handler"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature', '')

    try:
        event = json.loads(payload)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

    print(f"📨 Webhook received: {event.get('type', 'unknown')}")

    # Checkout Session Completed
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        customer_email = session.get('customer_details', {}).get('email', '')
        customer_name = session.get('customer_details', {}).get('name', '')
        amount_total = session.get('amount_total', 0)
        payment_intent = session.get('payment_intent', '')
        
        # Metadaten aus Session
        metadata = session.get('metadata', {})
        product_id = metadata.get('product_id', '')
        
        # Wenn keine metadata, anhand Preis ermitteln
        if not product_id:
            product_id, product = get_product_by_price(amount_total)
        else:
            product = PRODUCTS.get(product_id, PRODUCTS[DEFAULT_PRODUCT])

        print(f"💰 SALE: {customer_email} bought {product['name']} for €{amount_total/100}")

        # ZIP erstellen (oder premade nutzen)
        zip_dir = "/home/clawbot/.openclaw/workspace/products/zips"
        os.makedirs(zip_dir, exist_ok=True)
        zip_path = os.path.join(zip_dir, product['zip_name'])
        premade = product.get('premade_zip')
        
        if create_zip_from_files(product['files_dir'], zip_path, premade):
            # Email senden mit Attachment
            send_product_email(customer_email, product['name'], zip_path, customer_name)
        else:
            # Fallback: Download Link
            download_url = f"https://empirehazeclaw.store/download/{product_id}/{payment_intent}"
            send_download_link_email(customer_email, product['name'], download_url, customer_name)

        # Sale speichern
        sale_data = {
            "email": customer_email,
            "name": customer_name,
            "product": product['name'],
            "product_id": product_id,
            "amount": amount_total,
            "payment_intent": payment_intent,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        }
        save_sale(sale_data)

        return jsonify(success=True, sale=sale_data)

    return jsonify(success=True, message="Event processed")

@app.route('/download/<product_id>/<payment_intent>', methods=['GET'])
def download_file(product_id, payment_intent):
    """Download Endpoint (als Fallback)"""
    if product_id not in PRODUCTS:
        return jsonify(error="Product not found"), 404
    
    product = PRODUCTS[product_id]
    zip_path = f"/home/clawbot/.openclaw/workspace/products/zips/{product['zip_name']}"
    
    if not os.path.exists(zip_path):
        return jsonify(error="File not ready"), 404
    
    return send_file(zip_path, as_attachment=True, download_name=product['zip_name'])

@app.route('/health', methods=['GET'])
def health():
    """Health Check"""
    return jsonify(status="ok", timestamp=datetime.now().isoformat())

# ================= MAIN =================
if __name__ == '__main__':
    init_db()
    
    # Products Verzeichnisse erstellen
    for product_id, product in PRODUCTS.items():
        os.makedirs(product['files_dir'], exist_ok=True)
    
    port = int(os.environ.get("PORT", "5005"))
    print(f"🚀 Fulfillment Server started on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
