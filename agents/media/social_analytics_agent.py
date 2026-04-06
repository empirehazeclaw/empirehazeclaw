#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          SOCIAL ANALYTICS AGENT                             ║
║          Cross-Platform Social Media Analytics              ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Track metrics across platforms (Twitter, LinkedIn, Instagram, YouTube, TikTok, Facebook)
  - Engagement rate calculation
  - Follower growth tracking
  - Best performing content analysis
  - Competitive benchmarking
  - Content performance scoring
  - Trend detection per platform
  - Automated reports (daily/weekly/monthly)
  - CSV/JSON export

Usage:
    python3 social_analytics_agent.py --help
    python3 social_analytics_agent.py track --platform twitter --metric followers
    python3 social_analytics_agent.py report --period weekly
    python3 social_analytics_agent.py compare --platforms twitter,linkedin
    python3 social_analytics_agent.py trends --platform instagram
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger("openclaw.social_analytics")


class Platform(str, Enum):
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    REDDIT = "reddit"
    THREADS = "threads"


class MetricType(str, Enum):
    FOLLOWERS = "followers"
    FOLLOWING = "following"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    VIEWS = "views"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    SAVES = "saves"
    ENGAGEMENT = "engagement"


BENCHMARKS = {
    Platform.TWITTER: 0.5,
    Platform.LINKEDIN: 2.0,
    Platform.INSTAGRAM: 1.5,
    Platform.YOUTUBE: 1.0,
    Platform.TIKTOK: 4.0,
    Platform.FACEBOOK: 0.8,
    Platform.REDDIT: 1.0,
    Platform.THREADS: 1.2,
}


@dataclass
class PlatformMetrics:
    platform: Platform
    timestamp: datetime
    followers: int = 0
    following: int = 0
    posts: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    reach: int = 0
    impressions: int = 0
    saves: int = 0

    def engagement_rate(self) -> float:
        total = self.likes + self.comments + self.shares + self.saves
        if self.followers == 0:
            return 0.0
        return (total / self.followers) * 100

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'PlatformMetrics':
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['platform'] = Platform(data['platform'])
        return cls(**data)


@dataclass
class Post:
    id: str
    platform: Platform
    content: str
    timestamp: datetime
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    reach: int = 0
    impressions: int = 0
    saves: int = 0
    engagement_rate: float = 0.0
    performance_score: float = 0.0
    tags: List[str] = field(default_factory=list)

    def calculate_engagement(self):
        total = self.likes + self.comments + self.shares + self.saves
        estimated = max(self.views, self.reach, self.impressions)
        self.engagement_rate = (total / estimated) * 100 if estimated > 0 else 0.0

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Post':
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['platform'] = Platform(data['platform'])
        return cls(**data)


@dataclass
class DailySnapshot:
    date: str
    platform: Platform
    followers: int
    new_followers: int
    posts: int
    total_likes: int
    total_comments: int
    total_shares: int
    total_views: int
    avg_engagement: float

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'DailySnapshot':
        data = data.copy()
        data['platform'] = Platform(data['platform'])
        return cls(**data)


class SocialAnalytics:
    BENCHMARKS = BENCHMARKS

    def __init__(self, storage_path: str = "data/social_analytics"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metrics_file = self.storage_path / "metrics.json"
        self.posts_file = self.storage_path / "posts.json"
        self.snapshots_file = self.storage_path / "snapshots.json"
        self.metrics_history = self._load_json(self.metrics_file)
        self.posts = self._load_posts()
        self.snapshots = self._load_snapshots()

    def _load_json(self, filepath: Path) -> List:
        if not filepath.exists():
            return []
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def _load_posts(self) -> List[Post]:
        data = self._load_json(self.posts_file)
        return [Post.from_dict(p) if isinstance(p, dict) else p for p in data]

    def _load_snapshots(self) -> List[DailySnapshot]:
        data = self._load_json(self.snapshots_file)
        return [DailySnapshot.from_dict(s) if isinstance(s, dict) else s for s in data]

    def _save(self, data: List, filepath: Path):
        with open(filepath, 'w') as f:
            json.dump([m.to_dict() if hasattr(m, 'to_dict') else m for m in data], f, indent=2)

    def _save_metrics(self):
        self._save(self.metrics_history, self.metrics_file)

    def _save_posts(self):
        self._save(self.posts, self.posts_file)

    def _save_snapshots(self):
        self._save(self.snapshots, self.snapshots_file)

    def record_metrics(self, platform: str, **kwargs) -> PlatformMetrics:
        platform_enum = Platform(platform)
        timestamp = datetime.now()

        metrics = PlatformMetrics(
            platform=platform_enum,
            timestamp=timestamp,
            **{k: v for k, v in kwargs.items() if k in [
                'followers', 'following', 'posts', 'likes', 'comments',
                'shares', 'views', 'reach', 'impressions', 'saves'
            ]}
        )

        self.metrics_history.append(metrics)
        self._save_metrics()

        date_str = timestamp.strftime("%Y-%m-%d")
        existing = next((s for s in self.snapshots
                        if s.date == date_str and s.platform == platform_enum), None)

        if existing:
            existing.followers = metrics.followers
            existing.posts += 1
            existing.total_likes += metrics.likes
            existing.total_comments += metrics.comments
            existing.total_shares += metrics.shares
            existing.total_views += metrics.views
            if existing.posts > 0:
                existing.avg_engagement = (existing.total_likes + existing.total_comments) / existing.posts
        else:
            self.snapshots.append(DailySnapshot(
                date=date_str,
                platform=platform_enum,
                followers=metrics.followers,
                new_followers=0,
                posts=1,
                total_likes=metrics.likes,
                total_comments=metrics.comments,
                total_shares=metrics.shares,
                total_views=metrics.views,
                avg_engagement=metrics.engagement_rate()
            ))

        self._save_snapshots()
        log.info(f"Recorded {platform}: {metrics.followers} followers")
        return metrics

    def add_post(self, platform: str, content: str, post_id: Optional[str] = None,
                 tags: Optional[List[str]] = None, **metrics) -> Post:
        platform_enum = Platform(platform)
        pid = post_id or f"{platform}_{len(self.posts) + 1}"
        post = Post(
            id=pid,
            platform=platform_enum,
            content=content[:200],
            timestamp=datetime.now(),
            tags=tags or [],
            **{k: v for k, v in metrics.items() if k in [
                'likes', 'comments', 'shares', 'views', 'reach', 'impressions', 'saves'
            ]}
        )
        post.calculate_engagement()
        self.posts.append(post)
        self._save_posts()
        return post

    def get_latest_metrics(self, platform: str) -> Optional[PlatformMetrics]:
        platform_enum = Platform(platform)
        matches = [m for m in self.metrics_history if m.platform == platform_enum]
        return max(matches, key=lambda x: x.timestamp, default=None)

    def get_growth_rate(self, platform: str, days: int = 30) -> Dict:
        platform_enum = Platform(platform)
        cutoff = datetime.now() - timedelta(days=days)
        snapshots = [s for s in self.snapshots
                     if s.platform == platform_enum and datetime.strptime(s.date, "%Y-%m-%d") >= cutoff]

        if len(snapshots) < 2:
            return {"trend": "insufficient_data", "growth_percent": 0, "avg_daily": 0}

        sorted_snaps = sorted(snapshots, key=lambda x: x.date)
        first = sorted_snaps[0].followers
        last = sorted_snaps[-1].followers
        growth = ((last - first) / first * 100) if first > 0 else 0
        total_growth = last - first
        avg_daily = total_growth / days if days > 0 else 0

        return {
            "trend": "growing" if growth > 0 else "declining" if growth < 0 else "stable",
            "growth_percent": round(growth, 2),
            "total_growth": total_growth,
            "avg_daily": round(avg_daily, 2),
            "start_followers": first,
            "current_followers": last
        }

    def get_top_posts(self, platform: str, limit: int = 10) -> List[Post]:
        platform_enum = Platform(platform)
        posts = [p for p in self.posts if p.platform == platform_enum]
        for p in posts:
            p.calculate_engagement()
        return sorted(posts, key=lambda x: x.engagement_rate, reverse=True)[:limit]

    def get_engagement_comparison(self, platforms: List[str]) -> Dict:
        result = {}
        for p in platforms:
            platform_enum = Platform(p)
            latest = self.get_latest_metrics(p)
            posts = self.get_top_posts(p, limit=10)
            avg_eng = statistics.mean([po.engagement_rate for po in posts]) if posts else 0
            benchmark = self.BENCHMARKS.get(platform_enum, 1.0)
            result[p] = {
                "followers": latest.followers if latest else 0,
                "avg_engagement": round(avg_eng, 3),
                "benchmark": benchmark,
                "vs_benchmark": round((avg_eng / benchmark - 1) * 100, 1) if benchmark else 0,
                "top_post_engagement": posts[0].engagement_rate if posts else 0,
            }
        return result

    def get_trends(self, platform: str, days: int = 14) -> Dict:
        platform_enum = Platform(platform)
        cutoff = datetime.now() - timedelta(days=days)
        snapshots = [s for s in self.snapshots
                     if s.platform == platform_enum and datetime.strptime(s.date, "%Y-%m-%d") >= cutoff]
        snapshots = sorted(snapshots, key=lambda x: x.date)

        if len(snapshots) < 2:
            return {"trend": "unknown", "direction": "neutral", "change_percent": 0}

        first_eng = snapshots[0].avg_engagement
        last_eng = snapshots[-1].avg_engagement
        change = ((last_eng - first_eng) / first_eng * 100) if first_eng > 0 else 0

        return {
            "trend": "improving" if change > 10 else "declining" if change < -10 else "stable",
            "direction": "up" if change > 0 else "down" if change < 0 else "flat",
            "change_percent": round(change, 2),
            "data_points": len(snapshots),
            "platform": platform
        }

    def generate_report(self, period: str = "weekly") -> Dict:
        now = datetime.now()
        if period == "daily":
            days = 1
        elif period == "weekly":
            days = 7
        elif period == "monthly":
            days = 30
        else:
            days = 7

        cutoff = now - timedelta(days=days)
        recent_snapshots = [s for s in self.snapshots
                           if datetime.strptime(s.date, "%Y-%m-%d") >= cutoff]

        platforms = set(s.platform for s in recent_snapshots)
        report = {
            "period": period,
            "days": days,
            "generated_at": now.isoformat(),
            "platforms": {},
            "overall": {"total_followers": 0, "avg_engagement": 0}
        }

        for p in platforms:
            p_snaps = sorted([s for s in recent_snapshots if s.platform == p], key=lambda x: x.date)
            if not p_snaps:
                continue
            first = p_snaps[0]
            last = p_snaps[-1]
            follower_growth = ((last.followers - first.followers) / first.followers * 100) if first.followers > 0 else 0
            avg_eng = statistics.mean([s.avg_engagement for s in p_snaps]) if p_snaps else 0

            report["platforms"][p.value] = {
                "followers_start": first.followers,
                "followers_end": last.followers,
                "growth_percent": round(follower_growth, 2),
                "total_posts": sum(s.posts for s in p_snaps),
                "avg_engagement": round(avg_eng, 3),
                "benchmark": self.BENCHMARKS.get(p, 1.0),
            }
            report["overall"]["total_followers"] += last.followers

        all_engs = [s.avg_engagement for s in recent_snapshots]
        report["overall"]["avg_engagement"] = round(statistics.mean(all_engs), 3) if all_engs else 0

        return report

    def export_csv(self, filepath: str, days: int = 30):
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Platform', 'Followers', 'Posts', 'Likes', 'Comments', 'Shares', 'Views', 'Avg Engagement'])
            cutoff = datetime.now() - timedelta(days=days)
            for snap in self.snapshots:
                if datetime.strptime(snap.date, "%Y-%m-%d") >= cutoff:
                    writer.writerow([
                        snap.date, snap.platform.value, snap.followers, snap.posts,
                        snap.total_likes, snap.total_comments, snap.total_shares,
                        snap.total_views, snap.avg_engagement
                    ])
        log.info(f"Exported to {filepath}")

    def export_json(self, filepath: str):
        data = {
            "metrics": [m.to_dict() for m in self.metrics_history],
            "posts": [p.to_dict() for p in self.posts],
            "snapshots": [s.to_dict() for s in self.snapshots],
            "generated_at": datetime.now().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        log.info(f"Exported to {filepath}")

    def simulate_data(self, platform: str, days: int = 30):
        """Generate realistic simulated data for testing"""
        platform_enum = Platform(platform)
        base_followers = {
            Platform.TWITTER: 5000,
            Platform.LINKEDIN: 2000,
            Platform.INSTAGRAM: 8000,
            Platform.YOUTUBE: 3000,
            Platform.TIKTOK: 15000,
            Platform.FACEBOOK: 1000,
        }.get(platform_enum, 1000)

        followers = base_followers
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i)
            growth = random.randint(5, 50)
            followers += growth

            metrics = PlatformMetrics(
                platform=platform_enum,
                timestamp=date,
                followers=followers,
                following=followers // 10,
                posts=random.randint(1, 5),
                likes=random.randint(50, 500),
                comments=random.randint(5, 50),
                shares=random.randint(10, 100),
                views=random.randint(500, 5000),
            )
            self.metrics_history.append(metrics)

        self._save_metrics()
        log.info(f"Simulated {days} days of data for {platform}")


def format_report(report: Dict) -> str:
    lines = []
    lines.append(f"\n📊 SOCIAL ANALYTICS REPORT ({report['period']})")
    lines.append("=" * 60)
    lines.append(f"Period: Last {report['days']} days")
    lines.append(f"Generated: {report['generated_at'][:19]}")
    lines.append("")
    lines.append("📈 PLATFORM BREAKDOWN:")
    lines.append("-" * 60)

    for platform, data in report['platforms'].items():
        trend = "📈" if data['growth_percent'] > 0 else "📉" if data['growth_percent'] < 0 else "➡️"
        lines.append(f"  {platform.upper()}:")
        lines.append(f"    Followers: {data['followers_start']:,} → {data['followers_end']:,} {trend} ({data['growth_percent']:+.1f}%)")
        lines.append(f"    Posts: {data['total_posts']} | Avg Engagement: {data['avg_engagement']:.2f}%")
        lines.append(f"    Benchmark: {data['benchmark']}% | vs Benchmark: {data['vs_benchmark']:+.1f}%")
        lines.append("")

    lines.append(f"OVERALL: {report['overall']['total_followers']:,} total followers | "
                 f"Avg Engagement: {report['overall']['avg_engagement']:.2f}%")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Social Analytics Agent - Cross-Platform Social Media Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s track --platform twitter --followers 5000 --likes 500 --comments 50
  %(prog)s track --platform instagram --followers 8000 --likes 2000 --comments 100
  %(prog)s report --period weekly
  %(prog)s report --period monthly
  %(prog)s compare --platforms twitter,linkedin,instagram
  %(prog)s trends --platform twitter --days 14
  %(prog)s top --platform instagram --limit 5
  %(prog)s growth --platform twitter
  %(prog)s export --format csv --output analytics.csv
  %(prog)s simulate --platform twitter --days 30
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    track_parser = subparsers.add_parser("track", help="Record platform metrics")
    track_parser.add_argument("--platform", "-p", required=True,
                              choices=[p.value for p in Platform],
                              help="Platform name")
    track_parser.add_argument("--followers", type=int, default=0)
    track_parser.add_argument("--following", type=int, default=0)
    track_parser.add_argument("--posts", type=int, default=0)
    track_parser.add_argument("--likes", type=int, default=0)
    track_parser.add_argument("--comments", type=int, default=0)
    track_parser.add_argument("--shares", type=int, default=0)
    track_parser.add_argument("--views", type=int, default=0)
    track_parser.add_argument("--reach", type=int, default=0)
    track_parser.add_argument("--impressions", type=int, default=0)
    track_parser.add_argument("--storage", default="data/social_analytics")

    post_parser = subparsers.add_parser("post", help="Add a post with metrics")
    post_parser.add_argument("--platform", "-p", required=True,
                            choices=[p.value for p in Platform])
    post_parser.add_argument("--content", "-c", required=True)
    post_parser.add_argument("--id")
    post_parser.add_argument("--likes", type=int, default=0)
    post_parser.add_argument("--comments", type=int, default=0)
    post_parser.add_argument("--shares", type=int, default=0)
    post_parser.add_argument("--views", type=int, default=0)
    post_parser.add_argument("--tags", help="Comma-separated tags")
    post_parser.add_argument("--storage", default="data/social_analytics")

    report_parser = subparsers.add_parser("report", help="Generate analytics report")
    report_parser.add_argument("--period", default="weekly",
                               choices=["daily", "weekly", "monthly"])
    report_parser.add_argument("--storage", default="data/social_analytics")

    compare_parser = subparsers.add_parser("compare", help="Compare platforms")
    compare_parser.add_argument("--platforms", "-pl", required=True,
                               help="Comma-separated platforms")
    compare_parser.add_argument("--storage", default="data/social_analytics")

    trends_parser = subparsers.add_parser("trends", help="Analyze trends")
    trends_parser.add_argument("--platform", "-p", required=True,
                              choices=[p.value for p in Platform])
    trends_parser.add_argument("--days", type=int, default=14)
    trends_parser.add_argument("--storage", default="data/social_analytics")

    top_parser = subparsers.add_parser("top", help="Get top performing posts")
    top_parser.add_argument("--platform", "-p", required=True,
                           choices=[p.value for p in Platform])
    top_parser.add_argument("--limit", type=int, default=10)
    top_parser.add_argument("--storage", default="data/social_analytics")

    growth_parser = subparsers.add_parser("growth", help="Get growth rate")
    growth_parser.add_argument("--platform", "-p", required=True,
                              choices=[p.value for p in Platform])
    growth_parser.add_argument("--days", type=int, default=30)
    growth_parser.add_argument("--storage", default="data/social_analytics")

    export_parser = subparsers.add_parser("export", help="Export data")
    export_parser.add_argument("--format", "-f", choices=["csv", "json"],
                              default="csv")
    export_parser.add_argument("--output", "-o", required=True)
    export_parser.add_argument("--days", type=int, default=30)
    export_parser.add_argument("--storage", default="data/social_analytics")

    simulate_parser = subparsers.add_parser("simulate", help="Generate test data")
    simulate_parser.add_argument("--platform", "-p", required=True,
                               choices=[p.value for p in Platform])
    simulate_parser.add_argument("--days", type=int, default=30)
    simulate_parser.add_argument("--storage", default="data/social_analytics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        storage = getattr(args, 'storage', 'data/social_analytics')
        analytics = SocialAnalytics(storage)

        if args.command == "track":
            metrics = analytics.record_metrics(
                args.platform,
                followers=args.followers,
                following=args.following,
                posts=args.posts,
                likes=args.likes,
                comments=args.comments,
                shares=args.shares,
                views=args.views,
                reach=getattr(args, 'reach', 0),
                impressions=getattr(args, 'impressions', 0)
            )
            print(f"\n✅ Recorded metrics for {args.platform}")
            print(f"   Followers: {metrics.followers:,}")
            print(f"   Engagement Rate: {metrics.engagement_rate():.2f}%")

        elif args.command == "post":
            tags = args.tags.split(",") if args.tags else None
            post = analytics.add_post(
                args.platform, args.content,
                post_id=args.id, tags=tags,
                likes=args.likes, comments=args.comments,
                shares=args.shares, views=args.views
            )
            print(f"\n✅ Added post {post.id} for {args.platform}")
            print(f"   Engagement Rate: {post.engagement_rate():.2f}%")

        elif args.command == "report":
            report = analytics.generate_report(args.period)
            print(format_report(report))

        elif args.command == "compare":
            platforms = [p.strip() for p in args.platforms.split(",")]
            comparison = analytics.get_engagement_comparison(platforms)
            print(f"\n📊 PLATFORM COMPARISON:")
            print("=" * 70)
            for p, data in comparison.items():
                print(f"\n  {p.upper()}:")
                print(f"    Followers: {data['followers']:,}")
                print(f"    Avg Engagement: {data['avg_engagement']:.2f}%")
                print(f"    vs Benchmark: {data['vs_benchmark']:+.1f}%")
                print(f"    Top Post: {data['top_post_engagement']:.2f}%")

        elif args.command == "trends":
            trends = analytics.get_trends(args.platform, args.days)
            print(f"\n📈 TRENDS for {args.platform} (last {args.days} days):")
            print("=" * 50)
            print(f"  Direction: {trends['direction'].upper()}")
            print(f"  Change: {trends['change_percent']:+.2f}%")
            print(f"  Status: {trends['trend'].upper()}")

        elif args.command == "top":
            posts = analytics.get_top_posts(args.platform, args.limit)
            print(f"\n🏆 TOP {len(posts)} POSTS on {args.platform}:")
            print("=" * 70)
            for i, post in enumerate(posts, 1):
                print(f"  {i}. {post.content[:50]}...")
                print(f"     Engagement: {post.engagement_rate:.2f}% | "
                      f"Likes: {post.likes} | Comments: {post.comments}")
                print(f"     Date: {post.timestamp.strftime('%Y-%m-%d')}")
                print()

        elif args.command == "growth":
            growth = analytics.get_growth_rate(args.platform, args.days)
            print(f"\n📈 GROWTH for {args.platform} (last {args.days} days):")
            print("=" * 50)
            print(f"  Trend: {growth['trend'].upper()}")
            print(f"  Followers: {growth['start_followers']:,} → {growth['current_followers']:,}")
            print(f"  Growth: {growth['growth_percent']:+.2f}% ({growth['total_growth']:+,} followers)")
            print(f"  Avg Daily: {growth['avg_daily']:+.1f} followers/day")

        elif args.command == "export":
            if args.format == "csv":
                analytics.export_csv(args.output, args.days)
            else:
                analytics.export_json(args.output)
            print(f"\n✅ Exported to {args.output}")

        elif args.command == "simulate":
            analytics.simulate_data(args.platform, args.days)
            print(f"\n✅ Simulated {args.days} days of data for {args.platform}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled")
        sys.exit(130)
    except Exception as e:
        log.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
