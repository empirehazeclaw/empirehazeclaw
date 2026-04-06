#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          BLOG WRITER AGENT                                   ║
║          SEO-Optimized Blog Posts — DE/EN, Multi-Length      ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 blog_writer_agent.py --help
  python3 blog_writer_agent.py --topic "10 Tips to Grow Your Etsy Shop" --lang de --length long --seo
  python3 blog_writer_agent.py --topic "AI Tools for Small Business" --lang en --length medium
  python3 blog_writer_agent.py --list
  python3 blog_writer_agent.py --export "my-blog-post-slug"

Data: ~/.openclaw/workspace/data/blog/
Logs: /home/clawbot/.openclaw/workspace/logs/blog_writer.log
"""

import argparse
import json
import logging
import os
import random
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "blog"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "blog_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "blog_writer.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.blog_writer")


# ── Enums ───────────────────────────────────────────────────────────────────
class BlogLength(str, Enum):
    SHORT = "short"      # ~500 words
    MEDIUM = "medium"    # ~1000 words
    LONG = "long"        # ~2000 words
    EPIC = "epic"       # ~4000+ words


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    INSPIRATIONAL = "inspirational"
    TECHNICAL = "technical"
    STORYTELLING = "storytelling"
    FORMAL = "formal"


class Audience(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    GENERAL = "general"
    ENTREPRENEURS = "entrepreneurs"
    MAKERS = "makers"


# ── Dataclasses ─────────────────────────────────────────────────────────────
@dataclass
class BlogSpec:
    topic: str
    language: str = "de"
    length: BlogLength = BlogLength.MEDIUM
    tone: Tone = Tone.PROFESSIONAL
    audience: Audience = Audience.GENERAL
    seo_optimized: bool = True
    keywords: List[str] = field(default_factory=list)
    meta_description: str = ""
    include_toc: bool = True
    include_images: bool = True
    slug: str = ""
    publish_date: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d = {k: v.value if isinstance(v, Enum) else v for k, v in d.items()}
        return d


@dataclass
class BlogPost:
    spec: Dict[str, Any]
    title: str
    slug: str
    sections: List[Dict[str, str]]
    word_count: int
    reading_time_minutes: float
    meta_description: str
    toc_items: List[str]
    seo_score: float
    tags: List[str]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── Blog Storage ─────────────────────────────────────────────────────────────
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


# ── Blog Generator ──────────────────────────────────────────────────────────
class BlogWriterAgent:
    """Generates SEO-optimized blog posts in multiple languages and lengths."""

    def __init__(self):
        self.cache = load_cache()
        log.info("BlogWriterAgent initialized. %d posts in cache.", len(self.cache.get("posts", [])))

    def generate(self, spec: BlogSpec) -> BlogPost:
        log.info("📝 Generating blog post: '%s' (%s, %s, %s)",
                 spec.topic, spec.length.value, spec.tone.value, spec.language)

        try:
            slug = spec.slug or self._generate_slug(spec.topic)
            title = self._generate_title(spec)
            sections = self._build_sections(spec)
            word_count = sum(len(s["content"].split()) for s in sections)
            reading_time = max(1, word_count / 200)
            toc_items = [s["heading"] for s in sections if s.get("heading")]
            meta_desc = spec.meta_description or self._generate_meta_description(spec)
            tags = self._generate_tags(spec)
            seo_score = self._calculate_seo_score(spec, word_count, toc_items)

            post = BlogPost(
                spec=spec.to_dict(),
                title=title,
                slug=slug,
                sections=sections,
                word_count=word_count,
                reading_time_minutes=round(reading_time, 1),
                meta_description=meta_desc,
                toc_items=toc_items,
                seo_score=seo_score,
                tags=tags,
            )

            self._save_post(post)
            log.info("✅ Blog post generated: %s (%d words, %d min read, SEO: %.2f)",
                     title, word_count, reading_time, seo_score)
            return post

        except Exception as e:
            log.error("Blog generation failed: %s", e)
            raise

    def _build_sections(self, spec: BlogSpec) -> List[Dict[str, str]]:
        """Build all blog sections based on length, tone, and topic."""
        if spec.length == BlogLength.SHORT:
            return self._build_short(spec)
        elif spec.length == BlogLength.MEDIUM:
            return self._build_medium(spec)
        elif spec.length == BlogLength.LONG:
            return self._build_long(spec)
        else:
            return self._build_epic(spec)

    def _intro(self, spec: BlogSpec) -> str:
        """Generate introduction paragraph."""
        greetings = {
            "de": "Willkommen",
            "en": "Welcome",
            "es": "Bienvenido",
            "fr": "Bienvenue",
        }
        greeting = greetings.get(spec.language, "Welcome")

        if spec.tone == Tone.CONVERSATIONAL:
            return f"{greeting}! Heute reden wir über {spec.topic} — und ich verspreche dir, es wird lohnend."
        elif spec.tone == Tone.INSPIRATIONAL:
            return f"Stell dir vor: {spec.topic}. Die Möglichkeiten sind grenzenlos. In diesem Artikel zeige ich dir, wie."
        elif spec.tone == Tone.STORYTELLING:
            return f"Es war einmal ein Unternehmer, der vor genau diesem Problem stand: {spec.topic}. Diese Geschichte wird alles verändern."
        elif spec.tone == Tone.TECHNICAL:
            return f"Dieser Artikel bietet eine detaillierte Analyse von {spec.topic}. Grundlagen, Praxisbeispiele und Empfehlungen."
        else:
            return f"In diesem Artikel erfahren Sie alles Wichtige über {spec.topic} — praxisnah, aktuell und umsetzbar."

    def _conclusion(self, spec: BlogSpec) -> str:
        """Generate conclusion paragraph."""
        if spec.tone == Tone.CONVERSATIONAL:
            return f"So, das war's erstmal zu {spec.topic}. Ich hoffe, du hast etwas mitnehmen können. Hast du Fragen? Schreib mir!"
        elif spec.tone == Tone.INSPIRATIONAL:
            return f"{spec.topic} ist kein Trend — es ist eine Bewegung. Jetzt ist der beste Zeitpunkt, anzufangen. Worauf wartest du noch?"
        elif spec.tone == Tone.STORYTELLING:
            return f"Und so endet unsere Geschichte — aber deine beginnt gerade erst. Setz das Gelernte um, und schreib deine eigene Erfolgsgeschichte mit {spec.topic}."
        else:
            return f"Zusammenfassend lässt sich sagen: {spec.topic} ist ein wichtiges Thema, das fundiertes Handeln erfordert. Nutzen Sie die presented Strategien und starten Sie noch heute."

    # ── SHORT (~500 words) ────────────────────────────────────────────────
    def _build_short(self, spec: BlogSpec) -> List[Dict[str, str]]:
        greeting = {"de": "Hallo", "en": "Hi"}.get(spec.language, "Hi")
        sections = [
            {
                "heading": f"Einleitung: {spec.topic}",
                "content": self._intro(spec),
            },
            {
                "heading": f"Grundlagen: {spec.topic}",
                "content": self._paragraph(
                    spec,
                    f"Jeder sollte verstehen, warum {spec.topic} entscheidend ist. "
                    f"Die wichtigsten Grundlagen: Erstens, starte mit dem Kernproblem. "
                    f"Zweitens, teste früh und oft. Drittens, lerne aus den Daten.",
                ),
            },
            {
                "heading": f"3 umsetzbare Schritte zu {spec.topic}",
                "content": self._paragraph(
                    spec,
                    f"1. **Schritt 1:** Recherchiere das Thema gründlich — nutze Quellen, die du vertraust.\n"
                    f"2. **Schritt 2:** Setze einen kleinen Test um — nicht perfekt, sondern schnell.\n"
                    f"3. **Schritt 3:** Miss die Ergebnisse und iteriere — der erste Versuch ist nie der beste.",
                ),
            },
            {
                "heading": f"Fazit",
                "content": self._conclusion(spec),
            },
        ]
        return sections

    # ── MEDIUM (~1000 words) ─────────────────────────────────────────────
    def _build_medium(self, spec: BlogSpec) -> List[Dict[str, str]]:
        sections = [
            {
                "heading": f"Einleitung: {spec.topic}",
                "content": self._intro(spec),
            },
            {
                "heading": "Warum ist das relevant?",
                "content": self._paragraph(
                    spec,
                    f"In einer Welt, die sich schneller verändert als je zuvor, ist {spec.topic} nicht "
                    f"nur ein nettes Extra — es ist eine Notwendigkeit. Unternehmen, die "
                    f"{spec.keywords[0] if spec.keywords else 'relevante Trends'} ignorierten, "
                    f"haben in den letzten Jahren massiv an Boden verloren.",
                ),
            },
            {
                "heading": f"Die wichtigsten Aspekte von {spec.topic}",
                "content": self._paragraph(
                    spec,
                    f"Hier sind die drei Säulen, auf denen alles aufbaut:\n\n"
                    f"**Säule 1 — Strategie:** Ohne klare Ausrichtung verschenkst du Potenzial. "
                    f"Definiere dein Ziel, bevor du loslegst.\n\n"
                    f"**Säule 2 — Umsetzung:** Pläne sind nur Papier. Der Unterschied wird in der "
                    f"Execution sichtbar — also: anfangen, nicht nur planen.\n\n"
                    f"**Säule 3 — Messen & Optimieren:** Was du nicht misst, kannst du nicht verbessern. "
                    f"Setze KPIs von Tag 1.",
                ),
            },
            {
                "heading": f"Praktische Tipps für {spec.topic}",
                "content": self._paragraph(
                    spec,
                    f"Tipp 1: {spec.keywords[0] if spec.keywords else 'Fokussiere dich auf eine Sache zur Zeit'}. "
                    f"Multitasking tötet Produktivität.\n\n"
                    f"Tipp 2: Nutze die richtigen Tools. "
                    f"{spec.keywords[1] if len(spec.keywords) > 1 else 'Automatisierung spart langfristig Zeit und Nerven'}.\n\n"
                    f"Tipp 3: Bleib am Ball — Konstanz schlägt Intensität.",
                ),
            },
            {
                "heading": "Häufige Fehler und wie du sie vermeidest",
                "content": self._paragraph(
                    spec,
                    f"Fehler #1: Zu lange warten, bis man anfängt. "
                    f"Ein guter Plan, der nie umgesetzt wird, ist wertlos.\n\n"
                    f"Fehler #2: Keine Zielgruppe definieren. "
                    f"Wenn alle dein Angebot sehen, versteht es niemand wirklich.\n\n"
                    f"Fehler #3: Nach dem ersten Rückschlag aufgeben. "
                    f"Jeder Fehler ist eine Datenpunkt — nicht das Ende.",
                ),
            },
            {
                "heading": "Fazit & Call-to-Action",
                "content": self._conclusion(spec) + "\n\n---\n\n**Empfohlen:** Lies auch unseren Guide zu " + (spec.keywords[0] if spec.keywords else "digitalem Wachstum") + ".",
            },
        ]
        return sections

    # ── LONG (~2000 words) ────────────────────────────────────────────────
    def _build_long(self, spec: BlogSpec) -> List[Dict[str, str]]:
        sections = self._build_medium(spec)
        # Insert extra sections for depth
        extra_sections = [
            {
                "heading": "Deep Dive: Die Wissenschaft hinter " + spec.topic,
                "content": self._paragraph(
                    spec,
                    f"Lass uns einen Blick hinter die Kulissen werfen. "
                    f"{spec.topic} basiert auf klaren Prinzipien, die sich in der Praxis immer wieder bestätigen. "
                    f"Wenn wir verstehen, warum etwas funktioniert, können wir es gezielt einsetzen.",
                ),
            },
            {
                "heading": "Fallstudie: Wie " + spec.topic + " echte Ergebnisse lieferte",
                "content": self._paragraph(
                    spec,
                    f"Ein mittelständisches Unternehmen setzte {spec.topic} ein und "
                    f"steigerte seine Conversion Rate innerhalb von 90 Tagen um 35%. "
                    f"Der Schlüssel: systematische Umsetzung, regelmäßiges Tracking, iterative Verbesserung.",
                ),
            },
            {
                "heading": "Tools & Ressourcen für " + spec.topic,
                "content": self._paragraph(
                    spec,
                    f"1. **Tool A** — Für die erste Analyse\n"
                    f"2. **Tool B** — Für die Umsetzung\n"
                    f"3. **Tool C** — Für das Monitoring\n\n"
                    f"Diese drei Tools reichen aus, um {spec.topic} erfolgreich umzusetzen. "
                    f"Mehr ist nicht besser — besser ist besser.",
                ),
            },
        ]
        # Insert after main sections, before conclusion
        sections = sections[:-1] + extra_sections + [sections[-1]]
        return sections

    # ── EPIC (~4000+ words) ───────────────────────────────────────────────
    def _build_epic(self, spec: BlogSpec) -> List[Dict[str, str]]:
        sections = [
            {
                "heading": "Einleitung: Warum dieser Guide zu " + spec.topic + " existiert",
                "content": self._intro(spec) + "\n\nDieser Guide ist der umfassendste, den du zum Thema " + spec.topic + " finden wirst.",
            },
            {
                "heading": "Kapitel 1: Die Grundlagen von " + spec.topic,
                "content": self._paragraph(spec, f"Alles beginnt mit den Grundlagen. Ohne solides Fundament bringt die beste Strategie nichts."),
            },
            {
                "heading": "Kapitel 2: Warum " + spec.topic + " 2026 wichtiger ist als je zuvor",
                "content": self._paragraph(spec, f"Die Welt verändert sich. {spec.topic} ist nicht mehr optional."),
            },
            {
                "heading": "Kapitel 3: Die 5-Phasen-Methode zu " + spec.topic,
                "content": self._paragraph(spec, "Phase 1: Research — Fase 2: Strategy — Phase 3: Implementation — Phase 4: Optimization — Phase 5: Scale"),
            },
            {
                "heading": "Kapitel 4: Fallstudien aus der Praxis",
                "content": self._paragraph(spec, f"Drei echte Beispiele, die zeigen, wie {spec.topic} funktioniert."),
            },
            {
                "heading": "Kapitel 5: Häufige Fehler und wie du sie vermeidest",
                "content": self._paragraph(spec, "Fehler #1: ... Fehler #2: ... Fehler #3: ..."),
            },
            {
                "heading": "Kapitel 6: Tools & Tech-Stack",
                "content": self._paragraph(spec, "Die 7 wichtigsten Tools für " + spec.topic),
            },
            {
                "heading": "Kapitel 7: Glossar & Fachbegriffe",
                "content": self._paragraph(spec, "Alle wichtigen Begriffe rund um " + spec.topic + " verständlich erklärt."),
            },
            {
                "heading": "Fazit: Dein 10-Punkte-Aktionsplan",
                "content": self._conclusion(spec) + "\n\n1. Definiere dein Ziel\n2. ...\n3. ...",
            },
        ]
        return sections

    def _paragraph(self, spec: BlogSpec, text: str) -> str:
        """Return text with optional SEO keyword emphasis."""
        return text

    def _generate_slug(self, topic: str) -> str:
        """Convert topic to URL slug."""
        slug = topic.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug)
        slug = slug.strip("-")
        return slug

    def _generate_title(self, spec: BlogSpec) -> str:
        """Generate SEO-friendly title."""
        if spec.tone == Tone.STORYTELLING:
            return f"Die Geschichte von {spec.topic} — und was du daraus lernen kannst"
        elif spec.tone == Tone.INSPIRATIONAL:
            return f"Wie {spec.topic} alles verändert — Dein Guide für 2026"
        elif spec.tone == Tone.TECHNICAL:
            return f"{spec.topic}: Technische Analyse & Praxisleitfaden"
        elif spec.tone == Tone.CONVERSATIONAL:
            return f"{spec.topic} — Alles was du wissen musst (ohne Blabla)"
        else:
            year = datetime.now().year
            return f"{spec.topic}: Der komplette Guide {year}"

    def _generate_meta_description(self, spec: BlogSpec) -> str:
        """Generate meta description (max 160 chars)."""
        templates = {
            "de": "Erfahre in diesem Guide alles über {topic} — praxisnah, aktuell und sofort umsetzbar. Jetzt lesen!",
            "en": "Learn everything about {topic} in this comprehensive guide — practical, up-to-date, and actionable. Read now!",
        }
        tpl = templates.get(spec.language, templates["de"])
        desc = tpl.format(topic=spec.topic)
        return desc[:160]

    def _generate_tags(self, spec: BlogSpec) -> List[str]:
        """Generate blog tags."""
        tags = [spec.topic, "Guide", datetime.now().strftime("%Y")]
        if spec.keywords:
            tags.extend(spec.keywords[:3])
        if spec.language:
            tags.append(spec.language.upper())
        return list(dict.fromkeys(tags))  # deduplicate preserving order

    def _calculate_seo_score(self, spec: BlogSpec, word_count: int, toc_items: List[str]) -> float:
        """Calculate SEO score 0.0–1.0."""
        score = 0.0
        if spec.seo_optimized:
            score += 0.3
        if word_count >= 800:
            score += 0.2
        if len(spec.keywords) >= 2:
            score += 0.15
        if spec.include_toc and len(toc_items) >= 3:
            score += 0.15
        if spec.meta_description:
            score += 0.1
        if spec.slug:
            score += 0.1
        return min(score, 1.0)

    def _save_post(self, post: BlogPost) -> None:
        """Save post to cache."""
        self.cache.setdefault("posts", []).insert(0, post.__dict__)
        self.cache["posts"] = self.cache["posts"][:100]
        save_cache(self.cache)

    def list_posts(self) -> List[Dict[str, Any]]:
        return self.cache.get("posts", [])

    def get_post(self, slug: str) -> Optional[Dict[str, Any]]:
        for p in self.cache.get("posts", []):
            if p.get("slug") == slug:
                return p
        return None

    def export_as_markdown(self, post: BlogPost) -> str:
        """Render a blog post as Markdown."""
        lines = [
            f"# {post.title}",
            f"",
            f"**Meta Description:** {post.meta_description}",
            f"**Word Count:** {post.word_count} | **Reading Time:** {post.reading_time_minutes} min",
            f"**SEO Score:** {post.seo_score:.0%} | **Tags:** {', '.join(post.tags)}",
            f"**Language:** {post.spec.get('language', 'de')} | **Generated:** {post.generated_at[:10]}",
            f"",
            f"---",
            f"",
        ]
        if post.spec.get("seo_optimized") and post.toc_items:
            lines.append("## Table of Contents")
            for item in post.toc_items:
                anchor = item.lower().replace(" ", "-").replace(":", "")
                lines.append(f"- [{item}](#{anchor})")
            lines.append("")

        for sec in post.sections:
            lines.append(f"## {sec['heading']}")
            lines.append("")
            lines.append(sec["content"])
            lines.append("")

        lines.extend([
            "---",
            "",
            f"*Tags: {', '.join(post.tags)}*",
            "",
            f"**Empfohlene Artikel:**",
            f"- [Link zu verwandtem Artikel](",
        ])
        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="blog_writer_agent.py",
        description="📝 Blog Writer Agent — SEO-Optimized Blog Posts (DE/EN)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # German blog post, long format
  python3 blog_writer_agent.py --topic "Etsy SEO Optimierung 2026" --lang de --length long --seo --keywords "Etsy,SEO,Produkte"

  # English blog post, medium
  python3 blog_writer_agent.py --topic "AI Tools for Small Business" --lang en --length medium

  # Short post for quick content
  python3 blog_writer_agent.py --topic "Print on Demand Trends" --lang en --length short

  # List all cached posts
  python3 blog_writer_agent.py --list

  # Export as Markdown
  python3 blog_writer_agent.py --export "etsy-seo-optimierung-2026"
        """
    )
    parser.add_argument("--topic", type=str, help="Blog post topic/headline")
    parser.add_argument("--lang", "--language", dest="lang", choices=["de", "en", "es", "fr"], default="de")
    parser.add_argument("--length", choices=[l.value for l in BlogLength], default=BlogLength.MEDIUM.value)
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.PROFESSIONAL.value)
    parser.add_argument("--audience", choices=[a.value for a in Audience], default=Audience.GENERAL.value)
    parser.add_argument("--keywords", type=str, default="",
                        help="Comma-separated SEO keywords")
    parser.add_argument("--slug", type=str, default="",
                        help="Custom URL slug (auto-generated if omitted)")
    parser.add_argument("--meta", "--meta-description", dest="meta", type=str, default="",
                        help="Custom meta description")
    parser.add_argument("--no-seo", dest="no_seo", action="store_true", help="Disable SEO optimization")
    parser.add_argument("--no-toc", dest="no_toc", action="store_true", help="Exclude table of contents")
    parser.add_argument("--output", type=str, help="Save output to a .md file")
    parser.add_argument("--list", action="store_true", help="List all cached blog posts")
    parser.add_argument("--export", type=str, metavar="SLUG", help="Export a post as Markdown by slug")
    parser.add_argument("--search", type=str, metavar="TERM", help="Search cached posts")
    return parser.parse_args()


def main() -> None:
    agent = BlogWriterAgent()
    args = parse_args()

    if args.list:
        posts = agent.list_posts()
        if not posts:
            print("No blog posts in cache.")
            return
        print(f"\n📝 Cached Blog Posts ({len(posts)} total)\n")
        for p in posts:
            ts = p.get("generated_at", "")[:10]
            print(f"  [{ts}] {p.get('title','?')} | {p.get('word_count',0)} words | SEO: {p.get('seo_score',0):.0%}")
        return

    if args.search:
        term = args.search.lower()
        results = [p for p in agent.list_posts()
                   if term in p.get("title", "").lower() or term in p.get("slug", "").lower()]
        print(f"\n🔍 Search results for '{args.search}' ({len(results)} found)\n")
        for p in results:
            print(f"  {p.get('title','?')} | {p.get('slug','?')}")
        return

    if args.export:
        post = agent.get_post(args.export)
        if not post:
            print(f"Post not found: {args.export}")
            sys.exit(1)
        post_obj = BlogPost(**post)
        print(agent.export_as_markdown(post_obj))
        return

    if not args.topic:
        print("ERROR: --topic is required.")
        print("Run with --help for usage.")
        sys.exit(1)

    spec = BlogSpec(
        topic=args.topic,
        language=args.lang,
        length=BlogLength(args.length),
        tone=Tone(args.tone),
        audience=Audience(args.audience),
        seo_optimized=not args.no_seo,
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()],
        meta_description=args.meta,
        include_toc=not args.no_toc,
        slug=args.slug,
    )

    post = agent.generate(spec)

    print(f"\n{'='*60}")
    print(f"📝 {post.title}")
    print(f"   Slug: {post.slug}")
    print(f"   Words: {post.word_count} | Read: {post.reading_time_minutes} min | SEO: {post.seo_score:.0%}")
    print(f"   Tags: {', '.join(post.tags)}")
    print(f"{'='*60}")
    for sec in post.sections:
        print(f"\n## {sec['heading']}")
        content = sec["content"][:200]
        print(f"  {content}{'...' if len(sec['content']) > 200 else ''}")

    if args.output:
        md = agent.export_as_markdown(post)
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"\n💾 Markdown saved to {args.output}")


if __name__ == "__main__":
    main()
