#!/usr/bin/env python3
"""
Email Campaign Agent — EmpireHazeClaw Marketing System
Builds, manages, and tracks email marketing campaigns.
"""

import argparse
import csv
import json
import logging
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
EMAIL_DIR = DATA_DIR / "email"
CAMPAIGNS_FILE = EMAIL_DIR / "campaigns.json"
SUBSCRIBERS_FILE = EMAIL_DIR / "subscribers.json"
QUEUE_FILE = EMAIL_DIR / "email_queue.json"
TEMPLATES_DIR = EMAIL_DIR / "templates"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [EMAIL-CAMPAIGN] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "email_campaign.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("email_campaign")


# ── Data Layer ────────────────────────────────────────────────────────────────
def load_json(path: Path) -> dict | list:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load %s: %s", path, e)
    return {} if ".json" in str(path) else []


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_subscribers() -> list:
    return load_json(SUBSCRIBERS_FILE)


def save_subscribers(subs: list) -> None:
    save_json(SUBSCRIBERS_FILE, subs)


def load_campaigns() -> dict:
    return load_json(CAMPAIGNS_FILE)


def save_campaigns(data: dict) -> None:
    save_json(CAMPAIGNS_FILE, data)


def load_queue() -> list:
    return load_json(QUEUE_FILE)


def save_queue(q: list) -> None:
    save_json(QUEUE_FILE, q)


# ── Template Engine ───────────────────────────────────────────────────────────
EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to {brand} — Here's Where to Start",
        "body": """Hi {first_name},

Welcome aboard. You're now part of the {brand} community.

Here's what happens next:
1. Check your inbox — we sent you something special
2. Reply to this email if you have questions (yes, real humans read these)
3. Explore what we built for you

No fluff. Just the thing.

— The {brand} Team
""",
    },
    "lead_magnet": {
        "subject": "Your {offer_title} Is Ready — Here's How to Access It",
        "body": """Hi {first_name},

Thanks for requesting {offer_title}. You asked for it, here it is.

{offer_description}

Access it here: {offer_url}

A few things to know:
— No credit card required
— Instant access
— Unsubscribe anytime

Questions? Just reply. We're here.

— The {brand} Team
""",
    },
    "cart_recovery": {
        "subject": "You Left Something Behind — {product_name}",
        "body": """Hi {first_name},

You clicked but didn't complete. Happens to the best of us.

{item_summary}

Still interested? Here's your link: {checkout_url}

This offer expires in {expiry_hours} hours.

— The {brand} Team
""",
    },
    "newsletter": {
        "subject": "{issue_title} — {date}",
        "body": """Hi {first_name},

{issue_summary}

---

{content_body}

---

{cta_block}

You're receiving this because you subscribed. Manage preferences: {unsubscribe_url}
""",
    },
    "re_engagement": {
        "subject": "We miss you, {first_name} — Here's What's New",
        "body": """Hi {first_name},

It's been a while. We haven't heard from you since {last_active_date}.

Since then, we've shipped:
{new_features}

We'd love to have you back. Here's an offer just for you: {special_offer_url}

No pressure. But we do miss you.

— The {brand} Team
""",
    },
}


def render_template(template_key: str, variables: dict) -> dict:
    t = EMAIL_TEMPLATES.get(template_key)
    if not t:
        raise ValueError(f"Unknown template: {template_key}")
    subject = t["subject"]
    body = t["body"]
    for key, val in variables.items():
        placeholder = "{" + key + "}"
        subject = subject.replace(placeholder, str(val))
        body = body.replace(placeholder, str(val))
    return {"subject": subject, "body": body, "template": template_key}


# ── Personalization ───────────────────────────────────────────────────────────
PERSONALIZATION_TOKENS = {
    "{first_name}": "there",
    "{brand}": "EmpireHazeClaw",
    "{year}": str(datetime.now(timezone.utc).year),
    "{date}": datetime.now(timezone.utc).strftime("%B %d, %Y"),
}


def apply_personalization(text: str, subscriber: dict) -> str:
    result = text
    for token, default in PERSONALIZATION_TOKENS.items():
        result = result.replace(token, str(subscriber.get(token[1:-1], default)))
    return result


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_create_campaign(args: argparse.Namespace) -> None:
    campaigns = load_campaigns()
    cid = args.campaign_id or f"ec_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if cid in campaigns:
        log.error("Campaign '%s' already exists", cid)
        sys.exit(1)

    campaign = {
        "id": cid,
        "name": args.name,
        "subject": args.subject,
        "template": args.template,
        "status": "draft",
        "recipients": args.recipients or "all",
        "vars": {},
        "created": datetime.now(timezone.utc).isoformat(),
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "bounced": 0,
        "unsubscribed": 0,
    }
    campaigns[cid] = campaign
    save_campaigns(campaigns)
    print(f"✅ Campaign '{cid}' created: {args.name}")
    log.info("Email campaign created: %s", cid)


def cmd_list_campaigns(args: argparse.Namespace) -> None:
    campaigns = load_campaigns()
    if args.status:
        campaigns = {k: v for k, v in campaigns.items() if v.get("status") == args.status}
    print(f"{'ID':<30} {'NAME':<25} {'STATUS':<10} {'SENT':>6} {'OPENS':>6} {'CTR':>6}")
    print("-" * 90)
    for c in sorted(campaigns.values(), key=lambda x: x.get("created", "")):
        ctr = f"{c['clicked']/max(c['sent'],1)*100:.1f}%" if c['sent'] > 0 else "N/A"
        print(f"{c['id']:<30} {c.get('name',''):<25} {c.get('status',''):<10} {c.get('sent',0):>6} {c.get('opened',0):>6} {ctr:>6}")


def cmd_preview(args: argparse.Namespace) -> None:
    campaigns = load_campaigns()
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]

    subscribers = load_subscribers()
    sample = subscribers[0] if subscribers else {"first_name": "Max", "email": "example@test.com"}

    variables = {
        "first_name": sample.get("first_name", "Max"),
        "brand": "EmpireHazeClaw",
        "issue_title": "This Week's Insights",
        "date": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "issue_summary": "Fresh insights delivered to your inbox.",
        "content_body": "Your weekly content goes here...",
        "cta_block": "👉 [Your CTA here]",
        "unsubscribe_url": "#",
        "offer_title": c.get("name", "Free Guide"),
        "offer_description": "Your exclusive content.",
        "offer_url": "#",
        "product_name": "Your Product",
        "item_summary": "Something you left behind.",
        "checkout_url": "#",
        "expiry_hours": "48",
        "last_active_date": "January 2026",
        "new_features": "• New feature 1\n• New feature 2",
        "special_offer_url": "#",
    }

    email = render_template(c.get("template", "welcome"), variables)
    print(f"\n{'='*60}")
    print(f"CAMPAIGN PREVIEW — {cid}")
    print(f"{'='*60}")
    print(f"TO: {sample.get('email','')}")
    print(f"SUBJECT: {email['subject']}")
    print(f"TEMPLATE: {email['template']}")
    print(f"{'='*60}")
    print(email["body"])


def cmd_send(args: argparse.Namespace) -> None:
    """Queue emails for sending (simulated — no actual SMTP in this version)."""
    campaigns = load_campaigns()
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    c = campaigns[cid]
    subscribers = load_subscribers()

    if c["status"] == "sent":
        log.warning("Campaign '%s' already sent", cid)
        print("⚠️  Campaign already sent. Use --resend to force.")
        if not args.resend:
            sys.exit(1)

    # Filter recipients
    if args.segment:
        if args.segment == "active":
            subscribers = [s for s in subscribers if s.get("status") == "active"]
        elif args.segment == "inactive":
            subscribers = [s for s in subscribers if s.get("status") == "inactive"]

    if args.limit:
        subscribers = subscribers[: args.limit]

    queue = load_queue()
    queued_count = 0
    for sub in subscribers:
        email_data = {
            "campaign_id": cid,
            "subscriber": sub,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "status": "queued",
        }
        queue.append(email_data)
        queued_count += 1

    save_queue(queue)
    c["status"] = "sending"
    c["sent"] = c.get("sent", 0) + queued_count
    campaigns[cid] = c
    save_campaigns(campaigns)

    print(f"✅ {queued_count} emails queued for campaign '{cid}'.")
    print(f"   Run with --smtp-host to actually send.")
    log.info("Queued %d emails for campaign %s", queued_count, cid)


def cmd_add_subscriber(args: argparse.Namespace) -> None:
    subscribers = load_subscribers()
    email = args.email
    if any(s.get("email") == email for s in subscribers):
        log.warning("Subscriber '%s' already exists", email)
        print(f"Subscriber {email} already exists.")
        return

    sub = {
        "email": email,
        "first_name": args.first_name or email.split("@")[0],
        "last_name": args.last_name or "",
        "status": "active",
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "source": args.source or "manual",
    }
    subscribers.append(sub)
    save_subscribers(subscribers)
    print(f"✅ Subscriber added: {email}")
    log.info("Subscriber added: %s", email)


def cmd_list_subscribers(args: argparse.Namespace) -> None:
    subs = load_subscribers()
    if args.status:
        subs = [s for s in subs if s.get("status") == args.status]
    if args.tag:
        subs = [s for s in subs if args.tag in s.get("tags", [])]
    print(f"Total subscribers: {len(subs)}")
    print(f"{'EMAIL':<35} {'NAME':<20} {'STATUS':<10} {'TAGS':<20}")
    print("-" * 90)
    for s in subs:
        tags = ",".join(s.get("tags", []))
        print(f"{s.get('email',''):<35} {s.get('first_name',''):<20} {s.get('status',''):<10} {tags:<20}")


def cmd_import_csv(args: argparse.Namespace) -> None:
    rows = []
    try:
        with open(args.file, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        log.error("Could not read CSV: %s", e)
        sys.exit(1)

    subscribers = load_subscribers()
    added = 0
    skipped = 0
    for row in rows:
        email_field = args.email_column or "email"
        email = row.get(email_field, "").strip()
        if not email or "@" not in email:
            skipped += 1
            continue
        if any(s.get("email") == email for s in subscribers):
            skipped += 1
            continue
        subscribers.append({
            "email": email,
            "first_name": row.get(args.name_column or "first_name", ""),
            "last_name": row.get(args.last_name_column or "last_name", ""),
            "status": "active",
            "tags": [args.tag] if args.tag else [],
            "subscribed_at": datetime.now(timezone.utc).isoformat(),
            "source": f"csv_import:{args.file}",
        })
        added += 1

    save_subscribers(subscribers)
    print(f"✅ Import complete: {added} added, {skipped} skipped.")
    log.info("CSV import: %d added, %d skipped", added, skipped)


def cmd_queue_status(args: argparse.Namespace) -> None:
    queue = load_queue()
    stats = {"queued": 0, "sending": 0, "sent": 0, "failed": 0}
    for e in queue:
        stats[e.get("status", "queued")] = stats.get(e.get("status", "queued"), 0) + 1
    print(f"Queue Status:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    if args.clear:
        save_queue([])
        print("Queue cleared.")


def cmd_templates(args: argparse.Namespace) -> None:
    for key, t in EMAIL_TEMPLATES.items():
        print(f"\n📧 {key.upper()}")
        print(f"   Subject: {t['subject']}")
        print(f"   Body preview: {t['body'][:100]}...")


def cmd_report(args: argparse.Namespace) -> None:
    campaigns = load_campaigns()
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]
    sent = c.get("sent", 0)
    opened = c.get("opened", 0)
    clicked = c.get("clicked", 0)
    open_rate = f"{opened/sent*100:.1f}%" if sent > 0 else "N/A"
    click_rate = f"{clicked/sent*100:.1f}%" if sent > 0 else "N/A"

    print(f"\n{'='*50}")
    print(f"EMAIL REPORT — {cid} ({c.get('name','')})")
    print(f"{'='*50}")
    print(f"  Status:      {c.get('status','')}")
    print(f"  Template:    {c.get('template','')}")
    print(f"  Sent:        {sent}")
    print(f"  Opened:      {opened} ({open_rate})")
    print(f"  Clicked:     {clicked} ({click_rate})")
    print(f"  Bounced:     {c.get('bounced',0)}")
    print(f"  Unsubs:     {c.get('unsubscribed',0)}")
    print(f"{'='*50}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="email_campaign_agent.py",
        description="EmpireHazeClaw Email Campaign Manager.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # campaign commands
    p_c = sub.add_parser("create", help="Create a new email campaign")
    p_c.add_argument("--campaign-id", dest="campaign_id")
    p_c.add_argument("--name", required=True)
    p_c.add_argument("--subject", required=True)
    p_c.add_argument("--template", required=True,
                      choices=list(EMAIL_TEMPLATES.keys()),
                      help="Email template type")
    p_c.add_argument("--recipients", help="Recipient segment (default: all)")
    p_c.set_defaults(fn=cmd_create_campaign)

    p_l = sub.add_parser("list", help="List campaigns")
    p_l.add_argument("--status", choices=["draft", "sending", "sent", "paused"])
    p_l.set_defaults(fn=cmd_list_campaigns)

    p_prev = sub.add_parser("preview", help="Preview campaign email")
    p_prev.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_prev.set_defaults(fn=cmd_preview)

    p_send = sub.add_parser("send", help="Queue emails for a campaign")
    p_send.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_send.add_argument("--segment", choices=["all", "active", "inactive"], default="all")
    p_send.add_argument("--limit", type=int, help="Limit number of recipients")
    p_send.add_argument("--resend", action="store_true", help="Force resend of already-sent campaign")
    p_send.set_defaults(fn=cmd_send)

    p_rep = sub.add_parser("report", help="Show campaign report")
    p_rep.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_rep.set_defaults(fn=cmd_report)

    # subscriber commands
    p_as = sub.add_parser("add-subscriber", help="Add a subscriber")
    p_as.add_argument("--email", required=True)
    p_as.add_argument("--first-name", dest="first_name")
    p_as.add_argument("--last-name", dest="last_name")
    p_as.add_argument("--tags", help="Comma-separated tags")
    p_as.add_argument("--source")
    p_as.set_defaults(fn=cmd_add_subscriber)

    p_ls = sub.add_parser("subscribers", help="List subscribers")
    p_ls.add_argument("--status", choices=["active", "inactive", "unsubscribed"])
    p_ls.add_argument("--tag")
    p_ls.set_defaults(fn=cmd_list_subscribers)

    p_imp = sub.add_parser("import-csv", help="Import subscribers from CSV")
    p_imp.add_argument("--file", required=True, help="CSV file path")
    p_imp.add_argument("--email-column", dest="email_column", default="email")
    p_imp.add_argument("--name-column", dest="name_column", default="first_name")
    p_imp.add_argument("--last-name-column", dest="last_name_column", default="last_name")
    p_imp.add_argument("--tag", help="Tag all imported subscribers")
    p_imp.set_defaults(fn=cmd_import_csv)

    # queue
    p_q = sub.add_parser("queue", help="Show email queue status")
    p_q.add_argument("--clear", action="store_true")
    p_q.set_defaults(fn=cmd_queue_status)

    # templates
    p_t = sub.add_parser("templates", help="Show available email templates")
    p_t.set_defaults(fn=cmd_templates)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
