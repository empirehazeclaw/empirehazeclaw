#!/usr/bin/env python3
"""
Twitter Poster - Improved with Humanizer
Posts in English, natural language
"""
import subprocess
import random
from datetime import datetime
import json

# Content Templates - English, Human-like
POSTS = [
    {
        "topic": "ai_hosting",
        "content": "Just set up my own AI infrastructure on German servers. No US cloud, full DSGVO compliance, and it's actually working smoothly. 🇩🇪🤖",
        "hashtags": ["#AI", "#GermanTech", "#DSGVO"]
    },
    {
        "topic": "startup",
        "content": "Building in public: Launched a managed AI hosting service for German companies. Turns out many businesses just want AI working without dealing with servers. Validated!",
        "hashtags": ["#SaaS", "#Startup", "#BuildInPublic"]
    },
    {
        "topic": "automation",
        "content": "The future of business is automation. But most companies don't have devs on staff. That's where we come in - fully managed AI solutions. No setup required.",
        "hashtags": ["#Automation", "#AI", "#NoCode"]
    },
    {
        "topic": "german_market",
        "content": "Interesting: German companies are actually MORE interested in AI than expected. They just need it to be compliant. Data stays in Germany, everything works.",
        "hashtags": ["#GermanMarket", "#AI", "#Europe"]
    },
    {
        "topic": "launch",
        "content": "After weeks of building, our managed AI hosting is live. German servers, DSGVO compliant, OpenClaw pre-installed. The market response has been better than expected.",
        "hashtags": ["#Launch", "#AI", "#Hosting"]
    },
    {
        "topic": "value",
        "content": "Why manage your own servers when you can have AI working for you? Fixed costs, German data centers, zero sysadmin needed. Simple.",
        "hashtags": ["#ManagedServices", "#AI", "#Simplicity"]
    }
]

def post_twitter():
    """Post to Twitter using xurl"""
    # Select random post
    post = random.choice(POSTS)
    
    # Build tweet
    content = post["content"]
    hashtags = " ".join(post["hashtags"])
    tweet = f"{content}\n\n{hashtags}"
    
    # Limit to 280 chars
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    print(f"[{datetime.now().isoformat()}] 🐦 Posting to Twitter...")
    print(f"   Content: {content[:50]}...")
    
    # Post via xurl
    result = subprocess.run(
        ["xurl", "post", tweet],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if "id" in result.stdout:
        print(f"   ✅ Posted successfully!")
        return True
    else:
        print(f"   ❌ Error: {result.stderr[:100]}")
        return False

if __name__ == "__main__":
    success = post_twitter()
    exit(0 if success else 1)
