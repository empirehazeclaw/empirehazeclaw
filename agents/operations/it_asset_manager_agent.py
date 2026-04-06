#!/usr/bin/env python3
"""
💻 IT Asset Manager Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Tracks and manages IT hardware/software assets.
Features:
- Asset inventory (hardware, software, licenses)
- Lifecycle tracking (purchase → warranty → end-of-life)
- Depreciation calculation
- License compliance
- Maintenance scheduling
- Procurement alerts
- Hardware assignment to employees
- Asset depreciation (straight-line)

Usage:
  python3 operations/it_asset_manager_agent.py --help
  python3 operations/it_asset_manager_agent.py add --name "MacBook Pro 16" --type hardware --category laptop --serial ABC123 --purchase-date 2024-01-15 --cost 2499 --assigned-to "Max M."
  python3 operations/it_asset_manager_agent.py list --type hardware
  python3 operations/it_asset_manager_agent.py assign --asset-id 0 --to "Anna S."
  python3 operations/it_asset_manager_agent.py lifecycle --asset-id 0
  python3 operations/it_asset_manager_agent.py depreciation --asset-id 0
  python3 operations/it_asset_manager_agent.py maintenance_due
  python3 operations/it_asset_manager_agent.py report
  python3 operations/it_asset_manager_agent.py alert --type warranty --days 30
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
ASSET_DIR = DATA_DIR / "it_assets"

for d in [DATA_DIR, LOGS_DIR, ASSET_DIR]:
    d.mkdir(parents=True, exist_ok=True)

ASSETS_FILE      = ASSET_DIR / "assets.json"
MAINTENANCE_FILE = ASSET_DIR / "maintenance.json"
ALERTS_FILE     = ASSET_DIR / "alerts.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [IT_ASSET] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "it_asset_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("it_asset")

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_json(path, default):
    try: return json.loads(path.read_text())
    except Exception: return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def load_assets():
    return load_json(ASSETS_FILE, [])

def save_assets(assets):
    save_json(ASSETS_FILE, assets)

def parse_date(s: str) -> str:
    """Parse date string to ISO format."""
    for fmt in ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]:
        for try_fmt in [fmt]:
            try:
                return datetime.strptime(s.strip(), try_fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    return s  # return as-is if can't parse

# ─── ASSET TYPES ─────────────────────────────────────────────────────────────
ASSET_CATEGORIES = [
    "laptop", "desktop", "server", "monitor", "printer", "router",
    "phone", "tablet", "camera", "keyboard", "mouse", "headset",
    "network_switch", "storage", "ups", "other_hardware",
]

SOFTWARE_TYPES = [
    "os", "productivity", "development", "security", "design",
    "accounting", "crm", "communication", "database", "other_software",
]

LICENSE_TYPES = ["perpetual", "subscription", "per_seat", "enterprise", "open_source", "freeware"]

# ─── LIFECYCLE STAGES ─────────────────────────────────────────────────────────
LIFECYCLE_STAGES = [
    ("planning",    "Planning / Procurement"),
    ("ordered",     "Ordered"),
    ("provisioning","Provisioning / Setup"),
    ("active",      "Active / In Use"),
    ("maintenance", "Under Maintenance"),
    ("retiring",    "Retiring / Phasing Out"),
    ("retired",     "Retired / Disposed"),
    ("lost",        "Lost / Stolen"),
]

DEFAULT_LIFESPAN_YEARS = {
    "laptop": 4, "desktop": 5, "server": 5, "monitor": 5,
    "printer": 4, "phone": 3, "tablet": 3, "router": 4,
    "network_switch": 5, "storage": 5, "ups": 5,
    "other_hardware": 3,
}

DEPRECIATION_METHODS = {
    "straight_line": "Straight-Line (equal annual depreciation)",
    "declining": "Declining Balance (accelerated)",
}

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_add(args) -> int:
    """Add a new asset."""
    assets = load_assets()
    new_id = max([a.get("id", -1) for a in assets], default=-1) + 1

    purchase_date = parse_date(args.purchase_date) if args.purchase_date else datetime.now().strftime("%Y-%m-%d")
    category = args.category or args.asset_type

    # Calculate warranty end
    warranty_months = args.warranty_months or 24
    warranty_end = (datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=warranty_months * 30)).strftime("%Y-%m-%d") if purchase_date else ""

    # Calculate end-of-life
    lifespan = DEFAULT_LIFESPAN_YEARS.get(category, 4)
    eol_date = (datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=lifespan * 365)).strftime("%Y-%m-%d") if purchase_date else ""

    # Calculate depreciation
    cost = args.cost or 0
    salvage_value = cost * 0.1  # 10% residual value
    annual_depreciation = (cost - salvage_value) / lifespan if lifespan > 0 else 0

    asset = {
        "id": new_id,
        "name": args.name,
        "asset_type": args.asset_type,  # hardware | software | license
        "category": category,
        "serial_number": args.serial or "",
        "manufacturer": args.manufacturer or "",
        "model": args.model or "",
        "purchase_date": purchase_date,
        "purchase_cost": cost,
        "vendor": args.vendor or "",
        "warranty_months": warranty_months,
        "warranty_end": warranty_end,
        "lifecycle_stage": "active" if args.purchase_date else "provisioning",
        "assigned_to": args.assigned_to or "",
        "location": args.location or "",
        "notes": args.notes or "",
        "eol_date": eol_date,
        "lifespan_years": lifespan,
        "salvage_value": round(salvage_value, 2),
        "annual_depreciation": round(annual_depreciation, 2),
        "status": "operational",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    assets.append(asset)
    save_assets(assets)
    logger.info(f"Added asset: {asset['name']} (ID: {new_id})")

    print(f"✅ Asset added (ID: {new_id}): {asset['name']}")
    print(f"   Type: {asset['asset_type']} | Category: {asset['category']}")
    if args.serial:
        print(f"   Serial: {asset['serial_number']}")
    print(f"   Cost: €{cost} | Purchased: {purchase_date}")
    print(f"   Warranty: until {warranty_end} ({warranty_months} months)")
    print(f"   EOL: {eol_date} (in ~{lifespan} years)")
    print(f"   Annual Depreciation: €{annual_depreciation:.2f}")
    if args.assigned_to:
        print(f"   Assigned to: {args.assigned_to}")
    return 0


def cmd_list(args) -> int:
    """List assets."""
    assets = load_assets()
    if not assets:
        print("No assets in inventory. Add one with: add")
        return 0

    filters = {}
    if args.type:
        filters["asset_type"] = args.type
    if args.category:
        filters["category"] = args.category
    if args.status:
        filters["status"] = args.status
    if args.location:
        filters["location"] = args.location

    filtered = assets
    for k, v in filters.items():
        filtered = [a for a in filtered if a.get(k) == v]

    print(f"\n💻 IT Asset Inventory")
    print(f"{'='*90}")
    print(f"{'ID':>3} | {'Name':<25} | {'Category':<12} | {'Status':<14} | {'Cost':>8} | {'Assigned To':<15}")
    print("-" * 90)
    total_cost = 0
    for a in sorted(filtered, key=lambda x: x.get("name", "")):
        total_cost += a.get("purchase_cost", 0)
        name = a["name"][:23] + ".." if len(a["name"]) > 25 else a["name"]
        assigned = (a.get("assigned_to") or "—")[:13]
        print(f"{a['id']:>3} | {name:<25} | {a.get('category','?'):<12} | {a.get('status','?'):<14} | €{a.get('purchase_cost',0):>7} | {assigned:<15}")
    print("-" * 90)
    print(f"Total: {len(filtered)} asset(s) | Total Cost: €{total_cost:,.2f}")
    return 0


def cmd_assign(args) -> int:
    """Assign/reassign asset to employee."""
    assets = load_assets()
    try:
        asset = next(a for a in assets if a["id"] == int(args.asset_id))
    except StopIteration:
        print(f"Asset ID {args.asset_id} not found")
        return 1

    old_assignee = asset.get("assigned_to", "")
    asset["assigned_to"] = args.to
    asset["updated_at"] = datetime.now().isoformat()
    save_assets(assets)
    logger.info(f"Assigned asset {asset['name']} to {args.to} (was: {old_assignee})")

    print(f"✅ Asset '{asset['name']}' (ID: {asset['id']})")
    print(f"   Assigned: {old_assignee or '(none)'} → {args.to}")
    return 0


def cmd_lifecycle(args) -> int:
    """Show lifecycle status of an asset."""
    assets = load_assets()
    try:
        asset = next(a for a in assets if a["id"] == int(args.asset_id))
    except StopIteration:
        print(f"Asset ID {args.asset_id} not found")
        return 1

    stage = asset.get("lifecycle_stage", "unknown")
    print(f"\n🔄 Lifecycle: {asset['name']} (ID: {asset['id']})")
    print(f"{'='*55}")
    print(f"  Stage: {stage}")
    print(f"  Purchase: {asset.get('purchase_date', 'N/A')}")
    print(f"  EOL Date: {asset.get('eol_date', 'N/A')}")
    print(f"  Warranty End: {asset.get('warranty_end', 'N/A')}")
    print(f"  Lifespan: {asset.get('lifespan_years', 0)} years")
    print(f"  Assigned to: {asset.get('assigned_to', 'unassigned')}")

    # Show all stages
    current_idx = next((i for i, (s, _) in enumerate(LIFECYCLE_STAGES) if s == stage), -1)
    print(f"\n  Lifecycle Progress:")
    for i, (s, label) in enumerate(LIFECYCLE_STAGES):
        arrow = "→" if i == current_idx else ("✓" if i < current_idx else " ")
        marker = "[*]" if i == current_idx else ("[✓]" if i < current_idx else "[ ]")
        print(f"    {marker} {arrow} {s:<15} — {label}")

    # Days until EOL
    if asset.get("eol_date"):
        try:
            eol = datetime.strptime(asset["eol_date"], "%Y-%m-%d")
            days_left = (eol - datetime.now()).days
            pct_life = max(0, min(100, (datetime.now() - datetime.strptime(asset["purchase_date"], "%Y-%m-%d")).days / ((eol - datetime.strptime(asset["purchase_date"], "%Y-%m-%d")).days) * 100))
            bar = "█" * int(pct_life / 5) + "░" * (20 - int(pct_life / 5))
            print(f"\n  EOL Progress: [{bar}] {pct_life:.0f}% ({days_left} days remaining)")
        except Exception:
            pass
    return 0


def cmd_depreciation(args) -> int:
    """Calculate depreciation for an asset."""
    assets = load_assets()
    try:
        asset = next(a for a in assets if a["id"] == int(args.asset_id))
    except StopIteration:
        print(f"Asset ID {args.asset_id} not found")
        return 1

    cost = asset.get("purchase_cost", 0)
    salvage = asset.get("salvage_value", cost * 0.1)
    lifespan = asset.get("lifespan_years", 4)
    annual_dep = asset.get("annual_depreciation", (cost - salvage) / lifespan if lifespan else 0)

    purchase_date_str = asset.get("purchase_date")
    if purchase_date_str:
        try:
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
            age_days = (datetime.now() - purchase_date).days
            age_years = age_days / 365.25
        except Exception:
            age_years = 0
    else:
        age_years = 0

    # Straight-line depreciation
    accumulated = annual_dep * age_years
    book_value = cost - accumulated

    # Declining balance (double-declining)
    rate = 2.0 / lifespan if lifespan else 0.5
    declining_value = cost * ((1 - rate) ** age_years) if age_years else cost

    print(f"\n📉 Depreciation Report: {asset['name']}")
    print(f"{'='*55}")
    print(f"  Purchase Cost: €{cost:,.2f}")
    print(f"  Salvage Value: €{salvage:,.2f}")
    print(f"  Lifespan: {lifespan} years")
    print(f"  Age: {age_years:.1f} years")
    print(f"\n  STRAIGHT-LINE METHOD:")
    print(f"    Annual Depreciation: €{annual_dep:,.2f}")
    print(f"    Accumulated:         €{accumulated:,.2f}")
    print(f"    Current Book Value:  €{max(book_value, salvage):,.2f}")
    print(f"\n  DECLINING BALANCE (DDB):")
    print(f"    Rate: {rate*100:.1f}%/year")
    print(f"    Current Value: €{max(declining_value, salvage):,.2f}")

    # Year-by-year table
    print(f"\n  Year | Depreciation | Accumulated | Book Value")
    print(f"  " + "-" * 50)
    for year in range(lifespan + 1):
        if year == 0:
            print(f"    0  |      €0.00    |      €0.00   | €{cost:,.2f}")
        else:
            yr_dep = annual_dep
            yr_accum = yr_dep * year
            yr_book = max(cost - yr_accum, salvage)
            print(f"  {year:>4} |    €{yr_dep:>8,.2f} |   €{yr_accum:>8,.2f} | €{yr_book:,.2f}")

    return 0


def cmd_maintenance_due(args) -> int:
    """Show assets due for maintenance."""
    assets = load_assets()
    days = args.days or 30
    threshold = datetime.now() + timedelta(days=days)

    due = []
    for a in assets:
        # Check warranty expiration
        warranty_end = a.get("warranty_end", "")
        if warranty_end:
            try:
                we = datetime.strptime(warranty_end, "%Y-%m-%d")
                if we < threshold and we > datetime.now():
                    due.append((a, "warranty_expiring", f"Warranty expires {warranty_end}"))
            except Exception:
                pass

        # Check EOL approaching
        eol = a.get("eol_date", "")
        if eol:
            try:
                eol_date = datetime.strptime(eol, "%Y-%m-%d")
                if eol_date < threshold and eol_date > datetime.now():
                    due.append((a, "eol_approaching", f"EOL in {eol}"))
            except Exception:
                pass

    if not due:
        print(f"✅ No assets due for maintenance/warranty attention in the next {days} days")
        return 0

    print(f"\n🔧 Maintenance & Lifecycle Alerts (next {days} days)")
    print(f"{'='*65}")
    for a, alert_type, msg in sorted(due, key=lambda x: x[0]["name"]):
        print(f"  [{alert_type.replace('_', ' ').upper()}] {a['name']} (ID: {a['id']})")
        print(f"     {msg} | Cost: €{a.get('purchase_cost', 0)} | Assigned: {a.get('assigned_to','unassigned')}")
    return 0


def cmd_report(args) -> int:
    """Full IT asset report."""
    assets = load_assets()
    if not assets:
        print("No assets in inventory.")
        return 0

    total_cost = sum(a.get("purchase_cost", 0) for a in assets)
    by_category = {}
    by_status = {}
    by_type = {}
    total_depreciation = 0

    for a in assets:
        cat = a.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1
        by_status[a.get("status", "unknown")] = by_status.get(a.get("status", "unknown"), 0) + 1
        by_type[a.get("asset_type", "unknown")] = by_type.get(a.get("asset_type", "unknown"), 0) + 1
        # Estimate accumulated depreciation
        age_years = 0
        if a.get("purchase_date"):
            try:
                age = (datetime.now() - datetime.strptime(a["purchase_date"], "%Y-%m-%d")).days / 365.25
                age_years = min(age, a.get("lifespan_years", 4))
            except Exception:
                pass
        total_depreciation += a.get("annual_depreciation", 0) * age_years

    print(f"\n💻 IT ASSET REPORT")
    print(f"{'='*55}")
    print(f"  Total Assets: {len(assets)}")
    print(f"  Total Acquisition Cost: €{total_cost:,.2f}")
    print(f"  Accumulated Depreciation: €{total_depreciation:,.2f}")
    print(f"  Net Book Value: €{total_cost - total_depreciation:,.2f}")

    print(f"\n  By Type:")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {t:<15}: {c} asset(s)")

    print(f"\n  By Status:")
    for s, c in sorted(by_status.items(), key=lambda x: -x[1]):
        print(f"    {s:<15}: {c}")

    print(f"\n  Top Categories:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1])[:10]:
        cat_cost = sum(a.get("purchase_cost", 0) for a in assets if a.get("category") == cat)
        print(f"    {cat:<20}: {count} assets (€{cat_cost:,.2f})")

    # Unassigned
    unassigned = [a for a in assets if not a.get("assigned_to")]
    if unassigned:
        print(f"\n  ⚠️  Unassigned Assets ({len(unassigned)}):")
        for a in unassigned[:5]:
            print(f"     - {a['name']} ({a.get('category','?')})")
    return 0


def cmd_alert(args) -> int:
    """Set up asset alerts."""
    cfg = load_json(ASSET_DIR / "config.json", {})
    if args.type == "warranty":
        cfg["warranty_alert_days"] = int(args.days)
        print(f"✅ Warranty alerts set: {args.days} days before expiry")
    elif args.type == "eol":
        cfg["eol_alert_days"] = int(args.days)
        print(f"✅ EOL alerts set: {args.days} days before end-of-life")
    save_json(ASSET_DIR / "config.json", cfg)
    return 0


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="operations/it_asset_manager_agent.py",
        description="💻 IT Asset Manager — Track hardware, software, licenses, depreciation & maintenance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 operations/it_asset_manager_agent.py add --name "MacBook Pro 16" --type hardware --category laptop --serial ABC123 --purchase-date 2024-01-15 --cost 2499 --assigned-to "Max M." --location "Office Berlin"
  python3 operations/it_asset_manager_agent.py add --name "Microsoft 365" --type software --category productivity --cost 1200 --vendor "Microsoft"
  python3 operations/it_asset_manager_agent.py list
  python3 operations/it_asset_manager_agent.py list --type hardware --status operational
  python3 operations/it_asset_manager_agent.py assign --asset-id 0 --to "Anna S."
  python3 operations/it_asset_manager_agent.py lifecycle --asset-id 0
  python3 operations/it_asset_manager_agent.py depreciation --asset-id 0
  python3 operations/it_asset_manager_agent.py maintenance_due --days 60
  python3 operations/it_asset_manager_agent.py alert --type warranty --days 30
  python3 operations/it_asset_manager_agent.py report
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add", help="Add an asset")
    p.add_argument("--name", required=True)
    p.add_argument("--type",  required=True, choices=["hardware", "software", "license"])
    p.add_argument("--category", default="")
    p.add_argument("--serial", default="")
    p.add_argument("--manufacturer", default="")
    p.add_argument("--model", default="")
    p.add_argument("--purchase-date", default="")
    p.add_argument("--cost", type=float, default=0)
    p.add_argument("--vendor", default="")
    p.add_argument("--warranty-months", type=int, default=24)
    p.add_argument("--assigned-to", default="")
    p.add_argument("--location", default="")
    p.add_argument("--notes", default="")

    p = sub.add_parser("list", help="List assets")
    p.add_argument("--type", default="")
    p.add_argument("--category", default="")
    p.add_argument("--status", default="")
    p.add_argument("--location", default="")

    p = sub.add_parser("assign", help="Assign asset to employee")
    p.add_argument("--asset-id", required=True, type=int)
    p.add_argument("--to", required=True)

    p = sub.add_parser("lifecycle", help="Show asset lifecycle")
    p.add_argument("--asset-id", required=True, type=int)

    p = sub.add_parser("depreciation", help="Calculate depreciation")
    p.add_argument("--asset-id", required=True, type=int)

    p = sub.add_parser("maintenance_due", help="Show maintenance due")
    p.add_argument("--days", type=int, default=30)

    p = sub.add_parser("alert", help="Set alert threshold")
    p.add_argument("--type", required=True, choices=["warranty", "eol"])
    p.add_argument("--days", required=True, type=int)

    p = sub.add_parser("report", help="Full asset report")

    args = parser.parse_args()
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "assign": cmd_assign,
        "lifecycle": cmd_lifecycle,
        "depreciation": cmd_depreciation,
        "maintenance_due": cmd_maintenance_due,
        "alert": cmd_alert,
        "report": cmd_report,
    }
    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
