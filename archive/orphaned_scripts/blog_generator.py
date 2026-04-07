#!/usr/bin/env python3
"""
📝 BLOG GENERATOR
================
Generates blog posts from research and content.
"""

import os
import json
from datetime import datetime
from pathlib import Path

BLOG_DIR = Path("/home/clawbot/.openclaw/workspace/blog")
BLOG_DIR.mkdir(exist_ok=True)

TOPICS = [
    "AI Hosting",
    "DSGVO",
    "Marketing",
    "Automation",
    "German Tech"
]

class BlogGenerator:
    def __init__(self):
        self.topics = TOPICS
        
    def generate_post(self, topic, language="de"):
        """Generate a blog post"""
        
        templates = {
            "de": f"""---
title: {topic} - Der complete Guide
date: {datetime.now().strftime('%Y-%m-%d')}
category: {topic.lower()}
---

# {topic} - Der complete Guide

## Einleitung

{topic} wird immer wichtiger für deutsche Unternehmen.

## Warum {topic}?

- Punkt 1
- Punkt 2
- Punkt 3

## Fazit

{topic} ist ein Game-Changer.

---
*Automatisch generiert am {datetime.now().strftime('%Y-%m-%d')}*
""",
            "en": f"""---
title: {topic} - The Complete Guide
date: {datetime.now().strftime('%Y-%m-%d')}
category: {topic}
---

# {topic} - The Complete Guide

## Introduction

{topic} is becoming increasingly important.

## Why {topic}?

- Reason 1
- Reason 2
- Reason 3

## Conclusion

{topic} is a game-changer.

---
*Generated on {datetime.now().strftime('%Y-%m-%d')}*
"""
        }
        
        return templates.get(language, templates["de"])
    
    def save_post(self, topic, language="de"):
        """Save generated post"""
        content = self.generate_post(topic, language)
        filename = f"{BLOG_DIR}/{topic.lower().replace(' ','-')}-{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(filename, "w") as f:
            f.write(content)
        
        return filename

if __name__ == "__main__":
    generator = BlogGenerator()
    for topic in TOPICS[:3]:
        file = generator.save_post(topic)
        print(f"✅ Created: {file}")
