#!/usr/bin/env python3
"""
Brand Designer Agent
EmpireHazeClaw Creative Suite

Creates brand identity specifications: colors, typography, voice, logos.
Ressourceneffizienz: generate specs instantly, no expensive agency needed.
Integrität: brand must reflect real values, no false positioning.
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "creative"
LOG_DIR = BASE_DIR / "logs"
BRANDS_FILE = DATA_DIR / "brands.json"

LOG_FILE = LOG_DIR / "brand_designer.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BrandDesigner")


def load_brands() -> dict:
    if BRANDS_FILE.exists():
        try:
            with open(BRANDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("Failed to load %s: %s", BRANDS_FILE, e)
    return {}


def save_brands(data: dict) -> bool:
    try:
        with open(BRANDS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        logger.error("Failed to save %s: %s", BRANDS_FILE, e)
        return False


# ─── Brand Generation ──────────────────────────────────────────────────────────
def generate_brand(
    name: str,
    tagline: str = "",
    industry: str = "technology",
    audience: str = "general",
    style: str = "modern",
    color_preference: str = "auto",
) -> dict:
    """Generate a complete brand identity specification."""
    logger.info("Generating brand for: %s", name)

    # Color palettes
    palettes = {
        "modern": {
            "primary": "#6366F1",  # Indigo
            "secondary": "#EC4899",  # Pink
            "accent": "#10B981",  # Emerald
            "dark": "#0F172A",  # Slate 900
            "light": "#F8FAFC",  # Slate 50
            "text": "#1E293B",  # Slate 800
            "muted": "#64748B",  # Slate 500
        },
        "minimal": {
            "primary": "#000000",
            "secondary": "#FFFFFF",
            "accent": "#FF4500",
            "dark": "#000000",
            "light": "#FAFAFA",
            "text": "#111111",
            "muted": "#888888",
        },
        "bold": {
            "primary": "#FF3D00",  # Deep orange
            "secondary": "#FFD600",  # Yellow
            "accent": "#00E676",  # Green
            "dark": "#1A1A1A",
            "light": "#FFFDE7",
            "text": "#212121",
            "muted": "#757575",
        },
        "elegant": {
            "primary": "#1A1A2E",  # Midnight
            "secondary": "#C9A84C",  # Gold
            "accent": "#E8D5B7",  # Cream
            "dark": "#0D0D1A",
            "light": "#F5F0E8",
            "text": "#2D2D2D",
            "muted": "#8B8B8B",
        },
        "playful": {
            "primary": "#7C3AED",  # Purple
            "secondary": "#F59E0B",  # Amber
            "accent": "#06B6D4",  # Cyan
            "dark": "#1E1B4B",
            "light": "#FFFBEB",
            "text": "#312E81",
            "muted": "#6B7280",
        },
        "tech": {
            "primary": "#0EA5E9",  # Sky blue
            "secondary": "#8B5CF6",  # Violet
            "accent": "#22D3EE",  # Light cyan
            "dark": "#0C0C1E",
            "light": "#F0F9FF",
            "text": "#0F172A",
            "muted": "#475569",
        },
    }

    # Typography
    font_stacks = {
        "modern": {
            "heading": "Inter, system-ui, -apple-system, sans-serif",
            "body": "Inter, system-ui, -apple-system, sans-serif",
            "mono": "JetBrains Mono, Fira Code, monospace",
            "display": "Inter, system-ui, sans-serif",
        },
        "minimal": {
            "heading": "Helvetica Neue, Helvetica, Arial, sans-serif",
            "body": "Helvetica Neue, Helvetica, Arial, sans-serif",
            "mono": "Courier New, monospace",
            "display": "Helvetica Neue, sans-serif",
        },
        "bold": {
            "heading": "Oswald, Impact, sans-serif",
            "body": "Open Sans, system-ui, sans-serif",
            "mono": "Space Mono, monospace",
            "display": "Oswald, sans-serif",
        },
        "elegant": {
            "heading": "Playfair Display, Georgia, serif",
            "body": "Source Sans Pro, system-ui, sans-serif",
            "mono": "Fira Code, monospace",
            "display": "Playfair Display, serif",
        },
        "playful": {
            "heading": "Nunito, system-ui, sans-serif",
            "body": "Nunito, system-ui, sans-serif",
            "mono": "Fira Code, monospace",
            "display": "Nunito, sans-serif",
        },
        "tech": {
            "heading": "Space Grotesk, system-ui, sans-serif",
            "body": "Space Grotesk, system-ui, sans-serif",
            "mono": "JetBrains Mono, Fira Code, monospace",
            "display": "Space Grotesk, sans-serif",
        },
    }

    # Voice & Tone
    voice_profiles = {
        "modern": {
            "personality": "Innovative, direct, trustworthy",
            "tone": {"formal": 70, "professional": 60, "casual": 40, "friendly": 50},
            "vocabulary": "technical, precise, outcome-focused",
            "example": "We build tools that actually work. No fluff, no shortcuts.",
        },
        "minimal": {
            "personality": "Clean, confident, understated",
            "tone": {"formal": 80, "professional": 70, "casual": 20, "friendly": 30},
            "vocabulary": "precise, minimal, no filler",
            "example": "Less. More.",
        },
        "bold": {
            "personality": "Fearless, disruptive, energetic",
            "tone": {"formal": 30, "professional": 50, "casual": 70, "friendly": 60},
            "vocabulary": "powerful, action-oriented, challenging",
            "example": "Stop settling. Start building. Make noise.",
        },
        "elegant": {
            "personality": "Sophisticated, refined, premium",
            "tone": {"formal": 90, "professional": 80, "casual": 10, "friendly": 20},
            "vocabulary": "elevated, articulate, discerning",
            "example": "Crafted for those who demand excellence.",
        },
        "playful": {
            "personality": "Fun, approachable, human",
            "tone": {"formal": 20, "professional": 40, "casual": 90, "friendly": 95},
            "vocabulary": "conversational, warm, accessible",
            "example": "Hey! We've been working on something pretty cool. Wanna see?",
        },
        "tech": {
            "personality": "Expert, forward-thinking, transparent",
            "tone": {"formal": 60, "professional": 80, "casual": 50, "friendly": 40},
            "vocabulary": "technical, precise, developer-friendly",
            "example": "Open source, transparent, built by engineers for engineers.",
        },
    }

    palette = palettes.get(style, palettes["modern"])
    fonts = font_stacks.get(style, font_stacks["modern"])
    voice = voice_profiles.get(style, voice_profiles["modern"])

    brand = {
        "id": str(uuid.uuid4()),
        "name": name,
        "tagline": tagline,
        "industry": industry,
        "audience": audience,
        "style": style,
        "colors": palette,
        "typography": fonts,
        "voice": voice,
        "logo_concept": generate_logo_concept(name, style),
        "guidelines": generate_guidelines(name, style, palette, fonts, voice),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    brands = load_brands()
    brands[brand["id"]] = brand
    save_brands(brands)
    logger.info("Brand created: %s (%s)", name, brand["id"])
    return brand


def generate_logo_concept(name: str, style: str) -> dict:
    concepts = {
        "modern": {
            "approach": "Geometric, clean, minimal shapes",
            "primary_mark": f"First letter '{name[0]}' in geometric sans-serif, bold weight",
            "symbol_ideas": ["Abstract shape combining first two letters", "Minimalist icon with gradient", "Single-weight stroke mark"],
            "usage": "Dark background with primary color, or full color on white",
        },
        "minimal": {
            "approach": "Pure minimalism — typography-forward",
            "primary_mark": f"Full wordmark in Helvetica Neue Bold, tight tracking",
            "symbol_ideas": ["Single dot or line element", "Negative space letterform", "No symbol — wordmark only"],
            "usage": "Black on white, monochrome — no exceptions",
        },
        "bold": {
            "approach": "Loud, unmissable, memorable",
            "primary_mark": f"'{name[0]}' in Impact-style condensed bold with slight rotation",
            "symbol_ideas": ["Stark contrast mark", "Geometric with sharp angles", "Dynamic, slightly asymmetrical"],
            "usage": "Primary color on black, high contrast required",
        },
        "elegant": {
            "approach": "Refined serif with gold or metallic accents",
            "primary_mark": f"Wordmark in Playfair Display italic + thin gold line",
            "symbol_ideas": ["Monogram of initials", "Crown or geometric art-deco motif", "Thin line emblem"],
            "usage": "Cream/light backgrounds, gold accent on dark",
        },
        "playful": {
            "approach": "Rounded, colorful, approachable",
            "primary_mark": f"'{name[0]}' in rounded Nunito, bright gradient",
            "symbol_ideas": ["Bouncy blob shape", "Confetti or dot pattern", "Animated-friendly design"],
            "usage": "Colorful, fun, works on colorful backgrounds",
        },
        "tech": {
            "approach": "Sharp, precise, developer-aesthetic",
            "primary_mark": f"'{name[:2]}' monogram or geometric icon in tech palette",
            "symbol_ideas": ["Circuit-like pattern", "Hexagonal grid", "Data visualization mark"],
            "usage": "Dark mode optimized, tech stack colors",
        },
    }
    return concepts.get(style, concepts["modern"])


def generate_guidelines(name: str, style: str, palette: dict, fonts: dict, voice: dict) -> dict:
    return {
        "logo_usage": [
            "Always maintain clear space equal to the height of the logomark around all sides",
            "Never stretch, skew, rotate, or modify the logo",
            f"Minimum size: 24px height for digital, 10mm for print",
            "Use dark logo on light backgrounds, light logo on dark",
        ],
        "color_usage": [
            f"Primary color ({palette['primary']}) — use for CTAs, headers, key UI",
            f"Secondary color ({palette['secondary']}) — accents, highlights",
            f"Accent color ({palette['accent']}) — sparingly, for emphasis",
            "Never use more than 3 colors in a single composition",
            "Ensure WCAG AA contrast for all text on backgrounds",
        ],
        "typography_usage": [
            f"Headings: {fonts['heading']}",
            f"Body: {fonts['body']}",
            f"Code/mono: {fonts['mono']}",
            "Line height: 1.4–1.6 for body, 1.1–1.3 for headings",
            "Avoid: Papyrus, Comic Sans, Times New Roman, Arial",
        ],
        "voice_principles": [
            f"Core personality: {voice['personality']}",
            f"Vocabulary: {voice['vocabulary']}",
            f"Tone shifts by context: customer service (friendly), technical docs (professional)",
            "Always: clear, honest, respectful",
            "Never: jargon without explanation, misleading claims, gate-keeping",
        ],
        "forbidden": [
            "Low-quality imagery or unedited stock photos",
            "Artificial urgency or false scarcity",
            "Competitor comparisons without evidence",
            "All caps for emphasis (except legal/technical)",
            "More than 3 fonts on any single piece",
        ],
    }


def list_brands() -> list[dict]:
    brands = load_brands()
    return sorted(brands.values(), key=lambda x: x.get("created_at", ""), reverse=True)


def get_brand(brand_id: str) -> dict:
    brands = load_brands()
    if brand_id not in brands:
        raise ValueError(f"Brand not found: {brand_id}")
    return brands[brand_id]


def export_brand(brand_id: str, output_path: Path = None) -> str:
    brand = get_brand(brand_id)
    path = output_path or Path(f"brand_{brand['name'].lower().replace(' ','_')}_guide.md")
    content = format_brand_guide(brand)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info("Brand guide exported: %s", path)
    return str(path)


def format_brand_guide(brand: dict) -> str:
    colors = brand["colors"]
    voice = brand["voice"]
    guidelines = brand["guidelines"]
    logo = brand["logo_concept"]

    lines = [
        f"# {brand['name']} — Brand Guide",
        f"**Tagline:** {brand.get('tagline', '—')}",
        f"**Style:** {brand['style'].capitalize()}",
        f"**Industry:** {brand['industry']}",
        f"**Audience:** {brand['audience']}",
        f"**Generated:** {brand['created_at'][:10]}",
        "",
        "---",
        "",
        "## 🎨 Color Palette",
        "",
        f"| Name | Hex | Use |",
        f"|---|---|---|",
        f"| Primary | `{colors['primary']}` | CTAs, headers |",
        f"| Secondary | `{colors['secondary']}` | Accents |",
        f"| Accent | `{colors['accent']}` | Highlights |",
        f"| Dark | `{colors['dark']}` | Text on light |",
        f"| Light | `{colors['light']}` | Backgrounds |",
        f"| Text | `{colors['text']}` | Body text |",
        f"| Muted | `{colors['muted']}` | Secondary text |",
        "",
        "---",
        "",
        "## ✏️ Typography",
        "",
        f"- **Heading:** {brand['typography']['heading']}",
        f"- **Body:** {brand['typography']['body']}",
        f"- **Mono/Code:** {brand['typography']['mono']}",
        "",
        "---",
        "",
        "## 🗣️ Voice & Tone",
        "",
        f"- **Personality:** {voice['personality']}",
        f"- **Vocabulary:** {voice['vocabulary']}",
        f"- **Example:** _{voice['example']}_",
        "",
        "### Tone Distribution",
        f"- Formal: {voice['tone']['formal']}%",
        f"- Professional: {voice['tone']['professional']}%",
        f"- Casual: {voice['tone']['casual']}%",
        f"- Friendly: {voice['tone']['friendly']}%",
        "",
        "---",
        "",
        "## 🏷️ Logo Concept",
        "",
        f"- **Approach:** {logo['approach']}",
        f"- **Primary Mark:** {logo['primary_mark']}",
        "",
        "**Symbol Ideas:**",
    ]
    for idea in logo.get("symbol_ideas", []):
        lines.append(f"- {idea}")
    lines.extend([f"", f"**Usage:** {logo['usage']}", ""])

    lines.extend([
        "---",
        "",
        "## 📋 Usage Guidelines",
        "",
        "### Logo Usage",
    ])
    for rule in guidelines["logo_usage"]:
        lines.append(f"- {rule}")

    lines.extend(["", "### Color Usage"])
    for rule in guidelines["color_usage"]:
        lines.append(f"- {rule}")

    lines.extend(["", "### Typography"])
    for rule in guidelines["typography_usage"]:
        lines.append(f"- {rule}")

    lines.extend(["", "### Voice Principles"])
    for rule in guidelines["voice_principles"]:
        lines.append(f"- {rule}")

    lines.extend(["", "### Forbidden"])
    for rule in guidelines["forbidden"]:
        lines.append(f"- ~~{rule}~~")

    lines.extend(["", "---", f"*Brand guide generated by EmpireHazeClaw Brand Designer | {brand['id']}*"])
    return "\n".join(lines)


# ─── CLI ───────────────────────────────────────────────────────────────────────
def cmd_create(args):
    brand = generate_brand(
        name=args.name,
        tagline=args.tagline or "",
        industry=args.industry or "technology",
        audience=args.audience or "general",
        style=args.style,
        color_preference=args.colors or "auto",
    )
    print(f"✅ Brand created: {brand['id']}")
    print(f"   {brand['name']} — {brand['style']} style")
    print(f"\nColor Palette:")
    for name, hex_val in brand["colors"].items():
        print(f"  {name:<10} {hex_val}")
    if args.output:
        path = export_brand(brand["id"], Path(args.output))
        print(f"\n📄 Brand guide exported to: {path}")


def cmd_list(args):
    brands = list_brands()
    if not brands:
        print("No brands found. Create one with: brand-designer create --name ...")
        return
    print(f"\n{'#':<4} {'Name':<30} {'Style':<12} {'Industry':<15} {'ID':<10}")
    print("-" * 80)
    for i, b in enumerate(brands, 1):
        print(f"{i:<4} {b.get('name',''):<30} {b.get('style',''):<12} {b.get('industry',''):<15} {b['id'][:10]}")
    print(f"\nTotal: {len(brands)} brand(s)")


def cmd_show(args):
    brand = get_brand(args.brand_id)
    print(format_brand_guide(brand))


def cmd_export(args):
    path = export_brand(args.brand_id, Path(args.output))
    print(f"✅ Brand guide exported: {path}")


def cmd_styles(args):
    print("\nAvailable Brand Styles:")
    styles = ["modern", "minimal", "bold", "elegant", "playful", "tech"]
    descs = [
        "Clean, contemporary, trustworthy",
        "Ultra-clean, typography-focused, restrained",
        "Loud, energetic, disruptive",
        "Refined, premium, sophisticated",
        "Fun, colorful, approachable",
        "Sharp, developer-friendly, precise",
    ]
    for s, d in zip(styles, descs):
        print(f"  {s:<12} — {d}")


def main():
    parser = argparse.ArgumentParser(
        prog="brand-designer",
        description="EmpireHazeClaw Brand Designer — generate brand identity specifications.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_create = sub.add_parser("create", help="Create a new brand identity")
    p_create.add_argument("--name", required=True, help="Brand name")
    p_create.add_argument("--tagline", help="Brand tagline")
    p_create.add_argument("--industry", default="technology", help="Industry")
    p_create.add_argument("--audience", default="general", help="Target audience")
    p_create.add_argument("--style", default="modern", choices=["modern", "minimal", "bold", "elegant", "playful", "tech"])
    p_create.add_argument("--colors", help="Color preference (future: specific palette)")
    p_create.add_argument("--output", help="Export brand guide to file")
    p_create.set_defaults(fn=cmd_create)

    p_list = sub.add_parser("list", help="List all brands")
    p_list.set_defaults(fn=cmd_list)

    p_show = sub.add_parser("show", help="Show full brand guide")
    p_show.add_argument("brand_id", help="Brand ID")
    p_show.set_defaults(fn=cmd_show)

    p_export = sub.add_parser("export", help="Export brand guide to file")
    p_export.add_argument("brand_id", help="Brand ID")
    p_export.add_argument("--output", default="brand_guide.md", help="Output file")
    p_export.set_defaults(fn=cmd_export)

    p_styles = sub.add_parser("styles", help="List available brand styles")
    p_styles.set_defaults(fn=cmd_styles)

    args = parser.parse_args()
    try:
        args.fn(args)
    except Exception as e:
        logger.error("%s", e)
        sys.stderr.write(f"❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
