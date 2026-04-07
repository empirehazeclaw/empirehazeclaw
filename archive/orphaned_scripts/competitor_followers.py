#!/usr/bin/env python3
"""
Competitor Followers System
Automatically follow followers of successful AI/Tech accounts
"""

import json
import os
import random
from datetime import datetime, timedelta

LOG_FILE = "/home/clawbot/.openclaw/logs/competitor_followers.json"
CONFIG_FILE = "/home/clawbot/.openclaw/workspace/memory/social_config.json"

class CompetitorFollowers:
    def __init__(self):
        self.load_config()
        self.load_log()
        
    def load_config(self):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            self.twitter = config.get("twitter", {})
            
    def load_log(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "competitors": [
                    {"handle": "openclawai", "name": "OpenClaw AI", "followers": 10000},
                    {"handle": "chatgpt", "name": "ChatGPT", "followers": 5000000},
                    {"handle": "elonmusk", "name": "Elon Musk", "followers": 200000000},
                    {"handle": "anthropicai", "name": "Anthropic", "followers": 500000},
                    {"handle": "googleaistudio", "name": "Google AI", "followers": 1000000},
                    {"handle": "sama", "name": "Sam Altman", "followers": 500000},
                    {"handle": "AndrewYNg", "name": "Andrew Ng", "followers": 2000000},
                    {"handle": "midjourney", "name": "Midjourney", "followers": 500000},
                    {"handle": "runwayml", "name": "Runway", "followers": 200000},
                    {"handle": "stabilityai", "name": "Stability AI", "followers": 100000}
                ],
                "target_list": [],
                "followed": [],
                "skipped": [],
                "daily_stats": {},
                "settings": {
                    "follow_per_day": 20,
                    "unfollow_per_day": 20,
                    "min_followers": 10,
                    "max_followers": 10000,
                    "exclude_verified": False,
                    "priority_companies": True
                }
            }
            self.save_log()
            
    def save_log(self):
        with open(LOG_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def get_api(self):
        """Get Twitter API connection"""
        from requests_oauthlib import OAuth1
        import requests
        
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        return oauth
        
    def can_follow(self):
        """Check if we can follow more today"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_followed = len([
            e for e in self.data["followed"]
            if e.get("date") == today
        ])
        
        limit = self.data["settings"]["follow_per_day"]
        return today_followed < limit, today_followed, limit
        
    def can_unfollow(self):
        """Check if we can unfollow today"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_unfollowed = len([
            e for e in self.data.get("unfollowed", [])
            if e.get("date") == today
        ])
        
        limit = self.data["settings"]["unfollow_per_day"]
        return today_unfollowing < limit, today_unfollowed, limit
        
    def get_target_users(self, competitor, count=100):
        """Get users to follow from competitor's followers"""
        # In production, this would call Twitter API:
        # GET /2/users/:id/followers
        
        # For now, simulate with realistic usernames
        # These would be fetched from API in production
        
        users = []
        base_names = [
            "ai_enthusiast", "tech_founder", "startup_creator", "dev_ai",
            "ml_engineer", "data_scientist", "product_hacker", "growth_hacker",
            "automation_fan", "future_builder", "code_ninja", "innovator_ai",
            "bot_builder", "neural_nets", "deep_learner", "smart_tech"
        ]
        
        for i in range(count):
            users.append({
                "id": f"{competitor['handle']}_follower_{i}",
                "username": f"{random.choice(base_names)}_{random.randint(100,999)}",
                "followers": random.randint(10, 5000),
                "following": random.randint(50, 1000),
                "bio": f"Interested in {random.choice(['AI', 'Tech', 'Startup', 'Automation'])}",
                "source": competitor["handle"]
            })
            
        return users
        
    def should_follow(self, user):
        """Decide if we should follow a user"""
        settings = self.data["settings"]
        
        # Check follower count
        if user["followers"] < settings["min_followers"]:
            return False, "Too few followers"
        if user["followers"] > settings["max_followers"]:
            return False, "Too many followers"
            
        # Check if already followed
        if user["username"] in [e["username"] for e in self.data["followed"]]:
            return False, "Already followed"
            
        return True, "OK"
        
    def follow_user(self, user):
        """Follow a user"""
        can_follow, count, limit = self.can_follow()
        
        if not can_follow:
            return False, "Daily limit reached"
            
        # In production: POST /2/users/:id/following
        # For now, simulate
        
        self.data["followed"].append({
            "username": user["username"],
            "user_id": user.get("id"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "source": user.get("source")
        })
        
        self.save_log()
        return True, f"Followed @{user['username']}"
        
    def unfollow_user(self, username):
        """Unfollow a user"""
        can_unfollow, count, limit = self.can_unfollow()
        
        if not can_unfollow:
            return False, "Daily limit reached"
            
        # Remove from followed list
        for entry in self.data["followed"]:
            if entry["username"] == username:
                entry["unfollowed_at"] = datetime.now().isoformat()
                if "unfollowed" not in self.data:
                    self.data["unfollowed"] = []
                self.data["unfollowed"].append(entry)
                self.data["followed"].remove(entry)
                self.save_log()
                return True, f"Unfollowed @{username}"
                
        return False, "Not in followed list"
        
    def generate_follow_plan(self):
        """Generate a follow plan for today"""
        plan = []
        
        # Get competitors to target
        competitors = self.data["competitors"]
        
        # Shuffle and pick 3-5
        target_competitors = random.sample(competitors, min(5, len(competitors)))
        
        for comp in target_competitors:
            users = self.get_target_users(comp, count=20)
            
            for user in users:
                should, reason = self.should_follow(user)
                
                if should:
                    plan.append({
                        "action": "follow",
                        "user": user,
                        "reason": f"Follower of @{comp['handle']}",
                        "priority": "high" if comp in self.data["competitors"][:3] else "medium"
                    })
                    
                    if len(plan) >= self.data["settings"]["follow_per_day"]:
                        break
                        
            if len(plan) >= self.data["settings"]["follow_per_day"]:
                break
                
        return plan
        
    def execute_plan(self, plan):
        """Execute the follow plan"""
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for item in plan:
            if item["action"] == "follow":
                success, msg = self.follow_user(item["user"])
                if success:
                    results["success"] += 1
                    print(f"  ✅ Following: @{item['user']['username']}")
                else:
                    results["failed"] += 1
                    
        return results
        
    def get_stats(self):
        """Get current statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        today_followed = len([
            e for e in self.data["followed"]
            if e.get("date") == today
        ])
        
        total_followed = len(self.data["followed"])
        
        # Unique sources
        sources = set(e.get("source") for e in self.data["followed"])
        
        return {
            "today_followed": today_followed,
            "total_followed": total_followed,
            "unique_sources": len(sources),
            "limit": self.data["settings"]["follow_per_day"]
        }
        
    def run_cycle(self):
        """Run a complete competitor follow cycle"""
        print("🎯 **Competitor Followers System**\n")
        
        # Check limits
        can_follow, count, limit = self.can_follow()
        print(f"📊 Today: {count}/{limit} follows used")
        
        if not can_follow:
            print("  ⏸️ Daily limit reached")
            return
            
        # Generate plan
        print("\n📋 Generating follow plan...")
        plan = self.generate_follow_plan()
        
        print(f"  Found {len(plan)} users to follow")
        
        # Execute
        print("\n🚀 Executing...")
        results = self.execute_plan(plan)
        
        print(f"\n✅ Results: +{results['success']} follows")
        
        return results

if __name__ == "__main__":
    bot = CompetitorFollowers()
    bot.run_cycle()
    
    print("\n📈 Stats:")
    stats = bot.get_stats()
    print(f"  Today: {stats['today_followed']}/{stats['limit']}")
    print(f"  Total: {stats['total_followed']}")
