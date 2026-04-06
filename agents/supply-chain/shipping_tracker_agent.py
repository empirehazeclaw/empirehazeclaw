#!/usr/bin/env python3
"""
Shipping Tracker Agent
======================
Track shipments, monitor delivery status, and manage shipping logistics.

Usage:
    python3 shipping_tracker_agent.py --track --tracking-number <number>
    python3 shipping_tracker_agent.py --add-shipment --carrier <carrier> --recipient <name> --address <address>
    python3 shipping_tracker_agent.py --list-shipments
    python3 shipping_tracker_agent.py --update-status --id <id> --status <status>
"""

import argparse
import json
import logging
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "shipping_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/supply-chain")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SHIPMENTS_FILE = DATA_DIR / "shipments.json"
CARRIERS_FILE = DATA_DIR / "carriers.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def generate_tracking_number(carrier: str) -> str:
    """Generate a realistic tracking number based on carrier."""
    prefixes = {
        "UPS": "1Z",
        "FedEx": "7",
        "DHL": "JD",
        "USPS": "9400",
        "Amazon": "TBA"
    }
    prefix = prefixes.get(carrier, "TRK")
    
    if carrier == "UPS":
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        suffix = ''.join(random.choices(chars, k=16))
        return f"{prefix}{suffix}"
    elif carrier == "FedEx":
        return f"{prefix}{random.randint(100000000000, 999999999999)}"
    elif carrier == "DHL":
        return f"{prefix}{random.randint(1000000000, 9999999999)}"
    elif carrier == "USPS":
        return f"{prefix}{random.randint(10000000000000000000, 99999999999999999999)}"
    else:
        return f"{prefix}{random.randint(100000000, 999999999)}"


def initialize_data():
    """Initialize sample data."""
    if not CARRIERS_FILE.exists():
        save_json(CARRIERS_FILE, {
            "carriers": {
                "UPS": {"name": "UPS", "active": True, "tracking_url": "https://www.ups.com/track?tracknum={tracking}"},
                "FedEx": {"name": "FedEx", "active": True, "tracking_url": "https://www.fedex.com/fedextrack/?trknbr={tracking}"},
                "DHL": {"name": "DHL", "active": True, "tracking_url": "https://www.dhl.com/track?tracking-id={tracking}"},
                "USPS": {"name": "USPS", "active": True, "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking}"},
                "Amazon": {"name": "Amazon Logistics", "active": True, "tracking_url": "https://track.amazon.com/detail?trackingId={tracking}"}
            }
        })
        logger.info("Initialized carriers data")
    
    if not SHIPMENTS_FILE.exists():
        sample_shipments = {
            "shipments": [
                {
                    "id": "SHP-001",
                    "tracking_number": "1Z999AA10123456784",
                    "carrier": "UPS",
                    "recipient": "John Smith",
                    "address": "123 Main St, New York, NY 10001",
                    "status": "in_transit",
                    "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                    "created_at": datetime.now().isoformat(),
                    "history": [
                        {"status": "label_created", "timestamp": datetime.now().isoformat(), "location": "Origin Facility"}
                    ]
                },
                {
                    "id": "SHP-002",
                    "tracking_number": "794644790132",
                    "carrier": "FedEx",
                    "recipient": "Jane Doe",
                    "address": "456 Oak Ave, Los Angeles, CA 90001",
                    "status": "delivered",
                    "estimated_delivery": datetime.now().strftime("%Y-%m-%d"),
                    "created_at": (datetime.now() - timedelta(days=3)).isoformat(),
                    "history": [
                        {"status": "label_created", "timestamp": (datetime.now() - timedelta(days=3)).isoformat(), "location": "LA Hub"},
                        {"status": "picked_up", "timestamp": (datetime.now() - timedelta(days=2)).isoformat(), "location": "LA Hub"},
                        {"status": "in_transit", "timestamp": (datetime.now() - timedelta(days=1)).isoformat(), "location": "Phoenix Distribution"},
                        {"status": "out_for_delivery", "timestamp": datetime.now().isoformat(), "location": "Local Delivery"},
                        {"status": "delivered", "timestamp": datetime.now().isoformat(), "location": "Destination"}
                    ]
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        save_json(SHIPMENTS_FILE, sample_shipments)
        logger.info("Initialized shipments data")


def get_next_shipment_id() -> str:
    """Get next shipment ID."""
    shipments = load_json(SHIPMENTS_FILE)
    existing = shipments.get("shipments", [])
    if not existing:
        return "SHP-001"
    max_id = max(int(s["id"].split("-")[1]) for s in existing)
    return f"SHP-{max_id + 1:03d}"


def add_shipment(carrier: str, recipient: str, address: str, 
                 weight: Optional[float] = None, description: Optional[str] = None) -> dict:
    """Add a new shipment."""
    carriers = load_json(CARRIERS_FILE)
    
    if carrier not in carriers.get("carriers", {}):
        raise ValueError(f"Carrier {carrier} not found")
    
    shipments = load_json(SHIPMENTS_FILE)
    
    # Estimate delivery based on carrier
    delivery_days = {"UPS": 3, "FedEx": 3, "DHL": 5, "USPS": 5, "Amazon": 2}
    est_days = delivery_days.get(carrier, 5)
    
    tracking_number = generate_tracking_number(carrier)
    shipment_id = get_next_shipment_id()
    
    now = datetime.now()
    shipment = {
        "id": shipment_id,
        "tracking_number": tracking_number,
        "carrier": carrier,
        "recipient": recipient,
        "address": address,
        "weight": weight,
        "description": description,
        "status": "label_created",
        "estimated_delivery": (now + timedelta(days=est_days)).strftime("%Y-%m-%d"),
        "created_at": now.isoformat(),
        "history": [
            {"status": "label_created", "timestamp": now.isoformat(), "location": "Origin Facility"}
        ]
    }
    
    shipments["shipments"].append(shipment)
    shipments["last_updated"] = now.isoformat()
    save_json(SHIPMENTS_FILE, shipments)
    
    logger.info(f"Created shipment {shipment_id} with tracking {tracking_number}")
    return shipment


def track_shipment(tracking_number: str) -> Optional[dict]:
    """Track a shipment by tracking number."""
    shipments = load_json(SHIPMENTS_FILE)
    
    for shipment in shipments.get("shipments", []):
        if shipment["tracking_number"] == tracking_number:
            return shipment
    
    return None


def update_status(shipment_id: str, new_status: str, location: Optional[str] = None) -> bool:
    """Update shipment status."""
    shipments = load_json(SHIPMENTS_FILE)
    
    for shipment in shipments.get("shipments", []):
        if shipment["id"] == shipment_id:
            old_status = shipment["status"]
            shipment["status"] = new_status
            
            event = {
                "status": new_status,
                "timestamp": datetime.now().isoformat(),
                "location": location or "Unknown"
            }
            shipment["history"].append(event)
            shipments["last_updated"] = datetime.now().isoformat()
            
            save_json(SHIPMENTS_FILE, shipments)
            logger.info(f"Updated shipment {shipment_id}: {old_status} -> {new_status}")
            return True
    
    return False


def list_shipments(status_filter: Optional[str] = None) -> List[dict]:
    """List all shipments, optionally filtered by status."""
    shipments = load_json(SHIPMENTS_FILE)
    result = shipments.get("shipments", [])
    
    if status_filter:
        result = [s for s in result if s["status"] == status_filter]
    
    return result


def get_tracking_url(carrier: str, tracking_number: str) -> str:
    """Get tracking URL for a carrier."""
    carriers = load_json(CARRIERS_FILE)
    carrier_data = carriers.get("carriers", {}).get(carrier, {})
    url_template = carrier_data.get("tracking_url", "https://example.com/track/{tracking}")
    return url_template.replace("{tracking}", tracking_number)


def display_shipment(shipment: dict):
    """Display shipment details."""
    status_emoji = {
        "label_created": "📋",
        "picked_up": "📦",
        "in_transit": "🚚",
        "out_for_delivery": "🚚",
        "delivered": "✅",
        "exception": "⚠️",
        "returned": "↩️"
    }
    emoji = status_emoji.get(shipment["status"], "❓")
    
    print("\n" + "=" * 60)
    print(f"{emoji} SHIPMENT: {shipment['id']}")
    print("=" * 60)
    print(f"  Tracking:  {shipment['tracking_number']}")
    print(f"  Carrier:   {shipment['carrier']}")
    print(f"  Recipient: {shipment['recipient']}")
    print(f"  Address:   {shipment['address']}")
    print(f"  Status:    {shipment['status'].upper().replace('_', ' ')}")
    print(f"  Est. Delivery: {shipment.get('estimated_delivery', 'N/A')}")
    print()
    print("  HISTORY:")
    for event in reversed(shipment.get("history", [])):
        ts = event["timestamp"][:19].replace("T", " ")
        print(f"    [{ts}] {event['status'].replace('_', ' ').title()} @ {event.get('location', 'N/A')}")
    print("=" * 60)


def display_shipments(shipments: List[dict]):
    """Display list of shipments."""
    if not shipments:
        print("\nNo shipments found.")
        return
    
    print("\n" + "=" * 80)
    print("📦 SHIPMENTS")
    print("=" * 80)
    
    status_emoji = {
        "label_created": "📋",
        "picked_up": "📦",
        "in_transit": "🚚",
        "out_for_delivery": "🚚",
        "delivered": "✅",
        "exception": "⚠️",
        "returned": "↩️"
    }
    
    for s in shipments:
        emoji = status_emoji.get(s["status"], "❓")
        print(f"{emoji} {s['id']} | {s['tracking_number'][:15]}... | {s['carrier']} | "
              f"{s['recipient'][:15]}... | {s['status'].replace('_', ' ')}")
    
    print("=" * 80)


def main():
    valid_statuses = ["label_created", "picked_up", "in_transit", "out_for_delivery", 
                      "delivered", "exception", "returned"]
    
    parser = argparse.ArgumentParser(
        description="Shipping Tracker Agent - Track and manage shipments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --track --tracking-number 1Z999AA10123456784
  %(prog)s --add-shipment --carrier UPS --recipient "John Doe" --address "123 Main St, NYC"
  %(prog)s --list-shipments
  %(prog)s --list-shipments --status in_transit
  %(prog)s --update-status --id SHP-001 --status in_transit --location "Chicago Hub"
  %(prog)s --init
        """
    )
    
    parser.add_argument("--track", action="store_true", help="Track a shipment by tracking number")
    parser.add_argument("--tracking-number", type=str, help="Tracking number")
    parser.add_argument("--add-shipment", action="store_true", help="Add a new shipment")
    parser.add_argument("--carrier", type=str, choices=["UPS", "FedEx", "DHL", "USPS", "Amazon"], help="Shipping carrier")
    parser.add_argument("--recipient", type=str, help="Recipient name")
    parser.add_argument("--address", type=str, help="Delivery address")
    parser.add_argument("--weight", type=float, help="Package weight (optional)")
    parser.add_argument("--description", type=str, help="Package description (optional)")
    parser.add_argument("--list-shipments", action="store_true", help="List all shipments")
    parser.add_argument("--status", type=str, help="Filter by status (for --list-shipments)")
    parser.add_argument("--update-status", action="store_true", help="Update shipment status")
    parser.add_argument("--id", type=str, help="Shipment ID")
    parser.add_argument("--new-status", dest="new_status", type=str, choices=valid_statuses, help="New status")
    parser.add_argument("--location", type=str, help="Location for status update")
    parser.add_argument("--init", action="store_true", help="Initialize sample data")
    
    args = parser.parse_args()
    
    try:
        initialize_data()
        
        if args.init:
            print("✅ Sample data initialized")
            return
        
        if args.track:
            if not args.tracking_number:
                parser.error("--track requires --tracking-number")
            shipment = track_shipment(args.tracking_number)
            if shipment:
                display_shipment(shipment)
            else:
                print(f"\n❌ Shipment not found: {args.tracking_number}")
                sys.exit(1)
            return
        
        if args.add_shipment:
            if not args.carrier or not args.recipient or not args.address:
                parser.error("--add-shipment requires --carrier, --recipient, and --address")
            shipment = add_shipment(args.carrier, args.recipient, args.address, args.weight, args.description)
            print(f"\n✅ Shipment created: {shipment['id']}")
            print(f"   Tracking: {shipment['tracking_number']}")
            print(f"   Carrier: {shipment['carrier']}")
            print(f"   Est. Delivery: {shipment['estimated_delivery']}")
            return
        
        if args.list_shipments:
            shipments = list_shipments(args.status)
            display_shipments(shipments)
            return
        
        if args.update_status:
            if not args.id or not args.new_status:
                parser.error("--update-status requires --id and --new-status")
            if update_status(args.id, args.new_status, args.location):
                print(f"\n✅ Status updated for {args.id}: {args.new_status}")
                # Show updated shipment
                shipments = list_shipments()
                for s in shipments:
                    if s["id"] == args.id:
                        display_shipment(s)
                        break
            else:
                print(f"\n❌ Shipment not found: {args.id}")
                sys.exit(1)
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
