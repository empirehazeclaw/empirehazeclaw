#!/usr/bin/env python3
"""
Push Notification Agent — EmpireHazeClaw Marketing System
Manages push notification campaigns with segmentation, scheduling, and A/B testing.
"""

import argparse
import json
import logging
import random
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
PUSH_DIR = DATA_DIR / "push"
CAMPAIGNS_FILE = PUSH_DIR / "campaigns.json"
SUBSCRIBERS_FILE = PUSH_DIR / "subscribers.json"
SENT_FILE = PUSH_DIR / "sent.json"
NOTIF_TEMPLATES = PUSH_DIR / "templates.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
PUSH_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [PUSH-NOTIF] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "push_notification.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("push_notification")


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


# ── Validation ─────────────────────────────────────────────────────────────────
def validate_title(title: str) -> tuple[bool, str]:
    max_title = 50
    if len(title) > max_title:
        return False, f"Title exceeds {max_title} chars ({len(title)})"
    return True, "OK"


def validate_body(body: str) -> tuple[bool, str]:
    max_body = 200
    if len(body) > max_body:
        return False, f"Body exceeds {max_body} chars ({len(body)})"
    return True, "OK"


def validate_push(campaign: dict) -> tuple[bool, list]:
    errors = []
    title_ok, title_msg = validate_title(campaign.get("title", ""))
    if not title_ok:
        errors.append(title_msg)
    body_ok, body_msg = validate_body(campaign.get("body", ""))
    if not body_ok:
        errors.append(body_msg)
    return len(errors) == 0, errors


# ── Scheduling ────────────────────────────────────────────────────────────────
def parse_schedule(schedule_str: str) -> datetime | None:
    """Parse schedule string into datetime."""
    if not schedule_str:
        return None
    try:
        return datetime.fromisoformat(schedule_str)
    except ValueError:
        pass
    # Try common human formats
    now = datetime.now(timezone.utc)
    if schedule_str == "now":
        return now
    if schedule_str == "in1h":
        return now + timedelta(hours=1)
    if schedule_str == "in3h":
        return now + timedelta(hours=3)
    if schedule_str == "tomorrow":
        return now + timedelta(days=1)
    return None


def is_due(scheduled_at: str | None) -> bool:
    if not scheduled_at:
        return True
    try:
        scheduled = datetime.fromisoformat(scheduled_at)
        return datetime.now(timezone.utc) >= scheduled
    except (ValueError, TypeError):
        return True


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_create_campaign(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id or f"push_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if cid in campaigns:
        log.error("Campaign '%s' already exists", cid)
        sys.exit(1)

    campaign = {
        "id": cid,
        "name": args.name,
        "title": args.title,
        "body": args.body,
        "url": args.url or "",
        "icon": args.icon or "",
        "image": args.image or "",
        "badge": args.badge or "1",
        "tag": args.tag or "default",
        "require_interaction": args.require_interaction or False,
        "vibrate": args.vibrate or True,
        "priority": args.priority or "normal",
        "status": "draft",
        "segment": args.segment or "all",
        "schedule": args.schedule,
        "scheduled_at": parse_schedule(args.schedule).isoformat() if args.schedule else None,
        "ab_test": args.ab,
        "variants": [],
        "created": datetime.now(timezone.utc).isoformat(),
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "dismissed": 0,
        "failed": 0,
    }

    valid, errors = validate_push(campaign)
    if not valid:
        log.error("Validation errors: %s", errors)
        print(f"❌ Validation failed: {', '.join(errors)}")
        sys.exit(1)

    campaigns[cid] = campaign
    save_json(CAMPAIGNS_FILE, campaigns)
    print(f"✅ Push campaign '{cid}' created: {args.name}")
    log.info("Push campaign created: %s", cid)


def cmd_list_campaigns(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    if args.status:
        campaigns = {k: v for k, v in campaigns.items() if v.get("status") == args.status}
    print(f"{'ID':<30} {'NAME':<25} {'STATUS':<10} {'SENT':>6} {'OPEN%':>7} {'SCHEDULED':<20}")
    print("-" * 105)
    for c in sorted(campaigns.values(), key=lambda x: x.get("created", "")):
        open_pct = f"{c.get('opened',0)/max(c.get('sent',1),1)*100:.1f}%"
        sched = c.get("scheduled_at", "—")
        if sched and sched != "—":
            sched = sched[:16]
        print(f"{c['id']:<30} {c.get('name',''):<25} {c.get('status',''):<10} {c.get('sent',0):>6} {open_pct:>7} {sched:<20}")


def cmd_preview(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]

    print(f"\n{'='*60}")
    print(f"PUSH NOTIFICATION PREVIEW — {cid}")
    print(f"{'='*60}")
    print(f"📌 TITLE:   {c.get('title','')}")
    print(f"📄 BODY:    {c.get('body','')}")
    print(f"🔗 URL:     {c.get('url','')}")
    print(f"🏷️  TAG:    {c.get('tag','')}")
    print(f"⭐ PRIORITY: {c.get('priority','')}")
    print(f"⏰ SCHEDULED: {c.get('scheduled_at','—')}")
    print(f"📊 STATUS:   {c.get('status','')}")
    print(f"{'='*60}")


def cmd_send(args: argparse.Namespace) -> None:
    """Simulate sending push notifications (no actual Web Push API)."""
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    c = campaigns[cid]

    if not is_due(c.get("scheduled_at")):
        print(f"⏰ Campaign '{cid}' is scheduled for {c['scheduled_at']}. Not due yet.")
        sys.exit(0)

    if c["status"] == "sent":
        if not args.resend:
            print("⚠️  Campaign already sent. Use --resend to force.")
            sys.exit(1)

    subscribers = load_json(SUBSCRIBERS_FILE)
    if args.segment:
        seg_map = {
            "all": subscribers,
            "active": [s for s in subscribers if s.get("status") == "active"],
            "inactive": [s for s in subscribers if s.get("status") == "inactive"],
            "web": [s for s in subscribers if s.get("platform") == "web"],
            "mobile": [s for s in subscribers if s.get("platform") in ("ios", "android")],
        }
        subscribers = seg_map.get(args.segment, subscribers)

    if args.limit:
        subscribers = subscribers[: args.limit]

    sent_history = load_json(SENT_FILE)
    sent_count = 0
    open_count = 0
    for sub in subscribers:
        record = {
            "campaign_id": cid,
            "subscriber_id": sub.get("id", ""),
            "platform": sub.get("platform", "unknown"),
            "title": c.get("title", ""),
            "body": c.get("body", ""),
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
        }
        # Simulate open rate (~40% open rate for push)
        if random.random() < 0.4:
            record["status"] = "opened"
            open_count += 1
        sent_history.append(record)
        sent_count += 1

    save_json(SENT_FILE, sent_history)
    c["status"] = "sent"
    c["sent"] = c.get("sent", 0) + sent_count
    c["opened"] = c.get("opened", 0) + open_count
    campaigns[cid] = c
    save_json(CAMPAIGNS_FILE, campaigns)

    print(f"✅ {sent_count} push notifications sent for campaign '{cid}'.")
    print(f"   Simulated opens: {open_count} ({open_count/sent_count*100:.1f}%)")
    log.info("Push campaign %s sent: %d messages, %d opens", cid, sent_count, open_count)


def cmd_report(args: argparse.Namespace) -> None:
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)
    c = campaigns[cid]
    sent = c.get("sent", 0)
    opened = c.get("opened", 0)
    clicked = c.get("clicked", 0)
    dismissed = c.get("dismissed", 0)
    failed = c.get("failed", 0)
    open_rate = f"{opened/sent*100:.1f}%" if sent > 0 else "N/A"
    click_rate = f"{clicked/sent*100:.1f}%" if sent > 0 else "N/A"

    print(f"\n{'='*50}")
    print(f"PUSH REPORT — {cid} ({c.get('name','')})")
    print(f"{'='*50}")
    print(f"  Status:     {c.get('status','')}")
    print(f"  Segment:   {c.get('segment','')}")
    print(f"  Title:     {c.get('title','')}")
    print(f"  Sent:       {sent}")
    print(f"  Opened:     {opened} ({open_rate})")
    print(f"  Clicked:    {clicked} ({click_rate})")
    print(f"  Dismissed: {dismissed}")
    print(f"  Failed:    {failed}")
    print(f"{'='*50}")


def cmd_add_subscriber(args: argparse.Namespace) -> None:
    subscribers = load_json(SUBSCRIBERS_FILE)
    sid = args.subscriber_id or f"sub_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    if any(s.get("id") == sid or s.get("endpoint") == args.endpoint for s in subscribers):
        print(f"Subscriber already exists.")
        return

    sub = {
        "id": sid,
        "endpoint": args.endpoint,
        "keys": {"p256dh": args.p256dh or "", "auth": args.auth or ""},
        "platform": args.platform or "web",
        "status": "active",
        "language": args.language or "en",
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    subscribers.append(sub)
    save_json(SUBSCRIBERS_FILE, subscribers)
    print(f"✅ Subscriber added: {sid} ({args.platform})")
    log.info("Push subscriber added: %s", sid)


def cmd_list_subscribers(args: argparse.Namespace) -> None:
    subscribers = load_json(SUBSCRIBERS_FILE)
    if args.platform:
        subscribers = [s for s in subscribers if s.get("platform") == args.platform]
    if args.status:
        subscribers = [s for s in subscribers if s.get("status") == args.status]
    print(f"Total subscribers: {len(subscribers)}")
    print(f"{'ID':<30} {'PLATFORM':<10} {'STATUS':<10} {'LANG':<6}")
    print("-" * 65)
    for s in subscribers:
        print(f"{s.get('id',''):<30} {s.get('platform',''):<10} {s.get('status',''):<10} {s.get('language',''):<6}")


def cmd_schedule(args: argparse.Namespace) -> None:
    """Schedule a campaign for future sending."""
    campaigns = load_json(CAMPAIGNS_FILE)
    cid = args.campaign_id
    if cid not in campaigns:
        log.error("Campaign '%s' not found", cid)
        sys.exit(1)

    scheduled_dt = parse_schedule(args.at)
    if scheduled_dt is None:
        log.error("Invalid schedule format: %s. Use ISO format, 'now', 'in1h', 'tomorrow'", args.at)
        sys.exit(1)

    c = campaigns[cid]
    c["schedule"] = args.at
    c["scheduled_at"] = scheduled_dt.isoformat()
    c["status"] = "scheduled"
    campaigns[cid] = c
    save_json(CAMPAIGNS_FILE, campaigns)
    print(f"✅ Campaign '{cid}' scheduled for {scheduled_dt.isoformat()}")
    log.info("Push campaign %s scheduled for %s", cid, scheduled_dt)


def cmd_pending(args: argparse.Namespace) -> None:
    """Show campaigns pending scheduled send."""
    campaigns = load_json(CAMPAIGNS_FILE)
    pending = {k: v for k, v in campaigns.items() if v.get("status") == "scheduled"}
    if not pending:
        print("No pending scheduled campaigns.")
        return
    print(f"{'ID':<30} {'NAME':<25} {'SCHEDULED_AT':<25}")
    print("-" * 85)
    for c in pending.values():
        print(f"{c['id']:<30} {c.get('name',''):<25} {c.get('scheduled_at',''):<25}")


def cmd_webhook(args: argparse.Namespace) -> None:
    """Register/manage webhook for push events."""
    hooks_file = PUSH_DIR / "webhooks.json"
    hooks = []
    if hooks_file.exists():
        hooks = load_json(hooks_file)

    if args.list:
        if not hooks:
            print("No webhooks registered.")
            return
        print("Registered webhooks:")
        for h in hooks:
            print(f"  {h.get('url','')} — events: {', '.join(h.get('events',[]))}")
        return

    if args.remove:
        hooks = [h for h in hooks if h.get("url") != args.remove]
        save_json(hooks_file, hooks)
        print(f"✅ Webhook removed: {args.remove}")
        return

    if args.url:
        events = args.events.split(",") if args.events else ["push.sent", "push.opened", "push.clicked"]
        hook = {"url": args.url, "events": events, "added_at": datetime.now(timezone.utc).isoformat()}
        hooks.append(hook)
        save_json(hooks_file, hooks)
        print(f"✅ Webhook registered: {args.url}")
        log.info("Push webhook registered: %s", args.url)
        return

    print("Use: --url <url> [--events push.sent,push.opened] to add, --remove <url> to delete, --list to view")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="push_notification_agent.py",
        description="EmpireHazeClaw Push Notification Campaign Manager.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_c = sub.add_parser("create", help="Create push notification campaign")
    p_c.add_argument("--campaign-id", dest="campaign_id")
    p_c.add_argument("--name", required=True)
    p_c.add_argument("--title", required=True, help="Notification title (≤50 chars)")
    p_c.add_argument("--body", required=True, help="Notification body (≤200 chars)")
    p_c.add_argument("--url", help="Deep link URL")
    p_c.add_argument("--icon", help="Icon URL")
    p_c.add_argument("--image", help="Image URL")
    p_c.add_argument("--badge", help="Badge count")
    p_c.add_argument("--tag", help="Notification tag (for grouping)")
    p_c.add_argument("--priority", choices=["normal", "high"], default="normal")
    p_c.add_argument("--require-interaction", dest="require_interaction", action="store_true")
    p_c.add_argument("--vibrate", action="store_true", default=True)
    p_c.add_argument("--segment", choices=["all", "active", "inactive", "web", "mobile"])
    p_c.add_argument("--schedule", help="Schedule time (ISO or 'now', 'in1h', 'tomorrow')")
    p_c.add_argument("--ab", action="store_true", help="Enable A/B testing")
    p_c.set_defaults(fn=cmd_create_campaign)

    p_l = sub.add_parser("list", help="List push campaigns")
    p_l.add_argument("--status", choices=["draft", "scheduled", "sending", "sent", "paused"])
    p_l.set_defaults(fn=cmd_list_campaigns)

    p_prev = sub.add_parser("preview", help="Preview push notification")
    p_prev.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_prev.set_defaults(fn=cmd_preview)

    p_send = sub.add_parser("send", help="Send push campaign")
    p_send.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_send.add_argument("--segment", choices=["all", "active", "inactive", "web", "mobile"])
    p_send.add_argument("--limit", type=int)
    p_send.add_argument("--resend", action="store_true")
    p_send.set_defaults(fn=cmd_send)

    p_rep = sub.add_parser("report", help="Show push campaign report")
    p_rep.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_rep.set_defaults(fn=cmd_report)

    p_as = sub.add_parser("add-subscriber", help="Add push subscriber")
    p_as.add_argument("--subscriber-id", dest="subscriber_id")
    p_as.add_argument("--endpoint", required=True, help="Push endpoint/URL")
    p_as.add_argument("--p256dh", help="p256dh key")
    p_as.add_argument("--auth", help="auth key")
    p_as.add_argument("--platform", choices=["web", "ios", "android"], default="web")
    p_as.add_argument("--language", default="en")
    p_as.add_argument("--tags", help="Comma-separated tags")
    p_as.set_defaults(fn=cmd_add_subscriber)

    p_ls = sub.add_parser("subscribers", help="List push subscribers")
    p_ls.add_argument("--platform", choices=["web", "ios", "android"])
    p_ls.add_argument("--status", choices=["active", "inactive"])
    p_ls.set_defaults(fn=cmd_list_subscribers)

    p_sched = sub.add_parser("schedule", help="Schedule a draft campaign")
    p_sched.add_argument("--campaign-id", dest="campaign_id", required=True)
    p_sched.add_argument("--at", required=True, help="Schedule time (ISO or 'now', 'in1h', 'tomorrow')")
    p_sched.set_defaults(fn=cmd_schedule)

    p_pend = sub.add_parser("pending", help="Show pending scheduled campaigns")
    p_pend.set_defaults(fn=cmd_pending)

    p_wh = sub.add_parser("webhook", help="Manage push event webhooks")
    p_wh.add_argument("--url", help="Webhook URL to register")
    p_wh.add_argument("--events", help="Comma-separated events (push.sent,push.opened,push.clicked)")
    p_wh.add_argument("--list", action="store_true", help="List registered webhooks")
    p_wh.add_argument("--remove", help="Remove webhook by URL")
    p_wh.set_defaults(fn=cmd_webhook)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
