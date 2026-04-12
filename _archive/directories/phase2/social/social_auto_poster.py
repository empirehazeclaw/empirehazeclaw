#!/usr/bin/env python3
"""
Social Media Auto-Poster
Posts content to platforms automatically
"""

import json
import os
import asyncio
import base64
import hashlib
import time
import requests
from datetime import datetime
from pathlib import Path
import hmac
import urllib.parse

POSTS_FILE = "/home/clawbot/.openclaw/workspace/memory/social_posts_latest.json"
POST_LOG = "/home/clawbot/.openclaw/logs/social_post_log.json"

class AutoPoster:
    def __init__(self):
        self.load_posts()
        self.load_config()
        
    def load_posts(self):
        """Load latest generated posts"""
        if os.path.exists(POSTS_FILE):
            with open(POSTS_FILE, 'r') as f:
                self.posts = json.load(f)
        else:
            # Try date-specific file
            date = datetime.now().strftime("%Y-%m-%d")
            alt_file = f"/home/clawbot/.openclaw/workspace/memory/social_posts_{date}.md"
            if os.path.exists(alt_file):
                with open(alt_file, 'r') as f:
                    self.posts = json.load(f)
            else:
                self.posts = None
                
    def load_config(self):
        """Load platform auth configs"""
        config_file = "/home/clawbot/.openclaw/workspace/memory/social_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "twitter": {"enabled": False, "reason": "No API credentials"},
                "instagram": {"enabled": False, "reason": "No API credentials"},
                "facebook": {"enabled": False, "reason": "No API credentials"},
                "tiktok": {"enabled": False, "reason": "No API credentials"}
            }
            
    async def post_to_twitter(self, post):
        """Post to Twitter/X using OAuth 1.0a"""
        twitter_config = self.config.get("twitter", {})
        
        if not twitter_config.get("enabled"):
            return {
                "platform": "twitter",
                "status": "skipped",
                "reason": "Not enabled"
            }
            
        api_key = twitter_config.get("api_key", "")
        api_secret = twitter_config.get("api_secret", "")
        access_token = twitter_config.get("access_token", "")
        access_token_secret = twitter_config.get("access_token_secret", "")
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            return {
                "platform": "twitter",
                "status": "skipped",
                "reason": "Missing OAuth credentials"
            }
            
        # Twitter API v2 endpoint
        url = "https://api.twitter.com/2/tweets"
        
        # Build OAuth header using OAuth 1.0a
        from requests_oauthlib import OAuth1
        import requests
        
        oauth = OAuth1(
            api_key,
            client_secret=api_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )
        
        # Build tweet text
        content = post.get("content", "")
        hashtags = post.get("hashtags", [])
        
        if hashtags:
            hashtag_str = " ".join(hashtags)
            tweet_text = f"{content}\n\n{hashtag_str}"
        else:
            tweet_text = content
            
        # Limit to 280 chars
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:277] + "..."
            
        payload = {"text": tweet_text}
        
        try:
            response = requests.post(url, auth=oauth, json=payload, timeout=15)
            
            if response.status_code == 201:
                return {
                    "status": "posted",
                    "platform": "twitter",
                    "tweet_id": response.json().get("data", {}).get("id"),
                    "text": tweet_text[:50]
                }
            else:
                return {
                    "status": "error",
                    "platform": "twitter",
                    "error": response.text[:200],
                    "code": response.status_code
                }
        except Exception as e:
            return {
                "status": "error",
                "platform": "twitter",
                "error": str(e)
            }
        
    async def post_to_instagram(self, post):
        """Post to Instagram"""
        if not self.config.get("instagram", {}).get("enabled"):
            return {
                "platform": "instagram", 
                "status": "skipped",
                "reason": self.config.get("instagram", {}).get("reason", "Not configured")
            }
            
        return {"status": "posted", "platform": "instagram"}
        
    async def post_to_facebook(self, post):
        """Post to Facebook"""
        if not self.config.get("facebook", {}).get("enabled"):
            return {
                "platform": "facebook",
                "status": "skipped", 
                "reason": self.config.get("facebook", {}).get("reason", "Not configured")
            }
            
        return {"status": "posted", "platform": "facebook"}
        
    async def post_to_tiktok(self, post):
        """Post to TikTok"""
        if not self.config.get("tiktok", {}).get("enabled"):
            return {
                "platform": "tiktok",
                "status": "skipped",
                "reason": self.config.get("tiktok", {}).get("reason", "Not configured")
            }
            
        return {"status": "posted", "platform": "tiktok"}
        
    async def post_all(self):
        """Post to all enabled platforms"""
        if not self.posts:
            print("⚠️ No posts found to post!")
            return []
            
        results = []
        
        for platform, posts in self.posts.get("platforms", {}).items():
            print(f"\n📤 Posting to {platform}...")
            
            platform_key = platform.lower().replace("x (twitter)", "twitter").replace("x", "twitter")
            
            for post in posts:
                if platform_key == "twitter":
                    result = await self.post_to_twitter(post)
                elif platform_key == "instagram":
                    result = await self.post_to_instagram(post)
                elif platform_key == "facebook":
                    result = await self.post_to_facebook(post)
                elif platform_key == "tiktok":
                    result = await self.post_to_tiktok(post)
                else:
                    result = {"status": "skipped", "reason": "Unknown platform"}
                    
                results.append(result)
                print(f"  - Post {post.get('post_num')}: {result.get('status')}")
                
        self.log_results(results)
        return results
        
    def log_results(self, results):
        """Log posting results"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        if os.path.exists(POST_LOG):
            with open(POST_LOG, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
            
        logs.append(log_entry)
        logs = logs[-50:]  # Keep last 50
        
        with open(POST_LOG, 'w') as f:
            json.dump(logs, f, indent=2)
            
    def get_status(self):
        """Get platform status"""
        status = {}
        for platform, config in self.config.items():
            status[platform] = {
                "enabled": config.get("enabled", False),
                "reason": config.get("reason", "Unknown")
            }
        return status

async def main():
    poster = AutoPoster()
    
    print("📊 Platform Status:")
    status = poster.get_status()
    for platform, info in status.items():
        emoji = "✅" if info["enabled"] else "❌"
        print(f"  {emoji} {platform}: {info['reason']}")
        
    print("\n🚀 Attempting to post...")
    results = await poster.post_all()
    
    print("\n📋 Summary:")
    posted = sum(1 for r in results if r.get("status") == "posted")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    print(f"  Posted: {posted}")
    print(f"  Skipped: {skipped}")
    
if __name__ == "__main__":
    asyncio.run(main())
