#!/usr/bin/env python3
"""
Auto-Content Generator - Creates content from Research Finds
Triggered when research finds relevant topics
"""
import os
import json
from datetime import datetime

RESEARCH_FILE = "/home/clawbot/.openclaw/workspace/memory/research-{}.md"
CONTENT_DIR = "/home/clawbot/.openclaw/workspace/blog"

RELEVANT_TOPICS = [
    "ai", "chatgpt", "gpt", "llm", "automation",
    "marketing", "seo", "growth", "saas",
    "security", "kubernetes", "fastapi", "python"
]

def get_latest_research():
    """Get latest research findings"""
    date = datetime.now().strftime("%Y-%m-%d")
    filepath = RESEARCH_FILE.format(date)
    
    if os.path.exists(filepath):
        with open(filepath) as f:
            return f.read()
    return ""

def extract_topics(content):
    """Extract relevant topics from research"""
    found = []
    for topic in RELEVANT_TOPICS:
        if topic.lower() in content.lower():
            found.append(topic)
    return found

def generate_blog_post(topic):
    """Generate a blog post from topic"""
    # Simple template - in production use LLM
    title = f"{topic.title()} Insights - {datetime.now().strftime('%B %Y')}"
    content = f"""---
title: {title}
date: {datetime.now().strftime('%Y-%m-%d')}
category: research
---

# {title}

Basierend auf aktuellen Recherchen haben wir folgende Erkenntnisse zu {topic}:

## Zusammenfassung

[Auto-generierter Content basierend auf Research]

## Key Takeaways

- Erkenntnis 1
- Erkenntnis 2  
- Erkenntnis 3

## Fazit

{topic.title()} bleibt ein wichtiges Thema für Unternehmen.

---
*Automatisch generiert am {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
    return content

def save_blog_post(topic):
    """Save generated post"""
    filename = f"{CONTENT_DIR}/research-{topic}-{datetime.now().strftime('%Y%m%d')}.md"
    os.makedirs(CONTENT_DIR, exist_ok=True)
    
    content = generate_blog_post(topic)
    with open(filename, "w") as f:
        f.write(content)
    
    return filename

def main():
    print(f"🔍 Checking latest research...")
    
    content = get_latest_research()
    if not content:
        print("No research found today")
        return
    
    topics = extract_topics(content)
    if topics:
        print(f"Found relevant topics: {topics}")
        # Save first topic as blog post
        filename = save_blog_post(topics[0])
        print(f"✅ Created: {filename}")
    else:
        print("No relevant topics found")

if __name__ == "__main__":
    main()
