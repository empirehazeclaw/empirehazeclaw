#!/usr/bin/env python3
"""
Affiliate Tracker Agent
Tracks affiliate partners, commissions, referral links, and payouts.
Data: JSON files in data/ecommerce/affiliates/
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "affiliates"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

AFFILIATES_FILE = DATA_DIR / "affiliates.json"
REFERRALS_FILE = DATA_DIR / "referrals.json"
PAYOUTS_FILE = DATA_DIR / "payouts.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "affiliate_tracker.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("AffiliateTracker")


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
    if not AFFILIATES_FILE.exists():
        save_json(AFFILIATES_FILE, {})
    if not REFERRALS_FILE.exists():
        save_json(REFERRALS_FILE, [])
    if not PAYOUTS_FILE.exists():
        save_json(PAYOUTS_FILE, [])


def cmd_add_affiliate(args):
    affiliates = load_json(AFFILIATES_FILE, {})
    if args.affiliate_id in affiliates:
        print(f"⚠️  Affiliate ID '{args.affiliate_id}' already exists.")
        return 1
    now = datetime.now().isoformat()
    affiliates[args.affiliate_id] = {
        "affiliate_id": args.affiliate_id,
        "name": args.name,
        "email": args.email,
        "platform": args.platform or "general",
        "commission_rate": args.commission_rate,
        "commission_type": args.commission_type or "percentage",
        "referral_code": args.referral_code or args.affiliate_id.upper(),
        "payout_threshold": args.payout_threshold or 50.0,
        "payout_method": args.payout_method or "bank_transfer",
        "total_referred": 0,
        "total_sales": 0.0,
        "total_commission": 0.0,
        "total_paid": 0.0,
        "active": True,
        "created_at": now,
        "updated_at": now,
    }
    save_json(AFFILIATES_FILE, affiliates)
    logger.info(f"Added affiliate {args.affiliate_id}: {args.name}")
    print(f"✅ Affiliate '{args.name}' (ID: {args.affiliate_id}) added.")
    print(f"   Commission: {args.commission_rate}% ({args.commission_type}) | Code: {affiliates[args.affiliate_id]['referral_code']}")
    return 0


def cmd_list_affiliates(args):
    affiliates = load_json(AFFILIATES_FILE, {})
    if not affiliates:
        print("No affiliates found.")
        return 0
    if args.platform:
        affiliates = {k: v for k, v in affiliates.items() if v.get("platform") == args.platform}
    print(f"{'ID':<15} {'Name':<22} {'Platform':<12} {'Rate':>6} {'Referred':>8} {'Sales':>12} {'Commission':>11} {'Paid':>10}")
    print("-" * 100)
    for aid, a in sorted(affiliates.items(), key=lambda x: x[1].get("total_commission", 0), reverse=True):
        status = "🟢" if a.get("active", True) else "⚫"
        print(f"{aid:<15} {a.get('name',''):<22} {a.get('platform',''):<12} {a.get('commission_rate',0):>5.1f}% {a.get('total_referred',0):>8} ${a.get('total_sales',0):>11.2f} ${a.get('total_commission',0):>10.2f} ${a.get('total_paid',0):>9.2f} {status}")
    print("-" * 100)
    return 0


def cmd_register_referral(args):
    affiliates = load_json(AFFILIATES_FILE, {})
    referrals = load_json(REFERRALS_FILE, [])
    code_to_id = {a.get("referral_code", ""): aid for aid, a in affiliates.items()}
    affiliate_id = code_to_id.get(args.code)
    if not affiliate_id:
        print(f"❌ Referral code '{args.code}' not found.")
        return 1
    now = datetime.now().isoformat()
    sale_amount = args.sale_amount
    commission_rate = affiliates[affiliate_id].get("commission_rate", 0)
    if affiliates[affiliate_id].get("commission_type") == "percentage":
        commission = sale_amount * commission_rate / 100
    else:
        commission = commission_rate
    referral = {
        "referral_id": args.referral_id or f"REF-{now[:10]}-{args.code}",
        "affiliate_id": affiliate_id,
        "code": args.code,
        "sale_amount": sale_amount,
        "commission": commission,
        "status": "pending",
        "customer_email": args.customer_email or "",
        "order_id": args.order_id or "",
        "created_at": now,
        "paid_at": "",
    }
    referrals.append(referral)
    save_json(REFERRALS_FILE, referrals)
    a = affiliates[affiliate_id]
    a["total_referred"] = a.get("total_referred", 0) + 1
    a["total_sales"] = a.get("total_sales", 0) + sale_amount
    a["total_commission"] = a.get("total_commission", 0) + commission
    a["updated_at"] = now
    save_json(AFFILIATES_FILE, affiliates)
    logger.info(f"Referral registered: {args.code} -> ${commission:.2f} commission")
    print(f"✅ Referral registered for affiliate '{a['name']}'.")
    print(f"   Sale: ${sale_amount:.2f} | Commission: ${commission:.2f} ({commission_rate}% {a.get('commission_type')})")
    return 0


def cmd_list_referrals(args):
    referrals = load_json(REFERRALS_FILE, [])
    if args.affiliate_id:
        referrals = [r for r in referrals if r.get("affiliate_id") == args.affiliate_id]
    if args.status:
        referrals = [r for r in referrals if r.get("status") == args.status]
    if not referrals:
        print("No referrals found.")
        return 0
    print(f"\n{'ReferralID':<20} {'Affiliate':<18} {'Sale':>10} {'Commission':>11} {'Status':<12} {'Date':<26}")
    print("-" * 105)
    for r in sorted(referrals, key=lambda x: x.get("created_at", ""), reverse=True)[:args.limit]:
        print(f"{r.get('referral_id',''):<20} {r.get('affiliate_id',''):<18} ${r.get('sale_amount',0):>9.2f} ${r.get('commission',0):>10.2f} {r.get('status',''):<12} {r.get('created_at','')[:26]}")
    print("-" * 105)
    total_sales = sum(r.get("sale_amount", 0) for r in referrals)
    total_comm = sum(r.get("commission", 0) for r in referrals)
    print(f"Total: {len(referrals)} referrals | Sales: ${total_sales:.2f} | Commissions: ${total_comm:.2f}")
    return 0


def cmd_mark_paid(args):
    referrals = load_json(REFERRALS_FILE, [])
    found = False
    for r in referrals:
        if r["referral_id"] == args.referral_id:
            r["status"] = "paid"
            r["paid_at"] = datetime.now().isoformat()
            found = True
            break
    if not found:
        print(f"❌ Referral '{args.referral_id}' not found.")
        return 1
    save_json(REFERRALS_FILE, referrals)
    print(f"✅ Referral '{args.referral_id}' marked as paid.")
    return 0


def cmd_payout(args):
    affiliates = load_json(AFFILIATES_FILE, {})
    referrals = load_json(REFERRALS_FILE, [])
    payouts = load_json(PAYOUTS_FILE, [])
    pending_refs = [r for r in referrals if r.get("affiliate_id") == args.affiliate_id and r.get("status") == "pending"]
    if not pending_refs:
        print("No pending referrals to pay out.")
        return 1
    total = sum(r.get("commission", 0) for r in pending_refs)
    affiliate = affiliates.get(args.affiliate_id)
    if not affiliate:
        print(f"❌ Affiliate '{args.affiliate_id}' not found.")
        return 1
    if total < affiliate.get("payout_threshold", 50.0):
        print(f"⚠️  Total ${total:.2f} is below payout threshold ${affiliate['payout_threshold']:.2f}.")
        return 1
    payout = {
        "payout_id": f"PAY-{datetime.now().strftime('%Y%m%d')}-{args.affiliate_id[:6]}",
        "affiliate_id": args.affiliate_id,
        "amount": total,
        "method": args.method or affiliate.get("payout_method", "bank_transfer"),
        "referral_count": len(pending_refs),
        "status": "paid",
        "created_at": datetime.now().isoformat(),
    }
    payouts.append(payout)
    save_json(PAYOUTS_FILE, payouts)
    for r in pending_refs:
        r["status"] = "paid"
        r["paid_at"] = datetime.now().isoformat()
    save_json(REFERRALS_FILE, referrals)
    a = affiliates[args.affiliate_id]
    a["total_paid"] = a.get("total_paid", 0) + total
    a["updated_at"] = datetime.now().isoformat()
    save_json(AFFILIATES_FILE, affiliates)
    logger.info(f"Payout {payout['payout_id']}: ${total:.2f} to {args.affiliate_id}")
    print(f"✅ Payout {payout['payout_id']} created: ${total:.2f} to '{a['name']}' ({len(pending_refs)} referrals)")
    return 0


def cmd_stats(args):
    affiliates = load_json(AFFILIATES_FILE, {})
    referrals = load_json(REFERRALS_FILE, [])
    payouts = load_json(PAYOUTS_FILE, [])
    total_sales = sum(r.get("sale_amount", 0) for r in referrals)
    total_commission = sum(r.get("commission", 0) for r in referrals)
    total_paid = sum(p.get("amount", 0) for p in payouts)
    pending_commission = sum(r.get("commission", 0) for r in referrals if r.get("status") == "pending")
    print("\n📊 AFFILIATE STATISTICS")
    print(f"  Total Affiliates:    {len(affiliates)}")
    print(f"  Total Referrals:     {len(referrals)}")
    print(f"  Total Sales:         ${total_sales:,.2f}")
    print(f"  Total Commission:    ${total_commission:,.2f}")
    print(f"  Total Paid Out:     ${total_paid:,.2f}")
    print(f"  Pending Commission: ${pending_commission:,.2f}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="affiliate-tracker",
        description="🔗 Affiliate Tracker Agent — Track affiliates, referrals, and commissions.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-affiliate", help="Add new affiliate partner")
    p.add_argument("--affiliate-id", required=True, help="Unique affiliate ID")
    p.add_argument("--name", required=True, help="Affiliate name")
    p.add_argument("--email", required=True, help="Affiliate email")
    p.add_argument("--platform", help="Platform (e.g. tiktok, instagram, blog)")
    p.add_argument("--commission-rate", type=float, required=True, help="Commission rate (%% or $)")
    p.add_argument("--commission-type", choices=["percentage", "fixed"], default="percentage", help="Commission type")
    p.add_argument("--referral-code", help="Referral code (default: affiliate-id uppercase)")
    p.add_argument("--payout-threshold", type=float, help="Minimum payout threshold")
    p.add_argument("--payout-method", help="Payout method")

    p = sub.add_parser("list-affiliates", help="List all affiliates")
    p.add_argument("--platform", help="Filter by platform")

    p = sub.add_parser("register-referral", help="Register a new referral/sale")
    p.add_argument("--referral-id", help="Referral ID (auto-generated if omitted)")
    p.add_argument("--code", required=True, help="Referral code used")
    p.add_argument("--sale-amount", type=float, required=True, help="Sale amount ($)")
    p.add_argument("--customer-email", help="Customer email")
    p.add_argument("--order-id", help="Related order ID")

    p = sub.add_parser("list-referrals", help="List referrals")
    p.add_argument("--affiliate-id", help="Filter by affiliate")
    p.add_argument("--status", choices=["pending", "paid"], help="Filter by status")
    p.add_argument("--limit", type=int, default=50, help="Max records")

    p = sub.add_parser("mark-paid", help="Mark a referral as paid")
    p.add_argument("--referral-id", required=True, help="Referral ID")

    p = sub.add_parser("payout", help="Process payout for an affiliate")
    p.add_argument("--affiliate-id", required=True, help="Affiliate ID")
    p.add_argument("--method", help="Payout method override")

    p = sub.add_parser("stats", help="Show affiliate statistics")

    args = parser.parse_args()
    init_files()
    commands = {
        "add-affiliate": cmd_add_affiliate,
        "list-affiliates": cmd_list_affiliates,
        "register-referral": cmd_register_referral,
        "list-referrals": cmd_list_referrals,
        "mark-paid": cmd_mark_paid,
        "payout": cmd_payout,
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
