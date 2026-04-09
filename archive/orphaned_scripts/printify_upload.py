#!/usr/bin/env python3
"""
Printify API Automation Script
Automatisiert POD Upload zu Printify

Usage:
    python3 printify_upload.py --design "design.png" --title "T-Shirt Design" --price 19.99
"""

import os
import requests
import json
import argparse
from datetime import datetime

# Printify API Configuration
PRINTIFY_API_BASE = "https://api.printify.com/v1"

class PrintifyAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("PRINTIFY_API_KEY")
        if not self.api_key:
            raise ValueError("PRINTIFY_API_KEY not set")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_shops(self):
        """List all shops"""
        response = requests.get(
            f"{PRINTIFY_API_BASE}/shops.json",
            headers=self.headers
        )
        return response.json()
    
    def get_products(self, shop_id):
        """List all products in a shop"""
        response = requests.get(
            f"{PRINTIFY_API_BASE}/shops/{shop_id}/products.json",
            headers=self.headers
        )
        return response.json()
    
    def upload_image(self, shop_id, image_url, filename):
        """Upload an image to Printify"""
        payload = {
            "file_name": filename,
            "url": image_url
        }
        response = requests.post(
            f"{PRINTIFY_API_BASE}/shops/{shop_id}/images.json",
            headers=self.headers,
            json=payload
        )
        return response.json()
    
    def create_product(self, shop_id, product_data):
        """Create a new product"""
        response = requests.post(
            f"{PRINTIFY_API_BASE}/shops/{shop_id}/products.json",
            headers=self.headers,
            json=product_data
        )
        return response.json()
    
    def publish_product(self, shop_id, product_id):
        """Publish a product"""
        response = requests.post(
            f"{PRINTIFY_API_BASE}/shops/{shop_id}/products/{product_id}/publish.json",
            headers=self.headers
        )
        return response.json()


def create_tshirt_product(title, description, price, image_id, shop_id, api):
    """Create a T-Shirt product"""
    
    product_data = {
        "title": title,
        "description": description,
        "price": price,
        "type": "t-shirt",
        "tags": ["AI", "Tech", "Digital"],
        "variants": [
            {
                "id": 1,
                "name": "S / Black",
                "sku": "TSHIRT-S-BLK",
                "price": price,
                "cost": price * 0.6,
                "in_stock": true
            },
            {
                "id": 2,
                "name": "M / Black",
                "sku": "TSHIRT-M-BLK",
                "price": price,
                "cost": price * 0.6,
                "in_stock": true
            },
            {
                "id": 3,
                "name": "L / Black",
                "sku": "TSHIRT-L-BLK",
                "price": price,
                "cost": price * 0.6,
                "in_stock": true
            }
        ],
        "print_areas": [
            {
                "variant_ids": [1, 2, 3],
                "placeholders": [
                    {
                        "position": "front",
                        "images": [
                            {
                                "id": image_id
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    result = api.create_product(shop_id, product_data)
    return result


def main():
    parser = argparse.ArgumentParser(description="Printify POD Automation")
    parser.add_argument("--design", required=True, help="URL or path to design image")
    parser.add_argument("--title", required=True, help="Product title")
    parser.add_argument("--description", help="Product description")
    parser.add_argument("--price", type=float, required=True, help="Product price")
    parser.add_argument("--shop-id", type=int, help="Shop ID (auto-detect if not provided)")
    
    args = parser.parse_args()
    
    # Initialize API
    api = PrintifyAPI()
    
    # Get shops
    shops = api.get_shops()
    if not shops:
        print("❌ No shops found!")
        return
    
    shop_id = args.shop_id or shops[0]["id"]
    print(f"📦 Using shop: {shops[0]['title']} (ID: {shop_id})")
    
    # Upload image
    print(f"📤 Uploading image: {args.design}")
    image_result = api.upload_image(shop_id, args.design, f"{args.title}.png")
    image_id = image_result.get("id")
    
    if not image_id:
        print(f"❌ Image upload failed: {image_result}")
        return
    
    print(f"✅ Image uploaded (ID: {image_id})")
    
    # Create product
    print(f"🏗️ Creating product: {args.title}")
    product = create_tshirt_product(
        title=args.title,
        description=args.description or args.title,
        price=args.price,
        image_id=image_id,
        shop_id=shop_id,
        api=api
    )
    
    product_id = product.get("id")
    if product_id:
        print(f"✅ Product created (ID: {product_id})")
        
        # Publish
        print(f"🚀 Publishing product...")
        publish = api.publish_product(shop_id, product_id)
        print(f"✅ Product published!")
        print(f"🔗 URL: https://printify.com/product/{product_id}")
    else:
        print(f"❌ Product creation failed: {product}")


if __name__ == "__main__":
    main()
