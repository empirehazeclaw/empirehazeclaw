#!/usr/bin/env python3
"""
Price Optimizer Agent
Analyzes pricing data and calculates optimized prices based on cost, margin, and competition.
Data: JSON files in data/ecommerce/pricing/
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "pricing"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

PRODUCTS_FILE = DATA_DIR / "products.json"
PRICE_HISTORY_FILE = DATA_DIR / "price_history.json"
COMPETITORS_FILE = DATA_DIR / "competitors.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "price_optimizer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("PriceOptimizer")


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
    if not PRODUCTS_FILE.exists():
        save_json(PRODUCTS_FILE, {})
    if not PRICE_HISTORY_FILE.exists():
        save_json(PRICE_HISTORY_FILE, [])
    if not COMPETITORS_FILE.exists():
        save_json(COMPETITORS_FILE, {})


def _record_price_change(sku, old_price, new_price, reason):
    history = load_json(PRICE_HISTORY_FILE, [])
    history.append({
        "sku": sku,
        "old_price": old_price,
        "new_price": new_price,
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    })
    save_json(PRICE_HISTORY_FILE, history)


def _calculate_margin(cost, price):
    if price <= 0:
        return 0.0
    return (price - cost) / price * 100


def _calculate_optimal_price(cost, target_margin, competitor_price, strategy):
    if strategy == "premium":
        base_price = cost * (1 + target_margin / 100)
        if competitor_price and competitor_price > base_price:
            return round(base_price, 2)
        return round(competitor_price * 1.1 if competitor_price else base_price, 2)
    elif strategy == "competitive":
        if competitor_price:
            return round(min(competitor_price * 0.98, competitor_price - 0.01), 2)
        return round(cost * (1 + target_margin / 100), 2)
    elif strategy == "penetration":
        return round(cost * 1.2, 2)
    else:  # default: maintain target margin
        return round(cost * (1 + target_margin / 100), 2)


def cmd_set_product(args):
    products = load_json(PRODUCTS_FILE, {})
    now = datetime.now().isoformat()
    products[args.sku] = {
        "sku": args.sku,
        "name": args.name,
        "cost": args.cost,
        "current_price": args.price,
        "target_margin": args.margin or 30.0,
        "category": args.category or "general",
        "strategy": args.strategy or "default",
        "min_price": args.min_price or (args.cost * 1.1),
        "max_price": args.max_price or (args.cost * 5.0),
        "competitor_sku": args.competitor_sku or "",
        "last_updated": now,
        "created_at": products.get(args.sku, {}).get("created_at", now),
    }
    save_json(PRODUCTS_FILE, products)
    margin = _calculate_margin(args.cost, args.price)
    print(f"✅ Product '{args.name}' (SKU: {args.sku}) configured.")
    print(f"   Cost: ${args.cost:.2f} | Price: ${args.price:.2f} | Margin: {margin:.1f}%")
    return 0


def cmd_optimize(args):
    products = load_json(PRODUCTS_FILE, {})
    competitors = load_json(COMPETITORS_FILE, {})
    recommendations = []
    for sku, p in products.items():
        cost = p.get("cost", 0)
        current = p.get("current_price", 0)
        target_margin = p.get("target_margin", 30.0)
        strategy = p.get("strategy", "default")
        competitor_price = None
        if p.get("competitor_sku") and p.get("competitor_sku") in competitors:
            competitor_price = competitors[p.get("competitor_sku")].get("price")
        optimal = _calculate_optimal_price(cost, target_margin, competitor_price, strategy)
        min_price = p.get("min_price", cost * 1.1)
        max_price = p.get("max_price", cost * 5.0)
        optimal = max(min_price, min(max_price, optimal))
        if abs(optimal - current) < 0.01:
            status = "✅ OK"
        elif optimal > current:
            status = "📈 UP"
        else:
            status = "📉 DOWN"
        diff_pct = (optimal - current) / current * 100 if current > 0 else 0
        recommendations.append({
            "sku": sku,
            "name": p.get("name"),
            "current": current,
            "optimal": optimal,
            "diff_pct": diff_pct,
            "strategy": strategy,
            "status": status,
        })
    if args.sku:
        recommendations = [r for r in recommendations if args.sku in r["sku"]]
    if not recommendations:
        print("No products to optimize.")
        return 0
    print(f"\n{'SKU':<18} {'Name':<22} {'Current':>10} {'Optimal':>10} {'Diff':>8} {'Status':<8}")
    print("-" * 80)
    for r in sorted(recommendations, key=lambda x: abs(x["diff_pct"]), reverse=True):
        print(f"{r['sku']:<18} {r['name']:<22} ${r['current']:>9.2f} ${r['optimal']:>9.2f} {r['diff_pct']:>+7.1f}% {r['status']}")
    print("-" * 80)
    return 0


def cmd_apply(args):
    products = load_json(PRODUCTS_FILE, {})
    if args.sku not in products:
        print(f"❌ Product SKU '{args.sku}' not found.")
        return 1
    p = products[args.sku]
    old_price = p["current_price"]
    if args.price is None:
        cost = p.get("cost", 0)
        target_margin = p.get("target_margin", 30.0)
        competitor_price = None
        new_price = _calculate_optimal_price(cost, target_margin, competitor_price, p.get("strategy", "default"))
    else:
        new_price = args.price
    min_price = p.get("min_price", p["cost"] * 1.1)
    max_price = p.get("max_price", p["cost"] * 5.0)
    if new_price < min_price:
        print(f"⚠️  Price ${new_price:.2f} is below minimum ${min_price:.2f}. Setting to minimum.")
        new_price = min_price
    if new_price > max_price:
        print(f"⚠️  Price ${new_price:.2f} exceeds maximum ${max_price:.2f}. Setting to maximum.")
        new_price = max_price
    p["current_price"] = new_price
    p["last_updated"] = datetime.now().isoformat()
    save_json(PRODUCTS_FILE, products)
    _record_price_change(args.sku, old_price, new_price, args.reason or "Manual update")
    diff = (new_price - old_price) / old_price * 100 if old_price > 0 else 0
    print(f"✅ Price updated for SKU '{args.sku}': ${old_price:.2f} → ${new_price:.2f} ({diff:+.1f}%)")
    return 0


def cmd_set_competitor(args):
    competitors = load_json(COMPETITORS_FILE, {})
    competitors[args.competitor_sku] = {
        "competitor_sku": args.competitor_sku,
        "name": args.name,
        "price": args.price,
        "url": args.url or "",
        "last_seen": datetime.now().isoformat(),
    }
    save_json(COMPETITORS_FILE, competitors)
    print(f"✅ Competitor '{args.name}' (SKU: {args.competitor_sku}) price set to ${args.price:.2f}")
    return 0


def cmd_history(args):
    history = load_json(PRICE_HISTORY_FILE, [])
    if args.sku:
        history = [h for h in history if h.get("sku") == args.sku]
    if not history:
        print("No price history found.")
        return 1
    history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    print(f"\n📋 Price History {('(SKU: ' + args.sku + ')') if args.sku else ''}\n")
    for h in history[:args.limit]:
        diff = h.get("new_price", 0) - h.get("old_price", 0)
        print(f"  [{h['timestamp']}] SKU:{h['sku']} | ${h.get('old_price', 0):.2f} → ${h.get('new_price', 0):.2f} ({diff:+.2f}) | {h.get('reason','')}")
    return 0


def cmd_margin_report(args):
    products = load_json(PRODUCTS_FILE, {})
    if not products:
        print("No products configured.")
        return 0
    print("\n📊 MARGIN REPORT")
    print(f"{'SKU':<18} {'Name':<22} {'Cost':>10} {'Price':>10} {'Margin %':>9} {'Status':<10}")
    print("-" * 80)
    for sku, p in sorted(products.items(), key=lambda x: x[1].get("current_price", 0)):
        cost = p.get("cost", 0)
        price = p.get("current_price", 0)
        margin = _calculate_margin(cost, price)
        target = p.get("target_margin", 30.0)
        flag = "⚠️ LOW" if margin < target - 5 else "✅ OK" if margin >= target else "⚠️"
        print(f"{sku:<18} {p.get('name',''):<22} ${cost:>9.2f} ${price:>9.2f} {margin:>8.1f}% {flag}")
    print("-" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="price-optimizer",
        description="💰 Price Optimizer Agent — Optimize pricing for margin and competitiveness.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("set-product", help="Configure product pricing")
    p.add_argument("--sku", required=True, help="Product SKU")
    p.add_argument("--name", required=True, help="Product name")
    p.add_argument("--cost", type=float, required=True, help="Unit cost ($)")
    p.add_argument("--price", type=float, required=True, help="Current selling price ($)")
    p.add_argument("--margin", type=float, help="Target margin (%%)")
    p.add_argument("--category", help="Product category")
    p.add_argument("--strategy", choices=["default", "premium", "competitive", "penetration"],
                   default="default", help="Pricing strategy")
    p.add_argument("--min-price", type=float, help="Minimum allowed price")
    p.add_argument("--max-price", type=float, help="Maximum allowed price")
    p.add_argument("--competitor-sku", help="Competitor SKU for comparison")

    p = sub.add_parser("optimize", help="Calculate optimal prices for all or one SKU")
    p.add_argument("--sku", help="Specific SKU (optional)")

    p = sub.add_parser("apply", help="Apply new price to a product")
    p.add_argument("--sku", required=True, help="Product SKU")
    p.add_argument("--price", type=float, help="New price (optional, auto-calculates)")
    p.add_argument("--reason", help="Reason for price change")

    p = sub.add_parser("set-competitor", help="Set competitor price")
    p.add_argument("--competitor-sku", required=True, help="Competitor SKU")
    p.add_argument("--name", required=True, help="Competitor name")
    p.add_argument("--price", type=float, required=True, help="Competitor price")
    p.add_argument("--url", help="Competitor URL")

    p = sub.add_parser("history", help="Show price change history")
    p.add_argument("--sku", help="Filter by SKU")
    p.add_argument("--limit", type=int, default=20, help="Max records")

    p = sub.add_parser("margin-report", help="Show margin analysis")

    args = parser.parse_args()
    init_files()
    commands = {
        "set-product": cmd_set_product,
        "optimize": cmd_optimize,
        "apply": cmd_apply,
        "set-competitor": cmd_set_competitor,
        "history": cmd_history,
        "margin-report": cmd_margin_report,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
