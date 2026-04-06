#!/usr/bin/env python3
"""
Budget Tracker Agent
Manages budgets, tracks spending against budget limits, and provides alerts.
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

BUDGETS_FILE = DATA_DIR / "budgets.json"
SPENDING_FILE = DATA_DIR / "budget_spending.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "budget_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BudgetTracker")


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


def load_budgets():
    """Load budgets from file."""
    return load_json(BUDGETS_FILE, {"budgets": {}})


def load_spending():
    """Load spending records from file."""
    return load_json(SPENDING_FILE, {"spending": []})


def save_budgets(data):
    """Save budgets to file."""
    return save_json(BUDGETS_FILE, data)


def save_spending(data):
    """Save spending to file."""
    return save_json(SPENDING_FILE, data)


def create_budget(name, amount, period="monthly", category=None, description=None):
    """Create a new budget."""
    logger.info(f"Creating budget: {name} - {amount} {period}")
    
    budgets_data = load_budgets()
    
    budget_id = name.lower().replace(" ", "-")
    
    if budget_id in budgets_data.get("budgets", {}):
        logger.error(f"Budget {budget_id} already exists")
        return None
    
    budget = {
        "id": budget_id,
        "name": name,
        "amount": float(amount),
        "period": period,  # "weekly", "monthly", "quarterly", "yearly"
        "category": category,
        "description": description or "",
        "created_at": datetime.now().isoformat(),
        "active": True,
        " rollover": False
    }
    
    budgets_data["budgets"][budget_id] = budget
    
    if save_budgets(budgets_data):
        logger.info(f"Budget {name} created successfully")
        return budget
    else:
        logger.error("Failed to save budget")
        return None


def list_budgets(active_only=False):
    """List all budgets."""
    budgets_data = load_budgets()
    budgets = budgets_data.get("budgets", {})
    
    if active_only:
        budgets = {k: v for k, v in budgets.items() if v.get("active", True)}
    
    return budgets


def get_budget(budget_id):
    """Get budget by ID."""
    budgets_data = load_budgets()
    return budgets_data.get("budgets", {}).get(budget_id)


def update_budget(budget_id, updates):
    """Update budget fields."""
    budgets_data = load_budgets()
    
    if budget_id not in budgets_data.get("budgets", {}):
        return None
    
    budgets_data["budgets"][budget_id].update(updates)
    
    if save_budgets(budgets_data):
        logger.info(f"Budget {budget_id} updated")
        return budgets_data["budgets"][budget_id]
    
    return None


def delete_budget(budget_id):
    """Delete a budget."""
    budgets_data = load_budgets()
    
    if budget_id in budgets_data.get("budgets", {}):
        del budgets_data["budgets"][budget_id]
        if save_budgets(budgets_data):
            logger.info(f"Budget {budget_id} deleted")
            return True
    
    return False


def get_period_dates(period, reference_date=None):
    """Get start and end dates for a budget period."""
    if reference_date is None:
        reference_date = datetime.now()
    elif isinstance(reference_date, str):
        reference_date = datetime.fromisoformat(reference_date)
    
    if period == "weekly":
        start = reference_date - timedelta(days=reference_date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    elif period == "monthly":
        start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
        else:
            end = start.replace(month=start.month + 1) - timedelta(seconds=1)
    elif period == "quarterly":
        quarter = (reference_date.month - 1) // 3
        start_month = quarter * 3 + 1
        start = reference_date.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month >= 10:
            end = start.replace(year=start.year + 1, month=start.month - 9) - timedelta(seconds=1)
        else:
            end = start.replace(month=start.month + 3) - timedelta(seconds=1)
    elif period == "yearly":
        start = reference_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = reference_date.replace(year=start.year + 1, month=1, day=1) - timedelta(seconds=1)
    else:
        start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1) - timedelta(seconds=1)
        else:
            end = start.replace(month=start.month + 1) - timedelta(seconds=1)
    
    return start, end


def calculate_spent(budget_id, start_date=None, end_date=None):
    """Calculate total spent for a budget within period."""
    spending_data = load_spending()
    budget = get_budget(budget_id)
    
    if not budget:
        return 0.0
    
    if start_date is None or end_date is None:
        start, end = get_period_dates(budget["period"])
        start_date = start.isoformat()[:10]
        end_date = end.isoformat()[:10]
    
    total = 0.0
    for s in spending_data.get("spending", []):
        if s.get("budget_id") == budget_id:
            s_date = s.get("date", "")
            if start_date <= s_date <= end_date:
                total += s.get("amount", 0)
    
    return total


def record_spending(budget_id, amount, description, date=None):
    """Record spending against a budget."""
    budget = get_budget(budget_id)
    if not budget:
        logger.error(f"Budget {budget_id} not found")
        return None
    
    spending_data = load_spending()
    
    spending = {
        "id": str(uuid.uuid4()),
        "budget_id": budget_id,
        "amount": float(amount),
        "description": description,
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "created_at": datetime.now().isoformat()
    }
    
    spending_data["spending"].append(spending)
    
    if save_spending(spending_data):
        logger.info(f"Spending recorded: {amount} against {budget_id}")
        return spending
    else:
        logger.error("Failed to save spending")
        return None


def get_budget_status(budget_id):
    """Get budget status with spending details."""
    budget = get_budget(budget_id)
    if not budget:
        return None
    
    start, end = get_period_dates(budget["period"])
    spent = calculate_spent(budget_id, start.isoformat()[:10], end.isoformat()[:10])
    
    remaining = budget["amount"] - spent
    percentage = (spent / budget["amount"] * 100) if budget["amount"] > 0 else 0
    
    # Determine status
    if percentage >= 100:
        status = "exceeded"
    elif percentage >= 90:
        status = "critical"
    elif percentage >= 75:
        status = "warning"
    else:
        status = "ok"
    
    return {
        "budget": budget,
        "spent": spent,
        "remaining": remaining,
        "percentage": percentage,
        "status": status,
        "period_start": start.isoformat()[:10],
        "period_end": end.isoformat()[:10],
        "days_remaining": (end - datetime.now()).days
    }


def get_all_budgets_status():
    """Get status of all active budgets."""
    budgets = list_budgets(active_only=True)
    result = []
    
    for budget_id, budget in budgets.items():
        status = get_budget_status(budget_id)
        if status:
            result.append(status)
    
    return sorted(result, key=lambda x: x["percentage"], reverse=True)


def print_budget_status(status):
    """Pretty print budget status."""
    b = status["budget"]
    icons = {"ok": "✅", "warning": "⚠️", "critical": "🔴", "exceeded": "🚫"}
    icon = icons.get(status["status"], "•")
    
    print(f"\n{icon} Budget: {b['name']}")
    print(f"   Amount:      {b['amount']:.2f} EUR ({b['period']})")
    print(f"   Spent:       {status['spent']:.2f} EUR ({status['percentage']:.1f}%)")
    print(f"   Remaining:   {status['remaining']:.2f} EUR")
    print(f"   Period:      {status['period_start']} to {status['period_end']}")
    print(f"   Days Left:   {status['days_remaining']}")
    
    if status["remaining"] < 0:
        print(f"   ⚠️  OVER BUDGET by {-status['remaining']:.2f} EUR!")


def cmd_create(args):
    """Handle create command."""
    budget = create_budget(
        name=args.name,
        amount=args.amount,
        period=args.period,
        category=args.category,
        description=args.description
    )
    
    if budget:
        print(f"✅ Budget '{budget['name']}' created")
        print(f"   Amount: {budget['amount']:.2f} EUR per {budget['period']}")
    else:
        print("❌ Failed to create budget (may already exist)")
        sys.exit(1)


def cmd_list(args):
    """Handle list command."""
    budgets = list_budgets(active_only=args.active)
    
    if not budgets:
        print("No budgets found.")
        return
    
    print(f"\n📋 Found {len(budgets)} budget(s):\n")
    
    for budget_id, budget in budgets.items():
        status = get_budget_status(budget_id)
        icons = {"ok": "✅", "warning": "⚠️", "critical": "🔴", "exceeded": "🚫"}
        icon = icons.get(status["status"], "•") if status else "•"
        active_str = "🟢" if budget.get("active", True) else "⚫"
        print(f"  {active_str} {icon} {budget['name']:<25} {status['spent'] if status else 0:.2f}/{budget['amount']:.2f} EUR ({status['percentage'] if status else 0:.1f}%)")


def cmd_status(args):
    """Handle status command."""
    if args.budget == "all":
        statuses = get_all_budgets_status()
        if not statuses:
            print("No active budgets.")
            return
        
        print(f"\n📊 All Budgets Status\n{'='*50}")
        for s in statuses:
            print_budget_status(s)
    else:
        status = get_budget_status(args.budget)
        if status:
            print_budget_status(status)
        else:
            print(f"❌ Budget not found: {args.budget}")
            sys.exit(1)


def cmd_spend(args):
    """Handle spend command."""
    spending = record_spending(
        budget_id=args.budget,
        amount=args.amount,
        description=args.description,
        date=args.date
    )
    
    if spending:
        print(f"✅ Spending recorded: {args.amount} EUR")
        
        # Check if over budget
        status = get_budget_status(args.budget)
        if status and status["remaining"] < 0:
            print(f"⚠️  WARNING: Budget exceeded by {-status['remaining']:.2f} EUR!")
    else:
        print("❌ Failed to record spending")
        sys.exit(1)


def cmd_update(args):
    """Handle update command."""
    updates = {}
    if args.amount is not None:
        updates["amount"] = float(args.amount)
    if args.description is not None:
        updates["description"] = args.description
    
    result = update_budget(args.budget, updates)
    if result:
        print(f"✅ Budget '{args.budget}' updated")
        status = get_budget_status(args.budget)
        if status:
            print_budget_status(status)
    else:
        print("❌ Failed to update budget")
        sys.exit(1)


def cmd_activate(args):
    """Handle activate command."""
    result = update_budget(args.budget, {"active": True})
    if result:
        print(f"✅ Budget '{args.budget}' activated")
    else:
        print("❌ Failed to activate budget")
        sys.exit(1)


def cmd_deactivate(args):
    """Handle deactivate command."""
    result = update_budget(args.budget, {"active": False})
    if result:
        print(f"✅ Budget '{args.budget}' deactivated")
    else:
        print("❌ Failed to deactivate budget")
        sys.exit(1)


def cmd_delete(args):
    """Handle delete command."""
    if delete_budget(args.budget):
        print(f"✅ Budget '{args.budget}' deleted")
    else:
        print("❌ Failed to delete budget")
        sys.exit(1)


def cmd_alerts(args):
    """Handle alerts command - show budgets needing attention."""
    statuses = get_all_budgets_status()
    alerts = [s for s in statuses if s["status"] in ["warning", "critical", "exceeded"]]
    
    if not alerts:
        print("✅ All budgets are within safe limits!")
        return
    
    print(f"\n⚠️  Budget Alerts ({len(alerts)})\n{'='*50}")
    for s in alerts:
        b = s["budget"]
        if s["status"] == "exceeded":
            print(f"🚫 {b['name']}: EXCEEDED by {-s['remaining']:.2f} EUR!")
        elif s["status"] == "critical":
            print(f"🔴 {b['name']}: {s['percentage']:.1f}% used, {s['remaining']:.2f} EUR remaining")
        elif s["status"] == "warning":
            print(f"⚠️  {b['name']}: {s['percentage']:.1f}% used, {s['remaining']:.2f} EUR remaining")


def main():
    parser = argparse.ArgumentParser(
        description="Budget Tracker Agent - Manage budgets and track spending",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "Marketing" --amount 500 --period monthly
  %(prog)s spend marketing --amount 150 --description "Facebook Ads"
  %(prog)s status all
  %(prog)s status marketing
  %(prog)s alerts
  %(prog)s list --active
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new budget")
    create_parser.add_argument("--name", required=True, help="Budget name")
    create_parser.add_argument("--amount", required=True, type=float, help="Budget amount")
    create_parser.add_argument("--period", default="monthly", choices=["weekly", "monthly", "quarterly", "yearly"], help="Budget period")
    create_parser.add_argument("--category", help="Category (optional)")
    create_parser.add_argument("--description", help="Description")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all budgets")
    list_parser.add_argument("--active", action="store_true", help="Show only active budgets")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show budget status")
    status_parser.add_argument("budget", help="Budget ID or 'all'")
    
    # Spend command
    spend_parser = subparsers.add_parser("spend", help="Record spending against a budget")
    spend_parser.add_argument("budget", help="Budget ID")
    spend_parser.add_argument("--amount", required=True, type=float, help="Spending amount")
    spend_parser.add_argument("--description", required=True, help="Description")
    spend_parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update budget amount")
    update_parser.add_argument("budget", help="Budget ID")
    update_parser.add_argument("--amount", type=float, help="New budget amount")
    update_parser.add_argument("--description", help="New description")
    
    # Activate command
    subparsers.add_parser("activate", help="Activate a budget").add_argument("budget", help="Budget ID")
    
    # Deactivate command
    subparsers.add_parser("deactivate", help="Deactivate a budget").add_argument("budget", help="Budget ID")
    
    # Delete command
    subparsers.add_parser("delete", help="Delete a budget").add_argument("budget", help="Budget ID")
    
    # Alerts command
    subparsers.add_parser("alerts", help="Show budgets needing attention")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "create": cmd_create,
        "list": cmd_list,
        "status": cmd_status,
        "spend": cmd_spend,
        "update": cmd_update,
        "activate": cmd_activate,
        "deactivate": cmd_deactivate,
        "delete": cmd_delete,
        "alerts": cmd_alerts
    }
    
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
