#!/usr/bin/env python3
"""
YouTube Description Agent — Generate SEO-optimized video descriptions
Version: 1.0
Usage: python3 youtube_description_agent.py --task <task> [options]
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
    format='%(asctime)s [YT_DESC] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "youtube_description.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class YouTubeDescriptionAgent:
    """Generate SEO-optimized YouTube descriptions with timestamps, links, and CTAs."""

    DEFAULT_TEMPLATE = """{title}

{VIEW_HOOK}

{VIEW_COUNT} views {VIEWS_AGO}

---

{TOPIC_SENTENCE}

{SUMMARY}

---

📌 CHAPTERS / TIMESTAMPS
{TIMESTAMPS}

🔗 LINKS & RESOURCES
{LINKS}

📢 CONNECT WITH ME
Social links...

---

#Tags: {TAGS}
"""

    def __init__(self):
        self.log = log

    def generate_description(self, title: str, topic: str, timestamps: List[Dict[str, str]],
                            links: List[Dict[str, str]], duration_minutes: int,
                            keywords: List[str] = None, summary: str = None) -> Dict[str, Any]:
        """Generate a complete YouTube video description."""

        tags = keywords or self._extract_keywords(title, topic)

        # Generate timestamps string
        timestamps_str = "\n".join([f"{t['time']} - {t['label']}" for t in timestamps])

        # Generate links string
        links_str = "\n".join([f"🔗 {link.get('label', 'Link')}: {link.get('url', '')}" for link in links])

        # Generate tags string
        tags_str = " ".join([f"#{tag.replace(' ', '')}" for tag in tags[:15]])

        description = self.DEFAULT_TEMPLATE.format(
            title=title,
            VIEW_HOOK="Learn everything about",
            VIEW_COUNT="",
            VIEWS_AGO="",
            TOPIC_SENTENCE=f"In this video, you'll learn about {topic}.",
            SUMMARY=summary or f"{topic} - complete guide for beginners and advanced users alike.",
            TIMESTAMPS=timestamps_str,
            LINKS=links_str,
            TAGS=tags_str
        )

        return {
            "title": title,
            "description": description,
            "tags": tags,
            "timestamps": timestamps,
            "links": links,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "duration_minutes": duration_minutes,
                "char_count": len(description),
                "recommended_length": "2000-5000 chars for SEO"
            }
        }

    def generate_timestamps(self, duration_minutes: int, sections: List[str]) -> List[Dict[str, str]]:
        """Generate timestamp entries automatically."""

        timestamps = []
        interval = (duration_minutes * 60) / (len(sections) + 1)

        for i, section in enumerate(sections):
            seconds = int(interval * (i + 1))
            minutes = seconds // 60
            secs = seconds % 60
            timestamps.append({
                "time": f"{minutes:02d}:{secs:02d}",
                "label": section
            })

        return timestamps

    def add_timestamps_to_description(self, description: str, timestamps: List[Dict[str, str]]) -> str:
        """Add or update timestamps section in existing description."""

        new_timestamps = "\n".join([f"{t['time']} - {t['label']}" for t in timestamps])

        if "📌 CHAPTERS" in description or "TIMESTAMPS" in description:
            # Replace existing timestamps
            pattern = r'(📌 CHAPTERS.*?\n)(.*?)(\n\n---|\n🔗|\n📢)'
            match = re.search(pattern, description, re.DOTALL)
            if match:
                description = re.sub(pattern, rf'\1{new_timestamps}\3', description, flags=re.DOTALL)
        else:
            # Insert timestamps after summary
            description += f"\n\n📌 CHAPTERS / TIMESTAMPS\n{new_timestamps}"

        return description

    def add_links_to_description(self, description: str, links: List[Dict[str, str]]) -> str:
        """Add or update links section in existing description."""

        links_str = "\n".join([f"🔗 {link.get('label', 'Link')}: {link.get('url', '')}" for link in links])

        if "🔗 LINKS" in description:
            pattern = r'(🔗 LINKS.*?\n)(.*?)(\n\n---|\n📢)'
            match = re.search(pattern, description, re.DOTALL)
            if match:
                description = re.sub(pattern, rf'\1{links_str}\3', description, flags=re.DOTALL)
        else:
            description += f"\n\n🔗 LINKS & RESOURCES\n{links_str}"

        return description

    def optimize_for_seo(self, description: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze and optimize description for SEO."""

        issues = []
        suggestions = []

        # Check length
        if len(description) < 500:
            issues.append("Description too short (<500 chars). YouTube may not index well.")
            suggestions.append("Add more detail about the video content (2000+ chars recommended)")
        elif len(description) > 5000:
            issues.append("Description very long (>5000 chars). Important info may be missed.")
            suggestions.append("Consider moving less important info to comments or video")

        # Check keyword density
        desc_lower = description.lower()
        keyword_hits = sum(1 for kw in keywords if kw.lower() in desc_lower)
        if keyword_hits < len(keywords) // 2:
            issues.append(f"Only {keyword_hits}/{len(keywords)} keywords found in description")
            suggestions.append("Repeat main keywords naturally throughout description")

        # Check for CTA
        if not re.search(r'(subscribe|follow|comment|like)', description, re.I):
            issues.append("No clear call-to-action found")
            suggestions.append("Add a clear CTA (subscribe, comment, etc.)")

        # Check for timestamps
        if not re.search(r'\d{1,2}:\d{2}', description):
            issues.append("No timestamps found")
            suggestions.append("Add timestamps to help viewers navigate")

        # Check for links
        if not re.search(r'https?://', description):
            issues.append("No links found")
            suggestions.append("Add relevant resource links if applicable")

        return {
            "issues": issues,
            "suggestions": suggestions,
            "seo_score": max(0, 100 - len(issues) * 20),
            "length": len(description)
        }

    def _extract_keywords(self, title: str, topic: str) -> List[str]:
        """Extract keywords from title and topic."""

        # Common words to exclude
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}

        text = f"{title} {topic}".lower()
        words = re.findall(r'\b[a-z]+\b', text)
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        # Add important variations
        keywords.extend([
            topic.lower().replace(' ', ''),
            topic.lower().split()[0] if topic else ''
        ])

        return list(set(keywords))[:15]

    def format_for_import(self, data: Dict[str, Any], format: str = "youtube") -> str:
        """Format data for import to YouTube or third-party tools."""

        if format == "youtube":
            return f"""{data.get('title', 'Untitled')}

{data.get('description', '')}
"""
        elif format == "csv":
            return f"""{data.get('title', '')}|{data.get('description', '')}|{','.join(data.get('tags', []))}"""

        return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="YouTube Description Agent — Generate SEO-optimized descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full description
  python3 youtube_description_agent.py --task generate --title "API Rate Limiting Explained" \\
    --topic "API Rate Limiting" --duration 10 \\
    --sections "Introduction,What is Rate Limiting,Implementation,Best Practices" \\
    --keywords "api,rate limiting,backend,performance"

  # Add timestamps to existing description
  python3 youtube_description_agent.py --task add-timestamps --input ./description.txt \\
    --timestamps '[{"time":"00:00","label":"Intro"},{"time":"02:30","label":"Main Topic"}]'

  # SEO audit
  python3 youtube_description_agent.py --task optimize --input ./description.txt \\
    --keywords "api,rate limiting,tutorial"

  # Save to file
  python3 youtube_description_agent.py --task generate ... --output ./description.json
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["generate", "add-timestamps", "add-links", "optimize", "format"],
                        help="Task to perform")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--topic", help="Video topic/description")
    parser.add_argument("--duration", type=int, default=10, help="Video duration in minutes")
    parser.add_argument("--sections", help="Comma-separated section names for timestamps")
    parser.add_argument("--keywords", help="Comma-separated keywords")
    parser.add_argument("--timestamps", help="JSON array of timestamps")
    parser.add_argument("--links", help="JSON array of links")
    parser.add_argument("--input", help="Input description file or JSON")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown", "plain"], default="json")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = YouTubeDescriptionAgent()

    try:
        result = None

        if args.task == "generate":
            if not args.title or not args.topic:
                raise ValueError("--title and --topic required")

            keywords = args.keywords.split(",") if args.keywords else None
            sections = args.sections.split(",") if args.sections else ["Intro", "Main Content", "Conclusion"]

            # Generate timestamps
            timestamps = agent.generate_timestamps(args.duration, sections)

            # Generate links placeholder
            links = [{"label": "My Website", "url": "https://example.com"}]

            result = agent.generate_description(
                title=args.title,
                topic=args.topic,
                timestamps=timestamps,
                links=links,
                duration_minutes=args.duration,
                keywords=keywords
            )

        elif args.task == "add-timestamps":
            if not args.input:
                raise ValueError("--input required")

            # Load description
            if os.path.exists(args.input):
                with open(args.input, 'r') as f:
                    description = f.read()
            else:
                description = args.input

            # Parse timestamps
            if args.timestamps:
                timestamps = json.loads(args.timestamps)
            else:
                timestamps = agent.generate_timestamps(5, ["Intro", "Main"])

            result = {
                "description": agent.add_timestamps_to_description(description, timestamps),
                "timestamps_added": len(timestamps)
            }

        elif args.task == "add-links":
            if not args.input:
                raise ValueError("--input required")

            if os.path.exists(args.input):
                with open(args.input, 'r') as f:
                    description = f.read()
            else:
                description = args.input

            if args.links:
                links = json.loads(args.links)
            else:
                links = [{"label": "Resource", "url": "https://example.com"}]

            result = {
                "description": agent.add_links_to_description(description, links),
                "links_added": len(links)
            }

        elif args.task == "optimize":
            if not args.input:
                raise ValueError("--input required")

            if os.path.exists(args.input):
                with open(args.input, 'r') as f:
                    description = f.read()
            else:
                description = args.input

            keywords = args.keywords.split(",") if args.keywords else ["video", "tutorial"]
            result = agent.optimize_for_seo(description, keywords)

        elif args.task == "format":
            if not args.input:
                raise ValueError("--input required")

            with open(args.input, 'r') as f:
                data = json.load(f)

            result = {"formatted": agent.format_for_import(data, args.format)}

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    if isinstance(result, dict) and "description" in result:
                        f.write(result["description"])
                    else:
                        json.dump(result, f, indent=2)
                log.info(f"Output saved to {args.output}")
            else:
                print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
            log.info("Task completed successfully")

    except FileNotFoundError as e:
        log.error(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        log.error(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Task failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
