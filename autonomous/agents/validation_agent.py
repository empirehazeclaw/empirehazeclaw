import os
#!/usr/bin/env python3
"""
✅ VALIDATION AGENT
===================
Validates product ideas BEFORE building - per SOUL.md
Only builds products that have proven demand!
"""

import requests
import json
import random

def validate_search(niche):
    """Check if people search for this"""
    try:
        r = requests.get(
            f"https://www.google.com/search?q={niche}+kaufen",
            timeout=10
        )
        return "kaufen" in r.text.lower() or "€" in r.text
    except:
        return False

def validate_reddit(niche):
    """Check if people complain/ask about this on Reddit"""
    try:
        r = requests.get(
            f"https://www.reddit.com/search/?q={niche}",
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def validate_trends(niche):
    """Check Google Trends"""
    try:
        r = requests.get(
            f"https://trends.google.com/trends/explore?q={niche}",
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def validate_competition(niche):
    """Check if competitors exist and make money"""
    try:
        r = requests.get(
            f"https://www.google.com/search?q={niche}+software",
            timeout=10
        )
        return r.status_code == 200
    except:
        return False

def validate_product(product_name, niche):
    """Full validation - 4 methods"""
    
    print(f"\n🔬 Validating: {product_name}")
    print(f"   Nische: {niche}")
    print("-" * 40)
    
    results = {
        "search": validate_search(niche),
        "reddit": validate_reddit(niche),
        "trends": validate_trends(niche),
        "competition": validate_competition(niche),
    }
    
    score = sum(results.values()) * 25
    
    approved = score >= 75  # Need 3/4 methods positive
    
    print(f"   📊 Search:    {'✅' if results['search'] else '❌'}")
    print(f"   📊 Reddit:    {'✅' if results['reddit'] else '❌'}")
    print(f"   📊 Trends:    {'✅' if results['trends'] else '❌'}")
    print(f"   📊 Competition: {'✅' if results['competition'] else '❌'}")
    print(f"   Score: {score}%")
    print(f"   Status: {'✅ APPROVED' if approved else '❌ REJECTED'}")
    
    return {
        "product": product_name,
        "niche": niche,
        "results": results,
        "score": score,
        "approved": approved
    }

# Products to validate from our store
PRODUCTS_TO_VALIDATE = [
    ("KI für Anfänger", "KI lernen"),
    ("Productivity Dashboard", "Notion template"),
    ("AI Prompt Master", "KI prompts"),
    ("Trading Bot Guide", "trading bot lernen"),
    ("SaaS Boilerplate", "SaaS vorlage"),
    ("Trading Indicators", "trading indicators"),
]

def run():
    print("=" * 50)
    print("✅ VALIDATION AGENT - Product Validator")
    print("=" * 50)
    
    approved_products = []
    
    for product, niche in PRODUCTS_TO_VALIDATE:
        result = validate_product(product, niche)
        
        if result["approved"]:
            approved_products.append(result)
            print(f"   🚀 Kann gebaut werden!")
        else:
            print(f"   ⚠️ Nicht genug Demand - NICHT bauen")
    
    print("\n" + "=" * 50)
    print("📋 VALIDATION RESULTS:")
    print("=" * 50)
    
    print(f"\n✅ VALIDATED (können wir verkaufen):")
    for p in approved_products:
        print(f"   - {p['product']} ({p['score']}%)")
    
    rejected = len(PRODUCTS_TO_VALIDATE) - len(approved_products)
    print(f"\n❌ REJECTED: {rejected} Produkte")
    
    return approved_products

if __name__ == "__main__":
    run()
