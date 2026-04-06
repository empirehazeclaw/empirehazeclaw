#!/usr/bin/env python3
"""
Invoice Generator Agent
EmpireHazeClaw Finance Suite

Creates professional invoices, manages client data, stores in JSON.
Reads SOUL.md for business values: Eigenverantwortung, Integrität, Ressourceneffizienz.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "finance"
LOG_DIR = BASE_DIR / "logs"
INVOICES_FILE = DATA_DIR / "invoices.json"
CLIENTS_FILE = DATA_DIR / "clients.json"

# ─── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE = LOG_DIR / "invoice_generator.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("InvoiceGenerator")


# ─── Data Helpers ─────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict | list:
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return {} if ".json" in str(path) and "invoice" in str(path) else []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_invoices() -> dict:
    return load_json(INVOICES_FILE)


def save_invoices(data: dict) -> bool:
    return save_json(INVOICES_FILE, data)


def load_clients() -> list:
    data = load_json(CLIENTS_FILE)
    return data if isinstance(data, list) else []


def save_clients(data: list) -> bool:
    return save_json(CLIENTS_FILE, data)


def generate_invoice_number() -> str:
    now = datetime.utcnow()
    return f"INV-{now.year}{now.month:02d}-{uuid.uuid4().hex[:6].upper()}"


def format_currency(amount: float, currency: str = "EUR") -> str:
    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF"}
    sym = symbols.get(currency, currency + " ")
    return f"{sym}{amount:,.2f}"


# ─── Core Logic ────────────────────────────────────────────────────────────────
def create_invoice(
    client_id: str,
    items: list[dict],
    due_days: int = 30,
    currency: str = "EUR",
    notes: str = "",
    tax_rate: float = 0.0,
) -> dict:
    """Create a new invoice and save it."""
    logger.info("Creating invoice for client_id=%s", client_id)

    clients = load_clients()
    client = next((c for c in clients if c.get("id") == client_id), None)
    if not client:
        raise ValueError(f"Client not found: {client_id}")

    subtotal = sum(float(item.get("amount", 0)) for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    now = datetime.utcnow()
    invoice = {
        "id": str(uuid.uuid4()),
        "invoice_number": generate_invoice_number(),
        "client_id": client_id,
        "client_name": client.get("name", "Unknown"),
        "client_email": client.get("email", ""),
        "client_address": client.get("address", ""),
        "items": items,
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
        "currency": currency,
        "status": "draft",
        "issue_date": now.strftime("%Y-%m-%d"),
        "due_date": (now + timedelta(days=due_days)).strftime("%Y-%m-%d"),
        "notes": notes,
        "created_at": now.isoformat(),
        "paid_at": None,
    }

    invoices = load_invoices()
    invoices[invoice["id"]] = invoice
    save_invoices(invoices)

    logger.info("Invoice created: %s (total=%s)", invoice["invoice_number"], format_currency(total, currency))
    return invoice


def mark_paid(invoice_id: str) -> dict:
    """Mark an invoice as paid."""
    invoices = load_invoices()
    if invoice_id not in invoices:
        raise ValueError(f"Invoice not found: {invoice_id}")

    invoices[invoice_id]["status"] = "paid"
    invoices[invoice_id]["paid_at"] = datetime.utcnow().isoformat()
    save_invoices(invoices)
    logger.info("Invoice marked paid: %s", invoices[invoice_id]["invoice_number"])
    return invoices[invoice_id]


def cancel_invoice(invoice_id: str) -> dict:
    """Cancel an invoice."""
    invoices = load_invoices()
    if invoice_id not in invoices:
        raise ValueError(f"Invoice not found: {invoice_id}")

    invoices[invoice_id]["status"] = "cancelled"
    save_invoices(invoices)
    logger.info("Invoice cancelled: %s", invoices[invoice_id]["invoice_number"])
    return invoices[invoice_id]


def list_invoices(status: Optional[str] = None) -> list[dict]:
    """List all invoices, optionally filtered by status."""
    invoices = load_invoices()
    result = list(invoices.values())
    if status:
        result = [inv for inv in result if inv.get("status") == status]
    result.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return result


def get_invoice(invoice_id: str) -> dict:
    invoices = load_invoices()
    if invoice_id not in invoices:
        raise ValueError(f"Invoice not found: {invoice_id}")
    return invoices[invoice_id]


def render_text(invoice: dict) -> str:
    """Render a plain-text invoice for console output."""
    lines = [
        "=" * 60,
        f"  INVOICE  —  {invoice['invoice_number']}",
        "=" * 60,
        "",
        f"  Client   : {invoice['client_name']}",
        f"  Email    : {invoice['client_email']}",
        f"  Address  : {invoice['client_address']}",
        f"  Issue Date : {invoice['issue_date']}",
        f"  Due Date   : {invoice['due_date']}",
        f"  Status   : {invoice['status'].upper()}",
        "",
        "  LINE ITEMS",
        "  " + "-" * 54,
        f"  {'Description':<36} {'Qty':>5} {'Amount':>14}",
        "  " + "-" * 54,
    ]
    for item in invoice.get("items", []):
        desc = item.get("description", "")
        qty = item.get("quantity", 1)
        amt = float(item.get("amount", 0))
        lines.append(f"  {desc:<36} {qty:>5} {format_currency(amt, invoice['currency']):>14}")
        if item.get("unit_price"):
            lines.append(f"    unit price: {format_currency(float(item['unit_price']), invoice['currency'])}")

    lines.extend(
        [
            "  " + "-" * 54,
            f"  {'Subtotal':<36} {'':>5} {format_currency(invoice['subtotal'], invoice['currency']):>14}",
        ]
    )
    if invoice.get("tax_rate", 0) > 0:
        lines.append(
            f"  {'Tax (' + str(invoice['tax_rate']) + '%)':<36} {'':>5} {format_currency(invoice['tax_amount'], invoice['currency']):>14}"
        )
    lines.append("  " + "=" * 54)
    lines.append(
        f"  {'TOTAL':<36} {'':>5} {format_currency(invoice['total'], invoice['currency']):>14}"
    )
    lines.append("  " + "=" * 54)
    if invoice.get("notes"):
        lines.append(f"\n  Notes: {invoice['notes']}")
    return "\n".join(lines)


# ─── Client Management ────────────────────────────────────────────────────────
def add_client(name: str, email: str, address: str = "", company: str = "") -> dict:
    clients = load_clients()
    client = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "address": address,
        "company": company,
        "created_at": datetime.utcnow().isoformat(),
    }
    clients.append(client)
    save_clients(clients)
    logger.info("Client added: %s <%s>", name, email)
    return client


def list_clients() -> list:
    return load_clients()


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_create(args):
    items = []
    if args.item:
        for spec in args.item:
            # format: "Description;amount" or "Description;amount;quantity"
            parts = spec.split(";")
            desc = parts[0]
            amount = float(parts[1]) if len(parts) > 1 else 0.0
            qty = int(parts[2]) if len(parts) > 2 else 1
            items.append({"description": desc, "amount": amount * qty, "quantity": qty, "unit_price": amount})
    if not items:
        items = [{"description": "Professional Services", "amount": 0.0, "quantity": 1, "unit_price": 0.0}]

    inv = create_invoice(
        client_id=args.client_id,
        items=items,
        due_days=args.due_days,
        currency=args.currency.upper(),
        notes=args.notes or "",
        tax_rate=args.tax_rate,
    )
    print(render_text(inv))
    print(f"\n✅ Invoice saved: {INVOICES_FILE}")


def cmd_list(args):
    invoices = list_invoices(status=args.status)
    if not invoices:
        print("No invoices found.")
        return
    print(f"\n{'#':<4} {'Number':<20} {'Client':<25} {'Total':<12} {'Status':<10} {'Due Date'}")
    print("-" * 100)
    for i, inv in enumerate(invoices, 1):
        print(
            f"{i:<4} {inv['invoice_number']:<20} {inv['client_name']:<25} "
            f"{format_currency(inv['total'], inv['currency']):<12} "
            f"{inv['status']:<10} {inv['due_date']}"
        )
    print(f"\nTotal: {len(invoices)} invoice(s)")


def cmd_show(args):
    inv = get_invoice(args.invoice_id)
    print(render_text(inv))


def cmd_paid(args):
    inv = mark_paid(args.invoice_id)
    print(f"✅ Invoice {inv['invoice_number']} marked as PAID")


def cmd_cancel(args):
    inv = cancel_invoice(args.invoice_id)
    print(f"✅ Invoice {inv['invoice_number']} CANCELLED")


def cmd_add_client(args):
    client = add_client(name=args.name, email=args.email, address=args.address or "", company=args.company or "")
    print(f"✅ Client added: {client['id']}")
    print(f"   {client['name']} <{client['email']}>")


def cmd_list_clients(args):
    clients = list_clients()
    if not clients:
        print("No clients found. Add one with: invoice-generator add-client ...")
        return
    print(f"\n{'#':<4} {'Name':<30} {'Email':<35} {'Company'}")
    print("-" * 100)
    for i, c in enumerate(clients, 1):
        print(f"{i:<4} {c.get('name',''):<30} {c.get('email',''):<35} {c.get('company','')}")
    print(f"\nTotal: {len(clients)} client(s)")


def cmd_stats(args):
    invoices = list_invoices()
    total = sum(inv["total"] for inv in invoices if inv["status"] == "paid")
    pending = sum(inv["total"] for inv in invoices if inv["status"] not in ("paid", "cancelled"))
    cancelled = sum(inv["total"] for inv in invoices if inv["status"] == "cancelled")
    currency = "EUR"
    print("\n📊 Invoice Statistics")
    print("=" * 40)
    print(f"  Total Invoices : {len(invoices)}")
    print(f"  Paid           : {len([i for i in invoices if i['status']=='paid'])}")
    print(f"  Pending        : {len([i for i in invoices if i['status'] not in ('paid','cancelled')])}")
    print(f"  Cancelled      : {len([i for i in invoices if i['status']=='cancelled'])}")
    print(f"  Revenue (paid) : {format_currency(total, currency)}")
    print(f"  Outstanding     : {format_currency(pending, currency)}")
    print(f"  Cancelled Sum  : {format_currency(cancelled, currency)}")


def main():
    parser = argparse.ArgumentParser(
        prog="invoice-generator",
        description="EmpireHazeClaw Invoice Generator — create and manage invoices.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a new invoice")
    p_create.add_argument("--client-id", required=True, help="Client ID")
    p_create.add_argument("--item", action="append", help="Item as 'description;amount' or 'description;amount;qty'")
    p_create.add_argument("--due-days", type=int, default=30, help="Payment due days (default: 30)")
    p_create.add_argument("--currency", default="EUR", help="Currency (EUR/USD/GBP/CHF)")
    p_create.add_argument("--tax-rate", type=float, default=0.0, help="Tax rate in %% (default: 0)")
    p_create.add_argument("--notes", help="Invoice notes")
    p_create.set_defaults(fn=cmd_create)

    # list
    p_list = sub.add_parser("list", help="List all invoices")
    p_list.add_argument("--status", help="Filter by status: draft/paid/cancelled")
    p_list.set_defaults(fn=cmd_list)

    # show
    p_show = sub.add_parser("show", help="Show invoice details")
    p_show.add_argument("invoice_id", help="Invoice ID or invoice number")
    p_show.set_defaults(fn=cmd_show)

    # paid
    p_paid = sub.add_parser("paid", help="Mark invoice as paid")
    p_paid.add_argument("invoice_id", help="Invoice ID or invoice number")
    p_paid.set_defaults(fn=cmd_paid)

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel an invoice")
    p_cancel.add_argument("invoice_id", help="Invoice ID or invoice number")
    p_cancel.set_defaults(fn=cmd_cancel)

    # add-client
    p_ac = sub.add_parser("add-client", help="Add a new client")
    p_ac.add_argument("--name", required=True, help="Client name")
    p_ac.add_argument("--email", required=True, help="Client email")
    p_ac.add_argument("--address", help="Client address")
    p_ac.add_argument("--company", help="Company name")
    p_ac.set_defaults(fn=cmd_add_client)

    # list-clients
    p_lc = sub.add_parser("list-clients", help="List all clients")
    p_lc.set_defaults(fn=cmd_list_clients)

    # stats
    p_stats = sub.add_parser("stats", help="Show invoice statistics")
    p_stats.set_defaults(fn=cmd_stats)

    args = parser.parse_args()

    # Resolve invoice_id by number if needed
    if hasattr(args, "invoice_id") and args.invoice_id:
        if not args.invoice_id.startswith("/"):
            invoices = load_invoices()
            found = next((iid for iid, inv in invoices.items() if inv["invoice_number"] == args.invoice_id), None)
            if found:
                args.invoice_id = found

    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
