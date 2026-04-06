#!/usr/bin/env python3
"""
Shipping Calculator Agent
Calculates shipping costs based on weight, dimensions, destination, and carrier.
Data: JSON files in data/ecommerce/shipping/
"""

import argparse
import json
import logging
import math
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "shipping"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

CARRIERS_FILE = DATA_DIR / "carriers.json"
ZONES_FILE = DATA_DIR / "zones.json"
RATES_FILE = DATA_DIR / "rates.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "shipping_calculator.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ShippingCalculator")

# Zone definitions: zone_code -> list of country codes
DEFAULT_ZONES = {
    "zone_a": ["US", "CA", "MX"],
    "zone_b": ["GB", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "CH"],
    "zone_c": ["AU", "NZ", "JP", "SG"],
    "zone_d": ["BR", "AR", "CL", "CO"],
    "zone_e": ["CN", "IN", "KR", "TH", "VN", "MY", "PH", "ID"],
    "zone_f": ["RU", "UA", "KZ", "BY", "SA", "AE", "EG", "ZA", "NG"],
}

DIM_FACTOR = 139  # DIM weight divisor for domestic US


def load_json(path, default):
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load {path}: {e}")
    return default


def save_json(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except IOError as e:
        logger.error(f"Failed to save {path}: {e}")
        raise


def init_files():
    if not CARRIERS_FILE.exists():
        save_json(CARRIERS_FILE, {
            "usps": {
                "name": "USPS",
                "base_rates": {
                    "zone_a": 8.0, "zone_b": 12.0, "zone_c": 18.0,
                    "zone_d": 22.0, "zone_e": 28.0, "zone_f": 35.0,
                },
                "per_kg": 2.5,
                "max_weight_kg": 30,
            },
            "ups": {
                "name": "UPS",
                "base_rates": {
                    "zone_a": 9.0, "zone_b": 15.0, "zone_c": 25.0,
                    "zone_d": 30.0, "zone_e": 38.0, "zone_f": 48.0,
                },
                "per_kg": 3.0,
                "max_weight_kg": 70,
            },
            "fedex": {
                "name": "FedEx",
                "base_rates": {
                    "zone_a": 10.0, "zone_b": 16.0, "zone_c": 26.0,
                    "zone_d": 32.0, "zone_e": 40.0, "zone_f": 50.0,
                },
                "per_kg": 3.2,
                "max_weight_kg": 70,
            },
            "dhl": {
                "name": "DHL",
                "base_rates": {
                    "zone_a": 11.0, "zone_b": 17.0, "zone_c": 28.0,
                    "zone_d": 35.0, "zone_e": 42.0, "zone_f": 55.0,
                },
                "per_kg": 3.5,
                "max_weight_kg": 70,
            },
        })
    if not ZONES_FILE.exists():
        save_json(ZONES_FILE, DEFAULT_ZONES)
    if not RATES_FILE.exists():
        save_json(RATES_FILE, {})


def _get_zone(country_code, zones):
    for zone_code, countries in zones.items():
        if country_code.upper() in countries:
            return zone_code
    return "zone_f"  # Default to furthest zone


def _calculate_billable_weight(weight_kg, length_cm, width_cm, height_cm):
    dim_weight = (length_cm * width_cm * height_cm) / DIM_FACTOR / 0.453592
    return max(weight_kg * 2.20462, dim_weight)  # Return in lbs


def cmd_calculate(args):
    carriers = load_json(CARRIERS_FILE, {})
    zones = load_json(ZONES_FILE, {})
    zone = _get_zone(args.country, zones)
    weight_kg = args.weight
    length = args.length or 0
    width = args.width or 0
    height = args.height or 0

    print(f"\n🚚 Shipping Quote")
    print(f"  Destination: {args.country} (Zone: {zone})")
    print(f"  Weight: {weight_kg:.2f} kg")
    if length and width and height:
        print(f"  Dimensions: {length}x{width}x{height} cm")
    print("-" * 60)
    print(f"{'Carrier':<12} {'Service':<18} {'Rate/kg':>8} {'Total':>10} {'Est.Days':>9}")
    print("-" * 60)

    results = []
    for carrier_id, carrier in carriers.items():
        if args.carrier and args.carrier != carrier_id:
            continue
        max_w = carrier.get("max_weight_kg", 70)
        if weight_kg > max_w:
            continue
        zone_rate = carrier.get("base_rates", {}).get(zone, 50.0)
        per_kg = carrier.get("per_kg", 3.0)
        total = zone_rate + (weight_kg * per_kg)
        days = args.days_estimate or carrier.get("estimated_days", {}).get(zone, "5-10")
        results.append((carrier["name"], carrier_id, total, days))

    if args.cheapest:
        results.sort(key=lambda x: x[2])
        for name, cid, total, days in results:
            print(f"{name:<12} {cid:<18} {'Yes' if cid == results[0][1] else '':>8} ${total:>9.2f} {days:>9}")
    else:
        for name, cid, total, days in results:
            print(f"{name:<12} {cid:<18} ${carrier.get('per_kg', 3.0):>7.2f}/kg ${total:>9.2f} {days:>9}")
    print("-" * 60)
    if results:
        best = min(results, key=lambda x: x[2])
        print(f"💡 Cheapest: {best[0]} at ${best[2]:.2f}")
    return 0


def cmd_add_carrier(args):
    carriers = load_json(CARRIERS_FILE, {})
    carriers[args.carrier_id] = {
        "name": args.name,
        "base_rates": {
            "zone_a": args.zone_a,
            "zone_b": args.zone_b,
            "zone_c": args.zone_c,
            "zone_d": args.zone_d,
            "zone_e": args.zone_e,
            "zone_f": args.zone_f,
        },
        "per_kg": args.per_kg,
        "max_weight_kg": args.max_weight,
        "estimated_days": {
            "zone_a": args.days_a or "2-5",
            "zone_b": args.days_b or "5-10",
            "zone_c": args.days_c or "7-14",
            "zone_d": args.days_d or "10-20",
            "zone_e": args.days_e or "14-28",
            "zone_f": args.days_f or "21-42",
        },
    }
    save_json(CARRIERS_FILE, carriers)
    print(f"✅ Carrier '{args.name}' (ID: {args.carrier_id}) configured.")
    return 0


def cmd_list_carriers(args):
    carriers = load_json(CARRIERS_FILE, {})
    if not carriers:
        print("No carriers configured.")
        return 0
    print("\n🚛 Configured Carriers")
    print(f"{'ID':<12} {'Name':<15} {'Zone A':>8} {'Zone B':>8} {'Zone C':>8} {'Zone D':>8} {'Zone E':>8} {'Zone F':>8} {'Max kg':>7}")
    print("-" * 95)
    for cid, c in carriers.items():
        br = c.get("base_rates", {})
        print(f"{cid:<12} {c.get('name',''):<15} ${br.get('zone_a',0):>7.2f} ${br.get('zone_b',0):>7.2f} ${br.get('zone_c',0):>7.2f} ${br.get('zone_d',0):>7.2f} ${br.get('zone_e',0):>7.2f} ${br.get('zone_f',0):>7.2f} {c.get('max_weight_kg',70):>7.0f}")
    return 0


def cmd_set_zone(args):
    zones = load_json(ZONES_FILE, {})
    zones[args.zone_code] = args.countries.split(",")
    save_json(ZONES_FILE, zones)
    print(f"✅ Zone '{args.zone_code}' updated: {zones[args.zone_code]}")
    return 0


def cmd_list_zones(args):
    zones = load_json(ZONES_FILE, {})
    print("\n🌍 Shipping Zones")
    for zc, countries in zones.items():
        print(f"  {zc}: {', '.join(countries)}")
    return 0


def cmd_estimate_order(args):
    """Calculate shipping for an entire order with multiple packages."""
    carriers = load_json(CARRIERS_FILE, {})
    zones = load_json(ZONES_FILE, {})
    zone = _get_zone(args.country, zones)
    total_weight = 0.0
    total_packages = 0

    if args.packages:
        for pkg_str in args.packages:
            parts = pkg_str.split(":")
            weight = float(parts[0])
            length = float(parts[1]) if len(parts) > 1 else 0
            width = float(parts[2]) if len(parts) > 2 else 0
            height = float(parts[3]) if len(parts) > 3 else 0
            total_weight += weight
            total_packages += 1

    if not args.packages:
        weight_per_item = args.weight_per_item or 0.5
        total_weight = weight_per_item * args.quantity
        total_packages = math.ceil(args.quantity / (args.items_per_package or 1))

    print(f"\n📦 Order Shipping Estimate")
    print(f"  Country: {args.country} (Zone: {zone})")
    print(f"  Total Weight: {total_weight:.2f} kg")
    print(f"  Packages: {total_packages}")
    print("-" * 55)
    print(f"{'Carrier':<12} {'Per Pkg':>10} {'Total':>10}")
    print("-" * 55)
    for cid, carrier in carriers.items():
        zone_rate = carrier.get("base_rates", {}).get(zone, 50.0)
        per_kg = carrier.get("per_kg", 3.0)
        total_cost = (zone_rate * total_packages) + (total_weight * per_kg)
        per_pkg_cost = total_cost / total_packages if total_packages else total_cost
        print(f"{carrier['name']:<12} ${per_pkg_cost:>9.2f} ${total_cost:>9.2f}")
    print("-" * 55)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="shipping-calculator",
        description="🚚 Shipping Calculator Agent — Calculate shipping costs by carrier and zone.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("calculate", help="Calculate shipping cost")
    p.add_argument("--country", required=True, help="Destination country code (e.g. US, DE)")
    p.add_argument("--weight", type=float, required=True, help="Package weight (kg)")
    p.add_argument("--length", type=float, help="Length (cm)")
    p.add_argument("--width", type=float, help="Width (cm)")
    p.add_argument("--height", type=float, help="Height (cm)")
    p.add_argument("--carrier", help="Filter by carrier ID")
    p.add_argument("--cheapest", action="store_true", help="Show cheapest first")
    p.add_argument("--days-estimate", help="Estimated delivery days override")

    p = sub.add_parser("estimate-order", help="Estimate shipping for an entire order")
    p.add_argument("--country", required=True, help="Destination country")
    p.add_argument("--quantity", type=int, required=True, help="Total items")
    p.add_argument("--weight-per-item", type=float, help="Weight per item (kg)")
    p.add_argument("--items-per-package", type=int, help="Items per package")
    p.add_argument("--packages", nargs="+", help="Packages: Weight:Length:Width:Height (kg,cm)")

    p = sub.add_parser("add-carrier", help="Add a new carrier")
    p.add_argument("--carrier-id", required=True, help="Carrier ID (e.g. dhl)")
    p.add_argument("--name", required=True, help="Carrier name")
    p.add_argument("--zone-a", "--zone-a", type=float, required=True, dest="zone_a", help="Base rate Zone A ($)")
    p.add_argument("--zone-b", type=float, required=True, help="Base rate Zone B ($)")
    p.add_argument("--zone-c", type=float, required=True, help="Base rate Zone C ($)")
    p.add_argument("--zone-d", type=float, required=True, help="Base rate Zone D ($)")
    p.add_argument("--zone-e", type=float, required=True, help="Base rate Zone E ($)")
    p.add_argument("--zone-f", type=float, required=True, help="Base rate Zone F ($)")
    p.add_argument("--per-kg", type=float, required=True, help="Rate per kg ($)")
    p.add_argument("--max-weight", type=float, default=70, help="Max weight (kg)")
    p.add_argument("--days-a", help="Est. days Zone A")
    p.add_argument("--days-b", help="Est. days Zone B")
    p.add_argument("--days-c", help="Est. days Zone C")
    p.add_argument("--days-d", help="Est. days Zone D")
    p.add_argument("--days-e", help="Est. days Zone E")
    p.add_argument("--days-f", help="Est. days Zone F")

    p = sub.add_parser("list-carriers", help="List all configured carriers")

    p = sub.add_parser("set-zone", help="Set/update a shipping zone")
    p.add_argument("--zone-code", required=True, help="Zone code (e.g. zone_a)")
    p.add_argument("--countries", required=True, help="Comma-separated country codes")

    p = sub.add_parser("list-zones", help="List all shipping zones")

    args = parser.parse_args()
    init_files()
    commands = {
        "calculate": cmd_calculate,
        "estimate-order": cmd_estimate_order,
        "add-carrier": cmd_add_carrier,
        "list-carriers": cmd_list_carriers,
        "set-zone": cmd_set_zone,
        "list-zones": cmd_list_zones,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
