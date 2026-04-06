#!/usr/bin/env python3
"""
Ad Copywriter Agent
EmpireHazeClaw Creative Suite

Generates advertising copy for multiple platforms and audiences.
Geschwindigkeit über Perfektion: fast drafts, quick iteration.
Ressourceneffizienz: free channels, high ROI focus.
"""

import argparse
import json
import logging
import os
import random
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "creative"
LOG_DIR = BASE_DIR / "logs"
COPY_DB_FILE = DATA_DIR / "ad_copy.json"
BRIEFS_FILE = DATA_DIR / "ad_briefs.json"

LOG_FILE = LOG_DIR / "ad_copywriter.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("AdCopywriter")


def load_json(path: Path):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", path, e)
    return []


def save_json(path: Path, data) -> bool:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)
        return False


def load_copy() -> list:
    data = load_json(COPY_DB_FILE)
    return data if isinstance(data, list) else []


def save_copy(data: list) -> bool:
    return save_json(COPY_DB_FILE, data)


# ─── Copy Generation Engine ───────────────────────────────────────────────────
HOOKS = {
    "curiosity": [
        "What if everything you knew about {topic} was wrong?",
        "The single biggest mistake people make with {topic}...",
        "Nobody talks about this secret to {topic}.",
        "You don't need to be an expert to master {topic}.",
    ],
    "urgency": [
        "This changes everything about {topic} — starting now.",
        "Stop wasting time on {topic} the old way.",
        "Limited insight into {topic} — read before it's gone.",
        "The {topic} window is closing. Here's what to do.",
    ],
    "benefit": [
        "Get results with {topic} in half the time.",
        "Everything you need to know about {topic} — in one place.",
        "Transform your approach to {topic} today.",
        "Proven strategies to {topic} — no fluff.",
    ],
    "social_proof": [
        "Join 10,000+ people who've already discovered {topic}.",
        "Why experts are rethinking {topic}.",
        "The #1 reason people succeed at {topic}.",
        "What top performers know about {topic}.",
    ],
}

PLATFORM_LIMITS = {
    "twitter": {"headline": 70, "body": 280, "hashtag_limit": 3},
    "linkedin": {"headline": 70, "body": 3000, "hashtag_limit": 5},
    "facebook": {"headline": 40, "body": 500, "hashtag_limit": 5},
    "google": {"headline": 30, "description": 90, "hashtag_limit": 0},
    "instagram": {"headline": 125, "body": 2000, "hashtag_limit": 30},
    "email": {"subject": 50, "headline": 60, "body": 500, "hashtag_limit": 0},
}

CALLS_TO_ACTION = [
    "Learn more →",
    "Get started today",
    "Try it free",
    "Claim your spot",
    "Download now",
    "Start for free — no credit card",
    "Join now",
    "See for yourself",
    "Discover more",
    "Unlock it now",
]


def generate_copy(
    topic: str,
    platform: str = "twitter",
    tone: str = "professional",
    hook_type: str = "curiosity",
    num_variants: int = 3,
    audience: str = "general",
    language: str = "en",
) -> list[dict]:
    """Generate ad copy variants for a given topic and platform."""
    logger.info("Generating %d copy variants for '%s' on %s", num_variants, topic, platform)

    if platform not in PLATFORM_LIMITS:
        raise ValueError(f"Unknown platform: {platform}. Available: {', '.join(PLATFORM_LIMITS.keys())}")

    tone_styles = {
        "professional": ("authoritative", "trustworthy", "results-driven"),
        "casual": ("conversational", "friendly", "relatable"),
        "urgent": ("direct", "fast-paced", "high-stakes"),
        "playful": ("witty", "light", "memorable"),
        "empathetic": ("understanding", "supportive", "human"),
    }
    styles = tone_styles.get(tone, tone_styles["professional"])

    variants = []
    used_hooks = []

    for i in range(num_variants):
        hook_key = random.choice(list(HOOKS.keys())) if hook_type == "random" else hook_type
        hook_templates = HOOKS.get(hook_key, HOOKS["curiosity"])
        hook = random.choice([h for h in hook_templates if h not in used_hooks] or hook_templates)
        used_hooks.append(hook)
        headline = hook.replace("{topic}", topic)

        limits = PLATFORM_LIMITS[platform]
        headline = headline[: limits["headline"]]

        body_templates = [
            f"Discover how to {topic.lower()} with strategies that actually work. {random.choice(styles).capitalize()} insights, practical steps, and real results — no theory, just what works.",
            f"Stop guessing. Start {topic.lower()} with a proven approach designed for {audience} audiences. Built for people who want outcomes, not excuses.",
            f"{headline.split()[0].capitalize()} — {topic} doesn't have to be complicated. Our approach gives you clarity, speed, and results. {random.choice(styles).capitalize()}.",
            f"Ready to master {topic}? You don't need another course or framework. You need the right strategy. Start here.",
            f"Why struggle with {topic}? The solution is simpler than you think. Built for {audience} professionals who value their time.",
        ]
        body = random.choice(body_templates)
        if "body" in limits:
            body = body[: limits["body"]]

        cta = random.choice(CALLS_TO_ACTION)

        hashtags = []
        if platform in ["twitter", "instagram", "linkedin"]:
            tag_limit = limits["hashtag_limit"]
            for tag in [topic.replace(" ", ""), topic.split()[0].lower(), "AI", "growth", "tips"][:tag_limit]:
                hashtags.append(f"#{tag}")

        variant = {
            "id": str(uuid.uuid4()),
            "topic": topic,
            "platform": platform,
            "tone": tone,
            "hook_type": hook_key,
            "headline": headline,
            "body": body,
            "cta": cta,
            "hashtags": hashtags if hashtags else [],
            "language": language,
            "created_at": datetime.utcnow().isoformat(),
        }
        variants.append(variant)

    # Save to DB
    copy_db = load_copy()
    copy_db.extend(variants)
    save_copy(copy_db)

    return variants


def format_variant(v: dict) -> str:
    platform = v["platform"]
    lines = [
        f"─── {platform.upper()} ───",
        f"Headline: {v['headline']}",
    ]
    if v.get("body"):
        lines.append(f"Body: {v['body']}")
    if v.get("cta"):
        lines.append(f"CTA: {v['cta']}")
    if v.get("hashtags"):
        lines.append(f"Hashtags: {' '.join(v['hashtags'])}")
    lines.append(f"[{v['id']}]")
    return "\n".join(lines)


def generate_campaign(
    topic: str,
    platforms: list[str],
    tone: str = "professional",
    num_per_platform: int = 2,
    audience: str = "general",
    language: str = "en",
) -> dict:
    """Generate a multi-platform campaign."""
    logger.info("Generating campaign for '%s' across %s", topic, platforms)
    all_variants = []
    for platform in platforms:
        variants = generate_copy(
            topic=topic,
            platform=platform,
            tone=tone,
            num_variants=num_per_platform,
            audience=audience,
            language=language,
        )
        all_variants.extend(variants)

    campaign = {
        "id": str(uuid.uuid4()),
        "topic": topic,
        "platforms": platforms,
        "tone": tone,
        "audience": audience,
        "language": language,
        "variants": all_variants,
        "created_at": datetime.utcnow().isoformat(),
    }

    briefs = load_json(BRIEFS_FILE)
    briefs.append(campaign)
    save_json(BRIEFS_FILE, briefs)

    return campaign


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_generate(args):
    variants = generate_copy(
        topic=args.topic,
        platform=args.platform,
        tone=args.tone,
        hook_type=args.hook,
        num_variants=args.num,
        audience=args.audience,
        language=args.language,
    )
    print(f"\n✅ Generated {len(variants)} variant(s)\n")
    for v in variants:
        print(format_variant(v))
        print()


def cmd_campaign(args):
    platforms = args.platforms.split(",") if args.platforms else [args.platform]
    campaign = generate_campaign(
        topic=args.topic,
        platforms=platforms,
        tone=args.tone,
        num_per_platform=args.num_per_platform,
        audience=args.audience,
        language=args.language,
    )
    print(f"\n✅ Campaign generated: {campaign['id']}")
    print(f"   Topic: {campaign['topic']}")
    print(f"   Platforms: {', '.join(campaign['platforms'])}")
    print(f"   Variants: {len(campaign['variants'])}\n")
    for v in campaign["variants"]:
        print(format_variant(v))
        print()


def cmd_list(args):
    copy_db = load_copy()
    if not copy_db:
        print("No copy found. Generate some with: ad-copywriter generate --topic '...'")
        return
    if args.topic:
        copy_db = [c for c in copy_db if args.topic.lower() in c.get("topic", "").lower()]
    if args.platform:
        copy_db = [c for c in copy_db if c.get("platform") == args.platform]
    print(f"\n{'#':<4} {'Platform':<12} {'Tone':<15} {'Headline':<50} {'ID':<10}")
    print("-" * 100)
    for i, c in enumerate(copy_db[-50:], 1):  # last 50
        print(f"{i:<4} {c.get('platform',''):<12} {c.get('tone',''):<15} {c.get('headline','')[:48]:<50} {c['id'][:10]}")
    print(f"\nTotal: {len(copy_db)} copy piece(s) in DB")


def cmd_show(args):
    copy_db = load_copy()
    item = next((c for c in copy_db if c["id"] == args.copy_id), None)
    if not item:
        raise ValueError(f"Copy not found: {args.copy_id}")
    print(format_variant(item))


def cmd_platforms(args):
    print("\nSupported Platforms:")
    print("=" * 50)
    for platform, limits in PLATFORM_LIMITS.items():
        print(f"  {platform:<15} headline≤{limits.get('headline','?')} | body≤{limits.get('body', limits.get('description','?'))} | hashtags≤{limits.get('hashtag_limit','?')}")


def cmd_hooks(args):
    print("\nHook Types:")
    for htype, templates in HOOKS.items():
        print(f"\n  {htype.upper()}:")
        for t in templates:
            print(f"    - {t.replace('{topic}', 'TOPIC')}")


def main():
    parser = argparse.ArgumentParser(
        prog="ad-copywriter",
        description="EmpireHazeClaw Ad Copywriter — generate platform-optimized advertising copy.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Generate ad copy variants")
    p_gen.add_argument("--topic", required=True, help="Product/topic to advertise")
    p_gen.add_argument("--platform", default="twitter", choices=list(PLATFORM_LIMITS.keys()), help="Platform (default: twitter)")
    p_gen.add_argument("--tone", default="professional", choices=["professional", "casual", "urgent", "playful", "empathetic"])
    p_gen.add_argument("--hook", default="random", choices=list(HOOKS.keys()) + ["random"], help="Hook type")
    p_gen.add_argument("--num", type=int, default=3, help="Number of variants (default: 3)")
    p_gen.add_argument("--audience", default="general", help="Target audience description")
    p_gen.add_argument("--language", default="en", help="Language code (en/de)")
    p_gen.set_defaults(fn=cmd_generate)

    p_cmp = sub.add_parser("campaign", help="Generate multi-platform campaign")
    p_cmp.add_argument("--topic", required=True, help="Product/topic")
    p_cmp.add_argument("--platforms", help="Comma-separated platforms (default: --platform)")
    p_cmp.add_argument("--platform", default="twitter", help="Primary platform")
    p_cmp.add_argument("--tone", default="professional", choices=["professional", "casual", "urgent", "playful", "empathetic"])
    p_cmp.add_argument("--num-per-platform", type=int, default=2, help="Variants per platform")
    p_cmp.add_argument("--audience", default="general")
    p_cmp.add_argument("--language", default="en")
    p_cmp.set_defaults(fn=cmd_campaign)

    p_list = sub.add_parser("list", help="List saved copy")
    p_list.add_argument("--topic", help="Filter by topic")
    p_list.add_argument("--platform", help="Filter by platform")
    p_list.set_defaults(fn=cmd_list)

    p_show = sub.add_parser("show", help="Show a specific copy piece")
    p_show.add_argument("copy_id", help="Copy ID")
    p_show.set_defaults(fn=cmd_show)

    p_plat = sub.add_parser("platforms", help="List supported platforms with limits")
    p_plat.set_defaults(fn=cmd_platforms)

    p_hooks = sub.add_parser("hooks", help="List hook types")
    p_hooks.set_defaults(fn=cmd_hooks)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
