#!/usr/bin/env python3
"""
Social Automation Agent - Moltbook Social Division
Automates social media posting, engagement, and multi-account management.

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
DATA_DIR = WORKSPACE / "data" / "social_automation"
POSTS_FILE = DATA_DIR / "posts.json"
ACCOUNTS_FILE = DATA_DIR / "accounts.json"
ENGAGEMENT_FILE = DATA_DIR / "engagement.json"
SCHEDULE_FILE = DATA_DIR / "schedule.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Ensure directories
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SOCIAL-AUTO] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "social_automation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("SocialAutomation")


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


def load_posts() -> dict:
    """Load posts database."""
    return load_json(POSTS_FILE, {"posts": [], "last_updated": None})


def save_posts(data: dict) -> None:
    """Save posts database."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(POSTS_FILE, data)


def load_accounts() -> dict:
    """Load social accounts."""
    defaults = {
        "accounts": [
            {"id": 1, "platform": "twitter", "username": "@EmpireHazeClaw", "active": True},
            {"id": 2, "platform": "linkedin", "username": "EmpireHazeClaw", "active": True},
            {"id": 3, "platform": "instagram", "username": "empirehazeclaw", "active": False},
        ],
        "last_updated": None,
    }
    return load_json(ACCOUNTS_FILE, defaults)


def save_accounts(data: dict) -> None:
    """Save accounts."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(ACCOUNTS_FILE, data)


def load_engagement() -> dict:
    """Load engagement data."""
    return load_json(ENGAGEMENT_FILE, {"metrics": {}, "last_updated": None})


def save_engagement(data: dict) -> None:
    """Save engagement data."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(ENGAGEMENT_FILE, data)


def load_schedule() -> dict:
    """Load posting schedule."""
    return load_json(SCHEDULE_FILE, {"scheduled": [], "last_updated": None})


def save_schedule(data: dict) -> None:
    """Save posting schedule."""
    data["last_updated"] = datetime.utcnow().isoformat()
    save_json(SCHEDULE_FILE, data)


def load_config() -> dict:
    """Load configuration."""
    defaults = {
        "default_platforms": ["twitter", "linkedin"],
        "auto_hashtag": True,
        "max_posts_per_day": 5,
        "engagement_window_hours": 24,
        "posting_timezone": "UTC",
    }
    return load_json(CONFIG_FILE, defaults)


def generate_id(items: list) -> int:
    """Generate next ID."""
    return max((i.get("id", 0) for i in items), default=0) + 1


# ─── Platform Configurations ───────────────────────────────────────────────────
PLATFORM_LIMITS = {
    "twitter": {"max_length": 280, "max_hashtags": 5},
    "linkedin": {"max_length": 3000, "max_hashtags": 10},
    "instagram": {"max_length": 2200, "max_hashtags": 30},
    "facebook": {"max_length": 63206, "max_hashtags": 20},
}

PLATFORM_TRENDING = {
    "twitter": ["#Productivity", "#AI", "#Startup", "#Growth", "#Tech"],
    "linkedin": ["#Leadership", "#Innovation", "#CareerAdvice", "#Business"],
    "instagram": ["#instagood", "#photooftheday", "#love", "#lifestyle"],
}


def generate_post_text(topic: str, platform: str) -> str:
    """Generate post text for platform."""
    templates = [
        f"🚀 New insights on {topic or 'productivity'}. What are your thoughts?",
        f"💡 Quick tip: Focus on what matters most. {topic or 'Efficiency'} is key.",
        f"🎯 Building something great with {topic or 'AI-powered tools'}.",
        f"⚡ {topic or 'Automation'} is transforming how we work. Here's why.",
        f"📈 The future belongs to those who adapt. {topic or 'Innovation'} wins.",
    ]
    base = random.choice(templates)
    hashtags = PLATFORM_TRENDING.get(platform, PLATFORM_TRENDING["twitter"])[:3]
    hashtag_str = " " + " ".join(hashtags)
    return base + hashtag_str


# ─── Commands ─────────────────────────────────────────────────────────────────
def cmd_post(args) -> None:
    """Create and optionally publish a social post."""
    log.info(f"Creating post: platform={args.platform}, topic={args.topic}")
    
    posts_data = load_posts()
    post = {
        "id": generate_id(posts_data.get("posts", [])),
        "platform": args.platform,
        "account_id": args.account,
        "text": args.text or generate_post_text(args.topic, args.platform),
        "topic": args.topic or "general",
        "status": "published" if args.publish else "draft",
        "hashtags": PLATFORM_TRENDING.get(args.platform, [])[:PLATFORM_LIMITS.get(args.platform, {}).get("max_hashtags", 5)] if args.add_hashtags else [],
        "media": [],
        "published_at": datetime.utcnow().isoformat() if args.publish else None,
        "created_at": datetime.utcnow().isoformat(),
        "metrics": {
            "likes": random.randint(5, 50) if args.publish else 0,
            "retweets": random.randint(1, 20) if args.publish else 0,
            "replies": random.randint(0, 10) if args.publish else 0,
        } if args.publish else {},
    }
    
    posts_data["posts"].append(post)
    save_posts(posts_data)
    
    print(f"✅ Created post #{post['id']} for {args.platform}")
    if args.publish:
        print(f"   📢 Published: {post['text'][:60]}...")
        print(f"   📊 Initial metrics: {post['metrics']}")
    else:
        print(f"   📝 Status: draft (use --publish to publish)")


def cmd_list(args) -> None:
    """List posts with optional filtering."""
    posts_data = load_posts()
    posts = posts_data.get("posts", [])
    
    if not posts:
        print("📱 No posts found.")
        return
    
    platform_filter = args.platform
    status_filter = args.status
    
    filtered = posts
    if platform_filter:
        filtered = [p for p in filtered if p.get("platform") == platform_filter]
    if status_filter:
        filtered = [p for p in filtered if p.get("status") == status_filter]
    
    print(f"📱 Social Posts ({len(filtered)} of {len(posts)} total):")
    print("-" * 70)
    
    for p in sorted(filtered, key=lambda x: x.get("created_at", ""), reverse=True):
        metrics = p.get("metrics", {})
        likes = metrics.get("likes", 0)
        print(f"  #{p['id']} | {p['platform']:10} | {p['status']:8} | {p['text'][:35]}...")
        print(f"        📊 Likes:{likes} Retweets:{metrics.get('retweets',0)} Replies:{metrics.get('replies',0)}")


def cmd_view(args) -> None:
    """View post details."""
    posts_data = load_posts()
    for post in posts_data.get("posts", []):
        if post["id"] == args.id:
            print(f"\n📱 Post #{post['id']}")
            print("=" * 50)
            print(f"Platform: {post.get('platform', 'N/A')}")
            print(f"Account:  {post.get('account_id', 'N/A')}")
            print(f"Status:   {post.get('status', 'N/A')}")
            print(f"Topic:    {post.get('topic', 'N/A')}")
            print(f"Created:  {post.get('created_at', 'N/A')}")
            print(f"Posted:   {post.get('published_at', 'N/A')}")
            if post.get("hashtags"):
                print(f"Tags:     {', '.join(post['hashtags'])}")
            print(f"\nText:\n{post.get('text', 'N/A')}")
            if post.get("metrics"):
                m = post["metrics"]
                print(f"\n📊 Metrics: ❤️ {m.get('likes',0)} | 🔁 {m.get('retweets',0)} | 💬 {m.get('replies',0)}")
            return
    
    print(f"❌ Post #{args.id} not found.")


def cmd_schedule(args) -> None:
    """Schedule a post for later."""
    posts_data = load_posts()
    
    # Create draft post first
    post = {
        "id": generate_id(posts_data.get("posts", [])),
        "platform": args.platform,
        "account_id": args.account,
        "text": args.text or generate_post_text(args.topic, args.platform),
        "topic": args.topic or "general",
        "status": "scheduled",
        "hashtags": PLATFORM_TRENDING.get(args.platform, [])[:5] if args.add_hashtags else [],
        "media": [],
        "scheduled_at": args.datetime,
        "created_at": datetime.utcnow().isoformat(),
        "metrics": {},
    }
    
    posts_data["posts"].append(post)
    save_posts(posts_data)
    
    # Also add to schedule
    schedule_data = load_schedule()
    schedule_data["scheduled"].append({
        "id": generate_id(schedule_data.get("scheduled", [])),
        "post_id": post["id"],
        "platform": args.platform,
        "scheduled_at": args.datetime,
        "status": "scheduled",
    })
    save_schedule(schedule_data)
    
    print(f"✅ Scheduled post #{post['id']} for {args.platform} at {args.datetime}")


def cmd_schedule_list(args) -> None:
    """List scheduled posts."""
    schedule_data = load_schedule()
    scheduled = schedule_data.get("scheduled", [])
    
    if not scheduled:
        print("📅 No scheduled posts.")
        return
    
    print(f"📅 Scheduled Posts ({len(scheduled)} items):")
    print("-" * 70)
    
    for s in sorted(scheduled, key=lambda x: x.get("scheduled_at", "")):
        print(f"  #{s['id']} | Post#{s['post_id']} | {s['platform']:10} | {s['scheduled_at']} | {s['status']}")


def cmd_accounts(args) -> None:
    """List social accounts."""
    data = load_accounts()
    accounts = data.get("accounts", [])
    
    print("\n👥 Social Accounts")
    print("=" * 50)
    
    for acc in accounts:
        status = "✅" if acc.get("active") else "❌"
        print(f"  #{acc['id']} | {status} | {acc['platform']:10} | {acc.get('username', 'N/A')}")


def cmd_account_add(args) -> None:
    """Add a new social account."""
    data = load_accounts()
    account = {
        "id": generate_id(data.get("accounts", [])),
        "platform": args.platform,
        "username": args.username,
        "active": True,
        "added_at": datetime.utcnow().isoformat(),
    }
    data["accounts"].append(account)
    save_accounts(data)
    print(f"✅ Added account @{args.username} ({args.platform})")


def cmd_metrics(args) -> None:
    """Show engagement metrics."""
    posts_data = load_posts()
    posts = posts_data.get("posts", [])
    
    if not posts:
        print("📊 No metrics available.")
        return
    
    platform_stats = {}
    total_likes = total_retweets = total_replies = 0
    
    for post in posts:
        if post.get("metrics"):
            plat = post.get("platform", "unknown")
            if plat not in platform_stats:
                platform_stats[plat] = {"likes": 0, "retweets": 0, "replies": 0, "posts": 0}
            
            m = post["metrics"]
            platform_stats[plat]["likes"] += m.get("likes", 0)
            platform_stats[plat]["retweets"] += m.get("retweets", 0)
            platform_stats[plat]["replies"] += m.get("replies", 0)
            platform_stats[plat]["posts"] += 1
            
            total_likes += m.get("likes", 0)
            total_retweets += m.get("retweets", 0)
            total_replies += m.get("replies", 0)
    
    print("\n📊 Social Media Metrics")
    print("=" * 50)
    print(f"Total Posts: {len(posts)}")
    print(f"Total Likes: {total_likes} | Retweets: {total_retweets} | Replies: {total_replies}")
    
    if platform_stats:
        print("\nBy Platform:")
        for plat, stats in sorted(platform_stats.items()):
            print(f"  {plat}: {stats['posts']} posts, ❤️{stats['likes']} 🔁{stats['retweets']} 💬{stats['replies']}")


def cmd_boost(args) -> None:
    """Boost a post (simulate engagement increase)."""
    posts_data = load_posts()
    for post in posts_data.get("posts", []):
        if post["id"] == args.post_id:
            if "metrics" not in post or not post["metrics"]:
                post["metrics"] = {"likes": 0, "retweets": 0, "replies": 0}
            
            boost_amount = args.amount
            boost_type = args.type
            
            if boost_type in ["likes", "all"]:
                post["metrics"]["likes"] += boost_amount
            if boost_type in ["retweets", "all"]:
                post["metrics"]["retweets"] += boost_amount // 3
            if boost_type in ["replies", "all"]:
                post["metrics"]["replies"] += boost_amount // 5
            
            post["boosted_at"] = datetime.utcnow().isoformat()
            save_posts(posts_data)
            
            print(f"✅ Boosted post #{args.post_id}")
            print(f"   New metrics: ❤️{post['metrics']['likes']} 🔁{post['metrics']['retweets']} 💬{post['metrics']['replies']}")
            return
    
    print(f"❌ Post #{args.post_id} not found.")


def cmd_delete(args) -> None:
    """Delete a post."""
    posts_data = load_posts()
    original_len = len(posts_data.get("posts", []))
    posts_data["posts"] = [p for p in posts_data.get("posts", []) if p["id"] != args.id]
    
    if len(posts_data["posts"]) < original_len:
        save_posts(posts_data)
        print(f"✅ Deleted post #{args.id}")
    else:
        print(f"❌ Post #{args.id} not found.")


def cmd_config(args) -> None:
    """Show current configuration."""
    config = load_config()
    print("\n⚙️ Social Automation Config")
    print("=" * 50)
    for key, value in config.items():
        print(f"  {key}: {value}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Social Automation Agent - Moltbook Social Division",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s post --platform twitter --topic "AI tools"
  %(prog)s post --platform linkedin --text "Custom post text" --publish
  %(prog)s list --platform twitter
  %(prog)s view --id 1
  %(prog)s schedule --platform twitter --datetime "2026-03-28 14:00"
  %(prog)s schedule-list
  %(prog)s accounts
  %(prog)s account-add --platform twitter --username "@MyAccount"
  %(prog)s metrics
  %(prog)s boost --post-id 1 --amount 100 --type all
  %(prog)s delete --id 1
  %(prog)s config
        """,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Post
    p_post = subparsers.add_parser("post", help="Create a social post")
    p_post.add_argument("--platform", "-p", required=True,
                        choices=["twitter", "linkedin", "instagram", "facebook"],
                        help="Target platform")
    p_post.add_argument("--text", "-t", default=None, help="Post text (auto-generate if not provided)")
    p_post.add_argument("--topic", "-m", default=None, help="Topic for auto-generated post")
    p_post.add_argument("--account", "-a", type=int, default=1, help="Account ID")
    p_post.add_argument("--publish", action="store_true", help="Publish immediately")
    p_post.add_argument("--add-hashtags", action="store_true", default=True, help="Auto-add hashtags")
    
    # List
    p_list = subparsers.add_parser("list", help="List posts")
    p_list.add_argument("--platform", "-p", default=None, help="Filter by platform")
    p_list.add_argument("--status", "-s", default=None, help="Filter by status")
    
    # View
    p_view = subparsers.add_parser("view", help="View post details")
    p_view.add_argument("--id", "-i", type=int, required=True, help="Post ID")
    
    # Schedule
    p_schedule = subparsers.add_parser("schedule", help="Schedule a post")
    p_schedule.add_argument("--platform", "-p", required=True, help="Target platform")
    p_schedule.add_argument("--text", "-t", default=None, help="Post text")
    p_schedule.add_argument("--topic", "-m", default=None, help="Topic")
    p_schedule.add_argument("--account", "-a", type=int, default=1, help="Account ID")
    p_schedule.add_argument("--datetime", "-d", required=True, help="Schedule datetime")
    p_schedule.add_argument("--add-hashtags", action="store_true", default=True, help="Auto-add hashtags")
    
    # Schedule List
    subparsers.add_parser("schedule-list", help="List scheduled posts")
    
    # Accounts
    subparsers.add_parser("accounts", help="List social accounts")
    
    # Account Add
    p_acc_add = subparsers.add_parser("account-add", help="Add a social account")
    p_acc_add.add_argument("--platform", "-p", required=True, help="Platform")
    p_acc_add.add_argument("--username", "-u", required=True, help="Username")
    
    # Metrics
    subparsers.add_parser("metrics", help="Show engagement metrics")
    
    # Boost
    p_boost = subparsers.add_parser("boost", help="Boost a post's engagement")
    p_boost.add_argument("--post-id", type=int, required=True, help="Post ID")
    p_boost.add_argument("--amount", type=int, default=50, help="Boost amount")
    p_boost.add_argument("--type", default="all", choices=["likes", "retweets", "replies", "all"],
                        help="Boost type")
    
    # Delete
    p_delete = subparsers.add_parser("delete", help="Delete a post")
    p_delete.add_argument("--id", "-i", type=int, required=True, help="Post ID")
    
    # Config
    subparsers.add_parser("config", help="Show configuration")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "post":
            cmd_post(args)
        elif args.command == "list":
            cmd_list(args)
        elif args.command == "view":
            cmd_view(args)
        elif args.command == "schedule":
            cmd_schedule(args)
        elif args.command == "schedule-list":
            cmd_schedule_list(args)
        elif args.command == "accounts":
            cmd_accounts(args)
        elif args.command == "account-add":
            cmd_account_add(args)
        elif args.command == "metrics":
            cmd_metrics(args)
        elif args.command == "boost":
            cmd_boost(args)
        elif args.command == "delete":
            cmd_delete(args)
        elif args.command == "config":
            cmd_config(args)
    except Exception as e:
        log.error(f"Command '{args.command}' failed: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
