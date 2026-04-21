#!/usr/bin/env python3
"""
Sir HazeClaw Daily Habit Tracker
Tracks daily habits and streaks.

Habits:
- Morning Brief run
- Quality check (test_framework)
- Self-reflection done
- KG updated
- Backup verified

Usage:
    python3 habit_tracker.py
    python3 habit_tracker.py --check-in
    python3 habit_tracker.py --streaks
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
HABITS_FILE = WORKSPACE / "memory/habit_tracker.json"

# Habit definitions
HABITS = {
    'morning_brief': {
        'name': 'Morning Brief',
        'script': 'morning_brief.py',
        'frequency': 'daily',
        'time': 'before 10:00'
    },
    'test_framework': {
        'name': 'Test Framework',
        'script': 'test_framework.py',
        'frequency': 'daily',
        'time': 'after changes'
    },
    'self_eval': {
        'name': 'Self-Evaluation',
        'script': 'self_eval.py',
        'frequency': 'daily',
        'time': 'evening'
    },
    'deep_reflection': {
        'name': 'Deep Reflection',
        'script': 'deep_reflection.py',
        'frequency': 'weekly',
        'time': 'Sunday'
    },
    'kg_update': {
        'name': 'KG Update',
        'script': 'kg_updater.py',
        'frequency': 'daily',
        'time': 'after learning'
    },
    'backup_verify': {
        'name': 'Backup Verify',
        'script': 'backup_verify.py',
        'frequency': 'daily',
        'time': 'morning'
    },
    'health_check': {
        'name': 'Health Check',
        'script': 'health_monitor.py',
        'frequency': 'daily',
        'time': 'morning'
    },
    'cron_check': {
        'name': 'Cron Check',
        'script': 'cron_monitor.py',
        'frequency': 'daily',
        'time': 'morning'
    }
}

def load_habits():
    """Lädt Habit Tracker Daten."""
    if HABITS_FILE.exists():
        with open(HABITS_FILE) as f:
            return json.load(f)
    
    # Initialize with empty data
    return {
        'habits': {},
        'streaks': {},
        'last_updated': datetime.now().isoformat()
    }

def save_habits(data):
    """Speichert Habit Tracker Daten."""
    data['last_updated'] = datetime.now().isoformat()
    HABITS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(HABITS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def check_in(habit_key=None):
    """Check in für einen Habit."""
    data = load_habits()
    today = datetime.now().strftime('%Y-%m-%d')
    
    if habit_key:
        # Single habit
        habits_to_check = [habit_key]
    else:
        # All daily habits
        habits_to_check = [k for k, v in HABITS.items() 
                         if v['frequency'] == 'daily']
    
    for hk in habits_to_check:
        if hk not in data['habits']:
            data['habits'][hk] = {}
        
        if today not in data['habits'][hk]:
            data['habits'][hk][today] = []
        
        data['habits'][hk][today].append({
            'timestamp': datetime.now().isoformat(),
            'completed': True
        })
        
        # Update streak
        _update_streak(data, hk)
    
    save_habits(data)
    
    # Print status
    print(f"✅ Check-in recorded: {habit_key or 'all daily habits'}")
    print(f"   Time: {datetime.now().strftime('%H:%M')}")

def _update_streak(data, habit_key):
    """Berechnet Streak für einen Habit."""
    habit_data = data['habits'].get(habit_key, {})
    
    # Get all dates with completions
    dates = sorted(habit_data.keys(), reverse=True)
    
    streak = 0
    expected_date = datetime.now()
    
    for d in dates:
        date_dt = datetime.strptime(d, '%Y-%m-%d')
        
        # Check if this is consecutive
        diff = (expected_date.date() - date_dt.date()).days
        
        if diff <= 1:
            streak += 1
            expected_date = date_dt
        else:
            break
    
    data['streaks'][habit_key] = streak

def get_streaks():
    """Gibt alle Streaks zurück."""
    data = load_habits()
    streaks = {}
    
    for habit_key in HABITS.keys():
        _update_streak(data, habit_key)
        streaks[habit_key] = data['streaks'].get(habit_key, 0)
    
    return streaks

def get_today_status():
    """Gibt Status für heute zurück."""
    data = load_habits()
    today = datetime.now().strftime('%Y-%m-%d')
    
    status = {}
    for habit_key, habit_def in HABITS.items():
        if habit_key in data['habits'] and today in data['habits'][habit_key]:
            status[habit_key] = True
        else:
            status[habit_key] = False
    
    return status

def generate_report():
    """Generiert Habit Report."""
    streaks = get_streaks()
    today_status = get_today_status()
    
    # Count
    daily_habits = [k for k, v in HABITS.items() if v['frequency'] == 'daily']
    completed_today = sum(1 for k in daily_habits if today_status.get(k, False))
    
    lines = []
    lines.append("📊 **HABIT TRACKER**")
    lines.append(f"_Generated: {datetime.now().strftime('%H:%M')}_")
    lines.append("")
    
    # Today's progress
    lines.append(f"**Today:** {completed_today}/{len(daily_habits)} completed")
    
    # Progress bar
    bar_len = 10
    filled = int((completed_today / len(daily_habits)) * bar_len) if daily_habits else 0
    bar = '█' * filled + '░' * (bar_len - filled)
    lines.append(f"Progress: [{bar}]")
    lines.append("")
    
    # Daily habits
    lines.append("**Daily Habits:**")
    for habit_key in daily_habits:
        habit_def = HABITS[habit_key]
        done = today_status.get(habit_key, False)
        streak = streaks.get(habit_key, 0)
        
        emoji = "✅" if done else "⚪"
        streak_str = f" (🔥{streak})" if streak > 0 else ""
        
        lines.append(f"  {emoji} {habit_def['name']}{streak_str}")
    
    lines.append("")
    
    # Weekly habits
    weekly_habits = [k for k, v in HABITS.items() if v['frequency'] == 'weekly']
    if weekly_habits:
        lines.append("**Weekly Habits:**")
        for habit_key in weekly_habits:
            habit_def = HABITS[habit_key]
            streak = streaks.get(habit_key, 0)
            streak_str = f" (🔥{streak})" if streak > 0 else ""
            lines.append(f"  ⚪ {habit_def['name']}{streak_str}")
        lines.append("")
    
    # Overall streak
    total_streak = sum(streaks.values()) / len(streaks) if streaks else 0
    lines.append(f"**Average Streak:** {total_streak:.1f} days")
    
    return "\n".join(lines)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Habit Tracker')
    parser.add_argument('--check-in', nargs='?', const='', metavar='HABIT', help='Check in for habit')
    parser.add_argument('--streaks', action='store_true', help='Show streaks')
    parser.add_argument('--report', action='store_true', help='Generate report')
    args = parser.parse_args()
    
    if args.check_in is not None or args.streaks or args.report:
        pass  # Handled below
    else:
        # Default: show today's status
        streaks = get_streaks()
        today_status = get_today_status()
        daily_habits = [k for k, v in HABITS.items() if v['frequency'] == 'daily']
        completed = sum(1 for k in daily_habits if today_status.get(k, False))
        
        print(f"📊 Daily Habits: {completed}/{len(daily_habits)}")
        for k in daily_habits:
            emoji = "✅" if today_status.get(k, False) else "⚪"
            streak = streaks.get(k, 0)
            streak_str = f" 🔥{streak}" if streak > 0 else ""
            print(f"  {emoji} {HABITS[k]['name']}{streak_str}")

    if args.check_in is not None:
        check_in(args.check_in if args.check_in != '' else None)
    elif args.streaks:
        streaks = get_streaks()
        print("🔥 **Streaks:**")
        for k, v in streaks.items():
            print(f"  {HABITS[k]['name']}: {v} days")
    elif args.report:
        print(generate_report())
    else:
        # Default: show today's status
        streaks = get_streaks()
        today_status = get_today_status()
        daily_habits = [k for k, v in HABITS.items() if v['frequency'] == 'daily']
        completed = sum(1 for k in daily_habits if today_status.get(k, False))
        
        print(f"📊 Daily Habits: {completed}/{len(daily_habits)}")
        for k in daily_habits:
            emoji = "✅" if today_status.get(k, False) else "⚪"
            streak = streaks.get(k, 0)
            streak_str = f" 🔥{streak}" if streak > 0 else ""
            print(f"  {emoji} {HABITS[k]['name']}{streak_str}")

if __name__ == "__main__":
    main()
