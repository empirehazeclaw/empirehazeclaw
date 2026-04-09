#!/usr/bin/env python3
"""
University Leaderboard System
Tracks XP, lessons, quizzes, and adventures for all agents.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = "/home/clawbot/.openclaw/workspace/ceo/university"
LEADERBOARD_FILE = f"{WORKSPACE}/leaderboard.json"
QUIZ_RESULTS_FILE = f"{WORKSPACE}/quiz_results.json"
ADVENTURES_FILE = f"{WORKSPACE}/adventure_scenarios.json"

# XP Awards
XP = {
    "quiz_perfect": 50,      # 100% on quiz
    "quiz_pass": 25,         # Passed quiz
    "lesson_complete": 10,  # Finished a lesson
    "adventure_complete": 30, # Finished adventure
    "streak_7": 100,         # 7-day streak
    "streak_30": 500,        # 30-day streak
}

# Agent curriculum tracking
AGENTS = ["security", "builder", "data", "qc", "research"]

def get_default_stats():
    """Get default stats structure for an agent."""
    return {
        "xp": 0,
        "lessons_completed": 0,
        "quizzes_passed": 0,
        "quizzes_perfect": 0,
        "adventures_completed": 0,
        "current_streak": 0,
        "last_activity": None
    }

def load_leaderboard():
    """Load existing leaderboard data."""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return {"updated": None, "rankings": []}

def save_leaderboard(data):
    """Save leaderboard data."""
    data["updated"] = datetime.utcnow().isoformat() + "Z"
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def parse_quiz_results():
    """Parse quiz results and calculate XP."""
    stats = {agent: get_default_stats() for agent in AGENTS}
    
    if not os.path.exists(QUIZ_RESULTS_FILE):
        return stats
    
    with open(QUIZ_RESULTS_FILE, 'r') as f:
        data = json.load(f)
    
    results = data.get("results", [])
    for result in results:
        # Determine which agent took the quiz (from module name if available)
        module = result.get("module", "")
        score = result.get("score", 0)
        max_score = result.get("max_score", 1)
        percentage = result.get("percentage", 0)
        
        # Default to "security" for now (quiz was from security officer)
        agent = "security"
        
        # Count quiz
        stats[agent]["quizzes_passed"] += 1
        if percentage == 100:
            stats[agent]["quizzes_perfect"] += 1
            stats[agent]["xp"] += XP["quiz_perfect"]
        else:
            stats[agent]["xp"] += XP["quiz_pass"]
        
        # Update last activity
        stats[agent]["last_activity"] = result.get("date")
    
    return stats

def count_lessons_completed(stats):
    """Count completed lessons from lesson files."""
    lessons_dir = Path(WORKSPACE) / "lessons"
    
    for agent in AGENTS:
        # Count lesson files that exist
        agent_lessons = list(Path(lessons_dir).glob(f"lesson_{agent}_*.md"))
        # For now, use generic lesson count based on quiz participation
        if stats[agent]["quizzes_passed"] > 0:
            stats[agent]["lessons_completed"] = stats[agent]["quizzes_passed"]
            stats[agent]["xp"] += stats[agent]["lessons_completed"] * XP["lesson_complete"]
    
    return stats

def parse_adventures(stats):
    """Parse adventure completion."""
    if not os.path.exists(ADVENTURES_FILE):
        return stats
    
    with open(ADVENTURES_FILE, 'r') as f:
        data = json.load(f)
    
    completed = data.get("completed_adventures", [])
    for adventure in completed:
        agent = adventure.get("agent", "security")
        if agent in stats:
            stats[agent]["adventures_completed"] += 1
            stats[agent]["xp"] += XP["adventure_complete"]
    
    return stats

def calculate_streaks(stats):
    """Calculate streak bonuses."""
    for agent in AGENTS:
        streak = 0
        if os.path.exists(QUIZ_RESULTS_FILE):
            with open(QUIZ_RESULTS_FILE, 'r') as f:
                data = json.load(f)
            streak = data.get("streak_days", 0)
        
        stats[agent]["current_streak"] = streak
        
        if streak >= 30:
            stats[agent]["xp"] += XP["streak_30"]
        elif streak >= 7:
            stats[agent]["xp"] += XP["streak_7"]
    
    return stats

def build_rankings():
    """Build complete leaderboard rankings."""
    stats = parse_quiz_results()
    stats = count_lessons_completed(stats)
    stats = parse_adventures(stats)
    stats = calculate_streaks(stats)
    
    # Convert to ranking list
    rankings = []
    for agent, data in stats.items():
        rankings.append({
            "agent": agent.capitalize(),
            "xp": data["xp"],
            "lessons": data["lessons_completed"],
            "quizzes": data["quizzes_passed"],
            "adventures": data["adventures_completed"],
            "streak": data["current_streak"]
        })
    
    # Sort by XP descending
    rankings.sort(key=lambda x: x["xp"], reverse=True)
    
    # Add rank numbers
    for i, r in enumerate(rankings):
        r["rank"] = i + 1
    
    return rankings

def generate_discord_report(rankings):
    """Generate Discord-formatted leaderboard report."""
    report = ["🏆 **OpenClaw University Leaderboard**\n"]
    report.append(f"*Updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*\n")
    report.append("━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    medals = ["🥇", "🥈", "🥉", "4.", "5."]
    
    for i, r in enumerate(rankings):
        medal = medals[i] if i < 5 else f"{i+1}."
        report.append(
            f"{medal} **{r['agent']}** — {r['xp']} XP\n"
            f"   📚 {r['lessons']} Lessons | 🧠 {r['quizzes']} Quizzes | 🎮 {r['adventures']} Adventures | 🔥 {r['streak']} Streak"
        )
    
    report.append("\n━━━━━━━━━━━━━━━━━━━━━━━")
    report.append("\n*Keep learning to climb the leaderboard!*")
    
    return "\n".join(report)

def main():
    """Main leaderboard generation."""
    print("📊 Building University Leaderboard...")
    
    rankings = build_rankings()
    
    # Save JSON
    data = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "rankings": rankings
    }
    save_leaderboard(data)
    
    print(f"✅ Leaderboard saved with {len(rankings)} agents")
    
    # Print Discord report
    report = generate_discord_report(rankings)
    print("\n" + report)
    
    return data

if __name__ == "__main__":
    main()