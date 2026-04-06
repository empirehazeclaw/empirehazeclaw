#!/usr/bin/env python3
"""
Intelligent Research Trigger
Checks for breaking news + market hours → Triggers Research Agent
"""

import requests
import os
import time
from datetime import datetime

# Configuration
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = os.getenv("OPENCLAW_TOKEN", "")  # Set if needed

# Smart triggers
TRIGGERS = {
    "market_hours": {"active": True, "hours": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]},
    "breaking_keywords": {"active": True, "keywords": ["iran", "war", "trump", "putin", "recession", "stock", "market crash", "earnings"]},
}

def is_market_hours():
    """Check if in market hours (simplified)"""
    now = datetime.now()
    utc_hour = now.hour
    # US market hours: 14:30-21:00 UTC
    return 14 <= utc_hour <= 21

def check_keywords():
    """Check for breaking keywords in news (simple version)"""
    # Using a simple approach - could integrate with real news API
    keywords = TRIGGERS["breaking_keywords"]["keywords"]
    
    # For now, check GDELT (free)
    try:
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        params = {
            "query": " OR ".join(TRIGGERS["breaking_keywords"]["keywords"]),
            "mode": "artlist",
            "maxrecords": 3,
            "format": "json"
        }
        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            if articles:
                return True, articles[0].get("title", "Breaking news")
    except:
        pass
    
    return False, None

def trigger_research_agent(reason):
    """Trigger the research agent via OpenClaw API"""
    # This would spawn the research agent
    # For now, just log
    print(f"🤖 Would trigger research agent: {reason}")
    return True

def main():
    print(f"🔍 Intelligent Research Check - {datetime.now().strftime('%H:%M')}")
    
    reasons = []
    
    # Check market hours
    if is_market_hours():
        reasons.append("market_hours")
    
    # Check keywords
    has_keywords, title = check_keywords()
    if has_keywords:
        reasons.append(f"breaking: {title[:50]}")
    
    # Decide
    if reasons:
        reason = " + ".join(reasons)
        print(f"✅ Triggering research: {reason}")
        trigger_research_agent(reason)
    else:
        print("⏳ No trigger - quiet period")

if __name__ == "__main__":
    main()
