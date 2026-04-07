#!/usr/bin/env python3
"""
Weekly Content Generator
Automatisiert die Content-Erstellung für Blog, Twitter, LinkedIn und Reddit.
"""

import json
import os
from datetime import datetime, timedelta
import random

CONTENT_DIR = "/home/clawbot/.openclaw/workspace/content"
BLOG_TOPICS = [
    "KI-Transformation im deutschen Mittelstand",
    "Warum Agenten-Hostings die Zukunft sind",
    "DSGVO-konforme KI-Systeme in Deutschland",
    "Cost-Saving mit Prompt Caching",
    "Automatisierung von B2B-Akquise"
]

TWITTER_HOOKS = [
    "🐛 Germany’s SME sector is sleeping on AI agents.",
    "💸 90% of companies still waste money on AI.",
    "🇩🇪 Deutsche Firmen verpassen den KI-Zug.",
    "🤖 Your next employee costs 0€/hour.",
    "⚡ Stop doing manual outreach. Let AI do it."
]

def generate_blog_post():
    """Erstellt einen Blog-Post Entwurf"""
    topic = random.choice(BLOG_TOPICS)
    filename = f"{CONTENT_DIR}/blog_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    content = f"""---
title: {topic}
date: {datetime.now().isoformat()}
platform: empirehazeclaw.info
status: draft
---

# {topic}

## Einleitung

In diesem Artikel erfahren Sie, warum der deutsche Mittelstand von KI-Agenten profitiert...

## Hauptteil

### Das Problem
Viele Unternehmen...

### Die Lösung
Mit EmpireHazeClaw...

## Fazit
Die Zukunft ist automatisiert.

---
*Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    os.makedirs(CONTENT_DIR, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def generate_social_posts():
    """Erstellt Social Media Posts für Twitter/LinkedIn"""
    posts = []
    for i, hook in enumerate(TWITTER_HOOKS[:3]):
        filename = f"{CONTENT_DIR}/social_{datetime.now().strftime('%Y-%m-%d')}_{i}.md"
        content = f"""---
platform: twitter
date: {datetime.now().isoformat()}
status: scheduled
---

{hook}

#AI #GermanTech #Startup #Automation
"""
        with open(filename, 'w') as f:
            f.write(content)
        posts.append(filename)
    return posts

def generate_reddit_post():
    """Erstellt einen Reddit Post"""
    filename = f"{CONTENT_DIR}/reddit_{datetime.now().strftime('%Y-%m-%d')}.md"
    content = f"""---
subreddit: r/de_EDV
date: {datetime.now().isoformat()}
status: draft
---

# Wir haben unseren eigenen KI-Agenten - und er arbeitet 24/7

Hallo zusammen,

wir sind ein kleines Tech-Startup aus Deutschland und haben in den letzten Monaten ein System aufgebaut, das vollständig autonom arbeitet.

Frage an die Runde: Habt ihr schon Erfahrung mit KI-Agenten im Unternehmen?

---
*Automatisch generiert*
"""
    with open(filename, 'w') as f:
        f.write(content)
    return filename

if __name__ == "__main__":
    print("📝 Weekly Content Generator gestartet...")
    
    blog_file = generate_blog_post()
    print(f"✅ Blog Post erstellt: {blog_file}")
    
    social_files = generate_social_posts()
    print(f"✅ {len(social_files)} Social Posts erstellt")
    
    reddit_file = generate_reddit_post()
    print(f"✅ Reddit Post erstellt: {reddit_file}")
    
    print(f"\n🎉 Content für diese Woche generiert!")
    print(f"📁 Alle Dateien liegen in: {CONTENT_DIR}/")
