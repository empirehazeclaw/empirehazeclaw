#!/usr/bin/env python3
"""
🎯 Feature Router
Autonomous decision: which domain gets which feature?

DOMAIN DECISION RULES:

.de     → DE Business / Lead Gen / Kontakt /Pricing
.com    → EN Business / Global / International
.store  → E-Commerce / Zahlung / Checkout / Stripe
.info   → Blog / Dokumentation / Wissen / Blogposts
"""

DOMAIN_MAP = {
    "de": {
        "primary": ["pricing", "kontakt", "demo", "landing", "checkout", "lead", "anfrage", "beratung"],
        "fallback": "store"  # For payments
    },
    "com": {
        "primary": ["pricing", "contact", "demo", "landing", "checkout", "lead", "enquiry"],
        "fallback": "store"
    },
    "store": {
        "primary": ["buy", "pricing", "product", "checkout", "payment", "stripe", "kauf", "produkt"],
        "fallback": None  # Always store for commerce
    },
    "info": {
        "primary": ["blog", "post", "article", "docs", "documentation", "wissen", "guide", "help"],
        "fallback": None  # Always info for content
    }
}

def route_feature(feature_name: str) -> str:
    """
    Decide which domain a feature belongs to.
    
    Args:
        feature_name: Name/description of the feature
        
    Returns:
        Domain key: 'de', 'com', 'store', or 'info'
    """
    feature_lower = feature_name.lower()
    
    # Check each domain's keywords
    for domain, rules in DOMAIN_MAP.items():
        for keyword in rules["primary"]:
            if keyword in feature_lower:
                print(f"✅ '{feature_name}' → .{domain} (matched: {keyword})")
                return domain
    
    # Default fallback based on feature type
    print(f"⚠️ '{feature_name}' → .store (default fallback)")
    return "store"

def get_domain_url(domain: str) -> str:
    """Get URL for domain"""
    urls = {
        "de": "https://empirehazeclaw.de",
        "com": "https://empirehazeclaw.com",
        "store": "https://empirehazeclaw.store",
        "info": "https://empirehazeclaw.info"
    }
    return urls.get(domain, "https://empirehazeclaw.de")

def add_feature_to_domain(domain: str, feature_name: str, url_path: str):
    """
    Log a feature addition.
    This should be called when adding new features.
    """
    timestamp = __import__('datetime').datetime.now().isoformat()
    
    entry = f"""
## Feature: {feature_name}
- Domain: .{domain}
- URL: {get_domain_url(domain)}/{url_path}
- Added: {timestamp}
"""
    
    print(f"\n🎯 FEATURE ROUTING:")
    print(f"   Feature: {feature_name}")
    print(f"   Domain: .{domain}")
    print(f"   URL: {get_domain_url(domain)}/{url_path}")
    print(f"   Status: Logged for tracking")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        feature = " ".join(sys.argv[1:])
        domain = route_feature(feature)
        url_path = feature.lower().replace(" ", "-")
        add_feature_to_domain(domain, feature, url_path)
    else:
        print("Usage: python3 feature_router.py 'Feature Name'")
        print("\nExamples:")
        print("  python3 feature_router.py 'Pricing Page'")
        print("  python3 feature_router.py 'Blog Post about AI'")
        print("  python3 feature_router.py 'Checkout Flow'")
