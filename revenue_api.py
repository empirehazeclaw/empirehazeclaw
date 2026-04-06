import os
#!/usr/bin/env python3
"""
💰 REVENUE API - ENHANCED
=========================
Combines all revenue sources: Stripe, LemonSqueezy, PayPal, Etsy, Printify
"""

import json
import os
import requests
from datetime import datetime, timedelta

# === STRIPE ===
def get_stripe_revenue():
    try:
        stripe_key = "export STRIPE_SECRET_KEY"
        
        r = requests.get("https://api.stripe.com/v1/balance", auth=(stripe_key, ""))
        
        if r.status_code != 200:
            return 0
        
        data = r.json()
        available = data.get("available", [{}])[0].get("amount", 0)
        pending = data.get("pending", [{}])[0].get("amount", 0)
        
        return (available + pending) / 100
    except:
        return 0

# === LEMONSQUEEZY ===
def get_lemon_revenue():
    try:
        config_path = "/home/clawbot/.openclaw/workspace/config/lemon.json"
        if not os.path.exists(config_path):
            return 0
        
        with open(config_path) as f:
            config = json.load(f)
        
        token = config.get("api_key", "")
        if not token:
            return 0
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.api+json"
        }
        
        r = requests.get("https://api.lemonsqueezy.com/v1/orders", headers=headers, params={"page[size]": 100})
        
        if r.status_code != 200:
            return 0
        
        total = 0
        for order in r.json().get("data", []):
            total += order.get("attributes", {}).get("total", 0)
        
        return total / 100
    except:
        return 0

# === PAYPAL ===
def get_paypal_revenue():
    try:
        config_path = "/home/clawbot/.openclaw/workspace/config/paypal.json"
        if not os.path.exists(config_path):
            return 0
        
        with open(config_path) as f:
            config = json.load(f)
        
        client_id = config.get("client_id", "")
        client_secret = config.get("client_secret", "")
        
        if not client_id or not client_secret:
            return 0
        
        # Get token
        auth = (client_id, client_secret)
        data = {"grant_type": "client_credentials"}
        
        r = requests.post("https://api-m.paypal.com/v1/oauth2/token", auth=auth, data=data)
        
        if r.status_code != 200:
            return 0
        
        token = r.json().get("access_token")
        
        # Get transactions
        headers = {"Authorization": f"Bearer {token}"}
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        r2 = requests.get(
            "https://api-m.paypal.com/v1/reporting/transactions",
            headers=headers,
            params={"start_date": start_date, "page_size": 100}
        )
        
        if r2.status_code != 200:
            return 0
        
        total = 0
        for txn in r2.json().get("transaction_details", []):
            gross = txn.get("amount_with_breakdown", {}).get("gross_amount", {})
            if gross.get("currency_code") == "EUR":
                total += float(gross.get("value", 0))
        
        return total
    except Exception as e:
        print(f"PayPal error: {e}")
        return 0

# === MANUAL ENTRIES ===
def get_manual_revenue():
    """Get manually entered revenue"""
    try:
        path = "/home/clawbot/.openclaw/workspace/config/manual_revenue.json"
        if not os.path.exists(path):
            return {}
        
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def save_manual_revenue(source, amount, description=""):
    """Save manual revenue entry"""
    try:
        path = "/home/clawbot/.openclaw/workspace/config/manual_revenue.json"
        
        data = {}
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
        
        if "entries" not in data:
            data["entries"] = []
        
        data["entries"].append({
            "source": source,
            "amount": amount,
            "description": description,
            "date": datetime.now().isoformat()
        })
        
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        return True
    except:
        return False

# === COMBINED ===
def get_all_revenue():
    """Get combined revenue from all sources"""
    
    stripe = get_stripe_revenue()
    lemon = get_lemon_revenue()
    paypal = get_paypal_revenue()
    manual = get_manual_revenue()
    
    manual_total = sum(e.get("amount", 0) for e in manual.get("entries", []))
    
    total = stripe + lemon + paypal + manual_total
    
    return {
        "total": round(total, 2),
        "monthly": round(total, 2),
        "daily": 0,
        "transactions": 0,
        "sources": {
            "stripe": round(stripe, 2),
            "lemon": round(lemon, 2),
            "paypal": round(paypal, 2),
            "etsy": 0,
            "printify": 0,
            "manual": round(manual_total, 2)
        },
        "manual_entries": manual.get("entries", []),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("Content-Type: application/json")
    print()
    print(json.dumps(get_all_revenue(), indent=2))
