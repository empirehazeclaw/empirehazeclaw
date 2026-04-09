import requests
import json

STRIPE_KEY = "export STRIPE_SECRET_KEY"
HEADERS = {
    "Authorization": f"Bearer {STRIPE_KEY}",
    "Content-Type": "application/x-www-form-urlencoded"
}

def create_payment_link():
    try:
        # 1. Create Product (Premium Plan)
        prod_resp = requests.post("https://api.stripe.com/v1/products", headers=HEADERS, data={
            "name": "Managed AI Premium (All-Inclusive)",
            "description": "Das Rundum-Sorglos-Paket. Wir stellen Server (DE), Agenten UND die LLM-Schnittstelle. Kein API-Key-Chaos. Einfach buchen und loslegen. (Inkl. 1:1 Setup-Call)"
        })
        product_id = prod_resp.json()["id"]

        # 2. Create Price (149.00 EUR Einmalige Setup-Gebühr)
        price_resp = requests.post("https://api.stripe.com/v1/prices", headers=HEADERS, data={
            "product": product_id,
            "unit_amount": 14900,
            "currency": "eur"
        })
        price_id = price_resp.json()["id"]

        # 3. Create Payment Link
        pl_resp = requests.post("https://api.stripe.com/v1/payment_links", headers=HEADERS, data={
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1
        })
        return pl_resp.json()["url"]
    except Exception as e:
        return None

if __name__ == "__main__":
    url = create_payment_link()
    print(f"STRIPE_LINK_PREMIUM={url}")
