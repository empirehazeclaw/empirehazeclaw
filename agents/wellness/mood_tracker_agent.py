#!/usr/bin/env python3
"""
Mood Tracker Agent
Tracks daily moods, emotions, and wellness factors with analytics and insights.
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "mood_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MoodTrackerAgent")

DATA_FILE = Path("/home/clawbot/.openclaw/workspace/data/mood_data.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

MOOD_LEVELS = {
    1: "😢 Very Low",
    2: "😔 Low",
    3: "😐 Neutral",
    4: "🙂 Good",
    5: "😊 Great"
}

EMOTION_CATEGORIES = {
    "positive": ["happy", "excited", "grateful", "calm", "motivated", "confident", "loved", "energized"],
    "neutral": ["tired", "focused", "content", "relaxed", "neutral"],
    "negative": ["stressed", "anxious", "sad", "angry", "frustrated", "overwhelmed", "lonely", "worried"]
}

WELLNESS_FACTORS = ["sleep", "exercise", "nutrition", "social", "work", "stress", "meditation"]

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"entries": [], "last_entry_id": 0}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def log_mood(args):
    """Log a new mood entry."""
    data = load_data()
    date_key = args.date or datetime.now().strftime("%Y-%m-%d")
    
    data["last_entry_id"] += 1
    
    # Parse emotions
    emotions = []
    if args.emotions:
        for e in args.emotions:
            emotions.extend([em.strip().lower() for em in e.split(",")])
    
    # Parse wellness factors
    wellness = {}
    if args.sleep:
        wellness["sleep"] = int(args.sleep)
    if args.exercise:
        wellness["exercise"] = 1
    if args.stress:
        wellness["stress"] = int(args.stress)
    if args.meditation:
        wellness["meditation"] = 1
    
    entry = {
        "id": data["last_entry_id"],
        "date": date_key,
        "time": datetime.now().isoformat(),
        "mood": args.mood,
        "mood_label": MOOD_LEVELS.get(args.mood, "Unknown"),
        "emotions": emotions,
        "wellness_factors": wellness,
        "notes": args.notes or ""
    }
    
    data["entries"].append(entry)
    save_data(data)
    
    logger.info(f"Logged mood entry: {date_key} - Mood: {entry['mood_label']}")
    print(f"\n✅ Mood logged!")
    print(f"   Date: {date_key}")
    print(f"   Mood: {entry['mood_label']}")
    if emotions:
        print(f"   Emotions: {', '.join(emotions)}")
    if wellness:
        print(f"   Wellness: {wellness}")

def show_day(args):
    """Show mood entry for a specific day."""
    data = load_data()
    date_key = args.date or datetime.now().strftime("%Y-%m-%d")
    
    entry = next((e for e in data["entries"] if e["date"] == date_key), None)
    
    if not entry:
        print(f"No mood entry for {date_key}")
        return
    
    print(f"\n📊 MOOD FOR {date_key}")
    print("=" * 60)
    print(f"   Mood: {entry['mood_label']}")
    if entry["emotions"]:
        print(f"   Emotions: {', '.join(entry['emotions'])}")
    if entry["wellness_factors"]:
        wf = entry["wellness_factors"]
        if "sleep" in wf:
            print(f"   Sleep: {wf['sleep']} hours")
        if "exercise" in wf:
            print(f"   Exercise: ✅")
        if "stress" in wf:
            print(f"   Stress Level: {wf['stress']}/10")
        if "meditation" in wf:
            print(f"   Meditation: ✅")
    if entry["notes"]:
        print(f"   Notes: {entry['notes']}")

def show_history(args):
    """Show mood history."""
    data = load_data()
    
    if not data["entries"]:
        print("No mood entries yet. Log a mood with --log-mood")
        return
    
    entries = sorted(data["entries"], key=lambda x: x["date"], reverse=True)[:args.days]
    
    print(f"\n📅 RECENT MOOD HISTORY")
    print("=" * 60)
    
    for entry in entries:
        print(f"\n{entry['date']} - {entry['mood_label']}")
        if entry["emotions"]:
            print(f"   Emotions: {', '.join(entry['emotions'])}")
        if entry["notes"]:
            note_preview = entry["notes"][:50] + "..." if len(entry["notes"]) > 50 else entry["notes"]
            print(f"   Note: {note_preview}")

def show_analytics(args):
    """Show mood analytics and trends."""
    data = load_data()
    
    if not data["entries"]:
        print("Not enough data for analytics. Log some moods first.")
        return
    
    days = min(args.days, len(data["entries"]))
    recent = sorted(data["entries"], key=lambda x: x["date"], reverse=True)[:days]
    
    # Calculate averages
    avg_mood = sum(e["mood"] for e in recent) / len(recent)
    
    # Emotion frequency
    emotion_counts = defaultdict(int)
    for entry in recent:
        for emotion in entry["emotions"]:
            emotion_counts[emotion] += 1
    
    # Wellness averages
    total_sleep = 0
    sleep_count = 0
    total_stress = 0
    stress_count = 0
    exercise_count = 0
    meditation_count = 0
    
    for entry in recent:
        wf = entry.get("wellness_factors", {})
        if "sleep" in wf:
            total_sleep += wf["sleep"]
            sleep_count += 1
        if "stress" in wf:
            total_stress += wf["stress"]
            stress_count += 1
        if wf.get("exercise"):
            exercise_count += 1
        if wf.get("meditation"):
            meditation_count += 1
    
    print(f"\n📈 MOOD ANALYTICS (Last {days} entries)")
    print("=" * 60)
    print(f"\n🎯 AVERAGES")
    print(f"   Average Mood: {avg_mood:.1f}/5 ({MOOD_LEVELS.get(round(avg_mood), 'Unknown')})")
    
    if sleep_count > 0:
        print(f"   Average Sleep: {total_sleep/sleep_count:.1f} hours")
    if stress_count > 0:
        print(f"   Average Stress: {total_stress/stress_count:.1f}/10")
    
    print(f"\n🏃 WELLNESS FREQUENCY")
    print(f"   Days with Exercise: {exercise_count}/{days} ({exercise_count/days*100:.0f}%)")
    print(f"   Days with Meditation: {meditation_count}/{days} ({meditation_count/days*100:.0f}%)")
    
    if emotion_counts:
        print(f"\n😊 TOP EMOTIONS")
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for emotion, count in sorted_emotions:
            cat = "positive" if emotion in EMOTION_CATEGORIES["positive"] else "negative" if emotion in EMOTION_CATEGORIES["negative"] else "neutral"
            emoji = "✅" if cat == "positive" else "❌" if cat == "negative" else "➖"
            print(f"   {emoji} {emotion}: {count} times")

def show_trends(args):
    """Show mood trends over time."""
    data = load_data()
    
    if len(data["entries"]) < 3:
        print("Not enough data for trend analysis. Need at least 3 entries.")
        return
    
    # Group by week
    weeks = defaultdict(list)
    for entry in data["entries"]:
        date = datetime.strptime(entry["date"], "%Y-%m-%d")
        week_start = date - timedelta(days=date.weekday())
        weeks[week_start.strftime("%Y-%m-%d")].append(entry["mood"])
    
    print(f"\n📊 WEEKLY MOOD TRENDS")
    print("=" * 60)
    
    sorted_weeks = sorted(weeks.items(), key=lambda x: x[0], reverse=True)[:args.weeks]
    for week_start, moods in sorted_weeks:
        avg = sum(moods) / len(moods)
        bars = "█" * int(avg * 4)
        week_end = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%m-%d")
        print(f"   Week of {week_start}: {bars} {avg:.1f}/5 ({len(moods)} entries)")

def export_data(args):
    """Export mood data to JSON."""
    data = load_data()
    
    export_file = Path(args.output) if args.output else Path(f"mood_export_{datetime.now().strftime('%Y%m%d')}.json")
    
    with open(export_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    logger.info(f"Exported mood data to {export_file}")
    print(f"\n✅ Data exported to {export_file}")
    print(f"   Total entries: {len(data['entries'])}")

def main():
    parser = argparse.ArgumentParser(
        description="Mood Tracker Agent - Track moods, emotions, and wellness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --log-mood --mood 4 --emotions happy,motivated --sleep 7 --exercise --notes "Great day!"
  %(prog)s --show-day --date 2026-03-27
  %(prog)s --show-history --days 7
  %(prog)s --analytics --days 14
  %(prog)s --trends --weeks 4
  %(prog)s --export --output mood_backup.json
        """
    )
    
    parser.add_argument('--log-mood', action='store_true', help='Log a new mood entry')
    parser.add_argument('--mood', type=int, choices=[1, 2, 3, 4, 5], help='Mood level (1-5)')
    parser.add_argument('--emotions', type=str, nargs='+', help='Emotions (comma-separated)')
    parser.add_argument('--sleep', type=str, help='Hours of sleep')
    parser.add_argument('--exercise', action='store_true', help='Did you exercise today?')
    parser.add_argument('--stress', type=str, help='Stress level 1-10')
    parser.add_argument('--meditation', action='store_true', help='Did you meditate today?')
    parser.add_argument('--notes', type=str, help='Optional notes')
    parser.add_argument('--date', type=str, help='Date (YYYY-MM-DD), defaults to today')
    
    parser.add_argument('--show-day', action='store_true', help='Show mood for a specific day')
    
    parser.add_argument('--show-history', action='store_true', help='Show mood history')
    parser.add_argument('--days', type=int, default=7, help='Number of days to show (default: 7)')
    
    parser.add_argument('--analytics', action='store_true', help='Show mood analytics')
    
    parser.add_argument('--trends', action='store_true', help='Show mood trends')
    parser.add_argument('--weeks', type=int, default=4, help='Number of weeks for trends (default: 4)')
    
    parser.add_argument('--export', action='store_true', help='Export mood data')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(0)
    
    try:
        if args.log_mood:
            if not args.mood:
                print("❌ Error: --mood is required")
                sys.exit(1)
            log_mood(args)
        elif args.show_day:
            show_day(args)
        elif args.show_history:
            show_history(args)
        elif args.analytics:
            show_analytics(args)
        elif args.trends:
            show_trends(args)
        elif args.export:
            export_data(args)
        else:
            parser.print_help()
    except Exception as e:
        logger.exception("Error in MoodTrackerAgent")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
