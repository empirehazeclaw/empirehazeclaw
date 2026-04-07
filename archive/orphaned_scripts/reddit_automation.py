#!/usr/bin/env python3
"""
Reddit Automation
⚠️ IMPORTANT: Ask before posting!
"""
import praw
import os
import json

# Reddit credentials - User needs to fill these
CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET", "")
USER_AGENT = "EmpireHazeClaw/1.0"

CONTENT_FILE = "/home/clawbot/.openclaw/workspace/content/ready-to-post/reddit_posts.json"
POSTED_FILE = "/home/clawbot/.openclaw/workspace/content/ready-to-post/reddit_posted.json"

SUBREDDITS = ["artificial", "MachineLearning", "technology", "germany", "de_reddit"]

def get_reddit():
    """Get Reddit instance"""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("⚠️ Reddit credentials not configured!")
        print("   Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        return None
    
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

def load_posts():
    """Load Reddit posts from file"""
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE) as f:
            return json.load(f)
    return []

def get_hot_posts(subreddit, limit=10):
    """Get hot posts from subreddit"""
    reddit = get_reddit()
    if not reddit:
        return []
    
    posts = []
    for post in reddit.subreddit(subreddit).hot(limit=limit):
        posts.append({
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "url": post.url
        })
    return posts

def search_posts(subreddit, query, limit=10):
    """Search posts in subreddit"""
    reddit = get_reddit()
    if not reddit:
        return []
    
    posts = []
    for post in reddit.subreddit(subreddit).search(query, limit=limit):
        posts.append({
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "url": post.url
        })
    return posts

def upvote_post(post_id):
    """Upvote a post"""
    reddit = get_reddit()
    if not reddit:
        return False
    
    try:
        reddit.submission(id=post_id).upvote()
        return True
    except:
        return False

def get_my_posts(limit=10):
    """Get your own posts"""
    reddit = get_reddit()
    if not reddit:
        return []
    
    posts = []
    for post in reddit.user.me().new(limit=limit):
        posts.append({
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "subreddit": str(post.subreddit)
        })
    return posts

# CLI
if __name__ == "__main__":
    import sys
    
    print("📕 Reddit Automation")
    print("=" * 40)
    print("")
    
    if not CLIENT_ID:
        print("❌ Reddit credentials missing!")
        print("")
        print("To set up:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create 'script' app")
        print("3. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET")
        print("")
        print(f"Current: CLIENT_ID = {CLIENT_ID or 'NOT SET'}")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Commands:")
        print("  python3 reddit_automation.py hot <subreddit>   # Get hot posts")
        print("  python3 reddit_automation.py search <query>   # Search posts")
        print("  python3 reddit_automation.py my              # Your posts")
        print("")
        print("⚠️ IMPORTANT: Ask before posting!")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "hot":
        sub = sys.argv[2] if len(sys.argv) > 2 else "technology"
        print(f"📈 Hot posts from r/{sub}:")
        for post in get_hot_posts(sub, 5):
            print(f"  👍 {post['score']} | {post['title'][:50]}...")
    
    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else "AI"
        print(f"🔍 Searching for '{query}':")
        for post in search_posts("all", query, 5):
            print(f"  👍 {post['score']} | {post['title'][:50]}...")
    
    elif cmd == "my":
        print("📝 Your recent posts:")
        for post in get_my_posts(5):
            print(f"  r/{post['subreddit']} | 👍 {post['score']} | {post['title'][:40]}...")
    
    else:
        print(f"Unknown command: {cmd}")
