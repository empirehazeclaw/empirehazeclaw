#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SCRIPT WRITER AGENT                               ║
║          Video Scripts, Podcast Scripts, Presentation       ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 script_writer_agent.py --help
  python3 script_writer_agent.py --task video --topic "KI Trends 2026" --duration 5 --lang de --output scripts.json
  python3 script_writer_agent.py --task podcast --topic "Startup Growth" --duration 30 --lang en
  python3 script_writer_agent.py --list

Data: ~/.openclaw/workspace/data/scripts/
Logs: /home/clawbot/.openclaw/workspace/logs/script_writer.log
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "scripts"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "scripts_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "script_writer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.script_writer")


# ── Enums ───────────────────────────────────────────────────────────────────
class ScriptType(str, Enum):
    VIDEO = "video"
    PODCAST = "podcast"
    PRESENTATION = "presentation"
    AD_SPOT = "ad_spot"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    DRAMATIC = "dramatic"
    EDUCATIONAL = "educational"


class Audience(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    GENERAL = "general"
    B2B = "b2b"
    GenZ = "genz"


# ── Dataclasses ─────────────────────────────────────────────────────────────
@dataclass
class ScriptSpec:
    task: ScriptType
    topic: str
    duration_minutes: int = 5
    language: str = "de"
    tone: Tone = Tone.PROFESSIONAL
    audience: Audience = Audience.GENERAL
    include_music_cues: bool = True
    include_visuals: bool = True
    hook: str = ""
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v.value if isinstance(v, Enum) else k for k, v in asdict(self).items()}


@dataclass
class ScriptSection:
    """Single section / scene within a script."""
    section_type: str          # "hook", "intro", "main", "outro", "cta"
    title: str
    duration_seconds: int
    speaker_text: str
    visual_notes: str = ""
    music_cue: str = ""
    on_screen_text: str = ""


@dataclass
class ScriptResult:
    """Complete generated script."""
    spec: Dict[str, Any]
    title: str
    genre: str
    sections: List[Dict[str, Any]]
    total_duration_minutes: float
    word_count: int
    cta_text: str = ""
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec": self.spec,
            "title": self.title,
            "genre": self.genre,
            "sections": self.sections,
            "total_duration_minutes": self.total_duration_minutes,
            "word_count": self.word_count,
            "cta_text": self.cta_text,
            "generated_at": self.generated_at,
        }


# ── Script Storage ───────────────────────────────────────────────────────────
def load_cache() -> Dict[str, Any]:
    """Load cached scripts from JSON."""
    if not CACHE_FILE.exists():
        return {"scripts": [], "version": "1.0"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.warning("Cache read error: %s — resetting", e)
        return {"scripts": [], "version": "1.0"}


def save_cache(cache: Dict[str, Any]) -> None:
    """Persist scripts cache to JSON."""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ── Script Templates ─────────────────────────────────────────────────────────
HOOK_TEMPLATES = {
    ScriptType.VIDEO: [
        "Stop scrolling. What if I told you that {topic} could change everything?",
        "Most people get {topic} completely wrong. Here's why...",
        "I spent 3 years mastering {topic}. In the next {dur} minutes, I'll show you everything.",
    ],
    ScriptType.PODCAST: [
        "Welcome back to the show. Today: {topic} — let's dive in.",
        "Grab your coffee. We're talking {topic} and I promise you haven't heard this angle.",
    ],
    ScriptType.YOUTUBE: [
        "If you only watch one video about {topic}, make it this one.",
        "{topic}: The complete guide you've been searching for. Let's go.",
    ],
    ScriptType.TIKTOK: [
        "POV: You just discovered {topic} 🫵",
        "3 things about {topic} that nobody talks about 👀",
    ],
    ScriptType.PRESENTATION: [
        "Good {time_of_day}. Today I want to share insights on {topic} that can transform your approach.",
    ],
}

CTA_TEMPLATES = {
    ScriptType.VIDEO: "Like, subscribe, and hit the bell so you never miss an update!",
    ScriptType.PODCAST: "If you enjoyed this episode, please leave a review and share it with someone who'd benefit.",
    ScriptType.YOUTUBE: " Smash that subscribe button and join our community of {subscribers}+ learners!",
    ScriptType.TIKTOK: "Follow for more tips on {topic} — see you in the next one!",
    ScriptType.PRESENTATION: "Thank you. I'm happy to take questions now.",
}

MUSIC_CUES = {
    "intro": "Upbeat, energetic (0:00–0:05)",
    "hook": "Tension rise, dramatic (0:05–0:15)",
    "main": "Soft background, non-distracting (continuous)",
    "outro": "Wind down, emotional (final 30s)",
    "cta": "Positive jingle (10s)",
}


# ── Core Generator ───────────────────────────────────────────────────────────
class ScriptWriterAgent:
    """Generates structured scripts for video, podcast, presentation, and short-form content."""

    def __init__(self):
        self.cache = load_cache()
        log.info("ScriptWriterAgent initialized. %d scripts in cache.", len(self.cache.get("scripts", [])))

    def generate(self, spec: ScriptSpec) -> ScriptResult:
        """Generate a complete script based on the spec."""
        log.info("🎬 Generating %s script: '%s' (%d min, %s, %s)",
                 spec.task.value, spec.topic, spec.duration_minutes, spec.tone.value, spec.language)

        try:
            sections = self._build_sections(spec)
            total_words = sum(len(s["speaker_text"].split()) for s in sections)

            result = ScriptResult(
                spec=spec.to_dict(),
                title=self._generate_title(spec),
                genre=self._assign_genre(spec),
                sections=sections,
                total_duration_minutes=spec.duration_minutes,
                word_count=total_words,
                cta_text=self._build_cta(spec),
            )

            self._save_script(result)
            log.info("✅ Script generated: %s (%d words, %d sections)",
                     result.title, result.word_count, len(result.sections))
            return result

        except Exception as e:
            log.error("Script generation failed: %s", e)
            raise

    def _build_sections(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """Build all script sections based on script type and duration."""
        dur = spec.duration_minutes * 60  # seconds

        if spec.task == ScriptType.TIKTOK:
            return self._build_tiktok(spec)
        elif spec.task == ScriptType.VIDEO:
            return self._build_video(spec)
        elif spec.task == ScriptType.PODCAST:
            return self._build_podcast(spec)
        elif spec.task == ScriptType.YOUTUBE:
            return self._build_youtube(spec)
        elif spec.task == ScriptType.PRESENTATION:
            return self._build_presentation(spec)
        elif spec.task == ScriptType.AD_SPOT:
            return self._build_ad_spot(spec)
        else:
            return self._build_video(spec)

    def _build_tiktok(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """TikTok: hook → 3 rapid points → CTA (30–90s)."""
        hook_text = spec.hook or self._pick_hook(spec)
        dur = spec.duration_minutes * 60
        point_dur = max(10, (dur - 20) // 3)

        sections = [
            {
                "section_type": "hook",
                "title": "Hook",
                "duration_seconds": 5,
                "speaker_text": hook_text,
                "visual_notes": "Fast cut, bold text on screen, face close-up",
                "music_cue": MUSIC_CUES["hook"] if spec.include_music_cues else "",
                "on_screen_text": "👇",
            },
            {
                "section_type": "main",
                "title": f"Point 1: {spec.topic}",
                "duration_seconds": point_dur,
                "speaker_text": f"Here's the first thing you need to know about {spec.topic}. It's simpler than you think — and it starts with {spec.keywords[0] if spec.keywords else 'focus'}.",
                "visual_notes": "B-roll, text overlay, fast transitions",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": f"1/3: {spec.keywords[0] if spec.keywords else spec.topic}",
            },
            {
                "section_type": "main",
                "title": "Point 2",
                "duration_seconds": point_dur,
                "speaker_text": f"Second insight about {spec.topic}: Most people skip this step, but it's the one that actually moves the needle.",
                "visual_notes": "Same style, different B-roll",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "2/3: Don't skip this",
            },
            {
                "section_type": "main",
                "title": "Point 3",
                "duration_seconds": point_dur,
                "speaker_text": f"And third — the secret nobody tells you about {spec.topic}. Remember this one.",
                "visual_notes": "Reaction shot, engaging visuals",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "3/3: The secret",
            },
            {
                "section_type": "cta",
                "title": "CTA",
                "duration_seconds": 5,
                "speaker_text": "Follow for more — I'll see you in the next one!",
                "visual_notes": "End card with follow button",
                "music_cue": MUSIC_CUES["cta"] if spec.include_music_cues else "",
                "on_screen_text": "+ Follow",
            },
        ]
        return sections

    def _build_video(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """Standard video: hook → intro → 3 sections → conclusion → CTA."""
        dur = spec.duration_minutes * 60
        hook_dur = min(15, dur // 20)
        intro_dur = min(30, dur // 10)
        main_dur = (dur - hook_dur - intro_dur - 30) // 3
        outro_dur = 20

        sections = [
            {
                "section_type": "hook",
                "title": "Hook (0:00–{})".format(hook_dur),
                "duration_seconds": hook_dur,
                "speaker_text": spec.hook or self._pick_hook(spec),
                "visual_notes": "Teaser visuals, quick cuts" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["hook"] if spec.include_music_cues else "",
                "on_screen_text": spec.topic,
            },
            {
                "section_type": "intro",
                "title": "Intro ({}–{})".format(hook_dur, hook_dur + intro_dur),
                "duration_seconds": intro_dur,
                "speaker_text": f"Welcome! In this {spec.duration_minutes}-minute video about {spec.topic}, I'm going to walk you through everything you need to know. By the end, you'll have a clear action plan.",
                "visual_notes": "Host on camera, title card" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["intro"] if spec.include_music_cues else "",
                "on_screen_text": f"{spec.topic} | {spec.duration_minutes} min",
            },
            {
                "section_type": "main",
                "title": "Section 1: Foundation",
                "duration_seconds": main_dur,
                "speaker_text": f"Let's start with the foundations of {spec.topic}. Understanding this is critical — everything else builds on it. Key point: {spec.keywords[0] if spec.keywords else 'focus on the basics'}.",
                "visual_notes": "Screenshare / illustrations" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "Foundation",
            },
            {
                "section_type": "main",
                "title": "Section 2: Deep Dive",
                "duration_seconds": main_dur,
                "speaker_text": f"Now let's go deeper into {spec.topic}. Here's where most people stop — but we're going further. Point two: {spec.keywords[1] if len(spec.keywords) > 1 else 'iteration beats perfection'}.",
                "visual_notes": "Data visuals, charts" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "Deep Dive",
            },
            {
                "section_type": "main",
                "title": "Section 3: Action Steps",
                "duration_seconds": main_dur,
                "speaker_text": f"Practical time. Here's exactly what to do with {spec.topic} starting today. Step by step. Point three: {spec.keywords[2] if len(spec.keywords) > 2 else 'take action now'}.",
                "visual_notes": "Step-by-step visuals, checklist" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "Action Steps",
            },
            {
                "section_type": "outro",
                "title": "Conclusion",
                "duration_seconds": outro_dur,
                "speaker_text": f"To wrap up: {spec.topic} comes down to {spec.keywords[0] if spec.keywords else 'focus, consistency, and learning'}. Start small, stay consistent, and the results will come. Let's do this.",
                "visual_notes": "Host recap, outro screen" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["outro"] if spec.include_music_cues else "",
                "on_screen_text": "Key Takeaways",
            },
            {
                "section_type": "cta",
                "title": "Call to Action",
                "duration_seconds": 10,
                "speaker_text": CTA_TEMPLATES[ScriptType.VIDEO],
                "visual_notes": "Subscribe button, end screen" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["cta"] if spec.include_music_cues else "",
                "on_screen_text": "Subscribe",
            },
        ]
        return sections

    def _build_podcast(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """Podcast: intro music → intro → main discussion → outro."""
        dur = spec.duration_minutes * 60
        intro_dur = 60
        outro_dur = 60
        main_dur = dur - intro_dur - outro_dur

        sections = [
            {
                "section_type": "intro",
                "title": "Intro Music + Welcome",
                "duration_seconds": intro_dur,
                "speaker_text": f"Welcome to another episode! Today we're diving into {spec.topic}. I'm your host — let's get into it.",
                "visual_notes": "Audio only",
                "music_cue": "Podcast jingle (0:00–0:20), host intro (0:20–1:00)",
                "on_screen_text": "",
            },
            {
                "section_type": "main",
                "title": f"Discussion: {spec.topic}",
                "duration_seconds": main_dur,
                "speaker_text": self._build_podcast_body(spec),
                "visual_notes": "Audio only",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": "",
            },
            {
                "section_type": "outro",
                "title": "Outro",
                "duration_seconds": outro_dur,
                "speaker_text": f"That's a wrap on {spec.topic}. If you found value, share this episode with someone who'd love it. See you next time!",
                "visual_notes": "Audio only",
                "music_cue": "Podcast outro jingle",
                "on_screen_text": "",
            },
        ]
        return sections

    def _build_youtube(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """YouTube long-form: similar to video but with chapter markers."""
        sections = self._build_video(spec)
        for s in sections:
            s["chapter_marker"] = True
        return sections

    def _build_presentation(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """Presentation: agenda → sections → Q&A → close."""
        dur = spec.duration_minutes * 60
        agenda_dur = 60
        section_dur = (dur - agenda_dur - 120) // max(1, len(spec.keywords or [1, 2, 3]))
        qa_dur = 60

        sections = [
            {
                "section_type": "intro",
                "title": "Agenda",
                "duration_seconds": agenda_dur,
                "speaker_text": f"Good morning/afternoon. Today I'll cover {spec.topic} in {spec.duration_minutes} minutes. Here's our agenda: {', '.join(spec.keywords[:3]) if spec.keywords else 'Background, Core Concepts, Recommendations'}.",
                "visual_notes": "Slide 1: Agenda" if spec.include_visuals else "",
                "music_cue": "",
                "on_screen_text": "Agenda",
            },
        ]

        for i, kw in enumerate((spec.keywords or ["Context", "Core", "Recommendations"])[:4]):
            sections.append({
                "section_type": "main",
                "title": f"Part {i+1}: {kw}",
                "duration_seconds": section_dur,
                "speaker_text": f"Let's talk about {kw} in the context of {spec.topic}. This is where it gets practical.",
                "visual_notes": f"Slide {i+2}: {kw}" if spec.include_visuals else "",
                "music_cue": "",
                "on_screen_text": kw,
            })

        sections.append({
            "section_type": "outro",
            "title": "Q&A + Close",
            "duration_seconds": qa_dur,
            "speaker_text": CTA_TEMPLATES[ScriptType.PRESENTATION],
            "visual_notes": "Closing slide" if spec.include_visuals else "",
            "music_cue": "",
            "on_screen_text": "Questions?",
        })
        return sections

    def _build_ad_spot(self, spec: ScriptSpec) -> List[Dict[str, Any]]:
        """Ad spot: ultra-tight, CTA-first, 15–60s."""
        dur = min(spec.duration_minutes * 60, 60)
        hook_dur = 5
        body_dur = dur - hook_dur - 10

        return [
            {
                "section_type": "hook",
                "title": "Hook",
                "duration_seconds": hook_dur,
                "speaker_text": spec.hook or f"Imagine {spec.topic} — without the usual headaches.",
                "visual_notes": "Bold visual, fast cut" if spec.include_visuals else "",
                "music_cue": "High-energy track" if spec.include_music_cues else "",
                "on_screen_text": "Stop. Look.",
            },
            {
                "section_type": "main",
                "title": "Body",
                "duration_seconds": body_dur,
                "speaker_text": f"{spec.topic}: {spec.keywords[0] if spec.keywords else 'Better'}, {spec.keywords[1] if len(spec.keywords) > 1 else 'faster'}, {spec.keywords[2] if len(spec.keywords) > 2 else 'smarter'}.",
                "visual_notes": "Product/demo visuals" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["main"] if spec.include_music_cues else "",
                "on_screen_text": spec.topic,
            },
            {
                "section_type": "cta",
                "title": "CTA",
                "duration_seconds": 10,
                "speaker_text": "Try it free today at empirehazeclaw.com",
                "visual_notes": "URL on screen" if spec.include_visuals else "",
                "music_cue": MUSIC_CUES["cta"] if spec.include_music_cues else "",
                "on_screen_text": "empirehazeclaw.com",
            },
        ]

    def _build_podcast_body(self, spec: ScriptSpec) -> str:
        """Build the main podcast discussion body."""
        points = []
        for i, kw in enumerate((spec.keywords or ["background", "insights", "action"])[:3]):
            points.append(
                f"Point {i+1} — {kw.capitalize()}: When it comes to {spec.topic}, {kw} is often overlooked. "
                f"Here's my take after working in this space."
            )
        return "\n\n".join(points) + f"\n\nWrapping up: {spec.topic} is worth investing your time in. The key is to start before you're ready."

    def _pick_hook(self, spec: ScriptSpec) -> str:
        """Select a hook template based on script type."""
        templates = HOOK_TEMPLATES.get(spec.task, HOOK_TEMPLATES[ScriptType.VIDEO])
        hook = templates[len(spec.topic) % len(templates)]
        return hook.format(topic=spec.topic, dur=spec.duration_minutes)

    def _generate_title(self, spec: ScriptSpec) -> str:
        """Generate an engaging title."""
        templates = {
            ScriptType.VIDEO: "{topic} — Complete Guide {year}",
            ScriptType.PODCAST: "Episode: {topic} | {year}",
            ScriptType.YOUTUBE: "{topic} — Everything You Need to Know in {dur} Min",
            ScriptType.TIKTOK: "{topic} (Things Nobody Tells You) 🔥",
            ScriptType.PRESENTATION: "{topic} — Executive Briefing",
            ScriptType.AD_SPOT: "Ad: {topic} | {brand}",
        }
        year = datetime.now().year
        template = templates.get(spec.task, templates[ScriptType.VIDEO])
        return template.format(
            topic=spec.topic,
            year=year,
            dur=spec.duration_minutes,
            brand="EmpireHazeClaw"
        )

    def _assign_genre(self, spec: ScriptSpec) -> str:
        """Assign genre based on tone and audience."""
        mapping = {
            (Tone.EDUCATIONAL, Audience.GENERAL): "Educational",
            (Tone.HUMOROUS, Audience.GenZ): "Comedy/Entertainment",
            (Tone.INSPIRATIONAL, Audience.GENERAL): "Inspirational",
            (Tone.PROFESSIONAL, Audience.B2B): "Business/Corporate",
            (Tone.PROFESSIONAL, Audience.EXPERT): "Technical Deep-Dive",
        }
        return mapping.get((spec.tone, spec.audience), "General Interest")

    def _build_cta(self, spec: ScriptSpec) -> str:
        """Build CTA text."""
        cta = CTA_TEMPLATES.get(spec.task, "Learn more at empirehazeclaw.com")
        if "{topic}" in cta:
            cta = cta.format(topic=spec.topic)
        return cta

    def _save_script(self, result: ScriptResult) -> None:
        """Save script to cache."""
        self.cache.setdefault("scripts", []).insert(0, result.to_dict())
        # Keep last 100 scripts
        self.cache["scripts"] = self.cache["scripts"][:100]
        save_cache(self.cache)

    def list_scripts(self) -> List[Dict[str, Any]]:
        """Return all cached scripts."""
        return self.cache.get("scripts", [])

    def get_script(self, title: str) -> Optional[Dict[str, Any]]:
        """Get a specific script by title."""
        for s in self.cache.get("scripts", []):
            if s.get("title") == title:
                return s
        return None

    def export_script_text(self, result: ScriptResult) -> str:
        """Render a ScriptResult as plain readable text."""
        lines = [
            f"{'='*60}",
            f"TITLE:  {result.title}",
            f"Genre:  {result.genre}",
            f"Type:   {result.spec.get('task', 'unknown')}",
            f"Duration: {result.total_duration_minutes} min | Words: {result.word_count}",
            f"Generated: {result.generated_at}",
            f"{'='*60}",
            "",
        ]
        for sec in result.sections:
            dur = sec["duration_seconds"]
            lines.append(f"[{sec['section_type'].upper()}] {sec['title']} ({dur}s)")
            lines.append(f"  🎤 {sec['speaker_text']}")
            if sec.get("visual_notes"):
                lines.append(f"  🎥 Visuals: {sec['visual_notes']}")
            if sec.get("music_cue"):
                lines.append(f"  🎵 Music: {sec['music_cue']}")
            if sec.get("on_screen_text"):
                lines.append(f"  📺 On-Screen: {sec['on_screen_text']}")
            lines.append("")
        lines.append(f"{'='*60}")
        lines.append(f"CTA: {result.cta_text}")
        lines.append(f"{'='*60}")
        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="script_writer_agent.py",
        description="🎬 Script Writer Agent — Video, Podcast, Presentation, TikTok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a 5-min YouTube video script
  python3 script_writer_agent.py --task video --topic "KI Trends 2026" --duration 5 --lang de

  # Generate a podcast episode (30 min, English)
  python3 script_writer_agent.py --task podcast --topic "Startup Growth Hacks" --duration 30 --lang en

  # TikTok script (60s, GenZ audience)
  python3 script_writer_agent.py --task tiktok --topic "Productivity Hacks" --duration 1 --audience genz

  # List all cached scripts
  python3 script_writer_agent.py --list

  # Export a specific script as text
  python3 script_writer_agent.py --export "KI Trends 2026 — Complete Guide 2026"

  # Search scripts by keyword
  python3 script_writer_agent.py --search "podcast"
        """
    )
    parser.add_argument("--task", choices=[t.value for t in ScriptType], help="Type of script to generate")
    parser.add_argument("--topic", type=str, help="Main topic/keyword of the script")
    parser.add_argument("--duration", "--duration-minutes", dest="duration", type=int, default=5,
                        help="Duration in minutes (default: 5)")
    parser.add_argument("--lang", "--language", dest="lang", choices=["de", "en", "fr", "es"], default="de",
                        help="Script language (default: de)")
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.PROFESSIONAL.value,
                        help="Tone of the script (default: professional)")
    parser.add_argument("--audience", choices=[a.value for a in Audience], default=Audience.GENERAL.value,
                        help="Target audience (default: general)")
    parser.add_argument("--keywords", type=str, default="",
                        help="Comma-separated keywords (e.g. 'AI,automation,growth')")
    parser.add_argument("--hook", type=str, default="",
                        help="Custom hook/opening line (optional)")
    parser.add_argument("--no-music", dest="no_music", action="store_true",
                        help="Exclude music cues")
    parser.add_argument("--no-visuals", dest="no_visuals", action="store_true",
                        help="Exclude visual notes")
    parser.add_argument("--output", "--save-to", dest="output", type=str,
                        help="Save result to a specific JSON file")
    parser.add_argument("--list", action="store_true", help="List all cached scripts")
    parser.add_argument("--export", type=str, metavar="TITLE",
                        help="Export a specific script by title as readable text")
    parser.add_argument("--search", type=str, metavar="TERM",
                        help="Search cached scripts by keyword/topic")
    return parser.parse_args()


def main() -> None:
    agent = ScriptWriterAgent()
    args = parse_args()

    # --list
    if args.list:
        scripts = agent.list_scripts()
        if not scripts:
            print("No scripts in cache.")
            return
        print(f"\n📋 Cached Scripts ({len(scripts)} total)\n")
        for s in scripts:
            ts = s.get("generated_at", "")[:16]
            print(f"  [{ts}] {s.get('title','?')} | {s.get('spec',{}).get('task','?')} | {s.get('word_count',0)} words")
        return

    # --search
    if args.search:
        term = args.search.lower()
        results = [s for s in agent.list_scripts() if term in s.get("title", "").lower() or term in s.get("spec", {}).get("topic", "").lower()]
        print(f"\n🔍 Search results for '{args.search}' ({len(results)} found)\n")
        for s in results:
            print(f"  {s.get('title', '?')} | {s.get('generated_at','')[:16]}")
        return

    # --export
    if args.export:
        script = agent.get_script(args.export)
        if not script:
            print(f"Script not found: {args.export}")
            sys.exit(1)
        # Reconstruct as ScriptResult dict for rendering
        print(agent.export_script_text(
            ScriptResult(
                spec=script["spec"], title=script["title"],
                genre=script["genre"], sections=script["sections"],
                total_duration_minutes=script["total_duration_minutes"],
                word_count=script["word_count"],
                cta_text=script.get("cta_text", ""),
                generated_at=script.get("generated_at", ""),
            )
        ))
        return

    # --generate
    if not args.task or not args.topic:
        print("ERROR: --task and --topic are required for generation.")
        print("Run with --help for usage.")
        sys.exit(1)

    spec = ScriptSpec(
        task=ScriptType(args.task),
        topic=args.topic,
        duration_minutes=args.duration,
        language=args.lang,
        tone=Tone(args.tone),
        audience=Audience(args.audience),
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()],
        hook=args.hook,
        include_music_cues=not args.no_music,
        include_visuals=not args.no_visuals,
    )

    result = agent.generate(spec)

    # Save to custom file if requested
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"💾 Saved to {out_path}")

    # Print to console
    print(f"\n{'='*60}")
    print(f"🎬 {result.title}")
    print(f"   Type: {args.task} | {result.total_duration_minutes} min | {result.word_count} words")
    print(f"   Genre: {result.genre}")
    print(f"{'='*60}\n")
    for sec in result.sections:
        dur = sec["duration_seconds"]
        print(f"[{sec['section_type'].upper():8s}] {sec['title']} ({dur}s)")
        print(f"  🎤 {sec['speaker_text'][:120]}{'...' if len(sec['speaker_text']) > 120 else ''}")
        if sec.get("visual_notes"):
            print(f"  🎥 {sec['visual_notes']}")
        if sec.get("music_cue"):
            print(f"  🎵 {sec['music_cue']}")
        print()


if __name__ == "__main__":
    main()
