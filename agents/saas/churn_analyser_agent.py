#!/usr/bin/env python3
"""
SaaS Churn Analyser Agent
Analyses customer churn patterns, at-risk customers, and calculates churn metrics.
Reads/Writes: data/churn_data.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "churn_analyser.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ChurnAnalyser")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/churn_data.json")


def load_data():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "customers": [],
            "churn_events": [],
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


def add_customer(name, join_date, plan_amount, risk_score=0, customer_id=None):
    """Add a customer record."""
    data = load_data()
    cid = customer_id or len(data["customers"]) + 1
    customer = {
        "id": cid,
        "name": name,
        "join_date": join_date,
        "plan_amount": float(plan_amount),
        "risk_score": float(risk_score),  # 0-100, higher = more at risk
        "status": "active",
        "last_activity": datetime.utcnow().date().isoformat(),
        "churned_at": None
    }
    data["customers"].append(customer)
    save_data(data)
    logger.info(f"Added customer: {name}")
    return customer


def record_churn(customer_id, reason="", churn_date=None):
    """Record a churn event."""
    data = load_data()
    for c in data["customers"]:
        if c["id"] == int(customer_id):
            c["status"] = "churned"
            date = churn_date or datetime.utcnow().isoformat()
            c["churned_at"] = date
            c["churn_reason"] = reason
            event = {
                "customer_id": int(customer_id),
                "customer_name": c["name"],
                "plan_amount": c.get("plan_amount", 0),
                "churn_date": date,
                "reason": reason
            }
            data["churn_events"].append(event)
            save_data(data)
            logger.info(f"Recorded churn: {c['name']} - {reason}")
            return event
    logger.error(f"Customer {customer_id} not found")
    return None


def update_risk_score(customer_id, score):
    """Update at-risk score for a customer."""
    data = load_data()
    for c in data["customers"]:
        if c["id"] == int(customer_id):
            c["risk_score"] = float(score)
            c["last_activity"] = datetime.utcnow().date().isoformat()
            save_data(data)
            logger.info(f"Updated risk score for {c['name']}: {score}")
            return c
    return None


def calculate_churn_rate(period_days=30):
    """Calculate churn rate over a period."""
    data = load_data()
    now = datetime.utcnow()
    cutoff = (now - timedelta(days=period_days)).isoformat()

    total_at_start = 0
    churned_in_period = 0

    for c in data["customers"]:
        if c.get("join_date", "") <= cutoff:
            total_at_start += 1
        if c.get("churned_at", "") and c["churned_at"] >= cutoff:
            churned_in_period += 1

    if total_at_start == 0:
        return 0.0
    return round((churned_in_period / total_at_start) * 100, 2)


def get_at_risk_customers(threshold=50):
    """Get customers with risk score above threshold."""
    data = load_data()
    at_risk = [c for c in data["customers"]
               if c.get("status") == "active" and c.get("risk_score", 0) >= threshold]
    at_risk.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    return at_risk


def get_churn_analysis():
    """Comprehensive churn analysis."""
    data = load_data()
    total_customers = len(data["customers"])
    churned = [c for c in data["customers"] if c.get("status") == "churned"]
    active = [c for c in data["customers"] if c.get("status") == "active"]

    monthly_churn = calculate_churn_rate(30)
    quarterly_churn = calculate_churn_rate(90)

    # Churn by reason
    reasons = {}
    for ev in data.get("churn_events", []):
        reason = ev.get("reason", "unknown") or "unknown"
        reasons[reason] = reasons.get(reason, 0) + 1

    # MRR lost
    mrr_lost = sum(c.get("plan_amount", 0) for c in churned)

    return {
        "total_customers": total_customers,
        "active_customers": len(active),
        "churned_customers": len(churned),
        "churn_rate_30d": monthly_churn,
        "churn_rate_90d": quarterly_churn,
        "mrr_lost": round(mrr_lost, 2),
        "churn_by_reason": reasons,
        "avg_risk_score": round(
            sum(c.get("risk_score", 0) for c in active) / len(active), 2
        ) if active else 0
    }


def cmd_list(args):
    data = load_data()
    customers = data.get("customers", [])
    if args.status:
        customers = [c for c in customers if c.get("status") == args.status]
    print(f"\n{'ID':<4} {'Name':<25} {'Risk':>5} {'Status':<10} {'Plan':>8}")
    print("-" * 60)
    for c in customers:
        print(f"{c.get('id',''):<4} {c.get('name',''):<25} "
              f"{c.get('risk_score',0):>5.1f} {c.get('status','active'):<10} "
              f"${c.get('plan_amount',0):>7.2f}")


def cmd_analysis(args):
    analysis = get_churn_analysis()
    print(f"\n{'='*50}")
    print(f"  CHURN ANALYSIS REPORT")
    print(f"{'='*50}")
    print(f"  Total Customers    : {analysis['total_customers']}")
    print(f"  Active Customers   : {analysis['active_customers']}")
    print(f"  Churned Customers  : {analysis['churned_customers']}")
    print(f"  Churn Rate (30d)   : {analysis['churn_rate_30d']}%")
    print(f"  Churn Rate (90d)   : {analysis['churn_rate_90d']}%")
    print(f"  MRR Lost           : ${analysis['mrr_lost']:.2f}")
    print(f"  Avg Risk Score     : {analysis['avg_risk_score']}")
    print(f"\n  Churn by Reason:")
    for reason, count in analysis["churn_by_reason"].items():
        print(f"    {reason}: {count}")
    print(f"{'='*50}")


def cmd_at_risk(args):
    at_risk = get_at_risk_customers(args.threshold)
    if not at_risk:
        print(f"No customers with risk score >= {args.threshold}")
        return
    print(f"\nAt-Risk Customers (risk >= {args.threshold})")
    print(f"{'ID':<4} {'Name':<25} {'Risk':>5} {'Last Activity':<15} {'Plan':>8}")
    print("-" * 65)
    for c in at_risk:
        print(f"{c.get('id',''):<4} {c.get('name',''):<25} "
              f"{c.get('risk_score',0):>5.1f} {c.get('last_activity',''):<15} "
              f"${c.get('plan_amount',0):>7.2f}")


def cmd_add(args):
    c = add_customer(args.name, args.join_date, args.plan, args.risk, args.customer_id)
    print(f"Added customer: {c['name']} (ID: {c['id']})")


def cmd_churn(args):
    result = record_churn(args.customer_id, args.reason, args.date)
    if result:
        print(f"Recorded churn for customer {args.customer_id}: {args.reason}")
    else:
        print(f"Customer {args.customer_id} not found.")


def cmd_risk(args):
    result = update_risk_score(args.customer_id, args.score)
    if result:
        print(f"Updated risk score for {result['name']}: {args.score}")
    else:
        print(f"Customer {args.customer_id} not found.")


def main():
    parser = argparse.ArgumentParser(description="SaaS Churn Analyser")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("list", help="List customers").set_defaults(func=cmd_list)
    p_list = subparsers.choices["list"]
    p_list.add_argument("--status", help="Filter: active/churned")

    subparsers.add_parser("analysis", help="Full churn analysis").set_defaults(func=cmd_analysis)
    subparsers.add_parser("at-risk", help="Show at-risk customers").set_defaults(func=cmd_at_risk)

    p_ar = subparsers.choices["at-risk"]
    p_ar.add_argument("--threshold", type=float, default=50, help="Risk score threshold")

    p_add = subparsers.add_parser("add", help="Add a customer")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--join-date", dest="join_date", required=True, help="YYYY-MM-DD")
    p_add.add_argument("--plan", type=float, required=True)
    p_add.add_argument("--risk", type=float, default=0, dest="risk")
    p_add.add_argument("--customer-id", type=int, dest="customer_id")
    p_add.set_defaults(func=cmd_add)

    p_churn = subparsers.add_parser("churn", help="Record churn")
    p_churn.add_argument("--customer-id", type=int, required=True)
    p_churn.add_argument("--reason", default="")
    p_churn.add_argument("--date", help="Churn date YYYY-MM-DD")
    p_churn.set_defaults(func=cmd_churn)

    p_risk = subparsers.add_parser("risk", help="Update risk score")
    p_risk.add_argument("--customer-id", type=int, required=True)
    p_risk.add_argument("--score", type=float, required=True)
    p_risk.set_defaults(func=cmd_risk)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
