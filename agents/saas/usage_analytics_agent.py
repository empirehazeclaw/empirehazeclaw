#!/usr/bin/env python3
"""
SaaS Usage Analytics Agent
Tracks and analyses product usage metrics, feature usage, and user activity.
Reads/Writes: data/usage_analytics.json
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "usage_analytics.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("UsageAnalytics")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/usage_analytics.json")


def load_data():
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        default_data = {
            "events": [],
            "features": {},
            "users": {},
            "last_updated": datetime.utcnow().isoformat()
        }
        save_data(default_data)
        return default_data
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    data["last_updated"] = datetime.utcnow().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def track_event(user_id, event_type, feature=None, metadata=None, count=1):
    """Track a usage event."""
    data = load_data()
    event = {
        "user_id": str(user_id),
        "event_type": str(event_type),
        "feature": feature,
        "metadata": metadata or {},
        "count": count,
        "timestamp": datetime.utcnow().isoformat()
    }
    data["events"].append(event)

    # Update feature stats
    if feature:
        if feature not in data["features"]:
            data["features"][feature] = {"total_count": 0, "unique_users": [], "events": []}
        data["features"][feature]["total_count"] += count
        if str(user_id) not in data["features"][feature]["unique_users"]:
            data["features"][feature]["unique_users"].append(str(user_id))
        data["features"][feature]["events"].append(event["timestamp"])

    # Update user stats
    uid = str(user_id)
    if uid not in data["users"]:
        data["users"][uid] = {"event_count": 0, "last_seen": None, "features_used": []}
    data["users"][uid]["event_count"] += count
    data["users"][uid]["last_seen"] = datetime.utcnow().isoformat()
    if feature:
        if feature not in data["users"][uid]["features_used"]:
            data["users"][uid]["features_used"].append(feature)

    save_data(data)
    logger.info(f"Tracked event: user={user_id} type={event_type} feature={feature}")
    return event


def get_top_features(limit=10):
    """Get most used features."""
    data = load_data()
    features = []
    for name, info in data.get("features", {}).items():
        features.append({
            "name": name,
            "total_count": info["total_count"],
            "unique_users": len(info.get("unique_users", []))
        })
    features.sort(key=lambda x: x["total_count"], reverse=True)
    return features[:limit]


def get_active_users(days=7):
    """Get users active in the last N days."""
    data = load_data()
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    active = set()
    for event in data.get("events", []):
        if event["timestamp"] >= cutoff:
            active.add(event["user_id"])
    return list(active)


def get_usage_summary(period_days=30):
    """Get usage summary for a period."""
    data = load_data()
    cutoff = (datetime.utcnow() - timedelta(days=period_days)).isoformat()

    recent_events = [e for e in data.get("events", []) if e["timestamp"] >= cutoff]
    active_users = set(e["user_id"] for e in recent_events)

    event_types = defaultdict(int)
    for e in recent_events:
        event_types[e.get("event_type", "unknown")] += 1

    return {
        "period_days": period_days,
        "total_events": len(recent_events),
        "unique_users": len(active_users),
        "events_by_type": dict(event_types),
        "avg_events_per_user": round(len(recent_events) / len(active_users), 2) if active_users else 0
    }


def get_user_activity(user_id):
    """Get detailed activity for a specific user."""
    data = load_data()
    uid = str(user_id)
    events = [e for e in data.get("events", []) if e["user_id"] == uid]
    events.sort(key=lambda x: x["timestamp"], reverse=True)

    feature_counts = defaultdict(int)
    event_counts = defaultdict(int)
    for e in events:
        feature_counts[e.get("feature", "none")] += 1
        event_counts[e.get("event_type", "unknown")] += 1

    user_info = data.get("users", {}).get(uid, {})

    return {
        "user_id": uid,
        "total_events": len(events),
        "last_seen": user_info.get("last_seen"),
        "features_used": list(user_info.get("features_used", [])),
        "event_count_by_type": dict(event_counts),
        "feature_counts": dict(feature_counts),
        "recent_events": events[:20]
    }


def cmd_track(args):
    meta = {}
    if args.meta:
        for pair in args.meta:
            k, v = pair.split("=", 1)
            meta[k] = v
    track_event(args.user_id, args.type, args.feature, meta, args.count)
    print(f"Tracked: user={args.user_id} type={args.type} feature={args.feature}")


def cmd_top_features(args):
    features = get_top_features(args.limit)
    if not features:
        print("No feature data yet.")
        return
    print(f"\nTop {'Features' if not args.unique else 'Features (by unique users)'}")
    print(f"{'#':<4} {'Feature':<30} {'Usage Count':>12} {'Unique Users':>14}")
    print("-" * 65)
    for i, f in enumerate(features, 1):
        key = "unique_users" if args.unique else "total_count"
        print(f"{i:<4} {f['name']:<30} {f['total_count']:>12} {f['unique_users']:>14}")


def cmd_active_users(args):
    active = get_active_users(args.days)
    print(f"\nActive users (last {args.days} days): {len(active)}")
    for uid in active[:20]:
        print(f"  {uid}")
    if len(active) > 20:
        print(f"  ... and {len(active) - 20} more")


def cmd_summary(args):
    summary = get_usage_summary(args.period)
    print(f"\n{'='*55}")
    print(f"  USAGE SUMMARY (last {summary['period_days']} days)")
    print(f"{'='*55}")
    print(f"  Total Events     : {summary['total_events']}")
    print(f"  Unique Users     : {summary['unique_users']}")
    print(f"  Avg Events/User  : {summary['avg_events_per_user']}")
    print(f"\n  Events by Type:")
    for etype, count in summary["events_by_type"].items():
        print(f"    {etype}: {count}")
    print(f"{'='*55}")


def cmd_user(args):
    activity = get_user_activity(args.user_id)
    print(f"\nUser Activity: {args.user_id}")
    print(f"  Total Events : {activity['total_events']}")
    print(f"  Last Seen     : {activity['last_seen'] or 'Never'}")
    print(f"  Features Used : {', '.join(activity['features_used']) or 'None'}")
    print(f"  Event Types:")
    for etype, count in activity["event_count_by_type"].items():
        print(f"    {etype}: {count}")


def cmd_events(args):
    """Show recent events."""
    data = load_data()
    events = data.get("events", [])[-args.limit:]
    events.reverse()
    print(f"\nLast {args.limit} Events:")
    print(f"{'Time':<28} {'User':<15} {'Type':<20} {'Feature':<20}")
    print("-" * 85)
    for e in events:
        print(f"{e.get('timestamp',''):<28} {e.get('user_id',''):<15} "
              f"{e.get('event_type',''):<20} {e.get('feature') or '':<20}")


def main():
    parser = argparse.ArgumentParser(description="SaaS Usage Analytics Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    p_track = subparsers.add_parser("track", help="Track a usage event")
    p_track.add_argument("--user-id", required=True)
    p_track.add_argument("--type", required=True, help="Event type (login, click, api_call, etc)")
    p_track.add_argument("--feature", help="Feature name")
    p_track.add_argument("--count", type=int, default=1)
    p_track.add_argument("--meta", nargs="*", help="key=value pairs")
    p_track.set_defaults(func=cmd_track)

    p_top = subparsers.add_parser("top", help="Top features by usage")
    p_top.add_argument("--limit", type=int, default=10)
    p_top.add_argument("--unique", action="store_true", help="Sort by unique users")
    p_top.set_defaults(func=cmd_top_features)

    p_active = subparsers.add_parser("active", help="Active users")
    p_active.add_argument("--days", type=int, default=7)
    p_active.set_defaults(func=cmd_active_users)

    p_sum = subparsers.add_parser("summary", help="Usage summary")
    p_sum.add_argument("--period", type=int, default=30, dest="period")
    p_sum.set_defaults(func=cmd_summary)

    p_user = subparsers.add_parser("user", help="User activity detail")
    p_user.add_argument("user_id")
    p_user.set_defaults(func=cmd_user)

    p_events = subparsers.add_parser("events", help="Show recent events")
    p_events.add_argument("--limit", type=int, default=20)
    p_events.set_defaults(func=cmd_events)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
