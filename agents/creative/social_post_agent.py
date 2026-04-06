#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SOCIAL POST AGENT                                   ║
║          Twitter/X, LinkedIn, Instagram — Multi-Platform     ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 social_post_agent.py --help
  python3 social_post_agent.py --platform twitter --topic "New Product Launch" --lang en
  python3 social_post_agent.py --platform linkedin --topic "10 Growth Tips" --lang de
  python3 social_post_agent.py --platform instagram --topic "Behind the scenes" --lang en
  python3 social_post_agent.py --batch --topic "Weekly Tips" --lang de --platforms twitter,linkedin

Data: ~/.openclaw/workspace/data/social/
Logs: /home/clawbot/.openclaw/workspace/logs/social_post.log
"""

import argparse
import json
import logging
import random
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "social"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "social_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "social_post.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.social_post")


class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    THREADS = "threads"
    FACEBOOK = "facebook"


class PostStyle(str, Enum):
    STATEMENT = "statement"      # Strong opinion / hot take
    QUESTION = "question"       # Engage with a question
    THREAD = "thread"           # Multi-tweet / carousel thread
    QUOTE = "quote"             # Quote / stat repost
    STORY = "story"             # Personal story / anecdote
    TIPS = "tips"               # Numbered tips list
    ANNOUNCEMENT = "announcement"
    REACTION = "reaction"       # React to news / trend
    BEHIND_SCENES = "behind_scenes"
    POLL = "poll"


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FUNNY = "funny"
    INSPIRING = "inspiring"
    EDUCATIONAL = "educational"
    BOLD = "bold"


@dataclass
class PostSpec:
    platform: Platform
    topic: str
    language: str = "de"
    style: PostStyle = PostStyle.STATEMENT
    tone: Tone = Tone.PROFESSIONAL
    hashtags: List[str] = field(default_factory=list)
    mention_handles: List[str] = field(default_factory=list)
    brand: str = "EmpireHazeClaw"
    include_emoji: bool = True
    thread_count: int = 5

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v.value if isinstance(v, Enum) else v for k, v in d.items()}


@dataclass
class SocialPost:
    spec: Dict[str, Any]
    platform: str
    posts: List[Dict[str, Any]]
    total_characters: int
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


def load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"posts": [], "version": "1.0"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.warning("Cache read error: %s", e)
        return {"posts": [], "version": "1.0"}


def save_cache(cache: Dict[str, Any]) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


class SocialPostAgent:
    """Generates social media posts for multiple platforms."""

    LIMITS = {
        Platform.TWITTER: 280,
        Platform.LINKEDIN: 3000,
        Platform.INSTAGRAM: 2200,
        Platform.THREADS: 500,
        Platform.FACEBOOK: 500,
    }

    def __init__(self):
        self.cache = load_cache()
        log.info("SocialPostAgent initialized. %d posts in cache.", len(self.cache.get("posts", [])))

    def generate(self, spec: PostSpec) -> SocialPost:
        log.info("📱 Generating social post: '%s' (%s, %s, %s)",
                 spec.topic, spec.platform.value, spec.style.value, spec.tone.value)
        try:
            if spec.platform == Platform.TWITTER:
                posts = self._generate_twitter(spec)
            elif spec.platform == Platform.LINKEDIN:
                posts = self._generate_linkedin(spec)
            elif spec.platform == Platform.INSTAGRAM:
                posts = self._generate_instagram(spec)
            elif spec.platform == Platform.THREADS:
                posts = self._generate_threads(spec)
            else:
                posts = self._generate_twitter(spec)

            total_chars = sum(len(p["text"]) for p in posts)
            result = SocialPost(
                spec=spec.to_dict(),
                platform=spec.platform.value,
                posts=posts,
                total_characters=total_chars,
            )
            self._save(result)
            log.info("✅ Generated %d posts for %s (total: %d chars)", len(posts), spec.platform.value, total_chars)
            return result
        except Exception as e:
            log.error("Post generation failed: %s", e)
            raise

    def _generate_twitter(self, spec: PostSpec) -> List[Dict[str, Any]]:
        limit = self.LIMITS[Platform.TWITTER]

        if spec.style == PostStyle.THREAD:
            return self._twitter_thread(spec, limit)
        return [self._twitter_single(spec, limit)]

    def _twitter_single(self, spec: PostSpec, limit: int) -> Dict[str, Any]:
        hooks = {
            Tone.PROFESSIONAL: [
                "Here's what most people get wrong about {topic}:",
                "A thread on {topic} (🧵):",
                "Quick take on {topic}:",
            ],
            Tone.CASUAL: [
                "not gonna lie, {topic} is having a moment rn",
                "okay but {topic} is actually underrated",
                "unpopular opinion: {topic}",
            ],
            Tone.FUNNY: [
                "{topic} in 2026 be like 💀",
                "me explaining {topic} to my boss:",
                "POV: you just discovered {topic} 🫵",
            ],
            Tone.INSPIRING: [
                "If you're not thinking about {topic}, you're already behind.",
                "{topic} is the future. The question is: are you ready?",
            ],
            Tone.EDUCATIONAL: [
                "Everything you need to know about {topic}:",
                "The {topic} breakdown you've been waiting for:",
            ],
            Tone.BOLD: [
                "Hot take: {topic} will change everything in 2026.",
                "I'm calling it now: {topic} is the biggest opportunity of the decade.",
            ],
        }

        tone_hooks = hooks.get(spec.tone, hooks[Tone.PROFESSIONAL])
        hook = random.choice(tone_hooks).format(topic=spec.topic)
        emoji = "🔥" if spec.include_emoji else ""
        hashtags = self._format_hashtags(spec.hashtags or ["growth", "2026"], spec.platform)
        mentions = " ".join(f"@{m}" for m in spec.mention_handles)

        body = f"{hook}\n\n{emoji}{hashtags}"
        if mentions:
            body += f"\n\n{mentions}"

        if len(body) > limit:
            body = body[:limit - 3] + "..."

        return {
            "index": 1,
            "text": body.strip(),
            "char_count": len(body),
            "is_thread": False,
        }

    def _twitter_thread(self, spec: PostSpec, limit: int) -> List[Dict[str, Any]]:
        count = spec.thread_count
        topic = spec.topic
        posts = []

        templates = [
            f"A thread on {topic} 👇",
            f"Everything about {topic} (a thread) 🧵",
            f"Let's talk {topic} — a thread.",
        ]

        posts.append({
            "index": 1,
            "text": random.choice(templates),
            "char_count": len(random.choice(templates)),
            "is_thread": True,
            "type": "hook",
        })

        tip_templates = [
            f"{i+1}. {spec.topic}: {tip}"
            for i, tip in enumerate([
                "Start before you're ready",
                "Test early, not perfect",
                "Double down on what works",
                "Consistency beats intensity",
                "Learn from competitors",
                "Focus on one thing at a time",
                "Measure everything",
                "Automate what you can",
                "Build in public",
                "Ship weekly",
            ][:count - 2])
        ]

        for i, tip in enumerate(tip_templates, 2):
            posts.append({
                "index": i,
                "text": tip,
                "char_count": len(tip),
                "is_thread": True,
                "type": "body",
            })

        closing = [
            f"That's my take on {topic}. What would you add? 👇",
            f"What did I miss? Drop it below 👇",
            f"Save this for later 📌 | Follow for more on {spec.topic}",
        ]
        posts.append({
            "index": count,
            "text": random.choice(closing),
            "char_count": len(random.choice(closing)),
            "is_thread": True,
            "type": "cta",
        })

        return posts[:count]

    def _generate_linkin(self, spec: PostSpec) -> List[Dict[str, Any]]:
        limit = self.LIMITS[Platform.LINKEDIN]

        templates = {
            PostStyle.TIPS: self._linkedin_tips(spec),
            PostStyle.STATEMENT: self._linkedin_statement(spec),
            PostStyle.STORY: self._linkedin_story(spec),
            PostStyle.ANNOUNCEMENT: self._linkedin_announcement(spec),
            PostStyle.QUESTION: self._linkedin_question(spec),
            PostStyle.BEHIND_SCENES: self._linkedin_behind_scenes(spec),
            PostStyle.EDUCATIONAL: self._linkedin_educational(spec),
        }

        body = templates.get(spec.style, templates[PostStyle.TIPS])
        hashtags = self._format_hashtags(spec.hashtags or ["LinkedIn", "Growth", "2026"], Platform.LINKEDIN)
        body += f"\n\n{hashtags}"

        if len(body) > limit:
            body = body[:limit - 3] + "..."

        return [{"index": 1, "text": body, "char_count": len(body), "is_thread": False}]

    def _linkedin_tips(self, spec: PostSpec) -> str:
        tips = [
            "1. **Start with the problem, not the solution.**",
            "2. **Test before you build.**",
            "3. **Consistency is the real moat.**",
            "4. **Learn from failures — yours and others'.**",
            "5. **Ship weekly, improve daily.**",
        ][:spec.thread_count]
        emoji = "💡" if spec.include_emoji else ""
        return (
            f"{emoji} 5 Lessons About {spec.topic} I Wish I'd Known Sooner\n\n"
            + "\n\n".join(tips)
            + f"\n\nWhat would you add? 👇"
        )

    def _linkedin_statement(self, spec: PostSpec) -> str:
        return (
            f"Here's an unpopular opinion about {spec.topic}:\n\n"
            f"Most people are doing it wrong.\n\n"
            f"The real differentiator isn't what you do — it's how consistently you do it.\n\n"
            f"Agree or disagree? 👇"
        )

    def _linkedin_story(self, spec: PostSpec) -> str:
        return (
            f"I almost gave up on {spec.topic}.\n\n"
            f"6 months ago, nothing was working. The numbers were flat, the feedback was brutal, and I was questioning everything.\n\n"
            f"Then I changed one thing: [the key insight].\n\n"
            f"Result: [the outcome].\n\n"
            f"Here's what I learned about {spec.topic}..."
        )

    def _linkedin_announcement(self, spec: PostSpec) -> str:
        return (
            f"🎉 We're excited to announce: {spec.topic}\n\n"
            f"After months of work, we're finally ready to share this with the world.\n\n"
            f"What it does: [clear description]\n"
            f"Why it matters: [value proposition]\n\n"
            f"Link in comments 👇"
        )

    def _linkedin_question(self, spec: PostSpec) -> str:
        return (
            f"A question for the community about {spec.topic}:\n\n"
            f"What's the #1 challenge you're facing right now?\n\n"
            f"I've been researching this space extensively and I want to know: "
            f"what do you struggle with most?\n\n"
            f"Genuinely curious. Let's discuss 👇"
        )

    def _linkedin_behind_scenes(self, spec: PostSpec) -> str:
        return (
            f"Behind the scenes of building {spec.topic} 🏗️\n\n"
            f"This is what it actually looks like when you're building something from scratch.\n\n"
            f"- Week 1: [early stage]\n"
            f"- Month 1: [progress]\n"
            f"- Month 3: [milestone]\n\n"
            f"Building in public. More updates coming. 🚀"
        )

    def _linkedin_educational(self, spec: PostSpec) -> str:
        return (
            f"📚 The Complete Guide to {spec.topic}\n\n"
            f"Let me break this down so you understand it in 5 minutes:\n\n"
            f"**What is it?**\n[Definition]\n\n"
            f"**Why does it matter?**\n[Importance]\n\n"
            f"**How to get started:**\n[Steps]\n\n"
            f"Save this post for later. 📌"
        )

    def _generate_instagram(self, spec: PostSpec) -> List[Dict[str, Any]]:
        emoji = "✨" if spec.include_emoji else ""
        hashtags = self._format_hashtags(spec.hashtags or ["Instagood", "Growth", "Motivation"], Platform.INSTAGRAM)

        templates = {
            PostStyle.STATEMENT: f"{emoji} {spec.topic} — the real talk.\n\nWhat's your experience? 👇",
            PostStyle.TIPS: f"{emoji} 5 Tips for {spec.topic}:\n\n1. Start here\n2. Do this\n3. Avoid that\n4. Repeat\n5. Scale\n\nSave this! 📌",
            PostStyle.BEHIND_SCENES: f"Behind the scenes of {spec.topic} 🛠️\n\nThis is what most people don't see...",
            PostStyle.STORY: f"The story of how I discovered {spec.topic}...\n\n(Thread 👇)",
            PostStyle.ANNOUNCEMENT: f"🎉 ANNOUNCING: {spec.topic}\n\nEverything you need to know ↓",
        }

        body = templates.get(spec.style, templates[PostStyle.STATEMENT])
        body += f"\n\n{hashtags}"
        return [{"index": 1, "text": body, "char_count": len(body), "is_thread": False}]

    def _generate_threads(self, spec: PostSpec) -> List[Dict[str, Any]]:
        limit = self.LIMITS[Platform.THREADS]
        posts = []

        # Hook
        posts.append({
            "index": 1,
            "text": f"🧵 A thread on {spec.topic}:",
            "char_count": len(f"🧵 A thread on {spec.topic}:"),
            "is_thread": True,
            "type": "hook",
        })

        points = [
            "This is the first insight about {topic}.",
            "Here's the second thing most people miss.",
            "And this is the real secret nobody talks about.",
            "Action step: Do this one thing first.",
            "That's the thread. What would you add? 👇",
        ][:spec.thread_count]

        for i, pt in enumerate(points, 2):
            posts.append({
                "index": i,
                "text": pt.format(topic=spec.topic),
                "char_count": len(pt),
                "is_thread": True,
                "type": "body",
            })

        return posts

    def _format_hashtags(self, hashtags: List[str], platform: Platform) -> str:
        if not hashtags:
            return ""
        if platform == Platform.TWITTER:
            return " ".join(f"#{h.replace(' ','')}" for h in hashtags[:5])
        elif platform == Platform.LINKEDIN:
            return " ".join(f"#{h.replace(' ','')}" for h in hashtags[:3])
        elif platform == Platform.INSTAGRAM:
            return "\n" + " ".join(f"#{h.replace(' ','')}" for h in hashtags[:10])
        else:
            return " ".join(f"#{h.replace(' ','')}" for h in hashtags[:5])

    def _save(self, result: SocialPost) -> None:
        self.cache.setdefault("posts", []).insert(0, result.__dict__)
        self.cache["posts"] = self.cache["posts"][:100]
        save_cache(self.cache)

    def list_posts(self) -> List[Dict[str, Any]]:
        return self.cache.get("posts", [])

    def export_posts(self, result: SocialPost) -> str:
        lines = [f"{'='*60}",
                 f"📱 SOCIAL POST — {result.platform.upper()}",
                 f"{'='*60}",
                 f"Topic: {result.spec.get('topic')} | Style: {result.spec.get('style')} | {result.total_characters} total chars",
                 f"Generated: {result.generated_at[:16]}",
                 f"{'='*60}",
                 ""]
        for post in result.posts:
            idx = post.get("index", "?")
            label = f"[{idx}/{len(result.posts)}]"
            if post.get("is_thread"):
                label += f" ({post.get('type','body')})"
            lines.append(f"{label} {'─'*40}")
            lines.append(post["text"])
            lines.append("")
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="social_post_agent.py",
        description="📱 Social Post Agent — Twitter, LinkedIn, Instagram, Threads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single tweet
  python3 social_post_agent.py --platform twitter --topic "New AI Tool launched" --lang en --style statement --tone bold

  # LinkedIn post (tips format)
  python3 social_post_agent.py --platform linkedin --topic "5 Lessons on Startup Growth" --lang de --style tips

  # Twitter thread
  python3 social_post_agent.py --platform twitter --topic "SEO Mistakes" --lang en --style thread --thread-count 7

  # Instagram post
  python3 social_post_agent.py --platform instagram --topic "Behind the scenes" --lang en --style behind_scenes

  # Batch: generate for multiple platforms at once
  python3 social_post_agent.py --batch --topic "Weekly Tip" --lang de --platforms twitter,linkedin --style tips

  # List cached posts
  python3 social_post_agent.py --list
        """
    )
    parser.add_argument("--platform", choices=[p.value for p in Platform], help="Target platform")
    parser.add_argument("--topic", type=str, help="Post topic/content")
    parser.add_argument("--lang", choices=["de", "en"], default="de")
    parser.add_argument("--style", choices=[s.value for s in PostStyle], default=PostStyle.STATEMENT.value)
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.PROFESSIONAL.value)
    parser.add_argument("--hashtags", type=str, default="",
                        help="Comma-separated hashtags (without #)")
    parser.add_argument("--mentions", type=str, default="",
                        help="Comma-separated @handles")
    parser.add_argument("--thread-count", dest="thread_count", type=int, default=5,
                        help="Number of tweets in thread (default: 5)")
    parser.add_argument("--no-emoji", dest="no_emoji", action="store_true", help="Exclude emoji")
    parser.add_argument("--batch", action="store_true", help="Generate for all --platforms (comma-separated)")
    parser.add_argument("--platforms", type=str, default="twitter,linkedin",
                        help="Comma-separated platforms for --batch")
    parser.add_argument("--output", type=str, help="Save output to file")
    parser.add_argument("--list", action="store_true", help="List all cached posts")
    return parser.parse_args()


def main() -> None:
    agent = SocialPostAgent()
    args = parse_args()

    if args.list:
        posts = agent.list_posts()
        if not posts:
            print("No posts in cache.")
            return
        print(f"\n📱 Cached Social Posts ({len(posts)} total)\n")
        for p in posts:
            ts = p.get("generated_at", "")[:10]
            platforms = p.get("platform", "?")
            count = len(p.get("posts", []))
            print(f"  [{ts}] {p.get('spec',{}).get('topic','?')} | {platforms} ({count} posts)")
        return

    hashtags = [h.strip() for h in args.hashtags.split(",") if h.strip()]
    mentions = [m.strip() for m in args.mentions.split(",") if m.strip()]

    if args.batch:
        platforms_str = args.platforms or "twitter,linkedin"
        platform_list = [p.strip() for p in platforms_str.split(",")]
        results = []
        for plat_str in platform_list:
            try:
                plat = Platform(plat_str)
            except ValueError:
                print(f"Unknown platform: {plat_str}")
                continue
            spec = PostSpec(
                platform=plat,
                topic=args.topic or "Weekly Update",
                language=args.lang,
                style=PostStyle(args.style),
                tone=Tone(args.tone),
                hashtags=hashtags,
                mention_handles=mentions,
                include_emoji=not args.no_emoji,
                thread_count=args.thread_count,
            )
            results.append(agent.generate(spec))
        all_output = "\n\n".join(agent.export_posts(r) for r in results)
        print(all_output)
    else:
        if not args.platform:
            print("ERROR: --platform required (or use --batch).")
            sys.exit(1)
        if not args.topic:
            print("ERROR: --topic required.")
            sys.exit(1)

        spec = PostSpec(
            platform=Platform(args.platform),
            topic=args.topic,
            language=args.lang,
            style=PostStyle(args.style),
            tone=Tone(args.tone),
            hashtags=hashtags,
            mention_handles=mentions,
            include_emoji=not args.no_emoji,
            thread_count=args.thread_count,
        )
        result = agent.generate(spec)
        output = agent.export_posts(result)
        print(output)

    if args.output:
        Path(args.output).write_text(all_output if args.batch else output, encoding="utf-8")
        print(f"\n💾 Saved to {args.output}")


if __name__ == "__main__":
    main()
