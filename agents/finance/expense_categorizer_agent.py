#!/usr/bin/env python3
"""
Expense Categorizer Agent
Automatically categorizes expenses and provides spending insights.
"""

import argparse
import json
import logging
import os
import re
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE_DIR / "data" / "finance"
LOG_DIR = WORKSPACE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

EXPENSES_FILE = DATA_DIR / "expenses.json"
CATEGORIES_FILE = DATA_DIR / "expense_categories.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "expense_categorizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExpenseCategorizer")


# Default categories with keywords
DEFAULT_CATEGORIES = {
    "office": {
        "name": "Office & Supplies",
        "keywords": ["office", "supplies", "paper", "printer", "ink", "staples", "desk", "chair"],
        "icon": "🏢"
    },
    "technology": {
        "name": "Technology",
        "keywords": ["software", "hosting", "domain", "saas", "subscription", "aws", "digitalocean", "github", "figma", "notion"],
        "icon": "💻"
    },
    "marketing": {
        "name": "Marketing & Advertising",
        "keywords": ["marketing", "advertising", "facebook", "google ads", "ads", "promotion", "seo", "content", "social media"],
        "icon": "📢"
    },
    "travel": {
        "name": "Travel & Transportation",
        "keywords": ["travel", "flight", "hotel", "uber", "lyft", "taxi", "train", "rental car", "airbnb", "booking"],
        "icon": "✈️"
    },
    "food": {
        "name": "Food & Dining",
        "keywords": ["restaurant", "food", "meal", "lunch", "dinner", "breakfast", "catering", "doordash", "ubereats", "grubhub"],
        "icon": "🍔"
    },
    "utilities": {
        "name": "Utilities & Services",
        "keywords": ["electricity", "water", "gas", "internet", "phone", "utility", "rent", "lease"],
        "icon": "⚡"
    },
    "professional": {
        "name": "Professional Services",
        "keywords": ["accountant", "lawyer", "legal", "consulting", "freelancer", "contractor", "bookkeeper"],
        "icon": "👔"
    },
    "education": {
        "name": "Education & Training",
        "keywords": ["course", "training", "book", "education", "udemy", "coursera", "conference", "workshop"],
        "icon": "📚"
    },
    "equipment": {
        "name": "Equipment & Hardware",
        "keywords": ["computer", "laptop", "monitor", "keyboard", "mouse", "server", "hardware", "device"],
        "icon": "🔧"
    },
    "other": {
        "name": "Other",
        "keywords": [],
        "icon": "📦"
    }
}


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


def load_expenses():
    """Load expenses from file."""
    return load_json(EXPENSES_FILE, {"expenses": []})


def load_categories():
    """Load categories from file."""
    data = load_json(CATEGORIES_FILE, {"categories": DEFAULT_CATEGORIES})
    if not data.get("categories"):
        data["categories"] = DEFAULT_CATEGORIES
    return data.get("categories", DEFAULT_CATEGORIES)


def save_expenses(data):
    """Save expenses to file."""
    return save_json(EXPENSES_FILE, data)


def save_categories(categories):
    """Save categories to file."""
    return save_json(CATEGORIES_FILE, {"categories": categories})


def auto_categorize(description, categories=None):
    """Automatically categorize expense based on description."""
    if categories is None:
        categories = load_categories()
    
    description_lower = description.lower()
    
    for cat_id, cat_data in categories.items():
        keywords = cat_data.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in description_lower:
                return cat_id
    
    return "other"


def add_expense(amount, description, category=None, date=None, notes=None):
    """Add a new expense with auto-categorization."""
    logger.info(f"Adding expense: {amount} - {description}")
    
    expenses_data = load_expenses()
    categories = load_categories()
    
    if category is None:
        category = auto_categorize(description, categories)
    
    expense = {
        "id": str(uuid.uuid4()),
        "amount": float(amount),
        "description": description,
        "category": category,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat(),
        "notes": notes or "",
        "verified": False
    }
    
    expenses_data["expenses"].append(expense)
    
    if save_expenses(expenses_data):
        logger.info(f"Expense added: {description} -> {category}")
        return expense
    else:
        logger.error("Failed to save expense")
        return None


def list_expenses(category=None, start_date=None, end_date=None, unverified_only=False):
    """List expenses with optional filters."""
    expenses_data = load_expenses()
    expenses = expenses_data.get("expenses", [])
    
    if category:
        expenses = [e for e in expenses if e["category"] == category]
    if start_date:
        expenses = [e for e in expenses if e.get("date", "") >= start_date]
    if end_date:
        expenses = [e for e in expenses if e.get("date", "") <= end_date]
    if unverified_only:
        expenses = [e for e in expenses if not e.get("verified", False)]
    
    return sorted(expenses, key=lambda x: (x.get("date", ""), x["created_at"]), reverse=True)


def get_expense(expense_id):
    """Get expense by ID."""
    expenses_data = load_expenses()
    for e in expenses_data.get("expenses", []):
        if e["id"] == expense_id:
            return e
    return None


def update_expense(expense_id, updates):
    """Update expense fields."""
    expenses_data = load_expenses()
    
    for e in expenses_data.get("expenses", []):
        if e["id"] == expense_id:
            e.update(updates)
            if save_expenses(expenses_data):
                logger.info(f"Expense {expense_id} updated")
                return e
            break
    
    return None


def recategorize_expense(expense_id, new_category):
    """Recategorize an expense."""
    return update_expense(expense_id, {"category": new_category})


def delete_expense(expense_id):
    """Delete an expense."""
    expenses_data = load_expenses()
    
    for i, e in enumerate(expenses_data.get("expenses", [])):
        if e["id"] == expense_id:
            deleted = expenses_data["expenses"].pop(i)
            if save_expenses(expenses_data):
                logger.info(f"Deleted expense: {deleted['description']}")
                return True
            break
    
    return False


def get_category_summary(start_date=None, end_date=None):
    """Get spending summary by category."""
    expenses = list_expenses(start_date=start_date, end_date=end_date)
    categories = load_categories()
    
    summary = defaultdict(lambda: {"total": 0.0, "count": 0, "items": []})
    total = 0.0
    
    for e in expenses:
        cat_id = e["category"]
        summary[cat_id]["total"] += e["amount"]
        summary[cat_id]["count"] += 1
        summary[cat_id]["items"].append(e)
        total += e["amount"]
    
    result = []
    for cat_id, data in summary.items():
        cat_info = categories.get(cat_id, {"name": cat_id, "icon": "📦"})
        result.append({
            "category_id": cat_id,
            "name": cat_info.get("name", cat_id),
            "icon": cat_info.get("icon", "📦"),
            "total": data["total"],
            "count": data["count"],
            "percentage": (data["total"] / total * 100) if total > 0 else 0
        })
    
    return sorted(result, key=lambda x: x["total"], reverse=True)


def get_monthly_summary(year=None):
    """Get monthly spending summary."""
    if year is None:
        year = datetime.now().year
    
    expenses_data = load_expenses()
    monthly = defaultdict(lambda: {"total": 0.0, "count": 0})
    
    for e in expenses_data.get("expenses", []):
        date_str = e.get("date", "")
        if date_str.startswith(str(year)):
            month = date_str[5:7]
            monthly[month]["total"] += e["amount"]
            monthly[month]["count"] += 1
    
    result = []
    for month in range(1, 13):
        month_str = f"{month:02d}"
        data = monthly.get(month_str, {"total": 0.0, "count": 0})
        month_name = datetime(int(year), month, 1).strftime("%B")
        result.append({
            "month": month,
            "month_name": month_name,
            "year": year,
            "total": data["total"],
            "count": data["count"]
        })
    
    return result


def add_category(category_id, name, keywords, icon="📦"):
    """Add a new category."""
    categories = load_categories()
    
    if category_id in categories:
        logger.warning(f"Category {category_id} already exists")
        return None
    
    categories[category_id] = {
        "name": name,
        "keywords": keywords,
        "icon": icon
    }
    
    if save_categories(categories):
        logger.info(f"Category {category_id} added")
        return categories[category_id]
    
    return None


def update_category_keywords(category_id, keywords):
    """Update category keywords."""
    categories = load_categories()
    
    if category_id not in categories:
        logger.warning(f"Category {category_id} not found")
        return None
    
    categories[category_id]["keywords"] = keywords
    
    if save_categories(categories):
        logger.info(f"Category {category_id} keywords updated")
        return categories[category_id]
    
    return None


def list_categories():
    """List all categories."""
    categories = load_categories()
    result = []
    
    for cat_id, cat_data in categories.items():
        result.append({
            "id": cat_id,
            "name": cat_data.get("name", cat_id),
            "icon": cat_data.get("icon", "📦"),
            "keywords": cat_data.get("keywords", [])
        })
    
    return result


def print_expense(e, categories):
    """Pretty print an expense."""
    cat_info = categories.get(e["category"], {"name": e["category"], "icon": "📦"})
    print(f"\n💸 Expense: {e['description']}")
    print(f"   Amount:     {e['amount']:.2f} EUR")
    print(f"   Category:  {cat_info.get('icon')} {cat_info.get('name', e['category'])}")
    print(f"   Date:      {e.get('date', 'N/A')}")
    if e.get("notes"):
        print(f"   Notes:     {e['notes']}")
    verified = "✅" if e.get("verified") else "⏳"
    print(f"   Verified:  {verified}")


def cmd_add(args):
    """Handle add command."""
    expense = add_expense(
        amount=args.amount,
        description=args.description,
        category=args.category,
        date=args.date,
        notes=args.notes
    )
    
    if expense:
        categories = load_categories()
        print(f"✅ Expense added")
        print_expense(expense, categories)
    else:
        print("❌ Failed to add expense")
        sys.exit(1)


def cmd_list(args):
    """Handle list command."""
    expenses = list_expenses(
        category=args.category,
        start_date=args.start,
        end_date=args.end,
        unverified_only=args.unverified
    )
    
    if not expenses:
        print("No expenses found.")
        return
    
    categories = load_categories()
    print(f"\n📋 Found {len(expenses)} expense(s):\n")
    
    for e in expenses:
        cat_info = categories.get(e["category"], {"name": e["category"], "icon": "📦"})
        verified = "✅" if e.get("verified") else "⏳"
        print(f"  💸 {e['amount']:>10.2f} | {cat_info.get('icon')} {e['description'][:30]:<30} | {e.get('date', 'N/A')} {verified}")


def cmd_show(args):
    """Handle show command."""
    expense = get_expense(args.expense_id)
    if expense:
        categories = load_categories()
        print_expense(expense, categories)
    else:
        print(f"❌ Expense not found: {args.expense_id}")
        sys.exit(1)


def cmd_recategorize(args):
    """Handle recategorize command."""
    result = recategorize_expense(args.expense_id, args.category)
    if result:
        categories = load_categories()
        print(f"✅ Expense recategorized to: {args.category}")
        print_expense(result, categories)
    else:
        print("❌ Failed to recategorize expense")
        sys.exit(1)


def cmd_verify(args):
    """Handle verify command."""
    result = update_expense(args.expense_id, {"verified": True})
    if result:
        print(f"✅ Expense verified")
    else:
        print("❌ Failed to verify expense")
        sys.exit(1)


def cmd_delete(args):
    """Handle delete command."""
    if delete_expense(args.expense_id):
        print(f"✅ Expense deleted")
    else:
        print("❌ Failed to delete expense")
        sys.exit(1)


def cmd_summary(args):
    """Handle summary command."""
    year = int(args.year) if args.year else datetime.now().year
    
    if args.monthly:
        monthly = get_monthly_summary(year)
        print(f"\n📊 Monthly Spending Summary {year}\n{'='*50}")
        
        for m in monthly:
            bar = "█" * int(m["total"] / 100)
            print(f"  {m['month_name']:<10} {m['total']:>10.2f} EUR ({m['count']:>3} items) {bar}")
        
        total = sum(m["total"] for m in monthly)
        print(f"\n  {'TOTAL':<10} {total:>10.2f} EUR")
    else:
        summary = get_category_summary(start_date=f"{year}-01-01" if args.year else None, 
                                        end_date=f"{year}-12-31" if args.year else None)
        
        print(f"\n📊 Category Summary {year if args.year else 'All Time'}\n{'='*50}")
        
        for s in summary:
            bar = "█" * int(s["percentage"] / 2)
            print(f"  {s['icon']} {s['name']:<25} {s['total']:>10.2f} EUR ({s['percentage']:>5.1f}%) {bar}")
        
        total = sum(s["total"] for s in summary)
        print(f"\n  {'TOTAL':<25} {total:>10.2f} EUR")


def cmd_categories_list(args):
    """Handle categories list command."""
    cats = list_categories()
    print(f"\n📁 Available Categories ({len(cats)}):\n")
    for c in cats:
        print(f"  {c['icon']} {c['id']}: {c['name']}")
        if c["keywords"]:
            print(f"      Keywords: {', '.join(c['keywords'][:5])}{'...' if len(c['keywords']) > 5 else ''}")


def cmd_category_add(args):
    """Handle category add command."""
    keywords = args.keywords.split(",") if args.keywords else []
    keywords = [k.strip() for k in keywords]
    
    result = add_category(args.category_id, args.name, keywords, args.icon)
    if result:
        print(f"✅ Category '{args.category_id}' created")
    else:
        print("❌ Failed to create category (may already exist)")
        sys.exit(1)


def cmd_category_keywords(args):
    """Handle category keywords update command."""
    keywords = args.keywords.split(",") if args.keywords else []
    keywords = [k.strip() for k in keywords]
    
    result = update_category_keywords(args.category_id, keywords)
    if result:
        print(f"✅ Category '{args.category_id}' keywords updated")
        print(f"   Keywords: {', '.join(keywords)}")
    else:
        print("❌ Failed to update category")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Expense Categorizer Agent - Categorize and analyze expenses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --amount 150 --description "Office Supplies"
  %(prog)s add --amount 50 --description "GitHub Subscription" --category technology
  %(prog)s list --category technology --start 2026-01-01
  %(prog)s list --unverified
  %(prog)s summary
  %(prog)s summary --monthly --year 2026
  %(prog)s categories-list
  %(prog)s category-add hosting "Hosting Services" --keywords "hosting,vps,server"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--amount", required=True, type=float, help="Expense amount")
    add_parser.add_argument("--description", required=True, help="Expense description")
    add_parser.add_argument("--category", help="Category ID (auto-categorized if not provided)")
    add_parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    add_parser.add_argument("--notes", help="Additional notes")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List expenses")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    list_parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    list_parser.add_argument("--unverified", action="store_true", help="Show only unverified")
    
    # Show command
    show_parser = subparsers.add_parser("show", help="Show expense details")
    show_parser.add_argument("expense_id", help="Expense ID")
    
    # Recategorize command
    recat_parser = subparsers.add_parser("recategorize", help="Change expense category")
    recat_parser.add_argument("expense_id", help="Expense ID")
    recat_parser.add_argument("category", help="New category ID")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Mark expense as verified")
    verify_parser.add_argument("expense_id", help="Expense ID")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an expense")
    delete_parser.add_argument("expense_id", help="Expense ID")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Show spending summary")
    summary_parser.add_argument("--monthly", action="store_true", help="Show monthly breakdown")
    summary_parser.add_argument("--year", help="Year for summary (default: current)")
    
    # Categories list command
    subparsers.add_parser("categories-list", help="List all categories")
    
    # Category add command
    cat_add_parser = subparsers.add_parser("category-add", help="Add a new category")
    cat_add_parser.add_argument("category_id", help="Category ID")
    cat_add_parser.add_argument("name", help="Category name")
    cat_add_parser.add_argument("--keywords", help="Comma-separated keywords")
    cat_add_parser.add_argument("--icon", default="📦", help="Category icon (emoji)")
    
    # Category keywords command
    cat_kw_parser = subparsers.add_parser("category-keywords", help="Update category keywords")
    cat_kw_parser.add_argument("category_id", help="Category ID")
    cat_kw_parser.add_argument("keywords", help="Comma-separated keywords")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "show": cmd_show,
        "recategorize": cmd_recategorize,
        "verify": cmd_verify,
        "delete": cmd_delete,
        "summary": cmd_summary,
        "categories-list": cmd_categories_list,
        "category-add": cmd_category_add,
        "category-keywords": cmd_category_keywords
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
