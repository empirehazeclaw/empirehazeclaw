#!/usr/bin/env python3
"""
Printify Auto-Uploader
Automatically uploads designs and creates products on Etsy

Usage:
    python3 scripts/printify_auto_upload.py --test
    python3 scripts/printify_auto_upload.py --designs 5
    python3 scripts/printify_auto_upload.py --all
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Configuration - UPDATE THESE
CONFIG = {
    "api_key": "",  # Set via environment or config
    "shop_id": "26693517",
    "blueprint_id": 5,  # Unisex Cotton Crew Tee
    "print_provider_id": 41,
    "price_eur": 24.99,
    "designs_dir": "/home/clawbot/.openclaw/workspace/knowledge/pod_designs_upscaled"
}

# Product descriptions by niche
DESCRIPTIONS = {
    "pet": """🐕 Willkommen bei EmpireHazeClaw! 🐈

Premium Print-on-Demand T-Shirts für Tierliebhaber!

✓ 100% Baumwolle (Bio-Qualität)
✓ Hochwertiger Digitaldruck
✓ Deutsche Fertigung 🇩🇪
✓ Versand innerhalb 2-5 Werktagen

Perfekt als Geschenk für Hunde-Mamas, Katzen-Väter und alle Tierfreunde!
""",
    
    "gaming": """🎮 Willkommen bei EmpireHazeClaw!

Premium Gaming-Merch für Gamer!

✓ 100% Baumwolle (Bio-Qualität)  
✓ Hochwertiger Digitaldruck
✓ Deutsche Fertigung 🇩🇪
✓ Versand innerhalb 2-5 Werktagen

Zeig deine Gaming-Leidenschaft! 🎯""",
    
    "default": """🏷️ Willkommen bei EmpireHazeClaw!

Premium Print-on-Demand Qualitätsprodukte!

✓ 100% Baumwolle (Bio-Qualität)
✓ Hochwertiger Digitaldruck
✓ Deutsche Fertigung 🇩🇪
✓ Versand innerhalb 2-5 Werktagen

Vielen Dank für deine Bestellung!"""
}

def load_api_key():
    """Load API key from environment or config file"""
    # Try environment
    key = os.environ.get("PRINTIFY_API_KEY")
    if key:
        return key
    
    # Try config file
    config_file = Path.home() / ".openclaw" / "workspace" / ".printify_key"
    if config_file.exists():
        with open(config_file) as f:
            for line in f:
                if "KEY=" in line:
                    return line.split("=", 1)[1].strip()
    
    return None

def get_niche(design_name):
    """Determine niche from design name"""
    name = design_name.lower()
    
    if any(w in name for w in ["dog", "cat", "pet", "puppy", "kitten", "animal"]):
        return "pet"
    elif any(w in name for w in ["game", "gamer", "pixel", "retro", "8bit", "nintendo", "playstation"]):
        return "gaming"
    else:
        return "default"

def create_product_payload(design_name, image_url=None):
    """Create product payload for Printify API"""
    
    niche = get_niche(design_name)
    title = f"EmpireHazeClaw - {design_name.replace('_', ' ').replace('-', ' ').title()}"
    description = DESCRIPTIONS.get(niche, DESCRIPTIONS["default"])
    
    # If no image uploaded yet, create without image
    # User will add image manually in dashboard
    payload = {
        "title": title[:140],
        "description": description,
        "blueprint_id": CONFIG["blueprint_id"],
        "print_provider_id": CONFIG["print_provider_id"],
        "print_areas": [
            {
                "position": "front",
                "placeholders": []
            }
        ],
        "variants": []
    }
    
    return payload

def upload_design(api_key, design_path):
    """Upload a single design to Printify"""
    
    import requests
    
    url = "https://api.printify.com/v1/uploads.json"
    
    with open(design_path, 'rb') as f:
        files = {
            'file': (Path(design_path).name, f, 'image/jpeg')
        }
        data = {
            'title': Path(design_path).stem,
            'is_visible': True
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ❌ Upload failed: {response.status_code}")
        print(f"     {response.text[:200]}")
        return None

def create_product(api_key, design_name):
    """Create a product on Printify"""
    
    import requests
    
    url = f"https://api.printify.com/v1/shops/{CONFIG['shop_id']}/products.json"
    
    payload = create_product_payload(design_name)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ❌ Product creation failed: {response.status_code}")
        print(f"     {response.text[:300]}")
        return None

def list_designs():
    """List available designs"""
    designs_dir = Path(CONFIG["designs_dir"])
    designs = sorted(designs_dir.glob("*.jpg"))
    return designs

def main():
    parser = argparse.ArgumentParser(description="Printify Auto-Uploader")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--designs", type=int, help="Number of designs to upload")
    parser.add_argument("--all", action="store_true", help="Upload all designs")
    parser.add_argument("--list", action="store_true", help="List available designs")
    
    args = parser.parse_args()
    
    # Load API key
    api_key = load_api_key()
    if not api_key:
        print("❌ No API key found!")
        print("   Set PRINTIFY_API_KEY environment variable")
        print("   Or save to ~/.openclaw/workspace/.printify_key")
        sys.exit(1)
    
    print(f"✅ API Key loaded")
    
    # Test mode
    if args.test:
        import requests
        url = "https://api.printify.com/v1/shops.json"
        r = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
        if r.status_code == 200:
            print(f"✅ API Connection OK")
            shops = r.json()
            print(f"   Shops: {len(shops)}")
            for shop in shops:
                print(f"   - {shop['id']}: {shop.get('title', 'Unnamed')} ({shop.get('sales_channel')})")
        else:
            print(f"❌ API Error: {r.status_code}")
            print(r.text[:200])
        return
    
    # List designs
    if args.list:
        designs = list_designs()
        print(f"\n📁 Available designs ({len(designs)}):")
        for d in designs:
            niche = get_niche(d.stem)
            print(f"   [{niche[:3]}] {d.name}")
        return
    
    # Determine how many to upload
    designs = list_designs()
    
    if args.designs:
        designs = designs[:args.designs]
    elif not args.all:
        designs = designs[:3]  # Default: 3
    
    print(f"\n📤 Ready to upload {len(designs)} designs\n")
    
    # Upload each design
    for i, design in enumerate(designs, 1):
        print(f"{i}. 📤 {design.name}")
        
        # Try to upload image
        result = upload_design(api_key, str(design))
        
        if result:
            print(f"   ✅ Uploaded (ID: {result.get('id')})")
        else:
            print(f"   ⚠️ Skipping upload, creating product without image")
        
        # Create product
        product = create_product(api_key, design.stem)
        
        if product:
            print(f"   ✅ Product created!")
            print(f"   🔗 {product.get('url', 'N/A')}")
        else:
            print(f"   ❌ Failed")
        
        print()
    
    print("✅ Done!")

if __name__ == "__main__":
    main()
