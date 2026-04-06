#!/usr/bin/env python3
"""
Coupon Manager Agent
Creates, validates, and tracks discount coupons/promo codes.
Data: JSON files in data/ecommerce/coupons/
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "coupons"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

COUPONS_FILE = DATA_DIR / "coupons.json"
USAGE_FILE = DATA_DIR / "coupon_usage.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "coupon_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("CouponManager")


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
    if not COUPONS_FILE.exists():
        save_json(COUPONS_FILE, {})
    if not USAGE_FILE.exists():
        save_json(USAGE_FILE, [])


def _is_valid(coupon, now_dt):
    if not coupon.get("active", True):
        return False, "Coupon is inactive"
    usage_count = sum(1 for u in load_json(USAGE_FILE, []) if u.get("coupon_code") == coupon.get("code"))
    if coupon.get("max_uses") and usage_count >= coupon["max_uses"]:
        return False, "Coupon usage limit reached"
    starts = coupon.get("starts_at", "")
    if starts and now_dt < datetime.fromisoformat(starts):
        return False, "Coupon not yet active"
    expires = coupon.get("expires_at", "")
    if expires and now_dt > datetime.fromisoformat(expires):
        return False, "Coupon has expired"
    return True, "Valid"


def _generate_code(prefix, length=8):
    import random, string
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix.upper()}{suffix}"


def cmd_create(args):
    coupons = load_json(COUPONS_FILE, {})
    code = args.code or _generate_code(args.prefix, args.length)
    if code in coupons:
        print(f"⚠️  Coupon code '{code}' already exists.")
        return 1
    now = datetime.now()
    expires = now + timedelta(days=args.duration) if args.duration else None
    coupon = {
        "code": code,
        "description": args.description or "",
        "discount_type": args.type or "percentage",
        "discount_value": args.value,
        "min_order_amount": args.min_order or 0.0,
        "max_discount": args.max_discount,
        "max_uses": args.max_uses,
        "current_uses": 0,
        "active": True,
        "starts_at": now.isoformat(),
        "expires_at": expires.isoformat() if expires else "",
        "applicable_categories": args.categories.split(",") if args.categories else [],
        "applicable_skus": args.skus.split(",") if args.skus else [],
        "first_time_only": args.first_time_only,
        "created_at": now.isoformat(),
    }
    coupons[code] = coupon
    save_json(COUPONS_FILE, coupons)
    logger.info(f"Created coupon: {code} ({args.type}: {args.value})")
    print(f"✅ Coupon '{code}' created:")
    print(f"   Type: {args.type} ({args.value})")
    print(f"   Expires: {expires.strftime('%Y-%m-%d') if expires else 'Never'}")
    print(f"   Max Uses: {args.max_uses or 'Unlimited'}")
    print(f"   Min Order: ${args.min_order or 0:.2f}")
    return 0


def cmd_validate(args):
    coupons = load_json(COUPONS_FILE, {})
    code = args.code.upper()
    if code not in coupons:
        print(f"❌ Coupon '{code}' not found.")
        return 1
    coupon = coupons[code]
    now = datetime.now()
    valid, msg = _is_valid(coupon, now)
    usage = sum(1 for u in load_json(USAGE_FILE, []) if u.get("coupon_code") == code)
    print(f"\n🎟️  Coupon: {code}")
    print(f"  Status:        {'✅ VALID' if valid else '❌ INVALID'}")
    print(f"  Reason:        {msg}")
    print(f"  Description:   {coupon.get('description','')}")
    print(f"  Discount:      {coupon['discount_type']} — {coupon['discount_value']}")
    if coupon.get("max_discount"):
        print(f"  Max Discount:  ${coupon['max_discount']:.2f}")
    print(f"  Min Order:     ${coupon.get('min_order_amount', 0):.2f}")
    print(f"  Uses:          {usage} / {coupon.get('max_uses') or '∞'}")
    print(f"  Expires:       {coupon.get('expires_at', 'Never')}")
    return 0 if valid else 1


def cmd_apply(args):
    """Apply coupon to an order and calculate discount."""
    coupons = load_json(COUPONS_FILE, {})
    code = args.code.upper()
    if code not in coupons:
        print(f"❌ Coupon '{code}' not found.")
        return 1
    coupon = coupons[code]
    now = datetime.now()
    valid, msg = _is_valid(coupon, now)
    if not valid:
        print(f"❌ Cannot apply coupon: {msg}")
        return 1
    order_amount = args.order_amount
    if order_amount < coupon.get("min_order_amount", 0):
        print(f"❌ Order amount ${order_amount:.2f} is below minimum ${coupon['min_order_amount']:.2f}.")
        return 1
    if coupon["discount_type"] == "percentage":
        discount = order_amount * coupon["discount_value"] / 100
        if coupon.get("max_discount"):
            discount = min(discount, coupon["max_discount"])
    else:
        discount = min(coupon["discount_value"], order_amount)
    final_amount = order_amount - discount
    print(f"\n🧮 Coupon Applied: {code}")
    print(f"  Original:      ${order_amount:.2f}")
    print(f"  Discount:       -${discount:.2f} ({coupon['discount_type']}: {coupon['discount_value']}{'%' if coupon['discount_type'] == 'percentage' else '$'})")
    print(f"  Final:          ${final_amount:.2f}")
    if args.save:
        usage = load_json(USAGE_FILE, [])
        usage.append({
            "coupon_code": code,
            "order_id": args.order_id or "",
            "customer_email": args.customer_email or "",
            "order_amount": order_amount,
            "discount": discount,
            "applied_at": now.isoformat(),
        })
        save_json(USAGE_FILE, usage)
        coupons[code]["current_uses"] = coupons[code].get("current_uses", 0) + 1
        save_json(COUPONS_FILE, coupons)
        print(f"  ✅ Saved to usage log (Order: {args.order_id or 'N/A'})")
    return 0


def cmd_list(args):
    coupons = load_json(COUPONS_FILE, {})
    now = datetime.now()
    if args.status == "active":
        active_codes = []
        for code, c in coupons.items():
            valid, _ = _is_valid(c, now)
            if valid:
                active_codes.append(code)
        coupons = {k: coupons[k] for k in active_codes}
    elif args.status == "expired":
        expired = []
        for code, c in coupons.items():
            expires = c.get("expires_at", "")
            if expires and now > datetime.fromisoformat(expires):
                expired.append(code)
        coupons = {k: coupons[k] for k in expired}
    if args.category:
        coupons = {k: v for k, v in coupons.items() if args.category in v.get("applicable_categories", [])}
    print(f"\n{'Code':<16} {'Type':<12} {'Value':>8} {'Min$':>7} {'Uses':>6} {'Expires':<26} {'Status':<10}")
    print("-" * 95)
    for code, c in sorted(coupons.items(), key=lambda x: x[1].get("expires_at", "")):
        usage = sum(1 for u in load_json(USAGE_FILE, []) if u.get("coupon_code") == code)
        max_uses = c.get("max_uses") or "∞"
        valid, _ = _is_valid(c, now)
        status = "🟢" if valid else "⚫"
        expires = c.get("expires_at", "Never")[:26] if c.get("expires_at") else "Never"
        discount_str = f"{c['discount_value']}{'%' if c['discount_type'] == 'percentage' else '$'}"
        print(f"{code:<16} {c.get('discount_type',''):<12} {discount_str:>8} ${c.get('min_order_amount',0):>6.2f} {usage:>5}/{max_uses:<4} {expires:<26} {status}")
    print("-" * 95)
    print(f"Showing {len(coupons)} coupon(s)")
    return 0


def cmd_deactivate(args):
    coupons = load_json(COUPONS_FILE, {})
    if args.code.upper() not in coupons:
        print(f"❌ Coupon '{args.code}' not found.")
        return 1
    coupons[args.code.upper()]["active"] = False
    save_json(COUPONS_FILE, coupons)
    print(f"✅ Coupon '{args.code.upper()}' deactivated.")
    return 0


def cmd_usage(args):
    usage = load_json(USAGE_FILE, [])
    if args.code:
        usage = [u for u in usage if u.get("coupon_code") == args.code.upper()]
    if not usage:
        print("No usage records found.")
        return 1
    total_discount = sum(u.get("discount", 0) for u in usage)
    total_orders = sum(u.get("order_amount", 0) for u in usage)
    print(f"\n📋 Coupon Usage ({len(usage)} records)")
    print(f"{'Code':<16} {'Order':<18} {'Customer':<25} {'Order$':>10} {'Discount':>10} {'Applied At':<26}")
    print("-" * 115)
    for u in sorted(usage, key=lambda x: x.get("applied_at", ""), reverse=True)[:args.limit]:
        print(f"{u.get('coupon_code',''):<16} {u.get('order_id',''):<18} {u.get('customer_email',''):<25} ${u.get('order_amount',0):>9.2f} ${u.get('discount',0):>9.2f} {u.get('applied_at','')[:26]}")
    print("-" * 115)
    print(f"Total: {len(usage)} uses | ${total_orders:.2f} orders | ${total_discount:.2f} discounts given")
    return 0


def cmd_stats(args):
    coupons = load_json(COUPONS_FILE, {})
    usage = load_json(USAGE_FILE, [])
    total_discount = sum(u.get("discount", 0) for u in usage)
    total_orders = sum(u.get("order_amount", 0) for u in usage)
    total_uses = len(usage)
    active_coupons = sum(1 for c in coupons.values() if c.get("active", True))
    print("\n📊 COUPON STATISTICS")
    print(f"  Total Coupons:     {len(coupons)}")
    print(f"  Active Coupons:    {active_coupons}")
    print(f"  Total Uses:        {total_uses}")
    print(f"  Total Orders:      ${total_orders:,.2f}")
    print(f"  Total Discount:    ${total_discount:,.2f}")
    if total_orders > 0:
        roi = (total_orders - total_discount) / total_discount if total_discount > 0 else float('inf')
        print(f"  ROI Ratio:         {roi:.2f}x (orders per $ discount)")
    by_type = {}
    for u in usage:
        code = u.get("coupon_code", "")
        if code in coupons:
            t = coupons[code].get("discount_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
    print(f"  By Type:           {by_type}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="coupon-manager",
        description="🎟️ Coupon Manager Agent — Create and manage discount coupons.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="Create a new coupon")
    p.add_argument("--code", help="Coupon code (auto-generated if omitted)")
    p.add_argument("--prefix", default="SAVE", help="Prefix for auto-generated code")
    p.add_argument("--length", type=int, default=8, help="Length of auto-generated code suffix")
    p.add_argument("--description", help="Coupon description")
    p.add_argument("--type", choices=["percentage", "fixed"], default="percentage", help="Discount type")
    p.add_argument("--value", type=float, required=True, help="Discount value")
    p.add_argument("--max-discount", type=float, help="Maximum discount ($) for percentage type")
    p.add_argument("--min-order", type=float, help="Minimum order amount")
    p.add_argument("--max-uses", type=int, help="Maximum total uses")
    p.add_argument("--duration", type=int, help="Days until expiry")
    p.add_argument("--categories", help="Applicable categories (comma-separated)")
    p.add_argument("--skus", help="Applicable SKUs (comma-separated)")
    p.add_argument("--first-time-only", action="store_true", help="First-time customers only")

    p = sub.add_parser("validate", help="Validate a coupon")
    p.add_argument("--code", required=True, help="Coupon code")

    p = sub.add_parser("apply", help="Apply coupon to an order and calculate discount")
    p.add_argument("--code", required=True, help="Coupon code")
    p.add_argument("--order-amount", type=float, required=True, help="Order amount ($)")
    p.add_argument("--order-id", help="Order ID")
    p.add_argument("--customer-email", help="Customer email")
    p.add_argument("--save", action="store_true", help="Save to usage log")

    p = sub.add_parser("list", help="List all coupons")
    p.add_argument("--status", choices=["active", "expired"], help="Filter by status")
    p.add_argument("--category", help="Filter by category")

    p = sub.add_parser("deactivate", help="Deactivate a coupon")
    p.add_argument("--code", required=True, help="Coupon code")

    p = sub.add_parser("usage", help="Show coupon usage history")
    p.add_argument("--code", help="Filter by coupon code")
    p.add_argument("--limit", type=int, default=50, help="Max records")

    p = sub.add_parser("stats", help="Show coupon statistics")

    args = parser.parse_args()
    init_files()
    commands = {
        "create": cmd_create,
        "validate": cmd_validate,
        "apply": cmd_apply,
        "list": cmd_list,
        "deactivate": cmd_deactivate,
        "usage": cmd_usage,
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
