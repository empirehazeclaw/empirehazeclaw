#!/usr/bin/env python3
"""
CMO Marketing Agent
==================
Manages marketing campaigns, tracks KPIs, manages content calendar,
analyzes performance, and handles multi-channel marketing.
"""

import argparse
import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CMO - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "cmo_marketing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/business")
DATA_DIR.mkdir(parents=True, exist_ok=True)
CAMPAIGNS_FILE = DATA_DIR / "campaigns.json"
CONTENT_FILE = DATA_DIR / "content_calendar.json"
CHANNELS_FILE = DATA_DIR / "channels.json"
ANALYTICS_FILE = DATA_DIR / "marketing_analytics.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not CAMPAIGNS_FILE.exists():
        save_json(CAMPAIGNS_FILE, {"campaigns": []})
    
    if not CONTENT_FILE.exists():
        save_json(CONTENT_FILE, {"items": []})
    
    if not CHANNELS_FILE.exists():
        save_json(CHANNELS_FILE, {"channels": []})
    
    if not ANALYTICS_FILE.exists():
        save_json(ANALYTICS_FILE, {
            "daily": {},
            "weekly": {},
            "monthly": {},
            "goals": {}
        })


def cmd_dashboard(args) -> int:
    """Show marketing dashboard overview."""
    logger.info("Showing marketing dashboard...")
    
    campaigns = load_json(CAMPAIGNS_FILE)
    content = load_json(CONTENT_FILE)
    channels = load_json(CHANNELS_FILE)
    analytics = load_json(ANALYTICS_FILE)
    
    active_campaigns = [c for c in campaigns.get('campaigns', []) if c.get('status') == 'active']
    scheduled_content = [c for c in content.get('items', []) if c.get('status') == 'scheduled']
    total_channels = len(channels.get('channels', []))
    
    print("\n" + "="*60)
    print("📣 CMO MARKETING DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n🚀 CAMPAIGNS")
    print(f"   Active: {len(active_campaigns)}")
    print(f"   Total: {len(campaigns.get('campaigns', []))}")
    
    if active_campaigns:
        print("\n   Active Campaigns:")
        for camp in active_campaigns[:3]:
            print(f"      📌 {camp.get('name', 'Untitled')} ({camp.get('channel', '?')})")
    
    print("\n📅 CONTENT CALENDAR")
    print(f"   Scheduled: {len(scheduled_content)}")
    print(f"   Total Items: {len(content.get('items', []))}")
    
    print("\n📡 CHANNELS")
    print(f"   Active: {total_channels}")
    if channels.get('channels'):
        for ch in channels.get('channels', [])[:3]:
            print(f"      📢 {ch.get('name', 'Unknown')} ({ch.get('platform', '?')})")
    
    print("\n📊 ANALYTICS")
    goals = analytics.get('goals', {})
    if goals:
        print(f"   Leads Goal: {goals.get('leads', 0)}")
        print(f"   Conversions Goal: {goals.get('conversions', 0)}")
    
    print("\n" + "="*60)
    return 0


def cmd_add_campaign(args) -> int:
    """Add a new marketing campaign."""
    logger.info(f"Adding campaign: {args.name}")
    
    campaigns = load_json(CAMPAIGNS_FILE)
    
    campaign = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "channel": args.channel or "general",
        "status": args.status or "planning",
        "budget": float(args.budget) if args.budget else 0,
        "start_date": args.start_date or datetime.now().strftime('%Y-%m-%d'),
        "end_date": args.end_date,
        "created_at": datetime.now().isoformat(),
        "notes": args.notes or "",
        "metrics": {
            "impressions": 0,
            "clicks": 0,
            "conversions": 0,
            "spend": 0
        }
    }
    
    campaigns['campaigns'].append(campaign)
    save_json(CAMPAIGNS_FILE, campaigns)
    
    print(f"✅ Campaign added: {args.name}")
    return 0


def cmd_list_campaigns(args) -> int:
    """List all campaigns."""
    logger.info("Listing campaigns...")
    
    campaigns = load_json(CAMPAIGNS_FILE)
    all_camps = campaigns.get('campaigns', [])
    
    if args.status:
        all_camps = [c for c in all_camps if c.get('status') == args.status]
    if args.channel:
        all_camps = [c for c in all_camps if c.get('channel') == args.channel]
    
    if not all_camps:
        print("No campaigns found.")
        return 0
    
    print(f"\n🚀 Campaigns ({len(all_camps)}):")
    print("-"*70)
    for camp in all_camps:
        status_icon = {"planning": "📝", "active": "🚀", "paused": "⏸️", "completed": "✅", "cancelled": "❌"}.get(
            camp.get('status', 'planning'), "❓")
        print(f"   {status_icon} {camp.get('name', 'Untitled')}")
        print(f"       Channel: {camp.get('channel', '?')} | Budget: ${camp.get('budget', 0)} | {camp.get('status', '?')}")
    
    return 0


def cmd_update_campaign_metrics(args) -> int:
    """Update campaign metrics."""
    logger.info(f"Updating metrics for campaign: {args.campaign_id}")
    
    campaigns = load_json(CAMPAIGNS_FILE)
    
    for camp in campaigns.get('campaigns', []):
        if camp.get('id') == args.campaign_id:
            metrics = camp.get('metrics', {})
            
            if args.impressions is not None:
                metrics['impressions'] = int(args.impressions)
            if args.clicks is not None:
                metrics['clicks'] = int(args.clicks)
            if args.conversions is not None:
                metrics['conversions'] = int(args.conversions)
            if args.spend is not None:
                metrics['spend'] = float(args.spend)
            
            camp['metrics'] = metrics
            save_json(CAMPAIGNS_FILE, campaigns)
            
            print(f"✅ Campaign metrics updated!")
            
            # Calculate CTR and CVR
            impressions = metrics.get('impressions', 0)
            clicks = metrics.get('clicks', 0)
            conversions = metrics.get('conversions', 0)
            spend = metrics.get('spend', 0)
            
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cvr = (conversions / clicks * 100) if clicks > 0 else 0
            cpc = (spend / clicks) if clicks > 0 else 0
            
            print(f"   CTR: {ctr:.2f}% | CVR: {cvr:.2f}% | CPC: ${cpc:.2f}")
            return 0
    
    print(f"❌ Campaign {args.campaign_id} not found.")
    return 1


def cmd_add_content(args) -> int:
    """Add content to the calendar."""
    logger.info(f"Adding content: {args.title}")
    
    content = load_json(CONTENT_FILE)
    
    item = {
        "id": str(uuid.uuid4())[:8],
        "title": args.title,
        "type": args.type or "post",
        "platform": args.platform or "general",
        "status": args.status or "idea",
        "publish_date": args.publish_date,
        "created_at": datetime.now().isoformat(),
        "notes": args.notes or "",
        "metrics": {
            "views": 0,
            "engagement": 0,
            "clicks": 0
        }
    }
    
    content['items'].append(item)
    save_json(CONTENT_FILE, content)
    
    print(f"✅ Content added: {args.title}")
    return 0


def cmd_content_calendar(args) -> int:
    """Show content calendar."""
    logger.info("Showing content calendar...")
    
    content = load_json(CONTENT_FILE)
    items = content.get('items', [])
    
    # Filter by date range if provided
    if args.days:
        start_date = datetime.now()
        end_date = start_date + timedelta(days=int(args.days))
        items = [i for i in items if i.get('publish_date') 
                 and start_date.strftime('%Y-%m-%d') <= i.get('publish_date') <= end_date.strftime('%Y-%m-%d')]
    
    if args.status:
        items = [i for i in items if i.get('status') == args.status]
    if args.platform:
        items = [i for i in items if i.get('platform') == args.platform]
    
    if not items:
        print("No content found.")
        return 0
    
    print(f"\n📅 Content Calendar ({len(items)} items):")
    print("-"*70)
    for item in sorted(items, key=lambda x: x.get('publish_date', '9999')):
        status_icon = {"idea": "💡", "scheduled": "📅", "published": "✅", "draft": "📝"}.get(
            item.get('status', 'idea'), "❓")
        date = item.get('publish_date', 'TBD')
        print(f"   {status_icon} {date} | {item.get('platform', '?'):<10} | {item.get('title', 'Untitled')}")
    
    return 0


def cmd_add_channel(args) -> int:
    """Add a marketing channel."""
    logger.info(f"Adding channel: {args.name}")
    
    channels = load_json(CHANNELS_FILE)
    
    channel = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "platform": args.platform or "web",
        "url": args.url or "",
        "status": "active",
        "followers": 0,
        "created_at": datetime.now().isoformat(),
        "notes": args.notes or ""
    }
    
    channels['channels'].append(channel)
    save_json(CHANNELS_FILE, channels)
    
    print(f"✅ Channel added: {args.name}")
    return 0


def cmd_list_channels(args) -> int:
    """List all marketing channels."""
    logger.info("Listing channels...")
    
    channels = load_json(CHANNELS_FILE)
    all_channels = channels.get('channels', [])
    
    if not all_channels:
        print("No channels registered.")
        return 0
    
    print(f"\n📡 Marketing Channels ({len(all_channels)}):")
    print("-"*60)
    for ch in all_channels:
        status_icon = {"active": "🟢", "inactive": "🔴", "testing": "🟡"}.get(
            ch.get('status', 'active'), "⚪")
        print(f"   {status_icon} {ch.get('name', 'Unknown')} ({ch.get('platform', '?')}) | Followers: {ch.get('followers', 0)}")
    
    return 0


def cmd_set_goals(args) -> int:
    """Set marketing goals."""
    logger.info("Setting marketing goals...")
    
    analytics = load_json(ANALYTICS_FILE)
    
    goals = analytics.get('goals', {})
    
    if args.leads is not None:
        goals['leads'] = int(args.leads)
    if args.conversions is not None:
        goals['conversions'] = int(args.conversions)
    if args.revenue is not None:
        goals['revenue'] = float(args.revenue)
    if args.impressions is not None:
        goals['impressions'] = int(args.impressions)
    
    analytics['goals'] = goals
    save_json(ANALYTICS_FILE, analytics)
    
    print("✅ Marketing goals updated!")
    return 0


def cmd_report(args) -> int:
    """Generate marketing performance report."""
    logger.info("Generating marketing report...")
    
    campaigns = load_json(CAMPAIGNS_FILE)
    content = load_json(CONTENT_FILE)
    channels = load_json(CHANNELS_FILE)
    analytics = load_json(ANALYTICS_FILE)
    
    all_campaigns = campaigns.get('campaigns', [])
    active_campaigns = [c for c in all_campaigns if c.get('status') == 'active']
    
    # Aggregate metrics
    total_impressions = sum(c.get('metrics', {}).get('impressions', 0) for c in all_campaigns)
    total_clicks = sum(c.get('metrics', {}).get('clicks', 0) for c in all_campaigns)
    total_conversions = sum(c.get('metrics', {}).get('conversions', 0) for c in all_campaigns)
    total_spend = sum(c.get('metrics', {}).get('spend', 0) for c in all_campaigns)
    
    overall_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    overall_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
    cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
    
    goals = analytics.get('goals', {})
    
    print("\n" + "="*60)
    print("📊 MARKETING PERFORMANCE REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-"*60)
    
    print("\n🚀 CAMPAIGN SUMMARY")
    print(f"   Total Campaigns: {len(all_campaigns)}")
    print(f"   Active: {len(active_campaigns)}")
    
    print("\n📈 AGGREGATE METRICS")
    print(f"   Total Impressions: {total_impressions:,}")
    print(f"   Total Clicks: {total_clicks:,}")
    print(f"   Total Conversions: {total_conversions:,}")
    print(f"   Total Spend: ${total_spend:,.2f}")
    
    print("\n📊 PERFORMANCE RATIOS")
    print(f"   Overall CTR: {overall_ctr:.2f}%")
    print(f"   Overall CVR: {overall_cvr:.2f}%")
    print(f"   Cost Per Acquisition: ${cpa:.2f}")
    
    print("\n🎯 GOALS")
    if goals:
        for key, val in goals.items():
            print(f"   {key.capitalize()}: {val}")
    else:
        print("   No goals set.")
    
    print("\n📡 CHANNELS")
    print(f"   Total Active: {len([c for c in channels.get('channels', []) if c.get('status') == 'active'])}")
    
    print("\n📅 CONTENT")
    published = len([c for c in content.get('items', []) if c.get('status') == 'published'])
    scheduled = len([c for c in content.get('items', []) if c.get('status') == 'scheduled'])
    print(f"   Published: {published}")
    print(f"   Scheduled: {scheduled}")
    
    print("\n" + "="*60)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="📣 CMO Marketing Agent - Campaign & Content Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard                    Show marketing dashboard
  %(prog)s add-campaign --name "Summer Sale" --channel social --budget 500
  %(prog)s list-campaigns --status active
  %(prog)s update-metrics --campaign-id abc123 --impressions 10000 --clicks 500
  %(prog)s add-content --title "New Blog Post" --type blog --platform website
  %(prog)s content-calendar --days 30 --status scheduled
  %(prog)s add-channel --name "Twitter" --platform twitter
  %(prog)s list-channels
  %(prog)s set-goals --leads 100 --conversions 10
  %(prog)s report                       Generate full marketing report
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show marketing dashboard')
    
    # Campaign commands
    camp_parser = subparsers.add_parser('add-campaign', help='Add a new campaign')
    camp_parser.add_argument('--name', required=True, help='Campaign name')
    camp_parser.add_argument('--channel', help='Marketing channel')
    camp_parser.add_argument('--status', default='planning', choices=['planning', 'active', 'paused', 'completed', 'cancelled'])
    camp_parser.add_argument('--budget', help='Campaign budget')
    camp_parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    camp_parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    camp_parser.add_argument('--notes', help='Notes')
    
    list_camp_parser = subparsers.add_parser('list-campaigns', help='List campaigns')
    list_camp_parser.add_argument('--status', choices=['planning', 'active', 'paused', 'completed', 'cancelled'])
    list_camp_parser.add_argument('--channel', help='Filter by channel')
    
    metrics_parser = subparsers.add_parser('update-metrics', help='Update campaign metrics')
    metrics_parser.add_argument('--campaign-id', required=True, help='Campaign ID')
    metrics_parser.add_argument('--impressions', help='Total impressions')
    metrics_parser.add_argument('--clicks', help='Total clicks')
    metrics_parser.add_argument('--conversions', help='Total conversions')
    metrics_parser.add_argument('--spend', help='Total spend')
    
    # Content commands
    content_parser = subparsers.add_parser('add-content', help='Add content to calendar')
    content_parser.add_argument('--title', required=True, help='Content title')
    content_parser.add_argument('--type', choices=['post', 'blog', 'video', 'email', 'ad'])
    content_parser.add_argument('--platform', help='Platform (twitter, linkedin, website, etc.)')
    content_parser.add_argument('--status', default='idea', choices=['idea', 'draft', 'scheduled', 'published'])
    content_parser.add_argument('--publish-date', help='Publish date (YYYY-MM-DD)')
    content_parser.add_argument('--notes', help='Notes')
    
    cal_parser = subparsers.add_parser('content-calendar', help='Show content calendar')
    cal_parser.add_argument('--days', help='Show next N days')
    cal_parser.add_argument('--status', choices=['idea', 'draft', 'scheduled', 'published'])
    cal_parser.add_argument('--platform', help='Filter by platform')
    
    # Channel commands
    ch_parser = subparsers.add_parser('add-channel', help='Add a marketing channel')
    ch_parser.add_argument('--name', required=True, help='Channel name')
    ch_parser.add_argument('--platform', help='Platform type')
    ch_parser.add_argument('--url', help='Channel URL')
    ch_parser.add_argument('--notes', help='Notes')
    
    subparsers.add_parser('list-channels', help='List all channels')
    
    # Goals command
    goals_parser = subparsers.add_parser('set-goals', help='Set marketing goals')
    goals_parser.add_argument('--leads', help='Lead goal')
    goals_parser.add_argument('--conversions', help='Conversion goal')
    goals_parser.add_argument('--revenue', help='Revenue goal')
    goals_parser.add_argument('--impressions', help='Impression goal')
    
    # Report command
    subparsers.add_parser('report', help='Generate marketing performance report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'dashboard': cmd_dashboard,
        'add-campaign': cmd_add_campaign,
        'list-campaigns': cmd_list_campaigns,
        'update-metrics': cmd_update_campaign_metrics,
        'add-content': cmd_add_content,
        'content-calendar': cmd_content_calendar,
        'add-channel': cmd_add_channel,
        'list-channels': cmd_list_channels,
        'set-goals': cmd_set_goals,
        'report': cmd_report
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
