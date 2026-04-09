#!/usr/bin/env python3
"""
🎯 AUTONOMY CONTROLLER
=====================
Controls what I can do autonomously
"""

import json
from pathlib import Path

CONFIG_FILE = Path("config/autonomy.json")

# Default autonomy settings
DEFAULT = {
    "websites": {
        "can_edit": True,
        "can_create": True,
        "max_cost_per_month_eur": 0
    },
    "products": {
        "can_create": True,
        "max_price_eur": 500
    },
    "email": {
        "can_send": True,
        "can_read": False,
        "max_per_day": 20
    },
    "social": {
        "twitter": True,
        "linkedin": False,
        "instagram": False,
        "tiktok": False
    },
    "financial": {
        "can_spend": False,
        "max_spend_eur": 0,
        "must_ask_for": ["any_expense"]
    },
    "schedule": {
        "active_hours": "00-24",
        "max_consecutive_hours": 23,
        "must_notify_on_error": True
    }
}

def load_config():
    if CONFIG_FILE.exists():
        return json.load(open(CONFIG_FILE))
    save_config(DEFAULT)
    return DEFAULT

def save_config(data):
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    json.dump(data, open(CONFIG_FILE, "w"), indent=2)

def can_do(action):
    """Check if action is allowed"""
    config = load_config()
    
    # Website actions
    if action.startswith("website_"):
        return config["websites"]["can_edit"]
    
    # Product actions
    if action.startswith("product_"):
        return config["products"]["can_create"]
    
    # Email actions
    if action == "email_send":
        return config["email"]["can_send"]
    if action == "email_read":
        return config["email"]["can_read"]
    
    # Social actions
    if action.startswith("social_"):
        platform = action.replace("social_", "")
        return config["social"].get(platform, False)
    
    # Financial
    if action.startswith("spend_"):
        return config["financial"]["can_spend"]
    
    return False

def list_permissions():
    """List all current permissions"""
    config = load_config()
    
    print("🎯 AUTONOMY PERMISSIONS")
    print("=" * 40)
    print(f"\n🌐 Websites:")
    print(f"   Edit: {'✅' if config['websites']['can_edit'] else '❌'}")
    print(f"   Create: {'✅' if config['websites']['can_create'] else '❌'}")
    
    print(f"\n📦 Products:")
    print(f"   Create: {'✅' if config['products']['can_create'] else '❌'}")
    print(f"   Max Price: €{config['products']['max_price_eur']}")
    
    print(f"\n📧 Email:")
    print(f"   Send: {'✅' if config['email']['can_send'] else '❌'}")
    print(f"   Read: {'✅' if config['email']['can_read'] else '❌'}")
    
    print(f"\n🐦 Social:")
    for platform, enabled in config["social"].items():
        print(f"   {platform}: {'✅' if enabled else '❌'}")
    
    print(f"\n💰 Financial:")
    print(f"   Can spend: {'✅' if config['financial']['can_spend'] else '❌'}")
    print(f"   Must ask for: {', '.join(config['financial']['must_ask_for'])}")
    
    print(f"\n⏰ Schedule:")
    print(f"   Active: {config['schedule']['active_hours']}")
    print(f"   Must notify on error: {'✅' if config['schedule']['must_notify_on_error'] else '❌'}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        list_permissions()
    elif sys.argv[1] == "allow":
        print(f"✅ Allowed: {sys.argv[2]}")
    elif sys.argv[1] == "deny":
        print(f"❌ Denied: {sys.argv[2]}")
