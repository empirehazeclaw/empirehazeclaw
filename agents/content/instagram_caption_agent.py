#!/usr/bin/env python3
"""
Instagram Caption Agent — Generate engaging Instagram captions
Version: 1.0
Usage: python3 instagram_caption_agent.py --task <task> [options]
"""

import argparse
import json
import logging
import sys
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

# Logging Setup
LOG_DIR = "/home/clawbot/.openclaw/workspace/logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [IG_CAPTION] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "instagram_caption.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class InstagramCaptionAgent:
    """Generate engaging Instagram captions for posts and reels."""

    CAPTION_STYLES = {
        "personal": {
            "tone": "personal, authentic, storytelling",
            "structure": "hook -> story -> value -> CTA",
            "emoji_usage": "moderate"
        },
        "business": {
            "tone": "professional, value-driven, educational",
            "structure": "hook -> tips -> CTA",
            "emoji_usage": "minimal"
        },
        "lifestyle": {
            "tone": "casual, aspirational, relatable",
            "structure": "mood -> context -> CTA",
            "emoji_usage": "high"
        },
        "promo": {
            "tone": "compelling, urgent, benefit-focused",
            "structure": "hook -> offer -> details -> CTA",
            "emoji_usage": "moderate"
        }
    }

    def __init__(self):
        self.log = log
        self.max_caption_length = 2200  # Instagram limit
        self.optimal_length = 150-300  # Best engagement

    def generate_caption(self, content_type: str, topic: str, style: str = "personal",
                        include_hashtags: bool = True, brand_name: str = None) -> Dict[str, Any]:
        """Generate a complete Instagram caption."""

        style_config = self.CAPTION_STYLES.get(style, self.CAPTION_STYLES["personal"])

        # Generate caption text
        caption = self._build_caption(topic, content_type, style_config, brand_name)

        # Generate hashtags
        hashtags = self._generate_hashtags(topic, content_type, include_hashtags)

        # Calculate engagement prediction
        engagement = self._predict_engagement(caption, hashtags)

        return {
            "caption": caption,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{hashtags}",
            "metadata": {
                "content_type": content_type,
                "style": style,
                "char_count": len(caption),
                "hashtag_count": len(hashtags.split()),
                "engagement_prediction": engagement,
                "generated_at": datetime.now().isoformat()
            }
        }

    def generate_reel_caption(self, topic: str, hook_seconds: str = None,
                             brand_name: str = None) -> Dict[str, Any]:
        """Generate caption optimized for Reels."""

        hook_text = hook_seconds or "3 seconds"

        caption = f"""Watch till the end! 🎯

Here's everything you need to know about {topic} in under a minute.

Save this for later 📌

Follow for more content like this 👆"""

        if brand_name:
            caption += f"\n\n🔗 @{brand_name}"

        hashtags = f"#reels #viral #{topic.replace(' ', '')} #trending #fyp #contentcreator #tips"

        return {
            "caption": caption,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{hashtags}",
            "metadata": {
                "content_type": "reel",
                "optimized_for": "Reels algorithm",
                "hook_timing": hook_text,
                "engagement_prediction": "high"
            }
        }

    def generate_carousel_caption(self, topic: str, num_slides: int = 5,
                                  brand_name: str = None) -> Dict[str, Any]:
        """Generate caption for carousel posts."""

        caption = f"""Everything about {topic} in {num_slides} slides 👆

Swipe through to learn:

💡 Slide 1: Overview
💡 Slide 2: Key Concept
💡 Slide 3: Practical Tips
💡 Slide 4: Common Mistakes
💡 Slide 5: Action Steps

Which slide was most helpful? Comment below ⬇️

Save this for later 📌"""

        if brand_name:
            caption += f"\n\nFollow @{brand_name} for more"

        hashtags = f"#carousel #{topic.replace(' ', '')} #educational #content #tips #learn"

        return {
            "caption": caption,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{hashtags}",
            "metadata": {
                "content_type": "carousel",
                "num_slides": num_slides,
                "cta_type": "save + comment"
            }
        }

    def generate_story_caption(self, topic: str) -> Dict[str, Any]:
        """Generate short caption for Story shares."""

        caption = f"""✨ {topic}

Link in bio for more 👆"""

        hashtags = f"#{topic.replace(' ', '')}"

        return {
            "caption": caption,
            "hashtags": hashtags,
            "full_post": f"{caption}\n\n{hashtags}",
            "metadata": {
                "content_type": "story",
                "length": "short",
                "optimized_for": "story shares"
            }
        }

    def batch_generate(self, topics: List[str], content_type: str = "post",
                       styles: List[str] = None) -> List[Dict[str, Any]]:
        """Generate multiple captions at once."""

        results = []
        style_list = styles or ["personal", "business", "lifestyle"]

        for i, topic in enumerate(topics):
            style = style_list[i % len(style_list)]
            caption_data = self.generate_caption(content_type, topic, style)
            results.append(caption_data)

        return results

    def optimize_hashtags(self, topic: str, num_hashtags: int = 9,
                         category: str = None) -> Dict[str, Any]:
        """Generate optimized hashtag set."""

        # Mix of popularity levels
        all_tags = self._generate_hashtag_mix(topic, category)

        return {
            "hashtags": " ".join(all_tags[:num_hashtags]),
            "mix_breakdown": {
                "high_volume": all_tags[:3],
                "medium_volume": all_tags[3:6],
                "niche": all_tags[6:9]
            },
            "total_selected": min(num_hashtags, len(all_tags)),
            "topic": topic
        }

    def _build_caption(self, topic: str, content_type: str, style_config: Dict,
                      brand_name: str = None) -> str:
        """Build caption based on style configuration."""

        templates = {
            "post": self._template_post,
            "reel": self._template_reel,
            "story": self._template_story,
            "carousel": self._template_carousel
        }

        template_func = templates.get(content_type, self._template_post)
        return template_func(topic, style_config, brand_name)

    def _template_post(self, topic: str, style: Dict, brand: str = None) -> str:
        """Personal/storytelling template."""

        caption = f"""Something about {topic} I've been thinking about a lot lately.

Here's what I've learned:

→ Point 1 about {topic}
→ Point 2 about {topic}
→ Point 3 about {topic}

The key insight? It's simpler than you think.

What's your experience with {topic}? 👇

"""

        if brand:
            caption += f"🔗 More content: @{brand}"

        return caption.strip()

    def _template_reel(self, topic: str, style: Dict, brand: str = None) -> str:
        """Reel-optimized template."""

        return f"""Watch this {topic} tutorial 🎬

Save this for later 📌

Follow for more 👆"""

    def _template_story(self, topic: str, style: Dict, brand: str = None) -> str:
        """Story template."""

        return f"✨ {topic}"

    def _template_carousel(self, topic: str, style: Dict, brand: str = None) -> str:
        """Carousel template."""

        return f"""{topic} in carousel format 👆

Swipe to learn more ↓"""

    def _generate_hashtags(self, topic: str, content_type: str, include: bool) -> str:
        """Generate relevant hashtags."""

        if not include:
            return ""

        base_tags = [
            f"#{topic.replace(' ', '')}",
            f"#{content_type}",
            "#contentcreator",
            "#tips",
            "#learn"
        ]

        return " ".join(base_tags)

    def _generate_hashtag_mix(self, topic: str, category: str = None) -> List[str]:
        """Generate mix of high, medium, and niche hashtags."""

        base = topic.replace(' ', '')

        hashtags = [
            f"#{base}",
            f"#{base}tips",
            f"#{base}tutorial",
            f"#{base}2024",
            "#contentcreator",
            "#digitalmarketing",
            "#socialmediatips",
            "#learning",
            "#education",
            "#motivation",
            "#inspiration",
            "#business"
        ]

        if category:
            hashtags.append(f"#{category}")

        return hashtags

    def _predict_engagement(self, caption: str, hashtags: str) -> Dict[str, Any]:
        """Predict engagement potential of caption."""

        score = 50  # Base score

        # Length check
        if 150 <= len(caption) <= 300:
            score += 20
        elif len(caption) > 300:
            score += 10

        # Hashtag balance
        hashtag_count = len(hashtags.split())
        if 5 <= hashtag_count <= 15:
            score += 15
        elif hashtag_count > 20:
            score -= 10

        # Engagement elements
        if "?" in caption:
            score += 10  # Questions boost comments
        if any(word in caption.lower() for word in ["save", "save this", "save for later"]):
            score += 10  # Save prompts boost reach
        if "👇" in caption or "comment" in caption.lower():
            score += 10

        # Emoji usage
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', caption))
        if 2 <= emoji_count <= 5:
            score += 5

        return {
            "score": min(100, score),
            "level": "high" if score >= 80 else "medium" if score >= 60 else "low",
            "tips": self._get_engagement_tips(score)
        }

    def _get_engagement_tips(self, score: int) -> List[str]:
        """Get tips to improve engagement."""

        tips = []
        if score < 80:
            tips.append("Add a question to encourage comments")
            tips.append("Include 'save this' prompt to boost reach")
        if score < 70:
            tips.append("Try a stronger hook in the first line")
            tips.append("Keep caption between 150-300 characters")
        return tips


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Caption Agent — Generate engaging captions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate single caption
  python3 instagram_caption_agent.py --task generate --content-type post \\
    --topic "Morning routine tips" --style personal

  # Generate reel caption
  python3 instagram_caption_agent.py --task reel --topic "Productivity hacks"

  # Generate carousel caption
  python3 instagram_caption_agent.py --task carousel --topic "5 Tips for better sleep" --slides 5

  # Optimize hashtags
  python3 instagram_caption_agent.py --task hashtags --topic "digital marketing" --num 9

  # Batch generate
  python3 instagram_caption_agent.py --task batch --topics "tip1,tip2,tip3" --styles "personal,business"
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["generate", "reel", "carousel", "story", "hashtags", "batch", "optimize"],
                        help="Task to perform")
    parser.add_argument("--content-type", choices=["post", "reel", "story", "carousel"],
                        default="post", help="Type of content")
    parser.add_argument("--topic", help="Post topic/subject")
    parser.add_argument("--style", choices=["personal", "business", "lifestyle", "promo"],
                        default="personal", help="Caption style")
    parser.add_argument("--topics", help="Comma-separated topics for batch")
    parser.add_argument("--styles", help="Comma-separated styles for batch")
    parser.add_argument("--slides", type=int, default=5, help="Number of carousel slides")
    parser.add_argument("--brand", help="Brand/username to mention")
    parser.add_argument("--num", type=int, default=9, help="Number of hashtags")
    parser.add_argument("--no-hashtags", action="store_true", help="Exclude hashtags")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = InstagramCaptionAgent()

    try:
        result = None

        if args.task == "generate":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_caption(
                content_type=args.content_type,
                topic=args.topic,
                style=args.style,
                include_hashtags=not args.no_hashtags,
                brand_name=args.brand
            )

        elif args.task == "reel":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_reel_caption(topic=args.topic, brand_name=args.brand)

        elif args.task == "carousel":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_carousel_caption(
                topic=args.topic,
                num_slides=args.slides,
                brand_name=args.brand
            )

        elif args.task == "story":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_story_caption(topic=args.topic)

        elif args.task == "hashtags":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.optimize_hashtags(topic=args.topic, num_hashtags=args.num)

        elif args.task == "batch":
            if not args.topics:
                raise ValueError("--topics required")
            topics = args.topics.split(",")
            styles = args.styles.split(",") if args.styles else None
            result = {"captions": agent.batch_generate(topics, args.content_type, styles)}

        elif args.task == "optimize":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.optimize_hashtags(topic=args.topic, num_hashtags=args.num)

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
            log.info("Task completed successfully")

    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
