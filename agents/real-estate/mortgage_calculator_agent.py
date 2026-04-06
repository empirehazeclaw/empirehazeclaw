#!/usr/bin/env python3
"""
Mortgage Calculator Agent
Calculates mortgage payments, total interest, amortization schedules.
Stores calculation history in JSON.
"""

import argparse
import json
import logging
import math
import sys
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "mortgage_calculator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MortgageCalculatorAgent")

HISTORY_FILE = Path("/home/clawbot/.openclaw/workspace/data/mortgage_history.json")
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {"calculations": [], "last_id": 0}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def calculate_monthly_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment using standard formula."""
    if annual_rate == 0:
        return principal / (years * 12)
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    return payment

def calculate_mortgage(principal, annual_rate, years, property_tax=0, insurance=0, pmi=0):
    """Calculate complete mortgage details."""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if annual_rate == 0:
        principal_payment = principal / num_payments
    else:
        monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
        principal_payment = monthly_payment
    
    monthly_pi = calculate_monthly_payment(principal, annual_rate, years)
    total_monthly = monthly_pi + (property_tax / 12) + insurance + pmi
    
    total_interest = (monthly_pi * num_payments) - principal
    total_cost = (monthly_pi * num_payments) + (property_tax / 12 * num_payments) + (insurance * num_payments)
    
    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "years": years,
        "monthly_pi": round(monthly_pi, 2),
        "monthly_tax": round(property_tax / 12, 2),
        "monthly_insurance": round(insurance, 2),
        "monthly_pmi": round(pmi, 2),
        "total_monthly": round(total_monthly, 2),
        "total_interest": round(total_interest, 2),
        "total_cost": round(total_cost, 2),
        "loan_amount": principal
    }

def generate_amortization(principal, annual_rate, years):
    """Generate amortization schedule."""
    schedule = []
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    monthly_payment = calculate_monthly_payment(principal, annual_rate, years)
    
    balance = principal
    for month in range(1, num_payments + 1):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        balance -= principal_payment
        
        if month <= 12 or month == num_payments or month % 60 == 0:
            schedule.append({
                "month": month,
                "payment": round(monthly_payment, 2),
                "principal": round(principal_payment, 2),
                "interest": round(interest_payment, 2),
                "balance": round(max(balance, 0), 2)
            })
    
    return schedule

def print_calculation(result):
    """Print mortgage calculation results."""
    print(f"\n🏦 Mortgage Calculation Results")
    print(f"  Principal:              ${result['principal']:,.2f}")
    print(f"  Interest Rate:           {result['annual_rate']}%")
    print(f"  Loan Term:               {result['years']} years")
    print(f"  ─────────────────────────────────")
    print(f"  Monthly P&I:             ${result['monthly_pi']:,.2f}")
    print(f"  Monthly Tax:             ${result['monthly_tax']:,.2f}")
    print(f"  Monthly Insurance:       ${result['monthly_insurance']:,.2f}")
    print(f"  Monthly PMI:             ${result['monthly_pmi']:,.2f}")
    print(f"  ─────────────────────────────────")
    print(f"  TOTAL Monthly Payment:   ${result['total_monthly']:,.2f}")
    print(f"  ─────────────────────────────────")
    print(f"  Total Interest Paid:     ${result['total_interest']:,.2f}")
    print(f"  Total Loan Cost:         ${result['total_cost']:,.2f}")

def compare_rates(principal, years, rates):
    """Compare different interest rates."""
    print(f"\n📊 Rate Comparison for ${principal:,.0f} over {years} years\n")
    print(f"  {'Rate':<10} {'Monthly':<15} {'Total Interest':<18} {'Total Cost':<18}")
    print(f"  {'-'*10} {'-'*15} {'-'*18} {'-'*18}")
    
    for rate in rates:
        result = calculate_mortgage(principal, rate, years)
        print(f"  {rate:<10.2f}% ${result['monthly_pi']:>12,.2f} ${result['total_interest']:>15,.2f} ${result['total_cost']:>15,.2f}")

def affordability(monthly_budget, annual_rate, years, down_percent=20):
    """Calculate how much house you can afford."""
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    # Reverse calculate max loan from monthly payment
    if annual_rate == 0:
        max_loan = monthly_budget * num_payments
    else:
        max_loan = monthly_budget * ((1 + monthly_rate)**num_payments - 1) / (monthly_rate * (1 + monthly_rate)**num_payments)
    
    home_price = max_loan / (1 - down_percent / 100)
    down_payment = home_price * (down_percent / 100)
    
    print(f"\n🏠 Affordability Analysis")
    print(f"  Monthly Budget:          ${monthly_budget:,.2f}")
    print(f"  Down Payment:            {down_percent}%")
    print(f"  Interest Rate:           {annual_rate}%")
    print(f"  Loan Term:               {years} years")
    print(f"  ─────────────────────────────────")
    print(f"  Max Home Price:          ${home_price:,.2f}")
    print(f"  Max Loan Amount:         ${max_loan:,.2f}")
    print(f"  Down Payment Amount:     ${down_payment:,.2f}")
    
    return {"home_price": home_price, "loan_amount": max_loan, "down_payment": down_payment}

def main():
    parser = argparse.ArgumentParser(
        description="Mortgage Calculator Agent - Calculate mortgage payments and schedules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s calc --principal 350000 --rate 6.5 --years 30
  %(prog)s calc --principal 350000 --rate 6.5 --years 30 --property-tax 3000 --insurance 1500
  %(prog)s compare --principal 350000 --years 30 --rates 5.0,5.5,6.0,6.5,7.0
  %(prog)s afford --monthly 2000 --rate 6.5 --years 30 --down 20
  %(prog)s schedule --principal 350000 --rate 6.5 --years 30
  %(prog)s history
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Calculate
    p_calc = subparsers.add_parser("calc", help="Calculate mortgage payment")
    p_calc.add_argument("--principal", "--p", required=True, type=float, help="Loan principal amount")
    p_calc.add_argument("--rate", "--r", required=True, type=float, help="Annual interest rate (%%)")
    p_calc.add_argument("--years", "--y", required=True, type=int, help="Loan term in years")
    p_calc.add_argument("--property-tax", type=float, default=0, help="Annual property tax")
    p_calc.add_argument("--insurance", type=float, default=0, help="Annual insurance cost")
    p_calc.add_argument("--pmi", type=float, default=0, help="Monthly PMI")
    p_calc.add_argument("--save", action="store_true", help="Save to history")
    
    # Compare
    p_compare = subparsers.add_parser("compare", help="Compare different interest rates")
    p_compare.add_argument("--principal", "--p", required=True, type=float, help="Loan principal")
    p_compare.add_argument("--years", "--y", required=True, type=int, help="Loan term")
    p_compare.add_argument("--rates", required=True, help="Comma-separated rates (e.g., 5.0,6.0,7.0)")
    
    # Affordability
    p_afford = subparsers.add_parser("afford", help="Calculate affordability")
    p_afford.add_argument("--monthly", required=True, type=float, help="Monthly budget for housing")
    p_afford.add_argument("--rate", "--r", required=True, type=float, help="Expected interest rate")
    p_afford.add_argument("--years", "--y", required=True, type=int, help="Loan term")
    p_afford.add_argument("--down", type=float, default=20, help="Down payment percentage")
    
    # Amortization Schedule
    p_schedule = subparsers.add_parser("schedule", help="Generate amortization schedule")
    p_schedule.add_argument("--principal", "--p", required=True, type=float, help="Loan principal")
    p_schedule.add_argument("--rate", "--r", required=True, type=float, help="Annual rate")
    p_schedule.add_argument("--years", "--y", required=True, type=int, help="Loan term")
    p_schedule.add_argument("--years-display", type=int, default=5, help="Years of schedule to show")
    
    # History
    subparsers.add_parser("history", help="View calculation history")
    subparsers.add_parser("clear", help="Clear calculation history")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "calc":
            result = calculate_mortgage(
                args.principal, args.rate, args.years,
                args.property_tax, args.insurance, args.pmi
            )
            print_calculation(result)
            logger.info(f"Calculated mortgage: ${args.principal} at {args.rate}% for {args.years}yrs")
            
            if args.save:
                data = load_history()
                data["last_id"] += 1
                calc_record = {
                    "id": data["last_id"],
                    "timestamp": datetime.now().isoformat(),
                    **result
                }
                data["calculations"].append(calc_record)
                save_history(data)
                print(f"\n💾 Saved to history as calculation #{calc_record['id']}")
        
        elif args.command == "compare":
            rates = [float(r.strip()) for r in args.rates.split(",")]
            compare_rates(args.principal, args.years, rates)
        
        elif args.command == "afford":
            affordability(args.monthly, args.rate, args.years, args.down)
        
        elif args.command == "schedule":
            schedule = generate_amortization(args.principal, args.rate, args.years)
            print(f"\n📅 Amortization Schedule (${args.principal:,.0f} at {args.rate}% for {args.years} years)\n")
            print(f"  {'Month':<8} {'Payment':<12} {'Principal':<12} {'Interest':<12} {'Balance':<15}")
            print(f"  {'-'*8} {'-'*12} {'-'*12} {'-'*12} {'-'*15}")
            for row in schedule[:args.years_display * 12]:
                print(f"  {row['month']:<8} ${row['payment']:<11,.2f} ${row['principal']:<11,.2f} ${row['interest']:<11,.2f} ${row['balance']:<14,.2f}")
            if len(schedule) > args.years_display * 12:
                print(f"  ... ({len(schedule) - args.years_display * 12} more rows)")
                last = schedule[-1]
                print(f"  {last['month']:<8} ${last['payment']:<11,.2f} ${last['principal']:<11,.2f} ${last['interest']:<11,.2f} ${last['balance']:<14,.2f}")
        
        elif args.command == "history":
            data = load_history()
            if not data["calculations"]:
                print("No calculation history.")
            else:
                print(f"\n📜 Calculation History ({len(data['calculations'])} records)\n")
                for calc in data["calculations"][-10:]:
                    print(f"  [{calc['id']}] {calc['timestamp'][:10]} | ${calc['principal']:,.0f} @ {calc['annual_rate']}% | Monthly: ${calc['monthly_pi']:,.2f}")
        
        elif args.command == "clear":
            save_history({"calculations": [], "last_id": 0})
            print("✅ History cleared.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
