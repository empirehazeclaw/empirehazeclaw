#!/usr/bin/env python3
"""
Payment Tracker Agent
Tracks incoming and outgoing payments, manages payment status.
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

PAYMENTS_FILE = DATA_DIR / "payments.json"
ACCOUNTS_FILE = DATA_DIR / "payment_accounts.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "payment_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PaymentTracker")


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


def load_payments():
    """Load payments from file."""
    return load_json(PAYMENTS_FILE, {"payments": [], "accounts": {}})


def load_accounts():
    """Load accounts from file."""
    data = load_json(ACCOUNTS_FILE, {"accounts": {}})
    return data.get("accounts", {})


def save_payments(data):
    """Save payments to file."""
    return save_json(PAYMENTS_FILE, data)


def save_accounts(accounts):
    """Save accounts to file."""
    return save_json(ACCOUNTS_FILE, {"accounts": accounts})


def create_payment(amount, description, payment_type, account="default", reference=None, date=None):
    """Create a new payment record."""
    logger.info(f"Creating {payment_type} payment: {amount} - {description}")
    
    payments_data = load_payments()
    
    payment = {
        "id": str(uuid.uuid4()),
        "amount": float(amount),
        "description": description,
        "type": payment_type,  # "income" or "expense"
        "account": account,
        "reference": reference or f"REF-{uuid.uuid4().hex[:8].upper()}",
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "processed_at": None,
        "category": None
    }
    
    if date:
        payment["date"] = date
    else:
        payment["date"] = datetime.now().strftime("%Y-%m-%d")
    
    payments_data["payments"].append(payment)
    
    if save_payments(payments_data):
        logger.info(f"Payment created: {payment['reference']}")
        return payment
    else:
        logger.error("Failed to save payment")
        return None


def list_payments(payment_type=None, status=None, account=None, start_date=None, end_date=None):
    """List payments with optional filters."""
    payments_data = load_payments()
    payments = payments_data.get("payments", [])
    
    if payment_type:
        payments = [p for p in payments if p["type"] == payment_type]
    if status:
        payments = [p for p in payments if p["status"] == status]
    if account:
        payments = [p for p in payments if p["account"] == account]
    if start_date:
        payments = [p for p in payments if p.get("date", "") >= start_date]
    if end_date:
        payments = [p for p in payments if p.get("date", "") <= end_date]
    
    return sorted(payments, key=lambda x: (x.get("date", ""), x["created_at"]), reverse=True)


def get_payment(payment_id_or_ref):
    """Get payment by ID or reference."""
    payments_data = load_payments()
    for p in payments_data.get("payments", []):
        if p["id"] == payment_id_or_ref or p["reference"] == payment_id_or_ref:
            return p
    return None


def update_payment_status(payment_id_or_ref, new_status):
    """Update payment status."""
    valid_statuses = ["pending", "processing", "completed", "failed", "cancelled"]
    if new_status not in valid_statuses:
        logger.error(f"Invalid status: {new_status}")
        return None
    
    payments_data = load_payments()
    
    for p in payments_data.get("payments", []):
        if p["id"] == payment_id_or_ref or p["reference"] == payment_id_or_ref:
            p["status"] = new_status
            if new_status == "completed":
                p["processed_at"] = datetime.now().isoformat()
            if save_payments(payments_data):
                logger.info(f"Payment {p['reference']} status updated to {new_status}")
                return p
            break
    
    return None


def delete_payment(payment_id_or_ref):
    """Delete a payment record."""
    payments_data = load_payments()
    
    for i, p in enumerate(payments_data.get("payments", [])):
        if p["id"] == payment_id_or_ref or p["reference"] == payment_id_or_ref:
            deleted = payments_data["payments"].pop(i)
            if save_payments(payments_data):
                logger.info(f"Deleted payment {deleted['reference']}")
                return True
            break
    
    return False


def get_payment_summary(start_date=None, end_date=None):
    """Get payment summary statistics."""
    payments = list_payments(start_date=start_date, end_date=end_date)
    
    summary = {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "net_flow": 0.0,
        "pending_income": 0.0,
        "pending_expenses": 0.0,
        "completed_income": 0.0,
        "completed_expenses": 0.0,
        "total_payments": len(payments),
        "pending_count": 0,
        "completed_count": 0,
        "failed_count": 0
    }
    
    for p in payments:
        amount = p["amount"]
        
        if p["type"] == "income":
            summary["total_income"] += amount
            if p["status"] == "pending":
                summary["pending_income"] += amount
                summary["pending_count"] += 1
            elif p["status"] == "completed":
                summary["completed_income"] += amount
                summary["completed_count"] += 1
        else:  # expense
            summary["total_expenses"] += amount
            if p["status"] == "pending":
                summary["pending_expenses"] += amount
                summary["pending_count"] += 1
            elif p["status"] == "completed":
                summary["completed_expenses"] += amount
                summary["completed_count"] += 1
        
        if p["status"] == "failed":
            summary["failed_count"] += 1
    
    summary["net_flow"] = summary["completed_income"] - summary["completed_expenses"]
    summary["pending_net"] = summary["pending_income"] - summary["pending_expenses"]
    
    return summary


def get_account_balance(account="default"):
    """Calculate account balance."""
    payments = list_payments(account=account)
    
    balance = 0.0
    for p in payments:
        if p["status"] == "completed":
            if p["type"] == "income":
                balance += p["amount"]
            else:
                balance -= p["amount"]
    
    return balance


def add_account(name, initial_balance=0.0, currency="EUR"):
    """Add a new payment account."""
    accounts = load_accounts()
    
    if name in accounts:
        logger.warning(f"Account {name} already exists")
        return None
    
    accounts[name] = {
        "name": name,
        "initial_balance": float(initial_balance),
        "currency": currency,
        "created_at": datetime.now().isoformat()
    }
    
    if save_accounts(accounts):
        logger.info(f"Account {name} created with balance {initial_balance}")
        return accounts[name]
    
    return None


def list_accounts():
    """List all accounts with balances."""
    accounts = load_accounts()
    result = []
    
    for name, acc in accounts.items():
        balance = get_account_balance(name)
        result.append({
            **acc,
            "current_balance": balance
        })
    
    return result


def print_payment(p):
    """Pretty print a payment."""
    type_icon = "📥" if p["type"] == "income" else "📤"
    status_icon = {
        "pending": "⏳", "processing": "⚙️", "completed": "✅", "failed": "❌", "cancelled": "🚫"
    }.get(p["status"], "•")
    
    print(f"\n{type_icon} Payment: {p['reference']}")
    print(f"   Amount:      {p['amount']:.2f} EUR")
    print(f"   Type:        {p['type']}")
    print(f"   Description: {p['description']}")
    print(f"   Status:      {p['status']} {status_icon}")
    print(f"   Date:        {p.get('date', 'N/A')}")
    print(f"   Account:     {p['account']}")


def cmd_create(args):
    """Handle create command."""
    payment = create_payment(
        amount=args.amount,
        description=args.description,
        payment_type=args.type,
        account=args.account,
        reference=args.reference,
        date=args.date
    )
    
    if payment:
        print(f"✅ Payment created: {payment['reference']}")
        print_payment(payment)
    else:
        print("❌ Failed to create payment")
        sys.exit(1)


def cmd_list(args):
    """Handle list command."""
    payments = list_payments(
        payment_type=args.type,
        status=args.status,
        account=args.account,
        start_date=args.start,
        end_date=args.end
    )
    
    if not payments:
        print("No payments found.")
        return
    
    print(f"\n📋 Found {len(payments)} payment(s):\n")
    for p in payments:
        type_icon = "📥" if p["type"] == "income" else "📤"
        status_icon = {"pending": "⏳", "processing": "⚙️", "completed": "✅", "failed": "❌", "cancelled": "🚫"}.get(p["status"], "•")
        amount_str = f"+{p['amount']:.2f}" if p["type"] == "income" else f"-{p['amount']:.2f}"
        print(f"  {type_icon} {p['reference']} | {p['description'][:30]} | {amount_str} EUR | {p['status']} {status_icon} | {p.get('date', 'N/A')}")


def cmd_show(args):
    """Handle show command."""
    payment = get_payment(args.payment)
    if payment:
        print_payment(payment)
    else:
        print(f"❌ Payment not found: {args.payment}")
        sys.exit(1)


def cmd_process(args):
    """Handle process command."""
    result = update_payment_status(args.payment, "processing")
    if result:
        print(f"✅ Payment {result['reference']} is being processed")
    else:
        print("❌ Failed to process payment")
        sys.exit(1)


def cmd_complete(args):
    """Handle complete command."""
    result = update_payment_status(args.payment, "completed")
    if result:
        print(f"✅ Payment {result['reference']} completed")
    else:
        print("❌ Failed to complete payment")
        sys.exit(1)


def cmd_failed(args):
    """Handle failed command."""
    result = update_payment_status(args.payment, "failed")
    if result:
        print(f"✅ Payment {result['reference']} marked as failed")
    else:
        print("❌ Failed to update payment")
        sys.exit(1)


def cmd_delete(args):
    """Handle delete command."""
    if delete_payment(args.payment):
        print(f"✅ Payment deleted")
    else:
        print("❌ Failed to delete payment")
        sys.exit(1)


def cmd_summary(args):
    """Handle summary command."""
    summary = get_payment_summary(start_date=args.start, end_date=args.end)
    
    print(f"""
💰 Payment Summary
{'='*50}
Total Payments:  {summary['total_payments']}

📥 INCOME:
  Total Income:    {summary['total_income']:.2f} EUR
  Completed:       {summary['completed_income']:.2f} EUR
  Pending:         {summary['pending_income']:.2f} EUR

📤 EXPENSES:
  Total Expenses:  {summary['total_expenses']:.2f} EUR
  Completed:       {summary['completed_expenses']:.2f} EUR
  Pending:         {summary['pending_expenses']:.2f} EUR

💵 NET FLOW:
  Net (completed): {summary['net_flow']:.2f} EUR
  Pending Net:     {summary['pending_net']:.2f} EUR

📊 Status Counts:
  Pending:    {summary['pending_count']}
  Completed:  {summary['completed_count']}
  Failed:     {summary['failed_count']}
""")


def cmd_balance(args):
    """Handle balance command."""
    accounts = list_accounts()
    
    if args.account:
        balance = get_account_balance(args.account)
        print(f"\n💰 Account '{args.account}' Balance: {balance:.2f} EUR\n")
    else:
        print(f"\n💰 All Accounts:\n{'='*50}")
        for acc in accounts:
            print(f"  {acc['name']}: {acc.get('current_balance', 0):.2f} {acc.get('currency', 'EUR')}")


def cmd_account_add(args):
    """Handle account add command."""
    result = add_account(args.name, initial_balance=args.balance)
    if result:
        print(f"✅ Account '{args.name}' created with balance {args.balance} EUR")
    else:
        print("❌ Failed to create account (may already exist)")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Payment Tracker Agent - Track incoming and outgoing payments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --type income --amount 1500 --description "Client Payment"
  %(prog)s create --type expense --amount 200 --description "Office Supplies"
  %(prog)s list --type income --status pending
  %(prog)s list --start 2026-01-01 --end 2026-12-31
  %(prog)s complete REF-ABC123
  %(prog)s summary
  %(prog)s balance
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new payment")
    create_parser.add_argument("--type", required=True, choices=["income", "expense"], help="Payment type")
    create_parser.add_argument("--amount", required=True, type=float, help="Payment amount")
    create_parser.add_argument("--description", required=True, help="Payment description")
    create_parser.add_argument("--account", default="default", help="Account name")
    create_parser.add_argument("--reference", help="Payment reference (auto-generated if not provided)")
    create_parser.add_argument("--date", help="Payment date (YYYY-MM-DD)")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List payments")
    list_parser.add_argument("--type", choices=["income", "expense"], help="Filter by type")
    list_parser.add_argument("--status", choices=["pending", "processing", "completed", "failed", "cancelled"], help="Filter by status")
    list_parser.add_argument("--account", help="Filter by account")
    list_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    list_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show payment details")
    show_parser.add_argument("payment", help="Payment ID or reference")
    
    # Process command
    process_parser = subparsers.add_parser("process", help="Mark payment as processing")
    process_parser.add_argument("payment", help="Payment ID or reference")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark payment as completed")
    complete_parser.add_argument("payment", help="Payment ID or reference")
    
    # Failed command
    failed_parser = subparsers.add_parser("failed", help="Mark payment as failed")
    failed_parser.add_argument("payment", help="Payment ID or reference")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a payment")
    delete_parser.add_argument("payment", help="Payment ID or reference")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show payment summary")
    summary_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    summary_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    
    # Balance command
    balance_parser = subparsers.add_parser("balance", help="Show account balance(s)")
    balance_parser.add_argument("--account", help="Specific account (default: all)")
    
    # Account add command
    account_parser = subparsers.add_parser("account-add", help="Add a new account")
    account_parser.add_argument("name", help="Account name")
    account_parser.add_argument("--balance", type=float, default=0.0, help="Initial balance")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "show": cmd_show,
        "process": cmd_process,
        "complete": cmd_complete,
        "failed": cmd_failed,
        "delete": cmd_delete,
        "summary": cmd_summary,
        "balance": cmd_balance,
        "account-add": cmd_account_add
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
