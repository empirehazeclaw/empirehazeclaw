#!/usr/bin/env python3
"""
TikTok Script Agent — Generate viral TikTok video scripts
Version: 1.0
Usage: python3 tiktok_script_agent.py --task <task> [options]
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
    format='%(asctime)s [TIKTOK] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "tiktok_script.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class TikTokScriptAgent:
    """Generate viral TikTok video scripts with hooks, pacing, and trends."""

    VIRAL_HOOKS = [
        "POV:",
        "Wait for the end...",
        "Nobody is talking about this but...",
        "3 things I wish I knew sooner about",
        "Here's the thing nobody tells you about",
        "This is why most people fail at",
        "Drop a 🙋 if you",
        "Save this for later",
        "Reply to @user",
        "Duet this with"
    ]

    CONTENT_FORMATS = {
        "howto": {"structure": "Hook -> Problem -> Solution -> CTA", "pacing": "medium"},
        "listicle": {"structure": "Hook -> Item 1 -> Item 2 -> ... -> CTA", "pacing": "fast"},
        "storytime": {"structure": "Hook -> Setup -> Conflict -> Resolution -> CTA", "pacing": "slow"},
        "reaction": {"structure": "Hook -> React -> Key moments -> Final reaction", "pacing": "medium"},
        "dayinlife": {"structure": "Wake up -> Activities -> Sleep", "pacing": "fast"},
        "transformation": {"structure": "Before -> Process -> After -> CTA", "pacing": "slow"}
    }

    def __init__(self):
        self.log = log
        self.optimal_hook_duration = 3  # seconds
        self.cta_position = 55  # second mark

    def generate_script(self, topic: str, format_type: str = "howto",
                       duration_seconds: int = 60, audience: str = "general") -> Dict[str, Any]:
        """Generate a complete TikTok script."""

        format_config = self.CONTENT_FORMATS.get(format_type, self.CONTENT_FORMATS["howto"])

        script = {
            "format": "tiktok",
            "topic": topic,
            "content_format": format_type,
            "duration_seconds": duration_seconds,
            "aspect_ratio": "9:16",
            "vertical": True,
            "pacing": format_config["pacing"],
            "target_audience": audience,
            "hook": self._generate_hook(topic),
            "sections": self._generate_sections(topic, format_type, duration_seconds),
            "cta": self._generate_cta(),
            "captions": self._generate_caption_template(),
            "hashtags": self._generate_hashtags(topic, format_type),
            "sounds": self._suggest_sounds(topic, format_type),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "estimated_words": self._estimate_words(duration_seconds),
                "trending_elements": self._identify_trending_elements(topic)
            }
        }

        return script

    def generate_howto_script(self, topic: str, steps: List[str] = None,
                            duration_seconds: int = 60) -> Dict[str, Any]:
        """Generate a how-to tutorial script."""

        if not steps:
            steps = [f"Step {i+1} about {topic}" for i in range(3)]

        hook = self._generate_hook(topic, style="howto")

        # Distribute time across steps
        hook_time = 3
        steps_time = 45
        cta_time = duration_seconds - hook_time - steps_time
        per_step = steps_time // len(steps)

        sections = []
        current_time = hook_time

        for i, step in enumerate(steps):
            section = {
                "number": i + 1,
                "text": step,
                "start_time": current_time,
                "end_time": current_time + per_step,
                "visual_direction": f"Text overlay + demonstration"
            }
            sections.append(section)
            current_time += per_step

        return {
            "format": "tiktok",
            "type": "howto",
            "topic": topic,
            "duration_seconds": duration_seconds,
            "hook": hook,
            "steps": sections,
            "cta": self._generate_cta(),
            "captions": "White text, center screen, 24pt bold",
            "hashtags": self._generate_hashtags(topic, "howto"),
            "sound_suggestion": "Upbeat instrumental or trending sound"
        }

    def generate_listicle_script(self, topic: str, num_items: int = 5,
                                duration_seconds: int = 60) -> Dict[str, Any]:
        """Generate a list-style script (e.g., '5 tips about X')."""

        hook = self._generate_hook(topic, style="listicle")

        # Time distribution
        hook_time = 3
        items_time = 50
        cta_time = duration_seconds - hook_time - items_time
        per_item = items_time // num_items

        items = []
        current_time = hook_time

        for i in range(num_items):
            items.append({
                "number": i + 1,
                "text": f"Number {i+1}: {topic}",
                "start_time": current_time,
                "end_time": current_time + per_item,
                "visual": "B-roll or text overlay"
            })
            current_time += per_item

        return {
            "format": "tiktok",
            "type": "listicle",
            "topic": topic,
            "duration_seconds": duration_seconds,
            "hook": hook,
            "items": items,
            "cta": self._generate_cta(),
            "captions": "Bold numbered text",
            "hashtags": self._generate_hashtags(topic, "listicle")
        }

    def generate_趨勢_script(self, topic: str, trend_type: str = "challenge") -> Dict[str, Any]:
        """Generate script for trending content/challenges."""

        trend_templates = {
            "challenge": {
                "hook": "Can you do this challenge?",
                "structure": "Challenge intro -> Demonstration -> Tag friends"
            },
            "duet": {
                "hook": "Replying to @user",
                "structure": "Original video -> Your reaction/response"
            },
            "stitch": {
                "hook": "Let's stitch this",
                "structure": "Original clip -> Your addition"
            },
            "trend": {
                "hook": "Using [trending sound]",
                "structure": "Trending audio -> Relevant content"
            }
        }

        template = trend_templates.get(trend_type, trend_templates["trend"])

        return {
            "format": "tiktok",
            "type": "trend",
            "subtype": trend_type,
            "topic": topic,
            "duration_seconds": 60,
            "hook": {"text": template["hook"], "timing": "0-3 seconds"},
            "structure": template["structure"],
            "cta": {"text": "Duet with me!", "timing": "last 5 seconds"},
            "hashtags": self._generate_hashtags(topic, "trend"),
            "trending_sounds": ["Sound 1", "Sound 2", "Sound 3"]
        }

    def adapt_for_duet(self, original_script: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt existing script for duet format."""

        return {
            "format": "duet",
            "original_topic": original_script.get("topic"),
            "sections": [
                {
                    "timing": "0-15 sec",
                    "action": "Watch original (left side)",
                    "script": "[React with expression]"
                },
                {
                    "timing": "15-45 sec",
                    "action": "Add your thoughts (right side)",
                    "script": f"[Your观点 about {original_script.get('topic')}]"
                },
                {
                    "timing": "45-60 sec",
                    "action": "Call to action",
                    "script": "Follow for more!"
                }
            ],
            "layout": "Split screen (original left, reaction right)"
        }

    def _generate_hook(self, topic: str, style: str = None) -> Dict[str, Any]:
        """Generate attention-grabbing opening hook."""

        hook_type = style or "generic"
        hooks = {
            "howto": f"Here's how to {topic} in 60 seconds",
            "listicle": f"3 things about {topic} nobody talks about",
            "storytime": f"My experience with {topic} changed everything",
            "generic": f"Wait for this {topic} tip"
        }

        return {
            "text": hooks.get(hook_type, hooks["generic"]),
            "timing": "0-3 seconds",
            "visual": "Text on screen or face cam",
            "audio": "Hook sound or silence"
        }

    def _generate_sections(self, topic: str, format_type: str,
                          duration_seconds: int) -> List[Dict[str, Any]]:
        """Generate main content sections."""

        sections = []
        content_time = duration_seconds - 8  # Minus hook and CTA

        if format_type == "howto":
            for i in range(3):
                sections.append({
                    "name": f"Step {i+1}",
                    "timing": f"{(i * content_time // 3) + 3}-{(i * content_time // 3) + 3 + content_time // 3}",
                    "script": f"[Content for step {i+1}]",
                    "visual": "Screen record or B-roll"
                })
        else:
            sections.append({
                "name": "Main Content",
                "timing": f"3-{duration_seconds - 5}",
                "script": f"[{topic} content]",
                "visual": "Face cam or screen record"
            })

        return sections

    def _generate_cta(self) -> Dict[str, Any]:
        """Generate call-to-action."""

        return {
            "text": "Follow for more | Comment what to cover next",
            "timing": "last 5 seconds",
            "visual": "Face cam",
            "caption_addition": "Follow @youraccount"
        }

    def _generate_caption_template(self) -> str:
        """Generate caption display template."""

        return "White bold text, center aligned, appears at key moments"

    def _generate_hashtags(self, topic: str, content_type: str) -> List[str]:
        """Generate trending hashtags."""

        base = topic.replace(' ', '')

        return [
            f"#{base}",
            f"#{content_type}",
            "#fyp",
            "#viral",
            "#trending",
            "#foryou",
            "#tips",
            "#learnontiktok"
        ]

    def _suggest_sounds(self, topic: str, content_type: str) -> List[str]:
        """Suggest appropriate sounds."""

        return [
            "Trending sound (check TikTok trends)",
            "Upbeat instrumental",
            "No sound (text-to-speech)"
        ]

    def _estimate_words(self, duration_seconds: int) -> int:
        """Estimate words for given duration."""

        return int(duration_seconds * 2.5)  # ~150 words per minute / 60

    def _identify_trending_elements(self, topic: str) -> List[str]:
        """Identify trending elements for the topic."""

        return [
            "Use trending sound",
            "Jump cut editing",
            "Text overlays",
            "Fast pacing"
        ]

    def format_as_markdown(self, script: Dict[str, Any]) -> str:
        """Format script as readable markdown."""

        md = f"""# TikTok Script: {script.get('topic', 'Untitled')}

**Format:** {script.get('type', script.get('content_format', 'general'))}
**Duration:** {script.get('duration_seconds', 60)} seconds
**Aspect Ratio:** 9:16 (Vertical)

---

## 🎬 HOOK ({script['hook'].get('timing', '0-3 sec')})

**Text:** {script['hook'].get('text', '')}
**Visual:** {script['hook'].get('visual', 'TBD')}

---

"""

        for i, section in enumerate(script.get('sections', script.get('steps', [])), 1):
            md += f"""## 📍 SECTION {i}: {section.get('name', f'Part {i}')}

**Timing:** {section.get('timing', 'TBD')}
**Script:** {section.get('script', '[Content]')}
**Visual:** {section.get('visual', section.get('visual_direction', 'TBD'))}

"""

        md += f"""## 📢 CTA ({script.get('cta', {}).get('timing', 'last 5 sec')})

**Script:** {script.get('cta', {}).get('text', 'Follow for more!')}
**Visual:** {script.get('cta', {}).get('visual', 'Face cam')}

---

## #️⃣ HASHTAGS

{" ".join(script.get('hashtags', []))}

---

**Estimated Words:** {script.get('metadata', {}).get('estimated_words', 'N/A')}
"""
        return md


def main():
    parser = argparse.ArgumentParser(
        description="TikTok Script Agent — Generate viral TikTok scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate how-to script
  python3 tiktok_script_agent.py --task generate --topic "Morning routine" --format howto

  # Generate listicle
  python3 tiktok_script_agent.py --task listicle --topic "Productivity tips" --num 5

  # Generate trend script
  python3 tiktok_script_agent.py --task trend --topic "Work from home" --trend-type challenge

  # Format as markdown
  python3 tiktok_script_agent.py --task format --script-file ./script.json
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["generate", "howto", "listicle", "trend", "duet", "format"],
                        help="Task to perform")
    parser.add_argument("--topic", help="Video topic")
    parser.add_argument("--format", choices=["howto", "listicle", "storytime", "reaction", "dayinlife"],
                        default="howto", help="Content format")
    parser.add_argument("--trend-type", choices=["challenge", "duet", "stitch", "trend"],
                        default="trend", help="Trend type")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--num", type=int, default=5, help="Number of items for listicle")
    parser.add_argument("--audience", default="general", help="Target audience")
    parser.add_argument("--steps", help="Comma-separated steps")
    parser.add_argument("--script-file", help="Input script JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format-output", choices=["json", "markdown"], default="json")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = TikTokScriptAgent()

    try:
        result = None

        if args.task == "generate":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_script(
                topic=args.topic,
                format_type=args.format,
                duration_seconds=args.duration,
                audience=args.audience
            )

        elif args.task == "howto":
            if not args.topic:
                raise ValueError("--topic required")
            steps = args.steps.split(",") if args.steps else None
            result = agent.generate_howto_script(
                topic=args.topic,
                steps=steps,
                duration_seconds=args.duration
            )

        elif args.task == "listicle":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_listicle_script(
                topic=args.topic,
                num_items=args.num,
                duration_seconds=args.duration
            )

        elif args.task == "trend":
            if not args.topic:
                raise ValueError("--topic required")
            result = agent.generate_趨勢_script(
                topic=args.topic,
                trend_type=args.trend_type
            )

        elif args.task == "duet":
            if not args.script_file:
                raise ValueError("--script-file required")
            with open(args.script_file, 'r') as f:
                script = json.load(f)
            result = agent.adapt_for_duet(script)

        elif args.task == "format":
            if not args.script_file:
                raise ValueError("--script-file required")
            with open(args.script_file, 'r') as f:
                script = json.load(f)
            result = {"markdown": agent.format_as_markdown(script)}

        if result:
            if args.output:
                if args.format_output == "markdown" and "markdown" in result:
                    with open(args.output, 'w') as f:
                        f.write(result["markdown"])
                else:
                    with open(args.output, 'w') as f:
                        json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                if args.format_output == "markdown" and "markdown" in result:
                    print(result["markdown"])
                else:
                    print(json.dumps(result, indent=2))
            log.info("Task completed successfully")

    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
