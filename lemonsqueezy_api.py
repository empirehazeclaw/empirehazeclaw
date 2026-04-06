#!/usr/bin/env python3
"""
🍋 LEMONSQUEEZY INTEGRATION
============================
Automatisiere Verkäufe auf LemonSqueezy.

API Docs: https://docs.lemonsqueezy.com/api
"""

import requests
import json
import os
from datetime import datetime

class LemonSqueezyClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("LEMON_API_KEY", "")
        self.base_url = "https://api.lemonsqueezy.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json",
            "Content-Type": "application/vnd.api+json"
        }
    
    def test_connection(self):
        """Test API connection"""
        if not self.api_key:
            return {"status": "no_token", "message": "LEMON_API_KEY not set"}
        
        try:
            # Add Accept header for Lemonsqueezy
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/vnd.api+json"
            }
            r = requests.get(f"{self.base_url}/stores", headers=headers, timeout=10)
            if r.status_code == 200:
                return {"status": "ok", "data": r.json()}
            else:
                return {"status": "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_products(self):
        """List all products"""
        if not self.api_key:
            return {"error": "No API key"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json"
        }
        try:
            r = requests.get(f"{self.base_url}/products", headers=headers)
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def create_product(self, name, price_eur, description=""):
        """Create a new product"""
        if not self.api_key:
            return {"error": "No API key"}
        
        # First need to get store ID
        stores = self.list_stores()
        if "error" in stores:
            return stores
        
        store_id = stores["data"][0]["id"] if stores.get("data") else None
        if not store_id:
            return {"error": "No store found"}
        
        data = {
            "data": {
                "type": "products",
                "attributes": {
                    "name": name,
                    "description": description,
                    "price": int(price_eur * 100),  # cents
                    "currency": "eur"
                },
                "relationships": {
                    "store": {"data": {"type": "stores", "id": store_id}}
                }
            }
        }
        
        try:
            r = requests.post(f"{self.base_url}/products", headers=self.headers, json=data)
            return r.json() if r.status_code in [200, 201] else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def list_stores(self):
        """List stores"""
        if not self.api_key:
            return {"error": "No API key"}
        
        try:
            r = requests.get(f"{self.base_url}/stores", headers=self.headers)
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_orders(self, limit=50):
        """Get recent orders"""
        if not self.api_key:
            return {"error": "No API key"}
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/vnd.api+json"
        }
        try:
            r = requests.get(
                f"{self.base_url}/orders",
                headers=headers,
                params={"page[size]": limit}
            )
            return r.json() if r.status_code == 200 else {"error": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def get_earnings(self):
        """Calculate earnings from orders"""
        orders = self.get_orders(limit=100)
        
        if "error" in orders:
            return orders
        
        total = 0
        for order in orders.get("data", []):
            total += order["attributes"]["total"]  # in cents
        
        return {
            "total_earnings": total / 100,  # convert to euros
            "currency": "EUR",
            "order_count": len(orders.get("data", []))
        }


# CLI
if __name__ == "__main__":
    import sys
    
    client = LemonSqueezyClient()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 lemonsqueezy.py test       - Test connection")
        print("  python3 lemonsqueezy.py stores     - List stores")
        print("  python3 lemonsqueezy.py products   - List products")
        print("  python3 lemonsqueezy.py orders      - Get orders")
        print("  python3 lemonsqueezy.py earnings   - Get earnings")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "test":
        print(json.dumps(client.test_connection(), indent=2))
    elif cmd == "stores":
        print(json.dumps(client.list_stores(), indent=2))
    elif cmd == "products":
        print(json.dumps(client.list_products(), indent=2))
    elif cmd == "orders":
        print(json.dumps(client.get_orders(), indent=2))
    elif cmd == "earnings":
        print(json.dumps(client.get_earnings(), indent=2))
    else:
        print(f"Unknown command: {cmd}")
