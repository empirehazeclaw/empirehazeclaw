#!/usr/bin/env python3
"""
Ultimate Follower Growth System v2
Advanced optimization for Twitter growth
"""

import json
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict

LOG_FILE = "/home/clawbot/.openclaw/logs/growth_v2.json"

class UltimateGrowth:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "strategy": {
                    "aggressive_mode": True,
                    "sleep_hours": [0, 1, 2, 3, 4, 5],  # Don't engage at night
                    "target_competitors": True,
                    "engage_with_commenters": True,
                    "reply_to_trending": True
                },
                "targets": {
                    "competitors": [
                        {"handle": "openclawai", "name": "OpenClaw AI"},
                        {"handle": "elevenlabsai", "name": "ElevenLabs"},
                        {"handle": "runwayml", "name": "Runway"},
                        {"handle": "midjourney", "name": "Midjourney"},
                        {"handle": "chatgpt", "name": "ChatGPT"},
                        {"handle": "anthropicai", "name": "Anthropic"},
                        {"handle": "googleaistudio", "name": "Google AI"},
                        {"handle": "microsoftai", "name": "Microsoft AI"},
                        {"handle": "metaai", "name": "Meta AI"},
                        {"handle": "stabilityai", "name": "Stability AI"}
                    ],
                    "influencers": [
                        {"handle": "elonmusk", "name": "Elon Musk"},
                        {"handle": "sama", "name": "Sam Altman"},
                        {"handle": "AndrewYNg", "name": "Andrew Ng"},
                        {"handle": "GaryVee", "name": "Gary Vaynerchuk"},
                        {"handle": "swyx", "name": "swyx"},
                        {"handle": "levelsio", "name": "Pieter Levels"},
                        {"handle": "shl", "name": "Shlomo"},
                        {"handle": "brian_roemmele", "name": "Brian Roemmele"}
                    ],
                    "hashtags": {
                        "primary": ["#AI", "#Automation", "#Tech", "#Startup", "#Innovation", "#Coding"],
                        "secondary": ["#Entrepreneur", "#Business", "#Success", "#Productivity", "#GrowthHacking"],
                        "trending": ["#New", "#Viral", "#Trending"]
                    }
                },
                "content_templates": {
                    "reply_ai": [
                        "Great insight! 🔥 Following for more!",
                        "This is exactly what I needed to read today!",
                        "Couldn't agree more! 👏",
                        "Well said! Adding this to my notes 📝"
                    ],
                    "reply_business": [
                        "This is great advice! Thanks for sharing!",
                        "Love this perspective! 💡",
                        "Exactly what I needed to hear today!",
                        "Great point! 👆"
                    ]
                },
                "daily_stats": {},
                "engagement_log": []
            }
            self.save_data()
            
    def save_data(self):
        with open(LOG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def get_current_hour(self):
        return datetime.now().hour
        
    def should_engage(self):
        """Check if we should engage right now"""
        current_hour = self.get_current_hour()
        
        # Don't engage during sleep hours
        if current_hour in self.data["strategy"].get("sleep_hours", []):
            return False, "Sleep hours"
            
        # Don't engage if aggressive mode disabled
        if not self.data["strategy"].get("aggressive_mode", True):
            return False, "Aggressive mode off"
            
        return True, "Active"
        
    def get_target_hashtags(self, count=5):
        """Get hashtags to engage with"""
        primary = self.data["targets"]["hashtags"]["primary"]
        secondary = self.data["targets"]["hashtags"]["secondary"]
        
        # 70% primary, 30% secondary
        if random.random() < 0.7:
            return random.sample(primary, min(count, len(primary)))
        else:
            return random.sample(primary + secondary, min(count, len(primary + secondary)))
            
    def get_target_accounts(self, count=5):
        """Get accounts to engage with"""
        competitors = self.data["targets"]["competitors"]
        influencers = self.data["targets"]["influencers"]
        
        # Mix of competitors and influencers
        all_accounts = competitors + influencers
        return random.sample(all_accounts, min(count, len(all_accounts)))
        
    def get_reply_template(self, category="reply_ai"):
        """Get a random reply template"""
        templates = self.data["content_templates"].get(category, ["Nice!"])
        return random.choice(templates)
        
    def generate_action_plan(self):
        """Generate a comprehensive action plan"""
        can_engage, reason = self.should_engage()
        
        if not can_engage:
            return {
                "should_engage": False,
                "reason": reason,
                "actions": []
            }
            
        actions = []
        
        # 1. Follow 2-3 accounts
        targets = self.get_target_accounts(3)
        for t in targets:
            actions.append({
                "type": "follow",
                "target": t["handle"],
                "priority": "high"
            })
            
        # 2. Like 5-8 tweets
        hashtags = self.get_target_hashtags(8)
        for h in hashtags:
            actions.append({
                "type": "like",
                "target": h,
                "priority": "medium"
            })
            
        # 3. Reply to 1-2 tweets
        targets2 = self.get_target_accounts(2)
        for t in targets2:
            category = "reply_ai" if any(c in t["handle"].lower() for c in ["ai", "openai", "anthropic", "google", "meta"]) else "reply_business"
            actions.append({
                "type": "reply",
                "target": t["handle"],
                "template": self.get_reply_template(category),
                "priority": "medium"
            })
            
        # 4. Retweet 1-2 posts
        targets3 = self.get_target_accounts(2)
        for t in targets3:
            actions.append({
                "type": "retweet",
                "target": t["handle"],
                "priority": "low"
            })
            
        return {
            "should_engage": True,
            "timestamp": datetime.now().isoformat(),
            "hour": self.get_current_hour(),
            "actions": actions,
            "target_hashtags": hashtags[:5],
            "target_accounts": [t["handle"] for t in targets[:3]]
        }
        
    def log_action(self, action_type, target, success=True):
        """Log an engagement action"""
        self.data["engagement_log"].append({
            "action": action_type,
            "target": target,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "hour": self.get_current_hour()
        })
        
        # Keep last 500
        self.data["engagement_log"] = self.data["engagement_log"][-500:]
        self.save_data()
        
    def get_daily_stats(self):
        """Get today's stats"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_actions = [
            e for e in self.data["engagement_log"]
            if e.get("timestamp", "").startswith(today)
        ]
        
        return {
            "likes": len([e for e in today_actions if e["action"] == "like"]),
            "follows": len([e for e in today_actions if e["action"] == "follow"]),
            "replies": len([e for e in today_actions if e["action"] == "reply"]),
            "retweets": len([e for e in today_actions if e["action"] == "retweet"]),
            "total": len(today_actions)
        }
        
    def get_weekly_insights(self):
        """Get weekly insights and optimization tips"""
        # Analyze last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).timestamp()
        
        recent = [
            e for e in self.data["engagement_log"]
            if datetime.fromisoformat(e["timestamp"]).timestamp() > week_ago
        ]
        
        if not recent:
            return "No data yet - engage more to get insights!"
            
        # Analyze by action type
        by_action = defaultdict(int)
        by_hour = defaultdict(int)
        
        for e in recent:
            by_action[e["action"]] += 1
            by_hour[e.get("hour", 0)] += 1
            
        # Find best hours
        best_hour = max(by_hour.items(), key=lambda x: x[1])[0] if by_hour else 0
        
        insights = f"📊 **Weekly Insights**\n\n"
        insights += f"**Actions:** {len(recent)} total\n"
        insights += f"  ❤️ Likes: {by_action.get('like', 0)}\n"
        insights += f"  👤 Follows: {by_action.get('follow', 0)}\n"
        insights += f"  💬 Replies: {by_action.get('reply', 0)}\n"
        insights += f"  🔄 Retweets: {by_action.get('retweet', 0)}\n\n"
        
        insights += f"**🕐 Best hour to engage:** {best_hour}:00\n"
        
        return insights
        
    def optimize_strategy(self):
        """Auto-optimize based on results"""
        stats = self.get_daily_stats()
        
        recommendations = []
        
        # Analyze engagement rates
        if stats["follows"] < 3:
            recommendations.append("Increase follows - target more competitors")
        if stats["likes"] < 10:
            recommendations.append("Increase likes - more visibility")
        if stats["replies"] < 1:
            recommendations.append("Start replying to increase reach")
            
        return recommendations

if __name__ == "__main__":
    growth = UltimateGrowth()
    
    print("🎯 **Ultimate Follower Growth System v2**\n")
    
    # Generate action plan
    plan = growth.generate_action_plan()
    
    print(f"Status: {plan['should_engage']} ({plan.get('reason', '')})")
    print(f"Hour: {plan.get('hour', 0)}:00")
    
    print(f"\n📋 **Today's Action Plan:**")
    for action in plan.get("actions", []):
        emoji = {"follow": "👤", "like": "❤️", "reply": "💬", "retweet": "🔄"}.get(action["type"], "•")
        print(f"  {emoji} {action['type']}: @{action.get('target', action.get('template', '')[:30])}")
        
    print(f"\n🏷️ **Target Hashtags:** {', '.join(plan.get('target_hashtags', [])[:5])}")
    
    print("\n" + "="*40)
    print(growth.get_weekly_insights())
    
    print("\n💡 **Recommendations:**")
    for rec in growth.optimize_strategy():
        print(f"  • {rec}")
