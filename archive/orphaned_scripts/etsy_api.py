#!/usr/bin/env python3
"""
🛍️ ETSY API V3 INTEGRATION
==========================
Official Etsy Open API v3 for Digital Products
"""

import os
import requests
import json
from datetime import datetime

class EtsyAPI:
    def __init__(self, api_key=None):
        # Get from environment or ask user
        self.api_key = api_key or os.environ.get("ETSY_API_KEY", "")
        self.base_url = "https://openapi.etsy.com/v3"
        self.shop_id = os.environ.get("ETSY_SHOP_ID", "")
        
    def set_credentials(self, api_key, shop_id):
        self.api_key = api_key
        self.shop_id = shop_id
        
    def make_request(self, method, endpoint, data=None):
        """Make API request to Etsy"""
        
        if not self.api_key:
            return {"error": "API Key required"}
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        if method == "GET":
            r = requests.get(url, headers=headers)
        elif method == "POST":
            r = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            r = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers)
        
        if r.status_code in [200, 201]:
            return r.json() if r.content else {"status": "ok"}
        else:
            return {"error": r.text, "status_code": r.status_code}
    
    def get_shop(self):
        """Get shop info"""
        return self.make_request("GET", f"/application/shops/{self.shop_id}")
    
    def create_listing(self, title, description, price, tags, images=None):
        """Create a new listing (draft)"""
        
        listing_data = {
            "title": title[:140],
            "description": description[:5000],
            "price": price,
            "currency_code": "EUR",
            "quantity": 1,
            "is_digital": True,
            "state": "draft",
            "tags": tags[:13]  # Max 13 tags
        }
        
        return self.make_request(
            "POST", 
            f"/application/shops/{self.shop_id}/listings",
            listing_data
        )
    
    def upload_image(self, listing_id, image_url):
        """Upload image to listing"""
        # Would need actual image upload
        return {"status": "would_upload", "listing_id": listing_id}
    
    def publish_listing(self, listing_id):
        """Publish a draft listing"""
        return self.make_request(
            "POST",
            f"/application/shops/{self.shop_id}/listings/{listing_id}/publish"
        )


def setup_etsy(api_key, shop_id):
    """Setup Etsy with credentials"""
    api = EtsyAPI()
    api.set_credentials(api_key, shop_id)
    
    # Test connection
    shop = api.get_shop()
    
    return api, shop


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 2:
        api_key = sys.argv[1]
        shop_id = sys.argv[2]
        
        api, shop = setup_etsy(api_key, shop_id)
        
        if "error" in shop:
            print(f"❌ Error: {shop['error']}")
        else:
            print(f"✅ Connected to Etsy!")
            print(f"   Shop: {shop.get('shop_name')}")
    else:
        print("Usage: python3 etsy_api.py <API_KEY> <SHOP_ID>")
