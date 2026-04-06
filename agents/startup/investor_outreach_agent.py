#!/usr/bin/env python3
"""
Investor Outreach Agent
Helps startups find, research, and reach out to potential investors.
"""

import argparse
import logging
import sys
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/home/clawbot/.openclaw/workspace/logs/investor_outreach.log')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Investor:
    """Represents an investor or VC firm."""
    name: str
    type: str  # angel, vc, corporate, family_office
    stage: str  # pre-seed, seed, series_a, etc.
    sectors: List[str]
    portfolio: List[str]
    check_size: str
    location: str
    contact: str
    criteria: List[str]


# Investor database
INVESTORS = {
    "y_combinator": Investor(
        name="Y Combinator",
        type="accelerator",
        stage="pre-seed, seed",
        sectors=["saas", "marketplace", "consumer", "fintech", "ai", "b2b", "crypto"],
        portfolio=["Airbnb", "Dropbox", "Stripe", "Coinbase", "Reddit", "DoorDash"],
        check_size="$500K - $2M",
        location="Mountain View, CA (Global)",
        contact="apply@ycombinator.com",
        criteria=["Strong founders", "Large market", "Defensible product", "Fast execution"]
    ),
    "sequoia": Investor(
        name="Sequoia Capital",
        type="vc",
        stage="seed, series_a, series_b",
        sectors=["tech", "saas", "fintech", "healthcare", "crypto", "consumer"],
        portfolio=["Apple", "Google", "PayPal", "Stripe", "DoorDash", "WhatsApp"],
        check_size="$1M - $500M+",
        location="Menlo Park, CA",
        contact="sequoiacapital.com/contact",
        criteria=["Large TAM", "Strong team", "Product-market fit indicators", "Capital efficient"]
    ),
    "a16z": Investor(
        name="Andreessen Horowitz",
        type="vc",
        stage="seed, series_a, series_b, series_c",
        sectors=["ai", "crypto", "fintech", "saas", "consumer", "gaming", "bio"],
        portfolio=["Facebook", "Airbnb", "Coinbase", "Slack", "Pinterest", "Robinhood"],
        check_size="$1M - $100M+",
        location="Menlo Park, CA / NYC",
        contact="a16z.com/how-to-pitch",
        criteria=["Founders with domain expertise", "Transformative technology", "Large opportunity"]
    ),
    "foundersFund": Investor(
        name="Founders Fund",
        type="vc",
        stage="seed, series_a",
        sectors=["deep tech", "ai", "space", "bio", "consumer"],
        portfolio=["SpaceX", "Palantir", "Stripe", "Facebook", " Airbnb"],
        check_size="$500K - $50M",
        location="San Francisco, CA",
        contact="foundersfund.com/apply",
        criteria=["Bold ideas", "Exceptional founders", "Category-defining potential"]
    ),
    "benchmark": Investor(
        name="Benchmark",
        type="vc",
        stage="seed, series_a",
        sectors=["saas", "consumer", "marketplace", "enterprise", "mobile"],
        portfolio=["Uber", "Twitter", "Snapchat", "Instagram", "Discord"],
        check_size="$1M - $50M",
        location="San Francisco, CA",
        contact="benchmark.com/venture",
        criteria=["Early product-market fit", "Fast-growing", "Founder-led"]
    ),
    "index": Investor(
        name="Index Ventures",
        type="vc",
        stage="seed, series_a",
        sectors=["saas", "fintech", "marketplace", "ecommerce", "ai"],
        portfolio=["Slack", "Deliveroo", "Revolut", "Figma", "Notion"],
        check_size="€500K - €20M",
        location="Geneva / London / NYC",
        contact="indexventures.com/apply",
        criteria=["European focus", "Strong founders", "B2B software", "International scale"]
    ),
    "atomico": Investor(
        name="Atomico",
        type="vc",
        stage="seed, series_a, series_b",
        sectors=["saas", "fintech", "consumer", "climate tech", "ai"],
        portfolio=["Miro", "Klarna", "Pathable", "Pulse", "Synthesia"],
        check_size="€500K - €50M",
        location="London (Global)",
        contact="atomico.com/apply",
        criteria=["European founders", "Global ambitions", "Tech-focused", "Experienced team"]
    ),
    "earlybird": Investor(
        name="Earlybird",
        type="vc",
        stage="seed, series_a, series_b",
        sectors=["saas", "fintech", "deep tech", "cleantech", "healthcare"],
        portfolio=["N26", "Personio", "Celonis", "Trade Republic"],
        check_size="€500K - €25M",
        location="Munich / Berlin / Zurich",
        contact="earlybird.com",
        criteria=["European focus", "B2B software", "Experienced founders", "Clear market"]
    ),
    "potsdamer": Investor(
        name="Potsdamer Innovationsinstitut",
        type="vc",
        stage="seed, series_a",
        sectors=["saas", "fintech", "retail", "logistics", "manufacturing"],
        portfolio=["Various German startups"],
        check_size="€100K - €5M",
        location="Potsdam, Germany",
        contact="pi-i.de",
        criteria=["German market focus", "B2B", "Scalable model"]
    ),
    "angellist": Investor(
        name="AngelList",
        type="platform",
        stage="pre-seed, seed",
        sectors=["all tech"],
        portfolio=["Many startups via rolling funds"],
        check_size="$50K - $500K",
        location="Global",
        contact="angellist.com",
        criteria=["Strong founding team", "Innovative idea", "Some traction"]
    ),
    "techstars": Investor(
        name="Techstars",
        type="accelerator",
        stage="pre-seed, seed",
        sectors=["saas", "fintech", "healthcare", "retail", "ai", "climate"],
        portfolio=["Docker", "Twilio", "Coinbase", "DataRobot"],
        check_size="$120K - $500K",
        location="Global (many programs)",
        contact="techstars.com/apply",
        criteria=["Early traction", "Strong team", "Mentor network fit"]
    ),
    "plugandplay": Investor(
        name="Plug and Play",
        type="accelerator",
        stage="pre-seed, seed",
        sectors=["fintech", "healthcare", "supply chain", "retail", "insurtech"],
        portfolio=["PayPal", "Nvidia", "Dropbox"],
        check_size="$50K - $500K",
        location="Global",
        contact="plugandplaytech.com",
        criteria=["Corporate innovation focus", "Industry fit"]
    )
}

# Email templates
EMAIL_TEMPLATES = {
    "cold_intro": """Subject: {company_name} - {unique_hook}

Hi {investor_name},

I noticed your investment in {reference_point} and it immediately caught my attention because {connection_reason}.

We're building {company_name}, {one_liner}.

{key_metric} showing {metric_value}.

{focus_area} is an area I've {relevant_background} for {years_experience} years, and I believe there's a fundamental opportunity to {main_insight}.

We're raising ${amount} to {use_of_funds} and would love to discuss how we might fit your portfolio.

Would you be open to a 20-minute call this week?

Best,
{founder_name}
{founder_email}
""",
    "warm_intro": """Subject: Re: {reference} - Introduction via {mutual_connection}

Hi {investor_name},

{mutual_connection} suggested I reach out to you regarding {company_name}.

We're building {company_name}, {one_liner}, and recently {recent_achievement}.

{investor_focus_fit} - particularly interested in how you're looking at {sector}.

Would you have 20 minutes this week to chat?

Thanks,
{founder_name}
""",
    "follow_up": """Subject: Re: {previous_subject} - {company_name} Update

Hi {investor_name},

Following up on my previous email about {company_name}.

{Milestone_update}.

Still very much interested in discussing how we might work together. Would next week work for a brief call?

Best,
{founder_name}
"""
}


class InvestorOutreachAgent:
    """Agent for investor outreach and research."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        self.investors = INVESTORS.copy()
        self.templates = EMAIL_TEMPLATES.copy()
        logger.info("InvestorOutreachAgent initialized")

    def search_investors(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for investors matching criteria.
        
        Criteria can include: stage, sector, location, check_size
        """
        results = []
        stage = criteria.get("stage", "").lower()
        sector = criteria.get("sector", "").lower()
        investor_type = criteria.get("type", "").lower()
        location = criteria.get("location", "").lower()

        for key, investor in self.investors.items():
            match = True

            if stage:
                stages = [s.strip() for s in investor.stage.split(",")]
                if not any(stage in s.lower() for s in stages):
                    match = False

            if sector:
                if sector not in [s.lower() for s in investor.sectors]:
                    match = False

            if investor_type:
                if investor_type != investor.type.lower():
                    match = False

            if location:
                if location not in investor.location.lower():
                    match = False

            if match:
                results.append(asdict(investor))

        logger.info(f"Found {len(results)} investors matching criteria")
        return results

    def get_investor(self, name: str) -> Dict[str, Any]:
        """Get detailed info about a specific investor."""
        name_key = name.lower().replace(" ", "_")
        if name_key not in self.investors:
            available = ", ".join(self.investors.keys())
            raise ValueError(f"Unknown investor: {name}. Available: {available}")
        return asdict(self.investors[name_key])

    def list_investors(self, filter_type: Optional[str] = None) -> List[Dict[str, str]]:
        """List all investors with optional type filter."""
        investors = []
        for key, inv in self.investors.items():
            if filter_type:
                if inv.type.lower() != filter_type.lower():
                    continue
            investors.append({
                "key": key,
                "name": inv.name,
                "type": inv.type,
                "stage": inv.stage,
                "check_size": inv.check_size,
                "location": inv.location
            })
        logger.info(f"Listed {len(investors)} investors")
        return investors

    def generate_email(self, template_type: str, context: Dict[str, Any]) -> str:
        """Generate personalized outreach email."""
        if template_type not in self.templates:
            raise ValueError(f"Unknown template: {template_type}. Available: {', '.join(self.templates.keys())}")

        template = self.templates[template_type]

        # Validate required fields
        required = []
        if template_type == "cold_intro":
            required = ["investor_name", "company_name", "one_liner", "founder_name", "founder_email"]
        elif template_type == "warm_intro":
            required = ["investor_name", "mutual_connection", "company_name", "founder_name"]
        elif template_type == "follow_up":
            required = ["investor_name", "previous_subject", "company_name", "founder_name"]

        missing = [f for f in required if f not in context or not context[f]]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        email = template
        for key, value in context.items():
            email = email.replace(f"{{{key}}}", str(value))

        logger.info(f"Generated {template_type} email")
        return email

    def create_personalization_hook(self, investor_key: str, startup_info: Dict[str, Any]) -> str:
        """Create a personalized hook for an investor based on their portfolio."""
        if investor_key not in self.investors:
            raise ValueError(f"Unknown investor: {investor_key}")

        investor = self.investors[investor_key]
        company = startup_info.get("company_name", "We")
        sector = startup_info.get("sector", "")

        hooks = []

        # Based on portfolio
        for portfolio_company in investor.portfolio[:2]:
            hooks.append(f"your investment in {portfolio_company}")

        # Based on sector focus
        if sector and sector in [s.lower() for s in investor.sectors]:
            hooks.append(f"your focus on {sector}")

        # Based on stage
        hooks.append(f"your {investor.stage.split(',')[0].strip()} stage focus")

        return " or ".join(hooks[:2])

    def build_outreach_sequence(self, investor_key: str, startup_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build a complete outreach sequence."""
        if investor_key not in self.investors:
            raise ValueError(f"Unknown investor: {investor_key}")

        investor = self.investors[investor_key]
        sequence = []

        # Day 1: Initial email
        hook = self.create_personalization_hook(investor_key, startup_info)
        sequence.append({
            "day": 1,
            "action": "send_email",
            "type": "cold_intro" if "cold" not in investor_key else "warm_intro",
            "subject": f"{startup_info['company_name']} - {hook.split()[2] if len(hook.split()) > 2 else 'Introduction'}",
            "context": {
                "investor_name": investor.name,
                "company_name": startup_info.get("company_name", "Our Startup"),
                "unique_hook": hook.split(",")[0] if "," in hook else hook,
                "connection_reason": hook,
                "one_liner": startup_info.get("one_liner", "building something transformative"),
                "key_metric": startup_info.get("key_metric", "We've"),
                "metric_value": startup_info.get("metric_value", "achieved strong early traction"),
                "relevant_background": startup_info.get("relevant_background", "worked in"),
                "years_experience": startup_info.get("years_experience", "several"),
                "main_insight": startup_info.get("main_insight", "change the industry"),
                "amount": startup_info.get("raise_amount", "TBD"),
                "use_of_funds": startup_info.get("use_of_funds", "scale operations"),
                "founder_name": startup_info.get("founder_name", "Founder"),
                "founder_email": startup_info.get("founder_email", "founder@example.com")
            }
        })

        # Day 4: Follow-up
        sequence.append({
            "day": 4,
            "action": "send_email",
            "type": "follow_up",
            "subject": f"Re: {sequence[0]['subject']}",
            "context": {
                "investor_name": investor.name,
                "previous_subject": sequence[0]["subject"],
                "company_name": startup_info.get("company_name", "Our Startup"),
                "milestone_update": startup_info.get("milestone_update", "We've continued to make strong progress"),
                "founder_name": startup_info.get("founder_name", "Founder")
            }
        })

        # Day 10: Second follow-up or social
        sequence.append({
            "day": 10,
            "action": "send_email" if investor.type != "platform" else "linkedin_connect",
            "type": "follow_up",
            "subject": f"Re: {sequence[0]['subject']} - Quick question",
            "context": {
                "investor_name": investor.name,
                "previous_subject": sequence[0]["subject"],
                "company_name": startup_info.get("company_name", "Our Startup"),
                "milestone_update": startup_info.get("final_update", "Wanted to share one more update before moving on"),
                "founder_name": startup_info.get("founder_name", "Founder")
            }
        })

        logger.info(f"Built outreach sequence for {investor.name}: {len(sequence)} steps")
        return sequence

    def track_outreach(self, outreach_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track outreach status and next steps."""
        tracking = {
            "timestamp": datetime.now().isoformat(),
            "investor": outreach_data.get("investor", "Unknown"),
            "company": outreach_data.get("company", "Unknown"),
            "stage": outreach_data.get("stage", "initial_contact"),
            "emails_sent": outreach_data.get("emails_sent", 0),
            "last_contact": outreach_data.get("last_contact"),
            "response": outreach_data.get("response"),
            "next_action": None,
            "next_action_date": None
        }

        # Determine next action based on stage
        stage = tracking["stage"]
        if stage == "initial_contact":
            if tracking["emails_sent"] >= 3:
                tracking["next_action"] = "Move to cold list - consider event meetup"
            else:
                tracking["next_action"] = "Send follow-up email"
                tracking["next_action_date"] = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
        elif stage == "responded":
            tracking["next_action"] = "Schedule intro call"
            tracking["next_action_date"] = datetime.now().strftime("%Y-%m-%d")
        elif stage == "meeting_scheduled":
            tracking["next_action"] = "Prepare pitch deck and due diligence docs"
        elif stage == "closed":
            tracking["next_action"] = "Negotiate terms"

        logger.info(f"Tracked outreach for {tracking['investor']}: stage={tracking['stage']}")
        return tracking

    def generate_pitch_stats(self, startup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate stats section for pitch emails."""
        return {
            "key_metrics": startup_info.get("metrics", [
                "Monthly Recurring Revenue (MRR)",
                "Customer Acquisition Cost (CAC)",
                "Lifetime Value (LTV)",
                "Month-over-Month Growth",
                "Net Promoter Score (NPS)"
            ]),
            "recommended_format": "Use specific numbers over vague claims",
            "example": f"{startup_info.get('company_name', 'We')} grew 25% MoM and reached ${startup_info.get('current_revenue', '$X')} MRR in {startup_info.get('months_traction', 'X')} months"
        }


def main():
    parser = argparse.ArgumentParser(
        description="Investor Outreach Agent - Find and reach out to investors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list-investors
  %(prog)s --search --stage seed --sector saas --location europe
  %(prog)s --investor y_combinator --info
  %(prog)s --generate-email cold_intro --investor-name "John" --company-name "MyStartup" ...
  %(prog)s --sequence --investor sequoia --company "MyStartup" --one-liner "reinventing X"
  %(prog)s --track --investor "Sequoia" --stage initial_contact --emails-sent 2
        """
    )

    parser.add_argument("--list-investors", action="store_true", help="List all investors")
    parser.add_argument("--filter-type", type=str, help="Filter investors by type (vc, accelerator, etc.)")
    parser.add_argument("--search", action="store_true", help="Search investors by criteria")
    parser.add_argument("--stage", type=str, help="Investment stage (pre-seed, seed, series_a, etc.)")
    parser.add_argument("--sector", type=str, help="Sector/industry focus")
    parser.add_argument("--location", type=str, help="Location preference")
    parser.add_argument("--investor", type=str, help="Investor key or name")
    parser.add_argument("--info", action="store_true", help="Show detailed investor info")
    parser.add_argument("--generate-email", type=str, help="Generate outreach email")
    parser.add_argument("--investor-name", type=str, help="Investor/firm name for email")
    parser.add_argument("--company-name", type=str, help="Your company name")
    parser.add_argument("--one-liner", type=str, help="One line company description")
    parser.add_argument("--founder-name", type=str, help="Your name")
    parser.add_argument("--founder-email", type=str, help="Your email")
    parser.add_argument("--amount", type=str, help="Amount you're raising")
    parser.add_argument("--sequence", action="store_true", help="Build outreach sequence")
    parser.add_argument("--track", action="store_true", help="Track outreach status")
    parser.add_argument("--stage-status", type=str, help="Current outreach stage")
    parser.add_argument("--emails-sent", type=int, help="Number of emails sent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()
    agent = InvestorOutreachAgent(verbose=args.verbose)

    try:
        # List investors
        if args.list_investors:
            investors = agent.list_investors(args.filter_type)
            if args.json:
                print(json.dumps(investors, indent=2))
            else:
                print("\n📊 INVESTORS\n" + "-" * 70)
                for inv in investors:
                    print(f"  [{inv['key']}] {inv['name']}")
                    print(f"      Type: {inv['type']} | Stage: {inv['stage']}")
                    print(f"      Check: {inv['check_size']} | Location: {inv['location']}\n")

        # Search investors
        elif args.search:
            criteria = {}
            if args.stage:
                criteria["stage"] = args.stage
            if args.sector:
                criteria["sector"] = args.sector
            if args.location:
                criteria["location"] = args.location

            results = agent.search_investors(criteria)
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"\n🔍 Found {len(results)} matching investors:\n" + "-" * 70)
                for inv in results:
                    print(f"  [{inv['name']}]")
                    print(f"      Sectors: {', '.join(inv['sectors'])}")
                    print(f"      Stage: {inv['stage']} | Check: {inv['check_size']}")
                    print(f"      Contact: {inv['contact']}\n")

        # Investor info
        elif args.investor and args.info:
            info = agent.get_investor(args.investor)
            if args.json:
                print(json.dumps(info, indent=2))
            else:
                print(f"\n👤 {info['name']}\n" + "-" * 50)
                print(f"  Type: {info['type']}")
                print(f"  Stage: {info['stage']}")
                print(f"  Check Size: {info['check_size']}")
                print(f"  Location: {info['location']}")
                print(f"  Sectors: {', '.join(info['sectors'])}")
                print(f"  Portfolio: {', '.join(info['portfolio'])}")
                print(f"  Contact: {info['contact']}")
                print(f"\n  Criteria:")
                for criterion in info['criteria']:
                    print(f"    • {criterion}")

        # Generate email
        elif args.generate_email:
            context = {}
            if args.investor_name:
                context["investor_name"] = args.investor_name
            if args.company_name:
                context["company_name"] = args.company_name
            if args.one_liner:
                context["one_liner"] = args.one_liner
            if args.founder_name:
                context["founder_name"] = args.founder_name
            if args.founder_email:
                context["founder_email"] = args.founder_email
            if args.amount:
                context["amount"] = args.amount

            # Add defaults for missing optional fields
            for key in ["unique_hook", "connection_reason", "key_metric", "metric_value",
                       "relevant_background", "years_experience", "main_insight", "use_of_funds",
                       "previous_subject", "milestone_update"]:
                if key not in context:
                    context[key] = "N/A"

            email = agent.generate_email(args.generate_email, context)
            print(f"\n📧 Generated Email ({args.generate_email}):\n")
            print("=" * 60)
            print(email)
            print("=" * 60)

        # Build sequence
        elif args.sequence and args.investor:
            if not args.company_name:
                print("Error: --company-name is required for --sequence")
                sys.exit(1)

            startup_info = {"company_name": args.company_name}
            if args.one_liner:
                startup_info["one_liner"] = args.one_liner

            sequence = agent.build_outreach_sequence(args.investor, startup_info)
            if args.json:
                print(json.dumps(sequence, indent=2))
            else:
                print(f"\n📅 Outreach Sequence for {args.investor}:\n" + "-" * 50)
                for step in sequence:
                    print(f"\n  Day {step['day']}: {step['action'].replace('_', ' ').title()}")
                    print(f"  Type: {step['type']}")
                    print(f"  Subject: {step['subject']}")

        # Track outreach
        elif args.track:
            if not args.investor:
                print("Error: --investor is required for --track")
                sys.exit(1)

            tracking_data = {
                "investor": args.investor,
                "company": args.company_name or "Unknown",
                "stage": args.stage_status or "initial_contact",
                "emails_sent": args.emails_sent or 0
            }
            result = agent.track_outreach(tracking_data)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n📊 Outreach Tracking\n" + "-" * 50)
                print(f"  Investor: {result['investor']}")
                print(f"  Stage: {result['stage']}")
                print(f"  Emails Sent: {result['emails_sent']}")
                if result['next_action']:
                    print(f"\n  Next Action: {result['next_action']}")
                    if result['next_action_date']:
                        print(f"  Date: {result['next_action_date']}")

        else:
            parser.print_help()

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error")
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
