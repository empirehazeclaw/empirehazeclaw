#!/usr/bin/env python3
"""
Price Tracker Agent - OpenClaw E-Commerce Suite
Tracks product prices over time, detects deals, alerts on drops.
Reads/Writes: /home/clawbot/.openclaw/workspace/data/prices/prices.json
"""

import argparse
import json
import logging
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "prices"
DATA_FILE = DATA_DIR / "prices.json"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "price_tracker.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("PriceTracker")


def load_prices() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        initial = {"products": [], "price_history": [], "last_updated": datetime.utcnow().isoformat()}
        save_prices(initial)
        return initial
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load prices: {e}")
        return {"products": [], "price_history": [], "last_updated": datetime.utcnow().isoformat()}


def save_prices(data: dict) -> None:
    data["last_updated"] = datetime.utcnow().isoformat()
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save prices: {e}")


def generate_id(items: list) -> int:
    return max((i.get("id", 0) for i in items), default=0) + 1


def fetch_price(url: str) -> tuple:
    """Try to fetch price from a URL. Returns (price_float, currency, page_text)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, None, str(e)

    # Try common price patterns
    price_patterns = [
        r'["\'\$€£]?\s*(\d{1,3}[.,]\d{2})\s*(?:USD|EUR|GBP)?',
        r'price["\s:]+["\']?\s*(\d{1,3}[.,]\d{2})',
        r'(?:€|£|\$)\s*(\d{1,3}[.,]\d{2})',
        r'(\d{1,3}[.,]\d{2})\s*(?:USD|EUR|GBP)',
    ]
    for pat in price_patterns:
        matches = re.findall(pat, html, re.IGNORECASE)
        if matches:
            # Get the largest price (likely the main product price)
            prices = [float(m.replace(",", ".")) for m in matches]
            price = max(prices)
            currency = "USD"
            if "€" in html or "EUR" in html:
                currency = "EUR"
            elif "£" in html or "GBP" in html:
                currency = "GBP"
            return price, currency, html[:500]
    return None, None, html[:500]


def cmd_add(args) -> None:
    """Add a product URL to track."""
    data = load_prices()
    # Check if already tracking
    for p in data["products"]:
        if p.get("url") == args.url:
            print(f"ℹ️  Already tracking this URL (Product #{p['id']}: {p['name']})")
            return

    product = {
        "id": generate_id(data["products"]),
        "name": args.name,
        "url": args.url,
        "desired_price": args.desired_price or 0,
        "max_price": args.max_price or 0,
        "currency": args.currency or "USD",
        "category": args.category or "general",
        "notes": args.notes or "",
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "last_checked": None,
        "current_price": None,
        "lowest_price": None,
        "highest_price": None,
    }
    data["products"].append(product)
    save_prices(data)
    log.info(f"Product added to price tracking: {product['name']}")
    print(f"💰 Product #{product['id']} added: {product['name']}")
    print(f"   URL: {args.url}")
    if args.desired_price:
        print(f"   Target price: {args.currency} {args.desired_price}")


def cmd_check(args) -> None:
    """Check current prices for tracked products."""
    data = load_prices()
    products = data.get("products", [])
    if args.product_id:
        products = [p for p in products if p.get("id") == args.product_id]

    if not products:
        print("💰 No products to check.")
        return

    deals = []
    for p in products:
        if not p.get("status") == "active" and not args.include_inactive:
            continue
        print(f"\n  Checking: {p['name']}...")
        price, currency, page = fetch_price(p["url"])
        p["last_checked"] = datetime.utcnow().isoformat()

        if price is not None:
            p["current_price"] = price
            p["currency"] = currency or p.get("currency", "USD")

            if p.get("lowest_price") is None or price < p["lowest_price"]:
                p["lowest_price"] = price
            if p.get("highest_price") is None or price > p["highest_price"]:
                p["highest_price"] = price

            # Record history
            history_entry = {
                "product_id": p["id"],
                "price": price,
                "currency": currency or p.get("currency", "USD"),
                "checked_at": datetime.utcnow().isoformat(),
            }
            data["price_history"].append(history_entry)

            # Check for deal
            is_deal = False
            deal_reason = ""
            if p.get("desired_price") and price <= p["desired_price"]:
                is_deal = True
                deal_reason = f"🎯 At or below target: {price} <= {p['desired_price']}"
            elif price <= p.get("max_price", float("inf")) and p.get("max_price"):
                is_deal = True
                deal_reason = f"📉 Below max: {price} < {p['max_price']}"

            status_icon = "✅" if is_deal else "💰"
            print(f"    {status_icon} Current: {p['currency']} {price:.2f}")
            print(f"       Lowest: {p['currency']} {p.get('lowest_price', '?')}")
            print(f"       Highest: {p['currency']} {p.get('highest_price', '?')}")
            if is_deal:
                print(f"       {deal_reason}")
                deals.append((p, price, deal_reason))
        else:
            print(f"    ⚠️  Could not extract price")
            p["current_price"] = None

        import time
        time.sleep(1)  # Be polite to servers

    save_prices(data)

    if deals:
        print(f"\n🏷️  DEALS FOUND ({len(deals)}):")
        for p, price, reason in deals:
            print(f"   🎉 {p['name']}: {p['currency']} {price:.2f} — {reason}")
    else:
        print(f"\n💰 No deals found this check.")


def cmd_list(args) -> None:
    """List tracked products."""
    data = load_prices()
    products = data.get("products", [])
    if args.category:
        products = [p for p in products if p.get("category") == args.category]
    if args.status:
        products = [p for p in products if p.get("status") == args.status]
    if args.deals_only:
        products = [p for p in products if p.get("current_price") and p.get("desired_price") and p["current_price"] <= p["desired_price"]]

    if not products:
        print("💰 No products found matching filters.")
        return

    print(f"\n💰 Tracked Products ({len(products)})\n{'─'*70}")
    for p in products:
        current = p.get("current_price")
        lowest = p.get("lowest_price")
        highest = p.get("highest_price")
        currency = p.get("currency", "USD")
        last_checked = p.get("last_checked", "Never")[:19] if p.get("last_checked") else "Never"

        if current:
            if lowest and current <= lowest:
                price_str = f"💰 {currency} {current:.2f} (LOWEST!)"
            elif highest and current >= highest:
                price_str = f"🔺 {currency} {current:.2f} (HIGHEST)"
            else:
                price_str = f"   {currency} {current:.2f}"
        else:
            price_str = "   Not checked yet"

        status_icon = "🟢" if p.get("status") == "active" else "🔴"
        print(f"  {status_icon} #{p['id']:3d} {p['name'][:35]}")
        print(f"       {price_str} | Target: {p.get('desired_price', '?') or '?'}")
        print(f"       Range: {currency} {lowest or '?'} - {highest or '?'} | Checked: {last_checked}")
    print()


def cmd_history(args) -> None:
    """Show price history for a product."""
    data = load_prices()
    history = [h for h in data.get("price_history", []) if h.get("product_id") == args.product_id]

    if not history:
        print(f"📊 No price history for product #{args.product_id}.")
        return

    product = None
    for p in data["products"]:
        if p["id"] == args.product_id:
            product = p
            break

    print(f"\n📊 Price History: {product['name'] if product else args.product_id}\n{'─'*60}")
    print(f"  {'Date':<20} {'Price':>10} {'Currency':<8}")
    print(f"  {'-'*40}")

    # Show last N entries
    recent = history[-min(args.days * 4 if args.days else 20, len(history)):]
    for entry in recent:
        date = entry.get("checked_at", "")[:19]
        print(f"  {date:<20} {entry.get('price', 0):>10.2f} {entry.get('currency', 'USD'):<8}")

    # Summary stats
    prices = [h["price"] for h in history if h.get("price")]
    if prices:
        print(f"\n  Summary: Min={min(prices):.2f} | Max={max(prices):.2f} | Avg={sum(prices)/len(prices):.2f}")
    print()


def cmd_alerts(args) -> None:
    """Show products with price alerts."""
    data = load_prices()
    products = data.get("products", [])
    alerts = []
    for p in products:
        current = p.get("current_price")
        if current is None:
            continue
        desired = p.get("desired_price")
        max_p = p.get("max_price")
        if desired and current <= desired:
            alerts.append((p, current, "Below target price"))
        elif max_p and current <= max_p:
            alerts.append((p, current, "Below max price"))

    if not alerts:
        print("🏷️  No active price alerts (products at or below target).")
        return

    print(f"\n🏷️  Price Alerts ({len(alerts)})\n{'─'*60}")
    for p, price, reason in alerts:
        currency = p.get("currency", "USD")
        target = p.get("desired_price", p.get("max_price", 0))
        savings = target - price if target else 0
        pct = (savings / target * 100) if target else 0
        print(f"  🎉 {p['name']}")
        print(f"       Current: {currency} {price:.2f} | Target: {currency} {target:.2f}")
        print(f"       💰 Save {currency} {savings:.2f} ({pct:.1f}%) — {reason}")
    print()


def cmd_delete(args) -> None:
    """Delete a tracked product."""
    data = load_prices()
    original = len(data["products"])
    data["products"] = [p for p in data["products"] if p.get("id") != args.product_id]
    if len(data["products"]) < original:
        # Also clean up history
        data["price_history"] = [h for h in data["price_history"] if h.get("product_id") != args.product_id]
        save_prices(data)
        log.info(f"Product #{args.product_id} removed from price tracking")
        print(f"🗑️  Product #{args.product_id} removed from tracking.")
    else:
        print(f"❌ Product #{args.product_id} not found.")


def cmd_stats(args) -> None:
    """Show price tracking statistics."""
    data = load_prices()
    products = data.get("products", [])
    history = data.get("price_history", [])
    total = len(products)
    active = sum(1 for p in products if p.get("status") == "active")
    checked = sum(1 for p in products if p.get("last_checked"))
    with_current = [p for p in products if p.get("current_price")]
    deals = [p for p in with_current if p.get("desired_price") and p["current_price"] <= p["desired_price"]]

    print(f"\n💰 Price Tracker Statistics\n{'─'*40}")
    print(f"  Total Products:   {total}")
    print(f"  Active:           {active} 🟢")
    print(f"  Checked:          {checked}")
    print(f"  Current Deals:    {len(deals)} 🎉")
    print(f"  Price Records:    {len(history)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="price-tracker",
        description="💰 Price Tracker Agent — track product prices and detect deals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  price-tracker add "Nike Sneakers" --url https://example.com/nike --desired-price 80 --max-price 120
  price-tracker check
  price-tracker check --product-id 3
  price-tracker list --deals-only
  price-tracker history 3 --days 30
  price-tracker alerts
  price-tracker delete 5
  price-tracker stats
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a product URL to track")
    p_add.add_argument("name", help="Product name")
    p_add.add_argument("--url", required=True, help="Product URL")
    p_add.add_argument("--desired-price", type=float, help="Desired/target price")
    p_add.add_argument("--max-price", type=float, help="Maximum acceptable price")
    p_add.add_argument("--currency", default="USD", choices=["USD", "EUR", "GBP"], help="Currency")
    p_add.add_argument("--category", default="general", help="Product category")
    p_add.add_argument("--notes", default="", help="Notes")

    p_check = sub.add_parser("check", help="Check current prices")
    p_check.add_argument("--product-id", type=int, help="Check specific product only")
    p_check.add_argument("--include-inactive", action="store_true", help="Include inactive products")

    p_list = sub.add_parser("list", help="List tracked products")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--status", choices=["active", "inactive", "paused"])
    p_list.add_argument("--deals-only", action="store_true", help="Show only products at target price")

    p_hist = sub.add_parser("history", help="Show price history")
    p_hist.add_argument("product_id", type=int, help="Product ID")
    p_hist.add_argument("--days", type=int, default=30, help="Show history for N days")

    sub.add_parser("alerts", help="Show products at or below target price")

    p_del = sub.add_parser("delete", help="Delete a tracked product")
    p_del.add_argument("product_id", type=int, help="Product ID to remove")

    sub.add_parser("stats", help="Show price tracking statistics")

    args = parser.parse_args()
    try:
        if args.command == "add":
            cmd_add(args)
        elif args.command == "check":
            cmd_check(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "history":
            cmd_history(args)
        elif args.command == "alerts":
            cmd_alerts(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "stats":
            cmd_stats(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
