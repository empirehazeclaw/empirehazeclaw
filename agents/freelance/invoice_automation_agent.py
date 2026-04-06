#!/usr/bin/env python3
"""
Invoice Automation Agent - Freelance Division
Automates invoice generation, tracking, and management.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Integrität
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "freelance"
INVOICES_FILE = DATA_DIR / "invoices.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - INVOICE-AUTOMATION - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "invoice_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_DUE_DAYS = 30
DEFAULT_CURRENCY = "USD"


def load_invoices():
    """Load invoices from JSON file."""
    if not INVOICES_FILE.exists():
        return {"invoices": [], "settings": {}, "version": "1.0"}
    try:
        with open(INVOICES_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse invoices file: {e}")
        return {"invoices": [], "settings": {}, "version": "1.0"}


def save_invoices(data):
    """Save invoices to JSON file."""
    try:
        with open(INVOICES_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data['invoices'])} invoices to {INVOICES_FILE}")
    except IOError as e:
        logger.error(f"Failed to save invoices: {e}")
        raise


def generate_invoice_number():
    """Generate a unique invoice number."""
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def create_invoice(client_id, client_name, client_email, items, 
                   due_days=None, notes=None, tax_rate=0):
    """Create a new invoice."""
    data = load_invoices()
    
    due_days = due_days or DEFAULT_DUE_DAYS
    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
    
    # Calculate totals
    subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount
    
    invoice = {
        "id": len(data['invoices']) + 1,
        "invoice_number": generate_invoice_number(),
        "client_id": client_id,
        "client_name": client_name,
        "client_email": client_email,
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
        "currency": DEFAULT_CURRENCY,
        "status": "draft",
        "issue_date": issue_date,
        "due_date": due_date,
        "paid_date": None,
        "notes": notes or "",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "reminders_sent": 0
    }
    
    data['invoices'].append(invoice)
    save_invoices(data)
    logger.info(f"Created invoice {invoice['invoice_number']} for {client_name}: ${total:.2f}")
    print(f"✅ Created invoice {invoice['invoice_number']}")
    print(f"   Client: {client_name}")
    print(f"   Total: ${total:.2f} ({DEFAULT_CURRENCY})")
    print(f"   Due: {due_date}")
    return invoice['invoice_number']


def list_invoices(status_filter=None):
    """List all invoices."""
    data = load_invoices()
    invoices = data['invoices']
    
    if status_filter:
        invoices = [inv for inv in invoices if inv.get('status') == status_filter]
    
    if not invoices:
        print("📭 No invoices found.")
        return
    
    status_icons = {
        "draft": "📝",
        "sent": "📧",
        "viewed": "👁️",
        "paid": "✅",
        "overdue": "⚠️",
        "cancelled": "❌"
    }
    
    print(f"\n📋 Invoices ({len(invoices)} total):")
    print("-" * 90)
    for inv in sorted(invoices, key=lambda x: x.get('created_at', ''), reverse=True):
        icon = status_icons.get(inv.get('status', 'draft'), "📄")
        print(f"{icon} [{inv['id']}] {inv['invoice_number']}")
        print(f"   {inv['client_name']} | ${inv['total']:.2f} | Due: {inv.get('due_date', 'N/A')}")
        print(f"   Status: {inv.get('status', 'draft').upper()} | Created: {inv.get('issue_date', 'N/A')}")
        print()


def get_invoice(invoice_id=None, invoice_number=None):
    """Get a specific invoice."""
    data = load_invoices()
    for inv in data['invoices']:
        if invoice_id and inv['id'] == invoice_id:
            return inv
        if invoice_number and inv['invoice_number'] == invoice_number:
            return inv
    return None


def show_invoice(invoice_id=None, invoice_number=None):
    """Display detailed invoice information."""
    inv = get_invoice(invoice_id, invoice_number)
    if not inv:
        print(f"❌ Invoice not found.")
        return
    
    status_icons = {
        "draft": "📝 Draft",
        "sent": "📧 Sent",
        "viewed": "👁️ Viewed",
        "paid": "✅ PAID",
        "overdue": "⚠️ OVERDUE",
        "cancelled": "❌ Cancelled"
    }
    
    print(f"\n🧾 Invoice Details:")
    print("=" * 60)
    print(f"ID:             {inv['id']}")
    print(f"Invoice #:      {inv['invoice_number']}")
    print(f"Status:         {status_icons.get(inv.get('status'), inv.get('status'))}")
    print(f"Client ID:      {inv.get('client_id', 'N/A')}")
    print(f"Client:         {inv['client_name']}")
    print(f"Email:          {inv['client_email']}")
    print(f"Issue Date:     {inv.get('issue_date', 'N/A')}")
    print(f"Due Date:       {inv.get('due_date', 'N/A')}")
    if inv.get('paid_date'):
        print(f"Paid Date:      {inv['paid_date']}")
    print()
    print(f"Items:")
    print("-" * 50)
    for i, item in enumerate(inv.get('items', []), 1):
        line_total = item['quantity'] * item['unit_price']
        print(f"  {i}. {item.get('description', 'Item')}")
        print(f"     Qty: {item['quantity']} × ${item['unit_price']:.2f} = ${line_total:.2f}")
    
    print("-" * 50)
    print(f"Subtotal:    ${inv['subtotal']:.2f}")
    if inv.get('tax_rate', 0) > 0:
        print(f"Tax ({inv['tax_rate']}%): ${inv['tax_amount']:.2f}")
    print(f"TOTAL:       ${inv['total']:.2f} {inv.get('currency', 'USD')}")
    
    if inv.get('notes'):
        print(f"\nNotes: {inv['notes']}")
    
    if inv.get('reminders_sent', 0) > 0:
        print(f"\nReminders Sent: {inv['reminders_sent']}")


def update_status(invoice_id=None, invoice_number=None, new_status=None):
    """Update invoice status."""
    if not new_status:
        print("❌ Please specify --status")
        return False
    
    data = load_invoices()
    valid_statuses = ["draft", "sent", "viewed", "paid", "overdue", "cancelled"]
    
    if new_status not in valid_statuses:
        print(f"❌ Invalid status. Choose: {', '.join(valid_statuses)}")
        return False
    
    for inv in data['invoices']:
        if (invoice_id and inv['id'] == invoice_id) or \
           (invoice_number and inv['invoice_number'] == invoice_number):
            old_status = inv.get('status')
            inv['status'] = new_status
            inv['updated_at'] = datetime.now().isoformat()
            
            if new_status == 'paid' and not inv.get('paid_date'):
                inv['paid_date'] = datetime.now().strftime("%Y-%m-%d")
            
            save_invoices(data)
            logger.info(f"Updated invoice {inv['invoice_number']} status: {old_status} -> {new_status}")
            print(f"✅ Updated invoice {inv['invoice_number']} status to {new_status.upper()}")
            return True
    
    print(f"❌ Invoice not found.")
    return False


def mark_paid(invoice_id=None, invoice_number=None, paid_date=None):
    """Mark invoice as paid."""
    data = load_invoices()
    
    for inv in data['invoices']:
        if (invoice_id and inv['id'] == invoice_id) or \
           (invoice_number and inv['invoice_number'] == invoice_number):
            inv['status'] = 'paid'
            inv['paid_date'] = paid_date or datetime.now().strftime("%Y-%m-%d")
            inv['updated_at'] = datetime.now().isoformat()
            save_invoices(data)
            logger.info(f"Marked invoice {inv['invoice_number']} as paid on {inv['paid_date']}")
            print(f"✅ Marked invoice {inv['invoice_number']} as PAID")
            return True
    
    print(f"❌ Invoice not found.")
    return False


def send_reminder(invoice_id=None, invoice_number=None):
    """Simulate sending a payment reminder."""
    data = load_invoices()
    
    for inv in data['invoices']:
        if (invoice_id and inv['id'] == invoice_id) or \
           (invoice_number and inv['invoice_number'] == invoice_number):
            inv['reminders_sent'] = inv.get('reminders_sent', 0) + 1
            inv['updated_at'] = datetime.now().isoformat()
            save_invoices(data)
            logger.info(f"Sent reminder #{inv['reminders_sent']} for invoice {inv['invoice_number']}")
            print(f"✅ Sent payment reminder #{inv['reminders_sent']} for invoice {inv['invoice_number']}")
            print(f"   To: {inv['client_email']}")
            return True
    
    print(f"❌ Invoice not found.")
    return False


def cancel_invoice(invoice_id=None, invoice_number=None):
    """Cancel an invoice."""
    return update_status(invoice_id, invoice_number, "cancelled")


def delete_invoice(invoice_id=None, invoice_number=None):
    """Delete an invoice (only drafts)."""
    data = load_invoices()
    
    for i, inv in enumerate(data['invoices']):
        if (invoice_id and inv['id'] == invoice_id) or \
           (invoice_number and inv['invoice_number'] == invoice_number):
            if inv.get('status') != 'draft':
                print(f"❌ Can only delete draft invoices. Current status: {inv.get('status')}")
                return False
            data['invoices'].pop(i)
            save_invoices(data)
            logger.info(f"Deleted invoice {inv['invoice_number']}")
            print(f"✅ Deleted invoice {inv['invoice_number']}")
            return True
    
    print(f"❌ Invoice not found.")
    return False


def generate_invoice_text(invoice_id=None, invoice_number=None):
    """Generate plain text invoice for email."""
    inv = get_invoice(invoice_id, invoice_number)
    if not inv:
        print(f"❌ Invoice not found.")
        return None
    
    lines = [
        f"INVOICE",
        f"=" * 50,
        f"",
        f"Invoice #:     {inv['invoice_number']}",
        f"Date:          {inv.get('issue_date', 'N/A')}",
        f"Due Date:      {inv.get('due_date', 'N/A')}",
        f"",
        f"FROM:",
        f"  Your Business Name",
        f"  your@email.com",
        f"",
        f"TO:",
        f"  {inv['client_name']}",
        f"  {inv['client_email']}",
        f"",
        f"ITEMS:",
        "-" * 50,
    ]
    
    for i, item in enumerate(inv.get('items', []), 1):
        line_total = item['quantity'] * item['unit_price']
        lines.append(f"  {i}. {item.get('description', 'Item')}")
        lines.append(f"     {item['quantity']} x ${item['unit_price']:.2f} = ${line_total:.2f}")
    
    lines.extend([
        "-" * 50,
        f"Subtotal:      ${inv['subtotal']:.2f}",
    ])
    
    if inv.get('tax_rate', 0) > 0:
        lines.append(f"Tax ({inv['tax_rate']}%):   ${inv['tax_amount']:.2f}")
    
    lines.extend([
        f"TOTAL:         ${inv['total']:.2f} {inv.get('currency', 'USD')}",
        "",
    ])
    
    if inv.get('notes'):
        lines.append(f"Notes: {inv['notes']}")
    
    return "\n".join(lines)


def get_stats():
    """Show invoice statistics."""
    data = load_invoices()
    invoices = data['invoices']
    
    total = len(invoices)
    by_status = {}
    total_revenue = 0
    total_outstanding = 0
    
    for inv in invoices:
        status = inv.get('status', 'draft')
        by_status[status] = by_status.get(status, 0) + 1
        total_revenue += inv.get('total', 0)
        if status in ['sent', 'viewed', 'overdue']:
            total_outstanding += inv.get('total', 0)
    
    paid_revenue = sum(inv.get('total', 0) for inv in invoices if inv.get('status') == 'paid')
    
    # Find overdue
    today = datetime.now().date()
    overdue_count = 0
    overdue_amount = 0
    for inv in invoices:
        if inv.get('due_date') and inv.get('status') in ['sent', 'viewed', 'overdue']:
            try:
                due = datetime.strptime(inv['due_date'], "%Y-%m-%d").date()
                if due < today:
                    overdue_count += 1
                    overdue_amount += inv.get('total', 0)
                    if inv.get('status') != 'overdue':
                        inv['status'] = 'overdue'
            except ValueError:
                pass
    
    if overdue_count > 0:
        save_invoices(data)
    
    status_icons = {
        "draft": "📝",
        "sent": "📧",
        "viewed": "👁️",
        "paid": "✅",
        "overdue": "⚠️",
        "cancelled": "❌"
    }
    
    print(f"\n📊 Invoice Statistics:")
    print("=" * 40)
    print(f"Total Invoices:    {total}")
    print(f"Total Revenue:     ${total_revenue:.2f}")
    print(f"Paid Revenue:      ${paid_revenue:.2f} ✅")
    print(f"Outstanding:       ${total_outstanding:.2f}")
    print(f"Overdue:           ${overdue_amount:.2f} ⚠️ ({overdue_count} invoices)")
    print(f"\nBy Status:")
    for status, count in by_status.items():
        icon = status_icons.get(status, "📄")
        print(f"  {icon} {status.upper()}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="Invoice Automation Agent - Manage your freelance invoices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --client-id 1 --client-name "John Doe" --client-email john@example.com \\
    --item "Website Design" --qty 1 --price 1500 --item "Logo Design" --qty 1 --price 500 \\
    --due-days 30 --tax 10
  
  %(prog)s list
  %(prog)s list --status overdue
  %(prog)s show --number INV-20260327-ABC123
  %(prog)s show 1
  %(prog)s status 1 --status sent
  %(prog)s paid --number INV-20260327-ABC123
  %(prog)s remind --number INV-20260327-ABC123
  %(prog)s cancel 1
  %(prog)s delete 1
  %(prog)s text --number INV-20260327-ABC123
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create invoice
    create_parser = subparsers.add_parser('create', help='Create a new invoice')
    create_parser.add_argument('--client-id', type=int, required=True, help='Client ID')
    create_parser.add_argument('--client-name', required=True, help='Client name')
    create_parser.add_argument('--client-email', required=True, help='Client email')
    create_parser.add_argument('--item', '-i', action='append', help='Item description (can repeat)')
    create_parser.add_argument('--qty', '-q', type=float, action='append', help='Quantity (per item)')
    create_parser.add_argument('--price', '-p', type=float, action='append', help='Unit price (per item)')
    create_parser.add_argument('--due-days', type=int, default=30, help='Days until due')
    create_parser.add_argument('--tax', type=float, default=0, help='Tax rate %%')
    create_parser.add_argument('--notes', help='Invoice notes')
    
    # List invoices
    list_parser = subparsers.add_parser('list', help='List all invoices')
    list_parser.add_argument('--status', '-s', choices=['draft', 'sent', 'viewed', 'paid', 'overdue', 'cancelled'],
                            help='Filter by status')
    
    # Show invoice
    show_parser = subparsers.add_parser('show', help='Show invoice details')
    show_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    show_parser.add_argument('--number', help='Invoice number')
    
    # Update status
    status_parser = subparsers.add_parser('status', help='Update invoice status')
    status_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    status_parser.add_argument('--number', help='Invoice number')
    status_parser.add_argument('--status', '-s', required=True, 
                              choices=['draft', 'sent', 'viewed', 'paid', 'overdue', 'cancelled'],
                              help='New status')
    
    # Mark paid
    paid_parser = subparsers.add_parser('paid', help='Mark invoice as paid')
    paid_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    paid_parser.add_argument('--number', help='Invoice number')
    paid_parser.add_argument('--date', help='Payment date (YYYY-MM-DD)')
    
    # Send reminder
    remind_parser = subparsers.add_parser('remind', help='Send payment reminder')
    remind_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    remind_parser.add_argument('--number', help='Invoice number')
    
    # Cancel invoice
    cancel_parser = subparsers.add_parser('cancel', help='Cancel invoice')
    cancel_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    cancel_parser.add_argument('--number', help='Invoice number')
    
    # Delete invoice
    delete_parser = subparsers.add_parser('delete', help='Delete draft invoice')
    delete_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    delete_parser.add_argument('--number', help='Invoice number')
    
    # Generate text invoice
    text_parser = subparsers.add_parser('text', help='Generate plain text invoice')
    text_parser.add_argument('invoice_id', nargs='?', type=int, help='Invoice ID')
    text_parser.add_argument('--number', help='Invoice number')
    
    # Stats
    subparsers.add_parser('stats', help='Show invoice statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'create':
            # Build items list
            items = []
            item_names = args.item or []
            quantities = args.qty or []
            prices = args.price or []
            
            for i in range(len(item_names)):
                items.append({
                    "description": item_names[i],
                    "quantity": quantities[i] if i < len(quantities) else 1,
                    "unit_price": prices[i] if i < len(prices) else 0
                })
            
            if not items:
                print("❌ Please specify at least one item with --item, --qty, and --price")
                return
            
            create_invoice(args.client_id, args.client_name, args.client_email, 
                          items, args.due_days, args.notes, args.tax)
        
        elif args.command == 'list':
            list_invoices(args.status)
        
        elif args.command == 'show':
            show_invoice(args.invoice_id, args.number)
        
        elif args.command == 'status':
            update_status(args.invoice_id, args.number, args.status)
        
        elif args.command == 'paid':
            mark_paid(args.invoice_id, args.number, args.date)
        
        elif args.command == 'remind':
            send_reminder(args.invoice_id, args.number)
        
        elif args.command == 'cancel':
            cancel_invoice(args.invoice_id, args.number)
        
        elif args.command == 'delete':
            delete_invoice(args.invoice_id, args.number)
        
        elif args.command == 'text':
            text = generate_invoice_text(args.invoice_id, args.number)
            if text:
                print(text)
        
        elif args.command == 'stats':
            get_stats()
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
