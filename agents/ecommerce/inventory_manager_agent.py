#!/usr/bin/env python3
"""
Inventory Manager Agent
Tracks stock levels, low-stock alerts, reorder points.
Data: JSON files in data/ecommerce/inventory/
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "inventory"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

INVENTORY_FILE = DATA_DIR / "inventory.json"
MOVEMENTS_FILE = DATA_DIR / "movements.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "inventory_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("InventoryManager")


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
    if not INVENTORY_FILE.exists():
        save_json(INVENTORY_FILE, {})
    if not MOVEMENTS_FILE.exists():
        save_json(MOVEMENTS_FILE, [])
    if not SETTINGS_FILE.exists():
        save_json(SETTINGS_FILE, {
            "low_stock_threshold": 10,
            "reorder_point": 5,
            "auto_alert": True,
        })


def cmd_add(args):
    inventory = load_json(INVENTORY_FILE, {})
    if args.sku in inventory:
        logger.warning(f"SKU {args.sku} already exists. Use update command.")
        print(f"⚠️  SKU '{args.sku}' already exists. Use --update to modify.")
        return 1
    inventory[args.sku] = {
        "name": args.name,
        "quantity": args.quantity,
        "price": args.price,
        "category": args.category or "general",
        "location": args.location or "warehouse",
        "supplier": args.supplier or "",
        "low_stock_threshold": args.threshold or 10,
        "last_updated": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
    }
    save_json(INVENTORY_FILE, inventory)
    _record_movement(args.sku, args.quantity, "add", f"Initial stock: {args.name}")
    logger.info(f"Added SKU {args.sku} with qty {args.quantity}")
    print(f"✅ Added '{args.name}' (SKU: {args.sku}) — Qty: {args.quantity}, Price: ${args.price}")
    return 0


def cmd_update(args):
    inventory = load_json(INVENTORY_FILE, {})
    if args.sku not in inventory:
        print(f"❌ SKU '{args.sku}' not found.")
        return 1
    item = inventory[args.sku]
    changes = []
    if args.quantity is not None:
        diff = args.quantity - item["quantity"]
        item["quantity"] = args.quantity
        changes.append(f"qty {item['quantity']}")
        _record_movement(args.sku, diff, "adjust", f"Manual adjust to {args.quantity}")
    if args.price is not None:
        item["price"] = args.price
        changes.append(f"price ${args.price}")
    if args.name:
        item["name"] = args.name
        changes.append(f"name '{args.name}'")
    if args.category:
        item["category"] = args.category
        changes.append(f"category '{args.category}'")
    if args.location:
        item["location"] = args.location
        changes.append(f"location '{args.location}'")
    if args.supplier:
        item["supplier"] = args.supplier
        changes.append(f"supplier '{args.supplier}'")
    if args.threshold is not None:
        item["low_stock_threshold"] = args.threshold
        changes.append(f"threshold {args.threshold}")
    item["last_updated"] = datetime.now().isoformat()
    save_json(INVENTORY_FILE, inventory)
    print(f"✅ Updated SKU {args.sku}: {', '.join(changes)}")
    return 0


def cmd_adjust(args):
    inventory = load_json(INVENTORY_FILE, {})
    if args.sku not in inventory:
        print(f"❌ SKU '{args.sku}' not found.")
        return 1
    item = inventory[args.sku]
    old_qty = item["quantity"]
    if args.increment:
        item["quantity"] += args.increment
        _record_movement(args.sku, args.increment, "increment", args.reason or "Manual increment")
    elif args.decrement:
        new_qty = old_qty - args.decrement
        if new_qty < 0:
            print(f"⚠️  Cannot reduce by {args.decrement}: only {old_qty} available.")
            return 1
        item["quantity"] = new_qty
        _record_movement(args.sku, -args.decrement, "decrement", args.reason or "Manual decrement")
    item["last_updated"] = datetime.now().isoformat()
    save_json(INVENTORY_FILE, inventory)
    print(f"✅ SKU {args.sku}: {old_qty} → {item['quantity']} ({'+' if item['quantity'] > old_qty else ''}{item['quantity'] - old_qty})")
    return 0


def cmd_list(args):
    inventory = load_json(INVENTORY_FILE, {})
    if not inventory:
        print("📦 No items in inventory.")
        return 0
    if args.category:
        inventory = {k: v for k, v in inventory.items() if v.get("category") == args.category}
    if args.low_stock:
        inventory = {k: v for k, v in inventory.items() if v.get("quantity", 0) <= v.get("low_stock_threshold", 10)}
    header = f"{'SKU':<20} {'Name':<25} {'Qty':>6} {'Price':>8} {'Category':<15} {'Location':<12}"
    print(header)
    print("-" * len(header))
    total = 0
    for sku, item in sorted(inventory.items()):
        qty = item.get("quantity", 0)
        total += qty * item.get("price", 0)
        flag = " 🔴" if qty <= item.get("low_stock_threshold", 10) else ""
        print(f"{sku:<20} {item.get('name',''):<25} {qty:>6} ${item.get('price',0):>7.2f} {item.get('category',''):<15} {item.get('location',''):<12}{flag}")
    print("-" * len(header))
    print(f"Total inventory value: ${total:,.2f}  |  Total SKUs: {len(inventory)}")
    return 0


def cmd_alerts(args):
    inventory = load_json(INVENTORY_FILE, {})
    settings = load_json(SETTINGS_FILE, {"low_stock_threshold": 10})
    alerts = []
    for sku, item in inventory.items():
        threshold = item.get("low_stock_threshold", settings.get("low_stock_threshold", 10))
        if item.get("quantity", 0) <= threshold:
            alerts.append((sku, item, threshold))
    if not alerts:
        print("✅ No low-stock alerts.")
        return 0
    print(f"🔴 LOW STOCK ALERTS ({len(alerts)} items)\n")
    for sku, item, threshold in alerts:
        pct = int(item["quantity"] / threshold * 100) if threshold > 0 else 0
        print(f"  SKU: {sku}")
        print(f"  Name: {item.get('name')}")
        print(f"  Qty: {item['quantity']} / threshold: {threshold} ({pct}%)")
        print(f"  Supplier: {item.get('supplier', 'N/A')}")
        print()
    return 0


def cmd_history(args):
    movements = load_json(MOVEMENTS_FILE, [])
    sku_movements = [m for m in movements if m.get("sku") == args.sku]
    if not sku_movements:
        print(f"No movement history for SKU '{args.sku}'.")
        return 1
    sku_movements.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    print(f"📋 Movement history for SKU: {args.sku}\n")
    for m in sku_movements[:args.limit]:
        print(f"  [{m['timestamp']}] {m['type']:>10} | {'+' if m.get('quantity',0) > 0 else ''}{m.get('quantity',0)} | {m.get('reason','')}")
    return 0


def cmd_remove(args):
    inventory = load_json(INVENTORY_FILE, {})
    if args.sku not in inventory:
        print(f"❌ SKU '{args.sku}' not found.")
        return 1
    item = inventory.pop(args.sku)
    save_json(INVENTORY_FILE, inventory)
    print(f"✅ Removed SKU '{args.sku}' ({item.get('name')})")
    return 0


def cmd_stats(args):
    inventory = load_json(INVENTORY_FILE, {})
    if not inventory:
        print("No inventory data.")
        return 0
    total_skus = len(inventory)
    total_qty = sum(v.get("quantity", 0) for v in inventory.values())
    total_value = sum(v.get("quantity", 0) * v.get("price", 0) for v in inventory.values())
    low_stock = sum(1 for v in inventory.values() if v.get("quantity", 0) <= v.get("low_stock_threshold", 10))
    out_of_stock = sum(1 for v in inventory.values() if v.get("quantity", 0) == 0)
    categories = {}
    for v in inventory.values():
        cat = v.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
    print("📊 INVENTORY STATISTICS")
    print(f"  Total SKUs:         {total_skus}")
    print(f"  Total Units:        {total_qty:,}")
    print(f"  Total Value:        ${total_value:,.2f}")
    print(f"  Low Stock Items:    {low_stock} ({low_stock*100//max(total_skus,1)}%)")
    print(f"  Out of Stock:       {out_of_stock}")
    print(f"  Categories:         {categories}")
    return 0


def cmd_search(args):
    inventory = load_json(INVENTORY_FILE, {})
    query = args.query.lower()
    results = {k: v for k, v in inventory.items()
                if query in k.lower() or query in v.get("name", "").lower()
                or query in v.get("category", "").lower()}
    if not results:
        print(f"No items found matching '{args.query}'.")
        return 1
    print(f"🔍 Found {len(results)} items:\n")
    for sku, item in results.items():
        print(f"  SKU: {sku} | {item.get('name')} | Qty: {item.get('quantity')} | ${item.get('price')}")
    return 0


def _record_movement(sku, quantity, movement_type, reason):
    movements = load_json(MOVEMENTS_FILE, [])
    movements.append({
        "sku": sku,
        "quantity": quantity,
        "type": movement_type,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    })
    save_json(MOVEMENTS_FILE, movements)


def main():
    parser = argparse.ArgumentParser(
        prog="inventory-manager",
        description="🏭 Inventory Manager Agent — Track stock, alerts, movements.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="Add new inventory item")
    p.add_argument("--sku", required=True, help="Unique SKU/ID")
    p.add_argument("--name", required=True, help="Product name")
    p.add_argument("--quantity", type=int, required=True, help="Initial quantity")
    p.add_argument("--price", type=float, required=True, help="Unit price ($)")
    p.add_argument("--category", help="Product category")
    p.add_argument("--location", help="Storage location")
    p.add_argument("--supplier", help="Supplier name")
    p.add_argument("--threshold", type=int, help="Low-stock threshold")

    p = sub.add_parser("update", help="Update inventory item")
    p.add_argument("--sku", required=True, help="SKU to update")
    p.add_argument("--name", help="New name")
    p.add_argument("--quantity", type=int, help="New quantity")
    p.add_argument("--price", type=float, help="New price")
    p.add_argument("--category", help="New category")
    p.add_argument("--location", help="New location")
    p.add_argument("--supplier", help="New supplier")
    p.add_argument("--threshold", type=int, help="Low-stock threshold")

    p = sub.add_parser("adjust", help="Increment/decrement stock")
    p.add_argument("--sku", required=True, help="SKU")
    p.add_argument("--increment", type=int, help="Add units")
    p.add_argument("--decrement", type=int, help="Remove units")
    p.add_argument("--reason", help="Reason for adjustment")

    p = sub.add_parser("list", help="List all inventory items")
    p.add_argument("--category", help="Filter by category")
    p.add_argument("--low-stock", action="store_true", help="Show only low-stock items")

    p = sub.add_parser("alerts", help="Show low-stock alerts")
    p = sub.add_parser("stats", help="Show inventory statistics")

    p = sub.add_parser("history", help="Show movement history for a SKU")
    p.add_argument("--sku", required=True, help="SKU")
    p.add_argument("--limit", type=int, default=20, help="Max records")

    p = sub.add_parser("remove", help="Remove inventory item")
    p.add_argument("--sku", required=True, help="SKU to remove")

    p = sub.add_parser("search", help="Search inventory")
    p.add_argument("query", help="Search term (SKU, name, category)")

    args = parser.parse_args()
    init_files()

    commands = {
        "add": cmd_add,
        "update": cmd_update,
        "adjust": cmd_adjust,
        "list": cmd_list,
        "alerts": cmd_alerts,
        "stats": cmd_stats,
        "history": cmd_history,
        "remove": cmd_remove,
        "search": cmd_search,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
