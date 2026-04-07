#!/usr/bin/env python3
"""
🛒 GUMROAD INTEGRATION
=======================
Automatisiere Verkäufe auf Gumroad.

API Docs: https://app.gumroad.com/api
"""

import requests
import json
import os
from datetime import datetime

class GumroadClient:
    def __init__(self, access_token=None):
        # Load from env or use placeholder
        self.access_token = access_token or os.environ.get("GUMROAD_TOKEN", "")
        self.base_url = "https://api.gumroad.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def test_connection(self):
        """Test if API works"""
        if not self.access_token:
            return {"status": "no_token", "message": "GUMROAD_TOKEN not set"}
        
        try:
            r = requests.get(f"{self.base_url}/user", headers=self.headers, timeout=10)
            if r.status_code == 200:
                return {"status": "ok", "data": r.json()}
            else:
                return {"status": "error", "code": r.status_code, "message": r.text}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_products(self):
        """List all products"""
        if not self.access_token:
            return {"error": "No token"}
        
        try:
            r = requests.get(f"{self.base_url}/products", headers=self.headers)
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def create_product(self, name, price, description="", url=None):
        """Create a new digital product"""
        if not self.access_token:
            return {"error": "No token"}
        
        data = {
            "name": name,
            "price": price,  # in cents
            "description": description
        }
        
        if url:
            data["url"] = url  # Download URL for digital product
        
        try:
            r = requests.post(
                f"{self.base_url}/products",
                headers=self.headers,
                json=data
            )
            return r.json() if r.status_code in [200, 201] else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_sales(self, limit=50):
        """Get recent sales"""
        if not self.access_token:
            return {"error": "No token"}
        
        try:
            r = requests.get(
                f"{self.base_url}/sales",
                headers=self.headers,
                params={"limit": limit}
            )
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_earnings(self):
        """Get earnings summary"""
        if not self.access_token:
            return {"error": "No token"}
        
        try:
            r = requests.get(f"{self.base_url}/earnings", headers=self.headers)
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}


def upload_product(name, price_eur, description, file_path=None):
    """Quick product upload"""
    client = GumroadClient()
    
    # Convert EUR to cents
    price_cents = int(price_eur * 100)
    
    result = client.create_product(
        name=name,
        price=price_cents,
        description=description,
        url=file_path
    )
    
    return result


# CLI
if __name__ == "__main__":
    import sys
    
    client = GumroadClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 gumroad.py test           - Test connection")
        print("  python3 gumroad.py products       - List products")
        print("  python3 gumroad.py sales          - Get sales")
        print("  python3 gumroad.py earnings       - Get earnings")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        print(json.dumps(client.test_connection(), indent=2))
    elif cmd == "products":
        print(json.dumps(client.list_products(), indent=2))
    elif cmd == "sales":
        print(json.dumps(client.get_sales(), indent=2))
    elif cmd == "earnings":
        print(json.dumps(client.get_earnings(), indent=2))
    else:
        print(f"Unknown command: {cmd}")
