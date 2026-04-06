#!/usr/bin/env python3
"""
SaaS Customer Health Agent
Scores and tracks customer health based on usage, engagement, and support metrics.
Reads/Writes: data/customer_health.json
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
        logging.FileHandler(LOG_DIR / "customer_health.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CustomerHealth")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/customer_health.json")


def load_data():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "customers": [],
            "history": [],
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


def calculate_health_score(metrics):
    """
    Calculate health score (0-100) from metrics dict:
      - login_frequency: days since last login (0-30 → 0-30 points)
      - feature_adoption: % of features used (0-100 → 0-30 points)
      - support_tickets: number of open tickets (0 → 20, 1-2 → 10, 3+ → 0)
      - nps_score: NPS score (0-10 → 0-20 points)
    """
    score = 0
    # Login frequency (30 points max)
    days_since = metrics.get("days_since_login", 0)
    login_pts = max(0, 30 - days_since)
    score += login_pts

    # Feature adoption (30 points max)
    adoption = metrics.get("feature_adoption_pct", 0)
    score += min(30, adoption * 0.30)

    # Support tickets (20 points max)
    tickets = metrics.get("open_support_tickets", 0)
    if tickets == 0:
        score += 20
    elif tickets <= 2:
        score += 10
    # 3+ tickets = 0 points

    # NPS score (20 points max)
    nps = metrics.get("nps_score", 0)
    score += min(20, nps * 2)

    return min(100, max(0, round(score, 1)))


def health_label(score):
    if score >= 80:
        return "Healthy"
    elif score >= 60:
        return "Moderate"
    elif score >= 40:
        return "At Risk"
    else:
        return "Critical"


def add_customer(name, plan_tier, customer_id=None):
    """Register a new customer."""
    data = load_data()
    cid = customer_id or len(data["customers"]) + 1
    customer = {
        "id": cid,
        "name": name,
        "plan_tier": plan_tier,
        "status": "active",
        "health_score": 50,
        "health_label": "Moderate",
        "last_updated": datetime.utcnow().isoformat(),
        "metrics": {
            "days_since_login": 0,
            "feature_adoption_pct": 0,
            "open_support_tickets": 0,
            "nps_score": 0
        }
    }
    data["customers"].append(customer)
    save_data(data)
    logger.info(f"Added customer: {name}, initial health: 50")
    return customer


def update_metrics(customer_id, days_since_login=None, feature_adoption_pct=None,
                    open_support_tickets=None, nps_score=None):
    """Update customer health metrics and recalculate score."""
    data = load_data()
    for c in data["customers"]:
        if c["id"] == int(customer_id):
            m = c["metrics"]
            if days_since_login is not None:
                m["days_since_login"] = days_since_login
            if feature_adoption_pct is not None:
                m["feature_adoption_pct"] = min(100, max(0, feature_adoption_pct))
            if open_support_tickets is not None:
                m["open_support_tickets"] = max(0, open_support_tickets)
            if nps_score is not None:
                m["nps_score"] = min(10, max(0, nps_score))

            old_score = c["health_score"]
            new_score = calculate_health_score(m)
            c["health_score"] = new_score
            c["health_label"] = health_label(new_score)
            c["last_updated"] = datetime.utcnow().isoformat()

            # Record history
            data["history"].append({
                "customer_id": int(customer_id),
                "timestamp": datetime.utcnow().isoformat(),
                "old_score": old_score,
                "new_score": new_score,
                "metrics": dict(m)
            })
            save_data(data)
            logger.info(f"Updated {c['name']}: health {old_score} → {new_score}")
            return c
    return None


def get_health_report():
    """Generate overall health report."""
    data = load_data()
    active = [c for c in data["customers"] if c.get("status") == "active"]
    if not active:
        return {"avg_health": 0, "healthy": 0, "moderate": 0, "at_risk": 0, "critical": 0}

    scores = [c["health_score"] for c in active]
    avg = sum(scores) / len(scores)
    labels = {"healthy": 0, "moderate": 0, "at_risk": 0, "critical": 0}
    for c in active:
        lbl = c.get("health_label", "Moderate").lower().replace(" ", "_")
        labels[lbl] = labels.get(lbl, 0) + 1

    return {
        "avg_health": round(avg, 1),
        "total_active": len(active),
        "healthy": labels["healthy"],
        "moderate": labels["moderate"],
        "at_risk": labels["at_risk"],
        "critical": labels["critical"],
    }


def cmd_list(args):
    data = load_data()
    customers = data.get("customers", [])
    if args.status:
        customers = [c for c in customers if c.get("status") == args.status]
    print(f"\n{'ID':<4} {'Name':<25} {'Health':>6} {'Label':<10} {'Tier':<10}")
    print("-" * 60)
    for c in customers:
        print(f"{c.get('id',''):<4} {c.get('name',''):<25} "
              f"{c.get('health_score',0):>6.1f} {c.get('health_label',''):<10} "
              f"{c.get('plan_tier',''):<10}")


def cmd_report(args):
    report = get_health_report()
    print(f"\n{'='*50}")
    print(f"  CUSTOMER HEALTH REPORT")
    print(f"{'='*50}")
    print(f"  Total Active       : {report['total_active']}")
    print(f"  Average Health     : {report['avg_health']}")
    print(f"  Healthy (80+)      : {report['healthy']}")
    print(f"  Moderate (60-79)  : {report['moderate']}")
    print(f"  At Risk (40-59)    : {report['at_risk']}")
    print(f"  Critical (<40)    : {report['critical']}")
    print(f"{'='*50}")


def cmd_update(args):
    kwargs = {}
    if args.login_days is not None:
        kwargs["days_since_login"] = args.login_days
    if args.adoption is not None:
        kwargs["feature_adoption_pct"] = args.adoption
    if args.tickets is not None:
        kwargs["open_support_tickets"] = args.tickets
    if args.nps is not None:
        kwargs["nps_score"] = args.nps
    result = update_metrics(args.customer_id, **kwargs)
    if result:
        print(f"Updated {result['name']}: score={result['health_score']}, label={result['health_label']}")
    else:
        print(f"Customer {args.customer_id} not found.")


def cmd_detail(args):
    data = load_data()
    for c in data["customers"]:
        if c["id"] == int(args.customer_id):
            print(f"\nCustomer: {c['name']} (ID: {c['id']})")
            print(f"  Plan Tier   : {c.get('plan_tier','')}")
            print(f"  Status      : {c.get('status','active')}")
            print(f"  Health Score: {c['health_score']} ({c['health_label']})")
            print(f"  Last Updated: {c.get('last_updated','')}")
            m = c.get("metrics", {})
            print(f"  Metrics:")
            print(f"    Days since login     : {m.get('days_since_login',0)}")
            print(f"    Feature adoption     : {m.get('feature_adoption_pct',0)}%")
            print(f"    Open support tickets : {m.get('open_support_tickets',0)}")
            print(f"    NPS score            : {m.get('nps_score',0)}")
            return
    print(f"Customer {args.customer_id} not found.")


def cmd_add(args):
    c = add_customer(args.name, args.tier, args.customer_id)
    print(f"Added: {c['name']} (ID: {c['id']})")


def main():
    parser = argparse.ArgumentParser(description="SaaS Customer Health Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    subparsers.add_parser("list", help="List all customers").set_defaults(func=cmd_list)
    p_list = subparsers.choices["list"]
    p_list.add_argument("--status", help="Filter by status")

    subparsers.add_parser("report", help="Overall health report").set_defaults(func=cmd_report)
    subparsers.add_parser("detail", help="Customer detail").set_defaults(func=cmd_detail)

    p_det = subparsers.choices["detail"]
    p_det.add_argument("customer_id", type=int)

    p_upd = subparsers.add_parser("update", help="Update customer metrics")
    p_upd.add_argument("--customer-id", type=int, required=True)
    p_upd.add_argument("--login-days", type=int, dest="login_days")
    p_upd.add_argument("--adoption", type=int, help="Feature adoption %%")
    p_upd.add_argument("--tickets", type=int, help="Open support tickets")
    p_upd.add_argument("--nps", type=int, help="NPS score 0-10")
    p_upd.set_defaults(func=cmd_update)

    p_add = subparsers.add_parser("add", help="Add a customer")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--tier", required=True, help="Plan tier")
    p_add.add_argument("--customer-id", type=int, dest="customer_id")
    p_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
