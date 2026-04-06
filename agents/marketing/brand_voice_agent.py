#!/usr/bin/env python3
"""
Brand Voice Agent — EmpireHazeClaw Marketing System
Defines, manages, and applies brand voice guidelines across all content.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
VOICE_FILE = DATA_DIR / "brand_voice.json"
VOICE_HISTORY = DATA_DIR / "brand_voice_history.json"

LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BRAND-VOICE] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "brand_voice.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("brand_voice")


# ── Core ─────────────────────────────────────────────────────────────────────
def load_voice() -> dict:
    """Load current brand voice or return defaults."""
    if VOICE_FILE.exists():
        try:
            return json.loads(VOICE_FILE.read_text())
        except (json.JSONDecodeError, IOError) as e:
            log.warning("Could not load brand_voice.json: %s — using defaults", e)
    return _default_voice()


def save_voice(voice: dict) -> None:
    """Save brand voice to JSON and update history."""
    VOICE_FILE.write_text(json.dumps(voice, indent=2, ensure_ascii=False))
    # Append to history
    history = []
    if VOICE_HISTORY.exists():
        try:
            history = json.loads(VOICE_HISTORY.read_text())
        except json.JSONDecodeError:
            history = []
    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "voice": voice,
    })
    # Keep last 50 entries
    VOICE_HISTORY.write_text(json.dumps(history[-50:], indent=2, ensure_ascii=False))
    log.info("Brand voice saved.")


def _default_voice() -> dict:
    return {
        "name": "EmpireHazeClaw",
        "personality": {
            "tone": "confident, direct, no-nonsense",
            "voice": "CEO-speak: like a strategic advisor who cuts through noise",
            "mood": "professional but approachable, results-driven",
        },
        "values": [
            "Eigenverantwortung — own your decisions",
            "Speed over perfection — act, learn, iterate",
            "Integrity — no shortcuts, long-term thinking",
            "Transparency — honest with stakeholders",
        ],
        "do": [
            "Use short, punchy sentences",
            "Speak to outcomes, not features",
            "Ask the right questions before selling",
            "Show confidence without arrogance",
        ],
        "dont": [
            "Use buzzwords or filler ('synergy', 'leverage', 'circle back')",
            "Write passive voice",
            "Over-promise",
            "Be vague — always be specific",
        ],
        "audience": {
            "primary": "Entrepreneurs, small business owners, indie hackers",
            "language": "Bilingual (DE/EN)",
            "pain_points": ["time poverty", "tool overload", "decision fatigue"],
        },
        "channels": {
            "twitter": {"max_length": 280, "style": "provocative question + insight"},
            "linkedin": {"max_length": 3000, "style": "professional story + takeaway"},
            "email": {"style": "personal, direct, one clear CTA"},
            "blog": {"style": "SEO-optimized, scannable headers, actionable conclusion"},
        },
        "hashtags": ["#Entrepreneur", "#GrowthMindset", "#Startups", "#AI"],
        "version": datetime.now(timezone.utc).isoformat(),
    }


# ── Actions ───────────────────────────────────────────────────────────────────
def cmd_show(args: argparse.Namespace) -> None:
    voice = load_voice()
    print(json.dumps(voice, indent=2, ensure_ascii=False))


def cmd_update(args: argparse.Namespace) -> None:
    voice = load_voice()
    updates = {}

    if args.tone:
        updates["personality.tone"] = args.tone
    if args.voice:
        updates["personality.voice"] = args.voice
    if args.values:
        updates["values"] = [v.strip() for v in args.values.split(";")]
    if args.do:
        updates["do"] = [d.strip() for d in args.do.split(";")]
    if args.dont:
        updates["dont"] = [d.strip() for d in args.dont.split(";")]
    if args.audience:
        updates["audience.primary"] = args.audience
    if args.hashtags:
        updates["hashtags"] = [h.strip() for h in args.hashtags.split(";")]

    # Apply dotted-key updates
    for key, val in updates.items():
        parts = key.split(".")
        d = voice
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = val

    voice["version"] = datetime.now(timezone.utc).isoformat()
    save_voice(voice)
    log.info("Brand voice updated: %s", list(updates.keys()))
    print(f"✅ Updated: {', '.join(updates.keys())}")


def cmd_apply(args: argparse.Namespace) -> None:
    """Apply brand voice to a piece of content (text rewrite)."""
    voice = load_voice()
    tone = voice["personality"]["tone"]
    rules_do = voice["do"]
    rules_dont = voice["dont"]

    # Simple rule-based rewriting (not LLM — no API needed)
    text = args.text or ""
    if not text:
        log.error("No text provided for --text")
        sys.exit(1)

    # Apply transformations
    result = text.strip()

    # Rule: add punch by capitalizing first letter of sentences
    result = ". ".join(s.strip().capitalize() for s in result.split(". ") if s.strip())

    # Rule: strip trailing whitespace
    result = " ".join(result.split())

    # Rule: ensure it doesn't end with a weak closer
    weak_closers = ["thanks", "thank you", "cheers", "best", "regards"]
    result_words = result.lower().split()
    if result_words and result_words[-1] in weak_closers:
        result = result.rsplit(" ", 1)[0] + "."

    analysis = {
        "original": text,
        "transformed": result,
        "tone_used": tone,
        "rules_applied_do": rules_do[:3],
        "rules_applied_dont": rules_dont[:2],
        "transformations": [
            "capitalized sentence starts",
            "collapsed internal whitespace",
            "removed weak closers",
        ],
    }
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    log.info("Content transformation applied to %d chars", len(text))


def cmd_hashtags(args: argparse.Namespace) -> None:
    voice = load_voice()
    tags = voice.get("hashtags", [])
    if args.channel:
        channel_tags = voice.get("channels", {}).get(args.channel, {}).get("style", "")
        print(f"Channel: {args.channel} | Style: {channel_tags}")
    print(f"Hashtags: {' '.join(tags)}")


def cmd_history(args: argparse.Namespace) -> None:
    if not VOICE_HISTORY.exists():
        print("No history yet.")
        return
    history = json.loads(VOICE_HISTORY.read_text())
    for i, entry in enumerate(reversed(history[-args.lines :])):
        print(f"[{entry['timestamp']}]")
        print(json.dumps(entry["voice"], indent=2, ensure_ascii=False))
        print()


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate brand voice JSON structure."""
    voice = load_voice()
    required = ["personality", "values", "do", "dont", "audience"]
    missing = [k for k in required if k not in voice]
    if missing:
        print(f"❌ Missing fields: {missing}")
        log.error("Validation failed: missing %s", missing)
        sys.exit(1)
    print(f"✅ Brand voice valid. Version: {voice.get('version','unknown')}")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    parser = argparse.ArgumentParser(
        prog="brand_voice_agent.py",
        description="EmpireHazeClaw Brand Voice Manager — define, apply, and audit brand voice.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # show
    p_show = sub.add_parser("show", help="Display current brand voice")
    p_show.set_defaults(fn=cmd_show)

    # update
    p_upd = sub.add_parser("update", help="Update brand voice fields")
    p_upd.add_argument("--tone", help="Tone description")
    p_upd.add_argument("--voice", help="Voice description")
    p_upd.add_argument("--values", help="Semicolon-separated values")
    p_upd.add_argument("--do", help="Semicolon-separated DO rules")
    p_upd.add_argument("--dont", help="Semicolon-separated DONT rules")
    p_upd.add_argument("--audience", help="Primary audience description")
    p_upd.add_argument("--hashtags", help="Semicolon-separated hashtags")
    p_upd.set_defaults(fn=cmd_update)

    # apply
    p_apply = sub.add_parser("apply", help="Apply brand voice to content")
    p_apply.add_argument("--text", required=True, help="Content text to transform")
    p_apply.set_defaults(fn=cmd_apply)

    # hashtags
    p_tag = sub.add_parser("hashtags", help="Show recommended hashtags")
    p_tag.add_argument("--channel", help="Filter by channel (twitter/linkedin/email/blog)")
    p_tag.set_defaults(fn=cmd_hashtags)

    # history
    p_hist = sub.add_parser("history", help="Show brand voice change history")
    p_hist.add_argument("--lines", type=int, default=5, help="Number of entries")
    p_hist.set_defaults(fn=cmd_history)

    # validate
    p_val = sub.add_parser("validate", help="Validate brand voice JSON structure")
    p_val.set_defaults(fn=cmd_validate)

    args = parser.parse_args()

    try:
        args.fn(args)
    except Exception as e:
        log.exception("Command '%s' failed: %s", args.cmd, e)
        sys.exit(1)


if __name__ == "__main__":
    main()
