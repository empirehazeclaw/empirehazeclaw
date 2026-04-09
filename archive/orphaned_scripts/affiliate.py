#!/usr/bin/env python3
"""
Affiliate Marketing System
- Track affiliate sales
- Generate affiliate links
- Commission tracking
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
import random
import string

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
AFFILIATES_FILE = WORKSPACE / "data" / "affiliates.json"

def load_affiliates():
    if AFFILIATES_FILE.exists():
        return json.loads(AFFILIATES_FILE.read_text())
    return {"affiliates": {}, "sales": {}}

def save_affiliates(data):
    AFFILIATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    AFFILIATES_FILE.write_text(json.dumps(data, indent=2))

def generate_affiliate_id():
    return 'EH' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def create_affiliate(name, email, platform):
    """Create new affiliate"""
    data = load_affiliates()
    
    aff_id = generate_affiliate_id()
    while aff_id in data["affiliates"]:
        aff_id = generate_affiliate_id()
    
    affiliate = {
        "name": name,
        "email": email,
        "platform": platform,  # twitter, blog, youtube, etc.
        "affiliate_id": aff_id,
        "clicks": 0,
        "conversions": 0,
        "commission": 0,
        "created": datetime.now().isoformat()
    }
    
    data["affiliates"][aff_id] = affiliate
    save_affiliates(data)
    
    return aff_id

def track_click(affiliate_id, landing_page):
    """Track affiliate click"""
    data = load_affiliates()
    
    if affiliate_id in data["affiliates"]:
        data["affiliates"][affiliate_id]["clicks"] += 1
        save_affiliates(data)
        return True
    return False

def track_sale(affiliate_id, product, amount):
    """Track affiliate sale"""
    data = load_affiliates()
    
    if affiliate_id not in data["affiliates"]:
        return False
    
    # Calculate commission (20%)
    commission = round(amount * 0.20, 2)
    
    sale_id = str(uuid.uuid4())
    data["sales"][sale_id] = {
        "affiliate_id": affiliate_id,
        "product": product,
        "amount": amount,
        "commission": commission,
        "status": "pending",
        "created": datetime.now().isoformat()
    }
    
    # Update affiliate stats
    data["affiliates"][affiliate_id]["conversions"] += 1
    data["affiliates"][affiliate_id]["commission"] += commission
    
    save_affiliates(data)
    return sale_id

def get_affiliate_stats(affiliate_id):
    """Get affiliate statistics"""
    data = load_affiliates()
    return data["affiliates"].get(affiliate_id)

# Products and commission rates
PRODUCTS = {
    "chatbot_starter": {"price": 29, "commission": 5},
    "chatbot_pro": {"price": 89, "commission": 18},
    "chatbot_enterprise": {"price": 249, "commission": 50},
    "managed_hosting": {"price": 49, "commission": 10},
    "trading_bot": {"price": 79, "commission": 16},
    "discord_bot": {"price": 79, "commission": 16},
}

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "create":
            name = sys.argv[2] if len(sys.argv) > 2 else "Affiliate"
            email = sys.argv[3] if len(sys.argv) > 3 else "affiliate@example.com"
            platform = sys.argv[4] if len(sys.argv) > 4 else "twitter"
            
            aff_id = create_affiliate(name, email, platform)
            print(f"✅ Affiliate created: {aff_id}")
            print(f"   Link: https://empirehazeclaw.com?ref={aff_id}")
        
        elif cmd == "click":
            aff_id = sys.argv[2]
            page = sys.argv[3] if len(sys.argv) > 3 else "homepage"
            
            if track_click(aff_id, page):
                print(f"✅ Click tracked for {aff_id}")
            else:
                print("❌ Invalid affiliate ID")
        
        elif cmd == "sale":
            aff_id = sys.argv[2]
            product = sys.argv[3] if len(sys.argv) > 3 else "chatbot_starter"
            amount = float(sys.argv[4]) if len(sys.argv) > 4 else PRODUCTS.get(product, {}).get("price", 29)
            
            sale_id = track_sale(aff_id, product, amount)
            if sale_id:
                print(f"✅ Sale tracked! Sale ID: {sale_id}")
            else:
                print("❌ Invalid affiliate ID")
        
        elif cmd == "stats":
            aff_id = sys.argv[2] if len(sys.argv) > 2 else None
            if aff_id:
                stats = get_affiliate_stats(aff_id)
                if stats:
                    print(f"📊 Stats for {aff_id}:")
                    print(f"   Clicks: {stats['clicks']}")
                    print(f"   Conversions: {stats['conversions']}")
                    print(f"   Commission: €{stats['commission']}")
                else:
                    print("Affiliate not found")
            else:
                data = load_affiliates()
                print(f"📊 Total Affiliates: {len(data['affiliates'])}")
                print(f"   Total Sales: {len(data['sales'])}")
        
        elif cmd == "products":
            print("📦 Products:")
            for product, info in PRODUCTS.items():
                print(f"   {product}: €{info['price']} -> €{info['commission']} commission")
    else:
        print("Affiliate Marketing CLI")
        print("Usage: affiliate.py [create|click|sale|stats|products]")
