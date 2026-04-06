#!/usr/bin/env python3
"""
Music Playlist Creator Agent - Create and manage music playlists with smart curation.
Part of the music agent suite.
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
        logging.FileHandler(LOG_DIR / "playlist_creator.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("PlaylistCreatorAgent")


class PlaylistCreatorAgent:
    """Agent for creating and managing music playlists with smart curation."""

    GENRES = ["pop", "rock", "hip-hop", "electronic", "jazz", "classical", "country", "r&b", "metal", "indie", "folk", "latin", "reggae", "blues", "ambient"]
    MOODS = ["happy", "sad", "energetic", "relaxed", "romantic", "motivational", "melancholic", "chill", "party", "focus"]
    ACTIVITIES = ["workout", "study", "party", "dinner", "road_trip", "morning", "evening", "sleep", "commute", "gaming"]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / "playlists.json"
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not self.data_file.exists():
            data = {"playlists": [], "tracks": [], "last_updated": datetime.now().isoformat()}
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.data_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"playlists": [], "tracks": [], "last_updated": datetime.now().isoformat()}

    def _save_data(self, data: dict) -> None:
        data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save data: {e}")

    def _generate_track(self, genre: str | None = None) -> dict:
        """Generate a realistic track entry."""
        artists = ["The Midnight", "Aurora Waves", "Neon Pulse", "Crystal Sky", "Echo Valley", "Solar Wind", "Lunar Tide", "Urban Fox", "Silver River", "Dark Horse"]
        titles = ["Electric Dreams", "Starlight", "Ocean Drive", "City Lights", "Mountain High", "Desert Storm", "Arctic Wind", "Summer Rain", "Night Drive", "Golden Hour", "Midnight Sun", "Neon Sky", "Velvet Touch", "Iron Will", "Silent Storm"]
        genre = genre or random.choice(self.GENRES)
        return {
            "id": str(uuid.uuid4())[:8],
            "title": random.choice(titles),
            "artist": random.choice(artists),
            "genre": genre,
            "duration_seconds": random.randint(180, 360),
            "bpm": random.randint(80, 160),
            "year": random.randint(2015, 2026)
        }

    def create_playlist(self, name: str, description: str = "",
                        genre: str | None = None, mood: str | None = None,
                        activity: str | None = None) -> dict[str, Any]:
        """Create a new playlist."""
        logger.info(f"Creating playlist: {name}")
        try:
            data = self._load_data()
            if any(p.get("name") == name for p in data["playlists"]):
                return {"success": False, "error": "Playlist with this name already exists"}
            playlist = {
                "id": str(uuid.uuid4())[:8],
                "name": name, "description": description,
                "genre": genre, "mood": mood, "activity": activity,
                "track_count": 0, "total_duration_seconds": 0,
                "created_date": datetime.now().isoformat(),
                "modified_date": datetime.now().isoformat(),
                "is_public": False
            }
            data["playlists"].append(playlist)
            self._save_data(data)
            return {"success": True, "playlist": playlist}
        except Exception as e:
            logger.error(f"Create playlist failed: {e}")
            return {"success": False, "error": str(e)}

    def add_tracks(self, playlist_id: str, count: int = 5,
                   genre: str | None = None) -> dict[str, Any]:
        """Add tracks to a playlist."""
        logger.info(f"Adding {count} tracks to playlist {playlist_id}")
        try:
            data = self._load_data()
            playlist = next((p for p in data["playlists"] if p["id"] == playlist_id), None)
            if not playlist:
                return {"success": False, "error": "Playlist not found"}
            added_tracks = []
            for _ in range(count):
                track = self._generate_track(genre or playlist.get("genre"))
                track["added_to_playlist"] = playlist_id
                track["added_date"] = datetime.now().isoformat()
                data["tracks"].append(track)
                added_tracks.append(track)
            playlist["track_count"] = playlist.get("track_count", 0) + count
            playlist["total_duration_seconds"] = playlist.get("total_duration_seconds", 0) + sum(t["duration_seconds"] for t in added_tracks)
            playlist["modified_date"] = datetime.now().isoformat()
            self._save_data(data)
            return {"success": True, "playlist": playlist, "added_tracks": added_tracks}
        except Exception as e:
            logger.error(f"Add tracks failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_mood_playlist(self, mood: str, track_count: int = 20) -> dict[str, Any]:
        """Generate a playlist based on mood."""
        logger.info(f"Generating {track_count}-track mood playlist: {mood}")
        try:
            if mood not in self.MOODS:
                return {"success": False, "error": f"Invalid mood. Choose from: {self.MOODS}"}
            data = self._load_data()
            playlist_id = str(uuid.uuid4())[:8]
            playlist = {
                "id": playlist_id,
                "name": f"{mood.title()} Vibes",
                "description": f"Curated playlist for {mood} moods",
                "genre": None, "mood": mood, "activity": None,
                "track_count": track_count,
                "created_date": datetime.now().isoformat(),
                "modified_date": datetime.now().isoformat(),
                "auto_generated": True
            }
            data["playlists"].append(playlist)
            tracks = []
            for _ in range(track_count):
                track = self._generate_track()
                track["added_to_playlist"] = playlist_id
                track["added_date"] = datetime.now().isoformat()
                data["tracks"].append(track)
                tracks.append(track)
            self._save_data(data)
            total_duration = sum(t["duration_seconds"] for t in tracks)
            return {"success": True, "playlist": playlist, "tracks": tracks, "total_duration_minutes": round(total_duration / 60, 1)}
        except Exception as e:
            logger.error(f"Generate mood playlist failed: {e}")
            return {"success": False, "error": str(e)}

    def generate_activity_playlist(self, activity: str, track_count: int = 25) -> dict[str, Any]:
        """Generate a playlist based on activity."""
        logger.info(f"Generating {track_count}-track activity playlist: {activity}")
        try:
            if activity not in self.ACTIVITIES:
                return {"success": False, "error": f"Invalid activity. Choose from: {self.ACTIVITIES}"}
            genre_map = {"workout": "electronic", "study": "ambient", "party": "electronic", "road_trip": "rock", "morning": "pop", "evening": "jazz", "sleep": "ambient", "commute": "hip-hop", "gaming": "electronic"}
            genre = genre_map.get(activity, "pop")
            data = self._load_data()
            playlist_id = str(uuid.uuid4())[:8]
            playlist = {"id": playlist_id, "name": f"{activity.replace('_', ' ').title()} Playlist", "description": f"Perfect music for {activity}", "genre": genre, "mood": None, "activity": activity, "track_count": track_count, "created_date": datetime.now().isoformat(), "modified_date": datetime.now().isoformat(), "auto_generated": True}
            data["playlists"].append(playlist)
            tracks = []
            for _ in range(track_count):
                track = self._generate_track(genre)
                track["added_to_playlist"] = playlist_id
                track["added_date"] = datetime.now().isoformat()
                data["tracks"].append(track)
                tracks.append(track)
            self._save_data(data)
            return {"success": True, "playlist": playlist, "tracks": tracks}
        except Exception as e:
            logger.error(f"Generate activity playlist failed: {e}")
            return {"success": False, "error": str(e)}

    def get_playlist_tracks(self, playlist_id: str) -> dict[str, Any]:
        """Get all tracks in a playlist."""
        logger.info(f"Getting tracks for playlist {playlist_id}")
        try:
            data = self._load_data()
            playlist = next((p for p in data["playlists"] if p["id"] == playlist_id), None)
            if not playlist:
                return {"success": False, "error": "Playlist not found"}
            tracks = [t for t in data["tracks"] if t.get("added_to_playlist") == playlist_id]
            tracks.sort(key=lambda x: x.get("added_date", ""))
            return {"success": True, "playlist": {"id": playlist["id"], "name": playlist["name"]}, "tracks": tracks, "count": len(tracks), "total_duration_minutes": round(sum(t["duration_seconds"] for t in tracks) / 60, 1)}
        except Exception as e:
            logger.error(f"Get playlist tracks failed: {e}")
            return {"success": False, "error": str(e)}

    def list_playlists(self) -> dict[str, Any]:
        """List all playlists."""
        logger.info("Listing all playlists")
        try:
            data = self._load_data()
            playlists = [{
                "id": p["id"], "name": p["name"], "description": p.get("description", ""),
                "genre": p.get("genre"), "mood": p.get("mood"), "activity": p.get("activity"),
                "track_count": p.get("track_count", 0),
                "total_duration_minutes": round(p.get("total_duration_seconds", 0) / 60, 1),
                "created_date": p.get("created_date"),
                "auto_generated": p.get("auto_generated", False)
            } for p in data["playlists"]]
            return {"success": True, "playlists": playlists, "count": len(playlists)}
        except Exception as e:
            logger.error(f"List playlists failed: {e}")
            return {"success": False, "error": str(e)}

    def get_recommendations(self, playlist_id: str | None = None,
                             genre: str | None = None,
                             limit: int = 10) -> dict[str, Any]:
        """Get track recommendations based on playlist or genre."""
        logger.info(f"Getting recommendations for playlist={playlist_id}, genre={genre}")
        try:
            data = self._load_data()
            if playlist_id:
                playlist = next((p for p in data["playlists"] if p["id"] == playlist_id), None)
                if not playlist:
                    return {"success": False, "error": "Playlist not found"}
                source_genre = playlist.get("genre")
            else:
                source_genre = genre
            recommendations = [self._generate_track(source_genre) for _ in range(limit)]
            return {"success": True, "recommendations": recommendations, "count": len(recommendations)}
        except Exception as e:
            logger.error(f"Get recommendations failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Music Playlist Creator Agent - Create and manage music playlists", formatter_class=argparse.RawDescriptionHelpFormatter, epilog="""Examples:
  %(prog)s create --name "Chill Vibes" --description "Relaxing tracks" --mood relaxed
  %(prog)s add-tracks --playlist-id abc12345 --count 10
  %(prog)s generate-mood --mood happy --count 30
  %(prog)s generate-activity --activity workout --count 25
  %(prog)s tracks --playlist-id abc12345
  %(prog)s list
  %(prog)s recommend --genre rock --limit 15""")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    create_parser = subparsers.add_parser("create", help="Create a playlist")
    create_parser.add_argument("--name", required=True, help="Playlist name")
    create_parser.add_argument("--description", default="", help="Description")
    create_parser.add_argument("--genre", help=f"Genre: {', '.join(PlaylistCreatorAgent.GENRES)}")
    create_parser.add_argument("--mood", help=f"Mood: {', '.join(PlaylistCreatorAgent.MOODS)}")
    create_parser.add_argument("--activity", help=f"Activity: {', '.join(PlaylistCreatorAgent.ACTIVITIES)}")
    add_parser = subparsers.add_parser("add-tracks", help="Add tracks to playlist")
    add_parser.add_argument("--playlist-id", required=True, help="Playlist ID")
    add_parser.add_argument("--count", type=int, default=5, help="Number of tracks")
    add_parser.add_argument("--genre", help="Genre filter for tracks")
    mood_parser = subparsers.add_parser("generate-mood", help="Generate mood-based playlist")
    mood_parser.add_argument("--mood", required=True, help=f"Mood: {', '.join(PlaylistCreatorAgent.MOODS)}")
    mood_parser.add_argument("--count", type=int, default=20, help="Number of tracks")
    act_parser = subparsers.add_parser("generate-activity", help="Generate activity-based playlist")
    act_parser.add_argument("--activity", required=True, help=f"Activity: {', '.join(PlaylistCreatorAgent.ACTIVITIES)}")
    act_parser.add_argument("--count", type=int, default=25, help="Number of tracks")
    tracks_parser = subparsers.add_parser("tracks", help="Get playlist tracks")
    tracks_parser.add_argument("--playlist-id", required=True, help="Playlist ID")
    subparsers.add_parser("list", help="List all playlists")
    rec_parser = subparsers.add_parser("recommend", help="Get recommendations")
    rec_parser.add_argument("--playlist-id", help="Playlist ID for recommendations")
    rec_parser.add_argument("--genre", help="Genre for recommendations")
    rec_parser.add_argument("--limit", type=int, default=10, help="Number of recommendations")
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0
    agent = PlaylistCreatorAgent()
    try:
        if args.command == "create":
            result = agent.create_playlist(name=args.name, description=args.description, genre=args.genre, mood=args.mood, activity=args.activity)
        elif args.command == "add-tracks":
            result = agent.add_tracks(playlist_id=args.playlist_id, count=args.count, genre=args.genre)
        elif args.command == "generate-mood":
            result = agent.generate_mood_playlist(mood=args.mood, track_count=args.count)
        elif args.command == "generate-activity":
            result = agent.generate_activity_playlist(activity=args.activity, track_count=args.count)
        elif args.command == "tracks":
            result = agent.get_playlist_tracks(playlist_id=args.playlist_id)
        elif args.command == "list":
            result = agent.list_playlists()
        elif args.command == "recommend":
            result = agent.get_recommendations(playlist_id=args.playlist_id, genre=args.genre, limit=args.limit)
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
