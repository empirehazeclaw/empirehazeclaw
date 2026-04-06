#!/usr/bin/env python3
"""
SaaS Subscription Tracker Agent
Tracks recurring subscriptions, renewals, and billing cycles.
Reads/Writes: data/subscriptions.json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "subscription_tracker.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SubscriptionTracker")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/subscriptions.json")


def load_subscriptions():
    """Load subscriptions from JSON file."""
    if not DATA_FILE.exists():
        logger.warning(f"Data file not found: {DATA_FILE}, creating default")
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "subscriptions": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        save_subscriptions(default_data)
        return default_data
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Corrupt JSON: {e}")
        raise SystemExit(1)


def save_subscriptions(data):
    """Save subscriptions to JSON file."""
    data["last_updated"] = datetime.utcnow().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved {len(data.get('subscriptions', []))} subscriptions")


def add_subscription(name, amount, currency, billing_cycle, start_date, category="general", notes=""):
    """Add a new subscription."""
    data = load_subscriptions()
    sub_id = len(data["subscriptions"]) + 1
    sub = {
        "id": sub_id,
        "name": name,
        "amount": float(amount),
        "currency": currency.upper(),
        "billing_cycle": billing_cycle.lower(),  # monthly, yearly, weekly
        "start_date": start_date,
        "category": category.lower(),
        "notes": notes,
        "active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    data["subscriptions"].append(sub)
    save_subscriptions(data)
    logger.info(f"Added subscription: {name} ({currency} {amount}/{billing_cycle})")
    return sub


def cancel_subscription(sub_id):
    """Cancel a subscription by ID."""
    data = load_subscriptions()
    for sub in data["subscriptions"]:
        if sub["id"] == int(sub_id):
            sub["active"] = False
            sub["cancelled_at"] = datetime.utcnow().isoformat()
            save_subscriptions(data)
            logger.info(f"Cancelled subscription: {sub['name']}")
            return sub
    logger.error(f"Subscription ID {sub_id} not found")
    return None


def list_subscriptions(filter_active=True, category=None):
    """List all subscriptions."""
    data = load_subscriptions()
    subs = data.get("subscriptions", [])
    if filter_active:
        subs = [s for s in subs if s.get("active", True)]
    if category:
        subs = [s for s in subs if s.get("category", "").lower() == category.lower()]
    return subs


def get_upcoming_renewals(days=30):
    """Get subscriptions renewing within N days."""
    data = load_subscriptions()
    upcoming = []
    now = datetime.utcnow()
    for sub in data.get("subscriptions", []):
        if not sub.get("active", True):
            continue
        try:
            start = datetime.fromisoformat(sub["start_date"])
        except (KeyError, ValueError):
            continue
        cycle = sub.get("billing_cycle", "monthly")
        # Calculate next renewal
        if cycle == "monthly":
            next_renewal = start
            while next_renewal <= now:
                next_renewal += timedelta(days=30)
        elif cycle == "yearly":
            next_renewal = start
            while next_renewal <= now:
                next_renewal = next_renewal.replace(year=next_renewal.year + 1)
        elif cycle == "weekly":
            next_renewal = start
            while next_renewal <= now:
                next_renewal += timedelta(weeks=1)
        else:
            continue
        days_until = (next_renewal - now).days
        if 0 <= days_until <= int(days):
            sub_copy = sub.copy()
            sub_copy["next_renewal"] = next_renewal.isoformat()
            sub_copy["days_until_renewal"] = days_until
            upcoming.append(sub_copy)
    upcoming.sort(key=lambda x: x["days_until_renewal"])
    return upcoming


def calculate_total_spend():
    """Calculate monthly equivalent spend across all active subscriptions."""
    data = load_subscriptions()
    total = 0.0
    currency = "USD"
    for sub in data.get("subscriptions", []):
        if not sub.get("active", True):
            continue
        amount = sub.get("amount", 0)
        cycle = sub.get("billing_cycle", "monthly")
        currency = sub.get("currency", "USD")
        if cycle == "monthly":
            total += amount
        elif cycle == "yearly":
            total += amount / 12
        elif cycle == "weekly":
            total += amount * 4.33
    return {"monthly_equivalent": round(total, 2), "currency": currency}


def export_csv():
    """Export subscriptions to CSV format."""
    data = load_subscriptions()
    lines = ["id,name,amount,currency,billing_cycle,start_date,category,active"]
    for sub in data.get("subscriptions", []):
        lines.append(
            f"{sub.get('id','')},{sub.get('name','')},{sub.get('amount','')},"
            f"{sub.get('currency','')},{sub.get('billing_cycle','')},"
            f"{sub.get('start_date','')},{sub.get('category','')},{sub.get('active',True)}"
        )
    return "\n".join(lines)


def cmd_list(args):
    subs = list_subscriptions(filter_active=not args.include_cancelled, category=args.category)
    if not subs:
        print("No subscriptions found.")
        return
    print(f"\n{'ID':<4} {'Name':<30} {'Amount':>10} {'Cycle':<10} {'Category':<15} {'Active':<6}")
    print("-" * 80)
    for s in subs:
        print(f"{s.get('id',''):<4} {s.get('name',''):<30} "
              f"{s.get('currency','USD')} {s.get('amount',0):>8.2f} "
              f"{s.get('billing_cycle',''):<10} {s.get('category',''):<15} "
              f"{str(s.get('active', True)):<6}")
    print(f"\nTotal active: {len([s for s in subs if s.get('active', True)])}")


def cmd_add(args):
    add_subscription(args.name, args.amount, args.currency, args.billing_cycle,
                     args.start_date, args.category, args.notes)
    print(f"Added: {args.name}")


def cmd_cancel(args):
    result = cancel_subscription(args.id)
    if result:
        print(f"Cancelled: {result['name']}")
    else:
        print(f"Subscription ID {args.id} not found.")


def cmd_renewals(args):
    upcoming = get_upcoming_renewals(args.days)
    if not upcoming:
        print(f"No renewals in the next {args.days} days.")
        return
    print(f"\nUpcoming Renewals (next {args.days} days):")
    print(f"{'Name':<30} {'Amount':>10} {'Days':>5} {'Date':<25}")
    print("-" * 75)
    for s in upcoming:
        print(f"{s.get('name',''):<30} {s.get('currency','USD')} {s.get('amount',0):>8.2f} "
              f"{s.get('days_until_renewal',''):>5} {s.get('next_renewal',''):<25}")


def cmd_spend(args):
    result = calculate_total_spend()
    print(f"\nMonthly Equivalent Spend: {result['currency']} {result['monthly_equivalent']:.2f}/month")


def cmd_export(args):
    print(export_csv())


def main():
    parser = argparse.ArgumentParser(
        description="SaaS Subscription Tracker — manage recurring subscriptions"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list
    p_list = subparsers.add_parser("list", help="List all subscriptions")
    p_list.add_argument("--include-cancelled", action="store_true", help="Include cancelled")
    p_list.add_argument("--category", help="Filter by category")
    p_list.set_defaults(func=cmd_list)

    # add
    p_add = subparsers.add_parser("add", help="Add a subscription")
    p_add.add_argument("--name", required=True, help="Subscription name")
    p_add.add_argument("--amount", type=float, required=True, help="Amount per cycle")
    p_add.add_argument("--currency", default="USD", help="Currency code")
    p_add.add_argument("--billing-cycle", dest="billing_cycle", required=True,
                        choices=["monthly", "yearly", "weekly"], help="Billing cycle")
    p_add.add_argument("--start-date", dest="start_date", required=True, help="Start date (YYYY-MM-DD)")
    p_add.add_argument("--category", default="general", help="Category")
    p_add.add_argument("--notes", default="", help="Notes")
    p_add.set_defaults(func=cmd_add)

    # cancel
    p_cancel = subparsers.add_parser("cancel", help="Cancel a subscription")
    p_cancel.add_argument("id", type=int, help="Subscription ID")
    p_cancel.set_defaults(func=cmd_cancel)

    # renewals
    p_renew = subparsers.add_parser("renewals", help="Show upcoming renewals")
    p_renew.add_argument("--days", type=int, default=30, help="Days ahead")
    p_renew.set_defaults(func=cmd_renewals)

    # spend
    p_spend = subparsers.add_parser("spend", help="Calculate total monthly spend")
    p_spend.set_defaults(func=cmd_spend)

    # export
    p_export = subparsers.add_parser("export", help="Export to CSV")
    p_export.set_defaults(func=cmd_export)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
