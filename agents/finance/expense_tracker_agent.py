#!/usr/bin/env python3
"""
Expense Tracker Agent
EmpireHazeClaw Finance Suite

Tracks business expenses, categories, budgets. Reads/writes JSON.
Integrität: no manipulation, Ressourceneffizienz: free tools only.
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

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "finance"
LOG_DIR = BASE_DIR / "logs"
EXPENSES_FILE = DATA_DIR / "expenses.json"
CATEGORIES_FILE = DATA_DIR / "expense_categories.json"
BUDGETS_FILE = DATA_DIR / "expense_budgets.json"

LOG_FILE = LOG_DIR / "expense_tracker.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ExpenseTracker")


def load_json(path: Path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return {} if "budget" in str(path) else []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_expenses() -> list:
    data = load_json(EXPENSES_FILE)
    return data if isinstance(data, list) else []


def save_expenses(data: list) -> bool:
    return save_json(EXPENSES_FILE, data)


def load_budgets() -> dict:
    return load_json(BUDGETS_FILE)


def save_budgets(data: dict) -> bool:
    return save_json(BUDGETS_FILE, data)


DEFAULT_CATEGORIES = [
    {"id": "software", "name": "Software & SaaS", "color": "#6C5CE7"},
    {"id": "marketing", "name": "Marketing & Ads", "color": "#00B894"},
    {"id": "hosting", "name": "Hosting & Infrastructure", "color": "#0984E3"},
    {"id": "office", "name": "Office & Supplies", "color": "#FDCB6E"},
    {"id": "tools", "name": "Tools & Equipment", "color": "#E17055"},
    {"id": "travel", "name": "Travel & Transport", "color": "#74B9FF"},
    {"id": "services", "name": "Professional Services", "color": "#A29BFE"},
    {"id": "other", "name": "Other", "color": "#636E72"},
]


def ensure_categories():
    path = CATEGORIES_FILE
    if not path.exists():
        save_json(path, DEFAULT_CATEGORIES)


def load_categories() -> list:
    ensure_categories()
    return load_json(CATEGORIES_FILE)


def add_expense(
    description: str,
    amount: float,
    category: str,
    date: Optional[str] = None,
    vendor: str = "",
    notes: str = "",
    currency: str = "EUR",
    receipt: str = "",
) -> dict:
    """Add a new expense."""
    logger.info("Adding expense: %s — %s %s", description, amount, currency)
    expense = {
        "id": str(uuid.uuid4()),
        "description": description,
        "amount": round(amount, 2),
        "category": category,
        "vendor": vendor,
        "notes": notes,
        "currency": currency,
        "receipt": receipt,
        "date": date or datetime.utcnow().strftime("%Y-%m-%d"),
        "created_at": datetime.utcnow().isoformat(),
    }
    expenses = load_expenses()
    expenses.append(expense)
    save_expenses(expenses)
    return expense


def delete_expense(expense_id: str) -> bool:
    expenses = load_expenses()
    before = len(expenses)
    expenses = [e for e in expenses if e["id"] != expense_id]
    if len(expenses) == before:
        raise ValueError(f"Expense not found: {expense_id}")
    save_expenses(expenses)
    logger.info("Expense deleted: %s", expense_id)
    return True


def list_expenses(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    month: Optional[str] = None,
) -> list:
    """List expenses with optional filters."""
    expenses = load_expenses()
    if category:
        expenses = [e for e in expenses if e.get("category") == category]
    if month:
        expenses = [e for e in expenses if e.get("date", "").startswith(month)]
    if start_date:
        expenses = [e for e in expenses if e.get("date", "") >= start_date]
    if end_date:
        expenses = [e for e in expenses if e.get("date", "") <= end_date]
    expenses.sort(key=lambda x: x.get("date", ""), reverse=True)
    return expenses


def get_totals(expenses: list) -> dict:
    by_category = {}
    total = 0.0
    for e in expenses:
        cat = e.get("category", "other")
        by_category[cat] = by_category.get(cat, 0.0) + e.get("amount", 0)
        total += e.get("amount", 0)
    return {"total": round(total, 2), "by_category": {k: round(v, 2) for k, v in by_category.items()}}


def set_budget(category: str, amount: float, period: str = "monthly") -> dict:
    """Set a budget for a category."""
    budgets = load_budgets()
    budgets[category] = {"amount": round(amount, 2), "period": period, "updated_at": datetime.utcnow().isoformat()}
    save_budgets(budgets)
    logger.info("Budget set: %s = %s (%s)", category, amount, period)
    return budgets[category]


def check_budgets(expenses: list, month: Optional[str] = None) -> list:
    """Check which categories are over/under budget."""
    budgets = load_budgets()
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")
    month_expenses = [e for e in expenses if e.get("date", "").startswith(month)]
    totals = get_totals(month_expenses)
    result = []
    for cat, budget in budgets.items():
        spent = totals["by_category"].get(cat, 0)
        limit = budget["amount"]
        pct = (spent / limit * 100) if limit > 0 else 0
        result.append({
            "category": cat,
            "budget": limit,
            "spent": spent,
            "remaining": round(limit - spent, 2),
            "pct": round(pct, 1),
            "over": spent > limit,
        })
    return result


def format_currency(amount: float, currency: str = "EUR") -> str:
    symbols = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF"}
    sym = symbols.get(currency, currency + " ")
    return f"{sym}{amount:,.2f}"


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_add(args):
    expense = add_expense(
        description=args.description,
        amount=args.amount,
        category=args.category,
        date=args.date,
        vendor=args.vendor or "",
        notes=args.notes or "",
        currency=args.currency.upper(),
        receipt=args.receipt or "",
    )
    print(f"✅ Expense added: {expense['id']}")
    print(f"   {expense['date']} | {expense['category']} | {format_currency(expense['amount'], expense['currency'])}")
    print(f"   {expense['description']}")


def cmd_list(args):
    expenses = list_expenses(category=args.category, start_date=args.start, end_date=args.end, month=args.month)
    if not expenses:
        print("No expenses found.")
        return
    totals = get_totals(expenses)
    print(f"\n{'#':<4} {'Date':<12} {'Category':<20} {'Vendor':<20} {'Description':<25} {'Amount':>12}")
    print("-" * 100)
    for i, e in enumerate(expenses, 1):
        print(
            f"{i:<4} {e.get('date','?'):<12} {e.get('category','?'):<20} "
            f"{e.get('vendor',''):<20} {e.get('description',''):<25} "
            f"{format_currency(e.get('amount',0), e.get('currency','EUR')):>12}"
        )
    print("-" * 100)
    print(f"{'TOTAL':<80} {format_currency(totals['total'], 'EUR'):>12}")
    print(f"\nTotal: {len(expenses)} expense(s) | {format_currency(totals['total'], 'EUR')}")


def cmd_delete(args):
    delete_expense(args.expense_id)
    print(f"✅ Expense deleted: {args.expense_id}")


def cmd_stats(args):
    month = args.month or datetime.utcnow().strftime("%Y-%m")
    expenses = list_expenses(month=month)
    totals = get_totals(expenses)
    categories = load_categories()
    cat_map = {c["id"]: c for c in categories}

    print(f"\n📊 Expense Statistics — {month}")
    print("=" * 60)
    print(f"  Total Expenses : {len(expenses)}")
    print(f"  Total Amount   : {format_currency(totals['total'], 'EUR')}")
    print()
    print("  By Category:")
    for cat_id, amount in sorted(totals["by_category"].items(), key=lambda x: -x[1]):
        cat_name = cat_map.get(cat_id, {}).get("name", cat_id)
        print(f"    {cat_name:<30} {format_currency(amount, 'EUR'):>12}")

    budgets = check_budgets(expenses, month=month)
    if budgets:
        print()
        print("  Budget Status:")
        for b in budgets:
            status = "🔴 OVER" if b["over"] else "🟢 OK"
            print(f"    {b['category']:<20} {status}  {b['pct']:>5.1f}%  {format_currency(b['spent'],'EUR')} / {format_currency(b['budget'],'EUR')}")


def cmd_set_budget(args):
    set_budget(category=args.category, amount=args.amount, period=args.period)
    print(f"✅ Budget set: {args.category} = {format_currency(args.amount)} / {args.period}")


def cmd_budgets(args):
    budgets = load_budgets()
    if not budgets:
        print("No budgets set. Use: expense-tracker set-budget --category X --amount Y")
        return
    print(f"\n{'Category':<25} {'Budget':>12} {'Period':<10}")
    print("-" * 50)
    for cat, b in budgets.items():
        print(f"  {cat:<25} {format_currency(b['amount'],'EUR'):>12} {b['period']:<10}")


def cmd_categories(args):
    cats = load_categories()
    print("\nCategories:")
    for c in cats:
        print(f"  {c['id']:<20} {c['name']}  {c['color']}")


def cmd_export(args):
    """Export expenses as JSON."""
    expenses = list_expenses(category=args.category, start_date=args.start, end_date=args.end, month=args.month)
    export_file = Path(args.output)
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2, ensure_ascii=False)
    totals = get_totals(expenses)
    print(f"✅ Exported {len(expenses)} expenses to {export_file}")
    print(f"   Total: {format_currency(totals['total'], 'EUR')}")


def main():
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="EmpireHazeClaw Expense Tracker — track and categorize business expenses.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a new expense")
    p_add.add_argument("--description", required=True, help="Expense description")
    p_add.add_argument("--amount", type=float, required=True, help="Amount")
    p_add.add_argument("--category", required=True, help="Category ID (use 'categories' to list)")
    p_add.add_argument("--date", help="Date (YYYY-MM-DD, default: today)")
    p_add.add_argument("--vendor", help="Vendor name")
    p_add.add_argument("--notes", help="Additional notes")
    p_add.add_argument("--currency", default="EUR", help="Currency (default: EUR)")
    p_add.add_argument("--receipt", help="Receipt path/URL")
    p_add.set_defaults(fn=cmd_add)

    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--month", help="Filter by month (YYYY-MM)")
    p_list.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_list.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_list.set_defaults(fn=cmd_list)

    p_del = sub.add_parser("delete", help="Delete an expense")
    p_del.add_argument("expense_id", help="Expense ID")
    p_del.set_defaults(fn=cmd_delete)

    p_stats = sub.add_parser("stats", help="Show expense statistics")
    p_stats.add_argument("--month", help="Month (YYYY-MM, default: current)")
    p_stats.set_defaults(fn=cmd_stats)

    p_budget = sub.add_parser("set-budget", help="Set a budget for a category")
    p_budget.add_argument("--category", required=True)
    p_budget.add_argument("--amount", type=float, required=True)
    p_budget.add_argument("--period", default="monthly", choices=["monthly", "yearly"])
    p_budget.set_defaults(fn=cmd_set_budget)

    p_budgets = sub.add_parser("budgets", help="List all budgets")
    p_budgets.set_defaults(fn=cmd_budgets)

    p_cats = sub.add_parser("categories", help="List available categories")
    p_cats.set_defaults(fn=cmd_categories)

    p_export = sub.add_parser("export", help="Export expenses to JSON")
    p_export.add_argument("--output", default="expenses_export.json", help="Output file")
    p_export.add_argument("--category", help="Filter by category")
    p_export.add_argument("--month", help="Filter by month (YYYY-MM)")
    p_export.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p_export.add_argument("--end", help="End date (YYYY-MM-DD)")
    p_export.set_defaults(fn=cmd_export)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
