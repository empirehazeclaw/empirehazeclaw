#!/usr/bin/env python3
"""
Invoice Automation Agent
Handles creation, tracking, and management of invoices.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE_DIR / "data" / "finance"
LOG_DIR = WORKSPACE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

INVOICES_FILE = DATA_DIR / "invoices.json"
COUNTERS_FILE = DATA_DIR / "invoice_counters.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "invoice_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("InvoiceAutomation")


def load_json(filepath, default):
    """Load JSON file or return default."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {filepath}: {e}")
    return default


def save_json(filepath, data):
    """Save data to JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def load_invoices():
    """Load invoices from file."""
    return load_json(INVOICES_FILE, {"invoices": []})


def load_counters():
    """Load counters from file."""
    return load_json(COUNTERS_FILE, {"invoice_number": 1000})


def save_invoices(data):
    """Save invoices to file."""
    return save_json(INVOICES_FILE, data)


def save_counters(data):
    """Save counters to file."""
    return save_json(COUNTERS_FILE, data)


def generate_invoice_number():
    """Generate unique invoice number."""
    counters = load_counters()
    counters["invoice_number"] += 1
    save_counters(counters)
    year = datetime.now().year
    return f"INV-{year}-{counters['invoice_number']:04d}"


def create_invoice(client_name, amount, description, due_days=30, items=None):
    """Create a new invoice."""
    logger.info(f"Creating invoice for {client_name}: {amount}")
    
    invoices_data = load_invoices()
    
    due_date = datetime.now() + timedelta(days=due_days)
    
    invoice = {
        "id": str(uuid.uuid4()),
        "invoice_number": generate_invoice_number(),
        "client_name": client_name,
        "description": description,
        "amount": float(amount),
        "currency": "EUR",
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "due_date": due_date.isoformat(),
        "paid_date": None,
        "items": items or [{"description": description, "amount": float(amount)}]
    }
    
    invoices_data["invoices"].append(invoice)
    
    if save_invoices(invoices_data):
        logger.info(f"Invoice {invoice['invoice_number']} created successfully")
        return invoice
    else:
        logger.error("Failed to save invoice")
        return None


def list_invoices(status=None):
    """List all invoices, optionally filtered by status."""
    invoices_data = load_invoices()
    invoices = invoices_data.get("invoices", [])
    
    if status:
        invoices = [inv for inv in invoices if inv["status"] == status]
    
    return sorted(invoices, key=lambda x: x["created_at"], reverse=True)


def get_invoice(invoice_id_or_number):
    """Get invoice by ID or number."""
    invoices_data = load_invoices()
    for inv in invoices_data.get("invoices", []):
        if inv["id"] == invoice_id_or_number or inv["invoice_number"] == invoice_id_or_number:
            return inv
    return None


def update_invoice_status(invoice_id_or_number, new_status):
    """Update invoice status."""
    valid_statuses = ["draft", "sent", "paid", "overdue", "cancelled"]
    if new_status not in valid_statuses:
        logger.error(f"Invalid status: {new_status}. Valid: {valid_statuses}")
        return None
    
    invoices_data = load_invoices()
    
    for inv in invoices_data.get("invoices", []):
        if inv["id"] == invoice_id_or_number or inv["invoice_number"] == invoice_id_or_number:
            old_status = inv["status"]
            inv["status"] = new_status
            
            if new_status == "paid":
                inv["paid_date"] = datetime.now().isoformat()
            
            if save_invoices(invoices_data):
                logger.info(f"Invoice {inv['invoice_number']} status: {old_status} -> {new_status}")
                return inv
            break
    
    logger.warning(f"Invoice not found: {invoice_id_or_number}")
    return None


def delete_invoice(invoice_id_or_number):
    """Delete an invoice (only drafts)."""
    invoices_data = load_invoices()
    
    for i, inv in enumerate(invoices_data.get("invoices", [])):
        if inv["id"] == invoice_id_or_number or inv["invoice_number"] == invoice_id_or_number:
            if inv["status"] != "draft":
                logger.error(f"Cannot delete non-draft invoice {inv['invoice_number']}")
                return False
            
            deleted = invoices_data["invoices"].pop(i)
            if save_invoices(invoices_data):
                logger.info(f"Deleted invoice {deleted['invoice_number']}")
                return True
            break
    
    logger.warning(f"Invoice not found: {invoice_id_or_number}")
    return False


def send_invoice(invoice_id_or_number):
    """Mark invoice as sent."""
    return update_invoice_status(invoice_id_or_number, "sent")


def mark_paid(invoice_id_or_number):
    """Mark invoice as paid."""
    return update_invoice_status(invoice_id_or_number, "paid")


def get_summary():
    """Get invoice summary statistics."""
    invoices_data = load_invoices()
    invoices = invoices_data.get("invoices", [])
    
    summary = {
        "total": len(invoices),
        "draft": 0,
        "sent": 0,
        "paid": 0,
        "overdue": 0,
        "cancelled": 0,
        "total_revenue": 0.0,
        "paid_revenue": 0.0,
        "pending_revenue": 0.0,
        "overdue_revenue": 0.0
    }
    
    now = datetime.now()
    
    for inv in invoices:
        summary[inv["status"]] = summary.get(inv["status"], 0) + 1
        summary["total_revenue"] += inv["amount"]
        
        if inv["status"] == "paid":
            summary["paid_revenue"] += inv["amount"]
        elif inv["status"] == "overdue":
            summary["overdue_revenue"] += inv["amount"]
        elif inv["status"] in ["sent", "draft"]:
            summary["pending_revenue"] += inv["amount"]
        
        # Auto-mark overdue
        if inv["status"] == "sent":
            due_date = datetime.fromisoformat(inv["due_date"])
            if due_date < now:
                update_invoice_status(inv["id"], "overdue")
                summary["overdue"] += 1
                summary["sent"] -= 1
                summary["overdue_revenue"] += inv["amount"]
                summary["pending_revenue"] -= inv["amount"]
    
    return summary


def print_invoice(inv):
    """Pretty print an invoice."""
    print(f"\n{'='*50}")
    print(f"Invoice: {inv['invoice_number']}")
    print(f"{'='*50}")
    print(f"Client:     {inv['client_name']}")
    print(f"Description: {inv['description']}")
    print(f"Amount:     {inv['amount']:.2f} {inv['currency']}")
    print(f"Status:     {inv['status'].upper()}")
    print(f"Created:    {inv['created_at'][:10]}")
    print(f"Due Date:   {inv['due_date'][:10]}")
    if inv.get("paid_date"):
        print(f"Paid:       {inv['paid_date'][:10]}")
    print(f"{'='*50}\n")


def cmd_create(args):
    """Handle create command."""
    items = None
    if args.items:
        try:
            items = json.loads(args.items)
        except:
            items = [{"description": args.description, "amount": float(args.amount)}]
    
    invoice = create_invoice(
        client_name=args.client,
        amount=args.amount,
        description=args.description,
        due_days=args.due_days,
        items=items
    )
    
    if invoice:
        print(f"✅ Invoice created: {invoice['invoice_number']}")
        print_invoice(invoice)
    else:
        print("❌ Failed to create invoice")
        sys.exit(1)


def cmd_list(args):
    """Handle list command."""
    invoices = list_invoices(status=args.status)
    
    if not invoices:
        print("No invoices found.")
        return
    
    print(f"\n📋 Found {len(invoices)} invoice(s):\n")
    for inv in invoices:
        status_icon = {"draft": "📝", "sent": "📤", "paid": "✅", "overdue": "⚠️", "cancelled": "❌"}.get(inv["status"], "•")
        print(f"  {status_icon} {inv['invoice_number']} | {inv['client_name']} | {inv['amount']:.2f} EUR | {inv['status']} | Due: {inv['due_date'][:10]}")


def cmd_show(args):
    """Handle show command."""
    invoice = get_invoice(args.invoice)
    if invoice:
        print_invoice(invoice)
    else:
        print(f"❌ Invoice not found: {args.invoice}")
        sys.exit(1)


def cmd_send(args):
    """Handle send command."""
    result = send_invoice(args.invoice)
    if result:
        print(f"✅ Invoice {result['invoice_number']} marked as sent")
    else:
        print("❌ Failed to send invoice")
        sys.exit(1)


def cmd_paid(args):
    """Handle paid command."""
    result = mark_paid(args.invoice)
    if result:
        print(f"✅ Invoice {result['invoice_number']} marked as paid")
    else:
        print("❌ Failed to mark invoice as paid")
        sys.exit(1)


def cmd_cancel(args):
    """Handle cancel command."""
    result = update_invoice_status(args.invoice, "cancelled")
    if result:
        print(f"✅ Invoice {result['invoice_number']} cancelled")
    else:
        print("❌ Failed to cancel invoice")
        sys.exit(1)


def cmd_delete(args):
    """Handle delete command."""
    if delete_invoice(args.invoice):
        print(f"✅ Invoice deleted")
    else:
        print("❌ Failed to delete invoice (only drafts can be deleted)")
        sys.exit(1)


def cmd_summary(args):
    """Handle summary command."""
    summary = get_summary()
    
    print(f"""
📊 Invoice Summary
{'='*40}
Total Invoices:  {summary['total']}
  📝 Draft:      {summary['draft']}
  📤 Sent:       {summary['sent']}
  ⚠️  Overdue:   {summary['overdue']}
  ✅ Paid:       {summary['paid']}
  ❌ Cancelled:  {summary['cancelled']}

💰 Revenue:
  Total Revenue:   {summary['total_revenue']:.2f} EUR
  Paid Revenue:    {summary['paid_revenue']:.2f} EUR
  Pending:         {summary['pending_revenue']:.2f} EUR
  Overdue:         {summary['overdue_revenue']:.2f} EUR
""")


def main():
    parser = argparse.ArgumentParser(
        description="Invoice Automation Agent - Manage invoices efficiently",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --client "Acme Corp" --amount 1500 --description "Web Development"
  %(prog)s list
  %(prog)s list --status overdue
  %(prog)s show INV-2026-0001
  %(prog)s paid INV-2026-0001
  %(prog)s summary
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new invoice")
    create_parser.add_argument("--client", required=True, help="Client name")
    create_parser.add_argument("--amount", required=True, type=float, help="Invoice amount")
    create_parser.add_argument("--description", required=True, help="Invoice description")
    create_parser.add_argument("--due-days", type=int, default=30, help="Days until due (default: 30)")
    create_parser.add_argument("--items", help="JSON array of line items")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all invoices")
    list_parser.add_argument("--status", choices=["draft", "sent", "paid", "overdue", "cancelled"], help="Filter by status")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show invoice details")
    show_parser.add_argument("invoice", help="Invoice ID or number")
    
    # Send command
    send_parser = subparsers.add_parser("send", help="Mark invoice as sent")
    send_parser.add_argument("invoice", help="Invoice ID or number")
    
    # Paid command
    paid_parser = subparsers.add_parser("paid", help="Mark invoice as paid")
    paid_parser.add_argument("invoice", help="Invoice ID or number")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an invoice")
    cancel_parser.add_argument("invoice", help="Invoice ID or number")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a draft invoice")
    delete_parser.add_argument("invoice", help="Invoice ID or number")
    
    # Summary command
    subparsers.add_parser("summary", help="Show invoice summary statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "show": cmd_show,
        "send": cmd_send,
        "paid": cmd_paid,
        "cancel": cmd_cancel,
        "delete": cmd_delete,
        "summary": cmd_summary
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
