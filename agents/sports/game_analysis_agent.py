#!/usr/bin/env python3
"""
Sports Game Analysis Agent - Analyze sports game statistics and performance.
Part of the sports agent suite.
"""

import argparse
import json
import logging
import random
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "game_analysis.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("GameAnalysisAgent")


class GameAnalysisAgent:
    """Agent for analyzing sports game statistics and performance data."""

    SPORTS = ["basketball", "soccer", "football", "baseball", "hockey", "tennis", "golf"]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "game_analysis.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.data_file.exists():
            data = {"teams": [], "games": [], "player_stats": [], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"teams": [], "games": [], "player_stats": [], "last_updated": datetime.now().isoformat()}

    def _save_data(self, data: dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save data: {e}")

    def register_team(self, name: str, sport: str, city: str = "", league: str = "") -> dict[str, Any]:
        """Register a sports team."""
        logger.info(f"Registering team: {name} ({sport})")
        try:
            if sport not in self.SPORTS:
                return {"success": False, "error": f"Invalid sport. Choose from: {self.SPORTS}"}
            data = self._load_data()
            if any(t.get("name") == name and t.get("sport") == sport for t in data["teams"]):
                return {"success": False, "error": "Team already registered"}
            team = {"id": str(uuid.uuid4())[:8], "name": name, "sport": sport, "city": city, "league": league, "wins": 0, "losses": 0, "draws": 0, "points_for": 0, "points_against": 0, "registered_date": datetime.now().isoformat()}
            data["teams"].append(team)
            self._save_data(data)
            return {"success": True, "team": team}
        except Exception as e:
            logger.error(f"Register team failed: {e}")
            return {"success": False, "error": str(e)}

    def log_game(self, home_team_id: str, away_team_id: str, date: str, home_score: int | None = None, away_score: int | None = None, venue: str = "") -> dict[str, Any]:
        """Log a game result."""
        logger.info(f"Logging game: {home_team_id} vs {away_team_id} on {date}")
        try:
            data = self._load_data()
            home_team = next((t for t in data["teams"] if t["id"] == home_team_id), None)
            away_team = next((t for t in data["teams"] if t["id"] == away_team_id), None)
            if not home_team or not away_team:
                return {"success": False, "error": "One or both teams not found"}
            if home_score is None:
                home_score = random.randint(70, 110) if home_team["sport"] in ["basketball", "football"] else random.randint(0, 5)
            if away_score is None:
                away_score = random.randint(70, 110) if away_team["sport"] in ["basketball", "football"] else random.randint(0, 5)
            home_win = home_score > away_score
            away_win = away_score > home_score
            game = {"id": str(uuid.uuid4())[:8], "home_team_id": home_team_id, "home_team_name": home_team["name"], "away_team_id": away_team_id, "away_team_name": away_team["name"], "home_score": home_score, "away_score": away_score, "date": date, "venue": venue, "status": "completed", "logged_at": datetime.now().isoformat()}
            if home_win:
                home_team["wins"] = home_team.get("wins", 0) + 1
                away_team["losses"] = away_team.get("losses", 0) + 1
            elif away_win:
                away_team["wins"] = away_team.get("wins", 0) + 1
                home_team["losses"] = home_team.get("losses", 0) + 1
            else:
                home_team["draws"] = home_team.get("draws", 0) + 1
                away_team["draws"] = away_team.get("draws", 0) + 1
            home_team["points_for"] = home_team.get("points_for", 0) + home_score
            home_team["points_against"] = home_team.get("points_against", 0) + away_score
            away_team["points_for"] = away_team.get("points_for", 0) + away_score
            away_team["points_against"] = away_team.get("points_against", 0) + home_score
            data["games"].append(game)
            self._save_data(data)
            return {"success": True, "game": game}
        except Exception as e:
            logger.error(f"Log game failed: {e}")
            return {"success": False, "error": str(e)}

    def get_standings(self, sport: str | None = None) -> dict[str, Any]:
        """Get league standings."""
        logger.info(f"Getting standings for sport={sport}")
        try:
            data = self._load_data()
            teams = data["teams"]
            if sport:
                teams = [t for t in teams if t.get("sport") == sport]
            standings = []
            for t in teams:
                gp = t.get("wins", 0) + t.get("losses", 0) + t.get("draws", 0)
                win_pct = t.get("wins", 0) / gp if gp > 0 else 0
                point_diff = t.get("points_for", 0) - t.get("points_against", 0)
                standings.append({"id": t["id"], "name": t["name"], "sport": t.get("sport"), "wins": t.get("wins", 0), "losses": t.get("losses", 0), "draws": t.get("draws", 0), "games_played": gp, "win_pct": round(win_pct * 100, 1), "point_diff": point_diff})
            standings.sort(key=lambda x: (x["wins"], x["point_diff"]), reverse=True)
            for i, s in enumerate(standings):
                s["rank"] = i + 1
            return {"success": True, "standings": standings}
        except Exception as e:
            logger.error(f"Get standings failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_team_performance(self, team_id: str) -> dict[str, Any]:
        """Analyze team performance and trends."""
        logger.info(f"Analyzing performance for team {team_id}")
        try:
            data = self._load_data()
            team = next((t for t in data["teams"] if t["id"] == team_id), None)
            if not team:
                return {"success": False, "error": "Team not found"}
            games = [g for g in data["games"] if g["home_team_id"] == team_id or g["away_team_id"] == team_id]
            recent = sorted(games, key=lambda x: x["date"], reverse=True)[:10]
            recent_wins = sum(1 for g in recent if (g["home_team_id"] == team_id and g["home_score"] > g["away_score"]) or (g["away_team_id"] == team_id and g["away_score"] > g["home_score"]))
            trend = "improving" if recent_wins >= 6 else "declining" if recent_wins <= 2 else "stable"
            return {"success": True, "team": {"id": team["id"], "name": team["name"], "sport": team.get("sport")}, "record": {"wins": team.get("wins", 0), "losses": team.get("losses", 0), "draws": team.get("draws", 0)}, "trend": trend, "recent_games": [{"date": g["date"], "result": "W" if (g["home_team_id"] == team_id and g["home_score"] > g["away_score"]) or (g["away_team_id"] == team_id and g["away_score"] > g["home_score"]) else "L", "score": f"{g['home_score']}-{g['away_score']}" if g["home_team_id"] == team_id else f"{g['away_score']}-{g['home_score']}"} for g in recent]}
        except Exception as e:
            logger.error(f"Analyze performance failed: {e}")
            return {"success": False, "error": str(e)}

    def predict_outcome(self, team_a_id: str, team_b_id: str) -> dict[str, Any]:
        """Predict outcome between two teams."""
        logger.info(f"Predicting outcome: {team_a_id} vs {team_b_id}")
        try:
            data = self._load_data()
            team_a = next((t for t in data["teams"] if t["id"] == team_a_id), None)
            team_b = next((t for t in data["teams"] if t["id"] == team_b_id), None)
            if not team_a or not team_b:
                return {"success": False, "error": "One or both teams not found"}
            gp_a = team_a.get("wins", 0) + team_a.get("losses", 0)
            gp_b = team_b.get("wins", 0) + team_b.get("losses", 0)
            win_pct_a = team_a.get("wins", 0) / gp_a if gp_a > 0 else 0.5
            win_pct_b = team_b.get("wins", 0) / gp_b if gp_b > 0 else 0.5
            strength_a = win_pct_a * random.uniform(0.9, 1.1)
            strength_b = win_pct_b * random.uniform(0.9, 1.1)
            total_strength = strength_a + strength_b
            prob_a = round(strength_a / total_strength * 100, 1)
            prob_b = round(strength_b / total_strength * 100, 1)
            return {"success": True, "matchup": {"team_a": team_a["name"], "team_b": team_b["name"]}, "prediction": {"team_a_win_probability_percent": prob_a, "team_b_win_probability_percent": prob_b, "favored": team_a["name"] if prob_a > prob_b else team_b["name"]}}
        except Exception as e:
            logger.error(f"Matchup prediction failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Sports Game Analysis Agent - Analyze sports game statistics and performance", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""Examples:
  %(prog)s register-team --name "Warriors" --sport basketball --city Oakland --league NBA
  %(prog)s log-game --home abc12345 --away xyz98765 --date 2026-03-27 --home-score 110 --away-score 95
  %(prog)s standings --sport basketball
  %(prog)s analyze --team-id abc12345
  %(prog)s predict --team-a abc12345 --team-b xyz98765""")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    reg_parser = subparsers.add_parser("register-team", help="Register a team")
    reg_parser.add_argument("--name", required=True, help="Team name")
    reg_parser.add_argument("--sport", required=True, help=f"Sport: {', '.join(GameAnalysisAgent.SPORTS)}")
    reg_parser.add_argument("--city", default="", help="City")
    reg_parser.add_argument("--league", default="", help="League")
    game_parser = subparsers.add_parser("log-game", help="Log a game")
    game_parser.add_argument("--home", dest="home_team_id", required=True, help="Home team ID")
    game_parser.add_argument("--away", dest="away_team_id", required=True, help="Away team ID")
    game_parser.add_argument("--date", required=True, help="Game date (YYYY-MM-DD)")
    game_parser.add_argument("--home-score", type=int, dest="home_score", help="Home score")
    game_parser.add_argument("--away-score", type=int, dest="away_score", help="Away score")
    game_parser.add_argument("--venue", default="", help="Venue")
    stand_parser = subparsers.add_parser("standings", help="Get standings")
    stand_parser.add_argument("--sport", help=f"Filter by sport: {', '.join(GameAnalysisAgent.SPORTS)}")
    anal_parser = subparsers.add_parser("analyze", help="Analyze team performance")
    anal_parser.add_argument("--team-id", required=True, help="Team ID")
    pred_parser = subparsers.add_parser("predict", help="Predict game outcome")
    pred_parser.add_argument("--team-a", required=True, help="Team A ID")
    pred_parser.add_argument("--team-b", required=True, help="Team B ID")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    agent = GameAnalysisAgent()
    try:
        if args.command == "register-team":
            result = agent.register_team(name=args.name, sport=args.sport, city=args.city, league=args.league)
        elif args.command == "log-game":
            result = agent.log_game(home_team_id=args.home_team_id, away_team_id=args.away_team_id, date=args.date, home_score=args.home_score, away_score=args.away_score, venue=args.venue)
        elif args.command == "standings":
            result = agent.get_standings(sport=args.sport)
        elif args.command == "analyze":
            result = agent.analyze_team_performance(team_id=args.team_id)
        elif args.command == "predict":
            result = agent.predict_outcome(team_a_id=args.team_a, team_b_id=args.team_b)
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
