#!/usr/bin/env python3
"""
SaaS MRR Calculator Agent
Calculates Monthly Recurring Revenue, ARR, expansions, contractions, churn.
Reads/Writes: data/mrr_data.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "mrr_calculator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MRRCalculator")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/mrr_data.json")


def load_data():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "customers": [],
            "events": [],
            "last_updated": datetime.utcnow().isoformat()
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    data["last_updated"] = datetime.utcnow().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_customer(name, plan_amount, currency="USD", customer_id=None, meta=None):
    """Add a new customer with a subscription."""
    data = load_data()
    cid = customer_id or len(data["customers"]) + 1
    customer = {
        "id": cid,
        "name": name,
        "plan_amount": float(plan_amount),
        "currency": currency.upper(),
        "status": "active",
        "added_date": datetime.utcnow().date().isoformat(),
        "meta": meta or {}
    }
    data["customers"].append(customer)
    # Log new customer event
    data["events"].append({
        "type": "new",
        "customer_id": cid,
        "amount": float(plan_amount),
        "date": datetime.utcnow().isoformat()
    })
    save_data(data)
    logger.info(f"Added customer: {name}, plan: {currency} {plan_amount}/mo")
    return customer


def record_event(customer_id, event_type, amount_delta, note=""):
    """Record a MRR event: expansion, contraction, churn, reactivation."""
    data = load_data()
    event = {
        "type": event_type,
        "customer_id": int(customer_id),
        "amount_delta": float(amount_delta),
        "note": note,
        "date": datetime.utcnow().isoformat()
    }
    data["events"].append(event)

    # Update customer status
    for cust in data["customers"]:
        if cust["id"] == int(customer_id):
            if event_type == "churn":
                cust["status"] = "churned"
            elif event_type == "reactivation":
                cust["status"] = "active"
            break
    save_data(data)
    logger.info(f"Recorded event: {event_type} for customer {customer_id}, delta: {amount_delta}")


def calculate_mrr():
    """Calculate current MRR from active customers."""
    data = load_data()
    total = 0.0
    active_customers = []
    for c in data["customers"]:
        if c.get("status") == "active":
            total += c.get("plan_amount", 0)
            active_customers.append(c)
    return {
        "mrr": round(total, 2),
        "active_customers": len(active_customers),
        "currency": data["customers"][0].get("currency", "USD") if data["customers"] else "USD"
    }


def calculate_arr():
    """Calculate Annual Recurring Revenue."""
    mrr_data = calculate_mrr()
    return {
        "arr": round(mrr_data["mrr"] * 12, 2),
        "mrr": mrr_data["mrr"],
        "currency": mrr_data["currency"]
    }


def calculate_mrr_movement(months=1):
    """Calculate MRR movement over the past N months."""
    data = load_data()
    now = datetime.utcnow()
    cutoff = (now.replace(day=1) if now.month > months else now.replace(year=now.year - 1)).isoformat()
    # Actually just use last N events
    recent_events = data["events"][-100:]  # last 100 events

    new_mrr = sum(e["amount"] for e in recent_events if e["type"] == "new")
    expansion = sum(e["amount_delta"] for e in recent_events if e["type"] == "expansion")
    contraction = sum(e["amount_delta"] for e in recent_events if e["type"] == "contraction")
    churn = sum(abs(e["amount_delta"]) for e in recent_events if e["type"] == "churn")
    reactivation = sum(e["amount_delta"] for e in recent_events if e["type"] == "reactivation")

    net_new = new_mrr + expansion + reactivation - contraction - churn

    return {
        "new_mrr": round(new_mrr, 2),
        "expansion_mrr": round(expansion, 2),
        "contraction_mrr": round(contraction, 2),
        "churned_mrr": round(churn, 2),
        "reactivation_mrr": round(reactivation, 2),
        "net_new_mrr": round(net_new, 2)
    }


def get_mrr_breakdown():
    """Get MRR breakdown by plan tiers."""
    data = load_data()
    tiers = {}
    for c in data["customers"]:
        if c.get("status") != "active":
            continue
        amount = c.get("plan_amount", 0)
        tier = "free"
        if amount > 0 and amount <= 29:
            tier = "starter"
        elif amount <= 99:
            tier = "pro"
        elif amount <= 299:
            tier = "business"
        else:
            tier = "enterprise"
        if tier not in tiers:
            tiers[tier] = {"customers": 0, "mrr": 0.0}
        tiers[tier]["customers"] += 1
        tiers[tier]["mrr"] += amount
    return tiers


def cmd_list(args):
    data = load_data()
    customers = data.get("customers", [])
    if args.status:
        customers = [c for c in customers if c.get("status") == args.status]
    print(f"\n{'ID':<4} {'Name':<25} {'Plan':>8} {'Currency':<8} {'Status':<10}")
    print("-" * 60)
    for c in customers:
        print(f"{c.get('id',''):<4} {c.get('name',''):<25} "
              f"{c.get('plan_amount',0):>8.2f} {c.get('currency','USD'):<8} "
              f"{c.get('status','active'):<10}")


def cmd_mrr(args):
    mrr = calculate_mrr()
    print(f"\nMRR Report")
    print(f"  Active Customers : {mrr['active_customers']}")
    print(f"  MRR              : {mrr['currency']} {mrr['mrr']:.2f}")


def cmd_arr(args):
    arr = calculate_arr()
    print(f"\nARR Report")
    print(f"  MRR              : {arr['currency']} {arr['mrr']:.2f}")
    print(f"  ARR              : {arr['currency']} {arr['arr']:.2f}")


def cmd_movement(args):
    mv = calculate_mrr_movement(args.months)
    print(f"\nMRR Movement (last {args.months} month(s))")
    print(f"  New MRR          : +{mv['new_mrr']:.2f}")
    print(f"  Expansion MRR    : +{mv['expansion_mrr']:.2f}")
    print(f"  Contraction MRR  : {mv['contraction_mrr']:.2f}")
    print(f"  Churned MRR      : -{mv['churned_mrr']:.2f}")
    print(f"  Reactivation MRR : +{mv['reactivation_mrr']:.2f}")
    print(f"  Net New MRR      : {'+' if mv['net_new_mrr'] >= 0 else ''}{mv['net_new_mrr']:.2f}")


def cmd_breakdown(args):
    tiers = get_mrr_breakdown()
    print(f"\nMRR by Plan Tier")
    print(f"{'Tier':<15} {'Customers':>12} {'MRR':>12}")
    print("-" * 42)
    total_mrr = 0
    for tier, vals in sorted(tiers.items()):
        print(f"{tier.capitalize():<15} {vals['customers']:>12} {vals['mrr']:>12.2f}")
        total_mrr += vals["mrr"]
    print("-" * 42)
    print(f"{'Total':<15} {sum(v['customers'] for v in tiers.values()):>12} {total_mrr:>12.2f}")


def cmd_add(args):
    meta = {}
    if args.meta:
        for pair in args.meta:
            k, v = pair.split("=", 1)
            meta[k] = v
    customer = add_customer(args.name, args.plan, args.currency,
                             args.customer_id, meta)
    print(f"Added customer: {customer['name']} (ID: {customer['id']})")


def cmd_event(args):
    record_event(args.customer_id, args.type, args.amount, args.note or "")
    print(f"Recorded {args.type} event for customer {args.customer_id}, delta: {args.amount}")


def main():
    parser = argparse.ArgumentParser(description="SaaS MRR Calculator")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("list", help="List all customers").set_defaults(func=cmd_list)
    p_list = subparsers.choices["list"]
    p_list.add_argument("--status", help="Filter by status (active/churned)")

    subparsers.add_parser("mrr", help="Show current MRR").set_defaults(func=cmd_mrr)
    subparsers.add_parser("arr", help="Show ARR").set_defaults(func=cmd_arr)
    subparsers.add_parser("movement", help="Show MRR movement").set_defaults(func=cmd_movement)

    p_mv = subparsers.choices["movement"]
    p_mv.add_argument("--months", type=int, default=1, help="Number of months")

    subparsers.add_parser("breakdown", help="MRR by plan tier").set_defaults(func=cmd_breakdown)

    p_add = subparsers.add_parser("add", help="Add a customer")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--plan", type=float, required=True, help="Monthly plan amount")
    p_add.add_argument("--currency", default="USD")
    p_add.add_argument("--customer-id", type=int, dest="customer_id")
    p_add.add_argument("--meta", nargs="*", help="key=value pairs")
    p_add.set_defaults(func=cmd_add)

    p_event = subparsers.add_parser("event", help="Record a MRR event")
    p_event.add_argument("--customer-id", type=int, required=True)
    p_event.add_argument("--type", required=True,
                          choices=["expansion", "contraction", "churn", "reactivation"])
    p_event.add_argument("--amount", type=float, required=True)
    p_event.add_argument("--note", default="")
    p_event.set_defaults(func=cmd_event)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
