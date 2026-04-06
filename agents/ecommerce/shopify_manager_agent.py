#!/usr/bin/env python3
"""
Shopify Manager Agent - OpenClaw Ecommerce Division
Manages Shopify store operations: products, orders, inventory
Persona: CEO-mode, act fast, no TODOs, real results
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Config ──────────────────────────────────────────────────────────────────
AGENT_NAME = "ShopifyManager"
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "shopify"
LOG_DIR = BASE_DIR / "logs"
CONFIG_FILE = DATA_DIR / "config.json"
PRODUCTS_FILE = DATA_DIR / "products.json"
ORDERS_FILE = DATA_DIR / "orders.json"
INVENTORY_FILE = DATA_DIR / "inventory.json"

# ── Logging Setup ─────────────────────────────────────────────────────────────
def setup_logging(verbose: bool = False) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"shopify_manager_{datetime.now():%Y%m%d}.log"
    
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(AGENT_NAME)
    logger.setLevel(level)
    
    if logger.handlers:
        logger.handlers.clear()
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logging()

# ── Data Layer ────────────────────────────────────────────────────────────────
def load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load {path}: {e}")
    return default

def save_json(path: Path, data: dict | list) -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Failed to save {path}: {e}")
        return False

def init_data():
    """Initialize data files if they don't exist."""
    if not PRODUCTS_FILE.exists():
        save_json(PRODUCTS_FILE, {"products": [], "last_updated": datetime.now().isoformat()})
    if not ORDERS_FILE.exists():
        save_json(ORDERS_FILE, {"orders": [], "last_updated": datetime.now().isoformat()})
    if not INVENTORY_FILE.exists():
        save_json(INVENTORY_FILE, {"inventory": {}, "last_updated": datetime.now().isoformat()})
    if not CONFIG_FILE.exists():
        save_json(CONFIG_FILE, {
            "shop_url": os.getenv("SHOPIFY_SHOP_URL", ""),
            "api_token": os.getenv("SHOPIFY_API_TOKEN", ""),
            "api_version": "2024-01",
            "initialized": datetime.now().isoformat()
        })
    logger.info("Data files initialized")

# ── Product Management ───────────────────────────────────────────────────────
def cmd_product_list(args) -> int:
    """List all products in the store."""
    data = load_json(PRODUCTS_FILE, {"products": []})
    products = data.get("products", [])
    
    if not products:
        print("📦 No products found. Add products with --add-product")
        return 0
    
    print(f"\n📦 Products ({len(products)} total):")
    print("-" * 80)
    for i, p in enumerate(products, 1):
        status = "🟢" if p.get("status") == "active" else "🔴"
        print(f"  {i}. {status} {p.get('title', 'Untitled')}")
        print(f"     ID: {p.get('id', 'N/A')} | Price: ${p.get('price', 0):.2f} | Stock: {p.get('stock', 0)}")
    
    return 0

def cmd_product_add(args) -> int:
    """Add a new product."""
    data = load_json(PRODUCTS_FILE, {"products": []})
    
    product = {
        "id": f"PROD_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": args.title,
        "description": args.description or "",
        "price": args.price,
        "compare_at_price": args.compare_price or 0,
        "stock": args.stock,
        "sku": args.sku or f"SKU_{datetime.now().strftime('%H%M%S')}",
        "tags": args.tags.split(",") if args.tags else [],
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data["products"].append(product)
    data["last_updated"] = datetime.now().isoformat()
    
    if save_json(PRODUCTS_FILE, data):
        logger.info(f"Product added: {product['title']} (ID: {product['id']})")
        print(f"✅ Product '{product['title']}' added with ID: {product['id']}")
        return 0
    else:
        print("❌ Failed to save product")
        return 1

def cmd_product_update(args) -> int:
    """Update an existing product."""
    data = load_json(PRODUCTS_FILE, {"products": []})
    products = data.get("products", [])
    
    for p in products:
        if p["id"] == args.product_id or (args.sku and p.get("sku") == args.sku):
            if args.title is not None:
                p["title"] = args.title
            if args.price is not None:
                p["price"] = args.price
            if args.stock is not None:
                p["stock"] = args.stock
            if args.status is not None:
                p["status"] = args.status
            p["updated_at"] = datetime.now().isoformat()
            
            data["last_updated"] = datetime.now().isoformat()
            if save_json(PRODUCTS_FILE, data):
                logger.info(f"Product updated: {p['id']}")
                print(f"✅ Product {p['id']} updated")
                return 0
            else:
                print("❌ Failed to save product")
                return 1
    
    print(f"❌ Product not found: {args.product_id or args.sku}")
    return 1

def cmd_product_delete(args) -> int:
    """Delete a product."""
    data = load_json(PRODUCTS_FILE, {"products": []})
    products = data.get("products", [])
    
    new_products = [p for p in products if p["id"] != args.product_id]
    
    if len(new_products) == len(products):
        print(f"❌ Product not found: {args.product_id}")
        return 1
    
    data["products"] = new_products
    data["last_updated"] = datetime.now().isoformat()
    
    if save_json(PRODUCTS_FILE, data):
        logger.info(f"Product deleted: {args.product_id}")
        print(f"✅ Product {args.product_id} deleted")
        return 0
    return 1

# ── Order Management ──────────────────────────────────────────────────────────
def cmd_order_list(args) -> int:
    """List orders."""
    data = load_json(ORDERS_FILE, {"orders": []})
    orders = data.get("orders", [])
    
    if not orders:
        print("📋 No orders found")
        return 0
    
    print(f"\n📋 Orders ({len(orders)} total):")
    print("-" * 80)
    
    if args.status:
        orders = [o for o in orders if o.get("status") == args.status]
        print(f"Filtered by status: {args.status} ({len(orders)} results)")
    
    for i, o in enumerate(orders, 1):
        status_icons = {"pending": "⏳", "paid": "💳", "shipped": "🚚", "delivered": "✅", "cancelled": "❌"}
        icon = status_icons.get(o.get("status", "pending"), "❓")
        print(f"  {i}. {icon} Order {o.get('order_number', o['id'])} - {o.get('customer', 'Unknown')}")
        print(f"     Total: ${o.get('total', 0):.2f} | Items: {len(o.get('items', []))} | {o.get('created_at', '')[:10]}")
    
    return 0

def cmd_order_create(args) -> int:
    """Create a new order."""
    data = load_json(ORDERS_FILE, {"orders": []})
    
    # Parse items from JSON string or create single-item order
    try:
        items = json.loads(args.items) if args.items else [{"product_id": "manual", "quantity": 1, "price": args.total}]
    except json.JSONDecodeError:
        items = [{"product_id": "manual", "quantity": 1, "price": args.total or 0}]
    
    order = {
        "id": f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_number": len(data["orders"]) + 1001,
        "customer": args.customer or "Guest",
        "email": args.email or "",
        "status": "pending",
        "items": items,
        "subtotal": sum(i.get("price", 0) * i.get("quantity", 1) for i in items),
        "total": args.total or sum(i.get("price", 0) * i.get("quantity", 1) for i in items),
        "shipping": args.shipping or 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data["orders"].append(order)
    data["last_updated"] = datetime.now().isoformat()
    
    if save_json(ORDERS_FILE, data):
        logger.info(f"Order created: {order['id']} for {order['customer']}")
        print(f"✅ Order {order['order_number']} created (ID: {order['id']})")
        return 0
    return 1

def cmd_order_update_status(args) -> int:
    """Update order status."""
    data = load_json(ORDERS_FILE, {"orders": []})
    valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
    
    if args.status not in valid_statuses:
        print(f"❌ Invalid status. Choose: {', '.join(valid_statuses)}")
        return 1
    
    for o in data["orders"]:
        if o["id"] == args.order_id or o.get("order_number") == args.order_id:
            old_status = o.get("status")
            o["status"] = args.status
            o["updated_at"] = datetime.now().isoformat()
            
            data["last_updated"] = datetime.now().isoformat()
            if save_json(ORDERS_FILE, data):
                logger.info(f"Order {o['id']} status: {old_status} → {args.status}")
                print(f"✅ Order {o['id']} status: {old_status} → {args.status}")
                return 0
            return 1
    
    print(f"❌ Order not found: {args.order_id}")
    return 1

# ── Inventory Management ───────────────────────────────────────────────────────
def cmd_inventory(args) -> int:
    """Check and update inventory."""
    inv_data = load_json(INVENTORY_FILE, {"inventory": {}})
    products = load_json(PRODUCTS_FILE, {"products": []}).get("products", [])
    
    if args.low:
        # Show low stock items
        low_stock = [p for p in products if p.get("stock", 0) <= args.low]
        if not low_stock:
            print("✅ No products with low stock")
            return 0
        print(f"\n⚠️  Low Stock Items (≤{args.low}):")
        for p in low_stock:
            print(f"  🔴 {p.get('title')}: {p.get('stock', 0)} units")
        return 0
    
    if args.sync:
        # Sync inventory from products to inventory tracker
        inventory = {}
        for p in products:
            inventory[p["id"]] = {
                "sku": p.get("sku"),
                "title": p.get("title"),
                "quantity": p.get("stock", 0),
                "updated": datetime.now().isoformat()
            }
        inv_data["inventory"] = inventory
        inv_data["last_updated"] = datetime.now().isoformat()
        save_json(INVENTORY_FILE, inv_data)
        print(f"✅ Synced {len(inventory)} products to inventory")
        return 0
    
    # Default: show inventory summary
    print(f"\n📊 Inventory Summary:")
    print("-" * 50)
    total_items = sum(p.get("stock", 0) for p in products)
    total_products = len(products)
    print(f"  Total Products: {total_products}")
    print(f"  Total Items in Stock: {total_items}")
    low_count = len([p for p in products if p.get("stock", 0) <= 5])
    print(f"  Low Stock (≤5): {low_count}")
    return 0

# ── Stats ─────────────────────────────────────────────────────────────────────
def cmd_stats(args) -> int:
    """Show store statistics."""
    products = load_json(PRODUCTS_FILE, {"products": []}).get("products", [])
    orders = load_json(ORDERS_FILE, {"orders": []}).get("orders", [])
    
    print(f"\n📊 Shopify Store Stats")
    print("=" * 50)
    print(f"  Products: {len(products)}")
    
    active_products = len([p for p in products if p.get("status") == "active"])
    print(f"    - Active: {active_products}")
    print(f"    - Inactive: {len(products) - active_products}")
    
    print(f"\n  Orders: {len(orders)}")
    status_counts = {}
    total_revenue = 0
    for o in orders:
        status = o.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        if o.get("status") in ("paid", "shipped", "delivered"):
            total_revenue += o.get("total", 0)
    
    for status, count in sorted(status_counts.items()):
        print(f"    - {status}: {count}")
    
    print(f"\n  💰 Total Revenue: ${total_revenue:.2f}")
    
    # Value of inventory
    inventory_value = sum(p.get("stock", 0) * p.get("price", 0) for p in products)
    print(f"  📦 Inventory Value: ${inventory_value:.2f}")
    
    return 0

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="shopify_manager_agent.py",
        description="🛒 Shopify Manager Agent - Full-featured Shopify store management"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    
    # Product subcommands
    prod_parser = sub.add_parser("products", help="Manage products")
    prod_sub = prod_parser.add_subparsers(dest="action")
    
    p_list = prod_sub.add_parser("list", help="List all products")
    p_list.set_defaults(func=cmd_product_list)
    
    p_add = prod_sub.add_parser("add", help="Add a new product")
    p_add.add_argument("--title", required=True, help="Product title")
    p_add.add_argument("--description", help="Product description")
    p_add.add_argument("--price", type=float, required=True, help="Price in USD")
    p_add.add_argument("--compare-price", type=float, help="Compare-at price (for sales)")
    p_add.add_argument("--stock", type=int, default=0, help="Stock quantity")
    p_add.add_argument("--sku", help="SKU identifier")
    p_add.add_argument("--tags", help="Comma-separated tags")
    p_add.set_defaults(func=cmd_product_add)
    
    p_update = prod_sub.add_parser("update", help="Update a product")
    p_update.add_argument("--product-id", help="Product ID")
    p_update.add_argument("--sku", help="Product SKU")
    p_update.add_argument("--title", help="New title")
    p_update.add_argument("--price", type=float, help="New price")
    p_update.add_argument("--stock", type=int, help="New stock quantity")
    p_update.add_argument("--status", choices=["active", "draft"], help="Product status")
    p_update.set_defaults(func=cmd_product_update)
    
    p_delete = prod_sub.add_parser("delete", help="Delete a product")
    p_delete.add_argument("--product-id", required=True, help="Product ID to delete")
    p_delete.set_defaults(func=cmd_product_delete)
    
    # Order subcommands
    order_parser = sub.add_parser("orders", help="Manage orders")
    order_sub = order_parser.add_subparsers(dest="action")
    
    o_list = order_sub.add_parser("list", help="List all orders")
    o_list.add_argument("--status", choices=["pending", "paid", "shipped", "delivered", "cancelled"], help="Filter by status")
    o_list.set_defaults(func=cmd_order_list)
    
    o_create = order_sub.add_parser("create", help="Create a new order")
    o_create.add_argument("--customer", required=True, help="Customer name")
    o_create.add_argument("--email", help="Customer email")
    o_create.add_argument("--items", help="JSON array of items")
    o_create.add_argument("--total", type=float, help="Order total")
    o_create.add_argument("--shipping", type=float, default=0, help="Shipping cost")
    o_create.set_defaults(func=cmd_order_create)
    
    o_status = order_sub.add_parser("status", help="Update order status")
    o_status.add_argument("--order-id", required=True, help="Order ID")
    o_status.add_argument("--status", required=True, choices=["pending", "paid", "shipped", "delivered", "cancelled"])
    o_status.set_defaults(func=cmd_order_update_status)
    
    # Inventory subcommand
    inv_parser = sub.add_parser("inventory", help="Manage inventory")
    inv_parser.add_argument("--low", type=int, metavar="THRESHOLD", help="Show products with stock below threshold")
    inv_parser.add_argument("--sync", action="store_true", help="Sync inventory from products")
    inv_parser.set_defaults(func=cmd_inventory)
    
    # Stats subcommand
    stats_parser = sub.add_parser("stats", help="Show store statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    args = parser.parse_args()
    
    # Initialize data on first run
    init_data()
    
    try:
        return args.func(args)
    except Exception as e:
        logger.exception(f"Error in command {args.command}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
