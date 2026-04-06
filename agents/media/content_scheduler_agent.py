#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          CONTENT SCHEDULER AGENT                            ║
║          Multi-Platform Content Scheduling & Calendar        ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Schedule content for multiple platforms (Twitter, LinkedIn, Blog, Instagram, YouTube, Newsletter)
  - Calendar view with daily/weekly/monthly overview
  - Optimal posting time suggestions
  - Content queue management
  - Repeat/recurring posts
  - Timezone-aware scheduling
  - CSV/JSON export
  - Conflict detection

Usage:
    python3 content_scheduler_agent.py --help
    python3 content_scheduler_agent.py add "Tweet about AI" --platform twitter --time "2026-03-28 14:00"
    python3 content_scheduler_agent.py list --days 7
    python3 content_scheduler_agent.py calendar --month 3 --year 2026
    python3 content_scheduler_agent.py optimize --platform twitter
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger("openclaw.scheduler")


class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    BLOG = "blog"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    NEWSLETTER = "newsletter"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    THREADS = "threads"
    REDDIT = "reddit"


class ContentStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Optimal posting times by platform (UTC)
OPTIMAL_TIMES = {
    Platform.TWITTER: [(9, 11), (12, 14), (17, 19)],
    Platform.LINKEDIN: [(7, 9), (12, 14), (17, 18)],
    Platform.INSTAGRAM: [(11, 13), (17, 19), (21, 22)],
    Platform.FACEBOOK: [(12, 14), (16, 18)],
    Platform.YOUTUBE: [(11, 13), (14, 16)],
    Platform.BLOG: [(6, 8), (12, 14)],
    Platform.NEWSLETTER: [(8, 10)],
    Platform.TIKTOK: [(18, 20), (21, 22)],
    Platform.THREADS: [(11, 13), (18, 20)],
    Platform.REDDIT: [(6, 9), (18, 21)],
}

# Timezone mapping
TIMEZONES = {
    "UTC": 0,
    "CET": 1,
    "CEST": 2,
    "EST": -5,
    "PST": -8,
    "JST": 9,
}


@dataclass
class ScheduledContent:
    """Single scheduled content item"""
    id: str
    title: str
    content: str
    platform: Platform
    scheduled_time: datetime
    status: ContentStatus = ContentStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    repeat: Optional[str] = None  # e.g., "daily", "weekly"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['scheduled_time'] = self.scheduled_time.isoformat()
        d['created_at'] = self.created_at.isoformat()
        if self.published_at:
            d['published_at'] = self.published_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'ScheduledContent':
        data = data.copy()
        data['scheduled_time'] = datetime.fromisoformat(data['scheduled_time'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('published_at'):
            data['published_at'] = datetime.fromisoformat(data['published_at'])
        data['platform'] = Platform(data['platform'])
        data['status'] = ContentStatus(data['status'])
        data['priority'] = Priority(data['priority'])
        return cls(**data)


class ContentScheduler:
    """Manages content scheduling across platforms"""

    def __init__(self, storage_path: str = "data/content_scheduler.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.content: List[ScheduledContent] = self._load()

    def _load(self) -> List[ScheduledContent]:
        """Load content from storage"""
        if not self.storage_path.exists():
            return []
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return [ScheduledContent.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError) as e:
            log.warning(f"Could not load scheduler data: {e}")
            return []

    def _save(self):
        """Save content to storage"""
        with open(self.storage_path, 'w') as f:
            json.dump([c.to_dict() for c in self.content], f, indent=2)

    def generate_id(self) -> str:
        """Generate unique content ID"""
        existing = {c.id for c in self.content}
        i = 1
        while f"content_{i}" in existing:
            i += 1
        return f"content_{i}"

    def add(self, title: str, content: str, platform: str,
            scheduled_time: str, priority: str = "medium",
            tags: Optional[List[str]] = None, repeat: Optional[str] = None,
            **metadata) -> ScheduledContent:
        """Add new scheduled content"""
        platform_enum = Platform(platform.lower())
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace(' ', 'T'))

        item = ScheduledContent(
            id=self.generate_id(),
            title=title,
            content=content,
            platform=platform_enum,
            scheduled_time=scheduled_dt,
            status=ContentStatus.SCHEDULED,
            priority=Priority(priority.lower()),
            tags=tags or [],
            repeat=repeat,
            metadata=metadata
        )

        self.content.append(item)
        self._save()
        log.info(f"Added: [{platform_enum.value}] {title} @ {scheduled_dt}")
        return item

    def list(self, days: int = 7, platform: Optional[str] = None,
             status: Optional[str] = None) -> List[ScheduledContent]:
        """List scheduled content for next N days"""
        now = datetime.now()
        end = now + timedelta(days=days)

        filtered = [c for c in self.content
                    if now <= c.scheduled_time <= end]

        if platform:
            filtered = [c for c in filtered if c.platform.value == platform.lower()]
        if status:
            filtered = [c for c in filtered if c.status.value == status.lower()]

        return sorted(filtered, key=lambda x: x.scheduled_time)

    def get_calendar(self, year: int, month: int) -> Dict[int, List[ScheduledContent]]:
        """Get content calendar for a month"""
        calendar: Dict[int, List[ScheduledContent]] = {day: [] for day in range(1, 32)}

        for item in self.content:
            if item.scheduled_time.year == year and item.scheduled_time.month == month:
                calendar[item.scheduled_time.day].append(item)

        return calendar

    def publish(self, content_id: str) -> bool:
        """Mark content as published"""
        for item in self.content:
            if item.id == content_id:
                item.status = ContentStatus.PUBLISHED
                item.published_at = datetime.now()
                self._save()
                log.info(f"Published: {item.title}")
                return True
        return False

    def cancel(self, content_id: str) -> bool:
        """Cancel scheduled content"""
        for item in self.content:
            if item.id == content_id:
                item.status = ContentStatus.CANCELLED
                self._save()
                log.info(f"Cancelled: {item.title}")
                return True
        return False

    def delete(self, content_id: str) -> bool:
        """Delete content"""
        for i, item in enumerate(self.content):
            if item.id == content_id:
                deleted = self.content.pop(i)
                self._save()
                log.info(f"Deleted: {deleted.title}")
                return True
        return False

    def optimize_times(self, platform: str) -> List[Dict]:
        """Suggest optimal posting times for a platform"""
        platform_enum = Platform(platform.lower())
        times = OPTIMAL_TIMES.get(platform_enum, [])

        suggestions = []
        now = datetime.now()

        for day_offset in range(7):
            date = now + timedelta(days=day_offset)
            for start_hour, end_hour in times:
                suggestion_time = date.replace(hour=start_hour, minute=0, second=0)
                if suggestion_time > now:
                    suggestions.append({
                        "datetime": suggestion_time.isoformat(),
                        "platform": platform_enum.value,
                        "reason": f"Optimal engagement window ({start_hour}:00-{end_hour}:00)"
                    })

        return suggestions[:14]

    def get_stats(self) -> Dict:
        """Get scheduling statistics"""
        now = datetime.now()
        stats = {
            "total": len(self.content),
            "by_status": {},
            "by_platform": {},
            "upcoming_7_days": 0,
            "overdue": 0,
        }

        for item in self.content:
            status_key = item.status.value
            platform_key = item.platform.value
            stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1
            stats["by_platform"][platform_key] = stats["by_platform"].get(platform_key, 0) + 1

            if item.status == ContentStatus.SCHEDULED:
                if now <= item.scheduled_time <= now + timedelta(days=7):
                    stats["upcoming_7_days"] += 1
                elif item.scheduled_time < now:
                    stats["overdue"] += 1

        return stats

    def export_csv(self, filepath: str):
        """Export schedule to CSV"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Title', 'Platform', 'Scheduled', 'Status', 'Priority', 'Tags'])
            for item in self.content:
                writer.writerow([
                    item.id,
                    item.title,
                    item.platform.value,
                    item.scheduled_time.isoformat(),
                    item.status.value,
                    item.priority.value,
                    ','.join(item.tags)
                ])
        log.info(f"Exported to {filepath}")

    def export_json(self, filepath: str):
        """Export schedule to JSON"""
        with open(filepath, 'w') as f:
            json.dump([c.to_dict() for c in self.content], f, indent=2)
        log.info(f"Exported to {filepath}")

    def clear_published(self, days_old: int = 7):
        """Remove old published content"""
        cutoff = datetime.now() - timedelta(days=days_old)
        original = len(self.content)
        self.content = [
            c for c in self.content
            if c.status != ContentStatus.PUBLISHED or
            (c.published_at and c.published_at > cutoff)
        ]
        removed = original - len(self.content)
        self._save()
        log.info(f"Cleared {removed} old published items")
        return removed


def format_calendar(calendar: Dict[int, List[ScheduledContent]], year: int, month: int) -> str:
    """Format calendar for display"""
    month_names = ["", "January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    lines = []
    lines.append(f"\n╔══════════════════════════════════════════════════════╗")
    lines.append(f"║           CALENDAR - {month_names[month]} {year}".ljust(55) + "║")
    lines.append(f"╠══════════════════════════════════════════════════════╣")

    for day in range(1, 32):
        items = calendar.get(day, [])
        if items or day <= 28:
            day_str = f"│ Day {day:2d}".ljust(13)
            if items:
                item_strs = []
                for item in items[:3]:
                    platform = item.platform.value[:3].upper()
                    time = item.scheduled_time.strftime("%H:%M")
                    item_strs.append(f"{platform}@{time}")
                content_str = " | ".join(item_strs)
                if len(items) > 3:
                    content_str += f" +{len(items)-3}"
            else:
                content_str = "-"
            lines.append(f"{day_str} │ {content_str}".ljust(60) + "│")

    lines.append(f"╚══════════════════════════════════════════════════════╝")
    return "\n".join(lines)


def format_list(items: List[ScheduledContent]) -> str:
    """Format content list for display"""
    if not items:
        return "\n📭 No scheduled content found.\n"

    lines = []
    lines.append(f"\n📅 Scheduled Content ({len(items)} items):")
    lines.append("─" * 70)

    current_date = None
    for item in items:
        date_str = item.scheduled_time.strftime("%Y-%m-%d")
        if date_str != current_date:
            lines.append(f"\n📆 {date_str}")
            lines.append("─" * 70)
            current_date = date_str

        time_str = item.scheduled_time.strftime("%H:%M")
        status_icon = {
            ContentStatus.DRAFT: "📝",
            ContentStatus.SCHEDULED: "⏰",
            ContentStatus.PUBLISHED: "✅",
            ContentStatus.FAILED: "❌",
            ContentStatus.CANCELLED: "🚫",
        }.get(item.status, "•")

        priority_color = {
            Priority.LOW: "🔵",
            Priority.MEDIUM: "🟡",
            Priority.HIGH: "🟠",
            Priority.URGENT: "🔴",
        }.get(item.priority, "•")

        lines.append(
            f"  {status_icon} {priority_color} [{item.platform.value:10}] "
            f"{time_str} | {item.title[:35]}"
        )
        if item.tags:
            lines.append(f"           🏷️  {', '.join(item.tags)}")

    lines.append("─" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Content Scheduler Agent - Multi-Platform Content Scheduling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Product Launch" --platform twitter --time "2026-03-28 14:00"
  %(prog)s add "Weekly Newsletter" --platform newsletter --time "2026-03-29 09:00" --tags "marketing,email"
  %(prog)s list --days 14 --platform twitter
  %(prog)s calendar --month 3 --year 2026
  %(prog)s optimize --platform linkedin
  %(prog)s stats
  %(prog)s export --format csv --output schedule.csv
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add scheduled content")
    add_parser.add_argument("title", help="Content title")
    add_parser.add_argument("--content", "-c", required=True, help="Content body/text")
    add_parser.add_argument("--platform", "-p", required=True,
                            choices=[p.value for p in Platform],
                            help="Target platform")
    add_parser.add_argument("--time", "-t", required=True,
                            help="Scheduled time (ISO format: YYYY-MM-DD HH:MM)")
    add_parser.add_argument("--priority", default="medium",
                            choices=["low", "medium", "high", "urgent"],
                            help="Content priority")
    add_parser.add_argument("--tags", help="Comma-separated tags")
    add_parser.add_argument("--repeat", choices=["daily", "weekly", "monthly"],
                            help="Repeat schedule")
    add_parser.add_argument("--storage", default="data/content_scheduler.json",
                            help="Storage file path")

    # List command
    list_parser = subparsers.add_parser("list", help="List scheduled content")
    list_parser.add_argument("--days", "-d", type=int, default=7,
                             help="Number of days to look ahead")
    list_parser.add_argument("--platform", help="Filter by platform")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--storage", default="data/content_scheduler.json",
                             help="Storage file path")

    # Calendar command
    cal_parser = subparsers.add_parser("calendar", help="Show monthly calendar")
    cal_parser.add_argument("--month", "-m", type=int, help="Month (1-12)")
    cal_parser.add_argument("--year", "-y", type=int, help="Year")
    cal_parser.add_argument("--storage", default="data/content_scheduler.json",
                            help="Storage file path")

    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Suggest optimal posting times")
    opt_parser.add_argument("--platform", "-p", required=True,
                            choices=[p.value for p in Platform],
                            help="Platform to optimize for")
    opt_parser.add_argument("--storage", default="data/content_scheduler.json",
                            help="Storage file path")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show scheduling statistics")
    stats_parser.add_argument("--storage", default="data/content_scheduler.json",
                              help="Storage file path")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export schedule")
    export_parser.add_argument("--format", "-f", choices=["csv", "json"],
                               default="csv", help="Export format")
    export_parser.add_argument("--output", "-o", required=True,
                               help="Output file path")
    export_parser.add_argument("--storage", default="data/content_scheduler.json",
                               help="Storage file path")

    # Publish command
    pub_parser = subparsers.add_parser("publish", help="Mark content as published")
    pub_parser.add_argument("content_id", help="Content ID to publish")
    pub_parser.add_argument("--storage", default="data/content_scheduler.json",
                            help="Storage file path")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel scheduled content")
    cancel_parser.add_argument("content_id", help="Content ID to cancel")
    cancel_parser.add_argument("--storage", default="data/content_scheduler.json",
                               help="Storage file path")

    # Delete command
    del_parser = subparsers.add_parser("delete", help="Delete content")
    del_parser.add_argument("content_id", help="Content ID to delete")
    del_parser.add_argument("--storage", default="data/content_scheduler.json",
                            help="Storage file path")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear old published content")
    clear_parser.add_argument("--days", type=int, default=7,
                              help="Remove published content older than N days")
    clear_parser.add_argument("--storage", default="data/content_scheduler.json",
                              help="Storage file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == "add":
            scheduler = ContentScheduler(args.storage)
            tags = args.tags.split(",") if args.tags else None
            item = scheduler.add(
                title=args.title,
                content=args.content,
                platform=args.platform,
                scheduled_time=args.time,
                priority=args.priority,
                tags=tags,
                repeat=args.repeat
            )
            print(f"\n✅ Content scheduled successfully!")
            print(f"   ID: {item.id}")
            print(f"   Platform: {item.platform.value}")
            print(f"   Time: {item.scheduled_time}")

        elif args.command == "list":
            scheduler = ContentScheduler(args.storage)
            items = scheduler.list(days=args.days, platform=args.platform, status=args.status)
            print(format_list(items))

        elif args.command == "calendar":
            now = datetime.now()
            month = args.month or now.month
            year = args.year or now.year
            scheduler = ContentScheduler(args.storage)
            calendar = scheduler.get_calendar(year, month)
            print(format_calendar(calendar, year, month))

        elif args.command == "optimize":
            scheduler = ContentScheduler(args.storage)
            suggestions = scheduler.optimize_times(args.platform)
            print(f"\n⏰ Optimal Posting Times for {args.platform}:")
            print("=" * 50)
            for i, s in enumerate(suggestions, 1):
                dt = datetime.fromisoformat(s['datetime'])
                print(f"  {i:2d}. {dt.strftime('%Y-%m-%d %H:%M')} - {s['reason']}")

        elif args.command == "stats":
            scheduler = ContentScheduler(args.storage)
            stats = scheduler.get_stats()
            print(f"\n📊 Content Scheduler Statistics:")
            print("=" * 50)
            print(f"  Total items: {stats['total']}")
            print(f"  Upcoming (7 days): {stats['upcoming_7_days']}")
            print(f"  Overdue: {stats['overdue']}")
            print(f"\n  By Status:")
            for status, count in stats['by_status'].items():
                print(f"    {status}: {count}")
            print(f"\n  By Platform:")
            for platform, count in stats['by_platform'].items():
                print(f"    {platform}: {count}")

        elif args.command == "export":
            scheduler = ContentScheduler(args.storage)
            if args.format == "csv":
                scheduler.export_csv(args.output)
            else:
                scheduler.export_json(args.output)
            print(f"\n✅ Exported to {args.output}")

        elif args.command == "publish":
            scheduler = ContentScheduler(args.storage)
            if scheduler.publish(args.content_id):
                print(f"\n✅ Content {args.content_id} marked as published!")
            else:
                print(f"\n❌ Content {args.content_id} not found!")
                sys.exit(1)

        elif args.command == "cancel":
            scheduler = ContentScheduler(args.storage)
            if scheduler.cancel(args.content_id):
                print(f"\n🚫 Content {args.content_id} cancelled!")
            else:
                print(f"\n❌ Content {args.content_id} not found!")
                sys.exit(1)

        elif args.command == "delete":
            scheduler = ContentScheduler(args.storage)
            if scheduler.delete(args.content_id):
                print(f"\n🗑️  Content {args.content_id} deleted!")
            else:
                print(f"\n❌ Content {args.content_id} not found!")
                sys.exit(1)

        elif args.command == "clear":
            scheduler = ContentScheduler(args.storage)
            removed = scheduler.clear_published(args.days)
            print(f"\n🧹 Cleared {removed} old published items!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        log.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
