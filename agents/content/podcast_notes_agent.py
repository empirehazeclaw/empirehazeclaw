#!/usr/bin/env python3
"""
Podcast Notes Agent — Generate show notes, timestamps, and summaries
Version: 1.0
Usage: python3 podcast_notes_agent.py --task <task> [options]
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
    format='%(asctime)s [PODCAST] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "podcast_notes.log")),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


class PodcastNotesAgent:
    """Generate comprehensive podcast show notes, timestamps, and summaries."""

    def __init__(self):
        self.log = log
        self.words_per_minute = 150  # Average speaking pace

    def generate_show_notes(self, episode_title: str, episode_number: int,
                           duration_minutes: int, topics: List[str],
                           guests: List[Dict] = None, sponsor: str = None) -> Dict[str, Any]:
        """Generate complete show notes for a podcast episode."""

        # Generate timestamps
        timestamps = self._generate_timestamps(topics, duration_minutes)

        # Generate summary
        summary = self._generate_summary(episode_title, topics)

        # Generate key takeaways
        takeaways = self._generate_takeaways(topics)

        # Build show notes
        show_notes = f"""# {episode_title}

**Episode #{episode_number}** | {duration_minutes} minutes | {datetime.now().strftime('%B %d, %Y')}

## Episode Summary
{summary}

## What You'll Learn
{takeaways}

## Timestamps
{self._format_timestamps_markdown(timestamps)}

"""

        if guests:
            show_notes += "## Guest(s)\n"
            for guest in guests:
                show_notes += f"- **{guest.get('name', 'TBD')}** — {guest.get('title', '')}"
                if guest.get('bio'):
                    show_notes += f"\n  {guest['bio']}"
                show_notes += "\n"

        if sponsor:
            show_notes += f"\n## Sponsor\n{sponsor}\n"

        show_notes += """
## Resources Mentioned
- [Resource 1](link)
- [Resource 2](link)

## Connect With Us
- Website: yourpodcast.com
- Twitter: @yourpodcast
- Email: hello@yourpodcast.com

---
*Subscribe for new episodes every week!*
"""

        return {
            "episode_title": episode_title,
            "episode_number": episode_number,
            "duration_minutes": duration_minutes,
            "show_notes": show_notes,
            "timestamps": timestamps,
            "summary": summary,
            "takeaways": takeaways,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "word_count": len(show_notes.split()),
                "estimated_listeners": "N/A"
            }
        }

    def generate_episode_summary(self, transcript_text: str = None,
                                topics: List[str] = None) -> Dict[str, Any]:
        """Generate a concise episode summary."""

        if not topics and not transcript_text:
            raise ValueError("Either topics or transcript_text required")

        topic_str = ", ".join(topics) if topics else "the episode topic"

        summary = f"""In this episode, we dive deep into {topic_str}.

We cover the key insights, actionable strategies, and real-world examples that will help you apply what you learn to your own work and projects.

Whether you're a beginner or an experienced professional, this episode is packed with value you won't want to miss.
"""

        return {
            "summary": summary,
            "short_description": f"Learn about {topic_str} in this detailed discussion.",
            "long_description": summary,
            "topics": topics or []
        }

    def generate_timestamps(self, topics: List[str], duration_minutes: int) -> List[Dict[str, str]]:
        """Generate chapter timestamps for the episode."""

        timestamps = []
        time_per_topic = (duration_minutes * 60) // (len(topics) + 2)  # +2 for intro/outro

        current_seconds = 0

        # Intro
        timestamps.append({
            "time": self._format_time(current_seconds),
            "label": "Introduction",
            "type": "intro"
        })
        current_seconds += time_per_topic

        # Topics
        for i, topic in enumerate(topics):
            timestamps.append({
                "time": self._format_time(current_seconds),
                "label": topic,
                "type": "topic"
            })
            current_seconds += time_per_topic

        # Outro
        timestamps.append({
            "time": self._format_time(current_seconds),
            "label": "Wrap-up & Links",
            "type": "outro"
        })

        return timestamps

    def generate_key_takeaways(self, topics: List[str]) -> str:
        """Generate key takeaways section."""

        takeaways = []
        for i, topic in enumerate(topics, 1):
            takeaways.append(f"{i}. **{topic}** — Actionable insight here")

        return "\n".join(takeaways)

    def generate_shownotes_markdown(self, data: Dict[str, Any]) -> str:
        """Format show notes as markdown."""

        md = data.get("show_notes", "")
        if not md:
            md = self.generate_show_notes(
                episode_title=data.get("episode_title", ""),
                episode_number=data.get("episode_number", 1),
                duration_minutes=data.get("duration_minutes", 30),
                topics=data.get("topics", [])
            ).get("show_notes", "")

        return md

    def generate_shownotes_html(self, data: Dict[str, Any]) -> str:
        """Format show notes as HTML for website."""

        timestamps = data.get("timestamps", [])
        topics = data.get("topics", [])
        guests = data.get("guests", [])

        html = f"""
<div class="podcast-episode">
    <h2>{data.get('episode_title', 'Episode')}</h2>
    <p class="meta">Episode #{data.get('episode_number', 1)} | {data.get('duration_minutes', 30)} min</p>

    <div class="summary">
        <h3>Summary</h3>
        <p>{data.get('summary', '')}</p>
    </div>

    <div class="timestamps">
        <h3>Chapters</h3>
        <ul>
"""

        for ts in timestamps:
            html += f'            <li><strong>{ts.get("time", "0:00")}</strong> — {ts.get("label", "")}</li>\n'

        html += """        </ul>
    </div>

    <div class="takeaways">
        <h3>Key Takeaways</h3>
        <ul>
"""

        for i, topic in enumerate(topics, 1):
            html += f"            <li>{i}. {topic}</li>\n"

        html += """        </ul>
    </div>
</div>
"""
        return html

    def generate_podcast_chapter_file(self, data: Dict[str, Any],
                                     output_format: str = "json") -> str:
        """Generate chapter file for podcast hosting platforms."""

        timestamps = data.get("timestamps", [])
        chapters = []

        for i, ts in enumerate(timestamps, 1):
            chapters.append({
                "startTime": self._time_to_seconds(ts.get("time", "0:00")),
                "title": ts.get("label", f"Chapter {i}"),
                "image": "",
                "url": ""
            })

        if output_format == "json":
            return json.dumps(chapters, indent=2)
        elif output_format == "mp4chaps":
            # Format for MP4 chapters
            lines = ["CHAPTERS=0"]
            for chapter in chapters:
                time_str = self._seconds_to_time(chapter["startTime"])
                lines.append(f"CHAPTER{i:02d}={time_str}")
                lines.append(f"CHAPTER{i:02d}NAME={chapter['title']}")
            return "\n".join(lines)

        return json.dumps(chapters, indent=2)

    def generate_social_clips_plan(self, topics: List[str],
                                   num_clips: int = 5) -> List[Dict[str, Any]]:
        """Generate a plan for social media clips from the episode."""

        clips = []
        clips_per_topic = num_clips // len(topics)

        for i, topic in enumerate(topics):
            for j in range(clips_per_topic):
                clips.append({
                    "topic": topic,
                    "clip_number": len(clips) + 1,
                    "suggested_hook": self._generate_clip_hook(topic),
                    "duration_seconds": 30 if j == 0 else 15,
                    "platform": "TikTok" if j % 2 == 0 else "YouTube Shorts",
                    "caption": f"Full episode link in bio 🔗 #{topic.replace(' ', '')}"
                })

        return clips

    def generate_email_newsletter(self, data: Dict[str, Any]) -> str:
        """Generate content for email newsletter about episode."""

        return f"""
🎙️ New Episode: {data.get('episode_title', 'Episode')}

{data.get('summary', 'New episode is live!')}

⏱️ Duration: {data.get('duration_minutes', 30)} minutes

📚 What You'll Learn:
{data.get('takeaways', '')}

🎧 Listen now: [link]

---
"""

    def _generate_summary(self, title: str, topics: List[str]) -> str:
        """Generate episode summary."""

        topics_str = ", ".join(topics[:3])
        return f"""In this episode, we explore {topics_str}.

Join us as we discuss the key insights, strategies, and actionable tips you can apply to your own projects and goals.

From practical advice to deep dives into the concepts, this episode is packed with value for listeners at all levels.
"""

    def _generate_takeaways(self, topics: List[str]) -> str:
        """Generate key takeaways."""

        takeaways = []
        for i, topic in enumerate(topics, 1):
            takeaways.append(f"- **{topic}**")
        return "\n".join(takeaways)

    def _generate_timestamps(self, topics: List[str], duration_minutes: int) -> List[Dict[str, str]]:
        """Wrapper for timestamps generation."""

        return self.generate_timestamps(topic, duration_minutes)

    def _format_timestamps_markdown(self, timestamps: List[Dict[str, str]]) -> str:
        """Format timestamps as markdown list."""

        return "\n".join([f"- **{ts.get('time', '0:00')}** — {ts.get('label', '')}" for ts in timestamps])

    def _format_time(self, seconds: int) -> str:
        """Format seconds as HH:MM:SS or MM:SS."""

        if seconds >= 3600:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{mins:02d}:{secs:02d}"
        else:
            mins = seconds // 60
            secs = seconds % 60
            return f"{mins}:{secs:02d}"

    def _time_to_seconds(self, time_str: str) -> int:
        """Convert time string to seconds."""

        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])

    def _seconds_to_time(self, seconds: int) -> str:
        """Convert seconds to HH:MM:SS."""

        hours = seconds // 3600
        mins = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"

    def _generate_clip_hook(self, topic: str) -> str:
        """Generate hook for social media clip."""

        hooks = [
            f"Here's the truth about {topic}",
            f"Most people get {topic} wrong",
            f"What nobody tells you about {topic}",
            f"The key insight about {topic}"
        ]
        return hooks[hash(topic) % len(hooks)]


def main():
    parser = argparse.ArgumentParser(
        description="Podcast Notes Agent — Generate show notes and summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate full show notes
  python3 podcast_notes_agent.py --task show-notes --title "Building a SaaS" \\
    --episode 42 --duration 45 --topics "Planning,Development,Launch"

  # Generate episode summary
  python3 podcast_notes_agent.py --task summary --topics "AI,Marketing,Tools"

  # Generate clips plan
  python3 podcast_notes_agent.py --task clips --topics "tip1,tip2,tip3" --num-clips 6

  # Generate chapter file
  python3 podcast_notes_agent.py --task chapters --input ./episode.json --format mp4chaps
        """
    )

    parser.add_argument("--task", required=True,
                        choices=["show-notes", "summary", "clips", "chapters", "email", "html"],
                        help="Task to perform")
    parser.add_argument("--title", help="Episode title")
    parser.add_argument("--episode", type=int, help="Episode number")
    parser.add_argument("--duration", type=int, default=30, help="Duration in minutes")
    parser.add_argument("--topics", help="Comma-separated topics")
    parser.add_argument("--num-clips", type=int, default=5, help="Number of clips")
    parser.add_argument("--sponsor", help="Sponsor message")
    parser.add_argument("--guests", help="JSON array of guest objects")
    parser.add_argument("--input", help="Input JSON file")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "markdown", "html", "mp4chaps"],
                        default="json", help="Output format")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    agent = PodcastNotesAgent()

    try:
        result = None

        if args.task == "show-notes":
            if not args.title or not args.topics:
                raise ValueError("--title and --topics required")

            topics = args.topics.split(",")
            guests = json.loads(args.guests) if args.guests else None

            result = agent.generate_show_notes(
                episode_title=args.title,
                episode_number=args.episode or 1,
                duration_minutes=args.duration,
                topics=topics,
                guests=guests,
                sponsor=args.sponsor
            )

        elif args.task == "summary":
            if not args.topics:
                raise ValueError("--topics required")
            topics = args.topics.split(",")
            result = agent.generate_episode_summary(topics=topics)

        elif args.task == "clips":
            if not args.topics:
                raise ValueError("--topics required")
            topics = args.topics.split(",")
            result = {"clips_plan": agent.generate_social_clips_plan(topics, args.num_clips)}

        elif args.task == "chapters":
            if not args.input:
                raise ValueError("--input required")
            with open(args.input, 'r') as f:
                data = json.load(f)
            result = {"chapters": agent.generate_podcast_chapter_file(data, args.format)}

        elif args.task == "email":
            if not args.input:
                raise ValueError("--input required")
            with open(args.input, 'r') as f:
                data = json.load(f)
            result = {"email_content": agent.generate_email_newsletter(data)}

        elif args.task == "html":
            if not args.input:
                raise ValueError("--input required")
            with open(args.input, 'r') as f:
                data = json.load(f)
            result = {"html": agent.generate_shownotes_html(data)}

        if result:
            if args.output:
                with open(args.output, 'w') as f:
                    if "html" in result:
                        f.write(result["html"])
                    elif "email_content" in result:
                        f.write(result["email_content"])
                    elif "chapters" in result:
                        f.write(result["chapters"])
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
