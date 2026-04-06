#!/usr/bin/env python3
"""
Music Royalty Tracker Agent - Track music royalties, streams, and revenue.
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
        logging.FileHandler(LOG_DIR / "royalty_tracker.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("RoyaltyTrackerAgent")


class RoyaltyTrackerAgent:
    """Agent for tracking music royalties, streams, and revenue across platforms."""

    PLATFORMS = ["spotify", "apple_music", "youtube_music", "amazon_music", "soundcloud", "tidal", "deezer"]
    ROYALTY_TYPES = ["streaming", "mechanical", "performance", "sync", "print"]
    STATUSES = ["pending", "processing", "paid", "disputed"]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "royalty_data.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.data_file.exists():
            data = {"tracks": [], "royalty_payments": [], "stream_records": [], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"tracks": [], "royalty_payments": [], "stream_records": [], "last_updated": datetime.now().isoformat()}

    def _save_data(self, data: dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save data: {e}")

    def register_track(self, title: str, artist_name: str, isrc: str,
                       album_name: str = "", genre: str = "") -> dict[str, Any]:
        """Register a track for royalty tracking."""
        logger.info(f"Registering track: {title} by {artist_name}")
        try:
            data = self._load_data()
            if any(t.get("isrc") == isrc for t in data["tracks"]):
                return {"success": False, "error": "Track with this ISRC already registered"}
            track = {
                "id": str(uuid.uuid4())[:8],
                "title": title, "artist_name": artist_name,
                "isrc": isrc, "album_name": album_name, "genre": genre,
                "total_streams": 0, "total_revenue_usd": 0,
                "registration_date": datetime.now().isoformat()
            }
            data["tracks"].append(track)
            self._save_data(data)
            return {"success": True, "track": track}
        except Exception as e:
            logger.error(f"Register track failed: {e}")
            return {"success": False, "error": str(e)}

    def log_streams(self, track_id: str, platform: str, stream_count: int,
                    period_start: str | None = None, period_end: str | None = None) -> dict[str, Any]:
        """Log streaming data for a track."""
        logger.info(f"Logging {stream_count} streams on {platform} for track {track_id}")
        try:
            if platform not in self.PLATFORMS:
                return {"success": False, "error": f"Invalid platform. Choose from: {self.PLATFORMS}"}
            data = self._load_data()
            track = next((t for t in data["tracks"] if t["id"] == track_id), None)
            if not track:
                return {"success": False, "error": "Track not found"}
            if period_start is None:
                period_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            if period_end is None:
                period_end = datetime.now().strftime("%Y-%m-%d")
            rate_per_stream = {"spotify": 0.003, "apple_music": 0.008, "youtube_music": 0.002, "amazon_music": 0.004, "soundcloud": 0.003, "tidal": 0.012, "deezer": 0.004}
            revenue = round(stream_count * rate_per_stream.get(platform, 0.004), 2)
            record = {
                "id": str(uuid.uuid4())[:8],
                "track_id": track_id, "track_title": track["title"],
                "platform": platform, "stream_count": stream_count,
                "revenue_usd": revenue, "rate_per_stream": rate_per_stream.get(platform, 0.004),
                "period_start": period_start, "period_end": period_end,
                "logged_at": datetime.now().isoformat()
            }
            data["stream_records"].append(record)
            track["total_streams"] = track.get("total_streams", 0) + stream_count
            track["total_revenue_usd"] = track.get("total_revenue_usd", 0) + revenue
            self._save_data(data)
            return {"success": True, "record": record, "track": {"id": track["id"], "total_streams": track["total_streams"], "total_revenue_usd": track["total_revenue_usd"]}}
        except Exception as e:
            logger.error(f"Log streams failed: {e}")
            return {"success": False, "error": str(e)}

    def get_track_earnings(self, track_id: str) -> dict[str, Any]:
        """Get detailed earnings for a track."""
        logger.info(f"Getting earnings for track {track_id}")
        try:
            data = self._load_data()
            track = next((t for t in data["tracks"] if t["id"] == track_id), None)
            if not track:
                return {"success": False, "error": "Track not found"}
            records = [r for r in data["stream_records"] if r["track_id"] == track_id]
            platform_breakdown = {}
            for r in records:
                platform_breakdown[r["platform"]] = platform_breakdown.get(r["platform"], 0) + r["revenue_usd"]
            return {"success": True, "track": {"id": track["id"], "title": track["title"], "artist_name": track["artist_name"], "isrc": track["isrc"]}, "totals": {"streams": track.get("total_streams", 0), "revenue_usd": round(track.get("total_revenue_usd", 0), 2)}, "platform_breakdown": {k: round(v, 2) for k, v in platform_breakdown.items()}, "record_count": len(records)}
        except Exception as e:
            logger.error(f"Get track earnings failed: {e}")
            return {"success": False, "error": str(e)}

    def get_artist_earnings(self, artist_name: str) -> dict[str, Any]:
        """Get earnings for all tracks by an artist."""
        logger.info(f"Getting earnings for artist: {artist_name}")
        try:
            data = self._load_data()
            tracks = [t for t in data["tracks"] if t["artist_name"].lower() == artist_name.lower()]
            if not tracks:
                return {"success": False, "error": "No tracks found for this artist"}
            total_streams = sum(t.get("total_streams", 0) for t in tracks)
            total_revenue = sum(t.get("total_revenue_usd", 0) for t in tracks)
            return {"success": True, "artist_name": artist_name, "track_count": len(tracks), "tracks": [{"id": t["id"], "title": t["title"], "streams": t.get("total_streams", 0), "revenue_usd": round(t.get("total_revenue_usd", 0), 2)} for t in tracks], "totals": {"streams": total_streams, "revenue_usd": round(total_revenue, 2)}}
        except Exception as e:
            logger.error(f"Get artist earnings failed: {e}")
            return {"success": False, "error": str(e)}

    def get_revenue_report(self, period: str = "monthly") -> dict[str, Any]:
        """Get revenue report for a period."""
        logger.info(f"Getting {period} revenue report")
        try:
            data = self._load_data()
            records = data["stream_records"]
            if period == "daily":
                cutoff = (datetime.now() - timedelta(days=1)).isoformat()
            elif period == "weekly":
                cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            elif period == "monthly":
                cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            elif period == "yearly":
                cutoff = (datetime.now() - timedelta(days=365)).isoformat()
            else:
                cutoff = (datetime.now() - timedelta(days=30)).isoformat()
            recent = [r for r in records if r.get("logged_at", "") >= cutoff]
            total_revenue = sum(r["revenue_usd"] for r in recent)
            total_streams = sum(r["stream_count"] for r in recent)
            platform_totals = {}
            for r in recent:
                platform_totals[r["platform"]] = platform_totals.get(r["platform"], 0) + r["revenue_usd"]
            return {"success": True, "period": period, "total_revenue_usd": round(total_revenue, 2), "total_streams": total_streams, "avg_rate_per_stream": round(total_revenue / total_streams, 4) if total_streams > 0 else 0, "platform_breakdown": {k: round(v, 2) for k, v in platform_totals.items()}, "record_count": len(recent)}
        except Exception as e:
            logger.error(f"Get revenue report failed: {e}")
            return {"success": False, "error": str(e)}

    def project_earnings(self, track_id: str, projected_streams: int) -> dict[str, Any]:
        """Project earnings based on projected streams."""
        logger.info(f"Projecting earnings for {projected_streams} streams on track {track_id}")
        try:
            data = self._load_data()
            track = next((t for t in data["tracks"] if t["id"] == track_id), None)
            if not track:
                return {"success": False, "error": "Track not found"}
            rates = {"spotify": 0.003, "apple_music": 0.008, "youtube_music": 0.002, "amazon_music": 0.004, "soundcloud": 0.003, "tidal": 0.012, "deezer": 0.004}
            projections = {}
            for platform, rate in rates.items():
                projections[platform] = {"streams": int(projected_streams / len(rates)), "revenue_usd": round((projected_streams / len(rates)) * rate, 2)}
            total_projected = sum(p["revenue_usd"] for p in projections.values())
            return {"success": True, "track": {"id": track["id"], "title": track["title"]}, "projected_streams": projected_streams, "projections": projections, "total_projected_revenue_usd": round(total_projected, 2)}
        except Exception as e:
            logger.error(f"Project earnings failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Music Royalty Tracker Agent - Track music royalties and streams", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""Examples:
  %(prog)s register --title "My Song" --artist "Test Artist" --isrc ISRC123456
  %(prog)s streams --track-id abc12345 --platform spotify --count 10000
  %(prog)s earnings --track-id abc12345
  %(prog)s artist --artist-name "Test Artist"
  %(prog)s report --period monthly
  %(prog)s project --track-id abc12345 --streams 100000""")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    reg_parser = subparsers.add_parser("register", help="Register a track")
    reg_parser.add_argument("--title", required=True, help="Track title")
    reg_parser.add_argument("--artist", dest="artist_name", required=True, help="Artist name")
    reg_parser.add_argument("--isrc", required=True, help="ISRC code")
    reg_parser.add_argument("--album", dest="album_name", default="", help="Album name")
    reg_parser.add_argument("--genre", default="", help="Genre")
    streams_parser = subparsers.add_parser("streams", help="Log streams")
    streams_parser.add_argument("--track-id", required=True, help="Track ID")
    streams_parser.add_argument("--platform", required=True, help=f"Platform: {', '.join(RoyaltyTrackerAgent.PLATFORMS)}")
    streams_parser.add_argument("--count", type=int, required=True, help="Number of streams")
    streams_parser.add_argument("--start", dest="period_start", help="Period start (YYYY-MM-DD)")
    streams_parser.add_argument("--end", dest="period_end", help="Period end (YYYY-MM-DD)")
    earnings_parser = subparsers.add_parser("earnings", help="Get track earnings")
    earnings_parser.add_argument("--track-id", required=True, help="Track ID")
    artist_parser = subparsers.add_parser("artist", help="Get artist earnings")
    artist_parser.add_argument("--artist-name", required=True, help="Artist name")
    report_parser = subparsers.add_parser("report", help="Get revenue report")
    report_parser.add_argument("--period", default="monthly", choices=["daily", "weekly", "monthly", "yearly"], help="Report period")
    proj_parser = subparsers.add_parser("project", help="Project earnings")
    proj_parser.add_argument("--track-id", required=True, help="Track ID")
    proj_parser.add_argument("--streams", type=int, required=True, help="Projected stream count")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    agent = RoyaltyTrackerAgent()
    try:
        if args.command == "register":
            result = agent.register_track(title=args.title, artist_name=args.artist_name, isrc=args.isrc, album_name=args.album_name, genre=args.genre)
        elif args.command == "streams":
            result = agent.log_streams(track_id=args.track_id, platform=args.platform, stream_count=args.count, period_start=args.period_start, period_end=args.period_end)
        elif args.command == "earnings":
            result = agent.get_track_earnings(track_id=args.track_id)
        elif args.command == "artist":
            result = agent.get_artist_earnings(artist_name=args.artist_name)
        elif args.command == "report":
            result = agent.get_revenue_report(period=args.period)
        elif args.command == "project":
            result = agent.project_earnings(track_id=args.track_id, projected_streams=args.streams)
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
