#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          AD COPY AGENT                                     ║
║          Google Ads, Facebook Ads, Display Ads — DE/EN     ║
╚══════════════════════════════════════════════════════════════╝

Usage:
  python3 ad_copy_agent.py --help
  python3 ad_copy_agent.py --type google --product "AI Chatbot SaaS" --lang en
  python3 ad_copy_agent.py --type facebook --product "Print on Demand Course" --lang de
  python3 ad_copy_agent.py --type google --product "Etsy SEO Tool" --lang de --count 5
  python3 ad_copy_agent.py --list

Data: ~/.openclaw/workspace/data/ads/
Logs: /home/clawbot/.openclaw/workspace/logs/ad_copy.log
"""

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
from typing import Any, Dict, List, Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "ads"
LOG_DIR = BASE_DIR / "logs"
CACHE_FILE = DATA_DIR / "ad_cache.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_DIR / "ad_copy.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("openclaw.ad_copy")


class AdType(str, Enum):
    GOOGLE_SEARCH = "google_search"      # Headlines + descriptions
    GOOGLE_DISPLAY = "google_display"   # Display banners
    FACEBOOK = "facebook"               # Facebook/Instagram ads
    LINKEDIN_SPONSORED = "linkedin"    # LinkedIn sponsored content
    RETARGETING = "retargeting"         # Retargeting ads
    LANDING_PAGE_HERO = "landing_hero"  # Hero section copy


class Tone(str, Enum):
    URGENT = "urgent"           # "Only 3 spots left!"
    EMOTIONAL = "emotional"    # Aspirational, feeling-driven
    LOGICAL = "logical"        # Facts, data, rational
    TRUST_BUILDER = "trust"    # Social proof, authority
    CURIOSITY = "curiosity"    # Open loops, intrigue


@dataclass
class AdSpec:
    ad_type: AdType
    product: str
    language: str = "de"
    tone: Tone = Tone.EMOTIONAL
    headline_variants: int = 3
    description_variants: int = 2
    brand: str = "EmpireHazeClaw"
    website: str = "empirehazeclaw.com"
    price: str = ""
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)
    benefit_1: str = ""
    benefit_2: str = ""
    benefit_3: str = ""
    audience_pain: str = ""
    cta_text: str = ""
    include_numbers: bool = True

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v.value if isinstance(v, Enum) else v for k, v in d.items()}


@dataclass
class AdVariant:
    """Single ad variant (one headline combo or one body copy)."""
    label: str
    ad_type: str
    headlines: List[str]
    descriptions: List[str]
    cta: str
    char_counts: Dict[str, int]
    quality_score_estimate: float


@dataclass
class AdResult:
    spec: Dict[str, Any]
    ad_type: str
    variants: List[Dict[str, Any]]
    product: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


def load_cache() -> Dict[str, Any]:
    if not CACHE_FILE.exists():
        return {"ads": [], "version": "1.0"}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log.warning("Cache read error: %s", e)
        return {"ads": [], "version": "1.0"}


def save_cache(cache: Dict[str, Any]) -> None:
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


class AdCopyAgent:
    """Generates ad copy for Google, Facebook, LinkedIn, and display campaigns."""

    # Google Ads character limits
    HEADLINE_MAX = 30
    DESC_MAX = 90
    PATH_MAX = 15

    # Facebook/LinkedIn
    FB_HEADLINE_MAX = 40
    FB_BODY_MAX = 125

    def __init__(self):
        self.cache = load_cache()
        log.info("AdCopyAgent initialized. %d ad sets in cache.", len(self.cache.get("ads", [])))

    def generate(self, spec: AdSpec) -> AdResult:
        log.info("📢 Generating ad copy: '%s' (%s, %s)", spec.product, spec.ad_type.value, spec.tone.value)
        try:
            if spec.ad_type == AdType.GOOGLE_SEARCH:
                variants = self._google_search(spec)
            elif spec.ad_type == AdType.GOOGLE_DISPLAY:
                variants = self._google_display(spec)
            elif spec.ad_type == AdType.FACEBOOK:
                variants = self._facebook(spec)
            elif spec.ad_type == AdType.LINKEDIN_SPONSORED:
                variants = self._linkedin(spec)
            elif spec.ad_type == AdType.RETARGETING:
                variants = self._retargeting(spec)
            elif spec.ad_type == AdType.LANDING_PAGE_HERO:
                variants = self._landing_hero(spec)
            else:
                variants = self._google_search(spec)

            result = AdResult(
                spec=spec.to_dict(),
                ad_type=spec.ad_type.value,
                variants=variants,
                product=spec.product,
            )
            self._save(result)
            log.info("✅ Generated %d ad variants for %s", len(variants), spec.product)
            return result
        except Exception as e:
            log.error("Ad generation failed: %s", e)
            raise

    # ── Google Search Ads ────────────────────────────────────────────────

    def _google_search(self, spec: AdSpec) -> List[Dict[str, Any]]:
        variants = []

        # Variant 1: Benefit-led
        headlines_1 = self._headlines(spec, variant=1)
        descs_1 = self._descriptions(spec, variant=1)
        variants.append({
            "label": "Benefit-Led",
            "headlines": headlines_1, "descriptions": descs_1,
            "paths": self._path_options(spec),
            "quality": self._estimate_quality(headlines_1, descs_1, spec),
        })

        # Variant 2: Urgency-led
        headlines_2 = self._headlines(spec, variant=2)
        descs_2 = self._descriptions(spec, variant=2)
        variants.append({
            "label": "Urgency",
            "headlines": headlines_2, "descriptions": descs_2,
            "paths": self._path_options(spec),
            "quality": self._estimate_quality(headlines_2, descs_2, spec),
        })

        # Variant 3: Question-led
        headlines_3 = self._headlines(spec, variant=3)
        descs_3 = self._descriptions(spec, variant=3)
        variants.append({
            "label": "Question",
            "headlines": headlines_3, "descriptions": descs_3,
            "paths": self._path_options(spec),
            "quality": self._estimate_quality(headlines_3, descs_3, spec),
        })

        return variants

    def _headlines(self, spec: AdSpec, variant: int = 1) -> List[Dict[str, Any]]:
        prod = spec.product
        kw = spec.primary_keyword or prod
        benefit = spec.benefit_1 or "Schnelle Ergebnisse"

        if variant == 1:
            # Benefit-led
            h1 = self._truncate(f"{prod} — {benefit}", self.HEADLINE_MAX)
            h2 = self._truncate(f"Jetzt {kw} testen", self.HEADLINE_MAX)
            h3 = self._truncate(f"Kein Risiko | 30 Tage", self.HEADLINE_MAX)
        elif variant == 2:
            # Urgency
            h1 = self._truncate(f"Nur noch 3 Tage: {kw}", self.HEADLINE_MAX)
            h2 = self._truncate(f"Spare jetzt 20% auf {prod}", self.HEADLINE_MAX)
            h3 = self._truncate(f"{spec.brand} — offiziell", self.HEADLINE_MAX)
        else:
            # Question
            h1 = self._truncate(f"Was ist das beste {kw}?", self.HEADLINE_MAX)
            h2 = self._truncate(f"{prod} — finde es heraus", self.HEADLINE_MAX)
            h3 = self._truncate(f"★★★★★ {spec.brand}", self.HEADLINE_MAX)

        return [
            {"text": h1, "chars": len(h1)},
            {"text": h2, "chars": len(h2)},
            {"text": h3, "chars": len(h3)},
        ]

    def _descriptions(self, spec: AdSpec, variant: int = 1) -> List[Dict[str, Any]]:
        prod = spec.product
        kw = spec.primary_keyword or prod
        benefit = spec.benefit_1 or "besser als je zuvor"
        pain = spec.audience_pain or "Zeit und Geld sparen"

        if variant == 1:
            d1 = self._truncate(
                f"Teste {prod} noch heute und erlebe {benefit}. "
                f"Die Lösung für alle, die {pain} wollen.",
                self.DESC_MAX
            )
            d2 = self._truncate(
                f"Empfohlen von 1.000+ Nutzern. Starte jetzt!",
                self.DESC_MAX
            )
        elif variant == 2:
            d1 = self._truncate(
                f"20% Rabatt nur diese Woche auf {prod}. "
                f"Angebot endet bald — nicht verpassen!",
                self.DESC_MAX
            )
            d2 = self._truncate(
                f"✓ Keine Kreditkarte nötig ✓ Sofort starten",
                self.DESC_MAX
            )
        else:
            d1 = self._truncate(
                f"Du fragst dich, welches {kw} das beste ist? "
                f"Wir haben die Antwort — und sie überrascht.",
                self.DESC_MAX
            )
            d2 = self._truncate(
                f"Mehr erfahren auf {spec.website}",
                self.DESC_MAX
            )

        return [
            {"text": d1, "chars": len(d1)},
            {"text": d2, "chars": len(d2)},
        ]

    def _path_options(self, spec: AdSpec) -> List[str]:
        kw = (spec.primary_keyword or spec.product).replace(" ", "-")[:self.PATH_MAX]
        brand = spec.brand.replace(" ", "")[:self.PATH_MAX]
        return [kw, brand]

    # ── Google Display Ads ────────────────────────────────────────────────

    def _google_display(self, spec: AdSpec) -> List[Dict[str, Any]]:
        short_headlines = [
            f"Jetzt {spec.product} entdecken",
            f"{spec.product} — besser als je zuvor",
            f"20% Rabatt auf {spec.product}",
            f"Die Lösung: {spec.product}",
            f"{spec.brand} empfohlen",
        ]
        body_options = [
            f"Entdecke {spec.product} und erlebe den Unterschied. Jetzt testen!",
            f"Schneller, einfacher, besser — {spec.product} macht den Unterschied.",
            f"1.000+ Nutzer vertrauen bereits auf {spec.product}. Jetzt du auch!",
        ]

        variants = []
        for i in range(min(3, spec.headline_variants)):
            headline = short_headlines[i % len(short_headlines)]
            body = body_options[i % len(body_options)]
            variants.append({
                "label": f"Display Variant {i+1}",
                "headlines": [{"text": headline, "chars": len(headline)}],
                "descriptions": [{"text": body, "chars": len(body)}],
                "image_suggestions": [
                    f"Clean product mockup with text overlay: '{headline}'",
                    f"Lifestyle image related to {spec.product}",
                    f"Bold typography banner with CTA",
                ],
                "quality": 0.75 + i * 0.05,
            })
        return variants

    # ── Facebook Ads ──────────────────────────────────────────────────────

    def _facebook(self, spec: AdSpec) -> List[Dict[str, Any]]:
        primary_cta = spec.cta_text or "Mehr erfahren"
        website_url = f"https://{spec.website}"

        variants = []

        # Emotional / aspiration
        variants.append({
            "label": "Emotional",
            "headline": self._truncate(
                f"Stell dir vor: {spec.product} macht {spec.benefit_1 or 'dein Leben einfacher'}",
                self.FB_HEADLINE_MAX
            ),
            "body": self._truncate(
                f"Mit {spec.product} erreichst du endlich {spec.benefit_2 or 'deine Ziele schneller'}. "
                f"Kein Stress, keine Ausreden — nur Ergebnisse.\n\n"
                f"► Teste es jetzt kostenlos\n► Keine Kreditkarte nötig",
                self.FB_BODY_MAX * 2  # longer for FB
            ),
            "cta": primary_cta,
            "website_url": website_url,
            "quality": 0.8,
        })

        # Social proof
        variants.append({
            "label": "Social Proof",
            "headline": self._truncate(
                f"1.000+ Nutzer haben bereits {spec.product} getestet",
                self.FB_HEADLINE_MAX
            ),
            "body": self._truncate(
                f"Was sie gemeinsam haben: Sie sparen jetzt {spec.benefit_1 or 'Zeit und Geld'}.\n\n"
                f"▸ 94% Weiterempfehlungsrate\n▸ 4.8/5 Sterne Bewertung\n▸ Sofort einsatzbereit\n\n"
                f"Jetzt testen und selbst überzeugen →",
                self.FB_BODY_MAX * 2
            ),
            "cta": primary_cta,
            "website_url": website_url,
            "quality": 0.85,
        })

        # Urgency
        if spec.include_numbers:
            variants.append({
                "label": "Urgency",
                "headline": self._truncate(
                    f"Angebot endet in 48 Stunden: 20% auf {spec.product}",
                    self.FB_HEADLINE_MAX
                ),
                "body": self._truncate(
                    f"⚠️ Nicht verpassen: 20% Rabatt auf {spec.product} — nur noch kurz.\n\n"
                    f"► Code: SAVE20\n► Gültig bis [Datum]\n► Sofort gültig nach Anmeldung",
                    self.FB_BODY_MAX * 2
                ),
                "cta": "Jetzt Rabatt sichern!",
                "website_url": website_url,
                "quality": 0.78,
            })

        return variants

    # ── LinkedIn Sponsored ─────────────────────────────────────────────────

    def _linkedin(self, spec: AdSpec) -> List[Dict[str, Any]]:
        primary_cta = spec.cta_text or "Mehr erfahren"
        website_url = f"https://{spec.website}"

        variants = [
            {
                "label": "Professional Authority",
                "headline": self._truncate(
                    f"Die smartere Lösung für {spec.primary_keyword or spec.product}",
                    self.FB_HEADLINE_MAX
                ),
                "body": self._truncate(
                    f"Führende Unternehmen setzen bereits auf {spec.product} — "
                    f"und das aus gutem Grund.\n\n"
                    f"✓ Steigere die Produktivität um bis zu 40%\n"
                    f"✓ Integration in bestehende Workflows\n"
                    f"✓ Enterprise-ready & DSGVO-konform",
                    self.FB_BODY_MAX * 2
                ),
                "cta": primary_cta,
                "website_url": website_url,
                "quality": 0.82,
            },
            {
                "label": "B2B Problem-Solution",
                "headline": self._truncate(
                    f"Dein Team verliert Zeit an {spec.primary_keyword or 'manuellen Tasks'}?",
                    self.FB_HEADLINE_MAX
                ),
                "body": self._truncate(
                    f"Die Lösung: {spec.product}.\n\n"
                    f"Reduziere manuellem Aufwand um 60% — "
                    f"und gib deinem Team die Zeit zurück für das, was wirklich zählt.\n\n"
                    f"► Demo anfordern",
                    self.FB_BODY_MAX * 2
                ),
                "cta": "Demo anfordern",
                "website_url": website_url,
                "quality": 0.8,
            },
        ]
        return variants

    # ── Retargeting ────────────────────────────────────────────────────────

    def _retargeting(self, spec: AdSpec) -> List[Dict[str, Any]]:
        variants = [
            {
                "label": "Comeback — Reminder",
                "headline": f"Du hast {spec.product} fast entdeckt 👀",
                "body": (
                    f"Hey, wir haben gesehen, dass du dich für {spec.product} interessiert hast.\n\n"
                    f"Gute Neuigkeiten: Wir haben gerade ein Special — 15% Rabatt nur für dich!\n\n"
                    f"Angebot läuft in 24h ab."
                ),
                "cta": "Angebot einlösen →",
                "quality": 0.88,
            },
            {
                "label": "Social Proof Retargeting",
                "headline": f"1.000+ nutzen bereits {spec.product}",
                "body": (
                    f"Nicht überzeugt? Das sagen unsere Kunden:\n\n"
                    f"\"{spec.benefit_1 or 'Game changer für mein Business'}\" ⭐⭐⭐⭐⭐\n\n"
                    f"Sei der/die Nächste — starte noch heute."
                ),
                "cta": "Jetzt starten →",
                "quality": 0.85,
            },
        ]
        return variants

    # ── Landing Page Hero ─────────────────────────────────────────────────

    def _landing_hero(self, spec: AdSpec) -> List[Dict[str, Any]]:
        variants = [
            {
                "label": "Benefit Hero",
                "headline": self._hero_headline(spec, style="benefit"),
                "subheadline": f"Erlebe {spec.benefit_1 or 'den Unterschied'}, "
                               f"den {spec.benefit_2 or 'andere Produkte nicht bieten'}. "
                               f"Für alle, die {spec.audience_pain or 'mehr aus ihrer Zeit machen wollen'}.",
                "cta_primary": spec.cta_text or "Kostenlos testen",
                "cta_secondary": "Mehr erfahren",
                "social_proof": f"✓ 1.000+ aktive Nutzer  ✓ 4.8/5 Sterne  ✓ DSGVO-konform",
                "quality": 0.87,
            },
            {
                "label": "Question Hero",
                "headline": self._hero_headline(spec, style="question"),
                "subheadline": f"Was wäre, wenn du {spec.benefit_1 or 'doppelt so produktiv'} sein könntest? "
                               f"{spec.product} macht es möglich.",
                "cta_primary": "Ja, ich will starten",
                "cta_secondary": "Mehr erfahren",
                "social_proof": "✓ Kostenloser Start  ✓ Keine Kreditkarte  ✓ 30 Tage teste",
                "quality": 0.84,
            },
        ]
        return variants

    def _hero_headline(self, spec: AdSpec, style: str = "benefit") -> str:
        if style == "benefit":
            return f"{spec.product}: {spec.benefit_1 or 'Besser, schneller, smarter'}"
        elif style == "question":
            return f"Isn't it time for a better {spec.product}?"
        else:
            return spec.product

    # ── Utilities ─────────────────────────────────────────────────────────

    def _truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars - 3].rstrip() + "..."

    def _estimate_quality(self, headlines: List[Dict], descriptions: List[Dict], spec: AdSpec) -> float:
        score = 0.6
        # All headlines within limit
        if all(h["chars"] <= self.HEADLINE_MAX for h in headlines):
            score += 0.1
        # Primary keyword in headline
        kw = (spec.primary_keyword or spec.product).lower()
        if any(kw in h["text"].lower() for h in headlines):
            score += 0.1
        # CTA in description
        if any(len(d["text"]) <= self.DESC_MAX for d in descriptions):
            score += 0.1
        # Numbers included
        if spec.include_numbers:
            score += 0.05
        return min(score, 0.95)

    def _save(self, result: AdResult) -> None:
        self.cache.setdefault("ads", []).insert(0, result.__dict__)
        self.cache["ads"] = self.cache["ads"][:100]
        save_cache(self.cache)

    def list_ads(self) -> List[Dict[str, Any]]:
        return self.cache.get("ads", [])

    def export_ads(self, result: AdResult) -> str:
        lines = [
            f"{'='*60}",
            f"📢 AD COPY — {result.ad_type.upper()} | {result.product}",
            f"{'='*60}",
            f"Generated: {result.generated_at[:16]}",
            "",
        ]
        for var in result.variants:
            label = var.get("label", "Variant")
            quality = var.get("quality", 0)
            lines.append(f"─── {label} (Quality: {quality:.0%}) ───")

            if "headlines" in var and isinstance(var["headlines"], list):
                if "headlines" in var and isinstance(var["headlines"][0], dict) and "text" in var["headlines"][0]:
                    lines.append("  Headlines:")
                    for h in var["headlines"]:
                        lines.append(f"    [{h['chars']}c] {h['text']}")
                lines.append("  Descriptions:")
                for d in var["descriptions"]:
                    if isinstance(d, dict):
                        lines.append(f"    [{d['chars']}c] {d['text']}")
                    else:
                        lines.append(f"    {d}")
            elif "headline" in var:
                lines.append(f"  Headline: {var['headline']}")
                lines.append(f"  Body: {var['body'][:200]}")

            if var.get("cta"):
                lines.append(f"  CTA: {var['cta']}")
            if var.get("image_suggestions"):
                for img in var.get("image_suggestions", []):
                    lines.append(f"  🎨 Image: {img}")
            if var.get("social_proof"):
                lines.append(f"  ✓ Social Proof: {var['social_proof']}")
            lines.append("")
        return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ad_copy_agent.py",
        description="📢 Ad Copy Agent — Google Ads, Facebook Ads, Display, LinkedIn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Google Search ads
  python3 ad_copy_agent.py --type google_search --product "AI Chatbot SaaS" --lang en \\
    --primary-keyword "AI chatbot" --benefit-1 "automate support" --benefit-2 "save 10h/week"

  # Facebook ad
  python3 ad_copy_agent.py --type facebook --product "Print on Demand Course" --lang de \\
    --benefit-1 "dein eigenes Business" --benefit-2 "500€/Monat passiv"

  # Display banner
  python3 ad_copy_agent.py --type google_display --product "SEO Tool" --lang en

  # LinkedIn sponsored content
  python3 ad_copy_agent.py --type linkedin --product "B2B SaaS Platform" --lang en \\
    --primary-keyword "workflow automation"

  # Landing page hero
  python3 ad_copy_agent.py --type landing_hero --product "PromptCache Pro" --lang de

  # List all
  python3 ad_copy_agent.py --list
        """
    )
    parser.add_argument("--type", dest="ad_type", choices=[t.value for t in AdType], required=True)
    parser.add_argument("--product", type=str, required=True, help="Product/service name")
    parser.add_argument("--lang", choices=["de", "en"], default="de")
    parser.add_argument("--tone", choices=[t.value for t in Tone], default=Tone.EMOTIONAL.value)
    parser.add_argument("--primary-keyword", dest="primary_keyword", type=str, default="",
                        help="Primary targeting keyword")
    parser.add_argument("--secondary-keywords", dest="secondary_keywords", type=str, default="",
                        help="Comma-separated secondary keywords")
    parser.add_argument("--benefit-1", dest="benefit_1", type=str, default="",
                        help="Primary benefit (e.g. 'time savings')")
    parser.add_argument("--benefit-2", dest="benefit_2", type=str, default="",
                        help="Secondary benefit")
    parser.add_argument("--benefit-3", dest="benefit_3", type=str, default="",
                        help="Third benefit")
    parser.add_argument("--pain", dest="audience_pain", type=str, default="",
                        help="Audience pain point (e.g. 'zu viel Zeit verlieren')")
    parser.add_argument("--cta-text", dest="cta_text", type=str, default="",
                        help="Custom CTA text")
    parser.add_argument("--price", type=str, default="",
                        help="Price (for urgency ads)")
    parser.add_argument("--headline-count", dest="headline_variants", type=int, default=3)
    parser.add_argument("--desc-count", dest="description_variants", type=int, default=2)
    parser.add_argument("--no-numbers", dest="no_numbers", action="store_true", help="Exclude numbers from copy")
    parser.add_argument("--output", type=str, help="Save output to file")
    parser.add_argument("--list", action="store_true", help="List all cached ads")
    return parser.parse_args()


def main() -> None:
    agent = AdCopyAgent()
    args = parse_args()

    if args.list:
        ads = agent.list_ads()
        if not ads:
            print("No ads in cache.")
            return
        print(f"\n📢 Cached Ad Sets ({len(ads)} total)\n")
        for a in ads:
            ts = a.get("generated_at", "")[:10]
            print(f"  [{ts}] {a.get('product','?')} | {a.get('ad_type','?')} | {len(a.get('variants',[]))} variants")
        return

    spec = AdSpec(
        ad_type=AdType(args.ad_type),
        product=args.product,
        language=args.lang,
        tone=Tone(args.tone),
        primary_keyword=args.primary_keyword,
        secondary_keywords=[k.strip() for k in args.secondary_keywords.split(",") if k.strip()],
        benefit_1=args.benefit_1,
        benefit_2=args.benefit_2,
        benefit_3=args.benefit_3,
        audience_pain=args.audience_pain,
        cta_text=args.cta_text,
        price=args.price,
        headline_variants=args.headline_variants,
        description_variants=args.description_variants,
        include_numbers=not args.no_numbers,
    )

    result = agent.generate(spec)
    output = agent.export_ads(result)
    print(output)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"\n💾 Saved to {args.output}")


if __name__ == "__main__":
    main()
