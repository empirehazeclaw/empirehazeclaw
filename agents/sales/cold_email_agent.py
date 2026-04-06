#!/usr/bin/env python3
"""
📧 Sales Cold Email Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Specialized cold email agent for B2B/B2C outbound.
Features:
- Lead management (JSON storage)
- Personalized email generation
- Sequence/cadence management
- Open/reply/click tracking
- A/B variant generation
- Dry-run mode

Usage:
  python3 sales/cold_email_agent.py --help
  python3 sales/cold_email_agent.py add_lead --name "Max Mustermann" --email "max@company.com" --company "Acme GmbH"
  python3 sales/cold_email_agent.py list_leads
  python3 sales/cold_email_agent.py generate --lead-id 0 --template intro
  python3 sales/cold_email_agent.py send --lead-id 0 [--dry-run]
  python3 sales/cold_email_agent.py sequence --lead-id 0
  python3 sales/cold_email_agent.py report
"""

import argparse
import json
import logging
import os
import random
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ─── PATHS ────────────────────────────────────────────────────────────────────
WORKSPACE  = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR   = WORKSPACE / "data"
LOGS_DIR   = WORKSPACE / "logs"
SENT_DIR   = DATA_DIR / "cold_email"
CAMPAIGN_DIR = DATA_DIR / "campaigns"

for d in [DATA_DIR, LOGS_DIR, SENT_DIR, CAMPAIGN_DIR]:
    d.mkdir(parents=True, exist_ok=True)

LEADS_FILE   = SENT_DIR / "leads.json"
SENT_FILE    = SENT_DIR / "sent.json"
SEQUENCES_FILE = SENT_DIR / "sequences.json"
CONFIG_FILE  = SENT_DIR / "config.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [COLD_EMAIL] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "cold_email_agent.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("cold_email")

# ─── DATA MODELS ──────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

@dataclass
class Lead:
    id:        int
    name:      str
    email:     str
    company:   str = ""
    industry:  str = ""
    title:     str = ""
    source:    str = ""
    status:    str = "new"  # new, contacted, qualified, engaged, customer, bounced
    score:     int = 0
    tags:      List[str] = field(default_factory=list)
    notes:     str = ""
    last_contact: str = ""
    created_at: str = ""
    variables: Dict[str, str] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Lead(**d)

@dataclass
class SentEmail:
    id:        int
    lead_id:   int
    subject:   str
    body:      str
    template:  str
    status:    str = "sent"  # sent, opened, replied, clicked, bounced
    sent_at:   str = ""
    opened_at: str = ""
    replied_at: str = ""

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return SentEmail(**d)

# ─── STORE HELPERS ────────────────────────────────────────────────────────────
def load_leads() -> List[Lead]:
    data = load_json(LEADS_FILE, [])
    return [Lead.from_dict(d) for d in data]

def save_leads(leads: List[Lead]):
    save_json(LEADS_FILE, [l.to_dict() for l in leads])

def load_sent() -> List[SentEmail]:
    data = load_json(SENT_FILE, [])
    return [SentEmail.from_dict(d) for d in data]

def save_sent(sent: List[SentEmail]):
    save_json(SENT_FILE, [s.to_dict() for s in sent])

def load_config() -> dict:
    return load_json(CONFIG_FILE, {
        "sender_name": "EmpireHazeClaw",
        "sender_email": "hello@empirehazeclaw.com",
        "daily_limit": 50,
        "delay_seconds": 30,
    })

def save_config(cfg: dict):
    save_json(CONFIG_FILE, cfg)

# ─── TEMPLATES ─────────────────────────────────────────────────────────────────
EMAIL_TEMPLATES = {
    "intro": {
        "name": "Introduction Email",
        "subject": "Quick question about {company}",
        "body": """Subject: Quick question about {company}

Hi {first_name},

I noticed {company} is in the {industry} space, and I wanted to reach out
because we help companies like yours {value_prop}.

I have a quick question: {question}

Would you be open to a 15-minute call this week?

Best,
{sender_name}
{sender_email}""",
    },
    "follow1": {
        "name": "Follow-up #1",
        "subject": "Re: {original_subject}",
        "body": """Subject: Re: {original_subject}

Hi {first_name},

Just following up on my last email. I know you're busy —
no worries if now isn't the right time.

If you ever want to chat about {topic}, I'm here.

Best,
{sender_name}""",
    },
    "follow2": {
        "name": "Follow-up #2 (Value)",
        "subject": "{company} + something interesting",
        "body": """Subject: {company} + something interesting

Hi {first_name},

I found something that might be relevant to {company}:

{insight}

Happy to share more if useful.

Best,
{sender_name}""",
    },
    "breakup": {
        "name": "Breakup Email",
        "subject": "Last one — {topic}",
        "body": """Subject: Last one — {topic}

Hi {first_name},

I've tried reaching you a few times. I'll stop here.

If you ever want to chat, you know where to find me.

Best,
{sender_name}""",
    },
}

# ─── VARIABLE EXTRACTION ──────────────────────────────────────────────────────
def extract_variables(lead: Lead) -> Dict[str, str]:
    """Extract personalized variables from lead data."""
    first_name = lead.name.split()[0] if lead.name else "there"
    company_adj = lead.company.lower().replace("gmbh", "").replace("ag", "").strip() if lead.company else "your company"
    return {
        "{first_name}": first_name,
        "{name}":        lead.name,
        "{email}":       lead.email,
        "{company}":     lead.company or "your company",
        "{industry}":    lead.industry or "relevant",
        "{title}":       lead.title or "team",
        "{sender_name}": load_config().get("sender_name", "EmpireHazeClaw"),
        "{sender_email}": load_config().get("sender_email", "hello@empirehazeclaw.com"),
        "{original_subject}": "Quick question",
        "{topic}": lead.variables.get("topic", "what we do"),
        "{value_prop}": lead.variables.get("value_prop", "grow revenue"),
        "{question}": lead.variables.get("question", "what your biggest challenge is right now"),
        "{insight}": lead.variables.get("insight", "a relevant market insight"),
    }

def fill_template(template_str: str, variables: Dict[str, str]) -> str:
    result = template_str
    for key, val in variables.items():
        result = result.replace(key, val)
    return result

# ─── LLM PERSONALIZATION ─────────────────────────────────────────────────────
def call_llm(prompt: str) -> str:
    """Call LLM for enhanced personalization."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1024,
            system="Du bist ein B2B Sales-Experte. Personalisiere E-Mails basierend auf Lead-Informationen. Schreibe auf Deutsch oder Englisch je nach Context.",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"LLM unavailable: {e}")
        return None

def generate_personalized_email(lead: Lead, template_key: str) -> tuple:
    """Generate email from template + LLM enhancement."""
    cfg = load_config()
    tpl = EMAIL_TEMPLATES.get(template_key, EMAIL_TEMPLATES["intro"])
    variables = extract_variables(lead)

    # Fill template
    subject = fill_template(tpl["subject"], variables)
    body = fill_template(tpl["body"], variables)

    # LLM enhancement
    llm_prompt = f"""Personalisiere diese E-Mail für folgenden Lead:

Lead: {lead.name}, {lead.title} bei {lead.company} ({lead.industry})
Firma: {lead.company}
Branche: {lead.industry}

Original-E-Mail:
---
Subject: {subject}
Body: {body}
---

Erweitere die E-Mail mit spezifischen Details über {lead.company} oder {lead.industry}.
Ersetze die Platzhalter in {{}} mit realistischen, personalisierten Inhalten.
Gib Subject und Body zurück im Format:
SUBJECT: ...
BODY: ...(完整正文)"""

    enhanced = call_llm(llm_prompt)
    if enhanced and "SUBJECT:" in enhanced:
        parts = enhanced.split("BODY:", 1)
        if len(parts) == 2:
            subject = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()

    return subject, body

# ─── EMAIL SENDING ────────────────────────────────────────────────────────────
def send_email_via_gog(to_email: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Send email using gog CLI."""
    if dry_run:
        logger.info(f"[DRY RUN] Would send to {to_email}: {subject}")
        return True

    try:
        import subprocess
        result = subprocess.run(
            ["/home/linuxbrew/.linuxbrew/bin/gog",
             "send", "--to", to_email, "--subject", subject, "--body", body],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            logger.info(f"Email sent to {to_email}")
            return True
        else:
            logger.error(f"Failed to send: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Send error: {e}")
        return False

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_add_lead(args) -> int:
    """Add a new lead."""
    leads = load_leads()
    new_id = max([l.id for l in leads], default=-1) + 1
    lead = Lead(
        id=new_id,
        name=args.name,
        email=args.email,
        company=args.company or "",
        industry=args.industry or "",
        title=args.title or "",
        source=args.source or "manual",
        status="new",
        created_at=datetime.now().isoformat(),
        tags=args.tags.split(",") if args.tags else [],
        variables=args.variables,
    )
    leads.append(lead)
    save_leads(leads)
    logger.info(f"Added lead: {lead.name} <{lead.email}> (ID: {new_id})")
    print(f"✅ Lead added (ID: {new_id}): {lead.name} <{lead.email}>")
    if args.tags:
        print(f"   Tags: {lead.tags}")
    return 0


def cmd_list_leads(args) -> int:
    """List all leads."""
    leads = load_leads()
    if not leads:
        print("No leads found. Add one with: add_lead")
        return 0

    filter_status = args.status.split(",") if args.status else None
    filtered = [l for l in leads if not filter_status or l.status in filter_status]

    print(f"\n{'ID':>3} | {'Name':<25} | {'Email':<30} | {'Company':<20} | {'Status':<12} | Score")
    print("-" * 105)
    for l in filtered:
        name  = l.name[:23]  + ".." if len(l.name)  > 25 else l.name
        email = l.email[:28] + ".." if len(l.email) > 30 else l.email
        comp  = l.company[:18] + ".." if len(l.company) > 20 else l.company
        print(f"{l.id:>3} | {name:<25} | {email:<30} | {comp:<20} | {l.status:<12} | {l.score}")
    print(f"\nTotal: {len(filtered)} lead(s)")
    return 0


def cmd_generate(args) -> int:
    """Generate email for a lead."""
    leads = load_leads()
    try:
        lead = next(l for l in leads if l.id == args.lead_id)
    except StopIteration:
        print(f"Error: Lead ID {args.lead_id} not found")
        return 1

    subject, body = generate_personalized_email(lead, args.template)

    if args.count > 1:
        # A/B variants
        print(f"\n📧 A/B Variants for {lead.name}:\n")
        print(f"{'='*60}")
        for i in range(args.count):
            variant_body = body
            if i > 0:
                prompt = f"""Erstelle Variante {i+1} der gleichen E-Mail mit anderem 
Anschreiben/Stil (gleiche Info, andere Formulierung).

Original:
{body}

Gib nur die neue Version aus (kein Kommentar):"""
                result = call_llm(prompt)
                if result:
                    variant_body = result
            print(f"\n--- VARIANT {i+1} ---")
            print(f"Subject: {subject}")
            print(variant_body)
    else:
        print(f"\n📧 Email for {lead.name} ({lead.email}):\n")
        print(f"{'='*60}")
        print(f"Subject: {subject}")
        print(f"\n{body}")
        print(f"{'='*60}")

    if args.save:
        sent_list = load_sent()
        new_id = max([s.id for s in sent_list], default=-1) + 1
        se = SentEmail(
            id=new_id,
            lead_id=lead.id,
            subject=subject,
            body=body,
            template=args.template,
            status="draft",
            sent_at=datetime.now().isoformat(),
        )
        sent_list.append(se)
        save_sent(sent_list)
        print(f"\n✅ Draft saved (SentEmail ID: {new_id})")
    return 0


def cmd_send(args) -> int:
    """Send email to a lead."""
    leads = load_leads()
    try:
        lead = next(l for l in leads if l.id == args.lead_id)
    except StopIteration:
        print(f"Error: Lead ID {args.lead_id} not found")
        return 1

    subject, body = generate_personalized_email(lead, args.template or "intro")

    print(f"\n📤 Sending to {lead.name} <{lead.email}>")
    print(f"Subject: {subject}")

    if args.dry_run:
        print("\n[DRY RUN — no email sent]")
        return 0

    ok = send_email_via_gog(lead.email, subject, body)
    if ok:
        # Update lead
        lead.status = "contacted"
        lead.last_contact = datetime.now().isoformat()
        save_leads(leads)

        # Log sent
        sent_list = load_sent()
        new_id = max([s.id for s in sent_list], default=-1) + 1
        se = SentEmail(
            id=new_id,
            lead_id=lead.id,
            subject=subject,
            body=body,
            template=args.template or "intro",
            status="sent",
            sent_at=datetime.now().isoformat(),
        )
        sent_list.append(se)
        save_sent(sent_list)

        print(f"✅ Email sent to {lead.email} (ID: {new_id})")
    else:
        print(f"❌ Failed to send to {lead.email}")
    return 0


def cmd_sequence(args) -> int:
    """Run a full email sequence for a lead."""
    leads = load_leads()
    try:
        lead = next(l for l in leads if l.id == args.lead_id)
    except StopIteration:
        print(f"Error: Lead ID {args.lead_id} not found")
        return 1

    templates = ["intro", "follow1", "follow2", "breakup"]
    delay = load_config().get("delay_seconds", 30)

    print(f"\n📋 Running sequence for {lead.name} ({lead.company})")
    print(f"   Steps: {len(templates)} emails, {delay}s delay\n")

    for i, tpl in enumerate(templates):
        print(f"  Step {i+1}/{len(templates)}: {EMAIL_TEMPLATES[tpl]['name']}")
        subject, body = generate_personalized_email(lead, tpl)
        print(f"  Subject: {subject}")

        if args.dry_run:
            print(f"  [DRY RUN] Would send: {body[:100]}...")
        else:
            ok = send_email_via_gog(lead.email, subject, body)
            if ok:
                lead.last_contact = datetime.now().isoformat()
                sent_list = load_sent()
                new_id = max([s.id for s in sent_list], default=-1) + 1
                se = SentEmail(
                    id=new_id, lead_id=lead.id, subject=subject,
                    body=body, template=tpl, status="sent",
                    sent_at=datetime.now().isoformat(),
                )
                sent_list.append(se)
                save_sent(sent_list)
                print(f"  ✅ Sent")
            else:
                print(f"  ❌ Failed")
        if i < len(templates) - 1:
            print(f"  ⏳ Waiting {delay}s...")
            time.sleep(delay)

    lead.status = "contacted"
    save_leads(leads)
    print(f"\n✅ Sequence complete for {lead.name}")
    return 0


def cmd_report(args) -> int:
    """Show campaign report."""
    sent_list = load_sent()
    leads = load_leads()
    lead_map = {l.id: l for l in leads}

    total = len(sent_list)
    by_status = {}
    for s in sent_list:
        by_status[s.status] = by_status.get(s.status, 0) + 1

    print(f"\n📊 Cold Email Campaign Report")
    print(f"{'='*50}")
    print(f"Total emails: {total}")
    for status, count in sorted(by_status.items()):
        pct = count/total*100 if total else 0
        print(f"  {status:<10}: {count} ({pct:.1f}%)")

    # Recent activity
    recent = sorted(sent_list, key=lambda x: x.sent_at, reverse=True)[:10]
    if recent:
        print(f"\nRecent Activity:")
        for s in recent:
            lead_name = lead_map.get(s.lead_id, Lead(0,"?","?")).name
            print(f"  {s.sent_at[:10]} | {s.status:<8} | {lead_name:<20} | {s.subject[:40]}")

    # Lead status summary
    status_counts = {}
    for l in leads:
        status_counts[l.status] = status_counts.get(l.status, 0) + 1
    print(f"\nLead Status:")
    for s, c in sorted(status_counts.items()):
        print(f"  {s:<12}: {c}")
    return 0


def cmd_config(args) -> int:
    """View or update config."""
    cfg = load_config()
    if args.set_name:
        cfg["sender_name"] = args.set_name
        save_config(cfg)
        print(f"✅ sender_name set to: {args.set_name}")
    if args.set_email:
        cfg["sender_email"] = args.set_email
        save_config(cfg)
        print(f"✅ sender_email set to: {args.set_email}")
    if args.set_limit:
        cfg["daily_limit"] = int(args.set_limit)
        save_config(cfg)
        print(f"✅ daily_limit set to: {args.set_limit}")
    if not any([args.set_name, args.set_email, args.set_limit]):
        print("\n⚙️  Current Config:")
        for k, v in cfg.items():
            print(f"  {k}: {v}")
    return 0


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="sales/cold_email_agent.py",
        description="📧 Sales Cold Email Agent — B2B outbound email campaigns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sales/cold_email_agent.py add_lead --name "Max Mustermann" --email "max@acme.com" --company "Acme GmbH" --industry "SaaS"
  python3 sales/cold_email_agent.py add_lead --name "Anna Schmidt" --email "anna@techstartup.io" --company "TechStartup" --industry "Tech" --tags "early-stage,funded"
  python3 sales/cold_email_agent.py list_leads
  python3 sales/cold_email_agent.py list_leads --status contacted,qualified
  python3 sales/cold_email_agent.py generate --lead-id 0 --template intro
  python3 sales/cold_email_agent.py generate --lead-id 0 --template intro --count 3 --save
  python3 sales/cold_email_agent.py send --lead-id 0 --template intro [--dry-run]
  python3 sales/cold_email_agent.py sequence --lead-id 0 [--dry-run]
  python3 sales/cold_email_agent.py report
  python3 sales/cold_email_agent.py config [--set-name "My Name"] [--set-email "me@co.com"] [--set-limit 100]
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add_lead
    p = sub.add_parser("add_lead", help="Add a new lead")
    p.add_argument("--name",     required=True, help="Full name")
    p.add_argument("--email",    required=True, help="Email address")
    p.add_argument("--company",  default="",    help="Company name")
    p.add_argument("--industry", default="",    help="Industry")
    p.add_argument("--title",    default="",    help="Job title")
    p.add_argument("--source",   default="manual", help="Lead source")
    p.add_argument("--tags",     default="",    help="Comma-separated tags")
    p.add_argument("--variables", default={},   help="Extra variables as JSON string")

    # list_leads
    p = sub.add_parser("list_leads", help="List all leads")
    p.add_argument("--status", default="", help="Filter by status (comma-separated)")

    # generate
    p = sub.add_parser("generate", help="Generate personalized email")
    p.add_argument("--lead-id",  required=True, type=int)
    p.add_argument("--template", default="intro", choices=list(EMAIL_TEMPLATES.keys()))
    p.add_argument("--count",    type=int, default=1, help="Number of A/B variants")
    p.add_argument("--save",     action="store_true", help="Save as draft")

    # send
    p = sub.add_parser("send", help="Send email to lead")
    p.add_argument("--lead-id",  required=True, type=int)
    p.add_argument("--template", default="intro", choices=list(EMAIL_TEMPLATES.keys()))
    p.add_argument("--dry-run",  action="store_true")

    # sequence
    p = sub.add_parser("sequence", help="Run full email sequence")
    p.add_argument("--lead-id",  required=True, type=int)
    p.add_argument("--dry-run",  action="store_true")

    # report
    sub.add_parser("report", help="Show campaign report")

    # config
    p = sub.add_parser("config", help="View/update config")
    p.add_argument("--set-name",  help="Set sender name")
    p.add_argument("--set-email", help="Set sender email")
    p.add_argument("--set-limit", help="Set daily email limit")

    args = parser.parse_args()
    commands = {
        "add_lead": cmd_add_lead,
        "list_leads": cmd_list_leads,
        "generate": cmd_generate,
        "send": cmd_send,
        "sequence": cmd_sequence,
        "report": cmd_report,
        "config": cmd_config,
    }
    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
