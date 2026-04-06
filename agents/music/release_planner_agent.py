#!/usr/bin/env python3
"""
Music Release Planner Agent - Plan and track music releases, campaigns, and distribution.
Part of the music agent suite.
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
        logging.FileHandler(LOG_DIR / "release_planner.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("ReleasePlannerAgent")


class ReleasePlannerAgent:
    """Agent for planning and tracking music releases and distribution campaigns."""

    RELEASE_TYPES = ["single", "ep", "album", "compilation", "remix"]
    STATUSES = ["planned", "in_production", "mastered", "submitted", "approved", "released", "delayed"]
    DISTRIBUTION_PLATFORMS = ["spotify", "apple_music", "amazon_music", "youtube_music", "soundcloud", "tidal", "deezer", "pandora"]
    GENRES = ["pop", "rock", "hip-hop", "electronic", "jazz", "classical", "country", "r&b", "metal", "indie"]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "release_plans.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.data_file.exists():
            data = {"releases": [], "tasks": [], "campaigns": [], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"releases": [], "tasks": [], "campaigns": [], "last_updated": datetime.now().isoformat()}

    def _save_data(self, data: dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save data: {e}")

    def create_release_plan(self, title: str, artist_name: str, release_type: str,
                            genre: str, planned_release_date: str,
                            platforms: list[str] | None = None) -> dict[str, Any]:
        """Create a release plan."""
        logger.info(f"Creating release plan: {title} by {artist_name}")
        try:
            if release_type not in self.RELEASE_TYPES:
                return {"success": False, "error": f"Invalid release type. Choose from: {self.RELEASE_TYPES}"}
            if genre not in self.GENRES:
                return {"success": False, "error": f"Invalid genre. Choose from: {self.GENRES}"}
            platforms = platforms or self.DISTRIBUTION_PLATFORMS[:4]
            release = {
                "id": str(uuid.uuid4())[:8],
                "title": title, "artist_name": artist_name,
                "release_type": release_type, "genre": genre,
                "planned_release_date": planned_release_date,
                "actual_release_date": None, "status": "planned",
                "platforms": platforms, "track_count": 1 if release_type == "single" else 6 if release_type == "ep" else 10,
                "upc_code": f"UPC-{random.randint(10000000, 99999999)}",
                "isrc_code": f"ISRC-{random.randint(10000000, 99999999)}", "tasks": [], "created_date": datetime.now().isoformat()}
            data["releases"].append(release)
            self._add_release_tasks(data, release)
            self._save_data(data)
            return {"success": True, "release": release}
        except Exception as e:
            logger.error(f"Create release plan failed: {e}")
            return {"success": False, "error": str(e)}

    def _add_release_tasks(self, data: dict, release: dict) -> None:
        """Add standard release tasks."""
        release_date = datetime.strptime(release["planned_release_date"], "%Y-%m-%d")
        tasks_def = [
            ("Finalize master", -30, "Mixing & Mastering"),
            ("Submit to distribution", -21, "Distribution"),
            ("Create artwork", -28, "Design"),
            ("Write press release", -14, "PR"),
            ("Set up pre-save campaign", -14, "Marketing"),
            ("Notify press & media", -7, "PR"),
            ("Release day promotion", 0, "Marketing"),
            ("Post-release analytics", 7, "Analytics"),
        ]
        for task_name, days_offset, category in tasks_def:
            due_date = (release_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
            task = {"id": str(uuid.uuid4())[:8], "release_id": release["id"], "name": task_name, "category": category, "due_date": due_date, "status": "pending" if days_offset < 0 else "pending", "completed_at": None}
            data["tasks"].append(task)
            release["tasks"].append(task["id"])

    def update_release_status(self, release_id: str, status: str) -> dict[str, Any]:
        """Update release status."""
        logger.info(f"Updating release {release_id} to status {status}")
        try:
            if status not in self.STATUSES:
                return {"success": False, "error": f"Invalid status. Choose from: {self.STATUSES}"}
            data = self._load_data()
            release = next((r for r in data["releases"] if r["id"] == release_id), None)
            if not release:
                return {"success": False, "error": "Release not found"}
            release["status"] = status
            if status == "released":
                release["actual_release_date"] = datetime.now().strftime("%Y-%m-%d")
            self._save_data(data)
            return {"success": True, "release": release}
        except Exception as e:
            logger.error(f"Update release status failed: {e}")
            return {"success": False, "error": str(e)}

    def get_release_timeline(self, release_id: str) -> dict[str, Any]:
        """Get release timeline with tasks."""
        logger.info(f"Getting timeline for release {release_id}")
        try:
            data = self._load_data()
            release = next((r for r in data["releases"] if r["id"] == release_id), None)
            if not release:
                return {"success": False, "error": "Release not found"}
            tasks = [t for t in data["tasks"] if t.get("release_id") == release_id]
            tasks.sort(key=lambda x: x.get("due_date", ""))
            return {"success": True, "release": {"id": release["id"], "title": release["title"], "artist_name": release["artist_name"], "planned_release_date": release["planned_release_date"], "status": release["status"]}, "tasks": [{"id": t["id"], "name": t["name"], "category": t["category"], "due_date": t["due_date"], "status": t["status"]} for t in tasks]}
        except Exception as e:
            logger.error(f"Get timeline failed: {e}")
            return {"success": False, "error": str(e)}

    def list_releases(self, status: str | None = None) -> dict[str, Any]:
        """List all releases."""
        logger.info(f"Listing releases with status={status}")
        try:
            data = self._load_data()
            releases = data["releases"]
            if status:
                if status not in self.STATUSES:
                    return {"success": False, "error": f"Invalid status. Choose from: {self.STATUSES}"}
                releases = [r for r in releases if r.get("status") == status]
            summaries = [{"id": r["id"], "title": r["title"], "artist_name": r["artist_name"], "release_type": r["release_type"], "genre": r["genre"], "planned_release_date": r["planned_release_date"], "status": r["status"], "platforms": r.get("platforms", [])} for r in releases]
            return {"success": True, "releases": summaries, "count": len(summaries)}
        except Exception as e:
            logger.error(f"List releases failed: {e}")
            return {"success": False, "error": str(e)}

    def get_upcoming_releases(self, days: int = 30) -> dict[str, Any]:
        """Get upcoming releases within a time window."""
        logger.info(f"Getting upcoming releases in next {days} days")
        try:
            data = self._load_data()
            cutoff = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            upcoming = [r for r in data["releases"] if r["planned_release_date"] <= cutoff and r["status"] not in ["released", "delayed"]]
            upcoming.sort(key=lambda x: x["planned_release_date"])
            return {"success": True, "upcoming_releases": [{"id": r["id"], "title": r["title"], "artist_name": r["artist_name"], "release_date": r["planned_release_date"], "days_until_release": (datetime.strptime(r["planned_release_date"], "%Y-%m-%d") - datetime.now()).days} for r in upcoming], "count": len(upcoming)}
        except Exception as e:
            logger.error(f"Get upcoming releases failed: {e}")
            return {"success": False, "error": str(e)}

    def create_campaign(self, release_id: str, campaign_type: str,
                        start_date: str, end_date: str | None = None) -> dict[str, Any]:
        """Create a marketing campaign for a release."""
        logger.info(f"Creating campaign for release {release_id}: {campaign_type}")
        try:
            data = self._load_data()
            release = next((r for r in data["releases"] if r["id"] == release_id), None)
            if not release:
                return {"success": False, "error": "Release not found"}
            campaign = {"id": str(uuid.uuid4())[:8], "release_id": release_id, "release_title": release["title"], "campaign_type": campaign_type, "start_date": start_date, "end_date": end_date or (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=14)).strftime("%Y-%m-%d"), "budget_usd": 0, "status": "planned", "channels": [], "created_date": datetime.now().isoformat()}
            data["campaigns"].append(campaign)
            self._save_data(data)
            return {"success": True, "campaign": campaign}
        except Exception as e:
            logger.error(f"Create campaign failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Music Release Planner Agent - Plan and track music releases", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""Examples:
  %(prog)s create --title "New Single" --artist "Test Artist" --type single --genre pop --date 2026-05-01
  %(prog)s status --release-id abc12345 --status mastered
  %(prog)s timeline --release-id abc12345
  %(prog)s list
  %(prog)s list --status planned
  %(prog)s upcoming --days 60
  %(prog)s campaign --release-id abc12345 --type pre-release --start 2026-04-15""")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    create_parser = subparsers.add_parser("create", help="Create release plan")
    create_parser.add_argument("--title", required=True, help="Release title")
    create_parser.add_argument("--artist", dest="artist_name", required=True, help="Artist name")
    create_parser.add_argument("--type", dest="release_type", required=True, help=f"Type: {', '.join(ReleasePlannerAgent.RELEASE_TYPES)}")
    create_parser.add_argument("--genre", required=True, help=f"Genre: {', '.join(ReleasePlannerAgent.GENRES)}")
    create_parser.add_argument("--date", dest="planned_release_date", required=True, help="Planned release date (YYYY-MM-DD)")
    create_parser.add_argument("--platforms", help="Comma-separated platforms")
    status_parser = subparsers.add_parser("status", help="Update release status")
    status_parser.add_argument("--release-id", required=True, help="Release ID")
    status_parser.add_argument("--status", required=True, help=f"Status: {', '.join(ReleasePlannerAgent.STATUSES)}")
    timeline_parser = subparsers.add_parser("timeline", help="Get release timeline")
    timeline_parser.add_argument("--release-id", required=True, help="Release ID")
    list_parser = subparsers.add_parser("list", help="List releases")
    list_parser.add_argument("--status", help=f"Filter by status: {', '.join(ReleasePlannerAgent.STATUSES)}")
    upcoming_parser = subparsers.add_parser("upcoming", help="Get upcoming releases")
    upcoming_parser.add_argument("--days", type=int, default=30, help="Days to look ahead")
    campaign_parser = subparsers.add_parser("campaign", help="Create marketing campaign")
    campaign_parser.add_argument("--release-id", required=True, help="Release ID")
    campaign_parser.add_argument("--type", dest="campaign_type", required=True, help="Campaign type")
    campaign_parser.add_argument("--start", dest="start_date", required=True, help="Start date (YYYY-MM-DD)")
    campaign_parser.add_argument("--end", dest="end_date", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    agent = ReleasePlannerAgent()
    try:
        if args.command == "create":
            platforms = [p.strip() for p in args.platforms.split(",")] if args.platforms else None
            result = agent.create_release_plan(title=args.title, artist_name=args.artist_name, release_type=args.release_type, genre=args.genre, planned_release_date=args.planned_release_date, platforms=platforms)
        elif args.command == "status":
            result = agent.update_release_status(release_id=args.release_id, status=args.status)
        elif args.command == "timeline":
            result = agent.get_release_timeline(release_id=args.release_id)
        elif args.command == "list":
            result = agent.list_releases(status=args.status)
        elif args.command == "upcoming":
            result = agent.get_upcoming_releases(days=args.days)
        elif args.command == "campaign":
            result = agent.create_campaign(release_id=args.release_id, campaign_type=args.campaign_type, start_date=args.start_date, end_date=args.end_date)
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
