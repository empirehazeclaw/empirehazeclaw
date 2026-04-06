#!/usr/bin/env python3
"""
✍️ Writing & Editing Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Full-featured writing and editing agent with:
- Multiple content types (blog, email, ad, landing page, social, SEO)
- 7 tones (professional, casual, witty, empathetic, authoritative, persuasive, neutral)
- SEO optimization
- Grammar & style checking
- CLI with full help

Usage:
  python3 writing/editing_agent.py --help
  python3 writing/editing_agent.py write --type blog --topic "AI in business" --tone professional
  python3 writing/editing_agent.py edit --file /path/to/text.md --level thorough
  python3 writing/editing_agent.py seo --topic "best CRM software" --count 5
  python3 writing/editing_agent.py rewrite --text "Your text here" --tone witty
  python3 writing/editing_agent.py headline --topic "Email marketing" --count 10
"""

import argparse
import json
import logging
import os
import re
import sys
import textwrap
from datetime import datetime
from difflib import unified_diff
from pathlib import Path
from typing import Dict, List, Optional

# ─── PATHS ────────────────────────────────────────────────────────────────────
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR  = WORKSPACE / "data"
LOGS_DIR  = WORKSPACE / "logs"
OUTPUT_DIR = DATA_DIR / "writing"

for d in [DATA_DIR, LOGS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WRITING_AGENT] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "writing_agent.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("writing_agent")

# ─── PROMPTS ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Du bist ein erstklassiger Texter und Lektor. Du schreibst und bearbeitest Texte
für ein E-Commerce- und SaaS-Unternehmen (EmpireHazeClaw). Deine Stärken:
- Fesselnd, verkaufsstark, SEO-optimiert
- Multilingual (DE + EN)
- 7 Töne: professional, casual, witty, empathetic, authoritative, persuasive, neutral
- Formate: Blog, Email, Ad, Landing Page, Social Post, Produktbeschreibung, SEO-Text

Regeln:
- Schreibe klare, handlungsrelevante Texte
- Vermeide Füllwörter und Buzzword-Bingo
- Strukturiere mit Überschriften, Listen, Call-to-Actions
- Optimiere für Lesbarkeit und Conversion"""

TONES = {
    "professional": "Formell, sachlich, kompetent. Geeignet für B2B und professionelle Kontexte.",
    "casual":      "Locker, freundlich, conversaciónsnah. Wie ein guter Freund der zufällig Experte ist.",
    "witty":       "Clever, humorvoll, mit überraschenden Pointen. Unterhaltung mit Tiefgang.",
    "empathetic":  "Warm, verständnisvoll, menschlich. Zeigt, dass du die Situation verstehst.",
    "authoritative":"Bestimmt, selbstbewusst, faktenbasiert. Deine Meinung zählt.",
    "persuasive":  "Überzeugend, verkaufsorientiert. Bewegt den Leser zum Handeln.",
    "neutral":     "Ausgewogen, sachlich, objektiv. Für informative und journalistische Texte.",
}

CONTENT_TYPES = ["blog", "email", "ad", "landing_page", "social", "product", "seo", "newsletter"]

SEO_HEADINGS = [
    "H1: {title} — Ultimate Guide {year}",
    "H2: Was ist {topic}?",
    "H2: {topic} vs. Alternatives",
    "H2: Vorteile von {topic}",
    "H2: Schritt-für-Schritt Anleitung",
    "H2: Häufige Fehler bei {topic}",
    "H2: {topic} für Anfänger",
    "H2: Fazit: Lohnt sich {topic}?",
]

# ─── UTILS ───────────────────────────────────────────────────────────────────
def call_llm(prompt: str, system: str = SYSTEM_PROMPT) -> str:
    """Call local LLM via OpenClaw tool or subprocess."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"LLM call failed: {e}, using fallback")
        return _fallback_write(prompt)


def _fallback_write(prompt: str) -> str:
    """Fallback when LLM is unavailable."""
    return f"[Draft generated without LLM]\n\nPrompt: {prompt[:200]}"


def grammar_check(text: str) -> Dict[str, List[str]]:
    """Simple rule-based grammar/style check."""
    issues = {"grammar": [], "style": [], "clarity": []}
    sentences = re.split(r"[.!?]+", text)
    for i, s in enumerate(sentences):
        s = s.strip()
        if not s:
            continue
        # Passive voice
        if re.search(r"\b(wird|werden|wurde|wurden|worden)\b", s) and re.search(r"\bvon\b", s):
            issues["style"].append(f"Satz {i+1}: Vermeide Passivkonstruktionen")
        # Sentence too long
        if len(s.split()) > 25:
            issues["clarity"].append(f"Satz {i+1}: Sehr lang ({len(s.split())} Wörter). Kürzer formulieren.")
        # Starts with conjunction
        if re.match(r"^(und|oder|aber|denn|weil|da|ja|doch|noch|nun|so|übrigens)\b", s.lower()):
            issues["style"].append(f"Satz {i+1}: Beginnt mit Konjunktion — überdenken.")
        # Double spaces
        if "  " in s:
            issues["grammar"].append(f"Satz {i+1}: Doppelte Leerzeichen gefunden")
        # Missing verb (heuristic)
        words = s.split()
        if len(words) > 3 and not any(w[0].isupper() or w in ["der", "die", "das", "ein", "eine", "und", "oder", "mit", "von", "auf", "in", "zu", "für", "als", "bei", "nach", "um", "an"] for w in words[:3]):
            pass  # too noisy
    return issues


def seo_score(text: str, topic: str) -> Dict[str, int]:
    """Calculate simple SEO score."""
    words = text.lower().split()
    word_count = len(words)
    char_count = len(text)
    topic_lower = topic.lower()
    topic_words = topic_lower.split()
    # Keyword density
    density = sum(1 for w in words if any(tw in w for tw in topic_words)) / max(word_count, 1) * 100
    # Word count score
    wc_score = min(100, word_count / 5)  # ~5 words per 1 point, capped at 100
    return {
        "word_count": word_count,
        "char_count": char_count,
        "keyword_density_pct": round(density, 2),
        "wc_score": round(wc_score),
        "overall_seo": round((min(density / 5, 100) + wc_score) / 2),
    }


def diff_text(original: str, edited: str) -> str:
    """Generate unified diff between original and edited."""
    orig_lines = original.splitlines(keepends=True)
    edit_lines = edited.splitlines(keepends=True)
    diff = unified_diff(orig_lines, edit_lines, fromfile="original", tofile="edited", lineterm="")
    return "".join(diff)


# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_write(args) -> int:
    """Write new content."""
    logger.info(f"Writing {args.type} content — topic: {args.topic}, tone: {args.tone}")

    if args.tone not in TONES:
        print(f"Error: Unknown tone '{args.tone}'. Available: {', '.join(TONES.keys())}")
        return 1

    topic = args.topic
    tone_desc = TONES[args.tone]
    content_type = args.type

    prompt_templates = {
        "blog": f"""Schreibe einen Blogartikel zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Länge: {args.length} Wörter
Format: Markdown mit H1, H2, Einleitung, Hauptteil, Fazit
SEO-optimiert mit dem Keyword: {topic}
Schreibe jetzt:""",
        "email": f"""Schreibe eine Verkaufs-E-Mail zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Betreffzeile + Preview-Text + E-Mail-Body
CTA am Ende
Schreibe jetzt:""",
        "ad": f"""Schreibe eine Anzeige zum Thema: {topic}
Tonalität: {tone_desc}
Plattform: {args.platform or 'universal'}
Sprache: {args.language}
Formate: Überschrift (max 30 Zeichen) + Beschreibung (max 90 Zeichen)
Schreibe jetzt:""",
        "landing_page": f"""Schreibe eine Landing-Page zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Sections: Hero, Problem, Lösung, Features, Testimonials, CTA, FAQ
CTA am Ende jeder Sektion
Schreibe jetzt:""",
        "social": f"""Schreibe einen Social-Media-Post zum Thema: {topic}
Tonalität: {tone_desc}
Plattform: {args.platform or 'Twitter/X'}
Sprache: {args.language}
Hashtags und Emojis einbauen
Schreibe jetzt:""",
        "product": f"""Schreibe eine Produktbeschreibung zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Features, Vorteile, Use-Cases, CTA
Schreibe jetzt:""",
        "seo": f"""Schreibe einen SEO-optimierten Artikel zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Länge: {args.length} Wörter
Keyword: {topic}
Inklusive Meta-Description, URL-Slug, und Artikelstruktur mit H1-H3
Schreibe jetzt:""",
        "newsletter": f"""Schreibe einen Newsletter zum Thema: {topic}
Tonalität: {tone_desc}
Sprache: {args.language}
Persönlicher Stil, Emoji-Nutzung, klarer CTA
Schreibe jetzt:""",
    }

    prompt = prompt_templates.get(content_type, prompt_templates["blog"])
    result = call_llm(prompt)

    # Save output
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = re.sub(r"[^\w]", "_", topic)[:40]
    out_file = OUTPUT_DIR / f"{content_type}_{safe_topic}_{ts}.md"
    out_file.write_text(f"# {topic}\n\n## Metadata\n- Type: {content_type}\n- Tone: {args.tone}\n- Language: {args.language}\n- Generated: {datetime.now().isoformat()}\n- Topic: {topic}\n\n---\n\n{result}")
    logger.info(f"Saved: {out_file}")
    print(f"\n✅ Content written to: {out_file}")
    print(f"\n{'='*60}")
    print(result)
    print(f"{'='*60}")

    # SEO analysis for blog/SEO types
    if content_type in ("blog", "seo"):
        score = seo_score(result, topic)
        print(f"\n📊 SEO Score: {score['overall_seo']}/100")
        print(f"   Words: {score['word_count']} | Density: {score['keyword_density_pct']}%")

    return 0


def cmd_edit(args) -> int:
    """Edit an existing text file."""
    logger.info(f"Editing file: {args.file}")

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}")
        return 1

    original = Path(args.file).read_text(encoding="utf-8")
    max_lines = args.max_lines or 500
    original_preview = "\n".join(original.splitlines()[:max_lines])

    level_desc = {
        "light": "Leichte Korrekturen: Grammatik, Tippfehler, Interpunktion",
        "standard": "Standard-Lektorat: + Stil, Satzfluss, Klarheit",
        "thorough": "Gründliches Editieren: + Struktur, Argumentation, Copy",
    }

    prompt = f"""{level_desc.get(args.level, level_desc['standard'])}

Originaltext:
---
{original_preview}
---

{args.instructions if args.instructions else 'Korrigiere und verbessere den Text nach dem angegebenen Level.'}

Gib das editierte Ergebnis aus. Formatiere als reines Markdown ohne Marker wie [EDITED] etc."""

    result = call_llm(prompt)
    issues = grammar_check(result)

    # Save edited version
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = Path(args.file).name
    out_file = OUTPUT_DIR / f"edited_{safe_name}_{ts}.md"
    out_file.write_text(f"# Editiert: {safe_name}\n\n**Original:** `{args.file}`\n**Level:** {args.level}\n**Datum:** {datetime.now().isoformat()}\n\n---\n\n{result}")
    logger.info(f"Edited version saved: {out_file}")

    print(f"\n✅ Edited version saved to: {out_file}")

    if args.diff:
        diff = diff_text(original[:2000], result[:2000])
        print(f"\n{'='*60}")
        print("DIFF (first 2000 chars):")
        print(diff or "(no visible changes in preview)")
        print(f"{'='*60}")

    if issues["grammar"] or issues["style"] or issues["clarity"]:
        print(f"\n🔍 Grammar/Style Report:")
        for cat, items in issues.items():
            if items:
                print(f"  [{cat.upper()}]")
                for item in items[:5]:
                    print(f"    - {item}")
    else:
        print(f"\n✅ No issues found in grammar check")

    return 0


def cmd_rewrite(args) -> int:
    """Rewrite text in a different tone."""
    logger.info(f"Rewriting text in tone: {args.tone}")
    if args.tone not in TONES:
        print(f"Error: Unknown tone '{args.tone}'. Available: {', '.join(TONES.keys())}")
        return 1

    prompt = f"""Übersetze den folgenden Text in einen anderen Ton.

Zielton: {args.tone}
Beschreibung: {TONES[args.tone]}

Originaltext:
---
{args.text}
---

Gib nur den umgeschriebenen Text aus, keine Erklärung:"""

    result = call_llm(prompt)
    print(f"\n{'='*60}")
    print(result)
    print(f"{'='*60}")

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"\n✅ Saved to: {args.output}")

    return 0


def cmd_seo(args) -> int:
    """Generate SEO keyword research and article outline."""
    logger.info(f"SEO research for: {args.topic}")

    prompt = f"""Erstelle eine SEO-Analyse für das Keyword/Thema: {args.topic}

1. Primäres Keyword + 5 verwandte Long-Tail-Keywords
2. Suchintention (informational/commercial/transactional)
3. Article Outline mit H1, H2, H3 (mindestens {args.count} Hauptpunkte)
4. Meta-Description (max 160 Zeichen)
5. Empfohlene Wortanzahl
6. 5 Fragen, die in FAQ beantwortet werden sollten

Format: Klares Markdown. Sei konkret und datenbasiert."""

    result = call_llm(prompt)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"seo_{re.sub(r'[^\w]', '_', args.topic)[:40]}_{ts}.md"
    out_file.write_text(f"# SEO Analyse: {args.topic}\n\n**Datum:** {datetime.now().isoformat()}\n\n---\n\n{result}")
    logger.info(f"SEO saved: {out_file}")

    print(f"\n✅ SEO Analyse gespeichert: {out_file}")
    print(f"\n{'='*60}")
    print(result)
    print(f"{'='*60}")
    return 0


def cmd_headline(args) -> int:
    """Generate headline options."""
    logger.info(f"Generating {args.count} headlines for: {args.topic}")

    prompt = f"""Generiere genau {args.count} Überschriften/Headlines zum Thema: {args.topic}

Anforderungen:
- Verschiedene Stile (Frage, Statement, Number, How-to)
- Max 60 Zeichen pro Headline
- Für Blog, Ad oder Email verwendbar
- Auf Deutsch

Liste nummeriert aus:"""

    result = call_llm(prompt)

    print(f"\n{'='*60}")
    print(result)
    print(f"{'='*60}")
    return 0


def cmd_grammar(args) -> int:
    """Check grammar of a text file or string."""
    text = ""
    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
            return 1
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        print("Error: Provide --file or --text")
        return 1

    issues = grammar_check(text)
    print(f"\n🔍 Grammar & Style Check")
    print(f"   Words: {len(text.split())} | Chars: {len(text)}")

    total = sum(len(v) for v in issues.values())
    if total == 0:
        print("   ✅ No issues found!")
    else:
        for cat, items in issues.items():
            if items:
                print(f"\n  [{cat.upper()}] — {len(items)} issue(s)")
                for item in items[:10]:
                    print(f"    • {item}")
        print(f"\n  Total: {total} issue(s) found")
    return 0


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="writing/editing_agent.py",
        description="✍️ Writing & Editing Agent — Full-featured content creation and editing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 writing/editing_agent.py write --type blog --topic "AI in business" --tone professional
  python3 writing/editing_agent.py write --type email --topic "Black Friday Sale" --tone persuasive
  python3 writing/editing_agent.py edit --file /tmp/draft.md --level thorough
  python3 writing/editing_agent.py rewrite --text "Ihr Text hier" --tone witty
  python3 writing/editing_agent.py seo --topic "best CRM software 2026" --count 8
  python3 writing/editing_agent.py headline --topic "Email marketing" --count 10
  python3 writing/editing_agent.py grammar --file /tmp/text.md
  python3 writing/editing_agent.py grammar --text "Ein Satz mit eine fehler."

Tones: professional, casual, witty, empathetic, authoritative, persuasive, neutral
Types: blog, email, ad, landing_page, social, product, seo, newsletter
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # write
    p_write = sub.add_parser("write", help="Write new content")
    p_write.add_argument("--type",   required=True, choices=CONTENT_TYPES, help="Content type")
    p_write.add_argument("--topic",  required=True, help="Topic/keyword")
    p_write.add_argument("--tone",   default="professional", help=f"Tone ({', '.join(TONES.keys())})")
    p_write.add_argument("--language", default="de", help="Language (de/en)")
    p_write.add_argument("--length", type=int, default=800, help="Target word count")
    p_write.add_argument("--platform", help="Platform (for ad/social)")

    # edit
    p_edit = sub.add_parser("edit", help="Edit existing text")
    p_edit.add_argument("--file",       required=True, help="File to edit")
    p_edit.add_argument("--level",      default="standard", choices=["light", "standard", "thorough"])
    p_edit.add_argument("--instructions", help="Custom editing instructions")
    p_edit.add_argument("--diff",       action="store_true", help="Show diff")
    p_edit.add_argument("--max-lines",  type=int, default=500, help="Max lines to process")

    # rewrite
    p_rw = sub.add_parser("rewrite", help="Rewrite text in different tone")
    p_rw.add_argument("--text",    required=True, help="Text to rewrite")
    p_rw.add_argument("--tone",    required=True, help=f"Tone ({', '.join(TONES.keys())})")
    p_rw.add_argument("--output",  help="Save to file")

    # seo
    p_seo = sub.add_parser("seo", help="SEO keyword research and article outline")
    p_seo.add_argument("--topic", required=True, help="Main keyword/topic")
    p_seo.add_argument("--count", type=int, default=5, help="Number of outline points")

    # headline
    p_hl = sub.add_parser("headline", help="Generate headline options")
    p_hl.add_argument("--topic", required=True)
    p_hl.add_argument("--count", type=int, default=10)

    # grammar
    p_gr = sub.add_parser("grammar", help="Check grammar and style")
    p_gr.add_argument("--file", help="File to check")
    p_gr.add_argument("--text",  help="Text to check")

    args = parser.parse_args()

    commands = {
        "write": cmd_write,
        "edit":  cmd_edit,
        "rewrite": cmd_rewrite,
        "seo":   cmd_seo,
        "headline": cmd_headline,
        "grammar": cmd_grammar,
    }

    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
