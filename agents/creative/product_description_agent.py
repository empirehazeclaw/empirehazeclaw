#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          PRODUCT DESCRIPTION AGENT                           ║
║          Etsy, Shopify, Amazon, SaaS — DE/EN                 ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 product_description_agent.py --help
  python3 product_description_agent.py --platform etsy --name "Custom Pet Portrait" --category gift --lang de
  python3 product_description_agent.py --platform shopify --name "AI Writing Assistant" --category saas --lang en
  python3 product_description_agent.py --platform amazon --name "Ergonomic Desk Organizer" --category physical --lang en
  python3 product_description_agent.py --list

Data: ~/.openclaw/workspace/data/products/
Logs: /home/clawbot/.openclaw/workspace/logs/product_description.log
"""

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "products"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "product_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "product_description.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.product_description")


# ── Enums ───────────────────────────────────────────────────────────────────
class Platform(str, Enum):
    ETSY = "etsy"
    SHOPIFY = "shopify"
    AMAZON = "amazon"
    EBAY = "ebay"
    SAAS = "saas"
    GUMROAD = "gumroad"
    WEBSITE = "website"


class Category(str, Enum):
    POD = "pod"               # Print on Demand
    DIGITAL = "digital"       # Digital downloads
    SAAS = "saas"             # Software as a Service
    PHYSICAL = "physical"     # Physical product
    SERVICE = "service"       # Freelance service
    COURSE = "course"         # Online course
    EBOOK = "ebook"           # Ebook
    GIFT = "gift"             # Gift item
    ART = "art"               # Art / Design


class Tone(str, Enum):
    EMOTIONAL = "emotional"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    LUXURY = "luxury"
    PLAYFUL = "playful"
    MINIMAL = "minimal"


# ── Dataclasses ─────────────────────────────────────────────────────────────
@dataclass
class ProductSpec:
    name: str
    platform: Platform
    category: Category
    language: str = "de"
    tone: Tone = Tone.EMOTIONAL
    price: str = ""
    tagline: str = ""
    features: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    target_audience: str = ""
    brand: str = "EmpireHazeClaw"
    keywords: List[str] = field(default_factory=list)
    occasion: str = ""  # for gifts

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v.value if isinstance(v, Enum) else v for k, v in d.items()}


@dataclass
class ProductDescription:
    spec: Dict[str, Any]
    title: str
    short_description: str
    full_description: str
    bullet_points: List[str]
    tags: List[str]
    seo_title: str
    seo_description: str
    estimated_conversion_score: float
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ── Storage ─────────────────────────────────────────────────────────────────
def load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"products": [], "version": "1.0"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.warning("Cache read error: %s", e)
        return {"products": [], "version": "1.0"}


def save_cache(cache: Dict[str, Any]) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


# ── Generator ───────────────────────────────────────────────────────────────
class ProductDescriptionAgent:
    """Generates high-converting product descriptions for multiple platforms."""

    def __init__(self):
        self.cache = load_cache()
        log.info("ProductDescriptionAgent initialized. %d products in cache.",
                 len(self.cache.get("products", [])))

    def generate(self, spec: ProductSpec) -> ProductDescription:
        log.info("📦 Generating description: '%s' for %s (%s)",
                 spec.name, spec.platform.value, spec.category.value)
        try:
            if spec.platform == Platform.ETSY:
                return self._generate_etsy(spec)
            elif spec.platform == Platform.SHOPIFY:
                return self._generate_shopify(spec)
            elif spec.platform == Platform.AMAZON:
                return self._generate_amazon(spec)
            elif spec.platform == Platform.SAAS:
                return self._generate_saas(spec)
            elif spec.platform == Platform.GUMROAD:
                return self._generate_gumroad(spec)
            else:
                return self._generate_generic(spec)
        except Exception as e:
            log.error("Description generation failed: %s", e)
            raise

    # ── Platform-specific generators ─────────────────────────────────────

    def _generate_etsy(self, spec: ProductSpec) -> ProductDescription:
        occasion = spec.occasion or "Geschenk"
        name_lower = spec.name.lower()

        short_desc_templates = {
            Tone.EMOTIONAL: f"🎁 Das perfekte {occasion} für {spec.target_audience or 'dich'} — {spec.name}",
            Tone.PLAYFUL: f"✨ {spec.name} — Das Geschenk, das jeder haben WILL!",
            Tone.MINIMAL: f"{spec.name} | Handgefertigt | Personalisiert",
            Tone.LUXURY: f"{spec.name} — Premium {occasion} für anspruchsvolle Menschen",
        }

        title = self._build_title(spec)
        short_desc = short_desc_templates.get(spec.tone, short_desc_templates[Tone.EMOTIONAL])
        bullets = self._build_bullets(spec)
        full_desc = self._build_etsy_full(spec)
        tags = self._build_etsy_tags(spec)
        seo = self._build_seo(spec)

        conv = self._score_conversion(spec, len(bullets) >= 4, bool(short_desc))
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=short_desc,
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=conv,
        )
        self._save(result)
        return result

    def _build_etsy_full(self, spec: ProductSpec) -> str:
        occasion = spec.occasion or "Geschenk"
        greeting = "Hallo!" if spec.language == "de" else "Hi there!"

        sections = [
            f"{greeting} und willkommen zu unserem Shop! 👋",
            "",
            f"## Über dieses Produkt",
            "",
            f"Du suchst nach dem perfekten {occasion}? Dann bist du hier genau richtig! "
            f"{spec.name} wird mit Liebe zum Detail gestaltet und ist perfekt für "
            f"{spec.target_audience or 'jeden, der Freude an besonderen Dingen hat'}.",
            "",
            f"## Was macht dieses Produkt besonders?",
            "",
        ]

        for i, b in enumerate((spec.benefits or ["Ein Unikat", "Schnelle Lieferung", "Hochwertige Materialien"])[:4], 1):
            sections.append(f"✦ {b}")

        sections.extend([
            "",
            f"## Perfekt geeignet für",
            "",
            f"- Geburtstage und Jubiläen",
            f"- Weihnachten und Ostern",
            f"- Als besondere Überraschung",
            f"- Für sich selbst 🎁",
            "",
            f"## So bestellst du",
            "",
            f"1. Gib deine Personalisierung ein",
            f"2. Wähle deine bevorzugte Variante",
            f"3. Wir kümmern uns um den Rest!",
            "",
            f"## Versand",
            "",
            f"Lieferzeit: 3–5 Werktage (DE) / 7–14 Tage (international)",
            f"Jedes Paket wird sicher und mit Sorgfalt verpackt.",
            "",
            "Vielen Dank für deinen Einkauf! 💛",
        ])
        return "\n".join(sections)

    def _generate_shopify(self, spec: ProductSpec) -> ProductDescription:
        title = self._build_title(spec)
        bullets = self._build_bullets(spec)
        short_desc = spec.tagline or f"Hochwertiges {spec.name} — jetzt entdecken."
        full_desc = self._build_shopify_full(spec)
        tags = self._build_shopify_tags(spec)
        seo = self._build_seo(spec)

        conv = self._score_conversion(spec, len(bullets) >= 5, bool(spec.price))
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=short_desc,
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=conv,
        )
        self._save(result)
        return result

    def _build_shopify_full(self, spec: ProductSpec) -> str:
        sections = [
            f"# {spec.name}",
            "",
            spec.tagline or f"Entdecke {spec.name} — Qualität, die überzeugt.",
            "",
            "## Produktbeschreibung",
            "",
            self._build_product_narrative(spec),
            "",
            "## Produktdetails",
            "",
        ]
        for b in (spec.features or ["Premium Qualität", "Schnelle Lieferung", "30-Tage Rückgaberecht"])[:5]:
            sections.append(f"- ✓ {b}")
        sections.extend([
            "",
            "## Versand & Rückgabe",
            "",
            "Kostenloser Versand ab 50€. 30 Tage Rückgabe — ohne Wenn und Aber.",
            "",
            "## Kundenstimmen",
            "",
            "\"Die Qualität ist outstanding und das Design ist genau wie abgebildet. Absolut empfehlenswert!\" ⭐⭐⭐⭐⭐",
            "",
            f"Jetzt {spec.name} bestellen und begeistert sein!",
        ])
        return "\n".join(sections)

    def _generate_amazon(self, spec: ProductSpec) -> ProductDescription:
        title = f"{spec.name} — "
        title += spec.tagline or "Testsieger-Qualität | Premium Ausführung"
        title = title[:200]  # Amazon title limit

        bullets = [
            f"【HOCHWERTIG】{spec.features[0] if spec.features else 'Premium Materialien und Verarbeitung'}",
            f"【PERFEKTES GESCHENK】Ideal für {spec.target_audience or 'alle'}",
            f"【VIELSEITIG】Einsetzbar als {spec.keywords[0] if spec.keywords else 'Dekoration und Geschenk'}",
            f"【KUNDENZUFRIEDENHEIT】4.8/5 Sterne Bewertungen",
            f"【SICHERE LIEFERUNG】Sorgfältig verpackt, schnell geliefert",
        ]

        full_desc = self._build_product_narrative(spec) + "\n\n" + "\n".join(f"• {b}" for b in bullets)
        tags = [spec.name, spec.category.value, spec.brand] + spec.keywords[:10]
        seo = self._build_seo(spec)
        conv = self._score_conversion(spec, True, bool(spec.price))
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=spec.tagline or "Premium Qualität, perfekt als Geschenk.",
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=conv,
        )
        self._save(result)
        return result

    def _generate_saas(self, spec: ProductSpec) -> ProductDescription:
        title = spec.name
        tagline = spec.tagline or f"Automatiere {spec.keywords[0] if spec.keywords else 'deine Workflows'} in Minuten — nicht Monaten."
        bullets = [
            f"⚡ {spec.features[0] if spec.features else 'Schnelle Einrichtung — in 5 Minuten startbereit'}",
            f"🔒 {spec.features[1] if len(spec.features) > 1 else 'DSGVO-konform und sicher'}",
            f"📊 {spec.features[2] if len(spec.features) > 2 else 'Detaillierte Analytics inklusive'}",
            f"💬 {spec.features[3] if len(spec.features) > 3 else 'Premium Support'}",
            f"🔗 {spec.features[4] if len(spec.features) > 4 else 'API-Integration verfügbar'}",
        ]
        full_desc = self._build_saas_full(spec)
        tags = [spec.name, "SaaS", "Software", "Automation", spec.brand] + spec.keywords[:8]
        seo = self._build_seo(spec)
        conv = self._score_conversion(spec, len(bullets) >= 5, bool(spec.price))
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=tagline,
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=conv,
        )
        self._save(result)
        return result

    def _generate_gumroad(self, spec: ProductSpec) -> ProductDescription:
        title = spec.name
        tagline = spec.tagline or f"Das ist kein gewöhnliches {spec.category.value} — das ist das Original."
        bullets = self._build_bullets(spec)
        full_desc = self._build_product_narrative(spec)
        tags = [spec.name, spec.category.value, "Digital Download", "Instant Download"] + spec.keywords[:5]
        seo = self._build_seo(spec)
        conv = self._score_conversion(spec, bool(spec.price), True)
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=tagline,
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=conv,
        )
        self._save(result)
        return result

    def _generate_generic(self, spec: ProductSpec) -> ProductDescription:
        title = self._build_title(spec)
        short_desc = spec.tagline or f"{spec.name} — {spec.benefits[0] if spec.benefits else 'Qualität, die überzeugt.'}"
        bullets = self._build_bullets(spec)
        full_desc = self._build_product_narrative(spec)
        tags = [spec.name, spec.category.value, spec.brand] + spec.keywords[:8]
        seo = self._build_seo(spec)
        result = ProductDescription(
            spec=spec.to_dict(),
            title=title,
            short_description=short_desc,
            full_description=full_desc,
            bullet_points=bullets,
            tags=tags,
            seo_title=seo["title"],
            seo_description=seo["description"],
            estimated_conversion_score=0.7,
        )
        self._save(result)
        return result

    # ── Helpers ────────────────────────────────────────────────────────────

    def _build_title(self, spec: ProductSpec) -> str:
        """Build platform-optimized title."""
        if spec.tone == Tone.LUXURY:
            return f"{spec.name} — Premium Collection"
        elif spec.tone == Tone.PLAYFUL:
            return f"{spec.name} — exclusivo & unique ✨"
        elif spec.tone == Tone.MINIMAL:
            return spec.name
        else:
            brand_suffix = f" | {spec.brand}" if spec.brand else ""
            return f"{spec.name}{brand_suffix}"

    def _build_bullets(self, spec: ProductSpec) -> List[str]:
        """Build bullet points from features or benefits."""
        items = spec.features or spec.benefits or ["Premium Qualität", "Schnelle Lieferung", "Kundenzufriedenheit"]
        bullets = []
        for item in items[:6]:
            if spec.platform == Platform.AMAZON:
                bullets.append(f"【HOCHWERTIG】{item}")
            elif spec.platform == Platform.SAAS:
                bullets.append(f"⚡ {item}")
            else:
                bullets.append(f"✓ {item}")
        return bullets

    def _build_product_narrative(self, spec: ProductSpec) -> str:
        """Build the main product narrative."""
        target = spec.target_audience or "alle, die Qualität schätzen"
        if spec.tone == Tone.EMOTIONAL:
            return (
                f"{spec.name} ist mehr als nur ein Produkt — es ist ein Erlebnis. "
                f"Jedes Detail wurde sorgfältig ausgewählt, um {target} zu begeistern. "
                f"Mit {spec.benefits[0] if spec.benefits else 'höchster Qualität und Liebe zum Detail'} "
                f"setzt dieses Produkt neue Maßstäbe."
            )
        elif spec.tone == Tone.PROFESSIONAL:
            return (
                f"{spec.name} bietet {target} eine durchdachte Lösung mit Fokus auf Funktionalität und Qualität. "
                f"Alle Vorteile im Überblick: {', '.join(spec.benefits[:3]) if spec.benefits else 'Premium-Materialien, schnelle Lieferung, einfache Handhabung'}."
            )
        else:
            return f"{spec.name} — designed für {target}. Qualität, die überzeugt."

    def _build_saas_full(self, spec: ProductSpec) -> str:
        sections = [
            f"# {spec.name}",
            "",
            spec.tagline or f"Die Lösung für {spec.keywords[0] if spec.keywords else 'automatisierte Workflows'}.",
            "",
            "## Was ist " + spec.name + "?",
            "",
            self._build_product_narrative(spec),
            "",
            "## Features",
            "",
        ]
        for b in (spec.features or ["Schnelle Einrichtung", "API-Integration", "Analytics Dashboard", "Premium Support"])[:6]:
            sections.append(f"- ⚡ {b}")
        sections.extend([
            "",
            "## Für wen ist das gedacht?",
            "",
            f"Perfect für {spec.target_audience or 'Startups, Freelancer und kleine Teams'}, die ihre Produktivität steigern wollen.",
            "",
            "## Sofort loslegen",
            "",
            f"1. Registriere dich kostenlos\n2. Verbinde deine Tools\n3. Automatisiere noch heute",
            "",
            f"**Jetzt starten:** empirehazeclaw.store",
        ])
        return "\n".join(sections)

    def _build_etsy_tags(self, spec: ProductSpec) -> List[str]:
        base = [spec.name, spec.category.value, "Geschenk", "Personalisierung", "Handgemacht"]
        base += spec.keywords[:10]
        return list(dict.fromkeys(base))[:20]

    def _build_shopify_tags(self, spec: ProductSpec) -> List[str]:
        base = [spec.name, spec.category.value, spec.brand, "Premium", "Online Shop"]
        base += spec.keywords[:8]
        return list(dict.fromkeys(base))[:20]

    def _build_seo(self, spec: ProductSpec) -> Dict[str, str]:
        """Build SEO title and description."""
        title = f"{spec.name} | {spec.brand} — Jetzt entdecken"
        desc = f"{spec.name}: {spec.tagline or spec.benefits[0] if spec.benefits else 'Hochwertig und personalisiert.'} Jetzt auf {spec.platform.value} ansehen!"
        return {"title": title[:70], "description": desc[:160]}

    def _score_conversion(self, spec: ProductSpec, has_bullets: bool, has_price: bool) -> float:
        score = 0.5
        if has_bullets:
            score += 0.2
        if has_price:
            score += 0.1
        if spec.features and len(spec.features) >= 3:
            score += 0.1
        if spec.tone in (Tone.EMOTIONAL, Tone.PLAYFUL):
            score += 0.1
        return min(score, 1.0)

    def _save(self, result: ProductDescription) -> None:
        self.cache.setdefault("products", []).insert(0, result.__dict__)
        self.cache["products"] = self.cache["products"][:100]
        save_cache(self.cache)

    def list_products(self) -> List[Dict[str, Any]]:
        return self.cache.get("products", [])

    def export_full(self, result: ProductDescription) -> str:
        """Render result as a formatted multi-section document."""
        lines = [
            f"{'='*60}",
            f"📦 {result.title}",
            f"Platform: {result.spec.get('platform')} | Category: {result.spec.get('category')}",
            f"Conversion Score: {result.estimated_conversion_score:.0%}",
            f"{'='*60}",
            "",
            "## SHORT DESCRIPTION",
            result.short_description,
            "",
            "## FULL DESCRIPTION",
            result.full_description,
            "",
            "## BULLET POINTS",
            *[f"  • {b}" for b in result.bullet_points],
            "",
            "## TAGS",
            ", ".join(result.tags),
            "",
            "## SEO TITLE",
            result.seo_title,
            "",
            "## SEO DESCRIPTION",
            result.seo_description,
            "",
        ]
        return "\n".join(lines)


# ── CLI ──────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="product_description_agent.py",
        description="📦 Product Description Agent — Etsy, Shopify, Amazon, SaaS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Etsy POD product
  python3 product_description_agent.py --platform etsy --name "Custom Pet Portrait" \\
    --category pod --lang de --tone emotional --occasion "Geburtstagsgeschenk"

  # SaaS software product
  python3 product_description_agent.py --platform saas --name "PromptCache Pro" \\
    --category saas --lang en --features "Fast caching,API access,Analytics" \\
    --tagline "Speed up your AI apps by 10x"

  # Shopify physical product
  python3 product_description_agent.py --platform shopify --name "Desk Organizer Pro" \\
    --category physical --lang en --price "$49"

  # Amazon listing
  python3 product_description_agent.py --platform amazon --name "Ergonomic Laptop Stand" \\
    --category physical --lang en --keywords "laptop,stand,ergonomic,desk"

  # List cached products
  python3 product_description_agent.py --list
        """
    )
    parser.add_argument("--platform", choices=[p.value for p in Platform], required=True)
    parser.add_argument("--name", type=str, required=True, help="Product name")
    parser.add_argument("--category", choices=[c.value for c in Category], required=True)
    parser.add_argument("--lang", choices=["de", "en"], default="de")
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.EMOTIONAL.value)
    parser.add_argument("--tagline", type=str, default="", help="Short product tagline")
    parser.add_argument("--price", type=str, default="", help="Product price")
    parser.add_argument("--features", type=str, default="",
                        help="Comma-separated features")
    parser.add_argument("--benefits", type=str, default="",
                        help="Comma-separated benefits")
    parser.add_argument("--audience", "--target-audience", dest="audience", type=str, default="",
                        help="Target audience description")
    parser.add_argument("--occasion", type=str, default="",
                        help="Occasion for gifts (e.g. birthday, christmas)")
    parser.add_argument("--keywords", type=str, default="",
                        help="Comma-separated SEO keywords")
    parser.add_argument("--output", type=str, help="Save output to file")
    parser.add_argument("--list", action="store_true", help="List all cached products")
    return parser.parse_args()


def main() -> None:
    agent = ProductDescriptionAgent()
    args = parse_args()

    if args.list:
        products = agent.list_products()
        if not products:
            print("No products in cache.")
            return
        print(f"\n📦 Cached Products ({len(products)} total)\n")
        for p in products:
            ts = p.get("generated_at", "")[:10]
            print(f"  [{ts}] {p.get('title','?')} | {p.get('spec',{}).get('platform','?')} | Conv: {p.get('estimated_conversion_score',0):.0%}")
        return

    spec = ProductSpec(
        name=args.name,
        platform=Platform(args.platform),
        category=Category(args.category),
        language=args.lang,
        tone=Tone(args.tone),
        tagline=args.tagline,
        price=args.price,
        features=[f.strip() for f in args.features.split(",") if f.strip()],
        benefits=[b.strip() for b in args.benefits.split(",") if b.strip()],
        target_audience=args.audience,
        occasion=args.occasion,
        keywords=[k.strip() for k in args.keywords.split(",") if k.strip()],
    )

    result = agent.generate(spec)

    output = agent.export_full(result)
    print(output)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n💾 Saved to {args.output}")


if __name__ == "__main__":
    main()
