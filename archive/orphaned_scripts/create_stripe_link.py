import requests
import json
import sys

STRIPE_KEY = "export STRIPE_SECRET_KEY"
HEADERS = {
    "Authorization": f"Bearer {STRIPE_KEY}",
    "Content-Type": "application/x-www-form-urlencoded"
}

def create_subscription_link():
    try:
        # 1. Create Product
        print("Creating product...")
        prod_resp = requests.post("https://api.stripe.com/v1/products", headers=HEADERS, data={
            "name": "Prompt Cache API Pro Plan",
            "description": "Unlimitierte Cache Requests, 24h TTL, Semantisches Caching, Priority Support"
        })
        prod_data = prod_resp.json()
        if "id" not in prod_data:
            print(f"Error creating product: {prod_data}")
            return None
        product_id = prod_data["id"]

        # 2. Create Price (29.00 EUR / month)
        print("Creating price...")
        price_resp = requests.post("https://api.stripe.com/v1/prices", headers=HEADERS, data={
            "product": product_id,
            "unit_amount": 2900,
            "currency": "eur",
            "recurring[interval]": "month"
        })
        price_data = price_resp.json()
        if "id" not in price_data:
            print(f"Error creating price: {price_data}")
            return None
        price_id = price_data["id"]

        # 3. Create Payment Link
        print("Creating payment link...")
        pl_resp = requests.post("https://api.stripe.com/v1/payment_links", headers=HEADERS, data={
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": 1
        })
        pl_data = pl_resp.json()
        if "url" not in pl_data:
            print(f"Error creating payment link: {pl_data}")
            return None
        
        return pl_data["url"]
    except Exception as e:
        print(f"Exception: {e}")
        return None

if __name__ == "__main__":
    url = create_subscription_link()
    if url:
        print(f"SUCCESS_URL={url}")
    else:
        print("FAILED")
