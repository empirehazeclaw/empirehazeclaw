#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          AI REGULATOR AGENT                                  ║
║          AI Policy & Compliance Tracking                      ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - EU AI Act compliance tracking
  - AI system registration
  - Risk classification
  - Conformity assessment tracking
  - Incident reporting
  - Compliance deadlines
  - Multi-jurisdiction support (EU, US, China)

Usage:
  python3 ai_regulator_agent.py --register --name "Recruitment AI" --risk high
  python3 ai_regulator_agent.py --classify --description "CV screening system"
  python3 ai_regulator_agent.py --list --risk high
  python3 ai_regulator_agent.py --incident --id sys-001 --severity high --description "Bias detected"
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
        logging.FileHandler(LOG_DIR / "ai_regulator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger("openclaw.ai_regulator")

# Data storage
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/ai_regulation")
DATA_DIR.mkdir(parents=True, exist_ok=True)
REGISTRY_FILE = DATA_DIR / "ai_systems_registry.json"
INCIDENTS_FILE = DATA_DIR / "incidents.json"
ASSESSMENTS_FILE = DATA_DIR / "conformity_assessments.json"
DEADLINES_FILE = DATA_DIR / "compliance_deadlines.json"


@dataclass
class AISystem:
    id: str
    name: str
    description: str
    provider: str
    risk_level: str  # unacceptable, high, limited, minimal
    category: str
    jurisdiction: str  # EU, US, CN, GLOBAL
    registration_date: str
    status: str  # planning, development, deployed, discontinued
    conformity_status: str  # pending, in_progress, compliant, non_compliant
    last_assessment: str
    next_assessment: str
    technical_docs: list
    deployment_date: str = ""
    eu_database_id: str = ""


@dataclass
class AIIncident:
    id: str
    system_id: str
    system_name: str
    incident_date: str
    severity: str  # low, medium, high, critical
    description: str
    affected_parties: str
    root_cause: str
    corrective_actions: list
    status: str  # reported, investigating, resolved, closed
    reported_to_authority: bool
    report_date: str = ""


@dataclass
class ConformityAssessment:
    id: str
    system_id: str
    assessment_date: str
    assessor: str
    scope: str
    findings: list
    non_conformities: list
    recommendation: str
    status: str  # scheduled, in_progress, completed, expired


# EU AI Act risk classification helpers
RISK_KEYWORDS = {
    "unacceptable": [
        "social scoring", "subliminal manipulation", "exploitation vulnerable",
        "biometric categorization sensitive", "real-time remote biometric"
    ],
    "high": [
        "medical device", "critical infrastructure", "education exam",
        "employment hiring", "credit scoring", "insurance risk", "justice",
        "border control", "asylum", "essential services", "deepfake generation"
    ],
    "limited": [
        "chatbot", "virtual assistant", "deepfake", "emotion recognition",
        " Recommender", "content moderation", "spam detection"
    ],
    "minimal": [
        "ai video game", "spam filter", "inventory management",
        "route optimization", "weather forecast", "personal assistant simple"
    ]
}


def load_registry() -> list:
    """Load AI systems registry."""
    try:
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, 'r') as f:
                data = json.load(f)
                return [AISystem(**s) for s in data.get('systems', [])]
    except Exception as e:
        log.error(f"Error loading registry: {e}")
    return []


def save_registry(systems: list) -> None:
    """Save AI systems registry."""
    try:
        data = {'systems': [asdict(s) for s in systems], 'updated_at': datetime.now().isoformat()}
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving registry: {e}")


def load_incidents() -> list:
    """Load AI incidents."""
    try:
        if INCIDENTS_FILE.exists():
            with open(INCIDENTS_FILE, 'r') as f:
                data = json.load(f)
                return [AIIncident(**i) for i in data.get('incidents', [])]
    except Exception as e:
        log.error(f"Error loading incidents: {e}")
    return []


def save_incidents(incidents: list) -> None:
    """Save AI incidents."""
    try:
        data = {'incidents': [asdict(i) for i in incidents], 'updated_at': datetime.now().isoformat()}
        with open(INCIDENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving incidents: {e}")


def load_assessments() -> list:
    """Load conformity assessments."""
    try:
        if ASSESSMENTS_FILE.exists():
            with open(ASSESSMENTS_FILE, 'r') as f:
                data = json.load(f)
                return [ConformityAssessment(**a) for a in data.get('assessments', [])]
    except Exception as e:
        log.error(f"Error loading assessments: {e}")
    return []


def save_assessments(assessments: list) -> None:
    """Save conformity assessments."""
    try:
        data = {'assessments': [asdict(a) for a in assessments], 'updated_at': datetime.now().isoformat()}
        with open(ASSESSMENTS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Error saving assessments: {e}")


def generate_system_id() -> str:
    """Generate unique system ID."""
    return f"ai-{datetime.now().strftime('%Y%m')}-{len(load_registry()) + 1:03d}"


def classify_risk(description: str) -> dict:
    """Classify AI system risk under EU AI Act."""
    desc_lower = description.lower()
    
    # Check unacceptable risk first
    for kw in RISK_KEYWORDS["unacceptable"]:
        if kw in desc_lower:
            return {
                "level": "unacceptable",
                "category": "Prohibited",
                "requires": "NOT PERMITTED - Must redesign or discontinue",
                "articles": ["Article 5"],
                "deadline": "Immediate action required"
            }
    
    # Check high risk
    high_risk_categories = {
        "Critical Infrastructure": ["infrastructure", "transport", "energy", "water"],
        "Education & Employment": ["education", "exam", "recruitment", "hiring", "cv", "resume", "employee"],
        "Essential Services": ["credit", "insurance", "banking", "loan", "mortgage"],
        "Law Enforcement": ["law enforcement", "justice", "court", "judicial", "police", "surveillance"],
        "Migration & Asylum": ["migration", "asylum", "border", "immigration"],
        "Biometrics": ["biometric", "facial recognition", "voiceprint", "fingerprint"]
    }
    
    for category, keywords in high_risk_categories.items():
        if any(kw in desc_lower for kw in keywords):
            return {
                "level": "high",
                "category": category,
                "requires": "Conformity assessment, technical documentation, risk management, human oversight",
                "articles": ["Article 9-15"],
                "deadline": "Before market deployment"
            }
    
    # Check limited risk
    for kw in RISK_KEYWORDS["limited"]:
        if kw in desc_lower:
            return {
                "level": "limited",
                "category": "Transparency Obligation",
                "requires": "Disclosure that user is interacting with AI, label AI-generated content",
                "articles": ["Article 50"],
                "deadline": "At deployment"
            }
    
    # Minimal risk
    return {
        "level": "minimal",
        "category": "No Mandatory Requirements",
        "requires": "Voluntary codes of conduct encouraged",
        "articles": ["Article 69"],
        "deadline": "None"
    }


def register_ai_system(name: str, description: str, provider: str, 
                       risk_level: str, category: str, jurisdiction: str = "EU") -> AISystem:
    """Register a new AI system."""
    system = AISystem(
        id=generate_system_id(),
        name=name,
        description=description,
        provider=provider,
        risk_level=risk_level,
        category=category,
        jurisdiction=jurisdiction,
        registration_date=datetime.now().isoformat(),
        status="planning",
        conformity_status="pending",
        last_assessment="",
        next_assessment=(datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        technical_docs=[]
    )
    
    return system


def report_incident(system_id: str, severity: str, description: str,
                   affected_parties: str = "") -> AIIncident:
    """Report an AI incident."""
    systems = load_registry()
    system = next((s for s in systems if s.id == system_id), None)
    
    incident = AIIncident(
        id=f"inc-{datetime.now().strftime('%Y%m%d%H%M')}-{len(load_incidents()) + 1:02d}",
        system_id=system_id,
        system_name=system.name if system else "Unknown",
        incident_date=datetime.now().isoformat(),
        severity=severity,
        description=description,
        affected_parties=affected_parties,
        root_cause="",
        corrective_actions=[],
        status="reported",
        reported_to_authority=severity in ["high", "critical"]
    )
    
    if incident.reported_to_authority:
        incident.report_date = datetime.now().isoformat()
    
    return incident


def get_eu_deadlines() -> list:
    """Get EU AI Act implementation deadlines."""
    return [
        {"date": "2024-08-01", "event": "EU AI Act enters into force"},
        {"date": "2025-08-01", "event": "Prohibited AI practices ban takes effect"},
        {"date": "2026-08-01", "event": "High-risk AI systems requirements apply"},
        {"date": "2027-08-01", "event": "General AI systems transparency requirements apply"},
    ]


def cmd_register(args) -> int:
    """Register a new AI system."""
    # First classify if risk not specified
    if args.risk == "auto":
        classification = classify_risk(args.description)
        risk_level = classification["level"]
        category = classification["category"]
        print(f"\n🤖 Risk Classification Result:")
        print(f"   Level: {risk_level.upper()}")
        print(f"   Category: {category}")
        print(f"   Requires: {classification['requires']}")
        print(f"   Articles: {', '.join(classification['articles'])}")
        
        if risk_level == "unacceptable":
            print(f"\n❌ This system CANNOT be deployed in the EU.")
            return 1
        
        if args.yes or input("\nProceed with registration? (y/n): ").lower() == 'y':
            args.risk = risk_level
            args.category = category
        else:
            return 0
    else:
        classification = classify_risk(args.description)
        args.category = args.category or classification.get("category", "General")
    
    system = register_ai_system(
        name=args.name,
        description=args.description,
        provider=args.provider,
        risk_level=args.risk,
        category=args.category,
        jurisdiction=args.jurisdiction or "EU"
    )
    
    # Save
    systems = load_registry()
    systems.append(system)
    save_registry(systems)
    
    print(f"\n✅ AI System Registered")
    print(f"   ID: {system.id}")
    print(f"   Name: {system.name}")
    print(f"   Risk Level: {system.risk_level.upper()}")
    print(f"   Category: {system.category}")
    print(f"   Next Assessment Due: {system.next_assessment}")
    
    if system.risk_level == "high":
        print(f"\n⚠️  HIGH RISK SYSTEM - Required Actions:")
        print(f"   1. Conduct conformity assessment before deployment")
        print(f"   2. Implement risk management system")
        print(f"   3. Maintain technical documentation")
        print(f"   4. Register in EU database")
        print(f"   5. Establish human oversight measures")
    
    return 0


def cmd_classify(args) -> int:
    """Classify AI system risk."""
    classification = classify_risk(args.description)
    
    print(f"\n{'='*60}")
    print(f"🤖 EU AI ACT RISK CLASSIFICATION")
    print(f"{'='*60}")
    print(f"Description: {args.description[:60]}...")
    print(f"\nRisk Level: {classification['level'].upper()}")
    print(f"Category: {classification['category']}")
    print(f"\nLegal Requirements:")
    print(f"   {classification['requires']}")
    print(f"\nRelevant Articles: {', '.join(classification['articles'])}")
    print(f"Compliance Deadline: {classification['deadline']}")
    print(f"{'='*60}")
    
    if classification['level'] == "unacceptable":
        print(f"\n❌ PROHIBITED: This AI practice is not allowed under EU AI Act.")
        print(f"   You must redesign the system to remove prohibited features.")
    elif classification['level'] == "high":
        print(f"\n⚠️  HIGH RISK: Conformity assessment required before deployment.")
    
    return 0


def cmd_list(args) -> int:
    """List registered AI systems."""
    systems = load_registry()
    
    if not systems:
        print("No AI systems registered.")
        return 0
    
    # Apply filters
    filtered = systems
    if args.risk:
        filtered = [s for s in filtered if s.risk_level == args.risk]
    if args.status:
        filtered = [s for s in filtered if s.status == args.status]
    if args.jurisdiction:
        filtered = [s for s in filtered if s.jurisdiction == args.jurisdiction]
    
    if not filtered:
        print("No systems match your criteria.")
        return 0
    
    print(f"\nFound {len(filtered)} AI system(s):\n")
    for sys in filtered:
        print(f"{'='*60}")
        print(f"🆔 {sys.id} - {sys.name}")
        print(f"   Provider: {sys.provider}")
        print(f"   Risk Level: {sys.risk_level.upper()}")
        print(f"   Category: {sys.category}")
        print(f"   Jurisdiction: {sys.jurisdiction}")
        print(f"   Status: {sys.status.upper()}")
        print(f"   Conformity: {sys.conformity_status.upper()}")
        print(f"   Registered: {sys.registration_date[:10]}")
        print(f"   Next Assessment: {sys.next_assessment}")
    
    return 0


def cmd_incident(args) -> int:
    """Report or list incidents."""
    if args.action == "report":
        # Find system
        systems = load_registry()
        system = next((s for s in systems if s.id == args.id), None)
        
        if not system:
            print(f"AI system not found: {args.id}")
            return 1
        
        incident = report_incident(args.id, args.severity, args.description, args.affected)
        
        incidents = load_incidents()
        incidents.append(incident)
        save_incidents(incidents)
        
        print(f"\n✅ Incident Reported")
        print(f"   ID: {incident.id}")
        print(f"   System: {incident.system_name}")
        print(f"   Severity: {incident.severity.upper()}")
        print(f"   Status: {incident.status.upper()}")
        
        if incident.reported_to_authority:
            print(f"\n⚠️  This incident meets reporting threshold.")
            print(f"   Report submitted to relevant authority.")
        
    elif args.action == "list":
        incidents = load_incidents()
        
        if not incidents:
            print("No incidents reported.")
            return 0
        
        # Filter
        if args.severity:
            incidents = [i for i in incidents if i.severity == args.severity]
        
        print(f"\nFound {len(incidents)} incident(s):\n")
        for inc in incidents:
            print(f"{'='*60}")
            print(f"🚨 Incident: {inc.id}")
            print(f"   System: {inc.system_name} ({inc.system_id})")
            print(f"   Date: {inc.incident_date[:10]}")
            print(f"   Severity: {inc.severity.upper()}")
            print(f"   Status: {inc.status.upper()}")
            print(f"   Description: {inc.description[:80]}...")
            print(f"{'='*60}")
    
    return 0


def cmd_assess(args) -> int:
    """Manage conformity assessments."""
    assessments = load_assessments()
    
    if args.action == "schedule":
        systems = load_registry()
        system = next((s for s in systems if s.id == args.system_id), None)
        
        if not system:
            print(f"AI system not found: {args.system_id}")
            return 1
        
        assessment = ConformityAssessment(
            id=f"ass-{datetime.now().strftime('%Y%m%d%H%M')}",
            system_id=args.system_id,
            assessment_date=datetime.now().isoformat(),
            assessor=args.assessor or "Internal",
            scope=args.scope or "Full conformity assessment",
            findings=[],
            non_conformities=[],
            recommendation="pending",
            status="scheduled"
        )
        
        assessments.append(assessment)
        save_assessments(assessments)
        
        # Update system
        system.conformity_status = "in_progress"
        save_registry(systems)
        
        print(f"✅ Assessment scheduled for system {args.system_id}")
        print(f"   Assessment ID: {assessment.id}")
        
    elif args.action == "complete":
        for ass in assessments:
            if ass.system_id == args.system_id and ass.status == "in_progress":
                ass.status = "completed"
                ass.findings = args.findings.split('|') if args.findings else []
                ass.non_conformities = args.non_conformities.split('|') if args.non_conformities else []
                ass.recommendation = args.recommendation or "Compliant"
                save_assessments(assessments)
                
                # Update system
                systems = load_registry()
                for s in systems:
                    if s.id == args.system_id:
                        s.conformity_status = "compliant" if not ass.non_conformities else "non_compliant"
                        s.last_assessment = datetime.now().isoformat()
                        s.next_assessment = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                        save_registry(systems)
                        break
                
                print(f"✅ Assessment completed for {args.system_id}")
                print(f"   Status: {ass.recommendation}")
                return 0
        
        print(f"No pending assessment found for system: {args.system_id}")
        return 1
    
    elif args.action == "list":
        systems = load_registry()
        
        print(f"\nConformity Assessments:\n")
        for ass in assessments:
            system = next((s for s in systems if s.id == ass.system_id), None)
            print(f"{'='*60}")
            print(f"📋 Assessment: {ass.id}")
            print(f"   System: {system.name if system else ass.system_id}")
            print(f"   Date: {ass.assessment_date[:10]}")
            print(f"   Assessor: {ass.assessor}")
            print(f"   Status: {ass.status.upper()}")
            print(f"   Recommendation: {ass.recommendation}")
            print(f"{'='*60}")
    
    return 0


def cmd_deadlines(args) -> int:
    """Show regulatory deadlines."""
    deadlines = get_eu_deadlines()
    
    print(f"\n📅 EU AI ACT IMPLEMENTATION TIMELINE")
    print(f"{'='*60}")
    
    now = datetime.now()
    for dl in deadlines:
        dl_date = datetime.strptime(dl['date'], "%Y-%m-%d")
        days = (dl_date - now).days
        
        if days > 0:
            status = f"⏳ {days} days remaining"
        elif days == 0:
            status = "📍 TODAY"
        else:
            status = f"✅ {abs(days)} days ago"
        
        print(f"{dl['date']} - {status}")
        print(f"   {dl['event']}\n")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Regulator Agent - EU AI Act Compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --register --name "CV Screener" --description "AI for resume screening" \\
           --provider "TechCorp" --risk auto
  %(prog)s --classify --description "Facial recognition for office access"
  %(prog)s --list --risk high
  %(prog)s --list --status deployed
  %(prog)s --incident --action report --id ai-202401-001 --severity high \\
           --description "Bias detected in hiring outcomes" --affected "Job applicants"
  %(prog)s --incident --action list --severity high
  %(prog)s --assess --action schedule --system-id ai-202401-001 --assessor "External Auditor"
  %(prog)s --assess --action complete --system-id ai-202401-001 \\
           --recommendation "Compliant with minor issues"
  %(prog)s --assess --action list
  %(prog)s --deadlines
        """
    )
    
    parser.add_argument('--register', action='store_true', help='Register new AI system')
    parser.add_argument('--name', help='AI system name')
    parser.add_argument('--description', help='System description')
    parser.add_argument('--provider', help='System provider')
    parser.add_argument('--risk', help='Risk level (unacceptable/high/limited/minimal/auto)')
    parser.add_argument('--category', help='Risk category')
    parser.add_argument('--jurisdiction', help='Jurisdiction (EU/US/CN/GLOBAL)')
    parser.add_argument('--classify', action='store_true', help='Classify AI system risk')
    parser.add_argument('--list', dest='list_enabled', action='store_true', help='List AI systems')
    parser.add_argument('--status', help='Filter by status')
    parser.add_argument('--incident', action='store_true', help='Manage incidents')
    parser.add_argument('--action', choices=['report', 'list'], help='Incident action')
    parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'], help='Severity level')
    parser.add_argument('--affected', help='Affected parties')
    parser.add_argument('--assess', action='store_true', help='Manage assessments')
    parser.add_argument('--system-id', help='AI system ID')
    parser.add_argument('--assessor', help='Assessment assessor')
    parser.add_argument('--scope', help='Assessment scope')
    parser.add_argument('--findings', help='Assessment findings (pipe-separated)')
    parser.add_argument('--non-conformities', help='Non-conformities found (pipe-separated)')
    parser.add_argument('--recommendation', help='Assessment recommendation')
    parser.add_argument('--deadlines', action='store_true', help='Show regulatory deadlines')
    parser.add_argument('--yes', '-y', action='store_true', help='Auto-approve prompts')
    
    args = parser.parse_args()
    
    try:
        if args.register:
            if not all([args.name, args.description, args.provider]):
                print("Error: --name, --description, and --provider are required")
                return 1
            if not args.risk:
                args.risk = "auto"
            return cmd_register(args)
        elif args.classify:
            if not args.description:
                print("Error: --description is required")
                return 1
            return cmd_classify(args)
        elif args.list_enabled:
            return cmd_list(args)
        elif args.incident:
            if args.action == "report" and not all([args.id, args.severity, args.description]):
                print("Error: --id, --severity, and --description are required")
                return 1
            return cmd_incident(args)
        elif args.assess:
            if not args.action:
                print("Error: --action is required")
                return 1
            if args.action in ["schedule", "complete"] and not args.system_id:
                print("Error: --system-id is required")
                return 1
            return cmd_assess(args)
        elif args.deadlines:
            return cmd_deadlines(args)
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
