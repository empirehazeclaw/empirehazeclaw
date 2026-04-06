#!/usr/bin/env python3
"""
Trend Hunter System
Catches trending topics and creates timely content
Consolidated with trend_research.py
"""

import json
import os
import random
from datetime import datetime

# Optional: Import trend research module
try:
    from trend_research import TrendResearcher
    HAS_TREND_RESEARCH = True
except ImportError:
    HAS_TREND_RESEARCH = False

TRENDS_FILE = "/home/clawbot/.openclaw/logs/trend_hunter.json"

class TrendHunter:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        if os.path.exists(TRENDS_FILE):
            with open(TRENDS_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "tracked_keywords": [
                    "AI", "ChatGPT", "GPT-5", "OpenAI", "Anthropic",
                    "Automation", "NoCode", "Startup", "Tech", "Innovation",
                    "Bitcoin", "Crypto", "Trading", "SideHustle", "Money"
                ],
                "competitor_keywords": [
                    "OpenClaw", "Zapier", "Make", "Midjourney", "Leonardo"
                ],
                "trending_topics": [],
                "captured_trends": [],
                "posted_trends": [],
                "settings": {
                    "scan_interval_hours": 2,
                    "max_trends_per_day": 3,
                    "response_time_minutes": 30
                }
            }
            self.save_data()
            
    def save_data(self):
        with open(TRENDS_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def scan_twitter_trends(self):
        """Scan for trending topics (simulated - in production use Twitter API)"""
        
        # Simulated trending topics
        simulated_trends = [
            {
                "keyword": "GPT-5",
                "category": "AI",
                "volume": "500K+ tweets",
                "velocity": "high",
                "urgency": "high",
                "content_idea": "GPT-5 just released! Here is what it means for your business..."
            },
            {
                "keyword": "AI Agents",
                "category": "Automation",
                "volume": "100K+ tweets",
                "velocity": "medium",
                "urgency": "medium",
                "content_idea": "AI Agents are the future. Here is how to use them..."
            },
            {
                "keyword": "NoCode",
                "category": "Tech",
                "volume": "50K+ tweets",
                "velocity": "medium",
                "urgency": "low",
                "content_idea": "NoCode tools that will blow your mind in 2026..."
            },
            {
                "keyword": "Side Hustle",
                "category": "Business",
                "volume": "200K+ tweets",
                "velocity": "high",
                "urgency": "high",
                "content_idea": "5 Side Hustles that actually make money in 2026..."
            },
            {
                "keyword": "Bitcoin",
                "category": "Crypto",
                "volume": "1M+ tweets",
                "velocity": "very high",
                "urgency": "medium",
                "content_idea": "Bitcoin just hit a new high. Here is what to know..."
            }
        ]
        
        # Pick 2-3 random trends
        trends = random.sample(simulated_trends, min(3, len(simulated_trends)))
        
        for trend in trends:
            trend["detected_at"] = datetime.now().isoformat()
            trend["status"] = "new"
            
            # Check if already tracked
            existing = [t for t in self.data["trending_topics"] 
                      if t.get("keyword") == trend["keyword"]]
            
            if not existing:
                self.data["trending_topics"].append(trend)
                
        # Keep only last 20
        self.data["trending_topics"] = self.data["trending_topics"][-20:]
        self.save_data()
        
        return trends
        
    def capture_trend(self, trend_keyword):
        """Capture a trend for content creation"""
        trend = None
        for t in self.data["trending_topics"]:
            if t.get("keyword") == trend_keyword:
                trend = t
                break
                
        if not trend:
            return None, "Trend not found"
            
        # Create captured content
        captured = {
            "keyword": trend["keyword"],
            "category": trend.get("category"),
            "content_idea": trend.get("content_idea"),
            "urgency": trend.get("urgency"),
            "captured_at": datetime.now().isoformat(),
            "status": "ready_to_post"
        }
        
        self.data["captured_trends"].append(captured)
        self.save_data()
        
        return captured, "Success"
        
    def get_urgent_trends(self):
        """Get high urgency trends that need immediate action"""
        return [
            t for t in self.data["trending_topics"]
            if t.get("urgency") == "high" and t.get("status") != "posted"
        ]
        
    def get_ready_to_post(self):
        """Get trends ready to post"""
        return [
            t for t in self.data["captured_trends"]
            if t.get("status") == "ready_to_post"
        ]
        
    def mark_posted(self, keyword):
        """Mark a trend as posted"""
        for trend in self.data["captured_trends"]:
            if trend.get("keyword") == keyword:
                trend["status"] = "posted"
                trend["posted_at"] = datetime.now().isoformat()
                
        for trend in self.data["trending_topics"]:
            if trend.get("keyword") == keyword:
                trend["status"] = "posted"
                
        self.save_data()
        
    def generate_response(self, trend):
        """Generate a response template for a trend"""
        
        templates = {
            "high": [
                f"Just saw the buzz about {trend['keyword']}. Here is my take 🧵👇",
                f"{trend['keyword']} is trending! Let me break this down for you 👇",
                f"All eyes on {trend['keyword']}. Here is what you need to know:"
            ],
            "medium": [
                f"Interesting trend: {trend['keyword']}. My thoughts 👇",
                f"{trend['keyword']} - definitely worth watching. Here is why:",
                f"Noticed {trend['keyword']} gaining traction. Quick breakdown:"
            ],
            "low": [
                f"Saw some discussion about {trend['keyword']}. Sharing my perspective:",
                f"{trend['keyword']} - a solid trend worth exploring.",
                f"Filed this under 'interesting developments': {trend['keyword']}"
            ]
        }
        
        urgency = trend.get("urgency", "medium")
        return random.choice(templates.get(urgency, templates["medium"]))
        
    def get_stats(self):
        """Get trend hunter stats"""
        return {
            "total_trends": len(self.data["trending_topics"]),
            "captured": len(self.data["captured_trends"]),
            "posted": len(self.data["posted_trends"]),
            "urgent": len(self.get_urgent_trends())
        }
        
    def generate_report(self):
        """Generate trend hunter report"""
        stats = self.get_stats()
        urgent = self.get_urgent_trends()
        ready = self.get_ready_to_post()
        
        report = "📈 **Trend Hunter Report**\n\n"
        
        report += f"**📊 Stats:**\n"
        report += f"  Trending topics: {stats['total_trends']}\n"
        report += f"  Captured: {stats['captured']}\n"
        report += f"  Posted: {stats['posted']}\n"
        report += f"  🔥 Urgent: {stats['urgent']}\n\n"
        
        if urgent:
            report += "**🔥 Urgent Trends:**\n"
            for trend in urgent[:3]:
                report += f"  • {trend['keyword']} ({trend.get('category')})\n"
            report += "\n"
            
        if ready:
            report += "**✅ Ready to Post:**\n"
            for trend in ready:
                report += f"  • {trend['keyword']}: {trend.get('content_idea')[:50]}...\n"
                
        return report
        
    def run_scan(self):
        """Run a complete scan cycle"""
        print("🔍 Scanning for trends...")
        trends = self.scan_twitter_trends()
        
        print(f"Found {len(trends)} trending topics:")
        for t in trends:
            emoji = "🔴" if t.get("urgency") == "high" else "🟡" if t.get("urgency") == "medium" else "🟢"
            print(f"  {emoji} {t['keyword']} ({t.get('category')}) - {t.get('volume')}")
            
        print("\n" + self.generate_report())
        
        return trends

if __name__ == "__main__":
    hunter = TrendHunter()
    hunter.run_scan()
