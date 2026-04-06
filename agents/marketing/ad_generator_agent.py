#!/usr/bin/env python3
"""
Ad Generator Agent — EmpireHazeClaw Marketing System
Generates multi-format advertising copy and creative briefs.
"""

import argparse
import json
import logging
import random
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
ADS_DIR = DATA_DIR / "ads"
ADS_DB = ADS_DIR / "ads_database.json"
AD_TEMPLATES = ADS_DIR / "templates.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
ADS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [AD-GENERATOR] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "ad_generator.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("ad_generator")


# ── Database ─────────────────────────────────────────────────────────────────
def load_ads() -> dict:
    if ADS_DB.exists():
        try:
            return json.loads(ADS_DB.read_text())
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load ads database: %s", e)
    return {"ads": [], "version": "1.0"}


def save_ads(data: dict) -> None:
    ADS_DB.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_templates() -> dict:
    default_templates = {
        "facebook": {
            "name": "Facebook/Instagram Ads",
            "structure": "Hook (scroll-stopper) → Problem → Solution → CTA",
            "max_chars": 125,
            "placements": ["Feed", "Stories", "Reels"],
            "formula": "EMOTION + URGENCY + OFFER",
        },
        "google": {
            "name": "Google Search Ads",
            "structure": "Headline (≤30) + Description (≤90)",
            "max_chars": 90,
            "headlines": 3,
            "formulas": ["Problem-Solution", "How-To", "Comparison", "Question"],
        },
        "twitter": {
            "name": "Twitter/X Ads",
            "max_chars": 280,
            "structure": "Hook (first line) + Thread hook + CTA",
            "style": "Punchy,provocative, conversational",
        },
        "linkedin": {
            "name": "LinkedIn Ads",
            "max_chars": 3000,
            "structure": "Professional hook → Insight → Credibility → CTA",
            "style": "Thought leadership, data-driven",
        },
        "retargeting": {
            "name": "Retargeting Ads",
            "max_chars": 200,
            "structure": "Reminder + Specific offer + Urgency + CTA",
            "style": "Personal, urgency-driven",
        },
    }
    if AD_TEMPLATES.exists():
        try:
            stored = json.loads(AD_TEMPLATES.read_text())
            stored.update(default_templates)
            return stored
        except Exception:
            pass
    AD_TEMPLATES.write_text(json.dumps(default_templates, indent=2))
    return default_templates


# ── Ad Generation ─────────────────────────────────────────────────────────────
def generate_facebook_ad(offer: str, audience: str, pain_point: str, cta: str = "Get Started") -> dict:
    hooks = [
        f"Still struggling with {pain_point}?",
        f"What if you could {offer} in record time?",
        f"Most {audience} fail because of this one thing.",
        f"Tired of {pain_point}? You're not alone.",
    ]
    bodies = [
        f"We built the solution specifically for {audience} like you.\n\nNo fluff. No complexity. Just results.",
        f"{offer.title()} — without the headache.\n\nWe stripped away everything that doesn't work and kept what does.",
        f"Here's the uncomfortable truth: {pain_point.title()} is costing you time and money.\n\nWe have the fix.",
    ]
    ad = {
        "platform": "facebook",
        "hook": random.choice(hooks),
        "body": random.choice(bodies),
        "cta": cta,
        "hashtags": ["#" + h for h in ["Entrepreneur", "Growth", "Success", "Startups"]][:3],
        "tips": [
            "Use native-looking images (real people, not stock)",
            "Test 3-5 variations with different hooks",
            "Run for at least 5 days before judging performance",
        ],
    }
    return ad


def generate_google_ad(headline_topic: str, offer: str, brand: str = "EmpireHazeClaw") -> dict:
    formulas = [
        f"{headline_topic} — {offer}",
        f"How to {headline_topic} (Free Guide)",
        f"Best {headline_topic} — Compare & Save",
        f"Need {headline_topic}? Get It Now.",
    ]
    h1 = random.choice(formulas)
    h2_options = [
        f"{offer.title()} — Free Trial",
        f"Trusted by 1,000+ {brand} Users",
        f"No Credit Card Required",
    ]
    h2 = random.choice(h2_options)
    descriptions = [
        f"Stop wasting time on {headline_topic.lower()}. {offer.title()}. Start free today.",
        f"Discover the smarter way to {headline_topic.lower()}. {offer.title()}. Results in 30 days.",
    ]
    return {
        "platform": "google",
        "headline_1": h1[:30],
        "headline_2": h2[:30],
        "headline_3": f"{brand} Official Site"[:30],
        "description_1": random.choice(descriptions)[:90],
        "description_2": f"{offer.title()}. Limited time offer.".replace("  ", " ")[:90],
        "tips": ["Use all 3 headlines for maximum real estate", "Include keywords in all headlines"],
    }


def generate_twitter_ad(offer: str, pain_point: str) -> dict:
    tweets = [
        f"Hot take: Most people fail at {pain_point}.\n\nThe reason? They overcomplicate.\n\nSimpler solution: {offer}\n\n↓ Get it free.",
        f"If you're still struggling with {pain_point}, you're doing it wrong.\n\nHere's what actually works:\n\n{offer}\n\n🧵",
        f"The {pain_point} problem? Solved.\n\nWe built {offer}.\n\nNo fluff. Just the thing.\n\n→ Link in bio",
    ]
    return {
        "platform": "twitter",
        "tweet": random.choice(tweets),
        "thread_hook": f"Everything you need to know about {pain_point}:",
        "cta": "Quote tweet + Follow for more",
        "tips": ["Keep the first line scannable", "Use 1-2 relevant emojis max", "Link to landing page"],
    }


def generate_linkedin_ad(offer: str, audience: str) -> dict:
    return {
        "platform": "linkedin",
        "hook": f"Why {audience} consistently outperform others.",
        "body": (
            f"We've analyzed hundreds of high-performing {audience}.\n\n"
            f"Here's what they all have in common:\n\n"
            f"• Clear focus\n"
            f"• Systems over willpower\n"
            f"• {offer}\n\n"
            f"The data is clear. The path is simple. The only question is: are you ready?\n\n"
            f"→ Learn more"
        ),
        "cta": "Download the Guide",
        "hashtags": ["#Leadership", "#Entrepreneurship", "#Strategy", "#Growth"],
        "tips": ["Lead with data or a surprising insight", "Keep paragraphs short", "End with a direct question"],
    }


def generate_retargeting_ad(product: str, discount: str = "20% off") -> dict:
    return {
        "platform": "retargeting",
        "ad_copy": (
            f"Still thinking about {product}?\n\n"
            f"Here's what you missed: {discount} — for the next 24 hours only.\n\n"
            f"Don't leave without claiming your spot.\n\n"
            f"→ Claim Now"
        ),
        "cta": "Claim Your Discount",
        "urgency_elements": ["24-hour countdown", "Limited spots", f"{discount} for returning visitors"],
        "tips": ["Show the exact product they viewed", "Use countdown timer in creative", "Personalize with name if possible"],
    }


# ── Commands ───────────────────────────────────────────────────────────────────
def cmd_generate(args: argparse.Namespace) -> None:
    templates = load_templates()

    if args.template not in templates:
        log.error("Unknown template '%s'. Available: %s", args.template, list(templates.keys()))
        sys.exit(1)

    gen_map = {
        "facebook": generate_facebook_ad,
        "google": generate_google_ad,
        "twitter": generate_twitter_ad,
        "linkedin": generate_linkedin_ad,
        "retargeting": generate_retargeting_ad,
    }

    gen = gen_map.get(args.template)
    if gen is None:
        log.error("Generator not available for '%s'", args.template)
        sys.exit(1)

    if args.template == "facebook":
        ad = gen(offer=args.offer, audience=args.audience or "busy professionals", pain_point=args.pain_point or "inefficiency", cta=args.cta or "Get Started")
    elif args.template == "google":
        ad = gen(headline_topic=args.topic or args.offer, offer=args.offer, brand="EmpireHazeClaw")
    elif args.template == "twitter":
        ad = gen(offer=args.offer, pain_point=args.pain_point or "inefficiency")
    elif args.template == "linkedin":
        ad = gen(offer=args.offer, audience=args.audience or "business professionals")
    elif args.template == "retargeting":
        ad = gen(product=args.offer, discount=args.discount or "20% off")
    else:
        ad = {}

    ad["generated_at"] = datetime.now(timezone.utc).isoformat()
    ad["campaign_id"] = args.campaign_id or None
    ad["status"] = "draft"

    # Save to database
    data = load_ads()
    ad_id = f"ad_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{random.randint(100,999)}"
    ad["id"] = ad_id
    data["ads"].append(ad)
    save_ads(data)

    print(json.dumps(ad, indent=2, ensure_ascii=False))
    log.info("Ad generated: %s (%s)", ad_id, args.template)


def cmd_list(args: argparse.Namespace) -> None:
    data = load_ads()
    ads = data.get("ads", [])

    if args.platform:
        ads = [a for a in ads if a.get("platform") == args.platform]
    if args.campaign_id:
        ads = [a for a in ads if a.get("campaign_id") == args.campaign_id]
    if args.status:
        ads = [a for a in ads if a.get("status") == args.status]

    print(f"Total ads: {len(ads)}")
    print(f"{'ID':<35} {'PLATFORM':<12} {'STATUS':<10} {'GENERATED':<25}")
    print("-" * 90)
    for a in sorted(ads, key=lambda x: x.get("generated_at", ""), reverse=True):
        print(f"{a.get('id',''):<35} {a.get('platform',''):<12} {a.get('status',''):<10} {a.get('generated_at','')[:25]}")


def cmd_approve(args: argparse.Namespace) -> None:
    data = load_ads()
    ad = None
    for a in data["ads"]:
        if a["id"] == args.ad_id:
            ad = a
            break
    if ad is None:
        log.error("Ad '%s' not found", args.ad_id)
        sys.exit(1)
    ad["status"] = "approved"
    ad["approved_at"] = datetime.now(timezone.utc).isoformat()
    save_ads(data)
    print(f"✅ Ad '{args.ad_id}' approved.")
    log.info("Ad approved: %s", args.ad_id)


def cmd_archive(args: argparse.Namespace) -> None:
    data = load_ads()
    ads = [a for a in data["ads"] if a["id"] != args.ad_id]
    removed = [a for a in data["ads"] if a["id"] == args.ad_id]
    data["ads"] = ads
    save_ads(data)
    if removed:
        print(f"🗑️  Ad '{args.ad_id}' archived.")
        log.info("Ad archived: %s", args.ad_id)
    else:
        log.error("Ad '%s' not found", args.ad_id)
        sys.exit(1)


def cmd_templates(args: argparse.Namespace) -> None:
    templates = load_templates()
    if args.format == "json":
        print(json.dumps(templates, indent=2))
    else:
        for key, t in templates.items():
            print(f"\n📝 {key.upper()} — {t.get('name')}")
            print(f"   Max chars: {t.get('max_chars', 'N/A')}")
            print(f"   Structure: {t.get('structure', 'N/A')}")
            print(f"   Formula: {t.get('formula', t.get('formulas', 'N/A'))}")


def cmd_preview(args: argparse.Namespace) -> None:
    data = load_ads()
    ad = None
    for a in data["ads"]:
        if a["id"] == args.ad_id:
            ad = a
            break
    if ad is None:
        log.error("Ad '%s' not found", args.ad_id)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"AD PREVIEW — {ad.get('platform','').upper()} [{ad.get('status','')}]")
    print(f"{'='*60}")
    if ad.get("hook"):
        print(f"🪝 HOOK:\n{ad['hook']}\n")
    if ad.get("body"):
        print(f"📄 BODY:\n{ad['body']}\n")
    if ad.get("headline_1"):
        print(f"📌 HEADLINES:")
        for h in ["headline_1", "headline_2", "headline_3"]:
            if ad.get(h):
                print(f"   [{h.upper()}] {ad[h]}")
        print()
    if ad.get("description_1"):
        print(f"📄 DESCRIPTIONS:")
        for d in ["description_1", "description_2"]:
            if ad.get(d):
                print(f"   {ad[d]}")
        print()
    if ad.get("tweet"):
        print(f"🐦 TWEET:\n{ad['tweet']}\n")
    if ad.get("cta"):
        print(f"👉 CTA: {ad['cta']}")
    if ad.get("hashtags"):
        print(f"   Tags: {' '.join(ad['hashtags'])}")
    print(f"{'='*60}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ad_generator_agent.py",
        description="EmpireHazeClaw Ad Generator — create, manage, and approve ad copy.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # generate
    p_g = sub.add_parser("generate", help="Generate a new ad")
    p_g.add_argument("--template", required=True,
                     choices=["facebook", "google", "twitter", "linkedin", "retargeting"],
                     help="Ad template/platform")
    p_g.add_argument("--offer", required=True, help="What you're offering")
    p_g.add_argument("--audience", help="Target audience description")
    p_g.add_argument("--pain-point", dest="pain_point", help="Primary pain point to address")
    p_g.add_argument("--topic", help="Topic keyword (for Google ads)")
    p_g.add_argument("--cta", help="Call to action text")
    p_g.add_argument("--discount", help="Discount for retargeting ads")
    p_g.add_argument("--campaign-id", dest="campaign_id", help="Link to campaign ID")
    p_g.set_defaults(fn=cmd_generate)

    # list
    p_l = sub.add_parser("list", help="List all ads")
    p_l.add_argument("--platform", choices=["facebook", "google", "twitter", "linkedin", "retargeting"])
    p_l.add_argument("--campaign-id", dest="campaign_id")
    p_l.add_argument("--status", choices=["draft", "approved", "archived"])
    p_l.set_defaults(fn=cmd_list)

    # approve
    p_a = sub.add_parser("approve", help="Approve an ad for launch")
    p_a.add_argument("--ad-id", dest="ad_id", required=True)
    p_a.set_defaults(fn=cmd_approve)

    # archive
    p_ar = sub.add_parser("archive", help="Archive/delete an ad")
    p_ar.add_argument("--ad-id", dest="ad_id", required=True)
    p_ar.set_defaults(fn=cmd_archive)

    # templates
    p_t = sub.add_parser("templates", help="Show available ad templates")
    p_t.add_argument("--format", default="text", choices=["text", "json"])
    p_t.set_defaults(fn=cmd_templates)

    # preview
    p_p = sub.add_parser("preview", help="Preview a generated ad")
    p_p.add_argument("--ad-id", dest="ad_id", required=True)
    p_p.set_defaults(fn=cmd_preview)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
