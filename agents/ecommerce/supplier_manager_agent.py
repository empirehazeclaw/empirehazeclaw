#!/usr/bin/env python3
"""
Supplier Manager Agent
Manages supplier records, lead times, performance, and contact info.
Data: JSON files in data/ecommerce/suppliers/
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "suppliers"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

SUPPLIERS_FILE = DATA_DIR / "suppliers.json"
ORDERS_FILE = DATA_DIR / "supplier_orders.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "supplier_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("SupplierManager")


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
    if not SUPPLIERS_FILE.exists():
        save_json(SUPPLIERS_FILE, {})
    if not ORDERS_FILE.exists():
        save_json(ORDERS_FILE, [])


def cmd_add(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id in suppliers:
        print(f"⚠️  Supplier ID '{args.supplier_id}' already exists.")
        return 1
    supplier = {
        "supplier_id": args.supplier_id,
        "name": args.name,
        "category": args.category or "general",
        "contact_name": args.contact or "",
        "email": args.email or "",
        "phone": args.phone or "",
        "address": args.address or "",
        "website": args.website or "",
        "payment_terms": args.payment_terms or "net-30",
        "lead_time_days": args.lead_time or 7,
        "min_order_value": args.min_order or 0.0,
        "rating": 0.0,
        "total_orders": 0,
        "on_time_rate": 1.0,
        "notes": args.notes or "",
        "active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    suppliers[args.supplier_id] = supplier
    save_json(SUPPLIERS_FILE, suppliers)
    logger.info(f"Added supplier {args.supplier_id}: {args.name}")
    print(f"✅ Supplier '{args.name}' (ID: {args.supplier_id}) added.")
    return 0


def cmd_list(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if not suppliers:
        print("No suppliers found.")
        return 0
    if args.category:
        suppliers = {k: v for k, v in suppliers.items() if v.get("category") == args.category}
    if not args.include_inactive:
        suppliers = {k: v for k, v in suppliers.items() if v.get("active", True)}
    header = f"{'ID':<15} {'Name':<22} {'Category':<15} {'Lead':>5} {'Orders':>6} {'Rating':>6} {'Status':<10}"
    print(header)
    print("-" * len(header))
    for sid, s in sorted(suppliers.items(), key=lambda x: x[1].get("name", "")):
        status = "🟢 active" if s.get("active", True) else "⚫ inactive"
        rating = f"{s.get('rating', 0):.1f}"
        print(f"{sid:<15} {s.get('name',''):<22} {s.get('category',''):<15} {s.get('lead_time_days',0):>5}d {s.get('total_orders',0):>6} {rating:>6} {status}")
    print("-" * len(header))
    print(f"Showing {len(suppliers)} supplier(s)")
    return 0


def cmd_show(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id not in suppliers:
        print(f"❌ Supplier '{args.supplier_id}' not found.")
        return 1
    s = suppliers[args.supplier_id]
    print(f"\n🏢 Supplier: {s.get('name')}")
    print(f"  ID:              {s.get('supplier_id')}")
    print(f"  Category:        {s.get('category')}")
    print(f"  Contact:         {s.get('contact_name')}")
    print(f"  Email:           {s.get('email')}")
    print(f"  Phone:           {s.get('phone')}")
    print(f"  Website:         {s.get('website')}")
    print(f"  Address:         {s.get('address')}")
    print(f"  Payment Terms:   {s.get('payment_terms')}")
    print(f"  Lead Time:       {s.get('lead_time_days')} days")
    print(f"  Min Order:       ${s.get('min_order_value', 0):.2f}")
    print(f"  Rating:          {s.get('rating', 0):.1f}/5.0")
    print(f"  On-Time Rate:    {s.get('on_time_rate', 1.0)*100:.0f}%")
    print(f"  Total Orders:    {s.get('total_orders', 0)}")
    print(f"  Status:          {'Active' if s.get('active', True) else 'Inactive'}")
    print(f"  Notes:           {s.get('notes','')}")
    return 0


def cmd_update(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id not in suppliers:
        print(f"❌ Supplier '{args.supplier_id}' not found.")
        return 1
    s = suppliers[args.supplier_id]
    changes = []
    if args.name:
        s["name"] = args.name; changes.append(f"name='{args.name}'")
    if args.email:
        s["email"] = args.email; changes.append("email updated")
    if args.phone:
        s["phone"] = args.phone; changes.append("phone updated")
    if args.contact:
        s["contact_name"] = args.contact; changes.append("contact updated")
    if args.lead_time is not None:
        s["lead_time_days"] = args.lead_time; changes.append(f"lead_time={args.lead_time}d")
    if args.payment_terms:
        s["payment_terms"] = args.payment_terms; changes.append(f"payment_terms='{args.payment_terms}'")
    if args.min_order is not None:
        s["min_order_value"] = args.min_order; changes.append(f"min_order=${args.min_order}")
    if args.notes:
        s["notes"] = args.notes
    s["updated_at"] = datetime.now().isoformat()
    save_json(SUPPLIERS_FILE, suppliers)
    print(f"✅ Updated '{args.supplier_id}': {', '.join(changes)}")
    return 0


def cmd_deactivate(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id not in suppliers:
        print(f"❌ Supplier '{args.supplier_id}' not found.")
        return 1
    suppliers[args.supplier_id]["active"] = False
    suppliers[args.supplier_id]["updated_at"] = datetime.now().isoformat()
    save_json(SUPPLIERS_FILE, suppliers)
    print(f"✅ Supplier '{args.supplier_id}' deactivated.")
    return 0


def cmd_order(args):
    """Record a purchase order placed with a supplier."""
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id not in suppliers:
        print(f"❌ Supplier '{args.supplier_id}' not found.")
        return 1
    order = {
        "po_number": args.po_number,
        "supplier_id": args.supplier_id,
        "items": args.items or [],
        "total": args.total or 0.0,
        "status": "ordered",
        "expected_delivery": args.delivery or "",
        "ordered_at": datetime.now().isoformat(),
        "received_at": "",
    }
    orders = load_json(ORDERS_FILE, [])
    orders.append(order)
    save_json(ORDERS_FILE, orders)
    s = suppliers[args.supplier_id]
    s["total_orders"] = s.get("total_orders", 0) + 1
    s["updated_at"] = datetime.now().isoformat()
    save_json(SUPPLIERS_FILE, suppliers)
    print(f"✅ PO '{args.po_number}' recorded for supplier '{args.supplier_id}'. Total: ${order['total']:.2f}")
    return 0


def cmd_receive(args):
    """Mark a purchase order as received."""
    orders = load_json(ORDERS_FILE, [])
    found = False
    for o in orders:
        if o["po_number"] == args.po_number:
            o["status"] = "received"
            o["received_at"] = datetime.now().isoformat()
            found = True
            break
    if not found:
        print(f"❌ PO '{args.po_number}' not found.")
        return 1
    save_json(ORDERS_FILE, orders)
    print(f"✅ PO '{args.po_number}' marked as received.")
    return 0


def cmd_performance(args):
    suppliers = load_json(SUPPLIERS_FILE, {})
    if args.supplier_id not in suppliers:
        print(f"❌ Supplier '{args.supplier_id}' not found.")
        return 1
    s = suppliers[args.supplier_id]
    orders = load_json(ORDERS_FILE, [])
    supplier_orders = [o for o in orders if o.get("supplier_id") == args.supplier_id]
    total = len(supplier_orders)
    received = sum(1 for o in supplier_orders if o.get("status") == "received")
    on_time = sum(1 for o in supplier_orders if o.get("status") == "received")
    on_time_rate = on_time / received if received > 0 else 1.0
    total_spend = sum(o.get("total", 0) for o in supplier_orders)
    print(f"\n📊 Performance for Supplier: {s.get('name')}")
    print(f"  Total POs:          {total}")
    print(f"  Received:          {received}")
    print(f"  On-Time Rate:      {on_time_rate*100:.0f}%")
    print(f"  Total Spend:       ${total_spend:,.2f}")
    print(f"  Avg Lead Time:     {s.get('lead_time_days', 0)} days")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="supplier-manager",
        description="🏢 Supplier Manager Agent — Manage suppliers and purchase orders.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="Add new supplier")
    p.add_argument("--supplier-id", required=True, help="Unique supplier ID")
    p.add_argument("--name", required=True, help="Supplier name")
    p.add_argument("--category", help="Product category")
    p.add_argument("--contact", help="Contact person")
    p.add_argument("--email", help="Email address")
    p.add_argument("--phone", help="Phone number")
    p.add_argument("--address", help="Address")
    p.add_argument("--website", help="Website URL")
    p.add_argument("--payment-terms", help="Payment terms (e.g. net-30)")
    p.add_argument("--lead-time", type=int, help="Lead time in days")
    p.add_argument("--min-order", type=float, help="Minimum order value")
    p.add_argument("--notes", help="Notes")

    p = sub.add_parser("list", help="List all suppliers")
    p.add_argument("--category", help="Filter by category")
    p.add_argument("--include-inactive", action="store_true", help="Include inactive suppliers")

    p = sub.add_parser("show", help="Show supplier details")
    p.add_argument("--supplier-id", required=True, help="Supplier ID")

    p = sub.add_parser("update", help="Update supplier info")
    p.add_argument("--supplier-id", required=True, help="Supplier ID")
    p.add_argument("--name", help="New name")
    p.add_argument("--email", help="New email")
    p.add_argument("--phone", help="New phone")
    p.add_argument("--contact", help="New contact person")
    p.add_argument("--lead-time", type=int, help="New lead time")
    p.add_argument("--payment-terms", help="New payment terms")
    p.add_argument("--min-order", type=float, help="New min order value")
    p.add_argument("--notes", help="Notes")

    p = sub.add_parser("deactivate", help="Deactivate a supplier")
    p.add_argument("--supplier-id", required=True, help="Supplier ID")

    p = sub.add_parser("order", help="Record a purchase order with supplier")
    p.add_argument("--po-number", required=True, help="Purchase order number")
    p.add_argument("--supplier-id", required=True, help="Supplier ID")
    p.add_argument("--items", nargs="+", help="Items (description)")
    p.add_argument("--total", type=float, required=True, help="Order total ($)")
    p.add_argument("--delivery", help="Expected delivery date")

    p = sub.add_parser("receive", help="Mark PO as received")
    p.add_argument("--po-number", required=True, help="Purchase order number")

    p = sub.add_parser("performance", help="Show supplier performance")
    p.add_argument("--supplier-id", required=True, help="Supplier ID")

    args = parser.parse_args()
    init_files()
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "show": cmd_show,
        "update": cmd_update,
        "deactivate": cmd_deactivate,
        "order": cmd_order,
        "receive": cmd_receive,
        "performance": cmd_performance,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
