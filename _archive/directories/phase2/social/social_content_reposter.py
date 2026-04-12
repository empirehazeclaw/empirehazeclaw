#!/usr/bin/env python3
"""
Content Reposter
Re-posts high-performing content with variations
"""

import json
import os
import random
from datetime import datetime, timedelta

REPOSTER_FILE = "/home/clawbot/.openclaw/workspace/memory/content_reposter.json"

class ContentReposter:
    def __init__(self):
        self.load_data()
        
    def load_data(self):
        if os.path.exists(REPOSTER_FILE):
            with open(REPOSTER_FILE, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "reposts": [],
                "reposted_posts": [],
                "variations_templates": {
                    "question": [
                        "What do you think about {content}?",
                        "Agree or disagree? {content}",
                        "Hot take: {content}"
                    ],
                    "update": [
                        "UPDATE: {content}",
                        "Here's an update on {content}",
                        "New developments on {content}"
                    ],
                    "reminder": [
                        "Reminder: {content}",
                        "Don't forget: {content}",
                        "PSA: {content}"
                    ],
                    "stat": [
                        "🎯 {stat}% of people agree: {content}",
                        "Fact: {content}",
                        "Did you know? {content}"
                    ]
                }
            }
            
    def save_data(self):
        with open(REPOSTER_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
            
    def generate_variation(self, content, style=None):
        """Generate a variation of the content"""
        if not style:
            style = random.choice(list(self.data["variations_templates"].keys()))
            
        template = random.choice(self.data["variations_templates"][style])
        
        # Simple variation - in production, use AI for better variations
        return template.format(content=content[:100])
        
    def can_repost(self, original_post_id):
        """Check if a post can be reposted"""
        # Don't repost within 7 days
        for repost in self.data["reposted_posts"]:
            if repost["original_id"] == original_post_id:
                posted_at = datetime.fromisoformat(repost["posted_at"])
                days_since = (datetime.now() - posted_at).days
                if days_since < 7:
                    return False
                    
        return True
        
    def create_repost(self, original_post, new_platform=None):
        """Create a repost of a high-performing post"""
        if not self.can_repost(original_post.get("id")):
            return None
            
        # Generate variation
        content = original_post.get("content", "")
        variation = self.generate_variation(content)
        
        repost = {
            "original_id": original_post.get("id"),
            "original_platform": original_post.get("platform"),
            "new_platform": new_platform or original_post.get("platform"),
            "original_content": content,
            "new_content": variation,
            "hashtags": original_post.get("hashtags", []),
            "created": datetime.now().isoformat(),
            "status": "ready"
        }
        
        self.data["reposts"].append(repost)
        self.data["reposted_posts"].append({
            "original_id": original_post.get("id"),
            "posted_at": datetime.now().isoformat()
        })
        
        self.save_data()
        return repost
        
    def get_reposts_ready(self):
        """Get all reposts ready to post"""
        return [r for r in self.data["reposts"] if r.get("status") == "ready"]
        
    def mark_repost_posted(self, repost_id):
        """Mark a repost as posted"""
        for repost in self.data["reposts"]:
            if repost.get("id") == repost_id:
                repost["status"] = "posted"
                repost["posted_at"] = datetime.now().isoformat()
                
        self.save_data()
        
    def suggest_reposts(self, analytics_data):
        """Suggest posts that should be reposted"""
        suggestions = []
        
        # Find high-performing posts
        for post in analytics_data.get("posts", []):
            engagement = (
                post.get("metrics", {}).get("likes", 0) +
                post.get("metrics", {}).get("comments", 0) * 2 +
                post.get("metrics", {}).get("shares", 0) * 3
            )
            
            if engagement > 10:  # Threshold for "high performing"
                if self.can_repost(post.get("id")):
                    suggestions.append({
                        "post": post,
                        "engagement": engagement,
                        "reasons": []
                    })
                    
        return suggestions
        
    def generate_report(self):
        """Generate reposter report"""
        report = "🔄 **Content Reposter Report**\n\n"
        
        ready = self.get_reposts_ready()
        report += f"**📝 Reposts Ready:** {len(ready)}\n"
        
        if ready:
            report += "\n**Ready to post:**\n"
            for repost in ready[:3]:
                report += f"  - {repost['new_content'][:50]}...\n"
                
        report += f"\n**📊 Total Reposts:** {len(self.data['reposts'])}\n"
        
        return report
        
    def simulate(self):
        """Simulate some reposts"""
        # Create sample posts to repost
        sample_posts = [
            {
                "id": 1,
                "platform": "twitter",
                "content": "AI will change everything about business",
                "hashtags": ["#AI", "#Business"],
                "metrics": {"likes": 50, "comments": 10, "shares": 5}
            },
            {
                "id": 2,
                "platform": "instagram", 
                "content": "Automation is the future of work",
                "hashtags": ["#Automation", "#Future"],
                "metrics": {"likes": 30, "comments": 5, "shares": 2}
            }
        ]
        
        for post in sample_posts:
            if self.can_repost(post["id"]):
                repost = self.create_repost(post)
                if repost:
                    print(f"Created repost: {repost['new_content']}")
                    
        print(self.generate_report())

if __name__ == "__main__":
    reposter = ContentReposter()
    reposter.simulate()
