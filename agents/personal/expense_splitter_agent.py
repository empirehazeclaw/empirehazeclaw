#!/usr/bin/env python3
"""
Expense Splitter Agent
Splits expenses among groups, tracks who owes whom, settles debts.
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
        logging.FileHandler(LOG_DIR / "expense_splitter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExpenseSplitterAgent")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/expense_splitter.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"groups": [], "expenses": [], "balances": {}, "last_expense_id": 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_group(args):
    """Create a new group."""
    data = load_data()
    group = {
        "id": len(data["groups"]) + 1,
        "name": args.name,
        "members": args.members,
        "created_at": datetime.now().isoformat()
    }
    data["groups"].append(group)
    save_data(data)
    logger.info(f"Created group {group['id']}: {group['name']}")
    print(f"✅ Created group #{group['id']}: {group['name']}")
    print(f"   Members: {', '.join(args.members)}")
    return group

def add_expense(args):
    """Add an expense to a group."""
    data = load_data()
    
    group = None
    for g in data["groups"]:
        if g["id"] == int(args.group):
            group = g
            break
    
    if not group:
        print(f"Group #{args.group} not found.")
        return
    
    if args.split_with:
        participants = args.split_with
    else:
        participants = group["members"]
    
    num_people = len(participants)
    per_person = float(args.amount) / num_people
    
    data["last_expense_id"] += 1
    expense = {
        "id": data["last_expense_id"],
        "group_id": int(args.group),
        "description": args.description,
        "amount": float(args.amount),
        "paid_by": args.paid_by,
        "split_with": participants,
        "per_person": round(per_person, 2),
        "date": args.date or datetime.now().isoformat()[:10],
        "created_at": datetime.now().isoformat()
    }
    
    data["expenses"].append(expense)
    
    if args.paid_by not in data["balances"]:
        data["balances"][args.paid_by] = {}
    
    for member in participants:
        if member not in data["balances"]:
            data["balances"][member] = {}
        if args.paid_by not in data["balances"][member]:
            data["balances"][member][args.paid_by] = 0
        if args.paid_by not in data["balances"][args.paid_by]:
            data["balances"][args.paid_by][member] = 0
        
        if member != args.paid_by:
            data["balances"][member][args.paid_by] += per_person
            data["balances"][args.paid_by][member] -= per_person
    
    save_data(data)
    logger.info(f"Added expense {expense['id']}: {expense['description']}")
    print(f"✅ Added expense: {args.description}")
    print(f"   Amount: ${float(args.amount):.2f} | Paid by: {args.paid_by}")
    print(f"   Split {num_people} ways: ${per_person:.2f} each")
    return expense

def list_groups(args):
    """List all groups."""
    data = load_data()
    if not data["groups"]:
        print("No groups found.")
        return
    
    print(f"\n👥 Groups ({len(data['groups'])}):\n")
    for g in data["groups"]:
        expense_count = len([e for e in data["expenses"] if e["group_id"] == g["id"]])
        print(f"  [{g['id']}] {g['name']}")
        print(f"      Members: {', '.join(g['members'])}")
        print(f"      Expenses: {expense_count}")
        print()

def list_expenses(args):
    """List expenses for a group."""
    data = load_data()
    expenses = data["expenses"]
    
    if args.group:
        expenses = [e for e in expenses if e["group_id"] == int(args.group)]
    
    if not expenses:
        print("No expenses found.")
        return
    
    print(f"\n💰 Expenses ({len(expenses)}):\n")
    for e in expenses:
        print(f"  [{e['id']}] {e['description']}")
        print(f"      Amount: ${e['amount']:.2f} | Paid by: {e['paid_by']}")
        print(f"      Split: {', '.join(e['split_with'])} (${e['per_person']:.2f}/person)")
        print(f"      Date: {e['date']}")
        print()

def balances(args):
    """Show who owes whom."""
    data = load_data()
    
    if args.member:
        if args.member not in data["balances"]:
            print(f"No balance data for {args.member}.")
            return
        
        print(f"\n💳 Balances for {args.member}:\n")
        found = False
        for other, amount in data["balances"][args.member].items():
            if amount > 0.01:
                print(f"  {other} owes {args.member}: ${amount:.2f}")
                found = True
            elif amount < -0.01:
                print(f"  {args.member} owes {other}: ${-amount:.2f}")
                found = True
        if not found:
            print("  All settled up!")
    else:
        net_balances = defaultdict(float)
        for person, others in data["balances"].items():
            for other, amount in others.items():
                if amount > 0.01:
                    net_balances[person] -= amount
                elif amount < -0.01:
                    net_balances[person] += -amount
        
        print(f"\n💳 Net Balances:\n")
        for person in sorted(net_balances.keys()):
            bal = net_balances[person]
            if bal > 0.01:
                print(f"  {person}: is owed $${bal:.2f}")
            elif bal < -0.01:
                print(f"  {person}: owes ${-bal:.2f}")
            else:
                print(f"  {person}: settled")
        
        if not net_balances:
            print("  No outstanding balances.")

def settle(args):
    """Record a payment between two members."""
    data = load_data()
    
    from_member = args.from_
    to_member = args.to
    
    if from_member not in data["balances"]:
        data["balances"][from_member] = {}
    if to_member not in data["balances"][from_member]:
        data["balances"][from_member][to_member] = 0
    if from_member not in data["balances"][to_member]:
        data["balances"][to_member][from_member] = 0
    
    old_balance = data["balances"][from_member][to_member]
    data["balances"][from_member][to_member] -= float(args.amount)
    
    if from_member not in data["balances"]:
        data["balances"][from_member] = {}
    if to_member not in data["balances"]:
        data["balances"][to_member] = {}
    if from_member not in data["balances"][to_member]:
        data["balances"][to_member][from_member] = 0
    data["balances"][to_member][from_member] -= float(args.amount)
    
    save_data(data)
    print(f"✅ Recorded payment: {from_member} paid ${args.amount} to {to_member}")
    print(f"   Previous balance: ${old_balance:.2f} | New balance: ${data['balances'][from_member][to_member]:.2f}")

def summary(args):
    """Show expense summary for a group."""
    data = load_data()
    expenses = data["expenses"]
    
    if args.group:
        expenses = [e for e in expenses if e["group_id"] == int(args.group)]
    
    if not expenses:
        print("No expenses found.")
        return
    
    total = sum(e["amount"] for e in expenses)
    by_payer = defaultdict(float)
    for e in expenses:
        by_payer[e["paid_by"]] += e["amount"]
    
    print(f"\n📊 Expense Summary:\n")
    print(f"  Total Expenses: ${total:.2f}")
    print(f"  Number of Expenses: {len(expenses)}")
    print(f"\n  By Payer:")
    for payer, amount in sorted(by_payer.items()):
        print(f"    {payer}: ${amount:.2f}")

def main():
    parser = argparse.ArgumentParser(
        description="Expense Splitter Agent - Split expenses among groups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create-group --name "Trip to Paris" --members Alice Bob Charlie
  %(prog)s add --group 1 --description "Dinner" --amount 90 --paid-by Alice
  %(prog)s add --group 1 --description "Taxi" --amount 30 --paid-by Bob --split-with Alice Bob Charlie
  %(prog)s list-groups
  %(prog)s list-expenses --group 1
  %(prog)s balances --member Alice
  %(prog)s balances
  %(prog)s settle --from Bob --to Alice --amount 15
  %(prog)s summary --group 1
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_create = subparsers.add_parser("create-group", help="Create a group")
    p_create.add_argument("--name", required=True, help="Group name")
    p_create.add_argument("--members", required=True, nargs="+", help="Member names")
    
    p_add = subparsers.add_parser("add", help="Add expense")
    p_add.add_argument("--group", required=True, type=int, help="Group ID")
    p_add.add_argument("--description", required=True, help="Expense description")
    p_add.add_argument("--amount", required=True, help="Amount")
    p_add.add_argument("--paid-by", required=True, help="Who paid")
    p_add.add_argument("--split-with", nargs="+", help="Who to split with (default: all members)")
    p_add.add_argument("--date", help="Date (YYYY-MM-DD)")
    
    p_list_groups = subparsers.add_parser("list-groups", help="List groups")
    
    p_list_exp = subparsers.add_parser("list-expenses", help="List expenses")
    p_list_exp.add_argument("--group", type=int, help="Filter by group")
    
    p_bal = subparsers.add_parser("balances", help="Show balances")
    p_bal.add_argument("--member", help="Show balances for specific member")
    
    p_settle = subparsers.add_parser("settle", help="Record a payment")
    p_settle.add_argument("--from", dest="from_", required=True, help="Payer")
    p_settle.add_argument("--to", required=True, help="Payee")
    p_settle.add_argument("--amount", required=True, help="Amount")
    
    p_summary = subparsers.add_parser("summary", help="Expense summary")
    p_summary.add_argument("--group", type=int, help="Filter by group")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "create-group":
            create_group(args)
        elif args.command == "add":
            add_expense(args)
        elif args.command == "list-groups":
            list_groups(args)
        elif args.command == "list-expenses":
            list_expenses(args)
        elif args.command == "balances":
            balances(args)
        elif args.command == "settle":
            settle(args)
        elif args.command == "summary":
            summary(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
