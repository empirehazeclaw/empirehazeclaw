#!/usr/bin/env python3
"""
Campaign Analytics Agent — EmpireHazeClaw Marketing System
Tracks, aggregates, and reports on marketing campaign performance.
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CAMPAIGNS_DIR = DATA_DIR / "campaigns"
ANALYTICS_FILE = CAMPAIGNS_DIR / "analytics.json"
METRICS_FILE = CAMPAIGNS_DIR / "metrics.csv"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGNS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CAMPAIGN-ANALYTICS] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "campaign_analytics.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("campaign_analytics")


# ── Data Layer ────────────────────────────────────────────────────────────────
def load_analytics() -> dict:
    if ANALYTICS_FILE.exists():
        try:
            return json.loads(ANALYTICS_FILE.read_text())
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load analytics.json: %s", e)
    return {"campaigns": {}, "updated": datetime.now(timezone.utc).isoformat()}


def save_analytics(data: dict) -> None:
    data["updated"] = datetime.now(timezone.utc).isoformat()
    ANALYTICS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_metrics_csv() -> list:
    rows = []
    if METRICS_FILE.exists():
        try:
            with open(METRICS_FILE, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            log.warning("Could not read metrics.csv: %s", e)
    return rows


def save_metrics_csv(rows: list) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(METRICS_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ts() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Campaign CRUD ──────────────────────────────────────────────────────────────
def cmd_create(args: argparse.Namespace) -> None:
    data = load_analytics()
    cid = args.id or f"campaign_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if cid in data["campaigns"]:
        log.error("Campaign '%s' already exists", cid)
        sys.exit(1)

    campaign = {
        "id": cid,
        "name": args.name,
        "channel": args.channel,
        "status": "active",
        "budget": float(args.budget) if args.budget else 0.0,
        "spent": 0.0,
        "start_date": args.start_date or ts(),
        "end_date": args.end_date or None,
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "revenue": 0.0,
            "leads": 0,
        },
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "notes": args.notes or "",
        "created": ts(),
    }
    data["campaigns"][cid] = campaign
    save_analytics(data)
    print(f"✅ Campaign '{cid}' created: {args.name}")
    log.info("Campaign created: %s", cid)


def cmd_list(args: argparse.Namespace) -> None:
    data = load_analytics()
    campaigns = data.get("campaigns", {})

    if args.status:
        campaigns = {k: v for k, v in campaigns.items() if v.get("status") == args.status}
    if args.channel:
        campaigns = {k: v for k, v in campaigns.items() if v.get("channel") == args.channel}

    if not campaigns:
        print("No campaigns found.")
        return

    print(f"{'ID':<30} {'NAME':<25} {'CHANNEL':<12} {'STATUS':<10} {'SPENT':>10} {'CONV':>6}")
    print("-" * 100)
    for c in sorted(campaigns.values(), key=lambda x: x.get("created", ""), reverse=True):
        m = c.get("metrics", {})
        print(
            f"{c['id']:<30} {c.get('name',''):<25} {c.get('channel',''):<12} "
            f"{c.get('status',''):<10} ${c.get('spent',0):>9.2f} {m.get('conversions',0):>6}"
        )


def cmd_update(args: argparse.Namespace) -> None:
    data = load_analytics()
    cid = args.id
    if cid not in data["campaigns"]:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    c = data["campaigns"][cid]
    if args.status:
        c["status"] = args.status
    if args.budget:
        c["budget"] = float(args.budget)
    if args.spent:
        c["spent"] = float(args.spent)
    if args.end_date:
        c["end_date"] = args.end_date
    if args.notes:
        c["notes"] = args.notes

    save_analytics(data)
    print(f"✅ Campaign '{cid}' updated.")
    log.info("Campaign updated: %s", cid)


def cmd_delete(args: argparse.Namespace) -> None:
    data = load_analytics()
    cid = args.id
    if cid not in data["campaigns"]:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    del data["campaigns"][cid]
    save_analytics(data)
    print(f"🗑️  Campaign '{cid}' deleted.")
    log.info("Campaign deleted: %s", cid)


# ── Metrics ───────────────────────────────────────────────────────────────────
def cmd_log(args: argparse.Namespace) -> None:
    """Log a metrics event to CSV and update campaign."""
    data = load_analytics()
    cid = args.campaign_id

    if cid not in data["campaigns"]:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    row = {
        "timestamp": ts(),
        "campaign_id": cid,
        "impressions": args.impressions or 0,
        "clicks": args.clicks or 0,
        "conversions": args.conversions or 0,
        "revenue": args.revenue or 0.0,
        "leads": args.leads or 0,
        "spend": args.spend or 0.0,
        "channel": args.channel or data["campaigns"][cid].get("channel", ""),
    }

    rows = load_metrics_csv()
    rows.append(row)
    save_metrics_csv(rows)

    # Update campaign totals
    c = data["campaigns"][cid]
    m = c.setdefault("metrics", {})
    m["impressions"] = m.get("impressions", 0) + int(row["impressions"])
    m["clicks"] = m.get("clicks", 0) + int(row["clicks"])
    m["conversions"] = m.get("conversions", 0) + int(row["conversions"])
    m["revenue"] = m.get("revenue", 0.0) + float(row["revenue"])
    m["leads"] = m.get("leads", 0) + int(row["leads"])
    c["spent"] = c.get("spent", 0.0) + float(row["spend"])

    save_analytics(data)
    print(f"✅ Metrics logged for '{cid}': +{row['impressions']} impressions, +{row['clicks']} clicks, +{row['conversions']} conv")
    log.info("Metrics logged for %s", cid)


def cmd_report(args: argparse.Namespace) -> None:
    """Generate performance report for one or all campaigns."""
    data = load_analytics()

    if args.campaign_id:
        if args.campaign_id not in data["campaigns"]:
            log.error("Campaign '%s' not found", args.campaign_id)
            sys.exit(1)
        campaigns = {args.campaign_id: data["campaigns"][args.campaign_id]}
    else:
        campaigns = data.get("campaigns", {})

    if not campaigns:
        print("No campaigns to report on.")
        return

    report = {}
    for cid, c in campaigns.items():
        m = c.get("metrics", {})
        impressions = m.get("impressions", 0)
        clicks = m.get("clicks", 0)
        conversions = m.get("conversions", 0)
        revenue = m.get("revenue", 0.0)
        spent = c.get("spent", 0.0)

        ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
        conv_rate = (conversions / clicks * 100) if clicks > 0 else 0.0
        cpa = (spent / conversions) if conversions > 0 else 0.0
        roas = (revenue / spent) if spent > 0 else 0.0

        report[cid] = {
            "name": c.get("name"),
            "channel": c.get("channel"),
            "status": c.get("status"),
            "budget": c.get("budget", 0.0),
            "spent": spent,
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "ctr_percent": round(ctr, 2),
            "conv_rate_percent": round(conv_rate, 2),
            "cpa": round(cpa, 2),
            "roas": round(roas, 2),
        }

    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"CAMPAIGN PERFORMANCE REPORT — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"{'='*80}")
        for cid, r in report.items():
            print(f"\n📊 {cid} — {r['name']} ({r['channel']}) [{r['status']}]")
            print(f"   Budget: ${r['budget']:.2f} | Spent: ${r['spent']:.2f}")
            print(f"   Impressions: {r['impressions']:,} | Clicks: {r['clicks']:,} | CTR: {r['ctr_percent']}%")
            print(f"   Conversions: {r['conversions']:,} | Conv Rate: {r['conv_rate_percent']}%")
            print(f"   Revenue: ${r['revenue']:.2f} | CPA: ${r['cpa']:.2f} | ROAS: {r['roas']:.2f}x")

    log.info("Report generated for %d campaign(s)", len(report))


def cmd_health(args: argparse.Namespace) -> None:
    """Overall marketing health dashboard."""
    data = load_analytics()
    campaigns = data.get("campaigns", {})

    total_impressions = sum(c.get("metrics", {}).get("impressions", 0) for c in campaigns.values())
    total_clicks = sum(c.get("metrics", {}).get("clicks", 0) for c in campaigns.values())
    total_conversions = sum(c.get("metrics", {}).get("conversions", 0) for c in campaigns.values())
    total_revenue = sum(c.get("metrics", {}).get("revenue", 0.0) for c in campaigns.values())
    total_spent = sum(c.get("spent", 0.0) for c in campaigns.values())
    active = sum(1 for c in campaigns.values() if c.get("status") == "active")

    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_roas = (total_revenue / total_spent) if total_spent > 0 else 0

    print(f"\n{'='*60}")
    print(f"MARKETING HEALTH DASHBOARD — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    print(f"  Total Campaigns : {len(campaigns)}")
    print(f"  Active          : {active}")
    print(f"  Total Spend     : ${total_spent:,.2f}")
    print(f"  Total Revenue   : ${total_revenue:,.2f}")
    print(f"  Overall ROAS    : {overall_roas:.2f}x")
    print(f"  Total Impress.  : {total_impressions:,}")
    print(f"  Total Clicks    : {total_clicks:,}")
    print(f"  Overall CTR     : {overall_ctr:.2f}%")
    print(f"  Total Convers.  : {total_conversions:,}")
    print(f"{'='*60}\n")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="campaign_analytics_agent.py",
        description="EmpireHazeClaw Campaign Analytics — track and report on marketing campaigns.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # create
    p_c = sub.add_parser("create", help="Create a new campaign")
    p_c.add_argument("--id", help="Campaign ID (auto-generated if omitted)")
    p_c.add_argument("--name", required=True, help="Campaign name")
    p_c.add_argument("--channel", required=True, choices=["email", "sms", "push", "social", "ads", "seo", "other"], help="Channel")
    p_c.add_argument("--budget", help="Total budget (USD)")
    p_c.add_argument("--start-date", dest="start_date", help="Start date (ISO)")
    p_c.add_argument("--end-date", dest="end_date", help="End date (ISO)")
    p_c.add_argument("--tags", help="Comma-separated tags")
    p_c.add_argument("--notes", help="Campaign notes")
    p_c.set_defaults(fn=cmd_create)

    # list
    p_l = sub.add_parser("list", help="List campaigns")
    p_l.add_argument("--status", help="Filter by status (active/paused/ended)")
    p_l.add_argument("--channel", help="Filter by channel")
    p_l.set_defaults(fn=cmd_list)

    # update
    p_u = sub.add_parser("update", help="Update campaign fields")
    p_u.add_argument("--id", required=True, help="Campaign ID")
    p_u.add_argument("--status", choices=["active", "paused", "ended"])
    p_u.add_argument("--budget", help="New budget (USD)")
    p_u.add_argument("--spent", help="Add spent amount (USD)")
    p_u.add_argument("--end-date", dest="end_date", help="End date (ISO)")
    p_u.add_argument("--notes", help="Update notes")
    p_u.set_defaults(fn=cmd_update)

    # delete
    p_d = sub.add_parser("delete", help="Delete a campaign")
    p_d.add_argument("--id", required=True, help="Campaign ID")
    p_d.set_defaults(fn=cmd_delete)

    # log
    p_m = sub.add_parser("log", help="Log metrics event")
    p_m.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_m.add_argument("--impressions", type=int)
    p_m.add_argument("--clicks", type=int)
    p_m.add_argument("--conversions", type=int)
    p_m.add_argument("--revenue", type=float)
    p_m.add_argument("--leads", type=int)
    p_m.add_argument("--spend", type=float)
    p_m.add_argument("--channel")
    p_m.set_defaults(fn=cmd_log)

    # report
    p_r = sub.add_parser("report", help="Generate performance report")
    p_r.add_argument("--campaign-id", dest="campaign_id", help="Specific campaign ID (all if omitted)")
    p_r.add_argument("--format", default="text", choices=["text", "json"])
    p_r.set_defaults(fn=cmd_report)

    # health
    p_h = sub.add_parser("health", help="Overall marketing health dashboard")
    p_h.set_defaults(fn=cmd_health)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
