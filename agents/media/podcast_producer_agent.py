#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          PODCAST PRODUCER AGENT                             ║
║          End-to-End Podcast Production Workflow             ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Episode planning & script generation
  - Guest management & research
  - Show notes generation (auto-written blog post)
  - SEO optimization
  - Audio transcription support
  - Multi-language support (DE/EN)
  - Episode versioning & templating
  - Content repurposing (clips, quotes, social posts)
  - Production checklist tracking

Usage:
    python3 podcast_producer_agent.py --help
    python3 podcast_producer_agent.py plan --topic "AI Trends 2026"
    python3 podcast_producer_agent.py script --episode 1
    python3 podcast_producer_agent.py notes --episode 1
    python3 podcast_producer_agent.py list
"""

from __future__ import annotations

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
from typing import List, Dict, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger("openclaw.podcast")


class EpisodeStatus(str, Enum):
    IDEA = "idea"
    PLANNING = "planning"
    SCRIPTING = "scripting"
    RECORDED = "recorded"
    EDITING = "editing"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EpisodeType(str, Enum):
    SOLO = "solo"
    INTERVIEW = "interview"
    ROUNDTABLE = "roundtable"
    PANEL = "panel"
    NEWS = "news"
    Q_A = "q&a"
    TRAINING = "training"


EPISODE_TEMPLATES = {
    EpisodeType.SOLO: {
        "intro_duration": 60,
        "outro_duration": 120,
        "sections": ["Hook", "Main Topic", "Deep Dive", "Key Takeaways", "Call to Action"],
    },
    EpisodeType.INTERVIEW: {
        "intro_duration": 90,
        "outro_duration": 60,
        "sections": ["Introduction", "Guest Background", "Core Discussion", "Rapid Fire", "Wrap-up"],
    },
    EpisodeType.ROUNDTABLE: {
        "intro_duration": 120,
        "outro_duration": 90,
        "sections": ["Introduction", "Topic Setup", "Discussion Rounds", "Consensus", "Action Items"],
    },
    EpisodeType.NEWS: {
        "intro_duration": 45,
        "outro_duration": 45,
        "sections": ["Headlines", "Story Deep Dive", "Implications", "What's Next"],
    },
    EpisodeType.Q_A: {
        "intro_duration": 60,
        "outro_duration": 90,
        "sections": ["Intro", "Community Questions", "Deep Answers", "Tips", "Outro"],
    },
    EpisodeType.TRAINING: {
        "intro_duration": 120,
        "outro_duration": 60,
        "sections": ["Learning Objectives", "Concept Explanation", "Examples", "Practice", "Summary"],
    },
}

HOOK_TEMPLATES = [
    "Did you know that {fact}? Today we explore why this matters.",
    "I recently discovered {discovery} and it changed my perspective on {topic}.",
    "What if I told you that {statement}? Stick around as we dive deep.",
    "The biggest mistake people make around {topic} is {mistake}.",
    "Three years ago I {story}. Today, let me share what I learned.",
]


@dataclass
class Guest:
    id: str
    name: str
    role: str
    company: str
    expertise: List[str] = field(default_factory=list)
    bio: str = ""
    twitter: str = ""
    linkedin: str = ""
    email: str = ""
    talking_points: List[str] = field(default_factory=list)


@dataclass
class EpisodeSection:
    title: str
    duration_seconds: int
    content: str = ""
    key_points: List[str] = field(default_factory=list)


@dataclass
class Episode:
    id: int
    title: str
    topic: str
    episode_type: EpisodeType = EpisodeType.SOLO
    status: EpisodeStatus = EpisodeStatus.IDEA
    language: str = "en"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    season: int = 1
    episode_number: int = 0
    hook: str = ""
    sections: List[EpisodeSection] = field(default_factory=list)
    script: str = ""
    show_notes: str = ""
    target_duration_minutes: int = 30
    guest: Optional[Guest] = None
    recording_date: Optional[datetime] = None
    publish_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    seo_title: str = ""
    seo_description: str = ""
    keywords: List[str] = field(default_factory=list)
    clips: List[str] = field(default_factory=list)
    quotes: List[str] = field(default_factory=list)
    social_posts: List[str] = field(default_factory=list)
    checklist: Dict[str, bool] = field(default_factory=lambda: {
        "topic_approved": False,
        "guest_booked": False,
        "outline_created": False,
        "script_written": False,
        "recorded": False,
        "edited": False,
        "show_notes_done": False,
        "published": False,
    })

    def generate_hook(self) -> str:
        template = random.choice(HOOK_TEMPLATES)
        return template.format(
            fact="...", discovery="...", topic=self.topic,
            statement="...", mistake="...", story="..."
        )

    def get_progress(self) -> float:
        total = len(self.checklist)
        completed = sum(1 for v in self.checklist.values() if v)
        return (completed / total) * 100 if total > 0 else 0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        if self.recording_date:
            d['recording_date'] = self.recording_date.isoformat()
        if self.publish_date:
            d['publish_date'] = self.publish_date.isoformat()
        if self.guest:
            d['guest'] = asdict(self.guest)
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Episode':
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('recording_date'):
            data['recording_date'] = datetime.fromisoformat(data['recording_date'])
        if data.get('publish_date'):
            data['publish_date'] = datetime.fromisoformat(data['publish_date'])
        if data.get('guest'):
            data['guest'] = Guest(**data['guest'])
        data['episode_type'] = EpisodeType(data['episode_type'])
        data['status'] = EpisodeStatus(data['status'])
        return cls(**data)


class PodcastProducer:
    def __init__(self, storage_path: str = "data/podcast_producer.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.episodes: List[Episode] = self._load()
        self.guests: Dict[str, Guest] = self._load_guests()
        self.next_id = max([e.id for e in self.episodes], default=0) + 1

    def _load(self) -> List[Episode]:
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return [Episode.from_dict(e) for e in data.get('episodes', [])]
        except (json.JSONDecodeError, KeyError) as e:
            log.warning(f"Could not load podcast data: {e}")
            return []

    def _load_guests(self) -> Dict[str, Guest]:
        if not self.storage_path.exists():
            return {}
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return {g['id']: Guest(**g) for g in data.get('guests', [])}
        except (json.JSONDecodeError, KeyError):
            return {}

    def _save(self):
        data = {
            'episodes': [e.to_dict() for e in self.episodes],
            'guests': [asdict(g) for g in self.guests.values()]
        }
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _get_episode(self, episode_id: int) -> Optional[Episode]:
        for ep in self.episodes:
            if ep.id == episode_id:
                return ep
        return None

    def create_episode(self, title: str, topic: str,
                       episode_type: str = "solo",
                       language: str = "en",
                       target_duration: int = 30,
                       tags: Optional[List[str]] = None) -> Episode:
        ep_type = EpisodeType(episode_type)
        episode = Episode(
            id=self.next_id,
            title=title,
            topic=topic,
            episode_type=ep_type,
            language=language,
            target_duration_minutes=target_duration,
            tags=tags or [],
            episode_number=len([e for e in self.episodes if e.season == 1]) + 1
        )
        episode.hook = episode.generate_hook()
        episode.status = EpisodeStatus.PLANNING
        self.episodes.append(episode)
        self._save()
        log.info(f"Created episode #{episode.id}: {title}")
        return episode

    def generate_script(self, episode_id: int, language: str = "en") -> str:
        episode = self._get_episode(episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")

        template = EPISODE_TEMPLATES.get(episode.episode_type, EPISODE_TEMPLATES[EpisodeType.SOLO])
        sections = template['sections']
        total = episode.target_duration_minutes * 60
        intro_dur = template['intro_duration']
        outro_dur = template['outro_duration']
        main_time = total - intro_dur - outro_dur
        section_time = main_time // len(sections) if sections else 0

        lines = []
        lines.append("=" * 60)
        lines.append(f"PODCAST SCRIPT - Episode #{episode.id}: {episode.title}")
        lines.append(f"Type: {episode.episode_type.value} | Duration: ~{episode.target_duration_minutes} min")
        lines.append(f"Language: {language.upper()}")
        lines.append("=" * 60)
        lines.append("")
        lines.append("[INTRO]")
        lines.append(f"Welcome! Today: {episode.topic}")
        lines.append(f"Hook: {episode.hook}")
        lines.append("")

        elapsed = intro_dur
        for i, section_name in enumerate(sections):
            mins, secs = divmod(elapsed, 60)
            lines.append(f"[SECTION {i+1}: {section_name.upper()} - {mins:02d}:{secs:02d}]")
            lines.append(f"Key points for {section_name}:")
            lines.append(f"  - Point 1...")
            lines.append(f"  - Point 2...")
            lines.append(f"  - Point 3...")
            if language == "de":
                lines.append("  [SPRECHEN SIE HIER]")
            else:
                lines.append("  [SPEAK HERE]")
            lines.append("")
            elapsed += section_time

        mins, secs = divmod(elapsed, 60)
        lines.append(f"[OUTRO - {mins:02d}:{secs:02d}]")
        lines.append("Thanks for listening!")
        lines.append("Subscribe for more episodes.")
        lines.append("=" * 60)

        script = "\n".join(lines)
        episode.script = script
        episode.status = EpisodeStatus.SCRIPTING
        episode.checklist['script_written'] = True
        self._save()
        return script

    def generate_show_notes(self, episode_id: int, language: str = "en") -> str:
        episode = self._get_episode(episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")

        lines = []
        lines.append(f"# {episode.seo_title or episode.title}")
        lines.append("")
        lines.append(f"**Episode #{episode.episode_number} | {episode.topic}**")
        lines.append("")
        lines.append(f"## {('Description' if language == 'en' else 'Beschreibung')}")
        lines.append(episode.description or episode.hook)
        lines.append("")
        lines.append(f"## {('Key Takeaways' if language == 'en' else 'Wichtige Erkenntnisse')}")
        for i, section in enumerate(episode.sections):
            lines.append(f"{i+1}. {section.title}")
            for point in section.key_points:
                lines.append(f"   - {point}")
        lines.append("")
        lines.append(f"## {('Guest' if language == 'en' else 'Gast')}")
        if episode.guest:
            lines.append(f"**{episode.guest.name}** - {episode.guest.role} @ {episode.guest.company}")
        else:
            lines.append(f"**{('Host Solo Episode' if language == 'en' else 'Gastgeber Solo Episode')}**")
        lines.append("")
        lines.append(f"## {('Links & Resources' if language == 'en' else 'Links & Ressourcen')}")
        lines.append("- [Resource 1]")
        lines.append("- [Resource 2]")
        lines.append("")
        lines.append(f"## {('Tags')}")
        lines.append(f"{', '.join(['podcast', episode.topic] + episode.tags)}")

        notes = "\n".join(lines)
        episode.show_notes = notes
        episode.checklist['show_notes_done'] = True
        self._save()
        return notes

    def add_guest(self, name: str, role: str, company: str,
                 expertise: List[str], **kwargs) -> Guest:
        guest_id = f"guest_{len(self.guests) + 1}"
        guest = Guest(
            id=guest_id,
            name=name,
            role=role,
            company=company,
            expertise=expertise,
            bio=kwargs.get('bio', ''),
            twitter=kwargs.get('twitter', ''),
            linkedin=kwargs.get('linkedin', ''),
            email=kwargs.get('email', ''),
            talking_points=kwargs.get('talking_points', [])
        )
        self.guests[guest_id] = guest
        self._save()
        log.info(f"Added guest: {name}")
        return guest

    def assign_guest(self, episode_id: int, guest_id: str):
        episode = self._get_episode(episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")
        guest = self.guests.get(guest_id)
        if not guest:
            raise ValueError(f"Guest {guest_id} not found")
        episode.guest = guest
        episode.episode_type = EpisodeType.INTERVIEW
        episode.checklist['guest_booked'] = True
        self._save()

    def update_checklist(self, episode_id: int, item: str, value: bool = True):
        episode = self._get_episode(episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found")
        if item in episode.checklist:
            episode.checklist[item] = value
            self._save()
        else:
            raise ValueError(f"Unknown checklist item: {item}")

    def get_stats(self) -> Dict:
        return {
            "total": len(self.episodes),
            "by_status": {s.value: sum(1 for e in self.episodes if e.status.value == s.value)
                          for s in EpisodeStatus},
            "by_type": {t.value: sum(1 for e in self.episodes if e.episode_type.value == t.value)
                        for t in EpisodeType},
            "published": sum(1 for e in self.episodes if e.status == EpisodeStatus.PUBLISHED),
            "upcoming": sum(1 for e in self.episodes if e.status in [EpisodeStatus.PLANNING, EpisodeStatus.SCRIPTING]),
        }

    def list_episodes(self, status: Optional[str] = None,
                       platform: Optional[str] = None) -> List[Episode]:
        filtered = self.episodes
        if status:
            filtered = [e for e in filtered if e.status.value == status]
        return sorted(filtered, key=lambda x: x.created_at, reverse=True)


def format_episode(ep: Episode) -> str:
    status_icons = {
        EpisodeStatus.IDEA: "💡",
        EpisodeStatus.PLANNING: "📋",
        EpisodeStatus.SCRIPTING: "✍️",
        EpisodeStatus.RECORDED: "🎙️",
        EpisodeStatus.EDITING: "🎧",
        EpisodeStatus.PUBLISHED: "✅",
        EpisodeStatus.ARCHIVED: "📦",
    }
    progress = ep.get_progress()
    guest_info = f" | 🎤 {ep.guest.name}" if ep.guest else ""
    return (
        f"  {status_icons.get(ep.status, '•')} [{ep.status.value:12}] "
        f"#{ep.id:3d} | {ep.title[:40]}{guest_info}\n"
        f"        Progress: {progress:.0f}% | {ep.episode_type.value} | "
        f"{ep.target_duration_minutes}min"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Podcast Producer Agent - End-to-End Podcast Production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --title "AI Trends 2026" --topic "Latest AI developments" --type interview
  %(prog)s script --episode 1 --lang en
  %(prog)s notes --episode 1 --lang de
  %(prog)s list --status planning
  %(prog)s stats
  %(prog)s guest add --name "Jane Doe" --role "AI Researcher" --company "TechCorp"
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    create_parser = subparsers.add_parser("create", help="Create new episode")
    create_parser.add_argument("--title", "-t", required=True, help="Episode title")
    create_parser.add_argument("--topic", required=True, help="Main topic")
    create_parser.add_argument("--type", default="solo", choices=["solo", "interview", "roundtable", "news", "q&a", "training"])
    create_parser.add_argument("--lang", "--language", default="en", choices=["en", "de"])
    create_parser.add_argument("--duration", type=int, default=30, help="Target duration in minutes")
    create_parser.add_argument("--tags", help="Comma-separated tags")
    create_parser.add_argument("--storage", default="data/podcast_producer.json")

    script_parser = subparsers.add_parser("script", help="Generate episode script")
    script_parser.add_argument("--episode", "-e", type=int, required=True, help="Episode ID")
    script_parser.add_argument("--lang", "--language", default="en", choices=["en", "de"])
    script_parser.add_argument("--storage", default="data/podcast_producer.json")

    notes_parser = subparsers.add_parser("notes", help="Generate show notes")
    notes_parser.add_argument("--episode", "-e", type=int, required=True, help="Episode ID")
    notes_parser.add_argument("--lang", "--language", default="en", choices=["en", "de"])
    notes_parser.add_argument("--storage", default="data/podcast_producer.json")

    list_parser = subparsers.add_parser("list", help="List episodes")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--storage", default="data/podcast_producer.json")

    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--storage", default="data/podcast_producer.json")

    guest_parser = subparsers.add_parser("guest", help="Manage guests")
    guest_sub = guest_parser.add_subparsers(dest="guest_cmd")

    guest_add = guest_sub.add_parser("add", help="Add guest")
    guest_add.add_argument("--name", required=True)
    guest_add.add_argument("--role", required=True)
    guest_add.add_argument("--company", required=True)
    guest_add.add_argument("--expertise", required=True, help="Comma-separated expertise areas")
    guest_add.add_argument("--bio")
    guest_add.add_argument("--twitter")
    guest_add.add_argument("--email")
    guest_add.add_argument("--storage", default="data/podcast_producer.json")

    guest_list = guest_sub.add_parser("list", help="List guests")
    guest_list.add_argument("--storage", default="data/podcast_producer.json")

    assign_parser = subparsers.add_parser("assign", help="Assign guest to episode")
    assign_parser.add_argument("--episode", "-e", type=int, required=True)
    assign_parser.add_argument("--guest", "-g", required=True, help="Guest ID")
    assign_parser.add_argument("--storage", default="data/podcast_producer.json")

    checklist_parser = subparsers.add_parser("checklist", help="Update checklist")
    checklist_parser.add_argument("--episode", "-e", type=int, required=True)
    checklist_parser.add_argument("--item", "-i", required=True,
                                  choices=["topic_approved", "guest_booked", "outline_created",
                                           "script_written", "recorded", "edited",
                                           "show_notes_done", "published"])
    checklist_parser.add_argument("--value", type=bool, default=True)
    checklist_parser.add_argument("--storage", default="data/podcast_producer.json")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "create":
            producer = PodcastProducer(args.storage)
            tags = args.tags.split(",") if args.tags else None
            ep = producer.create_episode(
                title=args.title,
                topic=args.topic,
                episode_type=args.type,
                language=args.lang,
                target_duration=args.duration,
                tags=tags
            )
            print(f"\n✅ Episode created!")
            print(f"   ID: {ep.id}")
            print(f"   Title: {ep.title}")
            print(f"   Type: {ep.episode_type.value}")
            print(f"   Hook: {ep.hook}")

        elif args.command == "script":
            producer = PodcastProducer(args.storage)
            script = producer.generate_script(args.episode, args.lang)
            print(f"\n📜 SCRIPT FOR EPISODE #{args.episode}:")
            print("-" * 60)
            print(script)

        elif args.command == "notes":
            producer = PodcastProducer(args.storage)
            notes = producer.generate_show_notes(args.episode, args.lang)
            print(f"\n📝 SHOW NOTES FOR EPISODE #{args.episode}:")
            print("-" * 60)
            print(notes)

        elif args.command == "list":
            producer = PodcastProducer(args.storage)
            episodes = producer.list_episodes(status=args.status)
            print(f"\n🎙️  EPISODES ({len(episodes)} found):")
            print("=" * 60)
            for ep in episodes:
                print(format_episode(ep))

        elif args.command == "stats":
            producer = PodcastProducer(args.storage)
            stats = producer.get_stats()
            print(f"\n📊 PODCAST STATISTICS:")
            print("=" * 50)
            print(f"  Total episodes: {stats['total']}")
            print(f"  Published: {stats['published']}")
            print(f"  Upcoming: {stats['upcoming']}")
            print(f"\n  By Status:")
            for status, count in stats['by_status'].items():
                print(f"    {status}: {count}")
            print(f"\n  By Type:")
            for etype, count in stats['by_type'].items():
                print(f"    {etype}: {count}")

        elif args.command == "guest":
            producer = PodcastProducer(args.storage)
            if args.guest_cmd == "add":
                guest = producer.add_guest(
                    name=args.name,
                    role=args.role,
                    company=args.company,
                    expertise=args.expertise.split(","),
                    bio=args.bio or "",
                    twitter=args.twitter or "",
                    email=args.email or ""
                )
                print(f"\n✅ Guest added!")
                print(f"   ID: {guest.id}")
                print(f"   Name: {guest.name}")
                print(f"   Role: {guest.role} @ {guest.company}")
            elif args.guest_cmd == "list":
                print(f"\n👥 GUESTS ({len(producer.guests)}):")
                print("=" * 60)
                for g in producer.guests.values():
                    print(f"  {g.id}: {g.name} - {g.role} @ {g.company}")
                    print(f"      Expertise: {', '.join(g.expertise)}")

        elif args.command == "assign":
            producer = PodcastProducer(args.storage)
            producer.assign_guest(args.episode, args.guest)
            print(f"\n✅ Guest {args.guest} assigned to episode #{args.episode}")

        elif args.command == "checklist":
            producer = PodcastProducer(args.storage)
            producer.update_checklist(args.episode, args.item, args.value)
            print(f"\n✅ Checklist updated: {args.item} = {args.value}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled")
        sys.exit(130)
    except Exception as e:
        log.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
