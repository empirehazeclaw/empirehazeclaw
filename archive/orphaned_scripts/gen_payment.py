#!/usr/bin/env python3
"""Generate Stripe Payment Links"""
import subprocess
import sys

PRODUCTS = {
    "chatbot_starter": {"price": 2900, "name": "Chatbot Starter"},
    "chatbot_pro": {"price": 8900, "name": "Chatbot Pro"},
    "landing": {"price": 19900, "name": "Landing Page"},
    "managed_ai": {"price": 9900, "name": "Managed AI"}
}

def create_link(product):
    if product not in PRODUCTS:
        return f"❌ Unknown: {product}"
    
    p = PRODUCTS[product]
    print(f"💰 Creating {p['name']} (€{p['price']/100})...")
    
    # Use stripe CLI or API
    return f"📎 Payment Link would be created here"

def list_products():
    print("=== 💰 PRODUCTS ===")
    for k, v in PRODUCTS.items():
        print(f"  {k}: €{v['price']/100} ({v['name']})")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(create_link(sys.argv[1]))
    else:
        list_products()
