#!/usr/bin/env python3
"""
Property Valuator Agent - Valuate and analyze real estate properties
Part of the Real Estate Agent Suite
"""

import argparse
import json
import logging
import os
import sys
import math
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Setup
BASE_DIR = Path(__file__).parent.parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data" / "real-estate"
SCRIPT_NAME = "property_valuator_agent"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f"{SCRIPT_NAME}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(SCRIPT_NAME)

PROPERTIES_FILE = DATA_DIR / "properties.json"
VALUATIONS_FILE = DATA_DIR / "valuations.json"
MARKET_DATA_FILE = DATA_DIR / "market_data.json"


def load_data(file_path: Path, default: dict = None) -> dict:
    """Load data from JSON file."""
    if default is None:
        default = {}
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {file_path}: {e}")
    return default


def save_data(file_path: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Error saving to {file_path}: {e}")
        return False


def generate_sample_market_data() -> dict:
    """Generate sample market data for price per sqft by location."""
    market_data = load_data(MARKET_DATA_FILE)
    if not market_data.get("price_per_sqft"):
        market_data["price_per_sqft"] = {
            "New York": {"apartment": 1200, "house": 800, "condo": 1100},
            "Los Angeles": {"apartment": 800, "house": 600, "condo": 750},
            "Chicago": {"apartment": 400, "house": 350, "condo": 420},
            "Miami": {"apartment": 600, "house": 450, "condo": 580},
            "San Francisco": {"apartment": 1100, "house": 900, "condo": 1050},
            "Seattle": {"apartment": 650, "house": 500, "condo": 620},
            "Austin": {"apartment": 400, "house": 320, "condo": 380},
            "Denver": {"apartment": 500, "house": 400, "condo": 480},
        }
        market_data["market_trends"] = {
            "New York": {"trend": "stable", "change_yoy": 2.5},
            "Los Angeles": {"trend": "growing", "change_yoy": 5.2},
            "Miami": {"trend": "growing", "change_yoy": 8.1},
            "San Francisco": {"trend": "declining", "change_yoy": -3.2},
            "Austin": {"trend": "growing", "change_yoy": 4.8},
            "Seattle": {"trend": "stable", "change_yoy": 1.5},
        }
        save_data(MARKET_DATA_FILE, market_data)
    return market_data


def estimate_value(property_type: str, city: str, sqft: int,
                   bedrooms: int, bathrooms: float, year_built: int,
                   lot_size: int = None, condition: str = "good",
                   amenities: List[str] = None) -> dict:
    """Estimate property value based on various factors."""
    logger.info(f"Estimating value for {property_type} in {city}")
    
    market_data = generate_sample_market_data()
    price_per_sqft = market_data.get("price_per_sqft", {}).get(city, {}).get(property_type.lower(), 400)
    
    # Base calculation
    base_value = sqft * price_per_sqft
    
    # Bedroom adjustment
    bedroom_multiplier = 1 + (bedrooms - 2) * 0.05  # More/fewer bedrooms affect value
    base_value *= max(0.8, min(1.3, bedroom_multiplier))
    
    # Bathroom adjustment
    bathroom_multiplier = 1 + (bathrooms - 2) * 0.08
    base_value *= max(0.85, min(1.25, bathroom_multiplier))
    
    # Age adjustment
    age = datetime.now().year - year_built
    if age < 5:
        age_multiplier = 1.10
    elif age < 15:
        age_multiplier = 1.0
    elif age < 30:
        age_multiplier = 0.95
    elif age < 50:
        age_multiplier = 0.85
    else:
        age_multiplier = 0.75
    base_value *= age_multiplier
    
    # Condition adjustment
    condition_multipliers = {
        "excellent": 1.15,
        "good": 1.0,
        "fair": 0.90,
        "poor": 0.75
    }
    base_value *= condition_multipliers.get(condition, 1.0)
    
    # Lot size bonus (for houses)
    if property_type.lower() == "house" and lot_size and lot_size > 5000:
        lot_bonus = (lot_size - 5000) * 0.05
        base_value += lot_bonus
    
    # Amenities bonus
    amenity_values = {
        "pool": 15000,
        "garage": 10000,
        "garden": 5000,
        "basement": 12000,
        "renovated_kitchen": 18000,
        "renovated_bathroom": 8000,
        "central_ac": 6000,
        "smart_home": 5000,
        "view": 20000,
        "hardwood_floors": 8000
    }
    if amenities:
        for amenity in amenities:
            if amenity.lower() in amenity_values:
                base_value += amenity_values[amenity.lower()]
    
    # Market trend adjustment
    market_trend = market_data.get("market_trends", {}).get(city, {})
    trend = market_trend.get("trend", "stable")
    yoy_change = market_trend.get("change_yoy", 0)
    
    # Apply trend
    if trend == "growing":
        base_value *= 1.02
    elif trend == "declining":
        base_value *= 0.98
    
    # Round to nearest 1000
    estimated_value = round(base_value / 1000) * 1000
    price_per_sqft_actual = round(estimated_value / sqft)
    
    return {
        "estimated_value": estimated_value,
        "value_per_sqft": price_per_sqft_actual,
        "market_trend": trend,
        "yoy_change": yoy_change,
        "confidence": calculate_confidence(sqft, bedrooms, bathrooms, year_built)
    }


def calculate_confidence(sqft: int, bedrooms: int, bathrooms: float, year_built: int) -> str:
    """Calculate confidence level of valuation."""
    score = 0
    
    if 500 <= sqft <= 10000:
        score += 2
    elif 300 <= sqft <= 15000:
        score += 1
    
    if 1 <= bedrooms <= 6:
        score += 1
    
    if 1 <= bathrooms <= 5:
        score += 1
    
    if 1900 <= year_built <= 2026:
        score += 1
    
    if score >= 4:
        return "high"
    elif score >= 2:
        return "medium"
    else:
        return "low"


def add_property(address: str, city: str, state: str, zip_code: str,
                property_type: str, sqft: int, bedrooms: int, bathrooms: float,
                year_built: int, lot_size: int = None, 
                condition: str = "good", amenities: List[str] = None,
                listing_price: float = None, notes: str = "") -> dict:
    """Add a new property to the database."""
    logger.info(f"Adding property: {address}, {city}")
    
    property_id = f"PROP{int(datetime.now().timestamp())}"
    
    # Get valuation
    valuation = estimate_value(
        property_type, city, sqft, bedrooms, bathrooms, year_built,
        lot_size, condition, amenities
    )
    
    property_data = {
        "id": property_id,
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "property_type": property_type,
        "sqft": sqft,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "year_built": year_built,
        "lot_size": lot_size,
        "condition": condition,
        "amenities": amenities or [],
        "listing_price": listing_price,
        "notes": notes,
        "valuation": valuation,
        "created_at": datetime.now().isoformat()
    }
    
    properties_data = load_data(PROPERTIES_FILE, {"properties": []})
    properties_data["properties"].append(property_data)
    save_data(PROPERTIES_FILE, properties_data)
    
    # Save valuation history
    valuations_data = load_data(VALUATIONS_FILE, {"valuations": []})
    valuations_data["valuations"].append({
        "property_id": property_id,
        "valuation": valuation,
        "timestamp": datetime.now().isoformat()
    })
    save_data(VALUATIONS_FILE, valuations_data)
    
    logger.info(f"Property added: {property_id}")
    return property_data


def get_property(property_id: str) -> Optional[dict]:
    """Get a property by ID."""
    properties_data = load_data(PROPERTIES_FILE, {"properties": []})
    for p in properties_data.get("properties", []):
        if p["id"] == property_id:
            return p
    return None


def search_properties(city: str = None, property_type: str = None,
                     min_beds: int = None, max_price: float = None,
                     min_sqft: int = None) -> list:
    """Search properties with filters."""
    properties_data = load_data(PROPERTIES_FILE, {"properties": []})
    properties = properties_data.get("properties", [])
    
    results = []
    for p in properties:
        if city and p.get("city", "").lower() != city.lower():
            continue
        if property_type and p.get("property_type", "").lower() != property_type.lower():
            continue
        if min_beds and p.get("bedrooms", 0) < min_beds:
            continue
        if min_sqft and p.get("sqft", 0) < min_sqft:
            continue
        if max_price and p.get("valuation", {}).get("estimated_value", float('inf')) > max_price:
            continue
        results.append(p)
    
    return results


def get_market_analysis(city: str) -> dict:
    """Get market analysis for a city."""
    market_data = generate_sample_market_data()
    price_data = market_data.get("price_per_sqft", {}).get(city, {})
    trend_data = market_data.get("market_trends", {}).get(city, {})
    
    if not price_data:
        return None
    
    avg_price_per_sqft = sum(price_data.values()) / len(price_data) if price_data else 0
    
    return {
        "city": city,
        "price_ranges": price_data,
        "average_price_per_sqft": round(avg_price_per_sqft, 2),
        "market_trend": trend_data.get("trend", "unknown"),
        "year_over_year_change": trend_data.get("change_yoy", 0)
    }


def cmd_add(args):
    """Handle add command."""
    amenities = args.amenities.split(",") if args.amenities else None
    
    result = add_property(
        args.address, args.city, args.state, args.zip_code,
        args.type, args.sqft, args.bedrooms, args.bathrooms,
        args.year_built, args.lot_size, args.condition,
        amenities, args.price, args.notes or ""
    )
    
    print(f"\n✅ Property Added!")
    print(f"   Property ID: {result['id']}")
    print(f"   📍 {result['address']}, {result['city']}, {result['state']} {result['zip_code']}")
    print(f"   🏠 {result['property_type']} | {result['sqft']} sqft")
    print(f"   🛏️ {result['bedrooms']} bed | 🛁 {result['bathrooms']} bath | Built {result['year_built']}")
    print(f"\n   💰 Estimated Value: ${result['valuation']['estimated_value']:,}")
    print(f"   📊 Price/sqft: ${result['valuation']['value_per_sqft']}")
    print(f"   📈 Market Trend: {result['valuation']['market_trend'].upper()} ({result['valuation']['yoy_change']:+.1f}%)")
    print(f"   🎯 Confidence: {result['valuation']['confidence'].upper()}")
    
    if args.price:
        diff = result['valuation']['estimated_value'] - args.price
        diff_pct = (diff / args.price) * 100 if args.price else 0
        if diff > 0:
            print(f"\n   💡 Listing is ${diff:,.0f} BELOW estimated value ({diff_pct:.1f}%)")
        else:
            print(f"\n   💡 Listing is ${abs(diff):,.0f} ABOVE estimated value ({abs(diff_pct):.1f}%)")
    
    return 0


def cmd_valuate(args):
    """Handle valuate command."""
    amenities = args.amenities.split(",") if args.amenities else None
    
    result = estimate_value(
        args.type, args.city, args.sqft, args.bedrooms, args.bathrooms,
        args.year_built, args.lot_size, args.condition, amenities
    )
    
    print(f"\n💰 Valuation Estimate")
    print(f"   Property: {args.type} in {args.city}")
    print(f"   Size: {args.sqft} sqft | {args.bedrooms} bed | {args.bathrooms} bath")
    print(f"   Built: {args.year_built} | Condition: {args.condition}")
    print(f"\n   💰 Estimated Value: ${result['estimated_value']:,}")
    print(f"   📊 Price/sqft: ${result['value_per_sqft']}")
    print(f"   📈 Market Trend: {result['market_trend'].upper()} ({result['yoy_change']:+.1f}%)")
    print(f"   🎯 Confidence: {result['confidence'].upper()}")
    
    return 0


def cmd_show(args):
    """Handle show command."""
    prop = get_property(args.property_id)
    if not prop:
        print(f"\n❌ Property {args.property_id} not found")
        return 1
    
    print(f"\n🏠 Property: {prop['address']}")
    print(f"   ID: {prop['id']}")
    print(f"   📍 {prop['city']}, {prop['state']} {prop['zip_code']}")
    print(f"   🏠 Type: {prop['property_type']} | {prop['sqft']} sqft")
    print(f"   🛏️ {prop['bedrooms']} bedrooms | 🛁 {prop['bathrooms']} bathrooms")
    print(f"   📅 Built: {prop['year_built']} | Condition: {prop['condition']}")
    if prop.get('lot_size'):
        print(f"   📐 Lot Size: {prop['lot_size']} sqft")
    if prop.get('amenities'):
        print(f"   ✨ Amenities: {', '.join(prop['amenities'])}")
    
    val = prop.get('valuation', {})
    print(f"\n   💰 Estimated Value: ${val.get('estimated_value', 0):,}")
    print(f"   📊 Value/sqft: ${val.get('value_per_sqft', 0)}")
    print(f"   📈 Trend: {val.get('market_trend', 'unknown')} ({val.get('yoy_change', 0):+.1f}%)")
    print(f"   🎯 Confidence: {val.get('confidence', 'unknown').upper()}")
    
    if prop.get('listing_price'):
        print(f"\n   📋 Listing Price: ${prop['listing_price']:,}")
    
    if prop.get('notes'):
        print(f"\n   📝 Notes: {prop['notes']}")
    
    return 0


def cmd_search(args):
    """Handle search command."""
    results = search_properties(
        city=args.city, property_type=args.type,
        min_beds=args.min_beds, max_price=args.max_price,
        min_sqft=args.min_sqft
    )
    
    if results:
        print(f"\n🔍 Found {len(results)} properties:")
        for p in results:
            val = p.get('valuation', {})
            print(f"\n  🏠 {p['address']}")
            print(f"     📍 {p['city']}, {p['state']}")
            print(f"     🏠 {p['property_type']} | {p['sqft']} sqft | {p['bedrooms']} bed/{p['bathrooms']} bath")
            print(f"     💰 Est. Value: ${val.get('estimated_value', 0):,} | ${val.get('value_per_sqft', 0)}/sqft")
            print(f"     ID: {p['id']}")
    else:
        print(f"\n❌ No properties found with those criteria")
    return 0


def cmd_market(args):
    """Handle market command."""
    analysis = get_market_analysis(args.city)
    
    if not analysis:
        print(f"\n❌ No market data available for {args.city}")
        return 1
    
    print(f"\n📊 Market Analysis: {args.city}")
    print(f"   📈 Trend: {analysis['market_trend'].upper()}")
    print(f"   📅 Year-over-Year Change: {analysis['year_over_year_change']:+.1f}%")
    print(f"\n   💰 Average Price/sqft: ${analysis['average_price_per_sqft']}")
    print(f"\n   Price Ranges by Type:")
    for prop_type, price in analysis['price_ranges'].items():
        print(f"      • {prop_type.capitalize()}: ${price}/sqft")
    
    return 0


def cmd_list(args):
    """Handle list command."""
    properties_data = load_data(PROPERTIES_FILE, {"properties": []})
    properties = properties_data.get("properties", [])
    
    if properties:
        print(f"\n📋 All Properties ({len(properties)}):")
        for p in properties:
            val = p.get('valuation', {})
            print(f"\n  🏠 {p['address']} ({p['id']})")
            print(f"     📍 {p['city']} | {p['property_type']} | {p['sqft']} sqft")
            print(f"     💰 ${val.get('estimated_value', 0):,}")
    else:
        print("\n❌ No properties in database")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="🏠 Property Valuator Agent - Valuate and analyze real estate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --address "123 Main St" --city "New York" --state NY --zip 10001 --type apartment --sqft 1200 --bedrooms 2 --bathrooms 2 --year-built 2015
  %(prog)s valuate --type house --city "Miami" --sqft 2500 --bedrooms 4 --bathrooms 3 --year-built 2010 --condition good --amenities pool,garage
  %(prog)s show --property-id PROP1234567890
  %(prog)s search --city "Austin" --min-beds 3 --max-price 500000
  %(prog)s search --type apartment --min-sqft 800
  %(prog)s market --city "Los Angeles"
  %(prog)s list
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add and value a property")
    add_parser.add_argument("--address", required=True, help="Street address")
    add_parser.add_argument("--city", required=True, help="City")
    add_parser.add_argument("--state", required=True, help="State")
    add_parser.add_argument("--zip", required=True, dest="zip_code", help="ZIP code")
    add_parser.add_argument("--type", required=True, choices=["apartment", "house", "condo", "townhouse"],
                           help="Property type")
    add_parser.add_argument("--sqft", type=int, required=True, help="Square footage")
    add_parser.add_argument("--bedrooms", type=int, required=True, help="Number of bedrooms")
    add_parser.add_argument("--bathrooms", type=float, required=True, help="Number of bathrooms")
    add_parser.add_argument("--year-built", type=int, required=True, dest="year_built", help="Year built")
    add_parser.add_argument("--lot-size", type=int, dest="lot_size", help="Lot size in sqft")
    add_parser.add_argument("--condition", default="good", choices=["excellent", "good", "fair", "poor"],
                           help="Property condition")
    add_parser.add_argument("--amenities", help="Comma-separated amenities (pool,garage,garden)")
    add_parser.add_argument("--price", type=float, help="Listing price (for comparison)")
    add_parser.add_argument("--notes", help="Additional notes")
    
    # Valuate command
    val_parser = subparsers.add_parser("valuate", help="Quick property valuation")
    val_parser.add_argument("--type", required=True, choices=["apartment", "house", "condo", "townhouse"],
                           help="Property type")
    val_parser.add_argument("--city", required=True, help="City")
    val_parser.add_argument("--sqft", type=int, required=True, help="Square footage")
    val_parser.add_argument("--bedrooms", type=int, required=True, help="Number of bedrooms")
    val_parser.add_argument("--bathrooms", type=float, required=True, help="Number of bathrooms")
    val_parser.add_argument("--year-built", type=int, required=True, dest="year_built", help="Year built")
    val_parser.add_argument("--lot-size", type=int, dest="lot_size", help="Lot size in sqft")
    val_parser.add_argument("--condition", default="good", choices=["excellent", "good", "fair", "poor"],
                           help="Property condition")
    val_parser.add_argument("--amenities", help="Comma-separated amenities")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show property details")
    show_parser.add_argument("--property-id", required=True, help="Property ID")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search properties")
    search_parser.add_argument("--city", help="City")
    search_parser.add_argument("--type", choices=["apartment", "house", "condo", "townhouse"])
    search_parser.add_argument("--min-beds", type=int, dest="min_beds", help="Minimum bedrooms")
    search_parser.add_argument("--max-price", type=float, dest="max_price", help="Maximum price")
    search_parser.add_argument("--min-sqft", type=int, dest="min_sqft", help="Minimum sqft")
    
    # Market command
    market_parser = subparsers.add_parser("market", help="Get market analysis")
    market_parser.add_argument("--city", required=True, help="City name")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all properties")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    commands = {
        "add": cmd_add,
        "valuate": cmd_valuate,
        "show": cmd_show,
        "search": cmd_search,
        "market": cmd_market,
        "list": cmd_list
    }
    
    if args.command in commands:
        try:
            return commands[args.command](args)
        except Exception as e:
            logger.exception("Command failed")
            print(f"\n❌ Error: {e}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
