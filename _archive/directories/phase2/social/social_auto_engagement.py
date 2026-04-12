#!/usr/bin/env python3
"""
Social Media Auto-Engagement System - REAL API VERSION
Actually engages with Twitter using the API
"""

import json
import os
import random
from datetime import datetime

ENGAGEMENT_LOG = "/home/clawbot/.openclaw/logs/engagement.json"
CONFIG_FILE = "/home/clawbot/.openclaw/workspace/memory/social_config.json"
ENGAGEMENT_CONFIG = "/home/clawbot/.openclaw/workspace/memory/engagement_config.json"

class AutoEngagement:
    def __init__(self):
        self.load_config()
        self.load_log()
        
    def load_config(self):
        # Load Twitter config
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            self.twitter = config.get("twitter", {})
            
        # Load engagement settings (for ban status)
        with open(ENGAGEMENT_CONFIG, 'r') as f:
            eng_config = json.load(f)
            self.ban_active = eng_config.get("ban_status", {}).get("active", False)
            self.auto_follow = eng_config.get("twitter", {}).get("auto_follow", False)
            self.auto_like = eng_config.get("twitter", {}).get("auto_like", False)
            
    def load_log(self):
        if os.path.exists(ENGAGEMENT_LOG):
            with open(ENGAGEMENT_LOG, 'r') as f:
                self.log = json.load(f)
        else:
            self.log = {
                "likes": [],
                "follows": [],
                "unfollows": [],
                "comments": []
            }
            
    def save_log(self):
        with open(ENGAGEMENT_LOG, 'w') as f:
            json.dump(self.log, f, indent=2)
            
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
        return oauth, requests
            
    def can_do_action(self, action_type):
        """Check if we can perform action (rate limits)"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        limits = {
            "like": 50,
            "follow": 20,
            "unfollow": 20,
            "comment": 10
        }
        
        today_actions = [
            e for e in self.log.get(action_type + "s", [])
            if e.get("date") == today
        ]
        
        return len(today_actions) < limits.get(action_type, 10), len(today_actions), limits.get(action_type, 10)
        
    def get_target_tweets(self, hashtag, count=10):
        """Get recent tweets with a hashtag"""
        import requests
        from requests_oauthlib import OAuth1
        
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        
        # Search for tweets
        url = f"https://api.twitter.com/2/tweets/search/recent?query={hashtag}&max_results={count}"
        
        try:
            r = requests.get(url, auth=oauth, timeout=10)
            if r.status_code == 200:
                data = r.json()
                return data.get("data", [])
        except:
            pass
        return []
        
    def get_my_user_id(self):
        """Get authenticated user's ID"""
        from requests_oauthlib import OAuth1
        import requests
        
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        
        url = "https://api.twitter.com/2/users/me"
        r = requests.get(url, auth=oauth, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", {}).get("id")
        return None
        
    def get_user_id(self, username):
        """Get user ID from username"""
        from requests_oauthlib import OAuth1
        import requests
        
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        r = requests.get(url, auth=oauth, timeout=10)
        if r.status_code == 200:
            return r.json().get("data", {}).get("id")
        return None
        
    def like_tweet(self, tweet_id):
        """Like a tweet"""
        can_do, count, limit = self.can_do_action("like")
        if not can_do:
            return {"success": False, "reason": "limit_reached"}
            
        from requests_oauthlib import OAuth1
        import requests
        
        my_id = self.get_my_user_id()
        if not my_id:
            return {"success": False, "error": "no_user_id"}
            
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        
        url = f"https://api.twitter.com/2/users/{my_id}/likes"
        payload = {"tweet_id": str(tweet_id)}
        
        try:
            r = requests.post(url, auth=oauth, json=payload, timeout=10)
            if r.status_code == 200:
                self.log["likes"].append({
                    "tweet_id": tweet_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "timestamp": datetime.now().isoformat()
                })
                self.save_log()
                return {"success": True, "tweet_id": tweet_id}
            else:
                return {"success": False, "error": r.text[:100]}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def follow_user(self, username):
        """Follow a user"""
        can_do, count, limit = self.can_do_action("follow")
        if not can_do:
            return {"success": False, "reason": "limit_reached"}
            
        from requests_oauthlib import OAuth1
        import requests
        
        my_id = self.get_my_user_id()
        if not my_id:
            return {"success": False, "error": "no_user_id"}
            
        user_id = self.get_user_id(username)
        if not user_id:
            return {"success": False, "error": "user_not_found"}
            
        oauth = OAuth1(
            self.twitter.get("api_key", ""),
            client_secret=self.twitter.get("api_secret", ""),
            resource_owner_key=self.twitter.get("access_token", ""),
            resource_owner_secret=self.twitter.get("access_token_secret", "")
        )
        
        url = f"https://api.twitter.com/2/users/{my_id}/following"
        payload = {"target_user_id": user_id}
        
        try:
            r = requests.post(url, auth=oauth, json=payload, timeout=10)
            if r.status_code == 200:
                self.log["follows"].append({
                    "username": username,
                    "user_id": user_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "timestamp": datetime.now().isoformat()
                })
                self.save_log()
                return {"success": True, "username": username}
            else:
                return {"success": False, "error": r.text[:100]}
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    def run_engagement_cycle(self):
        """Run a complete engagement cycle"""
        print("🔄 Running REAL engagement cycle...")
        
        # Check if banned or paused
        if self.ban_active:
            print("⏸️ BANNED - Engagement paused until 2026-03-12")
            return {"error": "banned"}
            
        if not self.auto_follow and not self.auto_like:
            print("⏸️ Engagement disabled in config")
            return {"error": "disabled"}
            
        results = {"likes": 0, "follows": 0, "errors": []}
        
        # Target hashtags
        hashtags = ["#AI", "#Automation", "#Tech", "#Startup", "#Innovation", "#Entrepreneur"]
        
        # Try to like some tweets
        for hashtag in hashtags[:3]:
            can_do, count, limit = self.can_do_action("like")
            if not can_do:
                break
                
            tweets = self.get_target_tweets(hashtag, 5)
            for tweet in tweets[:2]:
                result = self.like_tweet(tweet.get("id"))
                if result.get("success"):
                    print(f"  ✅ Liked tweet: {tweet.get('id')}")
                    results["likes"] += 1
                else:
                    results["errors"].append(result.get("error", "unknown"))
                    
        # Target users to follow
        target_users = ["elonmusk", "sama", "AndrewYNg", "GaryVee", "levelsio", "swyx"]
        
        for username in target_users[:2]:
            can_do, count, limit = self.can_do_action("follow")
            if not can_do:
                break
                
            result = self.follow_user(username)
            if result.get("success"):
                print(f"  ✅ Followed: @{username}")
                results["follows"] += 1
            else:
                results["errors"].append(result.get("error", "unknown"))
                
        print(f"\n📊 Results: +{results['likes']} likes, +{results['follows']} follows")
        
        return results
        
    def get_stats(self):
        """Get engagement stats"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        stats = {}
        for platform in ["twitter", "instagram", "facebook"]:
            likes = len([e for e in self.log.get("likes", []) if e.get("date") == today])
            follows = len([e for e in self.log.get("follows", []) if e.get("date") == today])
            stats[platform] = {"likes": likes, "follows": follows}
            
        return stats

if __name__ == "__main__":
    engagement = AutoEngagement()
    engagement.run_engagement_cycle()
