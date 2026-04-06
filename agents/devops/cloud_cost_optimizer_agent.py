#!/usr/bin/env python3
"""
DevOps Cloud Cost Optimizer Agent
Analyses and optimises cloud costs across AWS/GCP/Azure resources.
Generates savings recommendations based on usage patterns.
Reads/Writes: data/cloud_costs.json
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
        logging.FileHandler(LOG_DIR / "cloud_cost_optimizer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CloudCostOptimizer")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/cloud_costs.json")


def load_data():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "resources": [],
            "invoices": [],
            "recommendations": [],
            "providers": [],
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


def add_resource(name, resource_type, provider, region, monthly_cost, tags=None, instance_size=""):
    """Add a cloud resource record."""
    data = load_data()
    rid = len(data["resources"]) + 1
    resource = {
        "id": rid,
        "name": name,
        "type": resource_type,
        "provider": provider.lower(),
        "region": region,
        "instance_size": instance_size,
        "monthly_cost": float(monthly_cost),
        "status": "active",
        "tags": tags or {},
        "added_date": datetime.utcnow().date().isoformat(),
        "optimisation_potential": 0.0
    }
    data["resources"].append(resource)
    save_data(data)
    logger.info(f"Added resource: {name} ({provider}) - ${monthly_cost}/mo")
    return resource


def remove_resource(resource_id):
    """Remove/archive a resource."""
    data = load_data()
    for r in data["resources"]:
        if r["id"] == int(resource_id):
            r["status"] = "removed"
            r["removed_date"] = datetime.utcnow().isoformat()
            save_data(data)
            logger.info(f"Removed resource: {r['name']}")
            return r
    return None


def generate_recommendations():
    """Analyse resources and generate cost optimisation recommendations."""
    data = load_data()
    recommendations = []

    # Reserved instance opportunities (>=$100/mo on-demand)
    for r in data.get("resources", []):
        if r.get("status") != "active":
            continue
        cost = r.get("monthly_cost", 0)
        if cost >= 500:
            recommendations.append({
                "id": len(recommendations) + 1,
                "resource_id": r["id"],
                "resource_name": r["name"],
                "type": "reserved_instance",
                "priority": "high",
                "savings_estimate": round(cost * 0.30, 2),
                "description": f"Consider Reserved/Spot Instances for {r['name']} ({r['type']}) "
                               f"costing ${cost}/mo. Potential: ${cost * 0.3:.2f}/mo."
            })
        elif cost >= 100:
            recommendations.append({
                "id": len(recommendations) + 1,
                "resource_id": r["id"],
                "resource_name": r["name"],
                "type": "reserved_instance",
                "priority": "medium",
                "savings_estimate": round(cost * 0.30, 2),
                "description": f"Consider Reserved/Spot for {r['name']}. "
                               f"Potential savings: ${cost * 0.3:.2f}/mo."
            })

        # Large instances that could be downsized
        size = r.get("instance_size", "").lower()
        if any(x in size for x in ["xlarge", "2xlarge", "4xlarge", "8xlarge"]) and cost >= 200:
            recommendations.append({
                "id": len(recommendations) + 1,
                "resource_id": r["id"],
                "resource_name": r["name"],
                "type": "downsize",
                "priority": "medium",
                "savings_estimate": round(cost * 0.25, 2),
                "description": f"Large instance {r['name']} ({size}) may be oversized. "
                               f"Potential savings: ${cost * 0.25:.2f}/mo."
            })

        # Storage cleanup candidates
        rtype = r.get("type", "").lower()
        if rtype in ("snapshot", "backup", "volume", "storage") and cost >= 50:
            recommendations.append({
                "id": len(recommendations) + 1,
                "resource_id": r["id"],
                "resource_name": r["name"],
                "type": "cleanup",
                "priority": "low",
                "savings_estimate": round(cost * 0.10, 2),
                "description": f"Storage resource {r['name']} may be unused. Review for cleanup. "
                               f"Potential: ${cost * 0.1:.2f}/mo."
            })

    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
    data["recommendations"] = recommendations
    save_data(data)
    logger.info(f"Generated {len(recommendations)} recommendations")
    return recommendations


def calculate_total_costs():
    """Calculate total costs by provider and type."""
    data = load_data()
    totals = {"total": 0.0, "by_provider": {}, "by_type": {}}

    for r in data.get("resources", []):
        if r.get("status") != "active":
            continue
        cost = r.get("monthly_cost", 0)
        totals["total"] += cost
        p = r.get("provider", "unknown")
        totals["by_provider"][p] = totals["by_provider"].get(p, 0) + cost
        t = r.get("type", "unknown")
        totals["by_type"][t] = totals["by_type"].get(t, 0) + cost

    totals["annual_projection"] = round(totals["total"] * 12, 2)
    totals["quarterly_projection"] = round(totals["total"] * 3, 2)
    return totals


def add_invoice(provider, amount, period_start, period_end, currency="USD"):
    """Record a cloud provider invoice."""
    data = load_data()
    invoice = {
        "id": len(data.get("invoices", [])) + 1,
        "provider": provider.lower(),
        "amount": float(amount),
        "currency": currency.upper(),
        "period_start": period_start,
        "period_end": period_end,
        "added_date": datetime.utcnow().isoformat()
    }
    if "invoices" not in data:
        data["invoices"] = []
    data["invoices"].append(invoice)
    save_data(data)
    logger.info(f"Added invoice: {provider} {currency} {amount}")
    return invoice


def cmd_add(args):
    add_resource(args.name, args.type, args.provider, args.region,
                 args.cost, {}, args.size)
    print(f"Added resource: {args.name}")


def cmd_remove(args):
    result = remove_resource(args.id)
    if result:
        print(f"Removed resource ID {args.id}: {result['name']}")
    else:
        print(f"Resource ID {args.id} not found.")


def cmd_list(args):
    data = load_data()
    resources = data.get("resources", [])
    if args.provider:
        resources = [r for r in resources if r.get("provider") == args.provider.lower()]
    if args.status:
        resources = [r for r in resources if r.get("status") == args.status]
    if not resources:
        print("No resources found.")
        return
    print(f"\n{'ID':<4} {'Name':<30} {'Provider':<10} {'Type':<15} {'Region':<12} {'Cost/mo':>10}")
    print("-" * 95)
    for r in resources:
        print(f"{r.get('id',''):<4} {r.get('name',''):<30} {r.get('provider',''):<10} "
              f"{r.get('type',''):<15} {r.get('region',''):<12} "
              f"${r.get('monthly_cost',0):>9.2f}")


def cmd_costs(args):
    totals = calculate_total_costs()
    print(f"\n{'='*55}")
    print(f"  CLOUD COST REPORT")
    print(f"{'='*55}")
    print(f"  Total Monthly Cost  : ${totals['total']:.2f}")
    print(f"  Quarterly Projection: ${totals['quarterly_projection']:.2f}")
    print(f"  Annual Projection   : ${totals['annual_projection']:.2f}")
    print(f"\n  By Provider:")
    for provider, cost in sorted(totals["by_provider"].items()):
        print(f"    {provider.capitalize():<12}: ${cost:.2f}/mo")
    print(f"\n  By Type:")
    for rtype, cost in sorted(totals["by_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"    {rtype:<20}: ${cost:.2f}/mo")
    print(f"{'='*55}")


def cmd_recommend(args):
    recs = generate_recommendations()
    if not recs:
        print("No recommendations generated. Add resources first.")
        return
    print(f"\nCost Optimisation Recommendations ({len(recs)} found)")
    print(f"{'#':<4} {'Priority':<10} {'Type':<20} {'Savings/mo':>12} {'Resource'}")
    print("-" * 75)
    total_savings = 0
    for r in recs:
        print(f"{r['id']:<4} {r['priority']:<10} {r['type']:<20} "
              f"${r['savings_estimate']:>10.2f} {r['resource_name']}")
        total_savings += r["savings_estimate"]
    print("-" * 75)
    print(f"{'Total Potential Monthly Savings':<40} ${total_savings:.2f}")
    print(f"{'Annual Savings Projection':<40} ${total_savings * 12:.2f}")


def cmd_invoice(args):
    invoice = add_invoice(args.provider, args.amount, args.period_start,
                           args.period_end, args.currency)
    print(f"Added invoice: {invoice['provider']} {invoice['currency']} {invoice['amount']}")


def cmd_invoices(args):
    data = load_data()
    invoices = data.get("invoices", [])
    if not invoices:
        print("No invoices recorded.")
        return
    print(f"\n{'ID':<4} {'Provider':<12} {'Amount':>12} {'Period':<30}")
    print("-" * 65)
    for inv in invoices[-20:]:
        period = f"{inv.get('period_start','')} -> {inv.get('period_end','')}"
        print(f"{inv.get('id',''):<4} {inv.get('provider',''):<12} "
              f"{inv.get('currency','USD')} {inv.get('amount',0):>10.2f} {period:<30}")


def main():
    parser = argparse.ArgumentParser(description="Cloud Cost Optimizer Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_add = subparsers.add_parser("add", help="Add a cloud resource")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--type", required=True, help="Resource type (ec2, s3, rds, etc)")
    p_add.add_argument("--provider", required=True, choices=["aws", "gcp", "azure", "other"])
    p_add.add_argument("--region", default="us-east-1")
    p_add.add_argument("--cost", type=float, required=True, help="Monthly cost")
    p_add.add_argument("--size", default="", help="Instance size (e.g. t3.medium)")
    p_add.set_defaults(func=cmd_add)

    p_rem = subparsers.add_parser("remove", help="Remove a resource")
    p_rem.add_argument("id", type=int)
    p_rem.set_defaults(func=cmd_remove)

    p_list = subparsers.add_parser("list", help="List all resources")
    p_list.add_argument("--provider")
    p_list.add_argument("--status")
    p_list.set_defaults(func=cmd_list)

    subparsers.add_parser("costs", help="Cost summary report").set_defaults(func=cmd_costs)

    subparsers.add_parser("recommend", help="Generate optimisation recommendations").set_defaults(func=cmd_recommend)

    p_inv = subparsers.add_parser("invoice", help="Add an invoice")
    p_inv.add_argument("--provider", required=True)
    p_inv.add_argument("--amount", type=float, required=True)
    p_inv.add_argument("--period-start", dest="period_start", required=True)
    p_inv.add_argument("--period-end", dest="period_end", required=True)
    p_inv.add_argument("--currency", default="USD")
    p_inv.set_defaults(func=cmd_invoice)

    subparsers.add_parser("invoices", help="List invoices").set_defaults(func=cmd_invoices)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
