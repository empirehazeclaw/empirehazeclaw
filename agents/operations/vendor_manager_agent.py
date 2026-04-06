#!/usr/bin/env python3
"""
🤝 Vendor Manager Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Manages vendor relationships, contracts, and performance.
Features:
- Vendor database (CRM-style)
- Contract management
- Performance scoring (quality, price, reliability, support)
- Payment tracking
- Renewal reminders
- RFP/procurement workflow
- Vendor categorization (strategic, preferred, approved, on-hold)
- Spend analytics per vendor

Usage:
  python3 operations/vendor_manager_agent.py --help
  python3 operations/vendor_manager_agent.py add_vendor --name "Acme Cloud" --category "cloud" --contact "Max@acme.com" --contract-value 12000
  python3 operations/vendor_manager_agent.py list_vendors
  python3 operations/vendor_manager_agent.py score --vendor-id 0 --quality 5 --price 4 --reliability 5 --support 4
  python3 operations/vendor_manager_agent.py contract --vendor-id 0 --show
  python3 operations/vendor_manager_agent.py renewals --days 90
  python3 operations/vendor_manager_agent.py spend_report
  python3 operations/vendor_manager_agent.py payment --vendor-id 0 --amount 1200 --type subscription --status paid
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ─── PATHS ────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR  = WORKSPACE / "data"
LOGS_DIR  = WORKSPACE / "logs"
VENDOR_DIR = DATA_DIR / "vendors"

for d in [DATA_DIR, LOGS_DIR, VENDOR_DIR]:
    d.mkdir(parents=True, exist_ok=True)

VENDORS_FILE    = VENDOR_DIR / "vendors.json"
CONTRACTS_FILE  = VENDOR_DIR / "contracts.json"
PAYMENTS_FILE   = VENDOR_DIR / "payments.json"
SCORES_FILE     = VENDOR_DIR / "scores.json"
ALERTS_FILE     = VENDOR_DIR / "alerts.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [VENDOR_MGR] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "vendor_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("vendor_manager")

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_json(path, default):
    try: return json.loads(path.read_text())
    except: return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def parse_date(s: str) -> str:
    for fmt in ["%Y-%m-%d", "%d.%m.%Y"]:
        try:
            return datetime.strptime(s.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s

# ─── CATEGORIES & STATUS ──────────────────────────────────────────────────────
VENDOR_CATEGORIES = [
    "cloud", "saas", "hosting", "development", "marketing", "advertising",
    "accounting", "hr", "legal", "office", "it_hardware", "logistics",
    "payment", "security", "analytics", "crm", "email", "other",
]

VENDOR_STATUSES = [
    "prospect", "active", "preferred", "on_hold", "terminated", "inactive",
]

CONTRACT_TYPES = [
    "subscription", "perpetual", "usage_based", "time_materials",
    "fixed_price", " retainer", "enterprise", "open_source",
]

PAYMENT_TYPES  = ["subscription", "one_time", "invoice", "metered", "retainer", "refund"]
PAYMENT_STATUS = ["pending", "paid", "overdue", "cancelled", "disputed"]

# ─── PERFORMANCE SCORING ────────────────────────────────────────────────────
def calculate_vendor_score(vendor_id: int) -> Dict:
    scores = [s for s in load_json(SCORES_FILE, []) if s.get("vendor_id") == vendor_id]
    if not scores:
        return {"score": None, "grade": "N/A", "count": 0}

    avg_quality      = sum(s.get("quality", 0) for s in scores) / len(scores)
    avg_price        = sum(s.get("price", 0) for s in scores) / len(scores)
    avg_reliability  = sum(s.get("reliability", 0) for s in scores) / len(scores)
    avg_support      = sum(s.get("support", 0) for s in scores) / len(scores)

    # Weighted overall (quality + reliability most important)
    overall = avg_quality * 0.30 + avg_price * 0.20 + avg_reliability * 0.30 + avg_support * 0.20

    if overall >= 4.5: grade = "A+"
    elif overall >= 4.0: grade = "A"
    elif overall >= 3.5: grade = "B+"
    elif overall >= 3.0: grade = "B"
    elif overall >= 2.5: grade = "C"
    elif overall >= 2.0: grade = "D"
    else: grade = "F"

    return {
        "score": round(overall, 2),
        "grade": grade,
        "quality": round(avg_quality, 2),
        "price": round(avg_price, 2),
        "reliability": round(avg_reliability, 2),
        "support": round(avg_support, 2),
        "count": len(scores),
    }

# ─── ALERTS ───────────────────────────────────────────────────────────────────
def create_alert(vendor_id: int, alert_type: str, message: str, severity: str = "info"):
    alerts = load_json(ALERTS_FILE, [])
    new_id = max([a.get("id", -1) for a in alerts], default=-1) + 1
    alerts.append({
        "id": new_id, "vendor_id": vendor_id, "type": alert_type,
        "message": message, "severity": severity,
        "acknowledged": False, "created_at": datetime.now().isoformat(),
    })
    save_json(ALERTS_FILE, alerts)
    logger.info(f"Alert [{alert_type}]: {message}")

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_add_vendor(args) -> int:
    """Add a new vendor."""
    vendors = load_json(VENDORS_FILE, [])
    new_id = max([v.get("id", -1) for v in vendors], default=-1) + 1

    vendor = {
        "id": new_id,
        "name": args.name,
        "category": args.category,
        "status": "active",
        "website": args.website or "",
        "contact_name": args.contact_name or "",
        "contact_email": args.contact or "",
        "phone": args.phone or "",
        "address": args.address or "",
        "contract_value_annual": args.contract_value or 0,
        "payment_terms_days": args.payment_terms or 30,
        "tax_id": args.tax_id or "",
        "notes": args.notes or "",
        "tags": args.tags.split(",") if args.tags else [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    vendors.append(vendor)
    save_json(VENDORS_FILE, vendors)
    logger.info(f"Added vendor: {vendor['name']} (ID: {new_id})")

    print(f"✅ Vendor added (ID: {new_id}): {vendor['name']}")
    print(f"   Category: {vendor['category']} | Status: {vendor['status']}")
    print(f"   Contact: {vendor['contact_name']} <{vendor['contact_email']}>")
    print(f"   Annual Contract: €{vendor['contract_value_annual']:,.2f}")
    return 0


def cmd_list_vendors(args) -> int:
    """List all vendors."""
    vendors = load_json(VENDORS_FILE, [])
    if not vendors:
        print("No vendors. Add one with: add_vendor")
        return 0

    filters = {}
    if args.category:
        filters["category"] = args.category
    if args.status:
        filters["status"] = args.status

    filtered = vendors
    for k, v in filters.items():
        filtered = [f for f in filtered if f.get(k) == v]

    print(f"\n🤝 Vendor Database")
    print(f"{'='*90}")
    print(f"{'ID':>3} | {'Name':<25} | {'Category':<12} | {'Status':<12} | {'Annual €':>10} | {'Grade'}")
    print("-" * 90)
    for v in sorted(filtered, key=lambda x: x.get("name", "")):
        score = calculate_vendor_score(v["id"])
        grade = score.get("grade", "N/A")
        name = v["name"][:23] + ".." if len(v["name"]) > 25 else v["name"]
        print(f"{v['id']:>3} | {name:<25} | {v.get('category','?'):<12} | {v.get('status','?'):<12} | €{v.get('contract_value_annual',0):>9,.0f} | {grade}")
    print(f"\nTotal: {len(filtered)} vendor(s) | Total Annual Spend: €{sum(v.get('contract_value_annual',0) for v in filtered):,.2f}")
    return 0


def cmd_score(args) -> int:
    """Rate/score a vendor."""
    scores = load_json(SCORES_FILE, [])
    new_id = max([s.get("id", -1) for s in scores], default=-1) + 1

    score = {
        "id": new_id,
        "vendor_id": int(args.vendor_id),
        "quality": args.quality,
        "price": args.price,
        "reliability": args.reliability,
        "support": args.support,
        "notes": args.notes or "",
        "rated_by": "manual",
        "created_at": datetime.now().isoformat(),
    }
    scores.append(score)
    save_json(SCORES_FILE, scores)

    # Recalculate overall
    overall = calculate_vendor_score(int(args.vendor_id))

    vendors = load_json(VENDORS_FILE, [])
    try:
        vendor = next(v for v in vendors if v["id"] == int(args.vendor_id))
    except StopIteration:
        print(f"Vendor ID {args.vendor_id} not found")
        return 1

    # Auto-update status based on score
    if overall["score"] is not None:
        if overall["score"] >= 4.0 and vendor.get("status") == "active":
            vendor["status"] = "preferred"
        elif overall["score"] < 2.5 and vendor.get("status") != "on_hold":
            create_alert(vendor["id"], "low_score", f"Vendor '{vendor['name']}' scored {overall['score']}/5 — consider review", "warning")
        save_json(VENDORS_FILE, vendors)

    print(f"✅ Score recorded for {vendor['name']} (ID: {vendor['id']})")
    print(f"\n  Scores: Quality={args.quality} | Price={args.price} | Reliability={args.reliability} | Support={args.support}")
    if overall["score"] is not None:
        print(f"\n  📊 Overall Score: {overall['score']}/5 (Grade: {overall['grade']})")
        print(f"     Based on {overall['count']} rating(s)")
    return 0


def cmd_contract(args) -> int:
    """Manage vendor contracts."""
    contracts = load_json(CONTRACTS_FILE, [])

    if args.action == "show":
        vendor_contracts = [c for c in contracts if c.get("vendor_id") == int(args.vendor_id)]
        if not vendor_contracts:
            print(f"No contracts found for vendor ID {args.vendor_id}")
            return 0

        vendors = load_json(VENDORS_FILE, [])
        vendor = next((v for v in vendors if v["id"] == int(args.vendor_id)), {"name": "?"})
        print(f"\n📄 Contracts: {vendor['name']}")
        print(f"{'='*60}")
        for c in sorted(vendor_contracts, key=lambda x: x.get("start_date", ""), reverse=True):
            print(f"\n  Contract: {c.get('title', 'Untitled')}")
            print(f"  Type: {c.get('contract_type','?')} | Value: €{c.get('value',0):,.2f}")
            print(f"  Period: {c.get('start_date','?')} → {c.get('end_date','?')}")
            print(f"  Auto-renew: {'Yes' if c.get('auto_renew') else 'No'}")
            if c.get("notice_days"):
                print(f"  Notice Period: {c['notice_days']} days")
        return 0

    elif args.action == "add":
        vendors = load_json(VENDORS_FILE, [])
        try:
            vendor = next(v for v in vendors if v["id"] == int(args.vendor_id))
        except StopIteration:
            print(f"Vendor ID {args.vendor_id} not found")
            return 1

        new_id = max([c.get("id", -1) for c in contracts], default=-1) + 1
        contract = {
            "id": new_id,
            "vendor_id": int(args.vendor_id),
            "title": args.title,
            "contract_type": args.contract_type or "subscription",
            "value": float(args.value or 0),
            "start_date": parse_date(args.start_date) if args.start_date else datetime.now().strftime("%Y-%m-%d"),
            "end_date": parse_date(args.end_date) if args.end_date else (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "auto_renew": args.auto_renew,
            "notice_days": int(args.notice_days or 30),
            "description": args.description or "",
            "created_at": datetime.now().isoformat(),
        }
        contracts.append(contract)
        save_json(CONTRACTS_FILE, contracts)

        # Alert for renewal
        renewal_date = datetime.strptime(contract["end_date"], "%Y-%m-%d") - timedelta(days=int(args.notice_days or 30))
        if renewal_date > datetime.now():
            create_alert(
                int(args.vendor_id), "contract_expiring",
                f"Contract '{args.title}' expires {contract['end_date']} — renewal due by {renewal_date.strftime('%Y-%m-%d')}",
                "info",
            )

        print(f"✅ Contract added (ID: {new_id}): {args.title}")
        print(f"   Period: {contract['start_date']} → {contract['end_date']}")
        print(f"   Value: €{contract['value']:,.2f} | Notice: {contract['notice_days']} days")
        return 0


def cmd_renewals(args) -> int:
    """Show upcoming contract renewals."""
    contracts = load_json(CONTRACTS_FILE, [])
    vendors = load_json(VENDORS_FILE, [])
    vendor_map = {v["id"]: v for v in vendors}
    threshold = datetime.now() + timedelta(days=args.days)

    upcoming = []
    for c in contracts:
        if not c.get("end_date"):
            continue
        try:
            end = datetime.strptime(c["end_date"], "%Y-%m-%d")
            if datetime.now() < end < threshold:
                v = vendor_map.get(c.get("vendor_id"), {"name": "?"})
                days_left = (end - datetime.now()).days
                upcoming.append((c, v, days_left))
        except:
            continue

    if not upcoming:
        print(f"✅ No contracts expiring in the next {args.days} days")
        return 0

    print(f"\n📅 Contract Renewals (next {args.days} days)")
    print(f"{'='*65}")
    for c, v, days in sorted(upcoming, key=lambda x: x[2]):
        urgency = "🔴" if days < 14 else ("🟡" if days < 30 else "🟢")
        print(f"  {urgency} [{days} days] {v.get('name','?')} | {c.get('title','?')}")
        print(f"     Value: €{c.get('value',0):,.2f} | Ends: {c['end_date']} | Notice: {c.get('notice_days',30)} days")

    total_value = sum(c.get("value", 0) for c, _, _ in upcoming)
    print(f"\n  Total renewal value at risk: €{total_value:,.2f}")
    return 0


def cmd_payment(args) -> int:
    """Log a payment to a vendor."""
    payments = load_json(PAYMENTS_FILE, [])

    if args.action == "list":
        vendor_payments = [p for p in payments if p.get("vendor_id") == int(args.vendor_id)]
        if not vendor_payments:
            print(f"No payments found for vendor ID {args.vendor_id}")
            return 0
        vendors = load_json(VENDORS_FILE, [])
        vendor = next((v for v in vendors if v["id"] == int(args.vendor_id)), {"name": "?"})
        print(f"\n💳 Payments: {vendor['name']}")
        print(f"{'='*60}")
        for p in sorted(vendor_payments, key=lambda x: x.get("date", ""), reverse=True):
            status_icon = {"paid": "✅", "pending": "⏳", "overdue": "🔴", "cancelled": "❌"}.get(p.get("status",""), " ")
            print(f"  {status_icon} {p.get('date','?')} | €{p.get('amount',0):>9,.2f} | {p.get('payment_type','?')} | {p.get('status','?')}")
        total_paid = sum(p.get("amount", 0) for p in vendor_payments if p.get("status") == "paid")
        print(f"\n  Total Paid: €{total_paid:,.2f}")
        return 0

    elif args.action == "add":
        new_id = max([p.get("id", -1) for p in payments], default=-1) + 1
        payment = {
            "id": new_id,
            "vendor_id": int(args.vendor_id),
            "amount": float(args.amount or 0),
            "payment_type": args.payment_type or "subscription",
            "status": args.status or "pending",
            "date": parse_date(args.date) if args.date else datetime.now().strftime("%Y-%m-%d"),
            "description": args.description or "",
            "created_at": datetime.now().isoformat(),
        }
        payments.append(payment)
        save_json(PAYMENTS_FILE, payments)
        logger.info(f"Payment logged: €{payment['amount']} to vendor {args.vendor_id} ({payment['status']})")
        print(f"✅ Payment logged (ID: {new_id}): €{payment['amount']:,.2f} — {payment['status']}")
        return 0


def cmd_spend_report(args) -> int:
    """Vendor spend analytics."""
    vendors = load_json(VENDORS_FILE, [])
    payments = load_json(PAYMENTS_FILE, [])
    contracts = load_json(CONTRACTS_FILE, [])

    if not vendors:
        print("No vendor data.")
        return 0

    # Spend per vendor
    spend = {}
    for p in payments:
        if p.get("status") in ("paid", "pending"):
            vid = p.get("vendor_id")
            spend[vid] = spend.get(vid, 0) + p.get("amount", 0)

    # Sort by spend
    vendor_spend = []
    for v in vendors:
        vid = v["id"]
        score = calculate_vendor_score(vid)
        contract_val = v.get("contract_value_annual", 0)
        paid_spend = sum(p.get("amount", 0) for p in payments if p.get("vendor_id") == vid and p.get("status") == "paid")
        vendor_spend.append({
            **v,
            "total_paid": paid_spend,
            "contract_annual": contract_val,
            "score": score,
        })

    vendor_spend.sort(key=lambda x: x["total_paid"], reverse=True)

    print(f"\n💰 Vendor Spend Report")
    print(f"{'='*75}")
    print(f"{'Vendor':<25} | {'Category':<10} | {'Paid €':>10} | {'Contract €':>10} | {'Grade':<5}")
    print("-" * 75)
    for v in vendor_spend:
        name = v["name"][:23] + ".." if len(v["name"]) > 25 else v["name"]
        grade = v["score"].get("grade", "N/A")
        print(f"{name:<25} | {v.get('category','?'):<10} | €{v['total_paid']:>9,.0f} | €{v['contract_annual']:>9,.0f} | {grade:<5}")

    total_spend = sum(v["total_paid"] for v in vendor_spend)
    total_contract = sum(v["contract_annual"] for v in vendor_spend)
    print("-" * 75)
    print(f"{'TOTAL':<25} | {'':<10} | €{total_spend:>9,.0f} | €{total_contract:>9,.0f} |")

    # Category breakdown
    by_cat = {}
    for v in vendor_spend:
        cat = v.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + v["total_paid"]

    print(f"\n  Spend by Category:")
    for cat, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        pct = amt / total_spend * 100 if total_spend else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"    {cat:<20}: €{amt:>10,.0f} ({pct:5.1f}%)  [{bar}]")
    return 0


def cmd_alerts(args) -> int:
    """Show vendor alerts."""
    alerts = load_json(ALERTS_FILE, [])
    if args.unack_only:
        alerts = [a for a in alerts if not a.get("acknowledged")]

    if not alerts:
        print("✅ No alerts")
        return 0

    vendors = load_json(VENDORS_FILE, [])
    vendor_map = {v["id"]: v["name"] for v in vendors}

    print(f"\n🚨 Vendor Alerts ({len(alerts)} total, {len([a for a in alerts if not a.get('acknowledged')])} unacknowledged)")
    print(f"{'='*65}")
    for a in sorted(alerts, key=lambda x: x.get("created_at", ""), reverse=True):
        v_name = vendor_map.get(a.get("vendor_id"), "?")
        ack = "✅" if a.get("acknowledged") else "❌"
        sev = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(a.get("severity", "info"), " ")
        print(f"  {ack}{sev} [{a['type']}] {v_name}: {a['message'][:50]}")
        print(f"     {a['created_at'][:19]}")
    return 0


def cmd_rfp(args) -> int:
    """Generate RFP document for vendor procurement."""
    prompt = f"""Erstelle ein professionelles Request for Proposal (RFP) Dokument für:

Kategorie: {args.category or 'General Services/Software'}
Unternehmen: EmpireHazeClaw
Anzahl Angebote: {args.count or 3}
Frist: {args.deadline or (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}

Das RFP soll enthalten:
1. Deckblatt und TOC
2. Unternehmensvorstellung (EmpireHazeClaw)
3. Projekt-/Bedarfsbeschreibung
4. Technische Anforderungen (Must-haves)
5. Gewichtungskriterien (Preis, Qualität, Support, Timeline)
6. Gewichtung: Kosten {args.price_weight or 40}%, Qualität {args.quality_weight or 30}%, Support {args.support_weight or 20}%, Timeline {args.timeline_weight or 10}%
7. Bieterfragen
8. Angebotsformat
9. Zeitplan (Submission → Evaluation → Decision)
10. Vertragsbedingungen

Gib das komplette RFP als Markdown aus."""

    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=2048,
            system="Du bist ein Procurement- und Business-Experte.",
            messages=[{"role": "user", "content": prompt}],
        )
        rfp = response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"LLM unavailable: {e}")
        rfp = "[RFP generation failed - LLM unavailable]"

    ts = datetime.now().strftime("%Y%m%d")
    out_file = VENDOR_DIR / f"RFP_{re.sub(r'[^a-zA-Z0-9]', '_', args.category or 'general')}_{ts}.md"
    out_file.write_text(f"# Request for Proposal: {args.category or 'General'}\n\n**Erstellt:** {datetime.now().isoformat()}\n**Deadline:** {args.deadline or '30 days'}\n\n---\n\n{rfp}", encoding="utf-8")
    logger.info(f"RFP saved: {out_file}")

    print(f"✅ RFP generated: {out_file}")
    print(f"\n{'='*60}")
    print(rfp[:2000])
    print(f"{'='*60}")
    return 0


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="operations/vendor_manager_agent.py",
        description="🤝 Vendor Manager — Vendor relationships, contracts & spend analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 operations/vendor_manager_agent.py add_vendor --name "AWS" --category "cloud" --contact "enterprise@aws.amazon.com" --contract-value 24000 --payment-terms 30
  python3 operations/vendor_manager_agent.py list_vendors
  python3 operations/vendor_manager_agent.py list_vendors --category cloud --status active
  python3 operations/vendor_manager_agent.py score --vendor-id 0 --quality 5 --price 4 --reliability 5 --support 4 --notes "Excellent service"
  python3 operations/vendor_manager_agent.py contract show --vendor-id 0
  python3 operations/vendor_manager_agent.py contract add --vendor-id 0 --title "AWS Enterprise Agreement" --value 24000 --start-date 2024-01-01 --end-date 2025-01-01 --auto-renew --notice-days 60
  python3 operations/vendor_manager_agent.py renewals --days 90
  python3 operations/vendor_manager_agent.py payment list --vendor-id 0
  python3 operations/vendor_manager_agent.py payment add --vendor-id 0 --amount 2000 --type subscription --status paid --date 2024-02-01
  python3 operations/vendor_manager_agent.py spend_report
  python3 operations/vendor_manager_agent.py alerts
  python3 operations/vendor_manager_agent.py rfp --category "Cloud Infrastructure" --count 5 --deadline 2026-04-30
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add_vendor", help="Add a vendor")
    p.add_argument("--name", required=True)
    p.add_argument("--category", required=True, choices=VENDOR_CATEGORIES)
    p.add_argument("--contact", default="", help="Contact email")
    p.add_argument("--contact-name", default="")
    p.add_argument("--phone", default="")
    p.add_argument("--website", default="")
    p.add_argument("--address", default="")
    p.add_argument("--contract-value", type=float, default=0)
    p.add_argument("--payment-terms", type=int, default=30)
    p.add_argument("--tax-id", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--notes", default="")

    p = sub.add_parser("list_vendors", help="List vendors")
    p.add_argument("--category", default="")
    p.add_argument("--status", default="")

    p = sub.add_parser("score", help="Rate a vendor")
    p.add_argument("--vendor-id", required=True, type=int)
    p.add_argument("--quality",     type=int, required=True, choices=[1,2,3,4,5])
    p.add_argument("--price",       type=int, required=True, choices=[1,2,3,4,5])
    p.add_argument("--reliability", type=int, required=True, choices=[1,2,3,4,5])
    p.add_argument("--support",     type=int, required=True, choices=[1,2,3,4,5])
    p.add_argument("--notes", default="")

    p = sub.add_parser("contract", help="Manage contracts")
    p.add_argument("--action",    required=True, choices=["show", "add"])
    p.add_argument("--vendor-id",  required=True, type=int)
    p.add_argument("--title",     default="")
    p.add_argument("--contract-type", default="subscription", choices=CONTRACT_TYPES)
    p.add_argument("--value",      default="0")
    p.add_argument("--start-date", default="")
    p.add_argument("--end-date",   default="")
    p.add_argument("--auto-renew", action="store_true")
    p.add_argument("--notice-days", default="30")
    p.add_argument("--description", default="")

    p = sub.add_parser("renewals", help="Show upcoming renewals")
    p.add_argument("--days", type=int, default=90)

    p = sub.add_parser("payment", help="Manage payments")
    p.add_argument("--action",    required=True, choices=["list", "add"])
    p.add_argument("--vendor-id", required=True, type=int)
    p.add_argument("--amount",    default="0")
    p.add_argument("--payment-type", default="subscription", choices=PAYMENT_TYPES)
    p.add_argument("--status",    default="pending", choices=PAYMENT_STATUS)
    p.add_argument("--date",      default="")
    p.add_argument("--description", default="")

    p = sub.add_parser("spend_report", help="Vendor spend analytics")

    p = sub.add_parser("alerts", help="Show vendor alerts")
    p.add_argument("--unack-only", action="store_true")

    p = sub.add_parser("rfp", help="Generate RFP document")
    p.add_argument("--category", default="General Services")
    p.add_argument("--count", type=int, default=3)
    p.add_argument("--deadline", default="")
    p.add_argument("--price-weight", type=int, default=40)
    p.add_argument("--quality-weight", type=int, default=30)
    p.add_argument("--support-weight", type=int, default=20)
    p.add_argument("--timeline-weight", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "add_vendor": cmd_add_vendor,
        "list_vendors": cmd_list_vendors,
        "score": cmd_score,
        "contract": cmd_contract,
        "renewals": cmd_renewals,
        "payment": cmd_payment,
        "spend_report": cmd_spend_report,
        "alerts": cmd_alerts,
        "rfp": cmd_rfp,
    }
    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
