#!/usr/bin/env python3
"""Analytics Dashboard - Revenue & Stats"""
import json
import os
from datetime import datetime

DATA_FILE = "data/revenue.json"

def load_stats():
    """Load revenue stats"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"today": 0, "week": 0, "month": 0}

def show_dashboard():
    """Show dashboard summary"""
    stats = load_stats()
    print("=== 📊 ANALYTICS DASHBOARD ===")
    print(f"Heute: €{stats.get('today', 0)}")
    print(f"Woche: €{stats.get('week', 0)}")
    print(f"Monat: €{stats.get('month', 0)}")
    print(f"Stand: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    return stats

if __name__ == "__main__":
    show_dashboard()
