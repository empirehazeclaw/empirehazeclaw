#!/usr/bin/env python3
"""
Property Listings Agent
Manages real estate property listings with full CRUD operations.
Stores data in JSON format.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "property_listings.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PropertyListingsAgent")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/property_listings.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_data():
    """Load listings from JSON file."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"listings": [], "last_id": 0}

def save_data(data):
    """Save listings to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_listing(args):
    """Create a new property listing."""
    data = load_data()
    data["last_id"] += 1
    listing = {
        "id": data["last_id"],
        "title": args.title,
        "address": args.address,
        "price": float(args.price),
        "property_type": args.type,
        "bedrooms": int(args.bedrooms),
        "bathrooms": float(args.bathrooms),
        "sqft": int(args.sqft) if args.sqft else None,
        "description": args.description,
        "status": "available",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    data["listings"].append(listing)
    save_data(data)
    logger.info(f"Created listing {listing['id']}: {listing['title']}")
    print(f"✅ Created listing #{listing['id']}: {listing['title']}")
    return listing

def list_listings(args):
    """List all property listings with optional filters."""
    data = load_data()
    listings = data["listings"]
    
    # Apply filters
    if args.status:
        listings = [l for l in listings if l["status"] == args.status]
    if args.min_price:
        listings = [l for l in listings if l["price"] >= float(args.min_price)]
    if args.max_price:
        listings = [l for l in listings if l["price"] <= float(args.max_price)]
    if args.bedrooms:
        listings = [l for l in listings if l["bedrooms"] >= int(args.bedrooms)]
    if args.type:
        listings = [l for l in listings if l["property_type"] == args.type]
    
    if not listings:
        print("No listings found matching criteria.")
        return
    
    print(f"\n📋 Found {len(listings)} listing(s):\n")
    for l in listings:
        print(f"  [{l['id']}] {l['title']}")
        print(f"      Address: {l['address']}")
        print(f"      Price: ${l['price']:,.2f} | {l['bedrooms']} bed | {l['bathrooms']} bath | {l.get('sqft', 'N/A')} sqft")
        print(f"      Type: {l['property_type']} | Status: {l['status']}")
        print()

def get_listing(args):
    """Get a specific listing by ID."""
    data = load_data()
    for l in data["listings"]:
        if l["id"] == int(args.id):
            print(f"\n🏠 Listing #{l['id']}")
            print(f"  Title: {l['title']}")
            print(f"  Address: {l['address']}")
            print(f"  Price: ${l['price']:,.2f}")
            print(f"  Type: {l['property_type']}")
            print(f"  Bedrooms: {l['bedrooms']} | Bathrooms: {l['bathrooms']}")
            if l.get('sqft'):
                print(f"  Sqft: {l['sqft']:,}")
            print(f"  Description: {l['description']}")
            print(f"  Status: {l['status']}")
            print(f"  Created: {l['created_at']}")
            print(f"  Updated: {l['updated_at']}")
            return
    print(f"Listing #{args.id} not found.")
    logger.warning(f"Listing not found: {args.id}")

def update_listing(args):
    """Update a property listing."""
    data = load_data()
    for l in data["listings"]:
        if l["id"] == int(args.id):
            if args.title:
                l["title"] = args.title
            if args.address:
                l["address"] = args.address
            if args.price:
                l["price"] = float(args.price)
            if args.type:
                l["property_type"] = args.type
            if args.bedrooms:
                l["bedrooms"] = int(args.bedrooms)
            if args.bathrooms:
                l["bathrooms"] = float(args.bathrooms)
            if args.sqft:
                l["sqft"] = int(args.sqft)
            if args.description:
                l["description"] = args.description
            if args.status:
                l["status"] = args.status
            l["updated_at"] = datetime.now().isoformat()
            save_data(data)
            logger.info(f"Updated listing {l['id']}")
            print(f"✅ Updated listing #{l['id']}")
            return
    print(f"Listing #{args.id} not found.")

def delete_listing(args):
    """Delete a property listing."""
    data = load_data()
    original_len = len(data["listings"])
    data["listings"] = [l for l in data["listings"] if l["id"] != int(args.id)]
    if len(data["listings"]) < original_len:
        save_data(data)
        logger.info(f"Deleted listing {args.id}")
        print(f"✅ Deleted listing #{args.id}")
    else:
        print(f"Listing #{args.id} not found.")

def stats_listings(args):
    """Show statistics about listings."""
    data = load_data()
    listings = data["listings"]
    
    if not listings:
        print("No listings available.")
        return
    
    total = len(listings)
    available = len([l for l in listings if l["status"] == "available"])
    pending = len([l for l in listings if l["status"] == "pending"])
    sold = len([l for l in listings if l["status"] == "sold"])
    avg_price = sum(l["price"] for l in listings) / total
    total_value = sum(l["price"] for l in listings)
    
    print(f"\n📊 Property Listings Statistics")
    print(f"  Total Listings: {total}")
    print(f"  Available: {available}")
    print(f"  Pending: {pending}")
    print(f"  Sold: {sold}")
    print(f"  Average Price: ${avg_price:,.2f}")
    print(f"  Total Value: ${total_value:,.2f}")

def main():
    parser = argparse.ArgumentParser(
        description="Property Listings Agent - Manage real estate listings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --title "Modern Apartment" --address "123 Main St" --price 350000 --type apartment --bedrooms 2 --bathrooms 1 --description "Beautiful view"
  %(prog)s list --status available --min-price 200000
  %(prog)s get --id 1
  %(prog)s update --id 1 --price 375000 --status pending
  %(prog)s delete --id 1
  %(prog)s stats
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Create
    p_create = subparsers.add_parser("create", help="Create a new listing")
    p_create.add_argument("--title", required=True, help="Property title")
    p_create.add_argument("--address", required=True, help="Property address")
    p_create.add_argument("--price", required=True, help="Price")
    p_create.add_argument("--type", required=True, choices=["house", "apartment", "condo", "land", "commercial"], help="Property type")
    p_create.add_argument("--bedrooms", required=True, type=int, help="Number of bedrooms")
    p_create.add_argument("--bathrooms", required=True, type=float, help="Number of bathrooms")
    p_create.add_argument("--sqft", type=int, help="Square footage")
    p_create.add_argument("--description", required=True, help="Property description")
    
    # List
    p_list = subparsers.add_parser("list", help="List all listings")
    p_list.add_argument("--status", choices=["available", "pending", "sold"], help="Filter by status")
    p_list.add_argument("--min-price", help="Minimum price")
    p_list.add_argument("--max-price", help="Maximum price")
    p_list.add_argument("--bedrooms", type=int, help="Minimum bedrooms")
    p_list.add_argument("--type", choices=["house", "apartment", "condo", "land", "commercial"], help="Property type")
    
    # Get
    p_get = subparsers.add_parser("get", help="Get a listing by ID")
    p_get.add_argument("--id", required=True, help="Listing ID")
    
    # Update
    p_update = subparsers.add_parser("update", help="Update a listing")
    p_update.add_argument("--id", required=True, help="Listing ID")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--address", help="New address")
    p_update.add_argument("--price", type=float, help="New price")
    p_update.add_argument("--type", choices=["house", "apartment", "condo", "land", "commercial"], help="New type")
    p_update.add_argument("--bedrooms", type=int, help="New bedrooms")
    p_update.add_argument("--bathrooms", type=float, help="New bathrooms")
    p_update.add_argument("--sqft", type=int, help="New sqft")
    p_update.add_argument("--description", help="New description")
    p_update.add_argument("--status", choices=["available", "pending", "sold"], help="New status")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete a listing")
    p_delete.add_argument("--id", required=True, help="Listing ID")
    
    # Stats
    subparsers.add_parser("stats", help="Show listing statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "create":
            create_listing(args)
        elif args.command == "list":
            list_listings(args)
        elif args.command == "get":
            get_listing(args)
        elif args.command == "update":
            update_listing(args)
        elif args.command == "delete":
            delete_listing(args)
        elif args.command == "stats":
            stats_listings(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
