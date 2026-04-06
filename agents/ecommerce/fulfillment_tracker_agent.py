#!/usr/bin/env python3
"""
Fulfillment Tracker Agent - OpenClaw Ecommerce Division
Tracks order fulfillment: status, shipping, delivery estimates, exceptions
Persona: CEO-mode - ensure orders arrive, protect customer experience
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

AGENT_NAME = "FulfillmentTracker"
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "fulfillment"
LOG_DIR = BASE_DIR / "logs"
ORDERS_FILE = DATA_DIR / "orders.json"
SHIPMENTS_FILE = DATA_DIR / "shipments.json"
CARRIERS_FILE = DATA_DIR / "carriers.json"
ALERTS_FILE = DATA_DIR / "alerts.json"

def setup_logging(verbose: bool = False) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"fulfillment_tracker_{datetime.now():%Y%m%d}.log"
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(AGENT_NAME)
    logger.setLevel(level)
    if logger.handlers:
        logger.handlers.clear()
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logging()

def load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default

def save_json(path: Path, data: dict | list) -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Failed to save: {e}")
        return False

def init_data():
    if not ORDERS_FILE.exists():
        save_json(ORDERS_FILE, {"orders": []})
    if not SHIPMENTS_FILE.exists():
        save_json(SHIPMENTS_FILE, {"shipments": []})
    if not CARRIERS_FILE.exists():
        save_json(CARRIERS_FILE, {"carriers": [
            {"id": "usps", "name": "USPS", "tracking_url": "https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking}"},
            {"id": "ups", "name": "UPS", "tracking_url": "https://www.ups.com/track?tracknum={tracking}"},
            {"id": "fedex", "name": "FedEx", "tracking_url": "https://www.fedex.com/fedextrack/?trknbr={tracking}"},
            {"id": "dhl", "name": "DHL", "tracking_url": "https://www.dhl.com/en/express/tracking.html?AWB={tracking}"},
        ]})
    if not ALERTS_FILE.exists():
        save_json(ALERTS_FILE, {"alerts": []})
    logger.info("Fulfillment tracker initialized")

FULFILLMENT_STAGES = ["pending","confirmed","processing","shipped","in_transit","out_for_delivery","delivered","cancelled","returned"]

def get_tracking_url(carrier_id: str, tracking_number: str) -> str:
    carriers = load_json(CARRIERS_FILE, {"carriers": []}).get("carriers", [])
    carrier = next((c for c in carriers if c["id"] == carrier_id), None)
    if carrier:
        return carrier["tracking_url"].replace("{tracking}", tracking_number)
    return f"https://example.com/track/{tracking_number}"

def calculate_eta(status: str, shipped_at: str, carrier_id: str = "usps") -> str:
    if status in ("delivered","cancelled","returned"):
        return "N/A"
    days = {"usps": 5, "ups": 3, "fedex": 3, "dhl": 5}.get(carrier_id, 5)
    if status == "shipped":
        ship = datetime.fromisoformat(shipped_at) if shipped_at else datetime.now()
        return (ship + timedelta(days=days)).strftime("%Y-%m-%d")
    elif status == "in_transit":
        return (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    elif status == "out_for_delivery":
        return "Today"
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

def cmd_order_add(args) -> int:
    data = load_json(ORDERS_FILE, {"orders": []})
    order = {
        "id": args.order_id or f"ORD_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "order_number": args.order_number or f"#{len(data['orders']) + 1001}",
        "customer_name": args.customer,
        "customer_email": args.email or "",
        "items": json.loads(args.items) if args.items else [{"name": "Item", "quantity": 1}],
        "total": args.total, "shipping_cost": args.shipping or 0,
        "status": "pending",
        "shipping_address": {"name": args.ship_name or args.customer, "street": args.street or "", "city": args.city or "", "state": args.state or "", "zip": args.zip or "", "country": args.country or "US"},
        "carrier": args.carrier or "usps", "tracking_number": "",
        "shipped_at": None, "delivered_at": None, "notes": args.notes or "",
        "created_at": datetime.now().isoformat(), "updated_at": datetime.now().isoformat()
    }
    data["orders"].append(order)
    data["last_updated"] = datetime.now().isoformat()
    save_json(ORDERS_FILE, data)
    print(f"✅ Order added: {order['order_number']} ({order['id']})")
    print(f"   Customer: {order['customer_name']} | Total: ${order['total']:.2f}")
    return 0

def cmd_order_list(args) -> int:
    data = load_json(ORDERS_FILE, {"orders": []})
    orders = data.get("orders", [])
    if args.status:
        orders = [o for o in orders if o.get("status") == args.status]
    if args.customer:
        orders = [o for o in orders if args.customer.lower() in o.get("customer_name","").lower()]
    if args.overdue:
        cutoff = (datetime.now() - timedelta(days=args.overdue)).isoformat()
        orders = [o for o in orders if o.get("status") not in ("delivered","cancelled","returned") and o.get("created_at","") < cutoff]
    if not orders:
        print("📦 No orders match")
        return 0
    icons = {"pending":"⏳","confirmed":"✅","processing":"⚙️","shipped":"🚚","in_transit":"📦","out_for_delivery":"🚗","delivered":"✅","cancelled":"❌","returned":"↩️"}
    print(f"\n📦 Orders ({len(orders)}):")
    for o in orders:
        icon = icons.get(o.get("status"),"❓")
        eta = calculate_eta(o.get("status"), o.get("shipped_at",""), o.get("carrier","usps"))
        print(f"  {icon} [{o['id']}] {o.get('order_number')} - {o.get('customer_name')}")
        print(f"     Total: ${o.get('total',0):.2f} | {o.get('status')}")
        if o.get("tracking_number"): print(f"     Tracking: {o.get('carrier').upper()} {o.get('tracking_number')}")
        if eta != "N/A" and o.get("status") not in ("delivered","cancelled"): print(f"     ETA: {eta}")
    return 0

def cmd_order_status(args) -> int:
    data = load_json(ORDERS_FILE, {"orders": []})
    for o in data["orders"]:
        if o["id"] == args.order_id or o.get("order_number") == args.order_id:
            old = o.get("status")
            o["status"] = args.status
            o["updated_at"] = datetime.now().isoformat()
            if args.status == "shipped": o["shipped_at"] = datetime.now().isoformat()
            if args.status == "delivered": o["delivered_at"] = datetime.now().isoformat()
            save_json(ORDERS_FILE, data)
            print(f"✅ {o['id']}: {old} → {args.status}")
            return 0
    print(f"❌ Order not found: {args.order_id}")
    return 1

def cmd_order_tracking(args) -> int:
    data = load_json(ORDERS_FILE, {"orders": []})
    for o in data["orders"]:
        if o["id"] == args.order_id or o.get("order_number") == args.order_id:
            o["carrier"] = args.carrier
            o["tracking_number"] = args.tracking
            o["tracking_url"] = get_tracking_url(args.carrier, args.tracking)
            if not o.get("shipped_at"): o["shipped_at"] = datetime.now().isoformat()
            o["updated_at"] = datetime.now().isoformat()
            save_json(ORDERS_FILE, data)
            print(f"✅ Tracking added: {args.carrier.upper()} {args.tracking}")
            print(f"   🔗 {o['tracking_url']}")
            return 0
    print(f"❌ Order not found: {args.order_id}")
    return 1

def cmd_order_cancel(args) -> int:
    data = load_json(ORDERS_FILE, {"orders": []})
    for o in data["orders"]:
        if o["id"] == args.order_id or o.get("order_number") == args.order_id:
            if o.get("status") in ("delivered","cancelled"):
                print(f"❌ Cannot cancel: status is '{o['status']}'")
                return 1
            o["status"] = "cancelled"
            o["cancelled_at"] = datetime.now().isoformat()
            o["cancel_reason"] = args.reason or "No reason"
            o["updated_at"] = datetime.now().isoformat()
            save_json(ORDERS_FILE, data)
            print(f"✅ Order {o['id']} cancelled")
            return 0
    print(f"❌ Order not found: {args.order_id}")
    return 1

def cmd_carrier_list(args) -> int:
    data = load_json(CARRIERS_FILE, {"carriers": []})
    print(f"\n🚚 Carriers ({len(data.get('carriers',[]))}):")
    for c in data.get("carriers", []):
        print(f"  [{c['id']}] {c['name']}")
    return 0

def cmd_stats(args) -> int:
    orders = load_json(ORDERS_FILE, {"orders": []}).get("orders", [])
    if not orders:
        print("📊 No order data")
        return 0
    total = len(orders)
    by_status = {}
    for o in orders: by_status[o.get("status","unknown")] = by_status.get(o.get("status","unknown"),0) + 1
    total_rev = sum(o.get("total",0) for o in orders)
    print(f"""
╔══════════════════════════════════════════════════════╗
║           📊 FULFILLMENT STATISTICS                   ║
║              {datetime.now().strftime('%Y-%m-%d %H:%M'):<36} ║
╚══════════════════════════════════════════════════════╝
  Total Orders:     {total}
  Total Revenue:    ${total_rev:.2f}
  Avg Order Value:  ${total_rev/total:.2f}
  ⏳ Pending:       {by_status.get('pending',0)}
  ✅ Confirmed:     {by_status.get('confirmed',0)}
  ⚙️ Processing:    {by_status.get('processing',0)}
  🚚 Shipped:       {by_status.get('shipped',0)}
  📦 In Transit:    {by_status.get('in_transit',0)}
  🚗 Out Delivery:  {by_status.get('out_for_delivery',0)}
  ✅ Delivered:     {by_status.get('delivered',0)}
  ❌ Cancelled:     {by_status.get('cancelled',0)}
  ↩️ Returned:      {by_status.get('returned',0)}
""")
    return 0

def cmd_alert(args) -> int:
    data = load_json(ALERTS_FILE, {"alerts": []})
    orders = load_json(ORDERS_FILE, {"orders": []}).get("orders", [])
    alerts = []
    for o in orders:
        if o.get("status") == "processing":
            created = datetime.fromisoformat(o.get("created_at", datetime.now().isoformat()))
            if (datetime.now() - created).days > 3:
                alerts.append({"type":"stale","order_id":o["id"],"message":"Stuck in processing >3 days","created_at":datetime.now().isoformat()})
    for o in orders:
        if o.get("status") == "confirmed":
            created = datetime.fromisoformat(o.get("created_at", datetime.now().isoformat()))
            if (datetime.now() - created).days > 2:
                alerts.append({"type":"unshipped","order_id":o["id"],"message":"Paid but not shipped in 2 days","created_at":datetime.now().isoformat()})
    if args.generate:
        data["alerts"] = alerts
        save_json(ALERTS_FILE, data)
        print(f"✅ Generated {len(alerts)} alerts")
        return 0
    active = data.get("alerts", [])
    print(f"\n🔔 Alerts ({len(active)}):")
    for a in active:
        icon = {"stale":"⚠️","unshipped":"🚨"}.get(a.get("type","🔔"),"🔔")
        print(f"  {icon} [{a.get('type')}] {a.get('message')} | Order: {a.get('order_id')}")
    return 0

def main():
    parser = argparse.ArgumentParser(description="🚚 Fulfillment Tracker Agent")
    sub = parser.add_subparsers(dest="command", required=True)
    
    order_p = sub.add_parser("order", help="Manage orders")
    order_sub = order_p.add_subparsers(dest="action")
    oa = order_sub.add_parser("add", help="Add order")
    oa.add_argument("--order-id"); oa.add_argument("--order-number")
    oa.add_argument("--customer", required=True); oa.add_argument("--email")
    oa.add_argument("--items"); oa.add_argument("--total", type=float, required=True)
    oa.add_argument("--shipping", type=float); oa.add_argument("--carrier", default="usps")
    oa.add_argument("--ship-name"); oa.add_argument("--street"); oa.add_argument("--city")
    oa.add_argument("--state"); oa.add_argument("--zip"); oa.add_argument("--country", default="US")
    oa.add_argument("--notes"); oa.set_defaults(func=cmd_order_add)
    ol = order_sub.add_parser("list", help="List orders")
    ol.add_argument("--status", choices=FULFILLMENT_STAGES)
    ol.add_argument("--customer"); ol.add_argument("--overdue", type=int)
    ol.set_defaults(func=cmd_order_list)
    os_ = order_sub.add_parser("status", help="Update status")
    os_.add_argument("--order-id", required=True); os_.add_argument("--status", required=True, choices=FULFILLMENT_STAGES)
    os_.set_defaults(func=cmd_order_status)
    ot = order_sub.add_parser("tracking", help="Add tracking")
    ot.add_argument("--order-id", required=True); ot.add_argument("--carrier", required=True); ot.add_argument("--tracking", required=True)
    ot.set_defaults(func=cmd_order_tracking)
    oc = order_sub.add_parser("cancel", help="Cancel order")
    oc.add_argument("--order-id", required=True); oc.add_argument("--reason")
    oc.set_defaults(func=cmd_order_cancel)
    
    sub.add_parser("carriers", help="List carriers").set_defaults(func=cmd_carrier_list)
    sub.add_parser("stats", help="Show statistics").set_defaults(func=cmd_stats)
    alert_p = sub.add_parser("alert", help="Manage alerts")
    alert_p.add_argument("--generate", action="store_true")
    alert_p.set_defaults(func=cmd_alert)
    
    args = parser.parse_args()
    init_data()
    try:
        return args.func(args)
    except Exception as e:
        logger.exception("Error")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
