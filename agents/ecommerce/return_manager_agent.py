#!/usr/bin/env python3
"""
Return Manager Agent
Manages product returns: request, approval, refund, restocking.
Data: JSON files in data/ecommerce/returns/
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "ecommerce" / "returns"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

RETURNS_FILE = DATA_DIR / "returns.json"
POLICY_FILE = DATA_DIR / "policy.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "return_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("ReturnManager")

VALID_REASONS = ["defective", "wrong_item", "not_as_described", "changed_mind", "damaged_in_transit", "other"]
VALID_STATUSES = ["requested", "approved", "rejected", "received", "refunded", "restocked", "closed"]


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
    if not RETURNS_FILE.exists():
        save_json(RETURNS_FILE, [])
    if not POLICY_FILE.exists():
        save_json(POLICY_FILE, {
            "return_window_days": 30,
            "restocking_fee_percent": 0.0,
            "refund_method": "original_payment",
            "require_original_packaging": False,
            "auto_approve_threshold": 0.0,
        })


def _generate_return_id():
    return f"RET-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"


def cmd_request(args):
    returns = load_json(RETURNS_FILE, [])
    now = datetime.now().isoformat()
    return_entry = {
        "return_id": _generate_return_id(),
        "order_id": args.order_id,
        "sku": args.sku,
        "product_name": args.product_name or args.sku,
        "quantity": args.quantity or 1,
        "reason": args.reason,
        "reason_detail": args.reason_detail or "",
        "customer_email": args.customer_email,
        "refund_amount": args.refund_amount or 0.0,
        "status": "requested",
        "restocking_fee": 0.0,
        "requested_at": now,
        "approved_at": "",
        "received_at": "",
        "refunded_at": "",
        "notes": args.notes or "",
    }
    returns.append(return_entry)
    save_json(RETURNS_FILE, returns)
    logger.info(f"Return requested: {return_entry['return_id']} for order {args.order_id}")
    print(f"✅ Return request created: {return_entry['return_id']}")
    print(f"   Order: {args.order_id} | SKU: {args.sku} | Qty: {args.quantity} | Reason: {args.reason}")
    return 0


def cmd_approve(args):
    returns = load_json(RETURNS_FILE, [])
    found = False
    for r in returns:
        if r["return_id"] == args.return_id:
            if r["status"] != "requested":
                print(f"⚠️  Return is already '{r['status']}', not 'requested'.")
                return 1
            r["status"] = "approved"
            r["approved_at"] = datetime.now().isoformat()
            r["notes"] = (r.get("notes", "") + f" | Approved: {args.note}" if args.note else r.get("notes", ""))
            found = True
            break
    if not found:
        print(f"❌ Return '{args.return_id}' not found.")
        return 1
    save_json(RETURNS_FILE, returns)
    print(f"✅ Return '{args.return_id}' approved.")
    return 0


def cmd_reject(args):
    returns = load_json(RETURNS_FILE, [])
    found = False
    for r in returns:
        if r["return_id"] == args.return_id:
            if r["status"] != "requested":
                print(f"⚠️  Return is already '{r['status']}', not 'requested'.")
                return 1
            r["status"] = "rejected"
            r["notes"] = (r.get("notes", "") + f" | Rejected: {args.reason}" if args.reason else r.get("notes", ""))
            found = True
            break
    if not found:
        print(f"❌ Return '{args.return_id}' not found.")
        return 1
    save_json(RETURNS_FILE, returns)
    print(f"❌ Return '{args.return_id}' rejected. Reason: {args.reason or 'not specified'}")
    return 0


def cmd_receive(args):
    returns = load_json(RETURNS_FILE, [])
    policy = load_json(POLICY_FILE, {})
    found = False
    for r in returns:
        if r["return_id"] == args.return_id:
            if r["status"] not in ("approved", "requested"):
                print(f"⚠️  Return status is '{r['status']}', expected 'approved' or 'requested'.")
                return 1
            r["status"] = "received"
            r["received_at"] = datetime.now().isoformat()
            r["notes"] = (r.get("notes", "") + f" | Received" if r.get("notes") else "Received")
            if args.condition:
                r["item_condition"] = args.condition
            restocking_fee_pct = policy.get("restocking_fee_percent", 0.0)
            if restocking_fee_pct > 0:
                r["restocking_fee"] = round(r["refund_amount"] * restocking_fee_pct / 100, 2)
            found = True
            break
    if not found:
        print(f"❌ Return '{args.return_id}' not found.")
        return 1
    save_json(RETURNS_FILE, returns)
    print(f"✅ Return '{args.return_id}' received and logged.")
    return 0


def cmd_refund(args):
    returns = load_json(RETURNS_FILE, [])
    found = False
    for r in returns:
        if r["return_id"] == args.return_id:
            if r["status"] not in ("received", "approved"):
                print(f"⚠️  Return status is '{r['status']}', expected 'received'.")
                return 1
            r["status"] = "refunded"
            r["refunded_at"] = datetime.now().isoformat()
            refund_amount = r["refund_amount"]
            restocking = r.get("restocking_fee", 0.0)
            actual_refund = max(0, refund_amount - restocking)
            r["actual_refund"] = actual_refund
            if args.method:
                r["refund_method"] = args.method
            found = True
            break
    if not found:
        print(f"❌ Return '{args.return_id}' not found.")
        return 1
    save_json(RETURNS_FILE, returns)
    print(f"✅ Return '{args.return_id}' refunded: ${actual_refund:.2f}")
    return 0


def cmd_list(args):
    returns = load_json(RETURNS_FILE, [])
    if args.status:
        returns = [r for r in returns if r.get("status") == args.status]
    if args.order_id:
        returns = [r for r in returns if r.get("order_id") == args.order_id]
    if not returns:
        print("No returns found.")
        return 0
    print(f"\n{'ReturnID':<22} {'OrderID':<18} {'SKU':<14} {'Qty':>4} {'Reason':<22} {'Refund':>9} {'Status':<12}")
    print("-" * 110)
    for r in sorted(returns, key=lambda x: x.get("requested_at", ""), reverse=True):
        print(f"{r.get('return_id',''):<22} {r.get('order_id',''):<18} {r.get('sku',''):<14} {r.get('quantity',0):>4} {r.get('reason',''):<22} ${r.get('refund_amount',0):>8.2f} {r.get('status',''):<12}")
    print("-" * 110)
    print(f"Showing {len(returns)} return(s)")
    return 0


def cmd_show(args):
    returns = load_json(RETURNS_FILE, [])
    r = next((x for x in returns if x.get("return_id") == args.return_id), None)
    if not r:
        print(f"❌ Return '{args.return_id}' not found.")
        return 1
    print(f"\n📋 Return: {r['return_id']}")
    print(f"  Order ID:         {r.get('order_id')}")
    print(f"  SKU:              {r.get('sku')}")
    print(f"  Product:          {r.get('product_name')}")
    print(f"  Quantity:         {r.get('quantity')}")
    print(f"  Reason:           {r.get('reason')}")
    print(f"  Reason Detail:    {r.get('reason_detail','')}")
    print(f"  Refund Amount:    ${r.get('refund_amount', 0):.2f}")
    print(f"  Restocking Fee:  ${r.get('restocking_fee', 0):.2f}")
    print(f"  Actual Refund:    ${r.get('actual_refund', 0):.2f}")
    print(f"  Status:           {r.get('status','').upper()}")
    print(f"  Customer:         {r.get('customer_email','')}")
    print(f"  Requested:       {r.get('requested_at','')}")
    print(f"  Approved:        {r.get('approved_at','')}")
    print(f"  Received:        {r.get('received_at','')}")
    print(f"  Refunded:        {r.get('refunded_at','')}")
    if r.get("notes"):
        print(f"  Notes:            {r['notes']}")
    return 0


def cmd_stats(args):
    returns = load_json(RETURNS_FILE, [])
    if not returns:
        print("No returns.")
        return 0
    total_refunds = sum(r.get("refund_amount", 0) for r in returns)
    actual_refunds = sum(r.get("actual_refund", r.get("refund_amount", 0)) for r in returns if r.get("status") == "refunded")
    by_status = {}
    by_reason = {}
    for r in returns:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        by_reason[r["reason"]] = by_reason.get(r["reason"], 0) + 1
    print("\n📊 RETURN STATISTICS")
    print(f"  Total Returns:    {len(returns)}")
    print(f"  Total Refunds:    ${total_refunds:,.2f}")
    print(f"  Actual Refunded:  ${actual_refunds:,.2f}")
    print(f"  By Status:        {by_status}")
    print(f"  By Reason:        {by_reason}")
    return 0


def cmd_policy(args):
    policy = load_json(POLICY_FILE, {})
    if args.set_return_window is not None:
        policy["return_window_days"] = args.set_return_window
    if args.set_restocking_fee is not None:
        policy["restocking_fee_percent"] = args.set_restocking_fee
    if args.set_refund_method:
        policy["refund_method"] = args.set_refund_method
    save_json(POLICY_FILE, policy)
    print(f"✅ Policy updated:")
    for k, v in policy.items():
        print(f"   {k}: {v}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="return-manager",
        description="♻️ Return Manager Agent — Process returns, approvals, and refunds.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("request", help="Create a return request")
    p.add_argument("--order-id", required=True, help="Original order ID")
    p.add_argument("--sku", required=True, help="Product SKU")
    p.add_argument("--product-name", help="Product name")
    p.add_argument("--quantity", type=int, help="Quantity to return")
    p.add_argument("--reason", required=True, choices=VALID_REASONS, help="Return reason")
    p.add_argument("--reason-detail", help="Detailed reason")
    p.add_argument("--customer-email", required=True, help="Customer email")
    p.add_argument("--refund-amount", type=float, required=True, help="Refund amount ($)")
    p.add_argument("--notes", help="Additional notes")

    p = sub.add_parser("approve", help="Approve a return request")
    p.add_argument("--return-id", required=True, help="Return ID")
    p.add_argument("--note", help="Approval note")

    p = sub.add_parser("reject", help="Reject a return request")
    p.add_argument("--return-id", required=True, help="Return ID")
    p.add_argument("--reason", help="Rejection reason")

    p = sub.add_parser("receive", help="Mark return item as received")
    p.add_argument("--return-id", required=True, help="Return ID")
    p.add_argument("--condition", help="Item condition on receipt")

    p = sub.add_parser("refund", help="Process refund for a return")
    p.add_argument("--return-id", required=True, help="Return ID")
    p.add_argument("--method", help="Refund method")

    p = sub.add_parser("list", help="List all returns")
    p.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    p.add_argument("--order-id", help="Filter by order ID")

    p = sub.add_parser("show", help="Show return details")
    p.add_argument("--return-id", required=True, help="Return ID")

    p = sub.add_parser("stats", help="Show return statistics")

    p = sub.add_parser("policy", help="View/update return policy")
    p.add_argument("--set-return-window", type=int, help="Return window in days")
    p.add_argument("--set-restocking-fee", type=float, help="Restocking fee (%%)")
    p.add_argument("--set-refund-method", help="Refund method")

    args = parser.parse_args()
    init_files()
    commands = {
        "request": cmd_request,
        "approve": cmd_approve,
        "reject": cmd_reject,
        "receive": cmd_receive,
        "refund": cmd_refund,
        "list": cmd_list,
        "show": cmd_show,
        "stats": cmd_stats,
        "policy": cmd_policy,
    }
    try:
        sys.exit(commands[args.cmd](args))
    except Exception as e:
        logger.exception(f"Command '{args.cmd}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
