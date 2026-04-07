#!/usr/bin/env python3
"""
Referral Program System
- Track referrals
- Generate referral codes
- Calculate commissions
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
import random
import string

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
REFERRALS_FILE = WORKSPACE / "data" / "referrals.json"

def load_referrals():
    if REFERRALS_FILE.exists():
        return json.loads(REFERRALS_FILE.read_text())
    return {"referrers": {}, "referred": {}}

def save_referrals(data):
    REFERRALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    REFERRALS_FILE.write_text(json.dumps(data, indent=2))

def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_referrer(name, email):
    """Create a new referrer"""
    data = load_referrals()
    
    code = generate_code()
    while code in data["referrers"]:
        code = generate_code()
    
    referrer = {
        "name": name,
        "email": email,
        "code": code,
        "referrals_count": 0,
        "commission_earned": 0,
        "created": datetime.now().isoformat()
    }
    
    data["referrers"][code] = referrer
    save_referrals(data)
    
    return code

def track_referral(referrer_code, referred_email, product):
    """Track a new referral"""
    data = load_referrals()
    
    if referrer_code not in data["referrers"]:
        return False
    
    # Add referral
    referral_id = str(uuid.uuid4())
    data["referred"][referral_id] = {
        "referrer_code": referrer_code,
        "email": referred_email,
        "product": product,
        "status": "pending",
        "commission": 0,
        "created": datetime.now().isoformat()
    }
    
    # Update referrer
    data["referrers"][referrer_code]["referrals_count"] += 1
    
    save_referrals(data)
    return True

def complete_referral(referral_id, commission):
    """Mark referral as completed and add commission"""
    data = load_referrals()
    
    if referral_id not in data["referred"]:
        return False
    
    ref = data["referred"][referral_id]
    ref["status"] = "completed"
    ref["commission"] = commission
    
    # Add commission to referrer
    data["referrers"][ref["referrer_code"]]["commission_earned"] += commission
    
    save_referrals(data)
    return True

def get_referrer_stats(code):
    """Get referrer statistics"""
    data = load_referrals()
    
    if code not in data["referrers"]:
        return None
    
    return data["referrers"][code]

# Referral rewards
REFERRAL_REWARDS = {
    "chatbot_starter": 15,
    "chatbot_pro": 30,
    "managed_hosting": 25,
    "trading_bot": 40,
    "discord_bot": 25
}

# CLI
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "create":
            name = sys.argv[2] if len(sys.argv) > 2 else "Referrer"
            email = sys.argv[3] if len(sys.argv) > 3 else "referrer@example.com"
            code = create_referrer(name, email)
            print(f"✅ Referral code created: {code}")
        
        elif cmd == "track":
            code = sys.argv[2]
            email = sys.argv[3] if len(sys.argv) > 3 else "new@example.com"
            product = sys.argv[4] if len(sys.argv) > 4 else "chatbot_starter"
            
            if track_referral(code, email, product):
                print(f"✅ Referral tracked: {email} -> {product}")
            else:
                print("❌ Invalid referral code")
        
        elif cmd == "stats":
            code = sys.argv[2] if len(sys.argv) > 2 else None
            if code:
                stats = get_referrer_stats(code)
                if stats:
                    print(f"📊 Stats for {code}:")
                    print(f"   Referrals: {stats['referrals_count']}")
                    print(f"   Commission: €{stats['commission_earned']}")
                else:
                    print("Code not found")
            else:
                data = load_referrals()
                print(f"📊 Total Referrers: {len(data['referrers'])}")
                print(f"   Total Referrals: {len(data['referred'])}")
        
        elif cmd == "rewards":
            print("🎁 Referral Rewards:")
            for product, reward in REFERRAL_REWARDS.items():
                print(f"   {product}: €{reward}")
    else:
        print("Referral Program CLI")
        print("Usage: referral.py [create|track|stats|rewards]")
