#!/usr/bin/env python3
"""
Reddit API Automation for AI Companion
Usage: python3 reddit_poster.py --post --title "Title" --content "Body"
"""

import os
import json
import requests
import argparse
from datetime import datetime

# Reddit API Credentials (set via environment variables)
CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
USER_AGENT = 'AICompanion/1.0'
USERNAME = os.environ.get('REDDIT_USERNAME', '')
PASSWORD = os.environ.get('REDDIT_PASSWORD', '')

# Relevant Subreddits for German AI/App market
SUBREDDITS = [
    'de',           # Germany general
    'de_tech',      # German tech
    'de_startup',   # German startups
    'ArtificialIntelligence',  # AI general
    'Chatbot',      # Chatbots
    'AICompanion',   # If exists
]

class RedditPoster:
    def __init__(self):
        self.access_token = None
        self.headers = {'User-Agent': USER_AGENT}
    
    def authenticate(self):
        """Authenticate with Reddit API"""
        if not CLIENT_ID or not CLIENT_SECRET:
            print("⚠️ No credentials - using demo mode")
            return False
        
        auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
        data = {
            'grant_type': 'password',
            'username': USERNAME,
            'password': PASSWORD
        }
        
        try:
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=self.headers
            )
            self.access_token = response.json().get('access_token')
            self.headers['Authorization'] = f'Bearer {self.access_token}'
            print("✅ Authenticated!")
            return True
        except Exception as e:
            print(f"❌ Auth failed: {e}")
            return False
    
    def post_to_subreddit(self, subreddit, title, content, flair_id=None):
        """Post a submission to a subreddit"""
        url = f'https://www.reddit.com/r/{subreddit}/api/submit'
        data = {
            'sr': subreddit,
            'kind': 'self',
            'title': title,
            'text': content,
            'api_type': 'json'
        }
        
        if flair_id:
            data['flair_id'] = flair_id
        
        try:
            response = requests.post(url, headers=self.headers, data=data)
            result = response.json()
            
            if 'json' in result and 'data' in result['json']:
                permalink = result['json']['data']['url']
                print(f"✅ Posted to r/{subreddit}")
                return permalink
            else:
                print(f"❌ Failed: {result}")
                return None
        except Exception as e:
            print(f"❌ Error posting to r/{subreddit}: {e}")
            return None
    
    def search_subreddits(self, query):
        """Search for subreddits"""
        url = 'https://www.reddit.com/subreddits/search.json'
        params = {'q': query, 'limit': 10}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            results = response.json()
            
            subs = []
            for child in results['data']['children']:
                data = child['data']
                subs.append({
                    'name': data['display_name'],
                    'subscribers': data['subscribers'],
                    'title': data['title']
                })
            return subs
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_my_posts(self, limit=10):
        """Get your recent posts"""
        url = 'https://www.reddit.com/user/me/submitted.json'
        params = {'limit': limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            return response.json()['data']['children']
        except:
            return []


# Pre-written posts for AI Companion Launch
LAUNCH_POSTS = [
    {
        'subreddit': 'de',
        'title': '🇩🇪 Mein KI Begleiter - Endlich auf Deutsch!',
        'content': '''Hallo liebe Community!

Ich habe eine AI Companion App entwickelt - endlich auf Deutsch! 🇩🇪

Was sie kann:
💬 Intelligente Konversationen
🎙️ Sprachausgabe
🧠 Erinnert sich an dich
🎮 Minigames
🎁 Daily Rewards

Preise:
🆓 Free: 100 Nachrichten/Tag
⭐ Premium: €5/Monat
🚀 Pro: €15/Monat

Der Clou: Günstiger als Re,plika & Co aber mit allen Features!

Würde mich über Feedback freuen! 😊

Link: [YOUR_URL]

#KI #ArtificialIntelligence #App #German #Deutschland'''
    },
    {
        'subreddit': 'de_tech',
        'title': 'KI Companion App - Alternative zu Replika',
        'content': '''Servus!

Hab eine eigene AI Companion App gebaut - als günstigere Alternative zu Replika & Character AI.

Features:
- Chat mit KI
- Voice Messages
- Memory System
- Gamification
- Analytics

Warum anders:
- Deutschsprachig 🇩🇪
- Günstiger (€5 vs $15)
- PWA (kein App Store nötig)

Bin gespannt auf eure Meinungen!

#Tech #AI #Startup'''
    },
    {
        'subreddit': 'ArtificialIntelligence',
        'title': 'Built a German AI Companion App - Feedback wanted!',
        'content': '''Hey everyone!

I built an AI Companion app focused on the German market.

Why:
- German language support
- Cheaper than competitors (€5/month vs $15)
- All-in-one PWA

Features:
- Chat, Voice, Memory
- Gamification
- Rewards system

Would love some feedback from the community!

#AI #German #Startup #App'''
    },
]


def main():
    parser = argparse.ArgumentParser(description='Reddit API Automation')
    parser.add_argument('--auth', action='store_true', help='Authenticate')
    parser.add_argument('--post', action='store_true', help='Post to subreddits')
    parser.add_argument('--search', type=str, help='Search subreddits')
    parser.add_argument('--title', type=str, help='Post title')
    parser.add_argument('--content', type=str, help='Post content')
    parser.add_argument('--subreddit', type=str, default='de', help='Subreddit')
    
    args = parser.parse_args()
    
    reddit = RedditPoster()
    
    if args.auth:
        reddit.authenticate()
    
    if args.search:
        results = reddit.search_subreddits(args.search)
        print(f"\n📋 Found {len(results)} subreddits:")
        for sub in results:
            print(f"  r/{sub['name']} - {sub['subscribers']} members")
    
    if args.post:
        if not reddit.authenticate():
            print("⚠️ Running in demo mode")
        
        # Post to multiple subreddits
        for post in LAUNCH_POSTS:
            print(f"\n📤 Posting to r/{post['subreddit']}...")
            reddit.post_to_subreddit(
                post['subreddit'],
                post['title'],
                post['content']
            )


if __name__ == '__main__':
    main()
