#!/usr/bin/env python3
"""
CFO Dashboard Agent
===================
Provides financial overview, revenue tracking, expense management, and KPI dashboards.
Reads/writes financial data from JSON files.
"""

import argparse
import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CFO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "cfo_dashboard.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/business")
DATA_DIR.mkdir(parents=True, exist_ok=True)
FINANCIALS_FILE = DATA_DIR / "financials.json"
REVENUE_FILE = DATA_DIR / "revenue.json"
EXPENSES_FILE = DATA_DIR / "expenses.json"
KPIS_FILE = DATA_DIR / "kpis.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not FINANCIALS_FILE.exists():
        save_json(FINANCIALS_FILE, {
            "currency": "USD",
            "fiscal_year_start": "01-01",
            "last_updated": datetime.now().isoformat(),
            "total_revenue": 0,
            "total_expenses": 0,
            "net_profit": 0
        })
    
    if not REVENUE_FILE.exists():
        save_json(REVENUE_FILE, {"sources": [], "total": 0})
    
    if not EXPENSES_FILE.exists():
        save_json(EXPENSES_FILE, {"categories": {}, "total": 0})
    
    if not KPIS_FILE.exists():
        save_json(KPIS_FILE, {
            "gross_margin": 0,
            "net_margin": 0,
            "burn_rate": 0,
            "runway_months": 0,
            "arr": 0,
            "mrr": 0
        })


def cmd_dashboard(args) -> int:
    """Display financial dashboard overview."""
    logger.info("Generating CFO dashboard...")
    
    financials = load_json(FINANCIALS_FILE)
    revenue = load_json(REVENUE_FILE)
    expenses = load_json(EXPENSES_FILE)
    kpis = load_json(KPIS_FILE)
    
    print("\n" + "="*60)
    print("💰 CFO DASHBOARD - Financial Overview")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"💵 Currency: {financials.get('currency', 'USD')}")
    print("-"*60)
    
    print("\n📊 REVENUE")
    print(f"   Total Revenue: ${financials.get('total_revenue', 0):,.2f}")
    print(f"   MRR (Monthly Recurring): ${kpis.get('mrr', 0):,.2f}")
    print(f"   ARR (Annual Recurring): ${kpis.get('arr', 0):,.2f}")
    
    print("\n💸 EXPENSES")
    print(f"   Total Expenses: ${financials.get('total_expenses', 0):,.2f}")
    if expenses.get('categories'):
        print("   By Category:")
        for cat, amt in expenses['categories'].items():
            print(f"      - {cat}: ${amt:,.2f}")
    
    print("\n📈 PROFITABILITY")
    net = financials.get('total_revenue', 0) - financials.get('total_expenses', 0)
    print(f"   Net Profit/Loss: ${net:,.2f}")
    print(f"   Gross Margin: {kpis.get('gross_margin', 0):.1f}%")
    print(f"   Net Margin: {kpis.get('net_margin', 0):.1f}%")
    
    print("\n⚡ KEY METRICS")
    print(f"   Burn Rate: ${kpis.get('burn_rate', 0):,.2f}/month")
    print(f"   Runway: {kpis.get('runway_months', 0)} months")
    
    print("\n" + "="*60)
    return 0


def cmd_add_revenue(args) -> int:
    """Add a new revenue entry."""
    logger.info(f"Adding revenue: {args.amount} from {args.source}")
    
    revenue = load_json(REVENUE_FILE)
    financials = load_json(FINANCIALS_FILE)
    
    entry = {
        "id": len(revenue.get('sources', [])) + 1,
        "source": args.source,
        "amount": float(args.amount),
        "date": datetime.now().isoformat(),
        "category": args.category or "general",
        "recurring": args.recurring
    }
    
    if 'sources' not in revenue:
        revenue['sources'] = []
    revenue['sources'].append(entry)
    revenue['total'] = sum(s['amount'] for s in revenue['sources'])
    
    financials['total_revenue'] = revenue['total']
    financials['last_updated'] = datetime.now().isoformat()
    
    save_json(REVENUE_FILE, revenue)
    save_json(FINANCIALS_FILE, financials)
    
    print(f"✅ Added revenue: ${args.amount} from {args.source}")
    return 0


def cmd_add_expense(args) -> int:
    """Add a new expense entry."""
    logger.info(f"Adding expense: {args.amount} for {args.description}")
    
    expenses = load_json(EXPENSES_FILE)
    financials = load_json(FINANCIALS_FILE)
    
    category = args.category or "general"
    if 'categories' not in expenses:
        expenses['categories'] = {}
    
    expenses['categories'][category] = expenses['categories'].get(category, 0) + float(args.amount)
    expenses['total'] = sum(expenses['categories'].values())
    
    financials['total_expenses'] = expenses['total']
    financials['last_updated'] = datetime.now().isoformat()
    
    save_json(EXPENSES_FILE, expenses)
    save_json(FINANCIALS_FILE, financials)
    
    print(f"✅ Added expense: ${args.amount} for {args.description} ({category})")
    return 0


def cmd_set_kpis(args) -> int:
    """Set KPI values."""
    logger.info("Updating KPIs...")
    
    kpis = load_json(KPIS_FILE)
    
    if args.mrr is not None:
        kpis['mrr'] = float(args.mrr)
        kpis['arr'] = float(args.mrr) * 12
    if args.gross_margin is not None:
        kpis['gross_margin'] = float(args.gross_margin)
    if args.net_margin is not None:
        kpis['net_margin'] = float(args.net_margin)
    if args.burn_rate is not None:
        kpis['burn_rate'] = float(args.burn_rate)
        revenue = load_json(FINANCIALS_FILE)
        if kpis['burn_rate'] > 0:
            current_cash = revenue.get('total_revenue', 0) - revenue.get('total_expenses', 0)
            kpis['runway_months'] = current_cash / kpis['burn_rate'] if current_cash > 0 else 0
    
    save_json(KPIS_FILE, kpis)
    
    print("✅ KPIs updated successfully")
    return 0


def cmd_report(args) -> int:
    """Generate financial report."""
    logger.info("Generating financial report...")
    
    financials = load_json(FINANCIALS_FILE)
    revenue = load_json(REVENUE_FILE)
    expenses = load_json(EXPENSES_FILE)
    kpis = load_json(KPIS_FILE)
    
    # Calculate trends
    total_rev = financials.get('total_revenue', 0)
    total_exp = financials.get('total_expenses', 0)
    net = total_rev - total_exp
    
    print("\n" + "="*60)
    print("📋 FINANCIAL REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    print("\n📊 INCOME STATEMENT")
    print(f"   Revenue:        ${total_rev:>12,.2f}")
    print(f"   Expenses:       ${total_exp:>12,.2f}")
    print(f"   {'─'*30}")
    print(f"   Net Profit:     ${net:>12,.2f}")
    
    if revenue.get('sources'):
        print("\n📑 REVENUE BREAKDOWN")
        for src in revenue['sources'][-10:]:  # Last 10 entries
            print(f"   {src.get('date','')[:10]} | {src.get('source',''):<20} | ${src.get('amount',0):>10,.2f}")
    
    if expenses.get('categories'):
        print("\n📑 EXPENSE BREAKDOWN")
        for cat, amt in expenses['categories'].items():
            pct = (amt / total_exp * 100) if total_exp > 0 else 0
            print(f"   {cat:<20} | ${amt:>10,.2f} | {pct:>5.1f}%")
    
    print("\n📈 KEY PERFORMANCE INDICATORS")
    print(f"   MRR:            ${kpis.get('mrr', 0):>12,.2f}")
    print(f"   ARR:            ${kpis.get('arr', 0):>12,.2f}")
    print(f"   Gross Margin:   {kpis.get('gross_margin', 0):>11.1f}%")
    print(f"   Net Margin:      {kpis.get('net_margin', 0):>11.1f}%")
    print(f"   Burn Rate:      ${kpis.get('burn_rate', 0):>12,.2f}/mo")
    print(f"   Runway:         {kpis.get('runway_months', 0):>12} months")
    
    print("\n" + "="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="💰 CFO Dashboard Agent - Financial Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard              Show financial overview
  %(prog)s add-revenue --source Etsy --amount 150 --recurring monthly
  %(prog)s add-expense --category marketing --amount 50 --description "Ad campaign"
  %(prog)s set-kpis --mrr 500 --burn-rate 200
  %(prog)s report                 Generate full financial report
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard command
    subparsers.add_parser('dashboard', help='Show financial dashboard overview')
    
    # Add revenue command
    rev_parser = subparsers.add_parser('add-revenue', help='Add a revenue entry')
    rev_parser.add_argument('--source', required=True, help='Revenue source name')
    rev_parser.add_argument('--amount', required=True, help='Revenue amount')
    rev_parser.add_argument('--category', help='Revenue category')
    rev_parser.add_argument('--recurring', default='no', choices=['yes', 'no'], 
                           help='Is this recurring revenue?')
    
    # Add expense command
    exp_parser = subparsers.add_parser('add-expense', help='Add an expense entry')
    exp_parser.add_argument('--amount', required=True, help='Expense amount')
    exp_parser.add_argument('--description', required=True, help='Expense description')
    exp_parser.add_argument('--category', help='Expense category')
    
    # Set KPIs command
    kpi_parser = subparsers.add_parser('set-kpis', help='Set KPI values')
    kpi_parser.add_argument('--mrr', help='Monthly Recurring Revenue')
    kpi_parser.add_argument('--gross-margin', help='Gross margin percentage')
    kpi_parser.add_argument('--net-margin', help='Net margin percentage')
    kpi_parser.add_argument('--burn-rate', help='Monthly burn rate')
    
    # Report command
    subparsers.add_parser('report', help='Generate full financial report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'dashboard': cmd_dashboard,
        'add-revenue': cmd_add_revenue,
        'add-expense': cmd_add_expense,
        'set-kpis': cmd_set_kpis,
        'report': cmd_report
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
