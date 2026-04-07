#!/usr/bin/env python3
"""
Reddit Scraper - Find trends and discussions
"""
import praw
import os
import json

# Note: User needs to provide their own Reddit credentials
# Or use read-only mode for public data

def get_reddit():
    """Get Reddit instance"""
    return praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID", ""),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET", ""),
        user_agent="EmpireHazeClaw/1.0"
    )

def search_subreddit(subreddit, query, limit=10):
    """Search a subreddit"""
    reddit = get_reddit()
    results = []
    
    for post in reddit.subreddit(subreddit).search(query, limit=limit):
        results.append({
            "title": post.title,
            "url": post.url,
            "score": post.score,
            "comments": post.num_comments
        })
    
    return results

def get_hot_posts(subreddit, limit=10):
    """Get hot posts from subreddit"""
    reddit = get_reddit()
    results = []
    
    for post in reddit.subreddit(subreddit).hot(limit=limit):
        results.append({
            "title": post.title,
            "url": post.url,
            "score": post.score,
            "comments": post.num_comments
        })
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 reddit_scraper.py <subreddit> [query]")
        print("Example: python3 reddit_scraper.py technology AI")
        sys.exit(1)
    
    subreddit = sys.argv[1]
    query = sys.argv[2] if len(sys.argv) > 2 else None
    
    if query:
        results = search_subreddit(subreddit, query)
    else:
        results = get_hot_posts(subreddit)
    
    print(f"\n=== r/{subreddit} ===\n")
    for r in results:
        print(f"📌 {r['title'][:60]}...")
        print(f"   👍 {r['score']} | 💬 {r['comments']}")
        print()
