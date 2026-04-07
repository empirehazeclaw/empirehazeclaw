#!/usr/bin/env python3
"""
💰 FINANCE TRACKER
================
Tracks income, expenses, and profitability
"""

import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data/finance")
DATA_DIR.mkdir(exist_ok=True)

TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

def load_transactions():
    if TRANSACTIONS_FILE.exists():
        return json.load(open(TRANSACTIONS_FILE))
    return {"income": [], "expenses": []}

def save_transactions(data):
    json.dump(data, open(TRANSACTIONS_FILE, "w"), indent=2)

def add_income(amount, source, description=""):
    data = load_transactions()
    data["income"].append({
        "date": datetime.now().isoformat(),
        "amount": amount,
        "source": source,
        "description": description
    })
    save_transactions(data)
    return f"✅ Income added: €{amount}"

def add_expense(amount, category, description=""):
    data = load_transactions()
    data["expenses"].append({
        "date": datetime.now().isoformat(),
        "amount": amount,
        "category": category,
        "description": description
    })
    save_transactions(data)
    return f"✅ Expense added: €{amount}"

def get_summary():
    data = load_transactions()
    income = sum(t["amount"] for t in data["income"])
    expenses = sum(t["amount"] for t in data["expenses"])
    return {
        "income": income,
        "expenses": expenses,
        "profit": income - expenses,
        "transactions": len(data["income"]) + len(data["expenses"])
    }

# CLI
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        s = get_summary()
        print(f"💰 Finance Summary:")
        print(f"   Income: €{s['income']}")
        print(f"   Expenses: €{s['expenses']}")
        print(f"   Profit: €{s['profit']}")
    elif sys.argv[1] == "income":
        print(add_income(float(sys.argv[2]), sys.argv[3], " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""))
    elif sys.argv[1] == "expense":
        print(add_expense(float(sys.argv[2]), sys.argv[3], " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""))
