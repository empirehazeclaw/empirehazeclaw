#!/usr/bin/env python3
"""
Printify Design Uploader
Automatically uploads designs and creates products on Etsy
"""

import os
import json
import requests
import time
from pathlib import Path

# Config
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6ImY3NTBhMTM4YjkyOGZlYzI4ZDgyZmRjMTBmOGY4NjRjN2FlYTExYzk0OTQyN2QwNTgyOTBjZGM5OWRjYjdjN2QxMzdlMDQ3NmU2MDQ5NTYyIiwiaWF0IjoxNzcyNzI4MTUzLjExNDk4NCwibmJmIjoxNzcyNzI4MTUzLjExNDk4OCwiZXhwIjoxODA0MjY0MTUzLjA5ODkwMiwic3ViIjoiMjY1NTA1OTIiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIiwidXNlci5pbmZvIl19.BItsrxyr7oFfzbB5MyOkwesUH8h-HjAY_DuCcJrWZTji-frYNHa9y4HPz-KgcltA7CtMzjkkYz0km5FMudpAA5Xy1AZfWDgWNNLK5GPkoBLqtWlnfho_xfbXEBQL-oQgSfYtqhSzyYGylakkClKk2ofb8YEhn-zIFWgY0t7NyxeXi6LPcBFTelama_WyiNkBCisQZ8xT7kxqHQkMFrpKybd1bxfRR7mPAOgobfuo4oc3D_0FHTNmv40K9Nnb6EaojyRfo91Dj7o04hIxS_GT64q9gAV7Ui7bFHHDQXmqZKNb7uQZykk9eQjDjJ4-BYykw98DZhnl5dV0rg7UEegXdN-IflOUJvkAJ27EapnX8ldJKLliMDUE3s5oQBVt2ETyB6vTeGCpr6m3RBq05TvEaWymLduLDTc3yDGDRrJzfTHPG4Lz72A054hn9dkhlwu9Zce33jp_qrVyZC2VufWwPVgDY8M6tIJ60eIdC5G9PSVOaJgOsmwLRn9jWqc42VvyzDBWBc2pNgT5uUvpC9EaEG6JdlNyE8J8yJ2BQCwIkVEk7YZ-UeOtjcTWeCwHvYymRF9FeKyn2HscFWZbDt7eJwq4UR_jvtHwGBf4SZ29KmZK7iQCZtywGyLkImEUlET6DZ1Du3W7ZagRMjbMNrkXbvrrsJIwNd12eTbuD6f8mmc"
SHOP_ID = "26693517"
DESIGNS_DIR = "/home/clawbot/.openclaw/workspace/knowledge/pod_designs_upscaled"

# API Headers
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Popular blueprints for POD
BLUEPRINTS = {
    "tee": 5,           # Unisex Cotton Crew Tee
    "hoodie": 12,       # Unisex Hoodie
    "tank": 10,         # Women's Flowy Racerback Tank
    "sweatshirt": 71,   # Unisex Sweatshirt
    "poster": 386,       # Poster
    "mug": 15,          # Ceramic Mug
    "tote": 17,         # Canvas Tote Bag
}

class PrintifyUploader:
    def __init__(self):
        self.base_url = "https://api.printify.com/v1"
    
    def upload_image(self, image_path, title):
        """Upload an image to Printify"""
        url = f"{self.base_url}/uploads.json"
        
        with open(image_path, 'rb') as f:
            files = {
                'file': (os.path.basename(image_path), f, 'image/jpeg')
            }
            data = {
                'title': title,
                'is_visible': True
            }
            
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {API_KEY}"},
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error uploading {title}: {response.text}")
            return None
    
    def create_product(self, blueprint_id, image_id, title, description, price):
        """Create a product on Printify"""
        url = f"{self.base_url}/shops/{SHOP_ID}/products.json"
        
        payload = {
            "title": title,
            "description": description,
            "blueprint_id": blueprint_id,
            "print_provider_id": 1,  # Default provider
            "images": [
                {
                    "id": image_id,
                    "position": "front"
                }
            ],
            "variants": [
                {
                    "blueprint_id": blueprint_id,
                    "print_provider_id": 1,
                    "price": price
                }
            ]
        }
        
        response = requests.post(
            url,
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error creating product: {response.text}")
            return None
    
    def publish_product(self, product_id):
        """Publish a product to Etsy"""
        url = f"{self.base_url}/shops/{SHOP_ID}/products/{product_id}/publish.json"
        
        response = requests.post(url, headers=HEADERS)
        return response.json() if response.status_code == 200 else None


def main():
    uploader = PrintifyUploader()
    
    # Get all designs
    designs = list(Path(DESIGNS_DIR).glob("*.jpg"))
    print(f"Found {len(designs)} designs")
    
    # Upload each design
    for design in designs[:10]:  # First 10
        print(f"\n📤 Uploading: {design.name}")
        
        # Upload image
        result = uploader.upload_image(str(design), design.stem)
        
        if result:
            image_id = result['id']
            print(f"   ✅ Uploaded (ID: {image_id})")
            
            # Create product (T-Shirt)
            title = f"EmpireHazeClaw - {design.stem.replace('_', ' ').title()}"
            description = f"High-quality print on demand t-shirt. Made with love in Germany 🇩🇪"
            
            product = uploader.create_product(
                BLUEPRINTS['tee'],
                image_id,
                title,
                description,
                2499  # €24.99
            )
            
            if product:
                print(f"   ✅ Product created!")
                print(f"   🔗 {product.get('url', 'N/A')}")
    
    print("\n✅ Done!")


if __name__ == "__main__":
    main()
