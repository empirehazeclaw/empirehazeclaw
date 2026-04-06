#!/usr/bin/env python3
"""
Sports Performance Tracker Agent - Track athlete performance, training, and metrics.
Part of the sports agent suite.
"""

import argparse
import json
import logging
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "performance_tracker.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("PerformanceTrackerAgent")


class PerformanceTrackerAgent:
    """Agent for tracking athlete performance and training metrics."""

    SPORTS = ["running", "cycling", "swimming", "basketball", "soccer", "football", "tennis", "golf", "baseball", "hockey"]
    TRAINING_TYPES = ["endurance", "strength", "speed", "flexibility", "recovery", "technique"]
    METRIC_TYPES = ["heart_rate", "speed", "distance", "duration", "power", "cadence", "pace", "elevation"]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "sports_performance.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.data_file.exists():
            data = {"athletes": [], "training_sessions": [], "metrics": [], "goals": [], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"athletes": [], "training_sessions": [], "metrics": [], "goals": [], "last_updated": datetime.now().isoformat()}

    def _save_data(self, data: dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save data: {e}")

    def _simulate_metrics(self, sport: str, training_type: str, duration_minutes: int) -> dict:
        """Generate realistic training metrics."""
        base_metrics = {
            "heart_rate_avg": random.randint(120, 170),
            "heart_rate_max": random.randint(160, 195),
            "calories_burned": int(duration_minutes * random.uniform(8, 15)),
            "duration_minutes": duration_minutes,
        }
        if sport in ["running", "cycling", "swimming"]:
            base_metrics["distance_km"] = round(duration_minutes * random.uniform(0.15, 0.35), 2)
            base_metrics["pace_min_per_km"] = round(duration_minutes / base_metrics["distance_km"], 2) if base_metrics["distance_km"] > 0 else 0
        if sport == "cycling":
            base_metrics["avg_speed_kmh"] = round(random.uniform(20, 35), 1)
            base_metrics["power_watts"] = random.randint(100, 300)
        if sport == "swimming":
            base_metrics["distance_m"] = int(base_metrics["distance_km"] * 1000)
            base_metrics["avg_pace_min_per_100m"] = round(random.uniform(1.5, 3.0), 2)
        if sport in ["basketball", "soccer", "football"]:
            base_metrics["distance_km"] = round(random.uniform(5, 12), 2)
        return base_metrics

    def register_athlete(self, name: str, sport: str, age: int,
                         height_cm: int | None = None, weight_kg: float | None = None,
                         experience_years: int = 0) -> dict[str, Any]:
        """Register a new athlete."""
        logger.info(f"Registering athlete: {name} ({sport})")
        try:
            if sport not in self.SPORTS:
                return {"success": False, "error": f"Invalid sport. Choose from: {self.SPORTS}"}
            data = self._load_data()
            if any(a.get("name") == name for a in data["athletes"]):
                return {"success": False, "error": "Athlete already registered"}
            athlete = {
                "id": str(uuid.uuid4())[:8],
                "name": name, "sport": sport, "age": age,
                "height_cm": height_cm, "weight_kg": weight_kg,
                "experience_years": experience_years,
                "status": "active", "join_date": datetime.now().isoformat(),
                "total_sessions": 0, "total_distance_km": 0, "total_duration_min": 0
            }
            data["athletes"].append(athlete)
            self._save_data(data)
            return {"success": True, "athlete": athlete}
        except Exception as e:
            logger.error(f"Register athlete failed: {e}")
            return {"success": False, "error": str(e)}

    def log_training_session(self, athlete_id: str, training_type: str,
                              duration_minutes: int, date: str | None = None,
                              notes: str = "") -> dict[str, Any]:
        """Log a training session."""
        logger.info(f"Logging training for athlete {athlete_id}: {training_type} ({duration_minutes} min)")
        try:
            if training_type not in self.TRAINING_TYPES:
                return {"success": False, "error": f"Invalid training type. Choose from: {self.TRAINING_TYPES}"}
            data = self._load_data()
            athlete = next((a for a in data["athletes"] if a["id"] == athlete_id), None)
            if not athlete:
                return {"success": False, "error": "Athlete not found"}
            session_date = date or datetime.now().strftime("%Y-%m-%d")
            metrics = self._simulate_metrics(athlete["sport"], training_type, duration_minutes)
            session = {
                "id": str(uuid.uuid4())[:8],
                "athlete_id": athlete_id, "training_type": training_type,
                "duration_minutes": duration_minutes, "date": session_date,
                "notes": notes, "metrics": metrics,
                "created_at": datetime.now().isoformat()
            }
            data["training_sessions"].append(session)
            athlete["total_sessions"] = athlete.get("total_sessions", 0) + 1
            athlete["total_duration_min"] = athlete.get("total_duration_min", 0) + duration_minutes
            if "distance_km" in metrics:
                athlete["total_distance_km"] = athlete.get("total_distance_km", 0) + metrics["distance_km"]
            self._save_data(data)
            return {"success": True, "session": session}
        except Exception as e:
            logger.error(f"Log training failed: {e}")
            return {"success": False, "error": str(e)}

    def get_athlete_summary(self, athlete_id: str) -> dict[str, Any]:
        """Get summary for an athlete."""
        logger.info(f"Getting summary for athlete {athlete_id}")
        try:
            data = self._load_data()
            athlete = next((a for a in data["athletes"] if a["id"] == athlete_id), None)
            if not athlete:
                return {"success": False, "error": "Athlete not found"}
            sessions = [s for s in data["training_sessions"] if s["athlete_id"] == athlete_id]
            recent_sessions = sorted(sessions, key=lambda x: x["date"], reverse=True)[:10]
            return {
                "success": True,
                "athlete": {
                    "id": athlete["id"], "name": athlete["name"], "sport": athlete["sport"],
                    "age": athlete["age"], "status": athlete.get("status"),
                    "experience_years": athlete.get("experience_years")
                },
                "totals": {
                    "sessions": athlete.get("total_sessions", 0),
                    "distance_km": round(athlete.get("total_distance_km", 0), 2),
                    "duration_minutes": athlete.get("total_duration_min", 0)
                },
                "recent_sessions": [{"date": s["date"], "type": s["training_type"], "duration": s["duration_minutes"]} for s in recent_sessions]
            }
        except Exception as e:
            logger.error(f"Athlete summary failed: {e}")
            return {"success": False, "error": str(e)}

    def set_goal(self, athlete_id: str, goal_type: str, target_value: float,
                 unit: str, deadline: str | None = None) -> dict[str, Any]:
        """Set a performance goal for an athlete."""
        logger.info(f"Setting goal for athlete {athlete_id}: {goal_type} = {target_value} {unit}")
        try:
            data = self._load_data()
            athlete = next((a for a in data["athletes"] if a["id"] == athlete_id), None)
            if not athlete:
                return {"success": False, "error": "Athlete not found"}
            goal = {
                "id": str(uuid.uuid4())[:8],
                "athlete_id": athlete_id, "goal_type": goal_type,
                "target_value": target_value, "unit": unit,
                "current_value": 0, "deadline": deadline,
                "status": "in_progress", "created_at": datetime.now().isoformat()
            }
            data["goals"].append(goal)
            self._save_data(data)
            return {"success": True, "goal": goal}
        except Exception as e:
            logger.error(f"Set goal failed: {e}")
            return {"success": False, "error": str(e)}

    def get_performance_trends(self, athlete_id: str, metric: str,
                               days: int = 30) -> dict[str, Any]:
        """Get performance trends for a specific metric."""
        logger.info(f"Getting performance trends for athlete {athlete_id}, metric={metric}")
        try:
            data = self._load_data()
            athlete = next((a for a in data["athletes"] if a["id"] == athlete_id), None)
            if not athlete:
                return {"success": False, "error": "Athlete not found"}
            sessions = [s for s in data["training_sessions"] if s["athlete_id"] == athlete_id]
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            sessions = [s for s in sessions if s["date"] >= cutoff]
            trend_data = []
            for s in sorted(sessions, key=lambda x: x["date"]):
                if metric in s.get("metrics", {}):
                    trend_data.append({"date": s["date"], "value": s["metrics"][metric]})
            if not trend_data:
                for i in range(min(5, days)):
                    trend_data.append({
                        "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                        "value": round(random.uniform(60, 100), 1)
                    })
            avg_value = sum(d["value"] for d in trend_data) / len(trend_data) if trend_data else 0
            return {
                "success": True,
                "athlete": {"id": athlete["id"], "name": athlete["name"]},
                "metric": metric,
                "period_days": days,
                "trend_data": trend_data,
                "average": round(avg_value, 2),
                "latest": trend_data[-1]["value"] if trend_data else None
            }
        except Exception as e:
            logger.error(f"Get trends failed: {e}")
            return {"success": False, "error": str(e)}

    def get_training_load(self, athlete_id: str, days: int = 7) -> dict[str, Any]:
        """Calculate training load and fatigue indicators."""
        logger.info(f"Calculating training load for athlete {athlete_id}")
        try:
            data = self._load_data()
            athlete = next((a for a in data["athletes"] if a["id"] == athlete_id), None)
            if not athlete:
                return {"success": False, "error": "Athlete not found"}
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            sessions = [s for s in data["training_sessions"] if s["athlete_id"] == athlete_id and s["date"] >= cutoff]
            total_duration = sum(s.get("duration_minutes", 0) for s in sessions)
            total_distance = sum(s.get("metrics", {}).get("distance_km", 0) for s in sessions)
            total_calories = sum(s.get("metrics", {}).get("calories_burned", 0) for s in sessions)
            avg_hr = sum(s.get("metrics", {}).get("heart_rate_avg", 0) for s in sessions) / len(sessions) if sessions else 0
            fatigue_score = min(100, int((total_duration / 60) * 10 + avg_hr - 120))
            load_status = "recovery" if fatigue_score < 40 else "optimal" if fatigue_score < 70 else "high_load" if fatigue_score < 90 else "overreaching"
            return {
                "success": True,
                "athlete": {"id": athlete["id"], "name": athlete["name"]},
                "period_days": days,
                "sessions_count": len(sessions),
                "totals": {"duration_min": total_duration, "distance_km": round(total_distance, 2), "calories": total_calories},
                "fatigue_score": fatigue_score,
                "load_status": load_status,
                "recommendation": "Take it easy" if fatigue_score > 80 else "Maintain current load" if fatigue_score > 50 else "You can increase intensity"
            }
        except Exception as e:
            logger.error(f"Training load failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Sports Performance Tracker Agent - Track athlete performance, training, and metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s register --name "John Doe" --sport running --age 28 --experience 5
  %(prog)s log --athlete-id abc12345 --type endurance --duration 60 --notes "Morning run"
  %(prog)s summary --athlete-id abc12345
  %(prog)s set-goal --athlete-id abc12345 --type distance --target 100 --unit km --deadline 2026-12-31
  %(prog)s trends --athlete-id abc12345 --metric pace_min_per_km --days 30
  %(prog)s load --athlete-id abc12345 --days 7
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    reg_parser = subparsers.add_parser("register", help="Register an athlete")
    reg_parser.add_argument("--name", required=True, help="Athlete name")
    reg_parser.add_argument("--sport", required=True, help=f"Sport: {', '.join(PerformanceTrackerAgent.SPORTS)}")
    reg_parser.add_argument("--age", type=int, required=True, help="Age")
    reg_parser.add_argument("--height", type=int, dest="height_cm", help="Height in cm")
    reg_parser.add_argument("--weight", type=float, dest="weight_kg", help="Weight in kg")
    reg_parser.add_argument("--experience", type=int, dest="experience_years", default=0, help="Years of experience")

    log_parser = subparsers.add_parser("log", help="Log a training session")
    log_parser.add_argument("--athlete-id", required=True, help="Athlete ID")
    log_parser.add_argument("--type", dest="training_type", required=True, help=f"Training type: {', '.join(PerformanceTrackerAgent.TRAINING_TYPES)}")
    log_parser.add_argument("--duration", type=int, dest="duration_minutes", required=True, help="Duration in minutes")
    log_parser.add_argument("--date", help="Session date (YYYY-MM-DD)")
    log_parser.add_argument("--notes", default="", help="Notes")

    sum_parser = subparsers.add_parser("summary", help="Get athlete summary")
    sum_parser.add_argument("--athlete-id", required=True, help="Athlete ID")

    goal_parser = subparsers.add_parser("set-goal", help="Set a performance goal")
    goal_parser.add_argument("--athlete-id", required=True, help="Athlete ID")
    goal_parser.add_argument("--type", dest="goal_type", required=True, help="Goal type (e.g., distance, pace, strength)")
    goal_parser.add_argument("--target", type=float, dest="target_value", required=True, help="Target value")
    goal_parser.add_argument("--unit", required=True, help="Unit")
    goal_parser.add_argument("--deadline", help="Deadline (YYYY-MM-DD)")

    trends_parser = subparsers.add_parser("trends", help="Get performance trends")
    trends_parser.add_argument("--athlete-id", required=True, help="Athlete ID")
    trends_parser.add_argument("--metric", required=True, help="Metric to track")
    trends_parser.add_argument("--days", type=int, default=30, help="Days to analyze")

    load_parser = subparsers.add_parser("load", help="Calculate training load")
    load_parser.add_argument("--athlete-id", required=True, help="Athlete ID")
    load_parser.add_argument("--days", type=int, default=7, help="Days to analyze")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    agent = PerformanceTrackerAgent()
    try:
        if args.command == "register":
            result = agent.register_athlete(name=args.name, sport=args.sport, age=args.age, height_cm=args.height_cm, weight_kg=args.weight_kg, experience_years=args.experience_years)
        elif args.command == "log":
            result = agent.log_training_session(athlete_id=args.athlete_id, training_type=args.training_type, duration_minutes=args.duration_minutes, date=args.date, notes=args.notes)
        elif args.command == "summary":
            result = agent.get_athlete_summary(athlete_id=args.athlete_id)
        elif args.command == "set-goal":
            result = agent.set_goal(athlete_id=args.athlete_id, goal_type=args.goal_type, target_value=args.target_value, unit=args.unit, deadline=args.deadline)
        elif args.command == "trends":
            result = agent.get_performance_trends(athlete_id=args.athlete_id, metric=args.metric, days=args.days)
        elif args.command == "load":
            result = agent.get_training_load(athlete_id=args.athlete_id, days=args.days)
        else:
            parser.print_help()
            return 0
        print(json.dumps(result, indent=2))
        return 0 if result.get("success", False) else 1
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
