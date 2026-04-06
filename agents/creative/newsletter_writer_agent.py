#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          NEWSLETTER WRITER AGENT                           ║
║          Email Newsletters — DE/EN, 6 Templates            ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 newsletter_writer_agent.py --help
  python3 newsletter_writer_agent.py --topic "March Update" --type weekly --lang de
  python3 newsletter_writer_agent.py --topic "New Feature Launch" --type product --lang en
  python3 newsletter_writer_agent.py --list

Data: ~/.openclaw/workspace/data/newsletters/
Logs: /home/clawbot/.openclaw/workspace/logs/newsletter_writer.log
"""

import argparse
import json
import logging
import random
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "newsletters"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "newsletter_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "newsletter_writer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.newsletter_writer")


class NewsletterType(str, Enum):
    WEEKLY = "weekly"           # Regular weekly update
    PRODUCT_LAUNCH = "product"  # New product/feature
    PROMO = "promo"            # Promotional / offer
    WELCOME = "welcome"        # Onboarding new subscribers
    REENGAGEMENT = "reengage"  # Win back inactive subscribers
    CONTENT_DIGEST = "digest"  # Curated content roundup


class Tone(str, Enum):
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    EXCITED = "excited"
    FORMAL = "formal"


@dataclass
class NewsletterSpec:
    topic: str
    nl_type: NewsletterType
    language: str = "de"
    tone: Tone = Tone.FRIENDLY
    subscriber_name: str = ""
    brand: str = "EmpireHazeClaw"
    website: str = "empirehazeclaw.com"
    featured_items: List[str] = field(default_factory=list)
    cta_text: str = ""
    cta_url: str = ""
    discount_code: str = ""
    discount_percent: int = 0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v.value if isinstance(v, Enum) else v for k, v in d.items()}


@dataclass
class NewsletterResult:
    spec: Dict[str, Any]
    subject: str
    preview_text: str
    sections: List[Dict[str, str]]
    word_count: int
    cta_text: str
    estimated_open_rate: float
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


def load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"newsletters": [], "version": "1.0"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.warning("Cache read error: %s", e)
        return {"newsletters": [], "version": "1.0"}


def save_cache(cache: Dict[str, Any]) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


class NewsletterWriterAgent:
    """Generates email newsletters for multiple use cases and languages."""

    def __init__(self):
        self.cache = load_cache()
        log.info("NewsletterWriterAgent initialized. %d newsletters in cache.",
                 len(self.cache.get("newsletters", [])))

    def generate(self, spec: NewsletterSpec) -> NewsletterResult:
        log.info("📧 Generating newsletter: '%s' (%s, %s)", spec.topic, spec.nl_type.value, spec.language)
        try:
            subject = self._build_subject(spec)
            preview = self._build_preview(spec)
            sections = self._build_sections(spec)
            word_count = sum(len(s["content"].split()) for s in sections)
            cta = spec.cta_text or self._default_cta(spec)
            open_rate = self._estimate_open_rate(spec, subject)

            result = NewsletterResult(
                spec=spec.to_dict(),
                subject=subject,
                preview_text=preview,
                sections=sections,
                word_count=word_count,
                cta_text=cta,
                estimated_open_rate=open_rate,
            )
            self._save(result)
            log.info("✅ Newsletter generated: '%s' (%d words, open rate: %.0f%%)", subject, word_count, open_rate * 100)
            return result
        except Exception as e:
            log.error("Newsletter generation failed: %s", e)
            raise

    def _build_subject(self, spec: NewsletterSpec) -> str:
        subjects = {
            NewsletterType.WEEKLY: {
                "de": ["Das war diese Woche bei {brand}: {topic}", "Dein Weekly Update — {topic}", "KW {week}: {topic}"],
                "en": ["This week at {brand}: {topic}", "Your weekly digest — {topic}", "Week {week}: {topic}"],
            },
            NewsletterType.PRODUCT_LAUNCH: {
                "de": ["Neues Feature: {topic} ist da! 🎉", "Exklusiv: {topic} — jetzt entdecken!", "ANGEKÜNDIGT: {topic}"],
                "en": ["Introducing: {topic} is live! 🎉", "Exclusive: {topic} — discover it now!", "ANNOUNCING: {topic}"],
            },
            NewsletterType.PROMO: {
                "de": ["🎁 {discount}% Rabatt auf {topic} — nur kurz!", "Dein persönlicher Code: {code}", "Nur diese Woche: {topic} sparen!"],
                "en": ["🎁 {discount}% OFF on {topic} — limited time!", "Your personal code: {code}", "This week only: save on {topic}!"],
            },
            NewsletterType.WELCOME: {
                "de": ["Willkommen bei {brand}! {topic}", "Schön, dass du da bist — {topic}", "Deine Reise mit {brand} beginnt!"],
                "en": ["Welcome to {brand}! {topic}", "Glad you're here — {topic}", "Your journey with {brand} starts now!"],
            },
            NewsletterType.REENGAGEMENT: {
                "de": ["Wir vermissen dich! {topic}", "Lange nicht gelesen? Das ist neu: {topic}", "Come back — wir haben etwas für dich!"],
                "en": ["We miss you! {topic}", "Haven't heard from you? Here's what's new: {topic}", "Come back — we saved something for you!"],
            },
            NewsletterType.CONTENT_DIGEST: {
                "de": ["Das Beste dieser Woche: {topic}", "Lese-Empfehlungen für dich — {topic}", "Dein Content-Check für KW {week}"],
                "en": ["The best of this week: {topic}", "Top reads curated for you — {topic}", "Your content digest — Week {week}"],
            },
        }
        candidates = subjects.get(spec.nl_type, subjects[NewsletterType.WEEKLY])
        lang_dict = candidates.get(spec.language, candidates["en"])
        template = random.choice(lang_dict)
        week = datetime.now().isocalendar()[1]
        return template.format(
            brand=spec.brand,
            topic=spec.topic,
            week=week,
            discount=spec.discount_percent,
            code=spec.discount_code or "SAVE20",
        )

    def _build_preview(self, spec: NewsletterSpec) -> str:
        previews = {
            "de": "Kurzer Überblick über {topic} — 2 Min Lesezeit.",
            "en": "Quick overview of {topic} — 2 min read.",
        }
        return previews.get(spec.language, previews["en"]).format(topic=spec.topic)

    def _build_sections(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        if spec.nl_type == NewsletterType.WEEKLY:
            return self._build_weekly(spec)
        elif spec.nl_type == NewsletterType.PRODUCT_LAUNCH:
            return self._build_product_launch(spec)
        elif spec.nl_type == NewsletterType.PROMO:
            return self._build_promo(spec)
        elif spec.nl_type == NewsletterType.WELCOME:
            return self._build_welcome(spec)
        elif spec.nl_type == NewsletterType.REENGAGEMENT:
            return self._build_reengage(spec)
        elif spec.nl_type == NewsletterType.CONTENT_DIGEST:
            return self._build_digest(spec)
        else:
            return self._build_weekly(spec)

    def _section(self, heading: str, content: str) -> Dict[str, str]:
        return {"heading": heading, "content": content}

    def _build_weekly(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        greeting = {"de": "Hey {name}!", "en": "Hey {name}!"}.get(spec.language, "Hey!")
        name = spec.subscriber_name or ({"de": "da", "en": "there"}.get(spec.language, "there"))
        sections = [
            self._section("Header", self._header_html(spec, greeting.format(name=name))),
            self._section("Intro", greeting.format(name=name) + f" Hier ist dein wöchentliches Update über {spec.topic}."),
            self._section("Highlights", self._build_highlights(spec)),
            self._section("Featured", self._build_featured_items(spec)),
            self._section("Tip of the Week", self._tip_of_week(spec)),
            self._section("CTA", self._cta_block(spec)),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_product_launch(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        launch_intros = {
            "de": f"Großartige Neuigkeiten! Wir haben {spec.topic} gelauncht — und wir sind sicher, es wird dir gefallen.",
            "en": f"Big news! We've launched {spec.topic} — and we think you're going to love it.",
        }
        sections = [
            self._section("Header", self._header_html(spec, "")),
            self._section("Launch Announcement", launch_intros.get(spec.language, launch_intros["en"])),
            self._section("What is it?", self._build_featured_items(spec)),
            self._section("Key Benefits", self._build_benefits_list(spec)),
            self._section("How to Get Started", f"1. Besuche {spec.website}\n2. Probiere es kostenlos\n3. Enjoy!"),
            self._section("Limited Launch Offer", self._launch_offer(spec)),
            self._section("CTA", self._cta_block(spec, cta_text=spec.cta_text or "Jetzt ausprobieren!")),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_promo(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        sections = [
            self._section("Header", self._header_html(spec, "🎉")),
            self._section("Offer", self._build_promo_offer(spec)),
            self._section("Why Act Now?", "• Exklusiv für dich\n• {days} Tage gültig\n• Kein Mindestbestellwert".format(days=7)),
            self._section("Featured Products", self._build_featured_items(spec)),
            self._section("CTA", self._cta_block(spec, cta_text=spec.cta_text or "Code einlösen!")),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_welcome(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        welcomes = {
            "de": f"Willkommen bei {spec.brand}! Wir freuen uns, dass du hier bist. {spec.topic}",
            "en": f"Welcome to {spec.brand}! We're thrilled you're here. {spec.topic}",
        }
        sections = [
            self._section("Header", self._header_html(spec, "👋")),
            self._section("Welcome", welcomes.get(spec.language, welcomes["en"])),
            self._section("What to Expect", "• Wöchentliche Updates\n• Exklusive Angebote\n• Tipps & Tricks"),
            self._section("Getting Started", self._build_featured_items(spec)),
            self._section("CTA", self._cta_block(spec, cta_text="Erste Schritte →")),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_reengage(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        sections = [
            self._section("Header", self._header_html(spec, "👀")),
            self._section("We Miss You", f"Es ist eine Weile her — aber wir haben {spec.topic} und dachten an dich."),
            self._section("What's New", self._build_featured_items(spec)),
            self._section("Special Comeback Offer", self._reengage_offer(spec)),
            self._section("CTA", self._cta_block(spec, cta_text="Zurückkehren →")),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_digest(self, spec: NewsletterSpec) -> List[Dict[str, str]]:
        sections = [
            self._section("Header", self._header_html(spec, "📚")),
            self._section("This Week's Top Picks", f"Die besten Links, Artikel und Ressourcen rund um {spec.topic}."),
            self._section("Curated Content", self._build_featured_items(spec)),
            self._section("Quick Reads", "• Artikel 1: 3 min\n• Artikel 2: 5 min\n• Artikel 3: 2 min"),
            self._section("CTA", self._cta_block(spec)),
            self._section("Footer", self._footer_html(spec)),
        ]
        return sections

    def _build_highlights(self, spec: NewsletterSpec) -> str:
        highlights = spec.featured_items or [
            "Feature A: Das ist neu diese Woche",
            "Feature B: Verbesserte Performance",
            "Feature C: Community Highlight",
        ]
        return "\n".join(f"✅ {h}" for h in highlights[:4])

    def _build_featured_items(self, spec: NewsletterSpec) -> str:
        items = spec.featured_items or ["Unser neuestes Feature ist jetzt live!", "Jetzt 20% sparen!", "Top Ressource: Der Guide für 2026."]
        return "\n\n".join(f"**{i+1}. {item}**" for i, item in enumerate(items[:4]))

    def _build_benefits_list(self, spec: NewsletterSpec) -> str:
        benefits = spec.featured_items or ["Schneller", "Einfacher", "Kosteneffizient"]
        return "\n".join(f"✨ {b}" for b in benefits[:4])

    def _tip_of_week(self, spec: NewsletterSpec) -> str:
        tips = {
            "de": "Pro-Tipp: Nutze Bullet Points in deinen E-Mails — die Öffnungsrate steigt nachweislich.",
            "en": "Pro tip: Use bullet points in your emails — open rates increase measurably.",
        }
        return tips.get(spec.language, tips["en"])

    def _default_cta(self, spec: NewsletterSpec) -> str:
        ctas = {
            "de": "Mehr erfahren →",
            "en": "Learn more →",
        }
        return spec.cta_text or ctas.get(spec.language, "Learn more →")

    def _cta_block(self, spec: NewsletterSpec, cta_text: str = "") -> str:
        text = cta_text or spec.cta_text or self._default_cta(spec)
        url = spec.cta_url or f"https://{spec.website}"
        return f"[{text}]({url})"

    def _launch_offer(self, spec: NewsletterSpec) -> str:
        if spec.discount_percent:
            return f"Exklusiv für Newsletter-Abonnenten: **{spec.discount_percent}% Rabatt** mit Code `{spec.discount_code or 'LAUNCH20'}`!"
        return f"Exklusiv für Newsletter-Abonnenten: **20% Rabatt** — code unten!"

    def _reengage_offer(self, spec: NewsletterSpec) -> str:
        return f"Willkommen zurück! Nutze Code **BACK10** für 10% Rabatt auf deine nächste Bestellung."

    def _build_promo_offer(self, spec: NewsletterSpec) -> str:
        if spec.discount_percent:
            return f"**{spec.discount_percent}% RABATT** auf {spec.topic}!\n\nGutscheincode: `{spec.discount_code or 'SAVE20'}`"
        return f"Spezialangebot für dich: **20% RABATT** auf {spec.topic}!"

    def _header_html(self, spec: NewsletterSpec, greeting: str = "") -> str:
        return f"**{spec.brand}** | {greeting}".strip()

    def _footer_html(self, spec: NewsletterSpec) -> str:
        unsub = {"de": "Abmelden", "en": "Unsubscribe"}.get(spec.language, "Unsubscribe")
        addr = {"de": "EmpireHazeClaw, Germany", "en": "EmpireHazeClaw, Germany"}.get(spec.language, "Germany")
        return f"---\n{addr}\n[{unsub}](https://{spec.website}/unsubscribe) | [Website](https://{spec.website})"

    def _estimate_open_rate(self, spec: NewsletterSpec, subject: str) -> float:
        rate = 0.25  # baseline
        if len(subject) <= 50:
            rate += 0.05
        if spec.nl_type == NewsletterType.PROMO:
            rate += 0.08
        if spec.nl_type == NewsletterType.WELCOME:
            rate += 0.10
        if spec.nl_type == NewsletterType.REENGAGEMENT:
            rate -= 0.05
        if spec.tone == Tone.EXCITED:
            rate += 0.03
        if "!" in subject or "🎉" in subject:
            rate += 0.05
        return min(rate, 0.55)

    def _save(self, result: NewsletterResult) -> None:
        self.cache.setdefault("newsletters", []).insert(0, result.__dict__)
        self.cache["newsletters"] = self.cache["newsletters"][:100]
        save_cache(self.cache)

    def list_newsletters(self) -> List[Dict[str, Any]]:
        return self.cache.get("newsletters", [])

    def export_as_text(self, result: NewsletterResult) -> str:
        lines = [
            f"{'='*60}",
            f"📧 NEWSLETTER",
            f"{'='*60}",
            f"SUBJECT: {result.subject}",
            f"PREVIEW: {result.preview_text}",
            f"Type: {result.spec.get('nl_type')} | Lang: {result.spec.get('language')} | {result.word_count} words",
            f"Est. Open Rate: {result.estimated_open_rate:.0%}",
            f"Generated: {result.generated_at[:16]}",
            f"{'='*60}",
            "",
        ]
        for sec in result.sections:
            if sec["heading"] not in ("Header", "Footer"):
                lines.append(f"[{sec['heading']}]")
                lines.append(sec["content"])
                lines.append("")
        lines.extend(["--", result.sections[-1]["content"]])
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="newsletter_writer_agent.py",
        description="📧 Newsletter Writer Agent — Email Newsletters (DE/EN)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Weekly newsletter
  python3 newsletter_writer_agent.py --topic "March Product Updates" --type weekly --lang en

  # Product launch
  python3 newsletter_writer_agent.py --topic "PromptCache Pro Launch" --type product --lang de --cta-url "https://empirehazeclaw.store"

  # Promotional
  python3 newsletter_writer_agent.py --topic "Spring Sale" --type promo --lang de --discount 20 --code SPRING20

  # Welcome series
  python3 newsletter_writer_agent.py --topic "Welcome to the Community" --type welcome --lang en

  # Re-engagement
  python3 newsletter_writer_agent.py --topic "We Have Something for You" --type reengage --lang en

  # List all
  python3 newsletter_writer_agent.py --list
        """
    )
    parser.add_argument("--topic", type=str, required=True, help="Newsletter topic/headline")
    parser.add_argument("--type", dest="nl_type", choices=[t.value for t in NewsletterType], default=NewsletterType.WEEKLY.value)
    parser.add_argument("--lang", choices=["de", "en"], default="de")
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.FRIENDLY.value)
    parser.add_argument("--name", dest="subscriber_name", type=str, default="", help="Subscriber name for personalization")
    parser.add_argument("--features", dest="featured_items", type=str, default="",
                        help="Comma-separated featured items/highlights")
    parser.add_argument("--cta-text", dest="cta_text", type=str, default="")
    parser.add_argument("--cta-url", dest="cta_url", type=str, default="")
    parser.add_argument("--discount", dest="discount_percent", type=int, default=0)
    parser.add_argument("--code", dest="discount_code", type=str, default="")
    parser.add_argument("--output", type=str, help="Save to file")
    parser.add_argument("--list", action="store_true", help="List all cached newsletters")
    return parser.parse_args()


def main() -> None:
    agent = NewsletterWriterAgent()
    args = parse_args()

    if args.list:
        newsletters = agent.list_newsletters()
        if not newsletters:
            print("No newsletters in cache.")
            return
        print(f"\n📧 Cached Newsletters ({len(newsletters)} total)\n")
        for n in newsletters:
            ts = n.get("generated_at", "")[:10]
            print(f"  [{ts}] {n.get('subject','?')} | {n.get('spec',{}).get('nl_type','?')} | Open: {n.get('estimated_open_rate',0):.0%}")
        return

    spec = NewsletterSpec(
        topic=args.topic,
        nl_type=NewsletterType(args.nl_type),
        language=args.lang,
        tone=Tone(args.tone),
        subscriber_name=args.subscriber_name,
        featured_items=[f.strip() for f in args.featured_items.split(",") if f.strip()],
        cta_text=args.cta_text,
        cta_url=args.cta_url,
        discount_percent=args.discount_percent,
        discount_code=args.discount_code,
    )

    result = agent.generate(spec)
    output = agent.export_as_text(result)
    print(output)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n💾 Saved to {args.output}")


if __name__ == "__main__":
    main()
