#!/usr/bin/env python3
"""
Property Analyzer Agent
Analyzes real estate properties for investment potential, valuations, and comparisons.
"""

import argparse
import json
import logging
import math
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/real-estate")
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "property_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PROPERTIES_FILE = DATA_DIR / "properties.json"
ANALYSES_FILE = DATA_DIR / "analyses.json"
MARKET_FILE = DATA_DIR / "market_data.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except IOError as e:
        logger.error(f"Error saving {path}: {e}")
        return False


def generate_id(prefix: str = "id") -> str:
    return f"{prefix}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"


def parse_number(value: str) -> float:
    """Parse a number from string, handling currency and comma formats."""
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r'[€$£,\s]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format a number as currency."""
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def calculate_mortgage(principal: float, annual_rate: float, years: int) -> dict:
    """Calculate monthly mortgage payment."""
    if principal <= 0 or annual_rate <= 0 or years <= 0:
        return {"monthly_payment": 0, "total_interest": 0, "total_cost": 0}
    
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_cost = monthly_payment * num_payments
    total_interest = total_cost - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_cost": round(total_cost, 2)
    }


def calculate_roi(purchase_price: float, rental_income: float, expenses: float, 
                  appreciation_rate: float = 3.0) -> dict:
    """Calculate ROI metrics for a property."""
    if purchase_price <= 0:
        return {"error": "Purchase price must be greater than 0"}
    
    # Annual figures
    annual_rental = rental_income * 12
    annual_expenses = expenses * 12
    annual_net_income = annual_rental - annual_expenses
    
    # Cash on cash return
    # Assuming 20% down payment, 5% closing costs
    down_payment = purchase_price * 0.20
    closing_costs = purchase_price * 0.05
    total_cash_invested = down_payment + closing_costs
    
    cash_on_cash = (annual_net_income / total_cash_invested * 100) if total_cash_invested > 0 else 0
    
    # Cap rate (NOI / Purchase Price)
    cap_rate = (annual_net_income / purchase_price * 100) if purchase_price > 0 else 0
    
    # Gross rent multiplier
    grm = purchase_price / annual_rental if annual_rental > 0 else 0
    
    # 5-year projection
    future_value = purchase_price * (1 + appreciation_rate / 100) ** 5
    equity_gain = future_value - purchase_price
    total_cash_flow_5yr = annual_net_income * 5
    total_roi_5yr = ((equity_gain + total_cash_flow_5yr) / total_cash_invested * 100) if total_cash_invested > 0 else 0
    
    # Break-even ratio
    break_even_ratio = ((annual_expenses + annual_rental * 0.5) / annual_rental * 100) if annual_rental > 0 else 0
    
    # Debt coverage ratio (assuming 70% LTV mortgage)
    loan_amount = purchase_price * 0.80
    mortgage = calculate_mortgage(loan_amount, 6.5, 30)
    annual_debt_service = mortgage["monthly_payment"] * 12
    dcr = annual_net_income / annual_debt_service if annual_debt_service > 0 else 0
    
    return {
        "annual_rental_income": round(annual_rental, 2),
        "annual_expenses": round(annual_expenses, 2),
        "annual_net_operating_income": round(annual_net_income, 2),
        "cash_on_cash_return": round(cash_on_cash, 2),
        "cap_rate": round(cap_rate, 2),
        "gross_rent_multiplier": round(grm, 2),
        "break_even_ratio": round(break_even_ratio, 2),
        "debt_coverage_ratio": round(dcr, 2),
        "projection_5yr": {
            "future_value": round(future_value, 2),
            "equity_gain": round(equity_gain, 2),
            "cash_flow": round(total_cash_flow_5yr, 2),
            "total_roi": round(total_roi_5yr, 2)
        }
    }


def estimate_property_value(area: float, price_per_sqm: float, condition: str = "average") -> float:
    """Estimate property value based on area and market rates."""
    base_value = area * price_per_sqm
    
    condition_factors = {
        "poor": 0.70,
        "fair": 0.85,
        "average": 1.00,
        "good": 1.15,
        "excellent": 1.30
    }
    
    factor = condition_factors.get(condition.lower(), 1.0)
    return base_value * factor


def analyze_property(property_data: dict) -> dict:
    """Perform comprehensive property analysis."""
    analysis_id = generate_id("analysis")
    
    # Extract property details
    price = parse_number(property_data.get("price", 0))
    rental_monthly = parse_number(property_data.get("rental_income_monthly", 0))
    area = property_data.get("area_sqm", 0)
    property_type = property_data.get("type", "unknown")
    condition = property_data.get("condition", "average")
    location = property_data.get("location", "")
    year_built = property_data.get("year_built", 2000)
    currency = property_data.get("currency", "EUR")
    
    # Expenses breakdown
    property_tax = parse_number(property_data.get("property_tax_annual", 0))
    insurance = parse_number(property_data.get("insurance_annual", 0))
    maintenance = parse_number(property_data.get("maintenance_annual", price * 0.01))  # 1% of value default
    management_fee = parse_number(property_data.get("management_fee_monthly", 0))
    hoa = parse_number(property_data.get("hoa_monthly", 0))
    utilities = parse_number(property_data.get("utilities_monthly", 0))
    other_expenses = parse_number(property_data.get("other_expenses_monthly", 0))
    
    # Calculate total monthly expenses
    monthly_expenses = (
        property_tax / 12 + 
        insurance / 12 + 
        maintenance / 12 + 
        management_fee + 
        hoa + 
        utilities + 
        other_expenses
    )
    
    # Calculate mortgage if financing
    down_payment_percent = property_data.get("down_payment_percent", 20)
    loan_rate = property_data.get("loan_rate", 6.5)
    loan_years = property_data.get("loan_years", 30)
    
    down_payment = price * (down_payment_percent / 100)
    loan_amount = price - down_payment
    mortgage = calculate_mortgage(loan_amount, loan_rate, loan_years)
    
    # Calculate ROI
    roi = calculate_roi(
        purchase_price=price,
        rental_income=rental_monthly,
        expenses=monthly_expenses,
        appreciation_rate=property_data.get("appreciation_rate", 3.0)
    )
    
    # Get market rate estimate
    market_rate = property_data.get("market_rate_per_sqm", 3000)
    estimated_value = estimate_property_value(area, market_rate, condition)
    price_per_sqm = price / area if area > 0 else 0
    value_vs_estimate = ((price - estimated_value) / estimated_value * 100) if estimated_value > 0 else 0
    
    # Calculate property age
    current_year = datetime.utcnow().year
    property_age = current_year - year_built if year_built else 0
    
    # Investment score
    score = 0
    if roi.get("cash_on_cash_return", 0) >= 8:
        score += 30
    elif roi.get("cash_on_cash_return", 0) >= 5:
        score += 20
    elif roi.get("cash_on_cash_return", 0) >= 0:
        score += 10
    
    if roi.get("cap_rate", 0) >= 6:
        score += 25
    elif roi.get("cap_rate", 0) >= 4:
        score += 15
    elif roi.get("cap_rate", 0) >= 0:
        score += 5
    
    if dcr >= 1.25:
        score += 20
    elif dcr >= 1.0:
        score += 10
    
    if value_vs_estimate <= -10:  # Undervalued
        score += 15
    elif value_vs_estimate <= 10:
        score += 5
    
    if property_age <= 10:
        score += 10
    elif property_age <= 30:
        score += 5
    
    investment_rating = "A" if score >= 70 else "B" if score >= 50 else "C" if score >= 30 else "D"
    
    analysis = {
        "id": analysis_id,
        "property_id": property_data.get("id"),
        "property_address": property_data.get("address", ""),
        "analyzed_at": datetime.utcnow().isoformat(),
        "price": price,
        "area_sqm": area,
        "price_per_sqm": round(price_per_sqm, 2),
        "estimated_value": round(estimated_value, 2),
        "value_vs_market": round(value_vs_estimate, 2),
        
        "financing": {
            "down_payment_percent": down_payment_percent,
            "down_payment": round(down_payment, 2),
            "loan_amount": round(loan_amount, 2),
            "loan_rate": loan_rate,
            "loan_years": loan_years,
            "monthly_mortgage": mortgage["monthly_payment"],
            "total_interest": mortgage["total_interest"]
        },
        
        "income": {
            "monthly_rental": rental_monthly,
            "annual_rental": roi.get("annual_rental_income", 0)
        },
        
        "expenses": {
            "monthly_total": round(monthly_expenses, 2),
            "annual_total": round(monthly_expenses * 12, 2),
            "breakdown": {
                "property_tax_annual": property_tax,
                "insurance_annual": insurance,
                "maintenance_annual": maintenance,
                "management_monthly": management_fee,
                "hoa_monthly": hoa,
                "utilities_monthly": utilities,
                "other_monthly": other_expenses
            }
        },
        
        "roi_metrics": roi,
        
        "investment_score": score,
        "investment_rating": investment_rating,
        
        "property_age": property_age,
        "condition": condition,
        "property_type": property_type,
        "location": location,
        "currency": currency,
        
        "recommendation": generate_recommendation(score, roi, value_vs_estimate)
    }
    
    logger.info(f"Property analyzed: {analysis_id}")
    return analysis


def generate_recommendation(score: int, roi: dict, value_diff: float) -> str:
    """Generate investment recommendation."""
    recommendations = []
    
    if score >= 70:
        recommendations.append("STRONG BUY - Excellent investment metrics")
    elif score >= 50:
        recommendations.append("BUY - Good investment potential")
    elif score >= 30:
        recommendations.append("HOLD - Consider if price is negotiable")
    else:
        recommendations.append("AVOID - Weak investment metrics")
    
    if value_diff < -15:
        recommendations.append("Property appears significantly undervalued")
    elif value_diff > 15:
        recommendations.append("Property appears overpriced vs market")
    
    if roi.get("cash_on_cash_return", 0) < 0:
        recommendations.append("Warning: Negative cash flow")
    
    if roi.get("debt_coverage_ratio", 0) < 1.0:
        recommendations.append("Warning: Debt coverage below 1.0 - risky financing")
    
    return " | ".join(recommendations)


def add_property(property_data: dict) -> dict:
    """Add a property to the database."""
    property_id = generate_id("prop")
    property_data["id"] = property_id
    property_data["created_at"] = datetime.utcnow().isoformat()
    property_data["updated_at"] = datetime.utcnow().isoformat()
    
    properties = load_json(PROPERTIES_FILE, {"properties": []})
    properties["properties"].append(property_data)
    save_json(PROPERTIES_FILE, properties)
    
    logger.info(f"Property added: {property_id}")
    return property_data


def update_market_data(location: str, price_per_sqm: float, avg_rent_per_sqm: float,
                       avg_cap_rate: float, trend: str = "stable") -> bool:
    """Update market data for a location."""
    market = load_json(MARKET_FILE, {"market_data": []})
    
    # Update or add location
    found = False
    for m in market["market_data"]:
        if m.get("location", "").lower() == location.lower():
            m["price_per_sqm"] = price_per_sqm
            m["avg_rent_per_sqm"] = avg_rent_per_sqm
            m["avg_cap_rate"] = avg_cap_rate
            m["trend"] = trend
            m["updated_at"] = datetime.utcnow().isoformat()
            found = True
            break
    
    if not found:
        market["market_data"].append({
            "location": location,
            "price_per_sqm": price_per_sqm,
            "avg_rent_per_sqm": avg_rent_per_sqm,
            "avg_cap_rate": avg_cap_rate,
            "trend": trend,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    return save_json(MARKET_FILE, market)


def get_properties(filters: dict = None) -> list[dict]:
    """Get properties with optional filters."""
    properties = load_json(PROPERTIES_FILE, {"properties": []}).get("properties", [])
    
    if filters:
        if "type" in filters:
            properties = [p for p in properties if p.get("type") == filters["type"]]
        if "min_price" in filters:
            properties = [p for p in properties if parse_number(p.get("price", 0)) >= filters["min_price"]]
        if "max_price" in filters:
            properties = [p for p in properties if parse_number(p.get("price", 0)) <= filters["max_price"]]
        if "location" in filters:
            properties = [p for p in properties if filters["location"].lower() in p.get("location", "").lower()]
    
    return sorted(properties, key=lambda x: x.get("created_at", ""), reverse=True)


def cmd_add_property(args):
    """Add a property interactively."""
    print("\n--- Add Property ---")
    
    prop = {}
    prop["address"] = input("Property Address: ").strip()
    if not prop["address"]:
        print("Address is required")
        return
    
    prop["type"] = input("Type (apartment/house/condo/commercial/land): ").strip() or "apartment"
    prop["location"] = input("City/Location: ").strip()
    
    price = input("Price: ").strip()
    prop["price"] = parse_number(price)
    
    area = input("Area (sqm): ").strip()
    prop["area_sqm"] = float(area) if area else 0
    
    year_built = input("Year Built: ").strip()
    prop["year_built"] = int(year_built) if year_built else 2000
    
    prop["condition"] = input("Condition (poor/fair/average/good/excellent): ").strip() or "average"
    
    rental = input("Monthly Rental Income: ").strip()
    prop["rental_income_monthly"] = parse_number(rental)
    
    # Expenses
    tax = input("Annual Property Tax: ").strip()
    prop["property_tax_annual"] = parse_number(tax)
    
    ins = input("Annual Insurance: ").strip()
    prop["insurance_annual"] = parse_number(ins)
    
    maint = input("Annual Maintenance (or % of price): ").strip()
    if maint.endswith("%"):
        prop["maintenance_annual"] = prop["price"] * float(maint[:-1]) / 100
    else:
        prop["maintenance_annual"] = parse_number(maint)
    
    mgt = input("Monthly Management Fee: ").strip()
    prop["management_fee_monthly"] = parse_number(mgt)
    
    prop["currency"] = input("Currency (EUR/USD/GBP): ").strip() or "EUR"
    
    result = add_property(prop)
    print(f"\n✅ Property added!")
    print(f"   ID: {result['id']}")
    print(f"   Address: {result['address']}")


def cmd_analyze(args):
    """Analyze a property."""
    properties = load_json(PROPERTIES_FILE, {"properties": []}).get("properties", [])
    prop = next((p for p in properties if p.get("id") == args.property_id), None)
    
    if not prop:
        print(f"Property not found: {args.property_id}")
        return
    
    analysis = analyze_property(prop)
    
    # Save analysis
    analyses = load_json(ANALYSES_FILE, {"analyses": []})
    analyses["analyses"].append(analysis)
    save_json(ANALYSES_FILE, analyses)
    
    print(f"\n{'='*70}")
    print(f"PROPERTY ANALYSIS: {prop.get('address', 'N/A')}")
    print(f"{'='*70}")
    
    print(f"\n📍 Property Details:")
    print(f"   Type: {analysis['property_type']} | Condition: {analysis['condition']}")
    print(f"   Area: {analysis['area_sqm']} sqm | Age: {analysis['property_age']} years")
    print(f"   Location: {analysis['location']}")
    
    print(f"\n💰 PRICE & VALUE:")
    print(f"   Asking Price: {format_currency(analysis['price'], analysis['currency'])}")
    print(f"   Price/sqm: {format_currency(analysis['price_per_sqm'], analysis['currency'])}")
    print(f"   Estimated Value: {format_currency(analysis['estimated_value'], analysis['currency'])}")
    print(f"   vs Market: {analysis['value_vs_market']:+.1f}%")
    
    print(f"\n🏦 FINANCING:")
    fin = analysis["financing"]
    print(f"   Down Payment ({fin['down_payment_percent']}%): {format_currency(fin['down_payment'], analysis['currency'])}")
    print(f"   Loan Amount: {format_currency(fin['loan_amount'], analysis['currency'])}")
    print(f"   Monthly Mortgage: {format_currency(fin['monthly_mortgage'], analysis['currency'])}")
    print(f"   Total Interest: {format_currency(fin['total_interest'], analysis['currency'])}")
    
    print(f"\n💵 INCOME:")
    inc = analysis["income"]
    print(f"   Monthly Rental: {format_currency(inc['monthly_rental'], analysis['currency'])}")
    print(f"   Annual Rental: {format_currency(inc['annual_rental'], analysis['currency'])}")
    
    print(f"\n📊 EXPENSES:")
    exp = analysis["expenses"]
    print(f"   Monthly: {format_currency(exp['monthly_total'], analysis['currency'])}")
    print(f"   Annual: {format_currency(exp['annual_total'], analysis['currency'])}")
    
    print(f"\n📈 ROI METRICS:")
    roi = analysis["roi_metrics"]
    print(f"   Cash-on-Cash Return: {roi.get('cash_on_cash_return', 0):.2f}%")
    print(f"   Cap Rate: {roi.get('cap_rate', 0):.2f}%")
    print(f"   Gross Rent Multiplier: {roi.get('gross_rent_multiplier', 0):.2f}")
    print(f"   Debt Coverage Ratio: {roi.get('debt_coverage_ratio', 0):.2f}")
    print(f"   Break-Even Ratio: {roi.get('break_even_ratio', 0):.1f}%")
    
    proj = roi.get("projection_5yr", {})
    print(f"\n📉 5-YEAR PROJECTION:")
    print(f"   Future Value: {format_currency(proj.get('future_value', 0), analysis['currency'])}")
    print(f"   Equity Gain: {format_currency(proj.get('equity_gain', 0), analysis['currency'])}")
    print(f"   Cash Flow: {format_currency(proj.get('cash_flow', 0), analysis['currency'])}")
    print(f"   Total ROI: {proj.get('total_roi', 0):.1f}%")
    
    print(f"\n🎯 INVESTMENT SCORE: {analysis['investment_score']}/100 ({analysis['investment_rating']})")
    print(f"   📋 {analysis['recommendation']}")


def cmd_list_properties(args):
    """List all properties."""
    properties = get_properties({
        "type": args.type,
        "min_price": parse_number(args.min_price) if args.min_price else None,
        "max_price": parse_number(args.max_price) if args.max_price else None,
        "location": args.location
    })
    
    if not properties:
        print("No properties found")
        return
    
    print(f"\n{'='*70}")
    print(f"PROPERTIES: {len(properties)}")
    print(f"{'='*70}\n")
    
    for p in properties:
        price = parse_number(p.get("price", 0))
        area = p.get("area_sqm", 0)
        price_per_sqm = price / area if area > 0 else 0
        currency = p.get("currency", "EUR")
        
        print(f"🏠 {p.get('address', 'N/A')}")
        print(f"   ID: {p.get('id')}")
        print(f"   Type: {p.get('type', 'N/A')} | {p.get('area_sqm', 0)} sqm")
        print(f"   Price: {format_currency(price, currency)} ({format_currency(price_per_sqm, currency)}/sqm)")
        print(f"   Location: {p.get('location', 'N/A')}")
        print(f"   Condition: {p.get('condition', 'N/A')}")
        if p.get("rental_income_monthly"):
            print(f"   Rental: {format_currency(p.get('rental_income_monthly'), currency)}/mo")
        print()


def cmd_compare(args):
    """Compare multiple properties."""
    properties = load_json(PROPERTIES_FILE, {"properties": []}).get("properties", [])
    selected = [p for p in properties if p.get("id") in args.property_ids]
    
    if len(selected) < 2:
        print("Need at least 2 properties to compare")
        return
    
    analyses = []
    for p in selected:
        analysis = analyze_property(p)
        analyses.append(analysis)
    
    print(f"\n{'='*70}")
    print(f"PROPERTY COMPARISON: {len(analyses)} Properties")
    print(f"{'='*70}\n")
    
    # Sort by score
    analyses.sort(key=lambda x: x["investment_score"], reverse=True)
    
    print(f"{'Metric':<25} " + " ".join(f"{'Property '+str(i+1):>15}" for i in range(len(analyses))))
    print("-" * 70)
    
    metrics = [
        ("Price", lambda a: format_currency(a["price"], a["currency"])),
        ("Area (sqm)", lambda a: str(a["area_sqm"])),
        ("Price/sqm", lambda a: format_currency(a["price_per_sqm"], a["currency"])),
        ("vs Market %", lambda a: f"{a['value_vs_market']:+.1f}%"),
        ("Cash-on-Cash %", lambda a: f"{a['roi_metrics'].get('cash_on_cash_return', 0):.2f}%"),
        ("Cap Rate %", lambda a: f"{a['roi_metrics'].get('cap_rate', 0):.2f}%"),
        ("Monthly Mortgage", lambda a: format_currency(a['financing']['monthly_mortgage'], a['currency'])),
        ("Monthly Cash Flow", lambda a: format_currency(a['income']['monthly_rental'] - a['expenses']['monthly_total'], a['currency'])),
        ("5yr Total ROI %", lambda a: f"{a['roi_metrics']['projection_5yr'].get('total_roi', 0):.1f}%"),
        ("Investment Score", lambda a: f"{a['investment_score']}/100"),
        ("Rating", lambda a: a['investment_rating']),
    ]
    
    for label, fn in metrics:
        row = f"{label:<25} "
        for a in analyses:
            row += f"{fn(a):>15} "
        print(row)
    
    print()
    print("🏆 RECOMMENDATION: Property with highest score is the best investment")


def cmd_market(args):
    """Update or view market data."""
    if args.location and args.price_per_sqm:
        update_market_data(
            location=args.location,
            price_per_sqm=float(args.price_per_sqm),
            avg_rent_per_sqm=float(args.rent_per_sqm or 15),
            avg_cap_rate=float(args.cap_rate or 5),
            trend=args.trend or "stable"
        )
        print(f"✅ Market data updated for: {args.location}")
        return
    
    # Show market data
    market = load_json(MARKET_FILE, {"market_data": []})
    data = market.get("market_data", [])
    
    if not data:
        print("No market data available. Add with --location and --price-per-sqm")
        return
    
    print(f"\n{'='*70}")
    print(f"MARKET DATA: {len(data)} locations")
    print(f"{'='*70}\n")
    
    for m in data:
        trend_icon = {"rising": "📈", "falling": "📉", "stable": "➡️"}.get(m.get("trend", "stable"), "➡️")
        print(f"{trend_icon} {m.get('location', 'N/A')}")
        print(f"   Price/sqm: €{m.get('price_per_sqm', 0):,.0f}")
        print(f"   Rent/sqm: €{m.get('avg_rent_per_sqm', 0):,.0f}/mo")
        print(f"   Avg Cap Rate: {m.get('avg_cap_rate', 0):.1f}%")
        print(f"   Trend: {m.get('trend', 'N/A')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Property Analyzer Agent - Analyze real estate investments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --add-property
  %(prog)s --list-properties
  %(prog)s --list-properties --location Berlin --max-price 500000
  %(prog)s --analyze --property-id prop_xxx
  %(prog)s --compare --property-ids prop_xxx prop_yyy prop_zzz
  %(prog)s --market --location Berlin --price-per-sqm 4500
  %(prog)s --market
        """
    )
    
    parser.add_argument("--add-property", action="store_true", help="Add a new property")
    
    parser.add_argument("--list-properties", action="store_true", help="List all properties")
    parser.add_argument("--type", type=str, choices=["apartment", "house", "condo", "commercial", "land"], help="Filter by type")
    parser.add_argument("--min-price", type=str, help="Minimum price")
    parser.add_argument("--max-price", type=str, help="Maximum price")
    parser.add_argument("--location", type=str, help="Location filter")
    
    parser.add_argument("--analyze", action="store_true", help="Analyze a property")
    parser.add_argument("--property-id", type=str, help="Property ID to analyze")
    
    parser.add_argument("--compare", action="store_true", help="Compare properties")
    parser.add_argument("--property-ids", type=str, nargs="+", help="Property IDs to compare")
    
    parser.add_argument("--market", action="store_true", help="View/update market data")
    parser.add_argument("--price-per-sqm", type=str, help="Price per sqm for market data")
    parser.add_argument("--rent-per-sqm", type=str, help="Rent per sqm for market data")
    parser.add_argument("--cap-rate", type=str, help="Average cap rate")
    parser.add_argument("--trend", type=str, choices=["rising", "falling", "stable"], help="Market trend")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.add_property:
        cmd_add_property(args)
    elif args.list_properties:
        cmd_list_properties(args)
    elif args.analyze:
        cmd_analyze(args)
    elif args.compare:
        cmd_compare(args)
    elif args.market:
        cmd_market(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
