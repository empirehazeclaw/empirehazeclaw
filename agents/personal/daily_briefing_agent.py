#!/usr/bin/env python3
"""
Daily Briefing Agent
Generates daily briefings with weather, tasks, calendar, news, and custom sections.
"""

import argparse
import json
import logging
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/personal")
LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "daily_briefing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BRIEFINGS_FILE = DATA_DIR / "briefings.json"
CONFIG_FILE = DATA_DIR / "briefing_config.json"
TASKS_FILE = DATA_DIR / "meeting_tasks.json"


def load_json(path: Path, default: Any = None) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading {path}: {e}")
    return default if default is not None else {}


def save_json(path: Path, data: Any) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        return True
    except IOError as e:
        logger.error(f"Error saving {path}: {e}")
        return False


# Motivational quotes
QUOTES = [
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
    "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt",
    "It does not matter how slowly you go as long as you do not stop. — Confucius",
    "Believe you can and you're halfway there. — Theodore Roosevelt",
    "The best time to plant a tree was 20 years ago. The second best time is now. — Chinese Proverb",
    "Your limitation—it's only your imagination.",
    "Great things never come from comfort zones.",
    "Dream it. Wish it. Do it.",
    "Success doesn't just find you. You have to go out and get it.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Don't stop when you're tired. Stop when you're done.",
    "Wake up with determination. Go to bed with satisfaction.",
    "Do something today that your future self will thank you for.",
    "Little things make big days.",
]

# Productivity tips
TIPS = [
    "Start your day with the hardest task - eat that frog!",
    "Use the 2-minute rule: If it takes less than 2 minutes, do it now.",
    "Batch similar tasks together to minimize context switching.",
    "Take regular breaks - try the Pomodoro technique (25 min work, 5 min break).",
    "Set up a 'shutdown ritual' at the end of each workday.",
    "Review your calendar the night before to prepare mentally.",
    "Keep your workspace clean and minimal for better focus.",
    "Turn off notifications during deep work sessions.",
    "Use time blocking for your most important tasks.",
    "Start meetings on time and end them early when possible.",
    "Keep a 'done' list alongside your to-do list to track progress.",
    "Delegate what others can do so you can focus on what only you can do.",
]


def get_weather_placeholder() -> dict:
    """Get placeholder weather data (mock)."""
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Clear"]
    return {
        "location": "Your Location",
        "temperature": random.randint(15, 30),
        "condition": random.choice(conditions),
        "humidity": random.randint(30, 80),
        "wind_speed": random.randint(5, 25),
        "suggestion": "Great day to be productive!" if random.random() > 0.3 else "Stay cozy and focused indoors."
    }


def get_tasks_for_today() -> list[dict]:
    """Get tasks due today or overdue."""
    tasks_data = load_json(TASKS_FILE, {"tasks": []})
    tasks = tasks_data.get("tasks", [])
    
    today = datetime.utcnow().strftime("%Y-%m-%d")
    today_tasks = []
    
    for task in tasks:
        if task.get("status") == "completed":
            continue
        
        due_date = task.get("due_date", "")
        if due_date:
            if due_date < today:
                task["overdue"] = True
                today_tasks.append(task)
            elif due_date == today:
                today_tasks.append(task)
        else:
            today_tasks.append(task)
    
    return sorted(today_tasks, key=lambda x: (x.get("overdue", False), x.get("due_date", "")))


def get_upcoming_events(days: int = 7) -> list[dict]:
    """Get upcoming calendar events."""
    # Try to load from meeting notes
    meeting_file = DATA_DIR / "meeting_notes.json"
    meetings = load_json(meeting_file, {"notes": []}).get("notes", [])
    
    upcoming = []
    today = datetime.utcnow().date()
    
    for meeting in meetings:
        meeting_date_str = meeting.get("meeting_date", "")
        if meeting_date_str:
            try:
                meeting_date = datetime.strptime(meeting_date_str[:10], "%Y-%m-%d").date()
                if today <= meeting_date <= today + timedelta(days=days):
                    upcoming.append({
                        "title": meeting.get("title", "Untitled"),
                        "date": meeting_date_str,
                        "participants": meeting.get("participants", []),
                        "type": "meeting"
                    })
            except ValueError:
                continue
    
    return sorted(upcoming, key=lambda x: x.get("date", ""))


def get_briefing_stats() -> dict:
    """Get statistics for the briefing."""
    tasks_file = DATA_DIR / "meeting_tasks.json"
    tasks = load_json(tasks_file, {"tasks": []}).get("tasks", [])
    
    completed = len([t for t in tasks if t.get("status") == "completed"])
    pending = len([t for t in tasks if t.get("status") == "pending"])
    overdue = len([t for t in tasks if t.get("overdue", False)])
    
    meeting_file = DATA_DIR / "meeting_notes.json"
    meetings = load_json(meeting_file, {"notes": []}).get("notes", [])
    
    return {
        "tasks_completed": completed,
        "tasks_pending": pending,
        "tasks_overdue": overdue,
        "meetings_total": len(meetings),
        "completion_rate": round(completed / max(completed + pending, 1) * 100, 1)
    }


def generate_briefing(date: str = None, sections: list = None) -> dict:
    """Generate a daily briefing."""
    briefing_date = date or datetime.utcnow().strftime("%Y-%m-%d")
    briefing_id = f"briefing_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    
    if sections is None:
        sections = ["greeting", "weather", "tasks", "upcoming", "stats", "quote", "tip"]
    
    briefing = {
        "id": briefing_id,
        "date": briefing_date,
        "generated_at": datetime.utcnow().isoformat(),
        "sections": {}
    }
    
    # Greeting
    if "greeting" in sections:
        hour = datetime.utcnow().hour
        if hour < 12:
            greeting = "Good morning!"
        elif hour < 17:
            greeting = "Good afternoon!"
        else:
            greeting = "Good evening!"
        
        briefing["sections"]["greeting"] = {
            "message": greeting,
            "day_of_week": datetime.utcnow().strftime("%A"),
            "date_formatted": datetime.utcnow().strftime("%B %d, %Y")
        }
    
    # Weather
    if "weather" in sections:
        briefing["sections"]["weather"] = get_weather_placeholder()
    
    # Tasks
    if "tasks" in sections:
        tasks = get_tasks_for_today()
        briefing["sections"]["tasks"] = {
            "items": tasks[:10],
            "count": len(tasks),
            "overdue_count": len([t for t in tasks if t.get("overdue", False)])
        }
    
    # Upcoming events
    if "upcoming" in sections:
        upcoming = get_upcoming_events()
        briefing["sections"]["upcoming"] = {
            "events": upcoming[:5],
            "count": len(upcoming)
        }
    
    # Stats
    if "stats" in sections:
        briefing["sections"]["stats"] = get_briefing_stats()
    
    # Quote
    if "quote" in sections:
        briefing["sections"]["quote"] = {
            "text": random.choice(QUOTES)
        }
    
    # Tip
    if "tip" in sections:
        briefing["sections"]["tip"] = {
            "text": random.choice(TIPS)
        }
    
    return briefing


def format_briefing_text(briefing: dict) -> str:
    """Format briefing as readable text."""
    output = []
    sections = briefing.get("sections", {})
    
    output.append("=" * 60)
    output.append("📅 DAILY BRIEFING")
    output.append("=" * 60)
    
    # Greeting
    if "greeting" in sections:
        g = sections["greeting"]
        output.append(f"\n{g['message']}")
        output.append(f"Today is {g['day_of_week']}, {g['date_formatted']}")
    
    # Weather
    if "weather" in sections:
        w = sections["weather"]
        output.append(f"\n🌤️ WEATHER")
        output.append(f"   {w['condition']}, {w['temperature']}°C")
        output.append(f"   Humidity: {w['humidity']}% | Wind: {w['wind_speed']} km/h")
        output.append(f"   💡 {w['suggestion']}")
    
    # Tasks
    if "tasks" in sections:
        t = sections["tasks"]
        output.append(f"\n📋 TASKS FOR TODAY ({t['count']})")
        if t['overdue_count'] > 0:
            output.append(f"   ⚠️ {t['overdue_count']} overdue!")
        
        if t["items"]:
            for task in t["items"]:
                icon = "🔴" if task.get("overdue") else "⬜"
                due = f"[{task.get('due_date', 'No due')}]" if task.get("due_date") else ""
                output.append(f"   {icon} {task.get('description', 'Untitled')} {due}")
        else:
            output.append("   🎉 No tasks for today!")
    
    # Upcoming
    if "upcoming" in sections:
        u = sections["upcoming"]
        if u["count"] > 0:
            output.append(f"\n📆 UPCOMING ({u['count']})")
            for event in u["events"][:5]:
                output.append(f"   📅 {event.get('date', 'TBD')} - {event.get('title', 'Event')}")
    
    # Stats
    if "stats" in sections:
        s = sections["stats"]
        output.append(f"\n📊 WEEKLY STATS")
        output.append(f"   Completed: {s['tasks_completed']}")
        output.append(f"   Pending: {s['tasks_pending']}")
        output.append(f"   Overdue: {s['tasks_overdue']}")
        output.append(f"   Completion Rate: {s['completion_rate']}%")
        output.append(f"   Total Meetings: {s['meetings_total']}")
    
    # Quote
    if "quote" in sections:
        output.append(f"\n💬 QUOTE OF THE DAY")
        output.append(f"   \"{sections['quote']['text']}\"")
    
    # Tip
    if "tip" in sections:
        output.append(f"\n💡 PRODUCTIVITY TIP")
        output.append(f"   {sections['tip']['text']}")
    
    output.append("\n" + "=" * 60)
    output.append(f"Generated at: {briefing.get('generated_at', 'N/A')}")
    output.append(f"Briefing ID: {briefing.get('id', 'N/A')}")
    
    return "\n".join(output)


def save_briefing(briefing: dict) -> bool:
    """Save briefing to history."""
    briefings = load_json(BRIEFINGS_FILE, {"briefings": []})
    briefings["briefings"].append(briefing)
    
    # Keep only last 30 briefings
    if len(briefings["briefings"]) > 30:
        briefings["briefings"] = briefings["briefings"][-30:]
    
    return save_json(BRIEFINGS_FILE, briefings)


def get_config() -> dict:
    """Get briefing configuration."""
    return load_json(CONFIG_FILE, {
        "config": {
            "default_sections": ["greeting", "weather", "tasks", "upcoming", "stats", "quote", "tip"],
            "default_location": "New York",
            "notification_enabled": True
        }
    })["config"]


def update_config(updates: dict) -> bool:
    """Update briefing configuration."""
    config = get_config()
    config.update(updates)
    return save_json(CONFIG_FILE, {"config": config})


def cmd_generate(args):
    """Generate a daily briefing."""
    sections = None
    if args.sections:
        sections = [s.strip() for s in args.sections.split(",")]
    
    briefing = generate_briefing(date=args.date, sections=sections)
    
    # Save if requested
    if args.save:
        save_briefing(briefing)
        print(f"Briefing saved: {briefing['id']}")
    
    # Output
    if args.format == "text":
        print(format_briefing_text(briefing))
    else:
        print(json.dumps(briefing, indent=2))


def cmd_history(args):
    """Show briefing history."""
    briefings = load_json(BRIEFINGS_FILE, {"briefings": []}).get("briefings", [])
    
    if not briefings:
        print("No briefings in history")
        return
    
    print(f"\n{'='*60}")
    print(f"BRIEFING HISTORY: {len(briefings)}")
    print(f"{'='*60}\n")
    
    for b in reversed(briefings[-10:]):
        date = b.get("date", "N/A")
        gen_time = b.get("generated_at", "")[11:16] if b.get("generated_at") else "N/A"
        sections_list = list(b.get("sections", {}).keys())
        print(f"📅 {date} at {gen_time}")
        print(f"   Sections: {', '.join(sections_list)}")
        print(f"   ID: {b.get('id')}")
        print()


def cmd_tasks_summary(args):
    """Show tasks summary."""
    tasks_data = load_json(TASKS_FILE, {"tasks": []})
    tasks = tasks_data.get("tasks", [])
    
    if not tasks:
        print("No tasks found")
        return
    
    completed = [t for t in tasks if t.get("status") == "completed"]
    pending = [t for t in tasks if t.get("status") == "pending"]
    overdue = [t for t in tasks if t.get("overdue", False)]
    
    print(f"\n{'='*60}")
    print(f"TASKS SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {len(tasks)}")
    print(f"Completed: {len(completed)} ✅")
    print(f"Pending: {len(pending)} ⬜")
    print(f"Overdue: {len(overdue)} 🔴")
    print()


def cmd_config_show(args):
    """Show current configuration."""
    config = get_config()
    print(f"\n{'='*60}")
    print(f"BRIEFING CONFIGURATION")
    print(f"{'='*60}")
    for key, value in config.items():
        print(f"  {key}: {value}")
    print()


def cmd_config_set(args):
    """Update configuration."""
    if not args.key or not args.value:
        print("Error: --key and --value are required")
        return
    
    config = get_config()
    # Try to parse value
    if args.value.lower() in ["true", "false"]:
        value = args.value.lower() == "true"
    elif args.value.isdigit():
        value = int(args.value)
    else:
        value = args.value
    
    config[args.key] = value
    save_json(CONFIG_FILE, {"config": config})
    print(f"✅ {args.key} set to {value}")


def main():
    parser = argparse.ArgumentParser(
        description="Daily Briefing Agent - Generate personalized daily briefings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --generate
  %(prog)s --generate --save
  %(prog)s --generate --format json
  %(prog)s --generate --sections weather,tasks,quote
  %(prog)s --generate --date 2024-03-20
  %(prog)s --history
  %(prog)s --tasks-summary
  %(prog)s --config-show
  %(prog)s --config-set --key default_location --value Berlin
        """
    )
    
    parser.add_argument("--generate", action="store_true", help="Generate a daily briefing")
    parser.add_argument("--date", type=str, help="Date for briefing (YYYY-MM-DD)")
    parser.add_argument("--sections", type=str, help="Comma-separated sections to include")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--save", action="store_true", help="Save briefing to history")
    
    parser.add_argument("--history", action="store_true", help="Show briefing history")
    parser.add_argument("--tasks-summary", action="store_true", help="Show tasks summary")
    
    parser.add_argument("--config-show", action="store_true", help="Show configuration")
    parser.add_argument("--config-set", action="store_true", help="Update configuration")
    parser.add_argument("--key", type=str, help="Config key")
    parser.add_argument("--value", type=str, help="Config value")
    
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.generate:
        cmd_generate(args)
    elif args.history:
        cmd_history(args)
    elif args.tasks_summary:
        cmd_tasks_summary(args)
    elif args.config_show:
        cmd_config_show(args)
    elif args.config_set:
        cmd_config_set(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
