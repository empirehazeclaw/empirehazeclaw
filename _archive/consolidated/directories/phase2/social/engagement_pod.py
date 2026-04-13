#!/usr/bin/env python3
"""
Engagement Pod System
Coordinates mutual engagement between creators
"""

import json
import os
import random
from datetime import datetime

POD_FILE = "/home/clawbot/.openclaw/logs/engagement_pod.json"

class EngagementPod:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        if os.path.exists(POD_FILE):
            with open(POD_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "pod_name": "AI Growth Pod",
                "members": [],
                "rules": {
                    "min_engagement_per_day": 5,
                    "max_members": 10,
                    "engagement_timeout_hours": 24
                },
                "posts": [],
                "engagement_log": [],
                "stats": {
                    "total_engagements": 0,
                    "total_members": 0
                }
            }
            self.save_data()
            
    def save_data(self):
        with open(POD_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def add_member(self, username, platform, engagement_level="medium"):
        """Add a member to the pod"""
        if len(self.data["members"]) >= self.data["rules"]["max_members"]:
            return False, "Pod is full"
            
        # Check if already member
        for member in self.data["members"]:
            if member["username"] == username:
                return False, "Already a member"
                
        member = {
            "username": username,
            "platform": platform,
            "engagement_level": engagement_level,
            "added_at": datetime.now().isoformat(),
            "posts_shared": 0,
            "engagement_given": 0,
            "engagement_received": 0,
            "last_active": datetime.now().isoformat()
        }
        
        self.data["members"].append(member)
        self.data["stats"]["total_members"] = len(self.data["members"])
        self.save_data()
        
        return True, f"Added @{username} to pod"
        
    def remove_member(self, username):
        """Remove a member from the pod"""
        for i, member in enumerate(self.data["members"]):
            if member["username"] == username:
                self.data["members"].pop(i)
                self.data["stats"]["total_members"] = len(self.data["members"])
                self.save_data()
                return True, f"Removed @{username}"
        return False, "Member not found"
        
    def share_post(self, username, post_url, platform):
        """Share a post with the pod for engagement"""
        # Check if member
        member = None
        for m in self.data["members"]:
            if m["username"] == username:
                member = m
                break
                
        if not member:
            return False, "Not a pod member"
            
        post = {
            "id": len(self.data["posts"]) + 1,
            "username": username,
            "post_url": post_url,
            "platform": platform,
            "shared_at": datetime.now().isoformat(),
            "engagements": [],
            "status": "pending"
        }
        
        self.data["posts"].append(post)
        
        # Update member stats
        member["posts_shared"] += 1
        member["last_active"] = datetime.now().isoformat()
        self.save_data()
        
        return True, f"Post shared with pod"
        
    def log_engagement(self, post_id, username, engagement_type):
        """Log an engagement action"""
        post = None
        for p in self.data["posts"]:
            if p["id"] == post_id:
                post = p
                break
                
        if not post:
            return False, "Post not found"
            
        engagement = {
            "username": username,
            "type": engagement_type,
            "timestamp": datetime.now().isoformat()
        }
        
        post["engagements"].append(engagement)
        
        # Update member stats
        for member in self.data["members"]:
            if member["username"] == username:
                member["engagement_given"] += 1
                member["last_active"] = datetime.now().isoformat()
                
        # Update post author stats
        for member in self.data["members"]:
            if member["username"] == post["username"]:
                member["engagement_received"] += 1
                
        self.data["engagement_log"].append(engagement)
        self.data["stats"]["total_engagements"] += 1
        
        # Check if post has enough engagement
        if len(post["engagements"]) >= self.data["rules"]["min_engagement_per_day"]:
            post["status"] = "completed"
            
        self.save_data()
        
        return True, f"Engagement logged for post {post_id}"
        
    def get_pending_posts(self):
        """Get posts that need engagement"""
        return [p for p in self.data["posts"] if p["status"] == "pending"]
        
    def get_member_stats(self):
        """Get stats for all members"""
        stats = []
        for member in self.data["members"]:
            ratio = 0
            if member["posts_shared"] > 0:
                ratio = member["engagement_received"] / member["posts_shared"]
                
            stats.append({
                "username": member["username"],
                "platform": member["platform"],
                "posts_shared": member["posts_shared"],
                "engagement_given": member["engagement_given"],
                "engagement_received": member["engagement_received"],
                "engagement_ratio": round(ratio, 2),
                "last_active": member["last_active"]
            })
        return stats
        
    def get_pod_health(self):
        """Get overall pod health"""
        active_members = len([
            m for m in self.data["members"]
            if (datetime.now() - datetime.fromisoformat(m["last_active"])).days < 7
        ])
        
        pending = len(self.get_pending_posts())
        
        return {
            "total_members": len(self.data["members"]),
            "active_members": active_members,
            "pending_posts": pending,
            "total_engagements": self.data["stats"]["total_engagements"]
        }
        
    def generate_report(self):
        """Generate pod report"""
        health = self.get_pod_health()
        members = self.get_member_stats()
        
        report = "🤝 **Engagement Pod Report**\n\n"
        
        report += f"**📊 Pod Health:**\n"
        report += f"  Members: {health['total_members']}\n"
        report += f"  Active: {health['active_members']}\n"
        report += f"  Pending Posts: {health['pending_posts']}\n"
        report += f"  Total Engagements: {health['total_engagements']}\n\n"
        
        if members:
            report += "**👥 Member Stats:**\n"
            for m in members:
                ratio_emoji = "🔥" if m["engagement_ratio"] > 1 else "🟡" if m["engagement_ratio"] > 0.5 else "⚠️"
                report += f"  {ratio_emoji} @{m['username']}: {m['engagement_given']} given / {m['engagement_received']} received\n"
                
        return report
        
    # AI/Niche specific pod members (simulated)
    def suggest_pod_members(self, niche="ai"):
        """Suggest potential pod members based on niche"""
        suggestions = {
            "ai": [
                {"username": "tech_ai_creator", "platform": "tiktok", "followers": "10K"},
                {"username": "ai_explained", "platform": "tiktok", "followers": "5K"},
                {"username": "automation_daily", "platform": "tiktok", "followers": "8K"},
                {"username": "future_tech_ai", "platform": "youtube", "subscribers": "15K"},
                {"username": "ai_journey", "platform": "instagram", "followers": "3K"}
            ],
            "business": [
                {"username": "startup_stories", "platform": "tiktok", "followers": "20K"},
                {"username": "sidehustle_king", "platform": "tiktok", "followers": "15K"},
                {"username": "business_tips_daily", "platform": "youtube", "subscribers": "50K"}
            ]
        }
        
        return suggestions.get(niche, suggestions["ai"])

if __name__ == "__main__":
    pod = EngagementPod()
    
    print("🤝 **Engagement Pod System**\n")
    
    # Show current status
    print(pod.generate_report())
    
    print("\n" + "="*50)
    print("\n📋 **Suggested Pod Members (AI Niche):**\n")
    
    suggestions = pod.suggest_pod_members("ai")
    for s in suggestions:
        print(f"  @{s['username']} ({s['platform']} - {s['followers']})")
