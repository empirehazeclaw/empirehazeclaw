#!/usr/bin/env python3
"""
Knowledge Base Agent - Support Operations
Manages knowledge base articles with search and categorization.
Based on SOUL.md principles: efficiency, clarity, actionable information.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "knowledge_base.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("KnowledgeBase")

DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
KB_FILE = DATA_DIR / "knowledge_base.json"

CATEGORIES = ["general", "technical", "billing", "faq", "tutorial", "troubleshooting"]


def load_kb() -> dict:
    """Load knowledge base from JSON file."""
    try:
        if KB_FILE.exists():
            with open(KB_FILE, 'r') as f:
                return json.load(f)
        return {"articles": [], "categories": CATEGORIES}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse KB JSON: {e}")
        return {"articles": [], "categories": CATEGORIES}
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
        return {"articles": [], "categories": CATEGORIES}


def save_kb(data: dict) -> bool:
    """Save knowledge base to JSON file."""
    try:
        with open(KB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save knowledge base: {e}")
        return False


def create_article(title: str, content: str, category: str = "general",
                   tags: Optional[List[str]] = None, author: str = "system") -> dict:
    """Create a new knowledge base article."""
    data = load_kb()
    article_id = len(data["articles"]) + 1
    now = datetime.utcnow().isoformat()
    
    article = {
        "id": article_id,
        "title": title,
        "content": content,
        "category": category if category in CATEGORIES else "general",
        "tags": tags or [],
        "author": author,
        "created_at": now,
        "updated_at": now,
        "views": 0,
        "helpful": 0,
        "not_helpful": 0
    }
    
    data["articles"].append(article)
    if save_kb(data):
        logger.info(f"Created article #{article_id}: {title}")
        return article
    raise Exception("Failed to save article")


def search_articles(query: str, category: Optional[str] = None, 
                    tags: Optional[List[str]] = None, limit: int = 20) -> list:
    """Search articles by query, category, or tags."""
    data = load_kb()
    results = data["articles"]
    
    if query:
        query_lower = query.lower()
        results = [a for a in results if 
                   query_lower in a["title"].lower() or 
                   query_lower in a["content"].lower()]
    
    if category:
        results = [a for a in results if a["category"] == category]
    
    if tags:
        results = [a for a in results if any(tag in a.get("tags", []) for tag in tags)]
    
    # Sort by relevance (views + helpful ratio)
    results.sort(key=lambda x: x.get("views", 0), reverse=True)
    return results[:limit]


def get_article(article_id: int) -> Optional[dict]:
    """Get a single article by ID and increment view count."""
    data = load_kb()
    for article in data["articles"]:
        if article["id"] == article_id:
            article["views"] += 1
            save_kb(data)
            return article
    return None


def update_article(article_id: int, **kwargs) -> Optional[dict]:
    """Update an article."""
    data = load_kb()
    for article in data["articles"]:
        if article["id"] == article_id:
            for key, value in kwargs.items():
                if key in ["title", "content", "category", "tags", "author"]:
                    article[key] = value
            article["updated_at"] = datetime.utcnow().isoformat()
            if save_kb(data):
                logger.info(f"Updated article #{article_id}")
                return article
            return None
    return None


def rate_article(article_id: int, helpful: bool) -> Optional[dict]:
    """Rate an article as helpful or not helpful."""
    data = load_kb()
    for article in data["articles"]:
        if article["id"] == article_id:
            if helpful:
                article["helpful"] += 1
            else:
                article["not_helpful"] += 1
            if save_kb(data):
                logger.info(f"Rated article #{article_id} as {'helpful' if helpful else 'not helpful'}")
                return article
            return None
    return None


def delete_article(article_id: int) -> bool:
    """Delete an article."""
    data = load_kb()
    original_len = len(data["articles"])
    data["articles"] = [a for a in data["articles"] if a["id"] != article_id]
    
    if len(data["articles"]) < original_len:
        if save_kb(data):
            logger.info(f"Deleted article #{article_id}")
            return True
    return False


def get_stats() -> dict:
    """Get knowledge base statistics."""
    data = load_kb()
    articles = data["articles"]
    
    stats = {
        "total": len(articles),
        "by_category": {},
        "total_views": 0,
        "total_helpful": 0,
        "avg_helpful_ratio": 0
    }
    
    for a in articles:
        stats["by_category"][a["category"]] = stats["by_category"].get(a["category"], 0) + 1
        stats["total_views"] += a.get("views", 0)
        stats["total_helpful"] += a.get("helpful", 0)
    
    if articles:
        total_ratings = sum(a.get("helpful", 0) + a.get("not_helpful", 0) for a in articles)
        if total_ratings > 0:
            stats["avg_helpful_ratio"] = round(stats["total_helpful"] / total_ratings * 100, 1)
    
    return stats


def list_categories() -> List[str]:
    """List all categories."""
    data = load_kb()
    return data.get("categories", CATEGORIES)


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Base Agent - Manage support knowledge articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --title "How to reset password" --content "Step 1: Go to settings..." --category tutorial
  %(prog)s search --query "password" --category technical
  %(prog)s get --id 1
  %(prog)s update --id 1 --title "New title"
  %(prog)s rate --id 1 --helpful
  %(prog)s delete --id 1
  %(prog)s stats
  %(prog)s categories
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create
    create_parser = subparsers.add_parser("create", help="Create a new article")
    create_parser.add_argument("--title", "-t", required=True, help="Article title")
    create_parser.add_argument("--content", "-c", required=True, help="Article content")
    create_parser.add_argument("--category", "-g", choices=CATEGORIES, default="general", help="Category")
    create_parser.add_argument("--tags", nargs="*", help="Tags (space-separated)")
    create_parser.add_argument("--author", "-a", default="system", help="Author name")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search articles")
    search_parser.add_argument("--query", "-q", help="Search query")
    search_parser.add_argument("--category", "-g", choices=CATEGORIES, help="Filter by category")
    search_parser.add_argument("--tags", nargs="*", help="Filter by tags")
    search_parser.add_argument("--limit", "-l", type=int, default=20, help="Limit results")
    
    # Get
    get_parser = subparsers.add_parser("get", help="Get article by ID")
    get_parser.add_argument("--id", "-i", type=int, required=True, help="Article ID")
    
    # Update
    update_parser = subparsers.add_parser("update", help="Update an article")
    update_parser.add_argument("--id", "-i", type=int, required=True, help="Article ID")
    update_parser.add_argument("--title", "-t", help="New title")
    update_parser.add_argument("--content", "-c", help="New content")
    update_parser.add_argument("--category", "-g", choices=CATEGORIES, help="New category")
    update_parser.add_argument("--tags", nargs="*", help="New tags")
    
    # Rate
    rate_parser = subparsers.add_parser("rate", help="Rate an article")
    rate_parser.add_argument("--id", "-i", type=int, required=True, help="Article ID")
    rate_parser.add_argument("--helpful", action="store_true", help="Mark as helpful")
    rate_parser.add_argument("--not-helpful", dest="not_helpful", action="store_true", help="Mark as not helpful")
    
    # Delete
    delete_parser = subparsers.add_parser("delete", help="Delete an article")
    delete_parser.add_argument("--id", "-i", type=int, required=True, help="Article ID")
    
    # Stats
    subparsers.add_parser("stats", help="Show knowledge base statistics")
    
    # Categories
    subparsers.add_parser("categories", help="List all categories")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    try:
        if args.command == "create":
            article = create_article(
                title=args.title,
                content=args.content,
                category=args.category,
                tags=args.tags,
                author=args.author
            )
            print(f"✅ Created article #{article['id']}: {article['title']}")
            
        elif args.command == "search":
            articles = search_articles(
                query=args.query,
                category=args.category,
                tags=args.tags,
                limit=args.limit
            )
            if not articles:
                print("No articles found.")
            else:
                print(f"Found {len(articles)} article(s):\n")
                for a in articles:
                    print(f"  #{a['id']} | {a['category']:12} | {a['title'][:50]}")
                    print(f"         Views: {a.get('views', 0)}, Helpful: {a.get('helpful', 0)}")
            
        elif args.command == "get":
            article = get_article(args.id)
            if article:
                print(f"\nArticle #{article['id']}")
                print(f"  Title: {article['title']}")
                print(f"  Category: {article['category']}")
                print(f"  Tags: {', '.join(article.get('tags', []))}")
                print(f"  Author: {article['author']}")
                print(f"  Created: {article['created_at']}")
                print(f"  Updated: {article['updated_at']}")
                print(f"  Views: {article.get('views', 0)}")
                print(f"  Helpful: {article.get('helpful', 0)} | Not helpful: {article.get('not_helpful', 0)}")
                print(f"\nContent:\n{article['content']}")
            else:
                print(f"Article #{args.id} not found.")
                return 1
                
        elif args.command == "update":
            kwargs = {k: v for k, v in vars(args).items() 
                      if k not in ['command', 'id'] and v is not None and v != []}
            article = update_article(args.id, **kwargs)
            if article:
                print(f"✅ Updated article #{article['id']}")
            else:
                print(f"Article #{args.id} not found.")
                return 1
                
        elif args.command == "rate":
            if args.helpful:
                article = rate_article(args.id, True)
                if article:
                    print(f"✅ Rated article #{article['id']} as helpful")
            elif args.not_helpful:
                article = rate_article(args.id, False)
                if article:
                    print(f"✅ Rated article #{article['id']} as not helpful")
            else:
                print("Please specify --helpful or --not-helpful")
                return 1
                
        elif args.command == "delete":
            if delete_article(args.id):
                print(f"✅ Deleted article #{args.id}")
            else:
                print(f"Article #{args.id} not found.")
                return 1
                
        elif args.command == "stats":
            stats = get_stats()
            print("\n📚 Knowledge Base Statistics")
            print(f"  Total Articles: {stats['total']}")
            print(f"  Total Views: {stats['total_views']}")
            print(f"  Avg Helpful Ratio: {stats['avg_helpful_ratio']}%")
            print("  By Category:")
            for cat, count in stats["by_category"].items():
                print(f"    {cat}: {count}")
                
        elif args.command == "categories":
            cats = list_categories()
            print("\n📂 Categories:")
            for cat in cats:
                print(f"  - {cat}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
