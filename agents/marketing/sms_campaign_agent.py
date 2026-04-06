#!/usr/bin/env python3
"""
SMS Campaign Agent — EmpireHazeClaw Marketing System
Manages SMS marketing campaigns with segmentation and A/B testing.
"""

import argparse
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
SMS_DIR = DATA_DIR / "sms"
CAMPAIGNS_FILE = SMS_DIR / "campaigns.json"
CONTACTS_FILE = SMS_DIR / "contacts.json"
SENT_FILE = SMS_DIR / "sent.json"
SMS_TEMPLATES = SMS_DIR / "templates.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
SMS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SMS-CAMPAIGN] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "sms_campaign.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("sms_campaign")


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


# ── Templates ─────────────────────────────────────────────────────────────────
DEFAULT_TEMPLATES = {
    "welcome": {"body": "Hi {first_name}! Welcome to {brand}. You're going to love what's coming. Reply STOP to opt out.", "max_len": 160},
    "promo": {"body": "{discount}% off for {first_name}! {offer}. Valid {expiry}. Shop now: {url}. Reply STOP to opt out.", "max_len": 160},
    "cart": {"body": "{first_name}, you left something behind! Complete your order: {url}. Offer expires {expiry}.", "max_len": 160},
    "alert": {"body": "{brand} update: {message}. Check your dashboard → {url}", "max_len": 160},
    "re_engagement": {"body": "Hey {first_name}, we miss you! {offer}. Come back: {url}. Reply STOP to opt out.", "max_len": 160},
    "appointment": {"body": "{brand} reminder: Your appointment is {date} at {time}. Reply CONFIRM or RESCHEDULE.", "max_len": 160},
    "order": {"body": "Order confirmed! {order_id}. Track: {url}. Questions? Reply here. {brand}", "max_len": 160},
}


def render_template(body: str, vars: dict) -> str:
    result = body
    for k, v in vars.items():
        result = result.replace("{" + k + "}", str(v))
    return result


def validate_sms(body: str) -> tuple[bool, int]:
    length = len(body)
    segments = (length // 160) + 1 if length > 160 else 1
    return length <= 1600, length


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_create_campaign(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id or f"sms_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if cid in campaigns:
        log.error("Campaign '%s' already exists", cid)
        sys.exit(1)

    campaign = {
        "id": cid,
        "name": args.name,
        "message": args.message,
        "template": args.template,
        "segment": args.segment or "all",
        "status": "draft",
        "a_b_test": args.ab,
        "variants": [],
        "created": datetime.now(timezone.utc).isoformat(),
        "sent": 0,
        "delivered": 0,
        "failed": 0,
        "opt_outs": 0,
    }
    campaigns[cid] = campaign
    save_json(CAMPAIGNS_FILE, campaigns)
    print(f"✅ SMS Campaign '{cid}' created: {args.name}")
    log.info("SMS campaign created: %s", cid)


def cmd_list_campaigns(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    if args.status:
        campaigns = {k: v for k, v in campaigns.items() if v.get("status") == args.status}
    print(f"{'ID':<30} {'NAME':<25} {'STATUS':<10} {'SENT':>6} {'SEGMENT':<12}")
    print("-" * 90)
    for c in sorted(campaigns.values(), key=lambda x: x.get("created", "")):
        print(f"{c['id']:<30} {c.get('name',''):<25} {c.get('status',''):<10} {c.get('sent',0):>6} {c.get('segment',''):<12}")


def cmd_preview(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]

    contacts = load_json(CONTACTS_FILE)
    sample = contacts[0] if contacts else {"first_name": "Max", "phone": "+1000000000"}

    vars_dict = {
        "first_name": sample.get("first_name", "Max"),
        "brand": "EmpireHazeClaw",
        "discount": "20%",
        "offer": "comeback deal",
        "expiry": "48 hours",
        "url": "https://empirehazeclaw.com",
        "message": "something important",
        "date": datetime.now(timezone.utc).strftime("%B %d"),
        "time": "2:00 PM",
        "order_id": "ORD-12345",
    }

    body = render_template(c.get("message", "Hello {first_name}!"), vars_dict)
    ok, length = validate_sms(body)
    segments = (length // 160) + 1 if length > 160 else 1

    print(f"\n{'='*60}")
    print(f"SMS PREVIEW — {cid}")
    print(f"{'='*60}")
    print(f"TO: {sample.get('phone','')}")
    print(f"CHARS: {length}/160 | SEGMENTS: {segments}")
    print(f"VALID: {'✅' if ok else '❌ (too long)'}")
    print(f"\n{'='*60}")
    print(body)
    print(f"\n{'='*60}")


def cmd_send(args: argparse.Namespace) -> None:
    """Simulate sending SMS campaign (no actual SMS gateway)."""
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    c = campaigns[cid]
    contacts = load_json(CONTACTS_FILE)

    if c["status"] == "sent":
        log.warning("Campaign already sent")
        if not args.resend:
            print("⚠️  Campaign already sent. Use --resend to force.")
            sys.exit(1)

    # Filter segment
    if args.segment:
        segment_map = {
            "all": contacts,
            "active": [x for x in contacts if x.get("status") == "active"],
            "inactive": [x for x in contacts if x.get("status") == "inactive"],
            "opted_in": [x for x in contacts if x.get("opted_in", True)],
        }
        contacts = segment_map.get(args.segment, contacts)

    if args.limit:
        contacts = contacts[: args.limit]

    sent_history = load_json(SENT_FILE)
    sent_count = 0
    for contact in contacts:
        vars_dict = {
            "first_name": contact.get("first_name", "there"),
            "brand": "EmpireHazeClaw",
            "discount": "20%",
            "offer": "special offer",
            "expiry": "48 hours",
            "url": "https://empirehazeclaw.com",
            "message": c.get("name", ""),
            "date": datetime.now(timezone.utc).strftime("%B %d"),
            "time": "2:00 PM",
            "order_id": "ORD-" + str(random.randint(10000, 99999)),
        }
        body = render_template(c.get("message", "Hi {first_name}!"), vars_dict)
        ok, _ = validate_sms(body)

        record = {
            "campaign_id": cid,
            "phone": contact.get("phone", ""),
            "message": body,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent" if ok else "failed",
        }
        sent_history.append(record)
        if ok:
            sent_count += 1

    save_json(SENT_FILE, sent_history)
    c["status"] = "sent"
    c["sent"] = sent_count
    campaigns[cid] = c
    save_json(CAMPAIGNS_FILE, campaigns)

    print(f"✅ {sent_count} SMS sent for campaign '{cid}'.")
    log.info("SMS campaign %s sent: %d messages", cid, sent_count)


def cmd_report(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]
    sent = c.get("sent", 0)
    delivered = c.get("delivered", 0)
    failed = c.get("failed", 0)
    opt_outs = c.get("opt_outs", 0)
    del_rate = f"{delivered/sent*100:.1f}%" if sent > 0 else "N/A"
    fail_rate = f"{failed/sent*100:.1f}%" if sent > 0 else "N/A"

    print(f"\n{'='*50}")
    print(f"SMS REPORT — {cid} ({c.get('name','')})")
    print(f"{'='*50}")
    print(f"  Status:     {c.get('status','')}")
    print(f"  Segment:   {c.get('segment','')}")
    print(f"  Sent:       {sent}")
    print(f"  Delivered: {delivered} ({del_rate})")
    print(f"  Failed:    {failed} ({fail_rate})")
    print(f"  Opt-outs:  {opt_outs}")
    print(f"{'='*50}")


def cmd_add_contact(args: argparse.Namespace) -> None:
    contacts = load_json(CONTACTS_FILE)
    phone = args.phone
    if any(x.get("phone") == phone for x in contacts):
        print(f"Contact {phone} already exists.")
        return
    contact = {
        "phone": phone,
        "first_name": args.first_name or "",
        "last_name": args.last_name or "",
        "status": "active",
        "opted_in": True,
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "added_at": datetime.now(timezone.utc).isoformat(),
        "source": args.source or "manual",
    }
    contacts.append(contact)
    save_json(CONTACTS_FILE, contacts)
    print(f"✅ Contact added: {phone}")
    log.info("SMS contact added: %s", phone)


def cmd_list_contacts(args: argparse.Namespace) -> None:
    contacts = load_json(CONTACTS_FILE)
    if args.status:
        contacts = [c for c in contacts if c.get("status") == args.status]
    print(f"Total contacts: {len(contacts)}")
    print(f"{'PHONE':<18} {'NAME':<20} {'STATUS':<10} {'TAGS':<20}")
    print("-" * 75)
    for c in contacts:
        tags = ",".join(c.get("tags", []))
        name = f"{c.get('first_name','')} {c.get('last_name','')}".strip() or "—"
        print(f"{c.get('phone',''):<18} {name:<20} {c.get('status',''):<10} {tags:<20}")


def cmd_templates(args: argparse.Namespace) -> None:
    templates = DEFAULT_TEMPLATES
    if SMS_TEMPLATES.exists():
        stored = load_json(SMS_TEMPLATES)
        templates.update(stored)
    for key, t in templates.items():
        body = t.get("body", "")
        print(f"\n📱 {key.upper()}")
        print(f"   Max: {t.get('max_len', 160)} chars")
        print(f"   Body: {body[:100]}...")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="sms_campaign_agent.py",
        description="EmpireHazeClaw SMS Campaign Manager.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_c = sub.add_parser("create", help="Create SMS campaign")
    p_c.add_argument("--campaign-id", dest="campaign_id")
    p_c.add_argument("--name", required=True)
    p_c.add_argument("--message", required=True, help="SMS body with {variables}")
    p_c.add_argument("--template", help="Template name to save as")
    p_c.add_argument("--segment", choices=["all", "active", "inactive", "opted_in"])
    p_c.add_argument("--ab", action="store_true", help="Enable A/B testing")
    p_c.set_defaults(fn=cmd_create_campaign)

    p_l = sub.add_parser("list", help="List SMS campaigns")
    p_l.add_argument("--status", choices=["draft", "sending", "sent", "paused"])
    p_l.set_defaults(fn=cmd_list_campaigns)

    p_prev = sub.add_parser("preview", help="Preview SMS message")
    p_prev.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_prev.set_defaults(fn=cmd_preview)

    p_send = sub.add_parser("send", help="Send SMS campaign")
    p_send.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_send.add_argument("--segment", choices=["all", "active", "inactive", "opted_in"])
    p_send.add_argument("--limit", type=int)
    p_send.add_argument("--resend", action="store_true")
    p_send.set_defaults(fn=cmd_send)

    p_rep = sub.add_parser("report", help="Show SMS campaign report")
    p_rep.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_rep.set_defaults(fn=cmd_report)

    p_ac = sub.add_parser("add-contact", help="Add SMS contact")
    p_ac.add_argument("--phone", required=True)
    p_ac.add_argument("--first-name", dest="first_name")
    p_ac.add_argument("--last-name", dest="last_name")
    p_ac.add_argument("--tags", help="Comma-separated tags")
    p_ac.add_argument("--source")
    p_ac.set_defaults(fn=cmd_add_contact)

    p_lc = sub.add_parser("contacts", help="List SMS contacts")
    p_lc.add_argument("--status", choices=["active", "inactive", "opted_in"])
    p_lc.set_defaults(fn=cmd_list_contacts)

    p_t = sub.add_parser("templates", help="Show SMS templates")
    p_t.set_defaults(fn=cmd_templates)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
