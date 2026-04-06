#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          PATENT FILER AGENT                                  ║
║          Patent Tracking & IP Management                      ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Patent idea tracking
  - Prior art search helper
  - Filing status tracking
  - Cost tracking
  - Jurisdiction management (US, EU, PCT, DE)
  - Patent timeline management
  - Portfolio overview

Usage:
  python3 patent_filer_agent.py --new --title "Novel AI Method" --description "..."
  python3 patent_filer_agent.py --list --status pending
  python3 patent_filer_agent.py --track --id 2024-001
  python3 patent_filer_agent.py --cost --id 2024-001 --add 500 --category filing
  python3 patent_filer_agent.py --search --query "machine learning classification"
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

# Logging setup
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "patent_filer.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("openclaw.patent_filer")

# Data storage
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/patents")
DATA_DIR.mkdir(parents=True, exist_ok=True)
PATENTS_FILE = DATA_DIR / "patent_portfolio.json"
COSTS_FILE = DATA_DIR / "patent_costs.json"
TIMELINE_FILE = DATA_DIR / "patent_timeline.json"


@dataclass
class Patent:
    id: str
    title: str
    description: str
    inventor: str
    filing_date: str
    application_number: str
    status: str  # idea, drafted, filed, published, granted, expired, abandoned
    jurisdiction: str  # US, EU, PCT, DE, WO
    ipc_classes: list  # International Patent Classification
    priority_date: str
    expiration_date: str
    costs_total: float
    notes: str
    documents: list
    related_patents: list


@dataclass
class PatentCost:
    id: str
    patent_id: str
    date: str
    amount: float
    currency: str
    category: str  # filing, examination, attorney, maintenance, other
    description: str


@dataclass
class PatentTimeline:
    id: str
    patent_id: str
    event_date: str
    event_type: str  # filing, office_action, response, publication, grant, renewal
    description: str
    deadline: str
    status: str  # scheduled, completed, overdue


# Sample IPC classes for reference
IPC_CLASSES = {
    "A": "Human Necessities",
    "B": "Performing Operations, Transporting",
    "C": "Chemistry, Metallurgy",
    "D": "Textiles, Paper",
    "E": "Fixed Constructions",
    "F": "Mechanical Engineering",
    "G": "Physics",
    "H": "Electricity"
}

SAMPLE_PATENTS = [
    {"class": "G06N", "description": "Computer systems based on specific computational models (Machine Learning)"},
    {"class": "G06F", "description": "Electric digital data processing"},
    {"class": "G06Q", "description": "Commerce/e-commerce, business data processing"},
    {"class": "H04L", "description": "Transmission of digital information"},
    {"class": "G10L", "description": "Speech recognition, analysis/synthesis of speech"},
]


def load_patents() -> list:
    """Load patent portfolio."""
    try:
        if PATENTS_FILE.exists():
            with open(PATENTS_FILE, 'r') as f:
                data = json.load(f)
                return [Patent(**p) for p in data.get('patents', [])]
    except Exception as e:
        log.error(f"Error loading patents: {e}")
    return []


def save_patents(patents: list) -> None:
    """Save patent portfolio."""
    try:
        data = {'patents': [asdict(p) for p in patents], 'updated_at': datetime.now().isoformat()}
        with open(PATENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving patents: {e}")


def load_costs() -> list:
    """Load patent costs."""
    try:
        if COSTS_FILE.exists():
            with open(COSTS_FILE, 'r') as f:
                data = json.load(f)
                return [PatentCost(**c) for c in data.get('costs', [])]
    except Exception as e:
        log.error(f"Error loading costs: {e}")
    return []


def save_costs(costs: list) -> None:
    """Save patent costs."""
    try:
        data = {'costs': [asdict(c) for c in costs], 'updated_at': datetime.now().isoformat()}
        with open(COSTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving costs: {e}")


def generate_patent_id() -> str:
    """Generate unique patent ID."""
    return f"{datetime.now().year}-{len(load_patents()) + 1:03d}"


def suggest_ipc_classes(description: str) -> list:
    """Suggest IPC classes based on description."""
    desc_lower = description.lower()
    suggestions = []
    
    # Keyword mapping to IPC classes
    keywords_map = {
        "G06N": ["machine learning", "neural network", "deep learning", "ai", "artificial intelligence", "classifier"],
        "G06F": ["software", "computer", "processor", "algorithm", "data processing", "computing"],
        "G06Q": ["commerce", "business", "e-commerce", "payment", "transaction", "recommendation"],
        "H04L": ["network", "communication", "internet", "data transmission", "protocol"],
        "G10L": ["speech", "voice", "audio", "speaker", "recognition", "synthesis", "nlp", "natural language"],
        "G06T": ["image", "video", "graphics", "visual", "rendering", "3d"],
        "G16H": ["health", "medical", "healthcare", "diagnosis", "treatment"],
        "B25J": ["robot", "robotic", "mechanical arm", "automation"],
    }
    
    for ipc, keywords in keywords_map.items():
        if any(kw in desc_lower for kw in keywords):
            suggestions.append(ipc)
    
    return suggestions if suggestions else ["G06F"]  # Default to G06F


def create_patent(title: str, description: str, inventor: str = "Company",
                  jurisdiction: str = "US") -> Patent:
    """Create a new patent record."""
    patent_id = generate_patent_id()
    now = datetime.now()
    
    patent = Patent(
        id=patent_id,
        title=title,
        description=description,
        inventor=inventor,
        filing_date="",
        application_number="",
        status="idea",
        jurisdiction=jurisdiction,
        ipc_classes=suggest_ipc_classes(description),
        priority_date=now.strftime("%Y-%m-%d"),
        expiration_date=(now + timedelta(days=365*20)).strftime("%Y-%m-%d"),  # 20 years from filing
        costs_total=0.0,
        notes="",
        documents=[],
        related_patents=[]
    )
    
    return patent


def add_cost(patent_id: str, amount: float, category: str, description: str = "",
             currency: str = "USD") -> PatentCost:
    """Add a cost to a patent."""
    cost = PatentCost(
        id=f"cost-{datetime.now().strftime('%Y%m%d%H%M')}",
        patent_id=patent_id,
        date=datetime.now().strftime("%Y-%m-%d"),
        amount=amount,
        currency=currency,
        category=category,
        description=description
    )
    
    costs = load_costs()
    costs.append(cost)
    save_costs(costs)
    
    # Update patent total
    patents = load_patents()
    for p in patents:
        if p.id == patent_id:
            p.costs_total += amount
            save_patents(patents)
            break
    
    return cost


def get_portfolio_summary() -> dict:
    """Get portfolio summary statistics."""
    patents = load_patents()
    costs = load_costs()
    
    total_cost = sum(c.amount for c in costs)
    by_status = {}
    by_jurisdiction = {}
    by_status_usd = {}
    
    for p in patents:
        by_status[p.status] = by_status.get(p.status, 0) + 1
        by_jurisdiction[p.jurisdiction] = by_jurisdiction.get(p.jurisdiction, 0) + 1
        
        # Calculate USD equivalent (rough estimate)
        usd_amount = p.costs_total if p.id not in by_status_usd else by_status_usd.get(p.jurisdiction, {})
        by_status_usd[p.jurisdiction] = by_status_usd.get(p.jurisdiction, 0) + p.costs_total
    
    return {
        "total_patents": len(patents),
        "total_cost_usd": total_cost,
        "by_status": by_status,
        "by_jurisdiction": by_jurisdiction,
        "upcoming_deadlines": len([p for p in patents if p.status == "filed"])
    }


def cmd_new(args) -> int:
    """Create a new patent record."""
    log.info(f"Creating new patent: {args.title}")
    
    patent = create_patent(
        title=args.title,
        description=args.description,
        inventor=args.inventor or "Company",
        jurisdiction=args.jurisdiction or "US"
    )
    
    # Save
    patents = load_patents()
    patents.append(patent)
    save_patents(patents)
    
    print(f"\n✅ Patent Record Created")
    print(f"   ID: {patent.id}")
    print(f"   Title: {patent.title}")
    print(f"   Inventor: {patent.inventor}")
    print(f"   Status: {patent.status.upper()}")
    print(f"   Suggested IPC Classes: {', '.join(patent.ipc_classes)}")
    print(f"   Jurisdiction: {patent.jurisdiction}")
    print(f"   Priority Date: {patent.priority_date}")
    
    print(f"\n📋 Next Steps:")
    print(f"   1. Conduct prior art search")
    print(f"   2. Draft patent application")
    print(f"   3. File with --update --id {patent.id} --status filed")
    
    return 0


def cmd_list(args) -> int:
    """List patents."""
    patents = load_patents()
    
    if not patents:
        print("No patents in portfolio.")
        return 0
    
    # Apply filters
    filtered = patents
    if args.status:
        filtered = [p for p in filtered if p.status == args.status]
    if args.jurisdiction:
        filtered = [p for p in filtered if p.jurisdiction == args.jurisdiction]
    if args.ipc:
        filtered = [p for p in filtered if any(args.ipc in c for c in p.ipc_classes)]
    
    if not filtered:
        print("No patents match your criteria.")
        return 0
    
    print(f"\nFound {len(filtered)} patent(s):\n")
    for p in filtered:
        print(f"{'='*60}")
        print(f"📜 {p.id} - {p.title}")
        print(f"   Inventor: {p.inventor}")
        print(f"   Status: {p.status.upper()}")
        print(f"   Jurisdiction: {p.jurisdiction}")
        print(f"   IPC Classes: {', '.join(p.ipc_classes)}")
        print(f"   Costs: ${p.costs_total:,.2f}")
        if p.application_number:
            print(f"   Application #: {p.application_number}")
        print(f"{'='*60}")
    
    return 0


def cmd_track(args) -> int:
    """Track specific patent."""
    patents = load_patents()
    
    patent = next((p for p in patents if p.id == args.id), None)
    
    if not patent:
        print(f"Patent not found: {args.id}")
        return 1
    
    print(f"\n{'='*60}")
    print(f"📜 PATENT DETAILS: {patent.id}")
    print(f"{'='*60}")
    print(f"Title: {patent.title}")
    print(f"Description: {patent.description}")
    print(f"Inventor: {patent.inventor}")
    print(f"Status: {patent.status.upper()}")
    print(f"Jurisdiction: {patent.jurisdiction}")
    print(f"Application #: {patent.application_number or 'Not filed'}")
    print(f"IPC Classes: {', '.join(patent.ipc_classes)}")
    print(f"\nDates:")
    print(f"   Priority Date: {patent.priority_date}")
    print(f"   Filing Date: {patent.filing_date or 'Not filed'}")
    print(f"   Expiration: {patent.expiration_date}")
    print(f"\nCosts: ${patent.costs_total:,.2f}")
    
    if patent.notes:
        print(f"Notes: {patent.notes}")
    
    if patent.documents:
        print(f"\nDocuments ({len(patent.documents)}):")
        for doc in patent.documents:
            print(f"   - {doc}")
    
    if patent.related_patents:
        print(f"\nRelated Patents: {', '.join(patent.related_patents)}")
    
    print(f"{'='*60}")
    
    # Show cost breakdown
    costs = load_costs()
    patent_costs = [c for c in costs if c.patent_id == args.id]
    
    if patent_costs:
        print(f"\n💰 Cost Breakdown:")
        by_category = {}
        for c in patent_costs:
            by_category[c.category] = by_category.get(c.category, 0) + c.amount
        
        for cat, amt in by_category.items():
            print(f"   {cat}: ${amt:,.2f}")
    
    return 0


def cmd_update(args) -> int:
    """Update patent status/details."""
    patents = load_patents()
    
    for i, patent in enumerate(patents):
        if patent.id == args.id:
            if args.status:
                old_status = patent.status
                patent.status = args.status
                
                # Update filing date if filing
                if args.status == "filed" and not patent.filing_date:
                    patent.filing_date = datetime.now().strftime("%Y-%m-%d")
                    patent.priority_date = patent.priority_date or patent.filing_date
                
                # Update expiration if granted
                if args.status == "granted" and patent.filing_date:
                    filing = datetime.strptime(patent.filing_date, "%Y-%m-%d")
                    patent.expiration_date = (filing + timedelta(days=365*20)).strftime("%Y-%m-%d")
                
                log.info(f"Updated patent {args.id} status: {old_status} -> {args.status}")
            
            if args.application_number:
                patent.application_number = args.application_number
            if args.notes:
                patent.notes = args.notes
            
            save_patents(patents)
            print(f"✅ Updated patent {args.id}")
            return 0
    
    print(f"Patent not found: {args.id}")
    return 1


def cmd_cost(args) -> int:
    """Add or view patent costs."""
    if args.action == "add":
        cost = add_cost(
            patent_id=args.id,
            amount=args.amount,
            category=args.category or "other",
            description=args.description or "",
            currency=args.currency or "USD"
        )
        
        print(f"\n✅ Cost Added")
        print(f"   ID: {cost.id}")
        print(f"   Patent: {cost.patent_id}")
        print(f"   Amount: ${cost.amount:,.2f} {cost.currency}")
        print(f"   Category: {cost.category}")
        print(f"   Date: {cost.date}")
        
    elif args.action == "summary":
        costs = load_costs()
        
        if args.id:
            patent_costs = [c for c in costs if c.patent_id == args.id]
        else:
            patent_costs = costs
        
        if not patent_costs:
            print("No costs recorded.")
            return 0
        
        by_category = {}
        total = 0
        for c in patent_costs:
            by_category[c.category] = by_category.get(c.category, 0) + c.amount
            total += c.amount
        
        print(f"\n💰 Cost Summary:")
        print(f"{'='*60}")
        print(f"Total: ${total:,.2f}")
        print(f"\nBy Category:")
        for cat, amt in sorted(by_category.items()):
            print(f"   {cat}: ${amt:,.2f}")
        
        if args.id:
            print(f"\nFor Patent: {args.id}")
        
        print(f"{'='*60}")
    
    return 0


def cmd_search(args) -> int:
    """Search for IPC classes and prior art."""
    print(f"\n🔍 Prior Art Search Helper")
    print(f"{'='*60}")
    print(f"Query: {args.query}")
    
    # Suggest IPC classes
    suggestions = suggest_ipc_classes(args.query)
    print(f"\n📑 Suggested IPC Classes:")
    for ipc in suggestions:
        # Find description
        desc = ""
        for s in SAMPLE_PATENTS:
            if s["class"] in ipc:
                desc = s["description"]
                break
        print(f"   {ipc} - {desc}")
    
    # IPC class reference
    print(f"\n📚 IPC Class Reference:")
    for letter, desc in IPC_CLASSES.items():
        print(f"   {letter} - {desc}")
    
    print(f"\n💡 Tips:")
    print(f"   - Search USPTO database: https://patents.google.com")
    print(f"   - Search EPO: https://worldwide.espacenet.com")
    print(f"   - Use IPC search to narrow down relevant patents")
    print(f"   - Check for 'prior art' before filing")
    
    return 0


def cmd_portfolio(args) -> int:
    """Show portfolio overview."""
    summary = get_portfolio_summary()
    
    print(f"\n{'='*60}")
    print(f"📊 PATENT PORTFOLIO OVERVIEW")
    print(f"{'='*60}")
    print(f"Total Patents: {summary['total_patents']}")
    print(f"Total Costs: ${summary['total_cost_usd']:,.2f}")
    
    print(f"\nBy Status:")
    for status, count in summary.get('by_status', {}).items():
        print(f"   {status}: {count}")
    
    print(f"\nBy Jurisdiction:")
    for jurisdiction, count in summary.get('by_jurisdiction', {}).items():
        print(f"   {jurisdiction}: {count}")
    
    print(f"\n💰 Cost Summary:")
    costs = load_costs()
    if costs:
        by_cat = {}
        for c in costs:
            by_cat[c.category] = by_cat.get(c.category, 0) + c.amount
        for cat, amt in sorted(by_cat.items()):
            print(f"   {cat}: ${amt:,.2f}")
    
    print(f"{'='*60}")
    
    # Upcoming deadlines
    patents = load_patents()
    upcoming = []
    now = datetime.now()
    
    for p in patents:
        if p.status == "filed":
            exp = datetime.strptime(p.expiration_date, "%Y-%m-%d")
            if exp > now:
                days_left = (exp - now).days
                upcoming.append((p.id, p.title, days_left))
    
    if upcoming:
        print(f"\n📅 Upcoming Deadlines:")
        for pid, title, days in sorted(upcoming, key=lambda x: x[2])[:5]:
            print(f"   {pid}: {days} days left - {title}")
    
    return 0


def cmd_ipc(args) -> int:
    """Show IPC classification reference."""
    print(f"\n📚 IPC CLASSIFICATION REFERENCE")
    print(f"{'='*60}")
    
    if args.code:
        # Show specific class
        code = args.code.upper()
        print(f"Class {code}:")
        for s in SAMPLE_PATENTS:
            if s["class"].startswith(code[0]):
                print(f"   {s['class']} - {s['description']}")
    else:
        # Show all main classes
        print(f"\nMain Classes:")
        for letter, desc in IPC_CLASSES.items():
            print(f"   {letter} - {desc}")
        
        print(f"\nCommon Subclasses:")
        for s in SAMPLE_PATENTS:
            print(f"   {s['class']} - {s['description']}")
    
    print(f"{'='*60}")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Patent Filer Agent - IP Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --new --title "Novel ML Method" --description "Machine learning classifier..."
  %(prog)s --list
  %(prog)s --list --status filed --jurisdiction US
  %(prog)s --track --id 2024-001
  %(prog)s --update --id 2024-001 --status filed --application-number "US17/123,456"
  %(prog)s --cost --action add --id 2024-001 --amount 500 --category filing
  %(prog)s --cost --action summary
  %(prog)s --search --query "neural network training optimization"
  %(prog)s --portfolio
  %(prog)s --ipc --code G06
        """
    )
    
    parser.add_argument('--new', action='store_true', help='Create new patent record')
    parser.add_argument('--title', help='Patent title')
    parser.add_argument('--description', help='Patent description')
    parser.add_argument('--inventor', help='Inventor name')
    parser.add_argument('--jurisdiction', choices=['US', 'EU', 'PCT', 'DE', 'WO'], help='Filing jurisdiction')
    parser.add_argument('--list', dest='list_enabled', action='store_true', help='List patents')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--ipc', help='Filter by IPC class')
    parser.add_argument('--track', action='store_true', help='Track specific patent')
    parser.add_argument('--id', help='Patent ID')
    parser.add_argument('--update', action='store_true', help='Update patent')
    parser.add_argument('--application-number', help='Application number')
    parser.add_argument('--notes', help='Additional notes')
    parser.add_argument('--cost', action='store_true', help='Manage costs')
    parser.add_argument('--action', choices=['add', 'summary'], help='Cost action')
    parser.add_argument('--amount', type=float, help='Cost amount')
    parser.add_argument('--category', help='Cost category')
    parser.add_argument('--currency', default='USD', help='Currency')
    parser.add_argument('--desc', help='Description')
    parser.add_argument('--search', action='store_true', help='Prior art search')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--portfolio', action='store_true', help='Portfolio overview')
    parser.add_argument('--ipc-ref', dest='ipc_ref', action='store_true', help='IPC reference')
    parser.add_argument('--code', help='IPC class code')
    
    args = parser.parse_args()
    
    # Handle --ipc conflict
    if hasattr(args, 'ipc_ref') and args.ipc_ref:
        args.list_enabled = False
    elif hasattr(args, 'ipc') and isinstance(args.ipc, bool):
        args.ipc_ref = args.ipc
    
    try:
        if args.new:
            if not all([args.title, args.description]):
                print("Error: --title and --description are required")
                return 1
            return cmd_new(args)
        elif args.list_enabled:
            return cmd_list(args)
        elif args.track:
            if not args.id:
                print("Error: --id is required")
                return 1
            return cmd_track(args)
        elif args.update:
            if not args.id:
                print("Error: --id is required")
                return 1
            return cmd_update(args)
        elif args.cost:
            return cmd_cost(args)
        elif args.search:
            if not args.query:
                print("Error: --query is required")
                return 1
            return cmd_search(args)
        elif args.portfolio:
            return cmd_portfolio(args)
        elif args.ipc_ref:
            return cmd_ipc(args)
        else:
            parser.print_help()
            return 0
    except KeyboardInterrupt:
        log.info("Operation cancelled")
        return 130
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
