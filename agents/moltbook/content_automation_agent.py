#!/usr/bin/env python3
"""
Content Automation Agent - Moltbook Content Division
Automates content creation, scheduling, and multi-platform publishing.

Inspired by SOUL.md: CEO mindset, Eigenverantwortung, Geschwindigkeit über Perfektion
"""

import argparse
import json
import logging
import os
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "content_automation"
CONTENT_FILE = DATA_DIR / "content.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"
TEMPLATES_FILE = DATA_DIR / "templates.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CONTENT-AUTO] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "content_automation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("ContentAutomation")


# ─── Data Helpers ─────────────────────────────────────────────────────────────
def load_json(path: Path, default: dict) -> dict:
    """Load JSON, return default if missing or invalid."""
    if not path.exists():
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.error(f"Failed to load {path}: {e}")
        return default


def save_json(path: Path, data: dict) -> None:
    """Save data to JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        log.error(f"Failed to save {path}: {e}")
        raise


def load_content() -> dict:
    """Load content database."""
    return load_json(CONTENT_FILE, {"pieces": [], "last_updated": None})


def save_content(data: dict) -> None:
    """Save content database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(CONTENT_FILE, data)


def load_schedule() -> dict:
    """Load publishing schedule."""
    return load_json(SCHEDULE_FILE, {"scheduled": [], "last_updated": None})


def save_schedule(data: dict) -> None:
    """Save publishing schedule."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(SCHEDULE_FILE, data)


def load_templates() -> dict:
    """Load content templates."""
    defaults = {
        "blog_post": {
            "name": "Blog Post",
            "structure": ["title", "introduction", "main_points", "conclusion"],
            "tone_options": ["professional", "casual", "educational", "persuasive"],
        },
        "social_post": {
            "name": "Social Post",
            "max_length": 280,
            "hashtags": True,
            "emoji_support": True,
        },
        "email_newsletter": {
            "name": "Email Newsletter",
            "structure": ["subject", "preview_text", "body", "cta"],
            "personalization": True,
        },
    }
    return load_json(TEMPLATES_FILE, defaults)


def load_config() -> dict:
    """Load configuration."""
    defaults = {
        "default_platforms": ["twitter", "linkedin", "blog"],
        "auto_hashtag": True,
        "min_content_length": 100,
        "publishing_timezone": "UTC",
        "approval_required": False,
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── Content Generation ───────────────────────────────────────────────────────
CONTENT_IDEAS = [
    "5 productivity hacks that actually work",
    "How AI is transforming small business workflows",
    "The ultimate guide to remote work optimization",
    "Why automation is your competitive advantage",
    "Building sustainable business systems in 2026",
    "From burnout to breakthrough: a founder's journey",
    "The science of high-performance teams",
    "Mastering your morning routine for peak performance",
    "Digital tools that save 10+ hours per week",
    "How to scale without burning out",
]

CONTENT_TONES = ["professional", "casual", "educational", "persuasive", "inspirational"]


def generate_content(topic: str, content_type: str, tone: str = "professional") -> dict:
    """Generate content piece from topic and parameters."""
    timestamp = datetime.utcnow().isoformat()
    word_count = random.randint(300, 1200) if content_type == "blog_post" else random.randint(50, 280)
    
    content_piece = {
        "id": generate_id(load_content().get("pieces", [])),
        "topic": topic,
        "type": content_type,
        "tone": tone,
        "title": topic.title() if topic else random.choice(CONTENT_IDEAS).title(),
        "body": f"Generated {tone} {content_type} about {topic or 'general productivity'}. "
                f"This content piece contains approximately {word_count} words and is "
                f"designed to engage and provide value to the target audience.",
        "word_count": word_count,
        "hashtags": generate_hashtags(topic) if content_type == "social_post" else [],
        "status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
    return content_piece


def generate_hashtags(topic: str) -> List[str]:
    """Generate relevant hashtags for topic."""
    base_tags = ["#Productivity", "#Business", "#Growth"]
    if topic:
        topic_tags = [f"#{word.capitalize()}" for word in topic.split()[:3]]
        base_tags.extend(topic_tags)
    return list(set(base_tags))[:5]


def promote_content(content_id: int, target_platform: str) -> bool:
    """Mark content as ready for platform."""
    data = load_content()
    for piece in data.get("pieces", []):
        if piece["id"] == content_id:
            if "platforms" not in piece:
                piece["platforms"] = {}
            piece["platforms"][target_platform] = {
                "status": "ready",
                "scheduled_at": None,
                "published_at": None,
            }
            piece["updated_at"] = datetime.utcnow().isoformat()
            save_content(data)
            log.info(f"Content #{content_id} prepared for {target_platform}")
            return True
    return False


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_generate(args) -> None:
    """Generate new content piece."""
    log.info(f"Generating {args.type} content (topic: {args.topic or 'random'}, tone: {args.tone})")
    
    content = generate_content(args.topic, args.type, args.tone)
    data = load_content()
    data["pieces"].append(content)
    save_content(data)
    
    print(f"✅ Created content #{content['id']}: {content['title']}")
    print(f"   Type: {content['type']}, Tone: {content['tone']}")
    print(f"   Words: {content['word_count']}")
    if content["hashtags"]:
        print(f"   Tags: {', '.join(content['hashtags'])}")


def cmd_list(args) -> None:
    """List all content pieces."""
    data = load_content()
    pieces = data.get("pieces", [])
    
    if not pieces:
        print("📝 No content pieces found. Generate some first!")
        return
    
    status_filter = args.status.lower() if args.status else None
    type_filter = args.type.lower() if args.type else None
    
    filtered = pieces
    if status_filter:
        filtered = [p for p in filtered if p.get("status") == status_filter]
    if type_filter:
        filtered = [p for p in filtered if p.get("type") == type_filter]
    
    print(f"📝 Content Pieces ({len(filtered)} of {len(pieces)} total):")
    print("-" * 70)
    
    for p in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True):
        platforms_str = ", ".join(p.get("platforms", {}).keys()) or "none"
        print(f"  #{p['id']} | {p['status']:8} | {p['type']:12} | {p['title'][:40]}")
        print(f"        Platforms: {platforms_str} | Created: {p.get('created_at', 'N/A')[:10]}")


def cmd_view(args) -> None:
    """View content piece details."""
    data = load_content()
    for piece in data.get("pieces", []):
        if piece["id"] == args.id:
            print(f"\n📄 Content #{piece['id']}")
            print("=" * 50)
            print(f"Title:    {piece.get('title', 'N/A')}")
            print(f"Type:     {piece.get('type', 'N/A')}")
            print(f"Tone:     {piece.get('tone', 'N/A')}")
            print(f"Status:   {piece.get('status', 'N/A')}")
            print(f"Words:    {piece.get('word_count', 'N/A')}")
            print(f"Created:  {piece.get('created_at', 'N/A')}")
            print(f"Updated:  {piece.get('updated_at', 'N/A')}")
            if piece.get("hashtags"):
                print(f"Hashtags: {', '.join(piece['hashtags'])}")
            if piece.get("platforms"):
                print("Platforms:")
                for plat, info in piece["platforms"].items():
                    print(f"  - {plat}: {info['status']}")
            print(f"\nBody:\n{piece.get('body', 'N/A')[:500]}...")
            return
    
    print(f"❌ Content #{args.id} not found.")


def cmd_schedule(args) -> None:
    """Schedule content for publishing."""
    data = load_content()
    piece = None
    for p in data.get("pieces", []):
        if p["id"] == args.content_id:
            piece = p
            break
    
    if not piece:
        print(f"❌ Content #{args.content_id} not found.")
        return
    
    schedule_data = load_schedule()
    schedule_entry = {
        "id": generate_id(schedule_data.get("scheduled", [])),
        "content_id": args.content_id,
        "platform": args.platform,
        "scheduled_at": args.datetime,
        "status": "scheduled",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    schedule_data["scheduled"].append(schedule_entry)
    save_schedule(schedule_data)
    
    promote_content(args.content_id, args.platform)
    
    print(f"✅ Scheduled content #{args.content_id} for {args.platform} at {args.datetime}")


def cmd_schedule_list(args) -> None:
    """List scheduled publishing."""
    data = load_schedule()
    scheduled = data.get("scheduled", [])
    
    if not scheduled:
        print("📅 No scheduled content.")
        return
    
    print(f"📅 Scheduled Content ({len(scheduled)} items):")
    print("-" * 70)
    
    for s in sorted(scheduled, key=lambda x: x.get("scheduled_at", "")):
        print(f"  #{s['id']} | Content#{s['content_id']} | {s['platform']:10} | {s['scheduled_at']} | {s['status']}")


def cmd_publish(args) -> None:
    """Mark content as published on platform."""
    if promote_content(args.content_id, args.platform):
        print(f"✅ Content #{args.content_id} marked as published on {args.platform}")
    else:
        print(f"❌ Failed to update content #{args.content_id}")


def cmd_delete(args) -> None:
    """Delete content piece."""
    data = load_content()
    original_len = len(data.get("pieces", []))
    data["pieces"] = [p for p in data.get("pieces", []) if p["id"] != args.id]
    
    if len(data["pieces"]) < original_len:
        save_content(data)
        print(f"✅ Deleted content #{args.id}")
    else:
        print(f"❌ Content #{args.id} not found.")


def cmd_stats(args) -> None:
    """Show content statistics."""
    data = load_content()
    pieces = data.get("pieces", [])
    
    if not pieces:
        print("📊 No content data available.")
        return
    
    status_counts = {}
    type_counts = {}
    platform_counts = {}
    
    for p in pieces:
        status_counts[p.get("status", "unknown")] = status_counts.get(p.get("status"), 0) + 1
        type_counts[p.get("type", "unknown")] = type_counts.get(p.get("type"), 0) + 1
        for plat in p.get("platforms", {}).keys():
            platform_counts[plat] = platform_counts.get(plat, 0) + 1
    
    print("\n📊 Content Statistics")
    print("=" * 50)
    print(f"Total Pieces: {len(pieces)}")
    print(f"\nBy Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print(f"\nBy Type:")
    for ptype, count in sorted(type_counts.items()):
        print(f"  {ptype}: {count}")
    if platform_counts:
        print(f"\nBy Platform:")
        for plat, count in sorted(platform_counts.items()):
            print(f"  {plat}: {count}")


def cmd_templates(args) -> None:
    """List available content templates."""
    templates = load_templates()
    print("\n📋 Available Content Templates")
    print("=" * 50)
    for tid, template in templates.items():
        print(f"\n{template['name']} ({tid})")
        if "structure" in template:
            print(f"  Structure: {' → '.join(template['structure'])}")
        if "max_length" in template:
            print(f"  Max Length: {template['max_length']} chars")
        if "tone_options" in template:
            print(f"  Tones: {', '.join(template['tone_options'])}")


def cmd_config(args) -> None:
    """Show current configuration."""
    config = load_config()
    print("\n⚙️ Content Automation Config")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Content Automation Agent - Moltbook Division",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --type blog_post --topic "AI productivity"
  %(prog)s list --status draft --type social_post
  %(prog)s view --id 1
  %(prog)s schedule --content-id 1 --platform twitter --datetime "2026-03-28 10:00"
  %(prog)s schedule-list
  %(prog)s publish --content-id 1 --platform linkedin
  %(prog)s delete --id 1
  %(prog)s stats
  %(prog)s templates
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate
    p_generate = subparsers.add_parser("generate", help="Generate new content")
    p_generate.add_argument("--type", "-t", default="blog_post",
                           choices=["blog_post", "social_post", "email_newsletter"],
                           help="Content type")
    p_generate.add_argument("--topic", "-m", default=None, help="Content topic")
    p_generate.add_argument("--tone", default="professional",
                           choices=CONTENT_TONES, help="Content tone")
    
    # List
    p_list = subparsers.add_parser("list", help="List all content")
    p_list.add_argument("--status", "-s", default=None, help="Filter by status")
    p_list.add_argument("--type", "-t", default=None, help="Filter by type")
    
    # View
    p_view = subparsers.add_parser("view", help="View content details")
    p_view.add_argument("--id", "-i", type=int, required=True, help="Content ID")
    
    # Schedule
    p_schedule = subparsers.add_parser("schedule", help="Schedule content for publishing")
    p_schedule.add_argument("--content-id", "-c", type=int, required=True, help="Content ID")
    p_schedule.add_argument("--platform", "-p", required=True, help="Target platform")
    p_schedule.add_argument("--datetime", "-d", required=True, help="Schedule datetime (YYYY-MM-DD HH:MM)")
    
    # Schedule List
    subparsers.add_parser("schedule-list", help="List scheduled content")
    
    # Publish
    p_publish = subparsers.add_parser("publish", help="Mark content as published")
    p_publish.add_argument("--content-id", "-c", type=int, required=True, help="Content ID")
    p_publish.add_argument("--platform", "-p", required=True, help="Target platform")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete content piece")
    p_delete.add_argument("--id", "-i", type=int, required=True, help="Content ID")
    
    # Stats
    subparsers.add_parser("stats", help="Show content statistics")
    
    # Templates
    subparsers.add_parser("templates", help="List available templates")
    
    # Config
    subparsers.add_parser("config", help="Show current configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "generate":
            cmd_generate(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "view":
            cmd_view(args)
        elif args.command == "schedule":
            cmd_schedule(args)
        elif args.command == "schedule-list":
            cmd_schedule_list(args)
        elif args.command == "publish":
            cmd_publish(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "stats":
            cmd_stats(args)
        elif args.command == "templates":
            cmd_templates(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
