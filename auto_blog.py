#!/usr/bin/env python3
"""Auto Blog Post Generator"""
import subprocess
import sys
import os
from datetime import datetime

BLOG_TOPICS = [
    "AI trends 2024",
    "Web design best practices",
    "Local business marketing",
    "SEO tips",
    "Chatbot benefits"
]

def generate_blog(topic=None):
    topic = topic or BLOG_TOPICS[0]
    print(f"✍️ Generating blog about: {topic}")
    
    # Check if blog generator exists
    if os.path.exists("scripts/blog_generator.py"):
        result = subprocess.run(["python3", "scripts/blog_generator.py", topic], 
                               capture_output=True, text=True)
        return result.stdout[:500]
    
    return "📝 Blog draft would be generated"

def list_topics():
    print("=== 📝 BLOG TOPICS ===")
    for t in BLOG_TOPICS:
        print(f"  - {t}")

if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    print(generate_blog(topic))
