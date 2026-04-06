#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          CONTENT AGENT - ENHANCED                          ║
║          Multi-Platform · Multiple Tones · SEO · Repurposing ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - 8 Plattformen (Blog, LinkedIn, Twitter, Instagram, YouTube, Newsletter, Press, Landing)
  - 7 Töne (Professional bis Storytelling)
  - Length Control (Short bis Epic)
  - SEO Optimierung
  - Content Repurposing (1→5 Formate)
  - Multi-Language (DE/EN)

Hinweis: LLM-Routing wird NICHT verwendet - wir nutzen Brevo für Mail
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Dict, Optional

log = logging.getLogger("openclaw.content")


class Platform(str, Enum):
    BLOG = "blog"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    NEWSLETTER = "newsletter"
    YOUTUBE = "youtube"
    PRESS = "press"
    LANDING_PAGE = "landing_page"
    THREAD = "thread"


class Tone(str, Enum):
    PROFESSIONAL = "professional"      # Formell, sachlich
    CONVERSATIONAL = "conversational"  # Locker, direkt
    INSPIRATIONAL = "inspirational"   # Motivierend, visionär
    TECHNICAL = "technical"            # Präzise, fachlich
    HUMOROUS = "humorous"             # Witzig, leicht
    AUTHORITATIVE = "authoritative"    # Experten-Stimme
    STORYTELLING = "storytelling"      # Narrativ, emotional


class ContentLength(str, Enum):
    SHORT = "short"     # < 300 Wörter
    MEDIUM = "medium"   # 300-800 Wörter
    LONG = "long"       # 800-2000 Wörter
    EPIC = "epic"      # 2000+ Wörter


@dataclass
class ContentSpec:
    """Spezifikation für Content"""
    platform: Platform
    topic: str
    tone: Tone = Tone.PROFESSIONAL
    length: ContentLength = ContentLength.MEDIUM
    language: str = "de"
    keywords: List[str] = field(default_factory=list)
    include_cta: bool = True
    hashtags: List[str] = field(default_factory=list)


@dataclass
class ContentResult:
    """Ergebnis von Content-Generierung"""
    content: str
    platform: Platform
    word_count: int
    seo_score: float
    meta_description: str = ""
    title: str = ""
    hashtags: List[str] = field(default_factory=list)


class ContentAgent:
    """
    Enhanced Content Agent mit:
    - Multi-Platform Support
    - Multiple Tones
    - SEO Optimization
    - Content Repurposing
    """
    
    def __init__(self):
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict:
        """Lade Content-Templates"""
        return {
            Platform.BLOG: {
                "structure": ["Einleitung", "Hauptteil", "Fazit"],
                "cta": "Kontaktieren Sie uns für mehr Informationen."
            },
            Platform.LINKEDIN: {
                "hook": "🐦 {hook}\n\n",
                "body": "{body}\n\n",
                "cta": "👇 Kommentieren Sie Ihre Erfahrungen!"
            },
            Platform.TWITTER: {
                "max_length": 280,
                "thread_format": True
            },
            Platform.NEWSLETTER: {
                "structure": ["Betreff", "Einleitung", "Hauptinhalt", "Call-to-Action"]
            }
        }
    
    def generate_content(self, spec: ContentSpec) -> ContentResult:
        """
        Generiere Content basierend auf Spec
        
        In real implementation: dies würde den LLM aufrufen.
        Hier: Template-basierte Generierung.
        """
        log.info(f"📝 Generiere Content: {spec.platform.value} | {spec.tone.value}")
        
        if spec.platform == Platform.BLOG:
            return self.generate_blog(spec)
        elif spec.platform == Platform.LINKEDIN:
            return self.generate_linkedin(spec)
        elif spec.platform == Platform.TWITTER:
            return self.generate_twitter(spec)
        elif spec.platform == Platform.NEWSLETTER:
            return self.generate_newsletter(spec)
        elif spec.platform == Platform.LANDING_PAGE:
            return self.generate_landing(spec)
        
        return ContentResult(
            content="Content generation requires LLM integration",
            platform=spec.platform,
            word_count=0,
            seo_score=0.0
        )
    
    def generate_blog(self, spec: ContentSpec) -> ContentResult:
        """Generiere Blog Post"""
        
        # Length-based structure
        structures = {
            ContentLength.SHORT: {
                "intro": "Einleitung (50 Wörter)",
                "body": "Hauptteil (150 Wörter)",
                "conclusion": "Fazit (50 Wörter)"
            },
            ContentLength.MEDIUM: {
                "intro": "Einleitung (100 Wörter)",
                "body": "Hauptteil (500 Wörter)",
                "conclusion": "Fazit (100 Wörter)"
            },
            ContentLength.LONG: {
                "intro": "Einleitung (200 Wörter)",
                "body": "Hauptteil (1500 Wörter)",
                "conclusion": "Fazit (200 Wörter)"
            },
            ContentLength.EPIC: {
                "intro": "Einleitung (300 Wörter)",
                "body": "Hauptteil (3000+ Wörter)",
                "conclusion": "Fazit (300 Wörter)"
            }
        }
        
        structure = structures.get(spec.length, structures[ContentLength.MEDIUM])
        
        # Tone-based intro
        intros = {
            Tone.PROFESSIONAL: f"In diesem Artikel behandeln wir das Thema {spec.topic}.",
            Tone.CONVERSATIONAL: f"Hey! Heute sprechen wir über {spec.topic} - das wird interessant!",
            Tone.INSPIRATIONAL: f"Stellen Sie sich vor: {spec.topic}. Die Möglichkeit, Ihr Leben zu verändern!",
            Tone.TECHNICAL: f"Technische Analyse: {spec.topic} - Fakten und Daten.",
            Tone.HUMOROUS: f"Okay, okay... {spec.topic}. Nicht langweilen, versprochen! 😄",
            Tone.AUTHORITATIVE: f"Als Experte kann ich sagen: {spec.topic} ist entscheidend.",
            Tone.STORYTELLING: f"Es war einmal... {spec.topic}. Diese Geschichte wird Ihr Leben verändern."
        }
        
        title = self.generate_title(spec.topic, spec.tone)
        intro = intros.get(spec.tone, intros[Tone.PROFESSIONAL])
        body = self.generate_body(spec.topic, spec.length, spec.keywords)
        conclusion = f"\n\n## Fazit\n\n{self.get_cta(spec)}"
        
        content = f"# {title}\n\n{intro}\n\n{body}\n\n{conclusion}"
        
        # SEO
        seo_score = self.calculate_seo_score(content, spec.keywords)
        meta_desc = content[:160].replace("\n", " ")
        
        return ContentResult(
            content=content,
            platform=Platform.BLOG,
            word_count=len(content.split()),
            seo_score=seo_score,
            meta_description=meta_desc,
            title=title
        )
    
    def generate_linkedin(self, spec: ContentSpec) -> ContentResult:
        """Generiere LinkedIn Post"""
        
        hooks = {
            Tone.PROFESSIONAL: f"📊 Wichtige Erkenntnis zum Thema {spec.topic}:",
            Tone.CONVERSATIONAL: f"🔥 Ich muss mal was loswerden über {spec.topic}...",
            Tone.INSPIRATIONAL: f"✨ {spec.topic} - So kann es gehen!",
            Tone.AUTHORITATIVE: f"📢 Faktencheck: {spec.topic}",
            Tone.STORYTELLING: f"Eine Geschichte aus der Praxis..."
        }
        
        hook = hooks.get(spec.tone, hooks[Tone.PROFESSIONAL])
        
        body = f"Hier sind meine Gedanken zu {spec.topic}:\n\n"
        body += "• Punkt 1: Wichtiger Aspekt\n"
        body += "• Punkt 2: Erfahrung aus der Praxis\n"
        body += "• Punkt 3: Nächste Schritte\n\n"
        
        cta = "👇 Ich bin gespannt auf eure Erfahrungen! Kommentiert unten."
        
        content = f"{hook}\n\n{body}\n\n{cta}"
        
        # Add hashtags
        hashtags = spec.hashtags or ["#business", "#growth", "#learning"]
        content += "\n\n" + " ".join(hashtags)
        
        return ContentResult(
            content=content,
            platform=Platform.LINKEDIN,
            word_count=len(content.split()),
            seo_score=0.7,
            hashtags=hashtags
        )
    
    def generate_twitter(self, spec: ContentSpec) -> ContentResult:
        """Generiere Twitter/X Post oder Thread"""
        
        max_length = 280
        
        tweets = []
        
        # Hook Tweet
        hook = f"🧵 Alles über {spec.topic} (Thread)\n\n"
        
        # Content tweets
        content_parts = spec.topic.split()
        tweet_count = min(5, len(content_parts) + 2)
        
        for i in range(tweet_count):
            if i == 0:
                tweet = f"1/{tweet_count}\n\n{hook}"
            else:
                tweet = f"{i+1}/{tweet_count}\n\nWichtiger Punkt #{i} zu {spec.topic}:\n\n"
                tweet += "Hier Details rein...\n"
            
            if len(tweet) > max_length:
                tweet = tweet[:max_length-3] + "..."
            
            tweets.append(tweet)
        
        # Final tweet
        tweets.append(f"{tweet_count}/{tweet_count}\n\n✅ Fazit: {spec.topic} ist wichtig. \n\n👉 Follow für mehr!\n\n#thread #content")
        
        content = "\n\n---\n\n".join(tweets)
        
        hashtags = spec.hashtags or ["#" + spec.topic.replace(" ", ""), "#learning"]
        
        return ContentResult(
            content=content,
            platform=Platform.TWITTER,
            word_count=len(content.split()),
            seo_score=0.6,
            hashtags=hashtags
        )
    
    def generate_newsletter(self, spec: ContentSpec) -> ContentResult:
        """Generiere Newsletter"""
        
        greeting = "Hallo!" if spec.language == "en" else "Guten Tag!"
        
        content = f"""Subject: {spec.topic} - Das Wichtigste diese Woche

{greeting}

Herzlich willkommen zu unserem Newsletter über {spec.topic}.

---

## Das Wichtigste in Kürze

• Punkt 1: Aktuelle Entwicklung
• Punkt 2: Was Sie wissen müssen
• Punkt 3: Nächste Schritte

---

## Detailansicht

[Hier folgt der ausführliche Inhalt zu {spec.topic}]

---

## Call-to-Action

{self.get_cta(spec)}

---

Mit freundlichen Grüßen,
Ihr EmpireHazeClaw Team

---
📧 Abmeldung jederzeit möglich
"""
        
        return ContentResult(
            content=content,
            platform=Platform.NEWSLETTER,
            word_count=len(content.split()),
            seo_score=0.5
        )
    
    def generate_landing(self, spec: ContentSpec) -> ContentResult:
        """Generiere Landing Page Content"""
        
        content = f"""
# {spec.topic}

## Ihr Problem, unsere Lösung

{self.get_hero_section(spec)}

---

## Warum wir?

✓ Qualität
✓ Schnelle Lieferung
✓ Faire Preise

---

## Angebot

[Hier Produkt/Service beschreiben]

---

## CTA

{self.get_cta(spec)}

---

## FAQ

**Frage 1:** Antwort
**Frage 2:** Antwort

---

## Kontakt

📧 empirehazeclaw@gmail.com
🌐 empirehazeclaw.de
"""
        
        return ContentResult(
            content=content,
            platform=Platform.LANDING_PAGE,
            word_count=len(content.split()),
            seo_score=0.8,
            title=spec.topic
        )
    
    def generate_title(self, topic: str, tone: Tone) -> str:
        """Generiere Titel basierend auf Tone"""
        
        templates = {
            Tone.PROFESSIONAL: "{topic} - Der complete Guide",
            Tone.CONVERSATIONAL: "{topic}: Alles was du wissen musst",
            Tone.INSPIRATIONAL: "Wie {topic} dein Leben verändert",
            Tone.TECHNICAL: "{topic} - Technische Analyse",
            Tone.HUMOROUS: "{topic} (und warum es weniger langweilig ist als du denkst)",
            Tone.AUTHORITATIVE: "Der definitive Guide zu {topic}",
            Tone.STORYTELLING: "Die Geschichte von {topic}"
        }
        
        template = templates.get(tone, templates[Tone.PROFESSIONAL])
        return template.format(topic=topic)
    
    def generate_body(self, topic: str, length: ContentLength, keywords: List[str]) -> str:
        """Generiere Hauptteil"""
        
        keyword_text = ""
        if keywords:
            keyword_text = "\n\n**Keywords:** " + ", ".join(keywords)
        
        body = f"""
## Einleitung

{topic} ist ein wichtiges Thema, das immer mehr an Bedeutung gewinnt.

## Hauptteil

In diesem Abschnitt behandeln wir die wichtigsten Aspekte von {topic}:

1. **Grundlagen**: Die Basis muss stimmen
2. **Fortgeschritten**: Tieferes Verständnis
3. **Praxis**: Umsetzung in der Realität

{keyword_text}

## Tipps

- Tipp 1: Anfang small
- Tipp 2: Kontinuierlich dranbleiben
- Tipp 3: Aus Fehlern lernen
"""
        
        return body
    
    def get_cta(self, spec: ContentSpec) -> str:
        """Generiere Call-to-Action"""
        
        ctas = {
            Platform.BLOG: "Haben Sie Fragen? Kontaktieren Sie uns!",
            Platform.LINKEDIN: "Gefällt Ihnen der Beitrag? 👍 + Kommentieren Sie!",
            Platform.NEWSLETTER: "Jetzt anmelden: empirehazeclaw.de",
            Platform.LANDING_PAGE: "Jetzt starten - kostenlos testen!"
        }
        
        return ctas.get(spec.platform, "Kontaktieren Sie uns!")
    
    def calculate_seo_score(self, content: str, keywords: List[str]) -> float:
        """Berechne SEO Score"""
        if not keywords:
            return 0.5
        
        content_lower = content.lower()
        keyword_count = sum(1 for kw in keywords if kw.lower() in content_lower)
        
        score = min(keyword_count / len(keywords), 1.0)
        
        # Bonus for structure
        if "# " in content:  # Has headings
            score += 0.1
        if len(content.split()) > 300:  # Sufficient length
            score += 0.1
        
        return min(score, 1.0)
    
    def repurposing(self, source_content: str, source_platform: Platform) -> List[ContentResult]:
        """
        Content Repurposing: 1 Content → 5 Formate
        """
        log.info("🔄 Repurposing Content...")
        
        results = []
        
        # Extract key points
        key_points = self.extract_key_points(source_content)
        
        # Generate for each platform
        specs = [
            ContentSpec(platform=Platform.LINKEDIN, topic="Content aus Blog", tone=Tone.PROFESSIONAL),
            ContentSpec(platform=Platform.TWITTER, topic="Content aus Blog", tone=Tone.CONVERSATIONAL),
            ContentSpec(platform=Platform.NEWSLETTER, topic="Content aus Blog", tone=Tone.PROFESSIONAL),
            ContentSpec(platform=Platform.INSTAGRAM, topic="Content aus Blog", tone=Tone.INSPIRATIONAL),
            ContentSpec(platform=Platform.THREAD, topic="Content aus Blog", tone=Tone.STORYTELLING)
        ]
        
        for spec in specs:
            result = self.generate_content(spec)
            results.append(result)
        
        return results
    
    def extract_key_points(self, content: str) -> List[str]:
        """Extrahiere wichtige Punkte aus Content"""
        points = []
        
        # Look for bullet points
        bullet_points = re.findall(r'[-•*]\s*(.+)', content)
        points.extend(bullet_points[:5])
        
        # Look for numbered lists
        numbered = re.findall(r'\d+\.\s*(.+)', content)
        points.extend(numbered[:5])
        
        return points[:10]
    
    def schedule_content(self, contents: List[ContentSpec], schedule: Dict) -> List[Dict]:
        """Plane Content für verschiedene Plattformen"""
        
        scheduled = []
        
        for i, spec in enumerate(contents):
            scheduled.append({
                "content": spec.topic,
                "platform": spec.platform.value,
                "scheduled_time": schedule.get(spec.platform.value, ""),
                "order": i + 1
            })
        
        return scheduled


async def main():
    """CLI Test"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Content Agent")
    parser.add_argument("--topic", default="KI Trends 2026")
    parser.add_argument("--platform", choices=[p.value for p in Platform], default="blog")
    parser.add_argument("--tone", choices=[t.value for t in Tone], default="professional")
    parser.add_argument("--length", choices=[l.value for l in ContentLength], default="medium")
    
    args = parser.parse_args()
    
    agent = ContentAgent()
    
    spec = ContentSpec(
        platform=Platform(args.platform),
        topic=args.topic,
        tone=Tone(args.tone),
        length=ContentLength(args.length),
        keywords=["KI", "2026", "Trends"]
    )
    
    result = agent.generate_content(spec)
    
    print(f"\n📝 CONTENT GENERATED")
    print(f"   Platform: {result.platform.value}")
    print(f"   Words: {result.word_count}")
    print(f"   SEO Score: {result.seo_score:.2f}")
    print(f"\n{result.content[:300]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
