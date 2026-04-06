#!/usr/bin/env python3
"""
Tenant Screener Agent
Screens rental applicants with background checks, credit info, and scoring.
Stores applicant data in JSON format.
"""

import argparse
import json
import logging
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "tenant_screener.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TenantScreenerAgent")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/tenant_screening")
DATA_DIR.mkdir(parents=True, exist_ok=True)
APPLICANTS_FILE = DATA_DIR / "applicants.json"
PROPERTIES_FILE = DATA_DIR / "properties.json"

def load_applicants():
    if APPLICANTS_FILE.exists():
        with open(APPLICANTS_FILE, 'r') as f:
            return json.load(f)
    return {"applicants": [], "last_id": 0}

def save_applicants(data):
    with open(APPLICANTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_properties():
    if PROPERTIES_FILE.exists():
        with open(PROPERTIES_FILE, 'r') as f:
            return json.load(f)
    return {"properties": []}

def save_properties(data):
    with open(PROPERTIES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def generate_credit_score():
    """Generate a realistic credit score."""
    weights = [0.05, 0.1, 0.2, 0.3, 0.25, 0.08, 0.02]
    ranges = [(300, 500), (500, 580), (580, 620), (620, 670), (670, 720), (720, 780), (780, 850)]
    idx = random.choices(range(len(weights)), weights=weights)[0]
    return random.randint(*ranges[idx])

def calculate_background_score(applicant):
    """Calculate background check score (0-100)."""
    score = 100
    score -= applicant.get("evictions", 0) * 25
    score -= applicant.get("bankruptcies", 0) * 20
    score -= applicant.get("criminal_felony", 0) * 30
    score -= applicant.get("criminal_misdemeanor", 0) * 10
    return max(0, min(100, score))

def calculate_income_score(applicant, rent_amount):
    """Calculate income adequacy score (0-100)."""
    monthly_income = applicant.get("monthly_income", 0)
    if rent_amount <= 0:
        return 50
    required = rent_amount * 3
    
    if monthly_income == 0:
        return 0
    ratio = monthly_income / required
    if ratio >= 3:
        return 100
    elif ratio >= 2.5:
        return 85
    elif ratio >= 2:
        return 70
    elif ratio >= 1.5:
        return 50
    elif ratio >= 1:
        return 30
    else:
        return 10

def screen_applicant(applicant, rent_amount):
    """Perform complete screening and return score breakdown."""
    credit_score = applicant.get("credit_score", generate_credit_score())
    background_score = calculate_background_score(applicant)
    income_score = calculate_income_score(applicant, rent_amount)
    overall = (credit_score * 0.4) + (background_score * 0.3) + (income_score * 0.3)
    
    if credit_score >= 780:
        credit_rating = "Excellent"
    elif credit_score >= 720:
        credit_rating = "Good"
    elif credit_score >= 680:
        credit_rating = "Fair"
    elif credit_score >= 620:
        credit_rating = "Poor"
    else:
        credit_rating = "Very Poor"
    
    if overall >= 80:
        recommendation = "STRONGLY APPROVE"
    elif overall >= 65:
        recommendation = "APPROVE"
    elif overall >= 50:
        recommendation = "CONDITIONAL (co-signer recommended)"
    else:
        recommendation = "DENY"
    
    return {
        "credit_score": credit_score,
        "credit_rating": credit_rating,
        "background_score": background_score,
        "income_score": income_score,
        "overall_score": round(overall, 1),
        "recommendation": recommendation
    }

def add_applicant(args):
    """Add a new tenant applicant."""
    data = load_applicants()
    data["last_id"] += 1
    
    applicant = {
        "id": data["last_id"],
        "name": args.name,
        "email": args.email,
        "phone": args.phone,
        "property_id": args.property,
        "monthly_income": float(args.income),
        "employment_status": args.employment,
        "credit_score": generate_credit_score() if not args.credit_score else int(args.credit_score),
        "evictions": int(args.evictions) if args.evictions else 0,
        "bankruptcies": int(args.bankruptcies) if args.bankruptcies else 0,
        "criminal_felony": int(args.felony) if args.felony else 0,
        "criminal_misdemeanor": int(args.misdemeanor) if args.misdemeanor else 0,
        "rental_history": [],
        "status": "pending",
        "applied_at": datetime.now().isoformat()
    }
    
    data["applicants"].append(applicant)
    save_applicants(data)
    logger.info(f"Added applicant {applicant['id']}: {applicant['name']}")
    print(f"✅ Added applicant #{applicant['id']}: {applicant['name']}")
    return applicant

def screen_applicant_cmd(args):
    """Screen an applicant by ID."""
    data = load_applicants()
    for app in data["applicants"]:
        if app["id"] == int(args.id):
            rent = float(args.rent) if args.rent else 0
            result = screen_applicant(app, rent)
            
            print(f"\n🔍 Screening Results for: {app['name']}")
            print(f"  Applied: {app['applied_at'][:10]} | Property ID: {app['property_id']}")
            print(f"  ───────────────────────────────────────")
            print(f"  Credit Score:    {result['credit_score']} ({result['credit_rating']})")
            print(f"  Background:      {result['background_score']}/100")
            print(f"  Income Score:    {result['income_score']}/100")
            print(f"  ───────────────────────────────────────")
            print(f"  OVERALL SCORE:   {result['overall_score']}/100")
            print(f"  Recommendation:  {result['recommendation']}")
            
            if "APPROVE" in result["recommendation"]:
                app["status"] = "approved"
            elif "CONDITIONAL" in result["recommendation"]:
                app["status"] = "conditional"
            else:
                app["status"] = "denied"
            app["screening_result"] = result
            app["screened_at"] = datetime.now().isoformat()
            save_applicants(data)
            return
    
    print(f"Applicant #{args.id} not found.")

def list_applicants(args):
    """List all applicants with optional filters."""
    data = load_applicants()
    apps = data["applicants"]
    
    if args.property:
        apps = [a for a in apps if a.get("property_id") == args.property]
    if args.status:
        apps = [a for a in apps if a.get("status") == args.status]
    if args.name:
        apps = [a for a in apps if args.name.lower() in a["name"].lower()]
    
    if not apps:
        print("No applicants found.")
        return
    
    print(f"\n👥 Applicants ({len(apps)} found):\n")
    for a in apps:
        status_emoji = {"pending": "⏳", "approved": "✅", "denied": "❌", "conditional": "⚠️"}.get(a.get("status"), "❓")
        print(f"  [{a['id']}] {status_emoji} {a['name']}")
        print(f"      Email: {a['email']} | Phone: {a['phone']}")
        print(f"      Property: {a['property_id']} | Income: ${a['monthly_income']:,.2f}")
        print(f"      Employment: {a['employment_status']} | Status: {a.get('status', 'pending')}")
        if "screening_result" in a:
            print(f"      Score: {a['screening_result']['overall_score']}/100 ({a['screening_result']['recommendation']})")
        print()

def add_property(args):
    """Add a rental property."""
    data = load_properties()
    prop_id = args.id or (max([p["id"] for p in data["properties"]], default=0) + 1)
    prop = {
        "id": prop_id,
        "address": args.address,
        "rent": float(args.rent),
        "bedrooms": int(args.bedrooms),
        "available": True
    }
    data["properties"].append(prop)
    save_properties(data)
    print(f"✅ Added property: {prop['address']} - ${prop['rent']}/month")

def list_properties(args):
    """List all properties."""
    data = load_properties()
    if not data["properties"]:
        print("No properties registered.")
        return
    
    print(f"\n🏠 Properties ({len(data['properties'])}):\n")
    for p in data["properties"]:
        avail = "✅ Available" if p.get("available") else "❌ Occupied"
        print(f"  [{p['id']}] {p['address']}")
        print(f"      Rent: ${p['rent']}/mo | {p['bedrooms']} bed | {avail}")
        print()

def report(args):
    """Generate screening report."""
    data = load_applicants()
    apps = data["applicants"]
    
    total = len(apps)
    pending = len([a for a in apps if a.get("status") == "pending"])
    approved = len([a for a in apps if a.get("status") == "approved"])
    denied = len([a for a in apps if a.get("status") == "denied"])
    conditional = len([a for a in apps if a.get("status") == "conditional"])
    
    avg_score = 0
    screened = [a for a in apps if "screening_result" in a]
    if screened:
        avg_score = sum(a["screening_result"]["overall_score"] for a in screened) / len(screened)
    
    print(f"\n📊 Tenant Screening Report")
    print(f"  Total Applications: {total}")
    print(f"  Pending: {pending} | Approved: {approved} | Denied: {denied} | Conditional: {conditional}")
    print(f"  Average Score: {avg_score:.1f}/100")
    print(f"  Average Credit: {sum(a['credit_score'] for a in apps) / total:.0f}" if total else "N/A")

def main():
    parser = argparse.ArgumentParser(
        description="Tenant Screener Agent - Screen rental applicants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add-property --id 1 --address "123 Main St" --rent 2000 --bedrooms 2
  %(prog)s add --name "John Doe" --email john@email.com --phone 555-1234 --property 1 --income 6000 --employment employed
  %(prog)s screen --id 1 --rent 2000
  %(prog)s list --status pending
  %(prog)s list-properties
  %(prog)s report
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    p_add_prop = subparsers.add_parser("add-property", help="Add a rental property")
    p_add_prop.add_argument("--id", type=int, help="Property ID")
    p_add_prop.add_argument("--address", required=True, help="Property address")
    p_add_prop.add_argument("--rent", required=True, type=float, help="Monthly rent")
    p_add_prop.add_argument("--bedrooms", required=True, type=int, help="Number of bedrooms")
    
    p_add = subparsers.add_parser("add", help="Add applicant")
    p_add.add_argument("--name", required=True, help="Full name")
    p_add.add_argument("--email", required=True, help="Email")
    p_add.add_argument("--phone", required=True, help="Phone")
    p_add.add_argument("--property", required=True, help="Property ID")
    p_add.add_argument("--income", required=True, type=float, help="Monthly income")
    p_add.add_argument("--employment", required=True, choices=["employed", "self-employed", "unemployed", "retired", "student"])
    p_add.add_argument("--credit-score", help="Known credit score")
    p_add.add_argument("--evictions", help="Number of evictions")
    p_add.add_argument("--bankruptcies", help="Number of bankruptcies")
    p_add.add_argument("--felony", help="Number of felonies")
    p_add.add_argument("--misdemeanor", help="Number of misdemeanors")
    
    p_screen = subparsers.add_parser("screen", help="Screen an applicant")
    p_screen.add_argument("--id", required=True, help="Applicant ID")
    p_screen.add_argument("--rent", type=float, help="Monthly rent amount")
    
    p_list = subparsers.add_parser("list", help="List applicants")
    p_list.add_argument("--status", choices=["pending", "approved", "denied", "conditional"])
    p_list.add_argument("--property", help="Filter by property ID")
    p_list.add_argument("--name", help="Filter by name (partial match)")
    
    p_list_prop = subparsers.add_parser("list-properties", help="List properties")
    subparsers.add_parser("report", help="Generate screening report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.command == "add-property":
            add_property(args)
        elif args.command == "add":
            add_applicant(args)
        elif args.command == "screen":
            screen_applicant_cmd(args)
        elif args.command == "list":
            list_applicants(args)
        elif args.command == "list-properties":
            list_properties(args)
        elif args.command == "report":
            report(args)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
