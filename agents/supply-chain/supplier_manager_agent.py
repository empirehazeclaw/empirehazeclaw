#!/usr/bin/env python3
"""
Supplier Manager Agent
======================
Manages supplier records, performance scoring, contracts, risk assessment,
and purchase-order tracking. Supports qualification, deactivation, and
on-time delivery analysis.

Usage:
    python3 supplier_manager_agent.py --list
    python3 supplier_manager_agent.py --score
    python3 supplier_manager_agent.py --order --supplier SUP-001 --items data/po_items.json
    python3 supplier_manager_agent.py --risk
    python3 supplier_manager_agent.py --qualify data/new_supplier.json
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("SupplierManager")


# ── Data Models ───────────────────────────────────────────────────────────────
@dataclass
class Supplier:
    id: str
    name: str
    category: str           # e.g. "Raw Materials", "Components", "Packaging"
    country: str
    rating: float = 3.0    # 1-5 stars
    status: str = "active"  # active | qualified | provisional | suspended | disqualified
    contact_name: str = ""
    contact_email: str = ""
    contract_end: Optional[str] = None
    payment_terms_days: int = 30
    lead_time_days: int = 14
    min_order_value: float = 0.0
    certifications: list[str] = field(default_factory=list)  # ISO-9001, etc.
    total_orders: int = 0
    on_time_count: int = 0
    quality_score: float = 3.0  # 1-5
    risk_level: str = "medium"   # low | medium | high | critical
    created_at: str = ""
    updated_at: str = ""


@dataclass
class PurchaseOrder:
    po_id: str
    supplier_id: str
    supplier_name: str
    items: list[dict]       # [{"sku": "...", "description": "...", "qty": int, "unit_price": float}]
    total_value: float
    order_date: str
    expected_delivery: str
    actual_delivery: Optional[str] = None
    status: str = "issued"   # issued | confirmed | shipped | delivered | cancelled
    on_time: Optional[bool] = None
    notes: str = ""


# ── Data Store ────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "supply_chain")
SUPPLIERS_FILE = os.path.join(DATA_DIR, "suppliers.json")
PO_FILE = os.path.join(DATA_DIR, "purchase_orders.json")


def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load %s: %s", path, e)
    return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


# ── Core Logic ────────────────────────────────────────────────────────────────
class SupplierManager:
    RISK_WEIGHTS = {
        "low": {"score": 10, "icon": "🟢"},
        "medium": {"score": 6, "icon": "🟡"},
        "high": {"score": 3, "icon": "🟠"},
        "critical": {"score": 1, "icon": "🔴"},
    }

    def __init__(self):
        self.suppliers: list[Supplier] = []
        self.orders: list[PurchaseOrder] = []

    # ── Data Loading ───────────────────────────────────────────────────────────
    def load_suppliers(self, path: Optional[str] = None):
        path = path or SUPPLIERS_FILE
        raw = load_json(path, [])
        self.suppliers = [Supplier(**s) if isinstance(s, dict) else s for s in raw]
        log.info("Loaded %d suppliers", len(self.suppliers))

    def load_orders(self, path: Optional[str] = None):
        path = path or PO_FILE
        raw = load_json(path, [])
        self.orders = [PurchaseOrder(**o) if isinstance(o, dict) else o for o in raw]
        log.info("Loaded %d purchase orders", len(self.orders))

    def generate_sample_data(self):
        import random
        now = datetime.utcnow()
        base = now - timedelta(days=365)

        raw_suppliers = [
            {"id": "SUP-001", "name": "Acme Steel Works", "category": "Raw Materials",
             "country": "DE", "rating": 4.2, "contact_name": "Klaus Weber",
             "contact_email": "k.weber@acmesteel.de",
             "contract_end": (base + timedelta(days=200)).isoformat()[:10],
             "payment_terms_days": 30, "lead_time_days": 14,
             "min_order_value": 5000.0,
             "certifications": ["ISO-9001", "ISO-14001"],
             "total_orders": 48, "on_time_count": 42, "quality_score": 4.3,
             "risk_level": "low"},
            {"id": "SUP-002", "name": "Beta Components Ltd", "category": "Components",
             "country": "CN", "rating": 3.8, "contact_name": "Li Wei",
             "contact_email": "liwei@betacomponents.cn",
             "contract_end": (base + timedelta(days=90)).isoformat()[:10],
             "payment_terms_days": 60, "lead_time_days": 35,
             "min_order_value": 1000.0,
             "certifications": ["ISO-9001"],
             "total_orders": 35, "on_time_count": 28, "quality_score": 3.9,
             "risk_level": "medium"},
            {"id": "SUP-003", "name": "Gamma Packaging SA", "category": "Packaging",
             "country": "FR", "rating": 4.5, "contact_name": "Marie Dupont",
             "contact_email": "m.dupont@gammapack.fr",
             "contract_end": (base + timedelta(days=400)).isoformat()[:10],
             "payment_terms_days": 30, "lead_time_days": 7,
             "min_order_value": 500.0,
             "certifications": ["ISO-9001", "FSC"],
             "total_orders": 60, "on_time_count": 57, "quality_score": 4.7,
             "risk_level": "low"},
            {"id": "SUP-004", "name": "Delta Electronics", "category": "Components",
             "country": "TW", "rating": 3.1, "contact_name": "Chen Ming",
             "contact_email": "c.ming@deltaelec.tw",
             "contract_end": (base + timedelta(days=30)).isoformat()[:10],
             "payment_terms_days": 45, "lead_time_days": 28,
             "min_order_value": 2000.0,
             "certifications": [],
             "total_orders": 20, "on_time_count": 12, "quality_score": 3.0,
             "risk_level": "high"},
            {"id": "SUP-005", "name": "Epsilon Fasteners GmbH", "category": "Components",
             "country": "AT", "rating": 4.0, "contact_name": "Franz Hofer",
             "contact_email": "f.hofer@eps-fasteners.at",
             "contract_end": (base + timedelta(days=150)).isoformat()[:10],
             "payment_terms_days": 30, "lead_time_days": 10,
             "min_order_value": 200.0,
             "certifications": ["ISO-9001"],
             "total_orders": 40, "on_time_count": 36, "quality_score": 4.1,
             "risk_level": "low"},
        ]
        self.suppliers = [Supplier(
            id=s["id"], name=s["name"], category=s["category"],
            country=s["country"], rating=s["rating"],
            contact_name=s["contact_name"], contact_email=s["contact_email"],
            contract_end=s["contract_end"],
            payment_terms_days=s["payment_terms_days"],
            lead_time_days=s["lead_time_days"],
            min_order_value=s["min_order_value"],
            certifications=s["certifications"],
            total_orders=s["total_orders"], on_time_count=s["on_time_count"],
            quality_score=s["quality_score"], risk_level=s["risk_level"],
            created_at=base.isoformat()[:10],
            updated_at=now.isoformat()[:10],
        ) for s in raw_suppliers]
        log.info("Generated %d sample suppliers", len(self.suppliers))
        self._save_suppliers()

        # Generate sample POs
        raw_pos = []
        statuses = ["delivered"] * 30 + ["shipped"] * 5 + ["confirmed"] * 3 + ["issued"] * 2
        for i, status in enumerate(statuses):
            sup = random.choice(self.suppliers)
            qty = random.randint(10, 500)
            unit_price = random.uniform(5, 200)
            order_date = base + timedelta(days=i * 10)
            expected = order_date + timedelta(days=sup.lead_time_days)
            actual = expected + timedelta(days=random.randint(-3, 7))
            raw_pos.append({
                "po_id": f"PO-{5000 + i}",
                "supplier_id": sup.id,
                "supplier_name": sup.name,
                "items": [{
                    "sku": f"SKU-{random.randint(1000,9999)}",
                    "description": random.choice(["Part-A", "Part-B", "Raw-Mat"]),
                    "qty": qty,
                    "unit_price": round(unit_price, 2),
                }],
                "total_value": round(qty * unit_price, 2),
                "order_date": order_date.isoformat()[:10],
                "expected_delivery": expected.isoformat()[:10],
                "actual_delivery": actual.isoformat()[:10] if status == "delivered" else None,
                "status": status,
                "on_time": (actual <= expected) if status == "delivered" else None,
            })
        self.orders = [PurchaseOrder(**p) for p in raw_pos]
        self._save_orders()

    # ── Persistence ────────────────────────────────────────────────────────────
    def _save_suppliers(self):
        save_json(SUPPLIERS_FILE, [s.__dict__ for s in self.suppliers])

    def _save_orders(self):
        save_json(PO_FILE, [o.__dict__ for o in self.orders])

    # ── Supplier CRUD ──────────────────────────────────────────────────────────
    def add_supplier(self, data: dict) -> Supplier:
        data["created_at"] = datetime.utcnow().isoformat()[:10]
        data["updated_at"] = data["created_at"]
        supplier = Supplier(**data)
        self.suppliers.append(supplier)
        self._save_suppliers()
        log.info("Added supplier %s (%s)", supplier.id, supplier.name)
        return supplier

    def update_supplier(self, supplier_id: str, updates: dict):
        sup = next((s for s in self.suppliers if s.id == supplier_id), None)
        if not sup:
            raise ValueError(f"Supplier {supplier_id} not found")
        for key, val in updates.items():
            if hasattr(sup, key):
                setattr(sup, key, val)
        sup.updated_at = datetime.utcnow().isoformat()[:10]
        self._save_suppliers()
        log.info("Updated supplier %s", supplier_id)

    def suspend_supplier(self, supplier_id: str, reason: str = ""):
        sup = next((s for s in self.suppliers if s.id == supplier_id), None)
        if not sup:
            raise ValueError(f"Supplier {supplier_id} not found")
        sup.status = "suspended"
        sup.updated_at = datetime.utcnow().isoformat()[:10]
        self._save_suppliers()
        log.warning("Supplier %s SUSPENDED: %s", supplier_id, reason)

    # ── Performance Scoring ─────────────────────────────────────────────────────
    def calculate_scores(self) -> list[dict]:
        """
        Compute composite performance score (0-100) for each supplier.
        Factors: on-time delivery, quality, lead time, response time, certs.
        """
        results = []
        for sup in self.suppliers:
            if sup.total_orders == 0:
                otd = 0.5
            else:
                otd = sup.on_time_count / sup.total_orders

            quality_factor = sup.quality_score / 5.0
            lead_factor = max(0, 1 - (sup.lead_time_days - 7) / 60)  # prefer short lead
            cert_factor = min(1.0, len(sup.certifications) * 0.2)
            # Contract risk
            contract_risk = 0.0
            if sup.contract_end:
                days_left = (datetime.fromisoformat(sup.contract_end) - datetime.utcnow()).days
                if days_left < 0:
                    contract_risk = 0.3
                elif days_left < 30:
                    contract_risk = 0.1

            composite = (
                otd * 0.40 +
                quality_factor * 0.30 +
                lead_factor * 0.15 +
                cert_factor * 0.10 -
                contract_risk * 0.05
            ) * 100

            results.append({
                "id": sup.id,
                "name": sup.name,
                "category": sup.category,
                "country": sup.country,
                "status": sup.status,
                "composite_score": round(composite, 1),
                "otd_rate": round(otd * 100, 1),
                "quality_score": sup.quality_score,
                "lead_time_days": sup.lead_time_days,
                "risk_level": sup.risk_level,
                "contracts_expiring_days": (
                    (datetime.fromisoformat(sup.contract_end) - datetime.utcnow()).days
                    if sup.contract_end else None
                ),
            })
        return sorted(results, key=lambda x: x["composite_score"], reverse=True)

    # ── Purchase Order ─────────────────────────────────────────────────────────
    def create_po(self, supplier_id: str, items: list[dict],
                  expected_delivery: str, notes: str = "") -> PurchaseOrder:
        sup = next((s for s in self.suppliers if s.id == supplier_id), None)
        if not sup:
            raise ValueError(f"Supplier {supplier_id} not found")
        if sup.status not in ("active", "qualified"):
            log.warning("Supplier %s is %s — proceed with caution.", supplier_id, sup.status)

        total = sum(item["qty"] * item["unit_price"] for item in items)
        idx = len(self.orders) + 1
        po = PurchaseOrder(
            po_id=f"PO-{6000 + idx}",
            supplier_id=supplier_id,
            supplier_name=sup.name,
            items=items,
            total_value=round(total, 2),
            order_date=datetime.utcnow().isoformat()[:10],
            expected_delivery=expected_delivery,
            status="issued",
            notes=notes,
        )
        self.orders.append(po)
        sup.total_orders += 1
        self._save_orders()
        self._save_suppliers()
        log.info("Created PO %s → %s (%.2f EUR)", po.po_id, sup.name, total)
        return po

    def receive_po(self, po_id: str):
        po = next((p for p in self.orders if p.po_id == po_id), None)
        if not po:
            raise ValueError(f"PO {po_id} not found")
        if po.status == "delivered":
            log.warning("PO %s already delivered.", po_id)
            return
        now = datetime.utcnow()
        po.actual_delivery = now.isoformat()[:10]
        po.status = "delivered"
        expected = datetime.fromisoformat(po.expected_delivery)
        po.on_time = now <= expected
        sup = next((s for s in self.suppliers if s.id == po.supplier_id), None)
        if sup:
            sup.total_orders += 1
            if po.on_time:
                sup.on_time_count += 1
            self._save_suppliers()
        self._save_orders()
        log.info("PO %s received (on_time=%s)", po_id, po.on_time)

    # ── Risk Assessment ─────────────────────────────────────────────────────────
    def risk_report(self) -> list[dict]:
        """Identify suppliers with elevated risk."""
        now = datetime.utcnow()
        report = []
        for sup in self.suppliers:
            flags = []
            score = 0

            if sup.contract_end:
                days_left = (datetime.fromisoformat(sup.contract_end) - now).days
                if days_left < 0:
                    flags.append("CONTRACT EXPIRED")
                    score += 40
                elif days_left < 30:
                    flags.append(f"Contract expires in {days_left}d")
                    score += 20

            if sup.total_orders > 0:
                otd = sup.on_time_count / sup.total_orders
                if otd < 0.70:
                    flags.append(f"OTD {otd*100:.0f}%")
                    score += 30

            if sup.quality_score < 3.0:
                flags.append(f"Quality {sup.quality_score}")
                score += 20

            if sup.risk_level in ("high", "critical"):
                flags.append(f"Risk: {sup.risk_level}")
                score += 15

            if len(sup.certifications) == 0:
                flags.append("No certifications")
                score += 10

            risk_label = (
                "🔴 CRITICAL" if score >= 50
                else "🟠 HIGH" if score >= 30
                else "🟡 MEDIUM" if score >= 15
                else "🟢 LOW"
            )
            report.append({
                "id": sup.id,
                "name": sup.name,
                "category": sup.category,
                "country": sup.country,
                "status": sup.status,
                "flags": flags,
                "risk_score": score,
                "risk_label": risk_label,
            })
        return sorted(report, key=lambda x: x["risk_score"], reverse=True)

    # ── Print Methods ───────────────────────────────────────────────────────────
    def print_supplier_list(self):
        if not self.suppliers:
            print("No suppliers found.")
            return
        print("\n🏭 SUPPLIER REGISTRY ──────────────────────────────────────────────────")
        print(f"{'ID':<10} {'Name':<22} {'Category':<14} {'Country':<8} "
              f"{'Status':<12} {'Rating':>7} {'Risk':<10}")
        print("─" * 88)
        for s in self.suppliers:
            icon = self.RISK_WEIGHTS.get(s.risk_level, {}).get("icon", " ")
            print(
                f"{s.id:<10} {s.name:<22} {s.category:<14} {s.country:<8} "
                f"{s.status:<12} {s.rating:>5.1f}★ {icon} {s.risk_level:<8}"
            )

    def print_scores(self):
        scores = self.calculate_scores()
        print("\n📊 SUPPLIER PERFORMANCE SCORES ───────────────────────────────────────")
        print(f"{'Rank':<5} {'Supplier':<22} {'Score':>7} {'OTD%':>7} "
              f"{'Quality':>8} {'Lead':>6} {'Contract':>10} {'Risk':<10}")
        print("─" * 85)
        for rank, s in enumerate(scores, 1):
            contract_str = (
                f"{s['contracts_expiring_days']}d"
                if s["contracts_expiring_days"] is not None else "—"
            )
            if s["contracts_expiring_days"] is not None and s["contracts_expiring_days"] < 30:
                contract_str = f"⚠{contract_str}"
            print(
                f"{rank:<5} {s['name']:<22} {s['composite_score']:>6.1f} "
                f"{s['otd_rate']:>6.1f}% {s['quality_score']:>7.1f}★ "
                f"{s['lead_time_days']:>5}d {contract_str:>10} {s['risk_level']:<10}"
            )

    def print_risk(self):
        risks = self.risk_report()
        print("\n⚠️  SUPPLIER RISK REPORT ──────────────────────────────────────────────")
        print(f"{'Supplier':<22} {'Country':<8} {'Status':<12} "
              f"{'Risk Score':>11} {'Risk Label':<12} {'Flags'}")
        print("─" * 85)
        for r in risks:
            flags = "; ".join(r["flags"]) if r["flags"] else "—"
            print(
                f"{r['name']:<22} {r['country']:<8} {r['status']:<12} "
                f"{r['risk_score']:>10} {r['risk_label']:<12} {flags}"
            )

    def print_orders(self, days: int = 30):
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = [o for o in self.orders
                  if datetime.fromisoformat(o.order_date) >= cutoff]
        if not recent:
            print(f"\nNo orders in the last {days} days.")
            return
        print(f"\n📦 PURCHASE ORDERS (last {days} days) ─────────────────────────────────")
        print(f"{'PO-ID':<10} {'Supplier':<22} {'Date':<12} {'Expected':<12} "
              f"{'Delivered':<12} {'Value':>10} {'Status':<12} {'OT?'}")
        print("─" * 108)
        for o in sorted(recent, key=lambda x: x.order_date, reverse=True):
            ot = "✅" if o.on_time else "❌" if o.on_time is False else "—"
            print(
                f"{o.po_id:<10} {o.supplier_name:<22} {o.order_date:<12} "
                f"{o.expected_delivery:<12} {(o.actual_delivery or '—'):<12} "
                f"{o.total_value:>10.2f} {o.status:<12} {ot}"
            )

    def print_contract_expiry(self):
        now = datetime.utcnow()
        upcoming = []
        for s in self.suppliers:
            if not s.contract_end:
                continue
            days_left = (datetime.fromisoformat(s.contract_end) - now).days
            upcoming.append({
                "name": s.name, "id": s.id,
                "contract_end": s.contract_end,
                "days_left": days_left,
                "status": s.status,
            })
        if not upcoming:
            print("\nNo contract expiry data available.")
            return
        print("\n📄 CONTRACT EXPIRY ───────────────────────────────────────────────────")
        print(f"{'Supplier':<22} {'Contract End':<14} {'Days Left':>9} {'Status':<12}")
        print("─" * 62)
        for s in sorted(upcoming, key=lambda x: x["days_left"]):
            warning = "⚠️" if s["days_left"] < 60 else ""
            print(
                f"{s['name']:<22} {s['contract_end']:<14} "
                f"{s['days_left']:>7} {warning} {s['status']:<12}"
            )


# ── CLI ───────────────────────────────────────────────────────────────────────
def build_parser():
    parser = argparse.ArgumentParser(
        prog="supplier_manager_agent.py",
        description="Supplier Manager — supplier records, performance scoring, POs, risk.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --simulate                Generate sample supplier + PO data
  %(prog)s --list                    List all suppliers
  %(prog)s --score                   Print performance scores
  %(prog)s --risk                    Print risk assessment
  %(prog)s --orders                  Show recent purchase orders
  %(prog)s --contract-expiry         Show contract expiry timeline
  %(prog)s --order SUP-001 --items data/po_items.json --delivery 2026-04-15
  %(prog)s --receive PO-6001         Mark PO as received
  %(prog)s --suspend SUP-004 "Quality issues"
  %(prog)s --qualify data/supplier.json
        """,
    )
    parser.add_argument("--list", action="store_true", help="List all suppliers")
    parser.add_argument("--score", action="store_true",
                        help="Print performance score table")
    parser.add_argument("--risk", action="store_true",
                        help="Print supplier risk report")
    parser.add_argument("--orders", action="store_true",
                        help="Show recent purchase orders")
    parser.add_argument("--contract-expiry", action="store_true",
                        dest="contract_expiry",
                        help="Show contract expiry timeline")
    parser.add_argument("--simulate", action="store_true",
                        help="Generate sample data")
    parser.add_argument("--order", dest="supplier_id",
                        help="Create PO for supplier ID")
    parser.add_argument("--items", dest="items_file",
                        help="JSON file with PO line items")
    parser.add_argument("--delivery", dest="delivery_date",
                        help="Expected delivery date (YYYY-MM-DD)")
    parser.add_argument("--receive", dest="po_id",
                        help="Mark PO as received/delivered")
    parser.add_argument("--suspend", dest="suspend_id",
                        help="Suspend supplier (use with --reason)")
    parser.add_argument("--reason", dest="suspend_reason",
                        help="Reason for suspension")
    parser.add_argument("--qualify", dest="qualify_file",
                        help="Add/qualify new supplier from JSON file")
    parser.add_argument("--suppliers-file", dest="suppliers_file",
                        help="Path to suppliers JSON")
    parser.add_argument("--verbose", "-v", action="store_true")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    mgr = SupplierManager()
    try:
        if args.simulate:
            mgr.generate_sample_data()
        else:
            mgr.load_suppliers(args.suppliers_file)
        mgr.load_orders()

        if args.list:
            mgr.print_supplier_list()
            return

        if args.score:
            mgr.print_scores()
            return

        if args.risk:
            mgr.print_risk()
            return

        if args.orders:
            mgr.print_orders()
            return

        if args.contract_expiry:
            mgr.print_contract_expiry()
            return

        if getattr(args, "order", None):
            if not args.delivery_date:
                parser.error("--order requires --delivery")
            items = [{"sku": "AUTO-001", "description": "Auto-generated item",
                      "qty": 100, "unit_price": 10.0}]
            if args.items_file:
                items = load_json(args.items_file, [])
            po = mgr.create_po(args.order, items, args.delivery_date)
            print(f"✅ Created {po.po_id} — {po.total_value:.2f} EUR")
            return

        if getattr(args, "receive", None):
            mgr.receive_po(args.receive)
            print(f"✅ PO {args.receive} marked as delivered.")
            return

        if getattr(args, "suspend_id", None):
            if not args.suspend_reason:
                parser.error("--suspend requires --reason")
            mgr.suspend_supplier(args.suspend_id, args.suspend_reason)
            print(f"✅ Supplier {args.suspend_id} suspended.")
            return

        if getattr(args, "qualify_file", None):
            data = load_json(args.qualify_file, {})
            sup = mgr.add_supplier(data)
            print(f"✅ Qualified supplier {sup.id} — {sup.name}")
            return

        # Default: summary view
        mgr.print_supplier_list()
        mgr.print_scores()
        mgr.print_risk()

    except KeyboardInterrupt:
        log.info("Interrupted.")
        sys.exit(130)
    except ValueError as e:
        log.error("%s", e)
        sys.exit(1)
    except Exception as e:
        log.exception("Fatal error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
