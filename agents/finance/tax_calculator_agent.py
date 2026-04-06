#!/usr/bin/env python3
"""
Tax Calculator Agent
Calculates taxes based on income, expenses, and tax rules.
Supports German tax calculation (EÜR, VAT).
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_DIR = SCRIPT_DIR.parent.parent.parent
DATA_DIR = WORKSPACE_DIR / "data" / "finance"
LOG_DIR = WORKSPACE_DIR / "logs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

TAX_RECORDS_FILE = DATA_DIR / "tax_records.json"
CONFIG_FILE = DATA_DIR / "tax_config.json"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "tax_calculator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TaxCalculator")


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


def load_records():
    """Load tax records from file."""
    return load_json(TAX_RECORDS_FILE, {"records": [], "yearly_data": {}})


def load_config():
    """Load tax configuration."""
    default_config = {
        "vat_rate": 19.0,
        "small_business_threshold": 22500,
        "tax_config": {
            "de": {
                "basic_allowance": 11604,
                "bracket1_limit": 17005,
                "standard_rate": 42,
                "top_rate_threshold": 66760,
                "soli_rate": 5.5
            }
        }
    }
    return load_json(CONFIG_FILE, default_config)


def save_records(data):
    """Save tax records to file."""
    return save_json(TAX_RECORDS_FILE, data)


def save_config(config):
    """Save tax configuration."""
    return save_json(CONFIG_FILE, config)


def calculate_german_income_tax(taxable_income, year=2026):
    """Calculate German income tax (Einkommensteuer) 2026.
    
    Uses official formula:
    Zone 1 (11,604 - 17,005): tax = (922.98*y + 1400)*y/10000 where y = taxable - 11604
    Zone 2 (17,005 - 66,760): tax = 1025.38 + (181.19*z + 2397)*z/10000 where z = taxable - 17005
    Zone 3 (>66,760): 0.42*(taxable-66760) + 16899.99
    
    Reference values:
    - 17,005 EUR taxable → ~2,694 EUR tax
    - 30,000 EUR taxable → ~5,200 EUR tax  
    - 66,760 EUR taxable → ~16,900 EUR tax
    """
    if taxable_income <= 0:
        return {"income_tax": 0, "soli": 0, "total": 0}
    
    taxable = float(taxable_income)
    
    if taxable <= 11604:
        income_tax = 0.0
    elif taxable <= 17005:
        # Zone 1: y = (taxable - 11604) / 10000
        # tax = (922.98 * y + 1400) * y
        y = (taxable - 11604) / 10000.0
        income_tax = (922.98 * y + 1400.0) * y
    elif taxable <= 66760:
        # Zone 2: z = (taxable - 17005) / 10000
        # tax = 1025.38 + (181.19 * z + 2397) * z
        z = (taxable - 17005) / 10000.0
        income_tax = 1025.38 + (181.19 * z + 2397.0) * z
    else:
        income_tax = 0.42 * (taxable - 66760.0) + 16899.99
    
    income_tax = max(0, income_tax)
    
    # Solidaritätszuschlag (Soli)
    if income_tax > 18130:
        soli = income_tax * 0.055
    elif income_tax > 17543:
        soli = (income_tax - 17543) * 0.119
    else:
        soli = 0
    
    return {
        "income_tax": round(income_tax, 2),
        "soli": round(soli, 2),
        "total": round(income_tax + soli, 2)
    }


def calculate_vat(amount, is_net=True, rate=19.0, small_business=False):
    """Calculate VAT. If is_net=True, amount is net and returns gross. Else amount is gross."""
    if small_business:
        return {"vat": 0, "gross": amount if is_net else amount, "net": amount if is_net else amount, "rate": 0}
    
    if is_net:
        vat = amount * rate / 100
        gross = amount + vat
        return {"vat": round(vat, 2), "gross": round(gross, 2), "net": round(amount, 2), "rate": rate}
    else:
        vat = amount * rate / (100 + rate)
        net = amount - vat
        return {"vat": round(vat, 2), "gross": round(amount, 2), "net": round(net, 2), "rate": rate}


def add_tax_record(year, quarter, income, expenses, tax_type="quarterly"):
    """Add a tax record."""
    logger.info(f"Adding tax record for {year} Q{quarter}")
    records_data = load_records()
    
    year_key = str(year)
    if year_key not in records_data.get("yearly_data", {}):
        records_data.setdefault("yearly_data", {})[year_key] = {"quarters": {}, "annual": None}
    
    quarter_key = f"q{quarter}"
    taxable_income = max(0, income - expenses)
    income_tax = calculate_german_income_tax(taxable_income, year)
    
    record = {
        "id": f"{year_key}-{quarter_key}",
        "year": year,
        "quarter": quarter,
        "income": float(income),
        "expenses": float(expenses),
        "taxable_income": taxable_income,
        "tax_type": tax_type,
        "income_tax": income_tax["income_tax"],
        "soli": income_tax["soli"],
        "total_tax": income_tax["total"],
        "created_at": datetime.now().isoformat()
    }
    
    records_data["yearly_data"][year_key]["quarters"][quarter_key] = record
    
    if save_records(records_data):
        logger.info(f"Tax record added: {year} Q{quarter}")
        return record
    else:
        logger.error("Failed to save tax record")
        return None


def get_tax_records(year):
    """Get all tax records for a year."""
    records_data = load_records()
    year_data = records_data.get("yearly_data", {}).get(str(year), {})
    return year_data.get("quarters", {})


def calculate_annual_summary(year):
    """Calculate annual tax summary."""
    records = get_tax_records(year)
    total_income = 0.0
    total_expenses = 0.0
    total_tax = 0.0
    
    for q, record in records.items():
        total_income += record.get("income", 0)
        total_expenses += record.get("expenses", 0)
        total_tax += record.get("total_tax", 0)
    
    taxable_income = max(0, total_income - total_expenses)
    annual_tax = calculate_german_income_tax(taxable_income, year)
    difference = total_tax - annual_tax["total"]
    
    return {
        "year": year,
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "taxable_income": round(taxable_income, 2),
        "total_quarterly_tax": round(total_tax, 2),
        "annual_tax": annual_tax["total"],
        "annual_income_tax": annual_tax["income_tax"],
        "annual_soli": annual_tax["soli"],
        "difference": round(difference, 2),
        "quarters": list(records.keys())
    }


def estimate_monthly_tax(monthly_income, monthly_expenses):
    """Estimate monthly tax liability."""
    annual_income = monthly_income * 12
    annual_expenses = monthly_expenses * 12
    taxable = max(0, annual_income - annual_expenses)
    tax = calculate_german_income_tax(taxable)
    
    return {
        "monthly_gross": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_taxable": monthly_income - monthly_expenses,
        "estimated_monthly_tax": round(tax["total"] / 12, 2),
        "annual_summary": {
            "income": annual_income,
            "expenses": annual_expenses,
            "taxable": taxable,
            "income_tax": tax["income_tax"],
            "soli": tax["soli"],
            "total_tax": tax["total"]
        }
    }


def cmd_add(args):
    """Handle add command."""
    record = add_tax_record(args.year, args.quarter, args.income, args.expenses, args.type)
    if record:
        print(f"✅ Tax record added for {args.year} Q{args.quarter}")
        print(f"\n📊 Record Details:")
        print(f"   Income:        {record['income']:.2f} EUR")
        print(f"   Expenses:      {record['expenses']:.2f} EUR")
        print(f"   Taxable Income:{record['taxable_income']:.2f} EUR")
        print(f"   Income Tax:    {record['income_tax']:.2f} EUR")
        print(f"   Soli:          {record['soli']:.2f} EUR")
        print(f"   TOTAL TAX:     {record['total_tax']:.2f} EUR")
    else:
        print("❌ Failed to add tax record")
        sys.exit(1)


def cmd_calculate(args):
    """Handle calculate command."""
    taxable = max(0, args.income - args.expenses)
    tax = calculate_german_income_tax(taxable, args.year)
    print(f"\n📊 Tax Calculation for {args.year}")
    print(f"{'='*50}")
    print(f"   Income:        {args.income:.2f} EUR")
    print(f"   Expenses:      {args.expenses:.2f} EUR")
    print(f"   Taxable Income:{taxable:.2f} EUR")
    print(f"\n   Income Tax:    {tax['income_tax']:.2f} EUR")
    print(f"   Soli:          {tax['soli']:.2f} EUR")
    print(f"   {'-'*30}")
    print(f"   TOTAL TAX:     {tax['total']:.2f} EUR")
    print(f"\n   Effective Rate: {(tax['total'] / taxable * 100) if taxable > 0 else 0:.1f}%")


def cmd_vat(args):
    """Handle VAT calculation."""
    rate = args.rate or 19.0
    if args.net is not None:
        result = calculate_vat(args.net, is_net=True, rate=rate, small_business=args.small_business)
        print(f"\n💰 VAT Calculation (Rate: {rate}%)")
        print(f"{'='*50}")
        print(f"   Net Amount:    {result['net']:.2f} EUR")
        print(f"   VAT ({rate}%):    {result['vat']:.2f} EUR")
        print(f"   Gross Amount:  {result['gross']:.2f} EUR")
    elif args.gross is not None:
        result = calculate_vat(args.gross, is_net=False, rate=rate, small_business=args.small_business)
        print(f"\n💰 VAT Calculation")
        print(f"{'='*50}")
        print(f"   Gross Amount:  {result['gross']:.2f} EUR")
        print(f"   VAT Rate:      {result['rate']}%")
        print(f"   Net Amount:    {result['net']:.2f} EUR")
        print(f"   VAT:           {result['vat']:.2f} EUR")
    else:
        print("❌ Specify --net or --gross")
        sys.exit(1)


def cmd_summary(args):
    """Handle summary command."""
    summary = calculate_annual_summary(args.year)
    if not summary["quarters"]:
        print(f"No tax records found for {args.year}")
        return
    print(f"\n📊 Annual Tax Summary {args.year}")
    print(f"{'='*50}")
    print(f"   Total Income:        {summary['total_income']:.2f} EUR")
    print(f"   Total Expenses:      {summary['total_expenses']:.2f} EUR")
    print(f"   Taxable Income:     {summary['taxable_income']:.2f} EUR")
    print(f"\n   Quarterly Taxes Paid:{summary['total_quarterly_tax']:.2f} EUR")
    print(f"   Annual Tax Est.:     {summary['annual_tax']:.2f} EUR")
    print(f"     - Income Tax:     {summary['annual_income_tax']:.2f} EUR")
    print(f"     - Soli:           {summary['annual_soli']:.2f} EUR")
    if summary["difference"] > 0:
        print(f"\n   ⚠️  Additional due: {summary['difference']:.2f} EUR")
    elif summary["difference"] < 0:
        print(f"\n   ✅ Potential refund: {-summary['difference']:.2f} EUR")
    print(f"\n   Quarters: {', '.join(summary['quarters'])}")


def cmd_estimate(args):
    """Handle estimate command."""
    result = estimate_monthly_tax(args.income, args.expenses)
    print(f"\n📊 Monthly Tax Estimate")
    print(f"{'='*50}")
    print(f"   Monthly Income:    {result['monthly_gross']:.2f} EUR")
    print(f"   Monthly Expenses:  {result['monthly_expenses']:.2f} EUR")
    print(f"   Monthly Taxable:  {result['monthly_taxable']:.2f} EUR")
    print(f"\n   Estimated Monthly Tax: {result['estimated_monthly_tax']:.2f} EUR")
    ann = result["annual_summary"]
    print(f"\n📊 Annual Projection:")
    print(f"   Annual Income:     {ann['income']:.2f} EUR")
    print(f"   Annual Expenses:   {ann['expenses']:.2f} EUR")
    print(f"   Annual Taxable:   {ann['taxable']:.2f} EUR")
    print(f"   Annual Income Tax: {ann['income_tax']:.2f} EUR")
    print(f"   Annual Soli:       {ann['soli']:.2f} EUR")
    print(f"   TOTAL ANNUAL TAX:  {ann['total_tax']:.2f} EUR")


def main():
    parser = argparse.ArgumentParser(description="Tax Calculator Agent - Calculate taxes (German EÜR/VAT)")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    add_parser = subparsers.add_parser("add", help="Add quarterly tax record")
    add_parser.add_argument("--year", required=True, type=int, help="Year")
    add_parser.add_argument("--quarter", required=True, type=int, choices=[1,2,3,4], help="Quarter")
    add_parser.add_argument("--income", required=True, type=float, help="Total income")
    add_parser.add_argument("--expenses", required=True, type=float, help="Total expenses")
    add_parser.add_argument("--type", default="quarterly", help="Tax type")
    
    calc_parser = subparsers.add_parser("calculate", help="Calculate tax on income/expenses")
    calc_parser.add_argument("--income", required=True, type=float, help="Income")
    calc_parser.add_argument("--expenses", required=True, type=float, help="Expenses")
    calc_parser.add_argument("--year", default=datetime.now().year, type=int, help="Year")
    
    vat_parser = subparsers.add_parser("vat", help="Calculate VAT")
    vat_parser.add_argument("--net", type=float, help="Net amount")
    vat_parser.add_argument("--gross", type=float, help="Gross amount")
    vat_parser.add_argument("--rate", type=float, help="VAT rate (default: 19)")
    vat_parser.add_argument("--small-business", action="store_true", help="Small business exemption")
    
    summary_parser = subparsers.add_parser("summary", help="Show annual summary")
    summary_parser.add_argument("--year", default=datetime.now().year, type=int, help="Year")
    
    est_parser = subparsers.add_parser("estimate", help="Estimate monthly tax")
    est_parser.add_argument("--income", required=True, type=float, help="Monthly income")
    est_parser.add_argument("--expenses", required=True, type=float, help="Monthly expenses")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {"add": cmd_add, "calculate": cmd_calculate, "vat": cmd_vat, "summary": cmd_summary, "estimate": cmd_estimate}
    try:
        commands[args.command](args)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
