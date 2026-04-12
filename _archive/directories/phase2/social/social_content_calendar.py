#!/usr/bin/env python3
"""
Social Media Content Calendar
Plans and schedules content for the week
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

CALENDAR_FILE = "/home/clawbot/.openclaw/workspace/memory/content_calendar.json"

class ContentCalendar:
    def __init__(self):
        self.load_calendar()
        
    def load_calendar(self):
        if os.path.exists(CALENDAR_FILE):
            with open(CALENDAR_FILE, 'r') as f:
                self.calendar = json.load(f)
        else:
            self.calendar = {
                "week_start": self.get_week_start(),
                "posts": [],
                "themes": {}
            }
            
    def get_week_start(self):
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        return monday.strftime("%Y-%m-%d")
        
    def save_calendar(self):
        with open(CALENDAR_FILE, 'w') as f:
            json.dump(self.calendar, f, indent=2)
            
    def add_post(self, day, platform, content, time=None, status="planned"):
        post = {
            "id": len(self.calendar["posts"]) + 1,
            "day": day,
            "platform": platform,
            "content": content[:200] if len(content) > 200 else content,
            "time": time or self.get_best_time(platform),
            "status": status,
            "created": datetime.now().isoformat()
        }
        self.calendar["posts"].append(post)
        self.save_calendar()
        return post
        
    def get_best_time(self, platform):
        """Get best posting time based on platform"""
        times = {
            "tiktok": "19:00",
            "twitter": "09:00",
            "x": "09:00",
            "instagram": "18:00",
            "facebook": "14:00"
        }
        return times.get(platform.lower(), "12:00")
        
    def get_posts_for_day(self, day):
        return [p for p in self.calendar["posts"] if p["day"] == day]
        
    def get_week_plan(self):
        """Get this week's content plan"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        plan = {}
        
        for i, day in enumerate(days):
            date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            posts = self.get_posts_for_day(date)
            if posts:
                plan[day] = posts
                
        return plan
        
    def set_theme(self, day, theme):
        """Set a theme for a day"""
        self.calendar["themes"][day] = theme
        self.save_calendar()
        
    def generate_weekly_plan(self, posts_data):
        """Auto-generate weekly plan from post ideas"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Assign posts to days
        for i, (platform, posts) in enumerate(posts_data.items()):
            day_idx = i % 7
            day = days[day_idx]
            
            for j, post in enumerate(posts[:2]):  # Max 2 posts per day
                date = (datetime.now() + timedelta(days=day_idx)).strftime("%Y-%m-%d")
                self.add_post(date, platform, post.get("content", post.get("hook", "")))
                
        self.save_calendar()
        
    def mark_posted(self, post_id):
        """Mark a post as posted"""
        for post in self.calendar["posts"]:
            if post["id"] == post_id:
                post["status"] = "posted"
                post["posted_at"] = datetime.now().isoformat()
        self.save_calendar()
        
    def get_pending_posts(self):
        """Get all pending posts"""
        return [p for p in self.calendar["posts"] if p["status"] == "planned"]
        
    def get_calendar_summary(self):
        """Get calendar summary"""
        pending = self.get_pending_posts()
        posted = len([p for p in self.calendar["posts"] if p["status"] == "posted"])
        
        summary = f"📅 **Content Calendar — Week of {self.calendar['week_start']}**\n\n"
        summary += f"📝 Planned: {len(pending)}\n"
        summary += f"✅ Posted: {posted}\n\n"
        
        plan = self.get_week_plan()
        for day, posts in plan.items():
            summary += f"**{day}:** {len(posts)} posts\n"
            
        return summary

if __name__ == "__main__":
    calendar = ContentCalendar()
    print(calendar.get_calendar_summary())
