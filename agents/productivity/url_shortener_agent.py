#!/usr/bin/env python3
"""
URL Shortener Agent - Productivity Division
Creates short URLs and manages link tracking.

Inspired by SOUL.md: CEO mindset, Ressourceneffizienz, Integrität
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
import random
import string

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE = SCRIPT_DIR.parent.parent.parent
LOG_DIR = WORKSPACE / "logs"
DATA_DIR = WORKSPACE / "data" / "productivity"
LINKS_FILE = DATA_DIR / "shortlinks.json"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - URL-SHORTENER - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "url_shortener.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "https://empirehazeclaw.info/r/"  # Default base URL for shortened links


def load_links():
    """Load links from JSON file."""
    if not LINKS_FILE.exists():
        return {"links": [], "settings": {"base_url": BASE_URL}, "version": "1.0"}
    try:
        with open(LINKS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse links file: {e}")
        return {"links": [], "settings": {"base_url": BASE_URL}, "version": "1.0"}


def save_links(data):
    """Save links to JSON file."""
    try:
        with open(LINKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data['links'])} links to {LINKS_FILE}")
    except IOError as e:
        logger.error(f"Failed to save links: {e}")
        raise


def generate_short_code(length=6, method='random'):
    """Generate a short code for the URL."""
    if method == 'hash':
        # Use MD5 hash of timestamp + random
        raw = f"{datetime.now().isoformat()}{random.random()}"
        return hashlib.md5(raw.encode()).hexdigest()[:length]
    else:
        # Random alphanumeric
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))


def validate_url(url):
    """Validate URL format."""
    if not url:
        return False
    if not url.startswith(('http://', 'https://', 'ftp://')):
        url = 'https://' + url
    return True


def shorten_url(long_url, custom_code=None, title=None, tags=None):
    """Create a shortened URL."""
    data = load_links()
    
    # Validate URL
    if not long_url.startswith(('http://', 'https://', 'ftp://')):
        long_url = 'https://' + long_url
    
    # Check for existing URL
    for link in data['links']:
        if link['long_url'] == long_url and not custom_code:
            logger.info(f"URL already shortened: {link['short_code']}")
            print(f"ℹ️  URL already has a short link:")
            print(f"   {data['settings']['base_url']}{link['short_code']}")
            return link['short_code']
    
    # Use custom code if provided
    if custom_code:
        # Check if custom code exists
        for link in data['links']:
            if link['short_code'] == custom_code:
                print(f"❌ Custom code '{custom_code}' already in use.")
                return None
        short_code = custom_code
    else:
        # Generate new code
        short_code = generate_short_code()
        # Ensure uniqueness
        while any(link['short_code'] == short_code for link in data['links']):
            short_code = generate_short_code()
    
    new_link = {
        "id": len(data['links']) + 1,
        "short_code": short_code,
        "long_url": long_url,
        "title": title or long_url[:50],
        "tags": tags or [],
        "clicks": 0,
        "created_at": datetime.now().isoformat(),
        "last_clicked": None,
        "active": True
    }
    
    data['links'].append(new_link)
    save_links(data)
    
    short_url = f"{data['settings']['base_url']}{short_code}"
    logger.info(f"Created short URL: {short_url} -> {long_url}")
    print(f"✅ Short URL created:")
    print(f"   Short: {short_url}")
    print(f"   Long:  {long_url}")
    
    return short_code


def list_links(tag_filter=None, active_filter=None):
    """List all shortened links."""
    data = load_links()
    links = data['links']
    
    if tag_filter:
        links = [l for l in links if tag_filter in l.get('tags', [])]
    
    if active_filter is not None:
        links = [l for l in links if l.get('active', True) == active_filter]
    
    if not links:
        print("📭 No links found.")
        return
    
    print(f"\n🔗 Shortened Links ({len(links)} total):")
    print("-" * 90)
    for link in sorted(links, key=lambda x: x.get('created_at', ''), reverse=True):
        status = "🟢" if link.get('active', True) else "🔴"
        short_url = f"{data['settings']['base_url']}{link['short_code']}"
        print(f"{status} [{link['id']}] {short_url}")
        print(f"   Title: {link.get('title', 'N/A')}")
        print(f"   Clicks: {link.get('clicks', 0)} | Created: {link.get('created_at', 'N/A')[:10]}")
        if link.get('tags'):
            print(f"   Tags: {', '.join(link['tags'])}")
        print()


def get_link(short_code):
    """Get a link by short code."""
    data = load_links()
    for link in data['links']:
        if link['short_code'] == short_code:
            return link
    return None


def show_link(short_code):
    """Display link details."""
    link = get_link(short_code)
    if not link:
        print(f"❌ Link with code '{short_code}' not found.")
        return
    
    data = load_links()
    short_url = f"{data['settings']['base_url']}{link['short_code']}"
    
    print(f"\n🔗 Link Details:")
    print("=" * 60)
    print(f"ID:           {link['id']}")
    print(f"Short URL:    {short_url}")
    print(f"Long URL:     {link['long_url']}")
    print(f"Title:        {link.get('title', 'N/A')}")
    print(f"Status:       {'Active 🟢' if link.get('active', True) else 'Inactive 🔴'}")
    print(f"Clicks:       {link.get('clicks', 0)}")
    print(f"Created:      {link.get('created_at', 'N/A')}")
    print(f"Last Clicked: {link.get('last_clicked', 'Never')}")
    if link.get('tags'):
        print(f"Tags:         {', '.join(link['tags'])}")


def resolve_url(short_code):
    """Resolve a short URL to its long URL (simulate redirect)."""
    link = get_link(short_code)
    if not link:
        print(f"❌ Link not found.")
        return None
    
    if not link.get('active', True):
        print(f"⚠️  Link is inactive.")
        return None
    
    # Update click count
    data = load_links()
    for l in data['links']:
        if l['short_code'] == short_code:
            l['clicks'] = l.get('clicks', 0) + 1
            l['last_clicked'] = datetime.now().isoformat()
            break
    save_links(data)
    
    logger.info(f"Resolved {short_code} -> {link['long_url']} (click #{link.get('clicks', 0)})")
    print(f"🔗 Redirecting to: {link['long_url']}")
    return link['long_url']


def update_link(short_code, **kwargs):
    """Update link properties."""
    data = load_links()
    
    for link in data['links']:
        if link['short_code'] == short_code:
            for key, value in kwargs.items():
                if key in ['title', 'tags', 'active']:
                    link[key] = value
            save_links(data)
            logger.info(f"Updated link {short_code}: {kwargs}")
            print(f"✅ Updated link {short_code}")
            return True
    
    print(f"❌ Link with code '{short_code}' not found.")
    return False


def delete_link(short_code):
    """Delete a link (soft delete by setting inactive)."""
    return update_link(short_code, active=False)


def hard_delete_link(short_code):
    """Permanently delete a link."""
    data = load_links()
    
    for i, link in enumerate(data['links']):
        if link['short_code'] == short_code:
            data['links'].pop(i)
            save_links(data)
            logger.info(f"Deleted link {short_code}")
            print(f"✅ Permanently deleted link {short_code}")
            return True
    
    print(f"❌ Link with code '{short_code}' not found.")
    return False


def add_tag(short_code, tag):
    """Add a tag to a link."""
    data = load_links()
    
    for link in data['links']:
        if link['short_code'] == short_code:
            tags = link.get('tags', [])
            if tag not in tags:
                tags.append(tag)
                link['tags'] = tags
                save_links(data)
                logger.info(f"Added tag '{tag}' to link {short_code}")
                print(f"✅ Added tag '{tag}' to link {short_code}")
            else:
                print(f"ℹ️  Tag '{tag}' already exists.")
            return True
    
    print(f"❌ Link with code '{short_code}' not found.")
    return False


def click_stats(short_code=None):
    """Show click statistics."""
    data = load_links()
    
    if short_code:
        link = get_link(short_code)
        if not link:
            print(f"❌ Link not found.")
            return
        print(f"\n📊 Click Stats for {short_code}:")
        print("=" * 40)
        print(f"Total Clicks:    {link.get('clicks', 0)}")
        print(f"Last Clicked:    {link.get('last_clicked', 'Never')}")
        return
    
    total_links = len(data['links'])
    active_links = len([l for l in data['links'] if l.get('active', True)])
    total_clicks = sum(l.get('clicks', 0) for l in data['links'])
    
    # Top clicked links
    top_links = sorted(data['links'], key=lambda x: x.get('clicks', 0), reverse=True)[:5]
    
    print(f"\n📊 URL Shortener Statistics:")
    print("=" * 40)
    print(f"Total Links:     {total_links}")
    print(f"Active Links:    {active_links} 🟢")
    print(f"Inactive Links:  {total_links - active_links} 🔴")
    print(f"Total Clicks:    {total_clicks}")
    
    if total_links > 0:
        avg_clicks = total_clicks / total_links
        print(f"Avg Clicks:      {avg_clicks:.1f}")
    
    if top_links:
        print(f"\n🏆 Top 5 Links by Clicks:")
        for i, link in enumerate(top_links, 1):
            print(f"  {i}. {link['short_code']}: {link.get('clicks', 0)} clicks")


def bulk_shorten(urls_file):
    """Bulk shorten URLs from a file."""
    try:
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except IOError as e:
        logger.error(f"Failed to read file: {e}")
        print(f"❌ Error reading file: {e}")
        return
    
    print(f"📦 Bulk shortening {len(urls)} URLs...")
    results = []
    for url in urls:
        code = shorten_url(url)
        if code:
            results.append(code)
    
    print(f"\n✅ Created {len(results)} short links.")
    return results


def main():
    parser = argparse.ArgumentParser(
        description="URL Shortener Agent - Create and manage short URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s shorten "https://example.com/very/long/url" --title "Example Site"
  %(prog)s shorten "https://empirehazeclaw.store/products" --custom "shop"
  %(prog)s list
  %(prog)s list --tag marketing
  %(prog)s show abc123
  %(prog)s resolve abc123
  %(prog)s update abc123 --title "New Title" --active true
  %(prog)s tag abc123 "important"
  %(prog)s delete abc123
  %(prog)s stats
  %(prog)s stats abc123
  %(prog)s bulk urls.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Shorten URL
    shorten_parser = subparsers.add_parser('shorten', help='Create a short URL')
    shorten_parser.add_argument('url', help='Long URL to shorten')
    shorten_parser.add_argument('--custom', '-c', help='Custom short code')
    shorten_parser.add_argument('--title', '-t', help='Title/description')
    shorten_parser.add_argument('--tag', action='append', help='Tag (can repeat)')
    
    # List links
    list_parser = subparsers.add_parser('list', help='List all shortened links')
    list_parser.add_argument('--tag', help='Filter by tag')
    list_parser.add_argument('--active', type=lambda x: x.lower() == 'true',
                            help='Filter by active status (true/false)')
    
    # Show link
    show_parser = subparsers.add_parser('show', help='Show link details')
    show_parser.add_argument('short_code', help='Short code')
    
    # Resolve/redirect
    resolve_parser = subparsers.add_parser('resolve', help='Resolve short URL (simulate redirect)')
    resolve_parser.add_argument('short_code', help='Short code')
    
    # Update link
    update_parser = subparsers.add_parser('update', help='Update link properties')
    update_parser.add_argument('short_code', help='Short code')
    update_parser.add_argument('--title', help='New title')
    update_parser.add_argument('--active', type=lambda x: x.lower() == 'true', help='Active status')
    update_parser.add_argument('--tag', action='append', help='Add tag')
    
    # Add tag
    tag_parser = subparsers.add_parser('tag', help='Add tag to link')
    tag_parser.add_argument('short_code', help='Short code')
    tag_parser.add_argument('tag', help='Tag to add')
    
    # Delete link (soft)
    delete_parser = subparsers.add_parser('delete', help='Deactivate link')
    delete_parser.add_argument('short_code', help='Short code')
    
    # Hard delete
    hard_delete_parser = subparsers.add_parser('hard-delete', help='Permanently delete link')
    hard_delete_parser.add_argument('short_code', help='Short code')
    
    # Stats
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('short_code', nargs='?', help='Show stats for specific link')
    
    # Bulk shorten
    bulk_parser = subparsers.add_parser('bulk', help='Bulk shorten URLs from file')
    bulk_parser.add_argument('file', help='File with URLs (one per line)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'shorten':
            shorten_url(args.url, args.custom, args.title, args.tag)
        
        elif args.command == 'list':
            list_links(args.tag if hasattr(args, 'tag') else None,
                      args.active if hasattr(args, 'active') else None)
        
        elif args.command == 'show':
            show_link(args.short_code)
        
        elif args.command == 'resolve':
            resolve_url(args.short_code)
        
        elif args.command == 'update':
            kwargs = {k: v for k, v in vars(args).items() 
                     if k not in ['command', 'short_code'] and v is not None}
            if kwargs:
                update_link(args.short_code, **kwargs)
            else:
                print("❌ No updates specified.")
        
        elif args.command == 'tag':
            add_tag(args.short_code, args.tag)
        
        elif args.command == 'delete':
            delete_link(args.short_code)
        
        elif args.command == 'hard-delete':
            hard_delete_link(args.short_code)
        
        elif args.command == 'stats':
            click_stats(args.short_code if hasattr(args, 'short_code') else None)
        
        elif args.command == 'bulk':
            bulk_shorten(args.file)
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
