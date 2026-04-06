#!/usr/bin/env python3
"""
Financial Report Agent
Generates comprehensive financial reports from all finance data.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Setup paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE_DIR / "data" / "finance"
LOG_DIR = WORKSPACE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# File paths for other finance agents
INVOICES_FILE = DATA_DIR / "invoices.json"
PAYMENTS_FILE = DATA_DIR / "payments.json"
EXPENSES_FILE = DATA_DIR / "expenses.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"
BUDGET_SPENDING_FILE = DATA_DIR / "budget_spending.json"
TAX_RECORDS_FILE = DATA_DIR / "tax_records.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "financial_report.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("FinancialReport")


def load_json(filepath, default=None):
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load {filepath}: {e}")
    return default


def get_invoice_summary():
    """Get summary from invoices."""
    data = load_json(INVOICES_FILE, {"invoices": []})
    invoices = data.get("invoices", [])
    
    summary = {"total": len(invoices), "draft": 0, "sent": 0, "paid": 0, "overdue": 0, "cancelled": 0,
               "total_amount": 0.0, "paid_amount": 0.0, "pending_amount": 0.0, "overdue_amount": 0.0}
    
    now = datetime.now()
    for inv in invoices:
        summary[inv.get("status", "draft")] += 1
        summary["total_amount"] += inv.get("amount", 0)
        if inv.get("status") == "paid":
            summary["paid_amount"] += inv.get("amount", 0)
        elif inv.get("status") == "overdue":
            summary["overdue_amount"] += inv.get("amount", 0)
        elif inv.get("status") in ["sent", "draft"]:
            summary["pending_amount"] += inv.get("amount", 0)
        
        # Check for overdue
        if inv.get("status") == "sent":
            due = datetime.fromisoformat(inv.get("due_date", now.isoformat()))
            if due < now:
                summary["overdue_amount"] += inv.get("amount", 0)
                summary["pending_amount"] -= inv.get("amount", 0)
    
    return summary


def get_payment_summary():
    """Get summary from payments."""
    data = load_json(PAYMENTS_FILE, {"payments": []})
    payments = data.get("payments", [])
    
    summary = {"total_income": 0.0, "total_expenses": 0.0, "pending_income": 0.0, "pending_expenses": 0.0,
               "completed_income": 0.0, "completed_expenses": 0.0, "net_flow": 0.0}
    
    for p in payments:
        amount = p.get("amount", 0)
        ptype = p.get("type", "expense")
        status = p.get("status", "pending")
        
        if ptype == "income":
            summary["total_income"] += amount
            if status == "completed":
                summary["completed_income"] += amount
            else:
                summary["pending_income"] += amount
        else:
            summary["total_expenses"] += amount
            if status == "completed":
                summary["completed_expenses"] += amount
            else:
                summary["pending_expenses"] += amount
    
    summary["net_flow"] = summary["completed_income"] - summary["completed_expenses"]
    return summary


def get_expense_summary():
    """Get summary from expenses."""
    data = load_json(EXPENSES_FILE, {"expenses": []})
    expenses = data.get("expenses", [])
    
    by_category = defaultdict(lambda: {"total": 0.0, "count": 0})
    total = 0.0
    
    for e in expenses:
        cat = e.get("category", "other")
        by_category[cat]["total"] += e.get("amount", 0)
        by_category[cat]["count"] += 1
        total += e.get("amount", 0)
    
    result = []
    for cat, data in by_category.items():
        result.append({
            "category": cat,
            "total": round(data["total"], 2),
            "count": data["count"],
            "percentage": round(data["total"] / total * 100, 1) if total > 0 else 0
        })
    
    return {"by_category": sorted(result, key=lambda x: x["total"], reverse=True), "total": round(total, 2)}


def get_budget_summary():
    """Get summary from budgets."""
    budgets_data = load_json(BUDGETS_FILE, {"budgets": {}})
    spending_data = load_json(BUDGET_SPENDING_FILE, {"spending": []})
    budgets = budgets_data.get("budgets", {})
    
    result = []
    now = datetime.now()
    
    for budget_id, budget in budgets.items():
        if not budget.get("active", True):
            continue
        
        period = budget.get("period", "monthly")
        amount = budget.get("amount", 0)
        
        # Calculate period dates
        if period == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
            else:
                end = start.replace(month=start.month + 1) - timedelta(seconds=1)
        elif period == "weekly":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif period == "yearly":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1) - timedelta(seconds=1)
        else:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if start.month == 12:
                end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
            else:
                end = start.replace(month=start.month + 1) - timedelta(seconds=1)
        
        # Calculate spent
        spent = 0.0
        start_str = start.isoformat()[:10]
        end_str = end.isoformat()[:10]
        for s in spending_data.get("spending", []):
            if s.get("budget_id") == budget_id:
                s_date = s.get("date", "")
                if start_str <= s_date <= end_str:
                    spent += s.get("amount", 0)
        
        remaining = amount - spent
        percentage = (spent / amount * 100) if amount > 0 else 0
        
        if percentage >= 100:
            status = "exceeded"
        elif percentage >= 90:
            status = "critical"
        elif percentage >= 75:
            status = "warning"
        else:
            status = "ok"
        
        result.append({
            "id": budget_id,
            "name": budget.get("name", budget_id),
            "amount": amount,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": round(percentage, 1),
            "status": status,
            "period": period
        })
    
    return {"budgets": sorted(result, key=lambda x: x["percentage"], reverse=True)}


def get_tax_summary(year=None):
    """Get tax summary for year."""
    if year is None:
        year = datetime.now().year
    
    data = load_json(TAX_RECORDS_FILE, {"yearly_data": {}})
    year_data = data.get("yearly_data", {}).get(str(year), {})
    quarters = year_data.get("quarters", {})
    
    total_income = 0.0
    total_expenses = 0.0
    total_tax = 0.0
    
    for q, record in quarters.items():
        total_income += record.get("income", 0)
        total_expenses += record.get("expenses", 0)
        total_tax += record.get("total_tax", 0)
    
    return {
        "year": year,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "taxable_income": round(max(0, total_income - total_expenses), 2),
        "total_tax": round(total_tax, 2),
        "quarters_recorded": list(quarters.keys())
    }


def generate_full_report(start_date=None, end_date=None, year=None):
    """Generate comprehensive financial report."""
    if year is None:
        year = datetime.now().year
    if start_date is None:
        start_date = f"{year}-01-01"
    if end_date is None:
        end_date = f"{year}-12-31"
    
    logger.info(f"Generating financial report for {year}")
    
    invoice_summary = get_invoice_summary()
    payment_summary = get_payment_summary()
    expense_summary = get_expense_summary()
    budget_summary = get_budget_summary()
    tax_summary = get_tax_summary(year)
    
    # Calculate profit & loss
    gross_income = payment_summary.get("completed_income", 0) + invoice_summary.get("paid_amount", 0)
    total_expenses = payment_summary.get("completed_expenses", 0) + expense_summary.get("total", 0)
    net_profit = gross_income - total_expenses
    
    # Estimated tax on profit
    estimated_tax = 0
    if net_profit > 11604:
        # Simplified German income tax estimate
        taxable = net_profit
        if taxable <= 17005:
            tax = (922.98 * 2398 + 1400 * taxable / 1000) * taxable / 10000
        elif taxable <= 66760:
            tax = (181.19 * 1062 + 2397 * (taxable - 17005) / 10000) * (taxable - 17005) / 10000 + 1025.38
        else:
            tax = 0.42 * (taxable - 66760) + 16899.99
        estimated_tax = round(tax * 1.055, 2)  # Including Soli
    
    report = {
        "report_date": datetime.now().isoformat(),
        "period": {"start": start_date, "end": end_date, "year": year},
        "invoice_summary": invoice_summary,
        "payment_summary": payment_summary,
        "expense_summary": expense_summary,
        "budget_summary": budget_summary,
        "tax_summary": tax_summary,
        "profit_loss": {
            "gross_income": round(gross_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(net_profit, 2),
            "estimated_tax": estimated_tax,
            "profit_after_tax": round(net_profit - estimated_tax, 2)
        }
    }
    
    return report


def format_report(report):
    """Format report for display."""
    lines = []
    lines.append("\n" + "=" * 60)
    lines.append("📊 FINANCIAL REPORT")
    lines.append(f"   Period: {report['period']['start']} to {report['period']['end']}")
    lines.append(f"   Generated: {report['report_date'][:10]}")
    lines.append("=" * 60)
    
    # Profit & Loss Summary
    pl = report["profit_loss"]
    lines.append("\n💵 PROFIT & LOSS SUMMARY")
    lines.append("-" * 40)
    lines.append(f"   Gross Income:     {pl['gross_income']:>12.2f} EUR")
    lines.append(f"   Total Expenses:   {pl['total_expenses']:>12.2f} EUR")
    lines.append(f"   {'-'*40}")
    lines.append(f"   Net Profit:       {pl['net_profit']:>12.2f} EUR")
    lines.append(f"   Estimated Tax:    {-pl['estimated_tax']:>12.2f} EUR")
    lines.append(f"   {'-'*40}")
    lines.append(f"   Profit After Tax: {pl['profit_after_tax']:>12.2f} EUR")
    
    # Invoice Summary
    inv = report["invoice_summary"]
    lines.append("\n📄 INVOICE SUMMARY")
    lines.append("-" * 40)
    lines.append(f"   Total Invoices:   {inv['total']:>12}")
    lines.append(f"   Paid:             {inv['paid']:>12} ({inv['paid_amount']:.2f} EUR)")
    lines.append(f"   Pending:          {inv['sent'] + inv['draft']:>12} ({inv['pending_amount']:.2f} EUR)")
    lines.append(f"   Overdue:          {inv['overdue']:>12} ({inv['overdue_amount']:.2f} EUR)")
    
    # Payment Summary
    pay = report["payment_summary"]
    lines.append("\n💰 PAYMENT SUMMARY")
    lines.append("-" * 40)
    lines.append(f"   Income Received:  {pay['completed_income']:>12.2f} EUR")
    lines.append(f"   Pending Income:   {pay['pending_income']:>12.2f} EUR")
    lines.append(f"   Expenses Paid:    {pay['completed_expenses']:>12.2f} EUR")
    lines.append(f"   Pending Expenses: {pay['pending_expenses']:>12.2f} EUR")
    lines.append(f"   Net Cash Flow:    {pay['net_flow']:>12.2f} EUR")
    
    # Expense Breakdown
    exp = report["expense_summary"]
    if exp["by_category"]:
        lines.append("\n📦 EXPENSE BREAKDOWN")
        lines.append("-" * 40)
        for cat in exp["by_category"][:5]:
            lines.append(f"   {cat['category']:<15} {cat['total']:>10.2f} EUR ({cat['percentage']:>5.1f}%)")
        lines.append(f"   {'Other':<15} {sum(c['total'] for c in exp['by_category'][5:]):>10.2f} EUR")
        lines.append(f"   {'TOTAL':<15} {exp['total']:>10.2f} EUR")
    
    # Budget Status
    bud = report["budget_summary"]
    if bud["budgets"]:
        lines.append("\n🎯 BUDGET STATUS")
        lines.append("-" * 40)
        for b in bud["budgets"]:
            status_icon = {"ok": "✅", "warning": "⚠️", "critical": "🔴", "exceeded": "🚫"}.get(b["status"], "•")
            lines.append(f"   {status_icon} {b['name']:<20} {b['spent']:>8.2f}/{b['amount']:.2f} EUR ({b['percentage']}%)")
    
    # Tax Summary
    tax = report["tax_summary"]
    if tax["quarters_recorded"]:
        lines.append("\n🏛️ TAX SUMMARY")
        lines.append("-" * 40)
        lines.append(f"   Year:             {tax['year']}")
        lines.append(f"   Total Income:     {tax['total_income']:>12.2f} EUR")
        lines.append(f"   Total Expenses:   {tax['total_expenses']:>12.2f} EUR")
        lines.append(f"   Taxable Income:   {tax['taxable_income']:>12.2f} EUR")
        lines.append(f"   Tax Recorded:     {tax['total_tax']:>12.2f} EUR")
        lines.append(f"   Quarters:         {', '.join(tax['quarters_recorded'])}")
    
    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def cmd_report(args):
    """Handle report command."""
    report = generate_full_report(year=args.year)
    print(format_report(report))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n✅ Report saved to: {args.output}")


def cmd_summary(args):
    """Handle summary command - quick summary."""
    payment_summary = get_payment_summary()
    invoice_summary = get_invoice_summary()
    budget_summary = get_budget_summary()
    
    net_flow = payment_summary.get("net_flow", 0)
    pending_income = payment_summary.get("pending_income", 0) + invoice_summary.get("pending_amount", 0)
    overdue = invoice_summary.get("overdue_amount", 0)
    
    print(f"""
📊 Quick Financial Summary
{'='*50}
💵 Cash Flow:      {net_flow:>10.2f} EUR
📥 Pending Income: {pending_income:>10.2f} EUR
⚠️  Overdue:        {overdue:>10.2f} EUR
""")
    
    # Budget alerts
    budgets = budget_summary.get("budgets", [])
    alerts = [b for b in budgets if b["status"] in ["warning", "critical", "exceeded"]]
    if alerts:
        print("⚠️  Budget Alerts:")
        for b in alerts:
            print(f"   - {b['name']}: {b['percentage']}% used")


def cmd_income(args):
    """Handle income command - detailed income analysis."""
    payment_summary = get_payment_summary()
    invoice_summary = get_invoice_summary()
    
    print(f"""
💰 INCOME ANALYSIS
{'='*50}
RECEIVED:
  Invoices Paid:     {invoice_summary.get('paid_amount', 0):>12.2f} EUR
  Payments Received: {payment_summary.get('completed_income', 0):>12.2f} EUR
  
PENDING:
  Invoices Sent:     {invoice_summary.get('pending_amount', 0):>12.2f} EUR
  Payments Pending:  {payment_summary.get('pending_income', 0):>12.2f} EUR

OVERDUE:
  Invoices Overdue:  {invoice_summary.get('overdue_amount', 0):>12.2f} EUR
""")


def cmd_expenses(args):
    """Handle expenses command."""
    expense_summary = get_expense_summary()
    payment_summary = get_payment_summary()
    
    print(f"""
📦 EXPENSE ANALYSIS
{'='*50}
PAYMENT TRACKER:
  Completed Expenses: {payment_summary.get('completed_expenses', 0):>12.2f} EUR
  Pending Expenses:   {payment_summary.get('pending_expenses', 0):>12.2f} EUR

CATEGORIZED EXPENSES (Total: {expense_summary.get('total', 0):.2f} EUR):
""")
    
    for cat in expense_summary.get("by_category", []):
        print(f"  {cat['category']:<20} {cat['total']:>10.2f} EUR ({cat['percentage']:>5.1f}%)")


def cmd_cashflow(args):
    """Handle cashflow command."""
    payment_summary = get_payment_summary()
    
    received = payment_summary.get("completed_income", 0)
    spent = payment_summary.get("completed_expenses", 0)
    net = payment_summary.get("net_flow", 0)
    
    # Monthly breakdown would require more data structure
    print(f"""
💵 CASH FLOW ANALYSIS
{'='*50}
Cash Received:    {received:>12.2f} EUR
Cash Spent:      {spent:>12.2f} EUR
{'-'*30}
Net Cash Flow:   {net:>12.2f} EUR
""")
    
    if net >= 0:
        print("✅ Positive cash flow - business is sustainable")
    else:
        print("⚠️  Negative cash flow - attention needed!")


def cmd_export(args):
    """Handle export command."""
    report = generate_full_report(year=args.year)
    
    if args.format == "json":
        filepath = args.output or f"financial_report_{args.year}.json"
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report exported to: {filepath}")
    
    elif args.format == "text":
        filepath = args.output or f"financial_report_{args.year}.txt"
        with open(filepath, 'w') as f:
            f.write(format_report(report))
        print(f"✅ Report exported to: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description="Financial Report Agent - Generate comprehensive financial reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s report --year 2026
  %(prog)s report --year 2026 --output /path/to/report.json
  %(prog)s summary
  %(prog)s income
  %(prog)s expenses
  %(prog)s cashflow
  %(prog)s export --format json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate full financial report")
    report_parser.add_argument("--year", type=int, default=datetime.now().year, help="Report year")
    report_parser.add_argument("--output", help="Save report to file")
    
    # Summary command
    subparsers.add_parser("summary", help="Quick financial summary")
    
    # Income command
    subparsers.add_parser("income", help="Detailed income analysis")
    
    # Expenses command
    subparsers.add_parser("expenses", help="Expense breakdown")
    
    # Cashflow command
    subparsers.add_parser("cashflow", help="Cash flow analysis")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export report to file")
    export_parser.add_argument("--format", choices=["json", "text"], default="json", help="Export format")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--year", type=int, default=datetime.now().year, help="Report year")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "report": cmd_report,
        "summary": cmd_summary,
        "income": cmd_income,
        "expenses": cmd_expenses,
        "cashflow": cmd_cashflow,
        "export": cmd_export
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
