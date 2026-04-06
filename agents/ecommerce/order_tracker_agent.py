#!/usr/bin/env python3
"""
Order Tracker Agent
Tracks orders through their lifecycle: pending → paid → shipped → delivered → cancelled.
Data: JSON files in data/ecommerce/orders/
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "orders"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

ORDERS_FILE = DATA_DIR / "orders.json"
STATUS_LOG_FILE = DATA_DIR / "status_log.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "order_tracker.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("OrderTracker")

VALID_STATUSES = ["pending", "paid", "processing", "shipped", "delivered", "cancelled", "refunded"]
STATUS_ORDER = {s: i for i, s in enumerate(VALID_STATUSES)}


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
    if not ORDERS_FILE.exists():
        save_json(ORDERS_FILE, {})
    if not STATUS_LOG_FILE.exists():
        save_json(STATUS_LOG_FILE, [])


def _log_status_change(order_id, old_status, new_status, note):
    log = load_json(STATUS_LOG_FILE, [])
    log.append({
        "order_id": order_id,
        "from": old_status,
        "to": new_status,
        "note": note,
        "timestamp": datetime.now().isoformat(),
    })
    save_json(STATUS_LOG_FILE, log)


def cmd_create(args):
    orders = load_json(ORDERS_FILE, {})
    if args.order_id in orders:
        print(f"⚠️  Order ID '{args.order_id}' already exists.")
        return 1
    now = datetime.now().isoformat()
    items = []
    for item_str in (args.items or []):
        parts = item_str.split(":")
        items.append({
            "sku": parts[0],
            "name": parts[1] if len(parts) > 1 else parts[0],
            "qty": int(parts[2]) if len(parts) > 2 else 1,
            "price": float(parts[3]) if len(parts) > 3 else 0.0,
        })
    total = sum(i["qty"] * i["price"] for i in items)
    order = {
        "order_id": args.order_id,
        "customer": args.customer,
        "email": args.email or "",
        "status": "pending",
        "items": items,
        "total": total,
        "shipping_address": args.address or "",
        "payment_method": args.payment or "unknown",
        "notes": args.notes or "",
        "created_at": now,
        "updated_at": now,
    }
    orders[args.order_id] = order
    save_json(ORDERS_FILE, orders)
    _log_status_change(args.order_id, "", "pending", "Order created")
    logger.info(f"Created order {args.order_id} for {args.customer}")
    print(f"✅ Order '{args.order_id}' created for {args.customer} — Total: ${total:.2f} — Status: pending")
    return 0


def cmd_status(args):
    orders = load_json(ORDERS_FILE, {})
    if args.order_id not in orders:
        print(f"❌ Order '{args.order_id}' not found.")
        return 1
    order = orders[args.order_id]
    print(f"\n📦 Order: {args.order_id}")
    print(f"  Customer:     {order['customer']}")
    print(f"  Email:        {order.get('email','')}")
    print(f"  Status:       {order['status'].upper()}")
    print(f"  Total:        ${order['total']:.2f}")
    print(f"  Payment:      {order.get('payment_method','N/A')}")
    print(f"  Created:      {order.get('created_at','')}")
    print(f"  Updated:      {order.get('updated_at','')}")
    print(f"  Items:")
    for item in order.get("items", []):
        print(f"    - {item['name']} (SKU:{item['sku']}) x{item['qty']} @ ${item['price']:.2f}")
    if order.get("notes"):
        print(f"  Notes:        {order['notes']}")
    return 0


def cmd_update(args):
    orders = load_json(ORDERS_FILE, {})
    if args.order_id not in orders:
        print(f"❌ Order '{args.order_id}' not found.")
        return 1
    order = orders[args.order_id]
    old_status = order["status"]
    if args.status:
        new_status = args.status.lower()
        if new_status not in VALID_STATUSES:
            print(f"❌ Invalid status. Valid: {', '.join(VALID_STATUSES)}")
            return 1
        order["status"] = new_status
        _log_status_change(args.order_id, old_status, new_status, args.note or f"Status update via CLI")
    if args.notes:
        order["notes"] = args.notes
    if args.email:
        order["email"] = args.email
    order["updated_at"] = datetime.now().isoformat()
    save_json(ORDERS_FILE, orders)
    print(f"✅ Order '{args.order_id}' updated: {old_status} → {order['status']}")
    return 0


def cmd_list(args):
    orders = load_json(ORDERS_FILE, {})
    if not orders:
        print("No orders found.")
        return 0
    filtered = orders
    if args.status:
        filtered = {k: v for k, v in filtered.items() if v["status"] == args.status.lower()}
    if args.customer:
        filtered = {k: v for k, v in filtered.items()
                    if args.customer.lower() in v.get("customer", "").lower()}
    statuses = {"pending": "⏳", "paid": "💳", "processing": "⚙️", "shipped": "📦",
                "delivered": "✅", "cancelled": "❌", "refunded": "💸"}
    header = f"{'Order ID':<20} {'Customer':<20} {'Status':<12} {'Total':>10} {'Date':<26}"
    print(header)
    print("-" * len(header))
    for oid, o in sorted(filtered.items(), key=lambda x: x[1].get("created_at", ""), reverse=True):
        icon = statuses.get(o["status"], "?")
        print(f"{oid:<20} {o.get('customer',''):<20} {icon} {o['status']:<8} ${o['total']:>9.2f} {o.get('created_at','')[:26]}")
    print("-" * len(header))
    print(f"Showing {len(filtered)} of {len(orders)} orders")
    return 0


def cmd_cancel(args):
    orders = load_json(ORDERS_FILE, {})
    if args.order_id not in orders:
        print(f"❌ Order '{args.order_id}' not found.")
        return 1
    order = orders[args.order_id]
    if order["status"] in ("delivered", "cancelled", "refunded"):
        print(f"⚠️  Cannot cancel order in '{order['status']}' status.")
        return 1
    old_status = order["status"]
    order["status"] = "cancelled"
    order["notes"] = (order.get("notes", "") + f" | Cancelled: {args.reason}" if args.reason else order.get("notes", ""))
    order["updated_at"] = datetime.now().isoformat()
    save_json(ORDERS_FILE, orders)
    _log_status_change(args.order_id, old_status, "cancelled", args.reason or "Cancelled")
    print(f"✅ Order '{args.order_id}' cancelled.")
    return 0


def cmd_ship(args):
    orders = load_json(ORDERS_FILE, {})
    if args.order_id not in orders:
        print(f"❌ Order '{args.order_id}' not found.")
        return 1
    order = orders[args.order_id]
    old_status = order["status"]
    if old_status not in ("paid", "processing"):
        print(f"⚠️  Can only ship orders in 'paid' or 'processing' status. Current: {old_status}")
        return 1
    order["status"] = "shipped"
    order["tracking_number"] = args.tracking or "not-provided"
    order["carrier"] = args.carrier or "unknown"
    order["updated_at"] = datetime.now().isoformat()
    save_json(ORDERS_FILE, orders)
    _log_status_change(args.order_id, old_status, "shipped", f"Shipped via {args.carrier or 'unknown'}")
    print(f"✅ Order '{args.order_id}' marked as shipped. Tracking: {args.tracking or 'N/A'}")
    return 0


def cmd_timeline(args):
    log = load_json(STATUS_LOG_FILE, [])
    entries = [e for e in log if e.get("order_id") == args.order_id]
    if not entries:
        print(f"No status history for order '{args.order_id}'.")
        return 1
    entries.sort(key=lambda x: x.get("timestamp", ""))
    print(f"\n📋 Timeline for Order: {args.order_id}\n")
    for e in entries:
        arrow = f"{e['from']} → {e['to']}" if e['from'] else "created"
        print(f"  [{e['timestamp']}] {arrow}")
        if e.get("note"):
            print(f"    Note: {e['note']}")
    return 0


def cmd_stats(args):
    orders = load_json(ORDERS_FILE, {})
    if not orders:
        print("No orders.")
        return 0
    total_revenue = sum(o["total"] for o in orders.values())
    by_status = {}
    for o in orders.values():
        by_status[o["status"]] = by_status.get(o["status"], 0) + 1
    avg_order = total_revenue / len(orders)
    recent = datetime.now() - timedelta(days=30)
    recent_orders = [o for o in orders.values() if o.get("created_at", "") > recent.isoformat()]
    recent_revenue = sum(o["total"] for o in recent_orders)
    print("📊 ORDER STATISTICS")
    print(f"  Total Orders:       {len(orders)}")
    print(f"  Total Revenue:      ${total_revenue:,.2f}")
    print(f"  Average Order:      ${avg_order:,.2f}")
    print(f"  Last 30 Days:       {len(recent_orders)} orders / ${recent_revenue:,.2f}")
    print(f"  By Status:          {by_status}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="order-tracker",
        description="📦 Order Tracker Agent — Manage order lifecycle.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="Create a new order")
    p.add_argument("--order-id", required=True, help="Unique order ID")
    p.add_argument("--customer", required=True, help="Customer name")
    p.add_argument("--email", help="Customer email")
    p.add_argument("--items", nargs="+", help="Items: SKU:Name:Qty:Price")
    p.add_argument("--address", help="Shipping address")
    p.add_argument("--payment", help="Payment method")
    p.add_argument("--notes", help="Order notes")

    p = sub.add_parser("status", help="Show order details")
    p.add_argument("--order-id", required=True, help="Order ID")

    p = sub.add_parser("update", help="Update order status/notes")
    p.add_argument("--order-id", required=True, help="Order ID")
    p.add_argument("--status", choices=VALID_STATUSES, help="New status")
    p.add_argument("--notes", help="Update notes")
    p.add_argument("--email", help="Update email")
    p.add_argument("--note", help="Status change note")

    p = sub.add_parser("list", help="List all orders")
    p.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    p.add_argument("--customer", help="Filter by customer name")

    p = sub.add_parser("cancel", help="Cancel an order")
    p.add_argument("--order-id", required=True, help="Order ID")
    p.add_argument("--reason", help="Cancellation reason")

    p = sub.add_parser("ship", help="Mark order as shipped")
    p.add_argument("--order-id", required=True, help="Order ID")
    p.add_argument("--tracking", help="Tracking number")
    p.add_argument("--carrier", help="Carrier name")

    p = sub.add_parser("timeline", help="Show order status timeline")
    p.add_argument("--order-id", required=True, help="Order ID")

    p = sub.add_parser("stats", help="Show order statistics")

    args = parser.parse_args()
    init_files()
    commands = {
        "create": cmd_create,
        "status": cmd_status,
        "update": cmd_update,
        "list": cmd_list,
        "cancel": cmd_cancel,
        "ship": cmd_ship,
        "timeline": cmd_timeline,
        "stats": cmd_stats,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
