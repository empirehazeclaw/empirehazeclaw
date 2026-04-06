#!/usr/bin/env python3
"""
Budget Planner Agent
Plans monthly budgets, tracks expenses vs budget, analyzes spending patterns.
Stores data in JSON format.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "budget_planner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BudgetPlannerAgent")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/budget_planner.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

CATEGORIES = ["housing", "transportation", "food", "utilities", "insurance", 
              "healthcare", "entertainment", "shopping", "debt", "savings", "other"]

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"budgets": {}, "expenses": [], "categories": CATEGORIES, "last_expense_id": 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def set_budget(args):
    """Set monthly budget for a category."""
    data = load_data()
    month = args.month or datetime.now().strftime("%Y-%m")
    
    if month not in data["budgets"]:
        data["budgets"][month] = {cat: {"limit": 0, "spent": 0} for cat in CATEGORIES}
    
    data["budgets"][month][args.category]["limit"] = float(args.amount)
    save_data(data)
    
    logger.info(f"Set budget for {month}/{args.category}: ${args.amount}")
    print(f"✅ Set {args.category} budget for {month}: ${float(args.amount):.2f}")

def add_expense(args):
    """Add an expense."""
    data = load_data()
    month = args.month or datetime.now().strftime("%Y-%m")
    
    if month not in data["budgets"]:
        data["budgets"][month] = {cat: {"limit": 0, "spent": 0} for cat in CATEGORIES}
    
    data["last_expense_id"] += 1
    expense = {
        "id": data["last_expense_id"],
        "description": args.description,
        "amount": float(args.amount),
        "category": args.category,
        "date": args.date or datetime.now().isoformat()[:10],
        "month": month,
        "created_at": datetime.now().isoformat()
    }
    
    data["expenses"].append(expense)
    data["budgets"][month][args.category]["spent"] += float(args.amount)
    
    save_data(data)
    logger.info(f"Added expense: {expense['description']} - ${expense['amount']}")
    print(f"✅ Added expense: {args.description}")
    print(f"   Amount: ${float(args.amount):.2f} | Category: {args.category}")

def list_expenses(args):
    """List expenses."""
    data = load_data()
    expenses = data["expenses"]
    
    month = args.month
    if month:
        expenses = [e for e in expenses if e["month"] == month]
    if args.category:
        expenses = [e for e in expenses if e["category"] == args.category]
    
    if not expenses:
        print("No expenses found.")
        return
    
    print(f"\n💰 Expenses ({len(expenses)}):\n")
    for e in sorted(expenses, key=lambda x: x["date"], reverse=True)[:20]:
        print(f"  [{e['id']}] {e['date']} | {e['description']}")
        print(f"      ${e['amount']:.2f} | {e['category']}")
    if len(expenses) > 20:
        print(f"\n  ... and {len(expenses) - 20} more")

def budget_status(args):
    """Show budget status for a month."""
    data = load_data()
    month = args.month or datetime.now().strftime("%Y-%m")
    
    if month not in data["budgets"]:
        print(f"No budget set for {month}.")
        return
    
    print(f"\n📊 Budget Status for {month}:\n")
    print(f"  {'Category':<18} {'Budget':<12} {'Spent':<12} {'Remaining':<12} {'Status'}")
    print(f"  {'-'*18} {'-'*12} {'-'*12} {'-'*12} {'-'*6}")
    
    total_budget = 0
    total_spent = 0
    
    for cat in CATEGORIES:
        info = data["budgets"][month].get(cat, {"limit": 0, "spent": 0})
        if info["limit"] > 0 or info["spent"] > 0:
            remaining = info["limit"] - info["spent"]
            pct = (info["spent"] / info["limit"] * 100) if info["limit"] > 0 else 0
            
            if remaining < 0:
                status = "🔴 OVER"
            elif pct > 90:
                status = "🟡 HIGH"
            else:
                status = "🟢 OK"
            
            print(f"  {cat:<18} ${info['limit']:<11.2f} ${info['spent']:<11.2f} ${remaining:<11.2f} {status}")
            total_budget += info["limit"]
            total_spent += info["spent"]
    
    print(f"\n  {'TOTALS':<18} ${total_budget:<11.2f} ${total_spent:<11.2f} ${total_budget - total_spent:<11.2f}")

def delete_expense(args):
    """Delete an expense."""
    data = load_data()
    for i, e in enumerate(data["expenses"]):
        if e["id"] == int(args.id):
            month = e["month"]
            if month in data["budgets"] and e["category"] in data["budgets"][month]:
                data["budgets"][month][e["category"]]["spent"] -= e["amount"]
            data["expenses"].pop(i)
            save_data(data)
            print(f"✅ Deleted expense #{args.id}")
            return
    print(f"Expense #{args.id} not found.")

def analyze(args):
    """Analyze spending patterns."""
    data = load_data()
    
    if not data["expenses"]:
        print("No expenses to analyze.")
        return
    
    # Last N months
    months = sorted(set(e["month"] for e in data["expenses"]))[-int(args.months):]
    
    print(f"\n📈 Spending Analysis (Last {args.months} Months):\n")
    
    # Total spending by category
    by_category = defaultdict(float)
    for e in data["expenses"]:
        if e["month"] in months:
            by_category[e["category"]] += e["amount"]
    
    print(f"  Total Spending by Category:")
    for cat, amount in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
        print(f"    {cat}: ${amount:.2f}")
    
    # Monthly trends
    by_month = defaultdict(float)
    for e in data["expenses"]:
        by_month[e["month"]] += e["amount"]
    
    print(f"\n  Monthly Trend:")
    for month in sorted(by_month.keys()):
        print(f"    {month}: ${by_month[month]:.2f}")
    
    # Average
    if by_month:
        avg = sum(by_month.values()) / len(by_month)
        print(f"\n  Monthly Average: ${avg:.2f}")

def main():
    parser = argparse.ArgumentParser(
        description="Budget Planner Agent - Plan and track monthly budgets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s set-budget --category food --amount 500 --month 2026-03
  %(prog)s add --description "Grocery shopping" --amount 85.50 --category food
  %(prog)s list --month 2026-03 --category food
  %(prog)s status --month 2026-03
  %(prog)s delete --id 1
  %(prog)s analyze --months 6
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_budget = subparsers.add_parser("set-budget", help="Set monthly budget")
    p_budget.add_argument("--category", required=True, choices=CATEGORIES, help="Category")
    p_budget.add_argument("--amount", required=True, help="Budget amount")
    p_budget.add_argument("--month", help="Month (YYYY-MM)")
    
    p_add = subparsers.add_parser("add", help="Add expense")
    p_add.add_argument("--description", required=True, help="Description")
    p_add.add_argument("--amount", required=True, help="Amount")
    p_add.add_argument("--category", required=True, choices=CATEGORIES, help="Category")
    p_add.add_argument("--date", help="Date (YYYY-MM-DD)")
    p_add.add_argument("--month", help="Month (YYYY-MM, auto-detected)")
    
    p_list = subparsers.add_parser("list", help="List expenses")
    p_list.add_argument("--month", help="Filter by month")
    p_list.add_argument("--category", choices=CATEGORIES, help="Filter by category")
    
    p_status = subparsers.add_parser("status", help="Budget status")
    p_status.add_argument("--month", help="Month (YYYY-MM)")
    
    p_delete = subparsers.add_parser("delete", help="Delete expense")
    p_delete.add_argument("--id", required=True, type=int, help="Expense ID")
    
    p_analyze = subparsers.add_parser("analyze", help="Analyze spending")
    p_analyze.add_argument("--months", default=6, type=int, help="Number of months to analyze")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "set-budget":
            set_budget(args)
        elif args.command == "add":
            add_expense(args)
        elif args.command == "list":
            list_expenses(args)
        elif args.command == "status":
            budget_status(args)
        elif args.command == "delete":
            delete_expense(args)
        elif args.command == "analyze":
            analyze(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
