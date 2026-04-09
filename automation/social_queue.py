#!/usr/bin/env python3
"""
Social Media Queue - Posts from queue when API available
"""
import os
import json
from datetime import datetime

QUEUE_FILE = "/home/clawbot/.openclaw/workspace/content/ready-to-post/queue.json"
ARCHIVE_FILE = "/home/clawbot/.openclaw/workspace/content/ready-to-post/posted.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE) as f:
            return json.load(f)
    return []

def save_posted(post):
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE) as f:
            posted = json.load(f)
    else:
        posted = []
    
    post["posted_at"] = datetime.now().isoformat()
    posted.append(post)
    
    with open(ARCHIVE_FILE, 'w') as f:
        json.dump(posted, f, indent=2)

def process_queue():
    queue = load_queue()
    
    if not queue:
        print("📝 Queue is empty")
        print("Add posts to queue.json")
        return
    
    print(f"📝 Processing {len(queue)} posts...")
    
    # Note: Cannot post without API
    # This prepares the queue for when API is available
    print("\n⚠️ Twitter API required for posting")
    print("Posts ready in queue:")
    for i, post in enumerate(queue[:3], 1):
        print(f"  {i}. {post.get('platform', 'unknown')}: {post.get('text', '')[:50]}...")
    
    # For now, just show what's in queue
    return len(queue)

if __name__ == "__main__":
    process_queue()
