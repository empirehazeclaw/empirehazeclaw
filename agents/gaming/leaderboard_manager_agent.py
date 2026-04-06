#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║          LEADERBOARD MANAGER AGENT                         ║
║          Gaming Leaderboards & Player Rankings               ║
╚══════════════════════════════════════════════════════════════╝

Features:
  - Create and manage multiple leaderboards (daily, weekly, all-time, seasonal)
  - Player profile management with stats tracking
  - Multiple game/mode support
  - Elo/rank calculation systems
  - Tournament brackets with auto-seeded rankings
  - Achievement tracking
  - Anti-cheat: outlier detection
  - Streak tracking
  - Team/group leaderboards
  - Export rankings to CSV/JSON
  - Historical ranking archives

Usage:
    python3 leaderboard_manager_agent.py --help
    python3 leaderboard_manager_agent.py create --name "Weekly FPS" --game "Halo" --type weekly
    python3 leaderboard_manager_agent.py submit --board 1 --player "Player1" --score 1500
    python3 leaderboard_manager_agent.py top --board 1 --limit 10
    python3 leaderboard_manager_agent.py rank --board 1 --player "Player1"
    python3 leaderboard_manager_agent.py tournament --board 1 --size 16
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import statistics
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger("openclaw.leaderboard")


class LeaderboardType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    ALL_TIME = "all_time"
    TOURNAMENT = "tournament"


class GameMode(str, Enum):
    SOLO = "solo"
    DUO = "duo"
    SQUAD = "squad"
    TEAM = "team"
    FFA = "ffa"  # Free for all


class RankTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    CHAMPION = "champion"


@dataclass
class Player:
    id: str
    username: str
    created_at: datetime = field(default_factory=datetime.now)
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_score: int = 0
    highest_score: int = 0
    average_score: float = 0.0
    current_streak: int = 0
    best_streak: int = 0
    elo: int = 1000
    rank_tier: RankTier = RankTier.BRONZE
    achievements: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def win_rate(self) -> float:
        total = self.wins + self.losses + self.draws
        return (self.wins / total * 100) if total > 0 else 0.0

    def update_stats(self, score: int, won: bool):
        self.games_played += 1
        self.total_score += score
        if score > self.highest_score:
            self.highest_score = score
        self.average_score = self.total_score / self.games_played
        if won:
            self.wins += 1
            self.current_streak += 1
            if self.current_streak > self.best_streak:
                self.best_streak = self.current_streak
        else:
            self.losses += 1
            self.current_streak = 0
        self._update_tier()

    def _update_tier(self):
        if self.elo >= 2500:
            self.rank_tier = RankTier.CHAMPION
        elif self.elo >= 2200:
            self.rank_tier = RankTier.GRANDMASTER
        elif self.elo >= 1900:
            self.rank_tier = RankTier.MASTER
        elif self.elo >= 1600:
            self.rank_tier = RankTier.DIAMOND
        elif self.elo >= 1300:
            self.rank_tier = RankTier.PLATINUM
        elif self.elo >= 1000:
            self.rank_tier = RankTier.GOLD
        elif self.elo >= 700:
            self.rank_tier = RankTier.SILVER
        else:
            self.rank_tier = RankTier.BRONZE

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['rank_tier'] = RankTier(data['rank_tier'])
        return cls(**data)


@dataclass
class ScoreEntry:
    id: str
    player_id: str
    score: int
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['timestamp'] = self.timestamp.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'ScoreEntry':
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class Leaderboard:
    id: int
    name: str
    game: str
    board_type: LeaderboardType
    mode: GameMode = GameMode.SOLO
    created_at: datetime = field(default_factory=datetime.now)
    starts_at: datetime = field(default_factory=datetime.now)
    ends_at: Optional[datetime] = None
    player_count: int = 0
    is_active: bool = True
    top_score: int = 0
    entries: List[Dict] = field(default_factory=list)  # [{player_id, score, rank, submitted_at}]

    def get_entry(self, player_id: str) -> Optional[Dict]:
        return next((e for e in self.entries if e['player_id'] == player_id), None)

    def add_entry(self, player_id: str, score: int) -> Dict:
        entry = self.get_entry(player_id)
        if entry:
            if score > entry['score']:
                entry['score'] = score
                entry['submitted_at'] = datetime.now().isoformat()
                if score > self.top_score:
                    self.top_score = score
        else:
            entry = {
                'player_id': player_id,
                'score': score,
                'rank': 0,
                'submitted_at': datetime.now().isoformat()
            }
            self.entries.append(entry)
            self.player_count += 1
            if score > self.top_score:
                self.top_score = score

        self._recalculate_ranks()
        return entry

    def _recalculate_ranks(self):
        sorted_entries = sorted(self.entries, key=lambda x: x['score'], reverse=True)
        for i, entry in enumerate(sorted_entries):
            entry['rank'] = i + 1

    def get_top(self, limit: int = 10) -> List[Dict]:
        return sorted(self.entries, key=lambda x: x['score'], reverse=True)[:limit]

    def is_ended(self) -> bool:
        if self.ends_at is None:
            return False
        return datetime.now() > self.ends_at

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        d['starts_at'] = self.starts_at.isoformat() if self.starts_at else None
        if d['ends_at']:
            d['ends_at'] = self.ends_at.isoformat() if self.ends_at else None
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Leaderboard':
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('starts_at'):
            data['starts_at'] = datetime.fromisoformat(data['starts_at'])
        if data.get('ends_at'):
            data['ends_at'] = datetime.fromisoformat(data['ends_at'])
        data['board_type'] = LeaderboardType(data['board_type'])
        data['mode'] = GameMode(data['mode'])
        return cls(**data)


@dataclass
class Tournament:
    id: int
    name: str
    board_id: int
    size: int  # Power of 2: 4, 8, 16, 32, 64
    rounds: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"  # pending, in_progress, completed, cancelled
    participants: List[str] = field(default_factory=list)  # player_ids
    brackets: List[Dict] = field(default_factory=list)
    winner_id: Optional[str] = None

    def generate_brackets(self):
        """Generate tournament brackets from participants"""
        self.size = max(self.size, len(self.participants))
        if self.size < 2:
            raise ValueError("Tournament needs at least 2 participants")

        rounds = []
        num_rounds = int(round(self.size ** 0.5)) if self.size <= 64 else 6
        self.rounds = num_rounds

        current_round = []
        for i in range(self.size):
            if i < len(self.participants):
                current_round.append({
                    'round': 1,
                    'match': i + 1,
                    'player1': self.participants[i],
                    'player2': self.participants[i + 1] if i + 1 < len(self.participants) else None,
                    'score1': 0,
                    'score2': 0,
                    'winner': None,
                    'status': 'pending'
                })
            elif len(current_round) > 0:
                current_round[-1]['player2'] = None  # Bye
                current_round[-1]['winner'] = current_round[-1]['player1']
        rounds.append(current_round)

        self.brackets = rounds
        self.status = "pending"
        return rounds

    def to_dict(self) -> Dict:
        d = asdict(self)
        d['created_at'] = self.created_at.isoformat()
        if self.started_at:
            d['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            d['completed_at'] = self.completed_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: Dict) -> 'Tournament':
        data = data.copy()
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


class LeaderboardManager:
    OUTLIER_THRESHOLD = 3.0  # Standard deviations for outlier detection

    def __init__(self, storage_path: str = "data/leaderboard_manager"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.boards_file = self.storage_path / "leaderboards.json"
        self.players_file = self.storage_path / "players.json"
        self.scores_file = self.storage_path / "scores.json"
        self.tournaments_file = self.storage_path / "tournaments.json"

        self.boards: List[Leaderboard] = self._load_json(self.boards_file, Leaderboard)
        self.players: Dict[str, Player] = self._load_players()
        self.scores: List[ScoreEntry] = self._load_json(self.scores_file, ScoreEntry)
        self.tournaments: List[Tournament] = self._load_json(self.tournaments_file, Tournament)

        self.next_board_id = max([b.id for b in self.boards], default=0) + 1
        self.next_tournament_id = max([t.id for t in self.tournaments], default=0) + 1

    def _load_json(self, filepath: Path, cls):
        if not filepath.exists():
            return []
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return [cls.from_dict(d) if isinstance(d, dict) else d for d in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def _load_players(self) -> Dict[str, Player]:
        data = self._load_json(self.players_file, Player)
        return {p.id: p for p in data}

    def _save(self, data: List, filepath: Path):
        with open(filepath, 'w') as f:
            json.dump([d.to_dict() if hasattr(d, 'to_dict') else d for d in data], f, indent=2)

    def _save_boards(self):
        self._save(self.boards, self.boards_file)

    def _save_players(self):
        with open(self.players_file, 'w') as f:
            json.dump([p.to_dict() if hasattr(p, 'to_dict') else p for p in self.players.values()], f, indent=2)

    def _save_scores(self):
        self._save(self.scores, self.scores_file)

    def _save_tournaments(self):
        self._save(self.tournaments, self.tournaments_file)

    def create_leaderboard(self, name: str, game: str, board_type: str,
                          mode: str = "solo", **kwargs) -> Leaderboard:
        lb_type = LeaderboardType(board_type)
        mode_enum = GameMode(mode)

        starts = datetime.now()
        ends = None
        if lb_type == LeaderboardType.DAILY:
            ends = starts + timedelta(days=1)
        elif lb_type == LeaderboardType.WEEKLY:
            ends = starts + timedelta(weeks=1)
        elif lb_type == LeaderboardType.MONTHLY:
            ends = starts + timedelta(days=30)
        elif lb_type == LeaderboardType.SEASONAL:
            ends = starts + timedelta(days=90)

        lb = Leaderboard(
            id=self.next_board_id,
            name=name,
            game=game,
            board_type=lb_type,
            mode=mode_enum,
            starts_at=starts,
            ends_at=ends,
            is_active=True
        )

        self.boards.append(lb)
        self._save_boards()
        log.info(f"Created leaderboard #{lb.id}: {name}")
        return lb

    def register_player(self, username: str, **metadata) -> Player:
        player_id = f"player_{username.lower().replace(' ', '_')}"
        if player_id in self.players:
            return self.players[player_id]

        player = Player(
            id=player_id,
            username=username,
            metadata=metadata
        )
        self.players[player_id] = player
        self._save_players()
        log.info(f"Registered player: {username}")
        return player

    def is_outlier(self, player_id: str, new_score: int) -> bool:
        """Detect if score is a statistical outlier"""
        player_scores = [s.score for s in self.scores if s.player_id == player_id]
        if len(player_scores) < 5:
            return False

        mean = statistics.mean(player_scores)
        stdev = statistics.stdev(player_scores)
        if stdev == 0:
            return False

        z_score = abs((new_score - mean) / stdev)
        return z_score > self.OUTLIER_THRESHOLD

    def submit_score(self, board_id: int, username: str, score: int,
                    skip_outlier_check: bool = False, **metadata) -> Dict:
        board = next((b for b in self.boards if b.id == board_id), None)
        if not board:
            raise ValueError(f"Leaderboard {board_id} not found")

        player = self.register_player(username)

        if not skip_outlier_check and self.is_outlier(player.id, score):
            log.warning(f"Outlier score detected for {username}: {score}")
            return {"error": "outlier_detected", "score": score, "player": username}

        entry = board.add_entry(player.id, score)

        score_entry = ScoreEntry(
            id=f"score_{len(self.scores) + 1}",
            player_id=player.id,
            score=score,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.scores.append(score_entry)

        player.update_stats(score, won=True)
        self._save_boards()
        self._save_players()
        self._save_scores()

        log.info(f"Score submitted: {username} = {score} on board #{board_id}")
        return {
            "player": username,
            "score": score,
            "rank": entry['rank'],
            "is_outlier": not skip_outlier_check and self.is_outlier(player.id, score)
        }

    def get_top(self, board_id: int, limit: int = 10) -> List[Dict]:
        board = next((b for b in self.boards if b.id == board_id), None)
        if not board:
            raise ValueError(f"Leaderboard {board_id} not found")

        results = []
        for entry in board.get_top(limit):
            player = self.players.get(entry['player_id'])
            results.append({
                'rank': entry['rank'],
                'player': player.username if player else entry['player_id'],
                'score': entry['score'],
                'tier': player.rank_tier.value if player else 'unknown',
                'submitted_at': entry['submitted_at']
            })
        return results

    def get_player_rank(self, board_id: int, username: str) -> Optional[Dict]:
        player_id = f"player_{username.lower().replace(' ', '_')}"
        board = next((b for b in self.boards if b.id == board_id), None)
        if not board:
            return None

        entry = board.get_entry(player_id)
        if not entry:
            return None

        player = self.players.get(player_id)
        return {
            'player': username,
            'rank': entry['rank'],
            'score': entry['score'],
            'tier': player.rank_tier.value if player else 'unknown',
            'elo': player.elo if player else 0,
            'wins': player.wins if player else 0,
            'games_played': player.games_played if player else 0,
            'win_rate': player.win_rate() if player else 0,
            'streak': player.current_streak if player else 0,
        }

    def get_player_profile(self, username: str) -> Optional[Dict]:
        player_id = f"player_{username.lower().replace(' ', '_')}"
        player = self.players.get(player_id)
        if not player:
            return None

        return {
            'id': player.id,
            'username': player.username,
            'games_played': player.games_played,
            'wins': player.wins,
            'losses': player.losses,
            'draws': player.draws,
            'win_rate': round(player.win_rate(), 2),
            'highest_score': player.highest_score,
            'average_score': round(player.average_score, 2),
            'elo': player.elo,
            'rank_tier': player.rank_tier.value,
            'current_streak': player.current_streak,
            'best_streak': player.best_streak,
            'achievements': player.achievements,
            'member_since': player.created_at.isoformat(),
        }

    def create_tournament(self, name: str, board_id: int, size: int = 16) -> Tournament:
        tournament = Tournament(
            id=self.next_tournament_id,
            name=name,
            board_id=board_id,
            size=size,
            participants=[],
            status="pending"
        )
        self.tournaments.append(tournament)
        self._save_tournaments()
        log.info(f"Created tournament #{tournament.id}: {name}")
        return tournament

    def add_tournament_participant(self, tournament_id: int, username: str):
        tournament = next((t for t in self.tournaments if t.id == tournament_id), None)
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")

        player = self.register_player(username)
        if player.id not in tournament.participants:
            tournament.participants.append(player.id)
            self._save_tournaments()

    def start_tournament(self, tournament_id: int):
        tournament = next((t for t in self.tournaments if t.id == tournament_id), None)
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")

        tournament.generate_brackets()
        tournament.status = "in_progress"
        tournament.started_at = datetime.now()
        self._save_tournaments()
        return tournament.brackets

    def award_achievement(self, username: str, achievement: str) -> bool:
        player_id = f"player_{username.lower().replace(' ', '_')}"
        player = self.players.get(player_id)
        if not player:
            return False
        if achievement not in player.achievements:
            player.achievements.append(achievement)
            self._save_players()
        return True

    def export_leaderboard(self, board_id: int, filepath: str, format: str = "csv"):
        board = next((b for b in self.boards if b.id == board_id), None)
        if not board:
            raise ValueError(f"Leaderboard {board_id} not found")

        if format == "csv":
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Rank', 'Player', 'Score', 'Tier', 'Submitted'])
                for entry in sorted(board.entries, key=lambda x: x['rank']):
                    player = self.players.get(entry['player_id'])
                    writer.writerow([
                        entry['rank'],
                        player.username if player else entry['player_id'],
                        entry['score'],
                        player.rank_tier.value if player else 'unknown',
                        entry['submitted_at']
                    ])
        else:
            data = {
                'leaderboard': board.to_dict(),
                'entries': [{
                    'rank': e['rank'],
                    'player': self.players.get(e['player_id']).username if self.players.get(e['player_id']) else e['player_id'],
                    'score': e['score'],
                    'submitted_at': e['submitted_at']
                } for e in board.entries]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        log.info(f"Exported leaderboard #{board_id} to {filepath}")

    def list_leaderboards(self, active_only: bool = True) -> List[Dict]:
        boards = self.boards
        if active_only:
            boards = [b for b in boards if b.is_active and not b.is_ended()]
        return [{
            'id': b.id,
            'name': b.name,
            'game': b.game,
            'type': b.board_type.value,
            'mode': b.mode.value,
            'player_count': b.player_count,
            'top_score': b.top_score,
            'is_active': b.is_active,
            'ends_at': b.ends_at.isoformat() if b.ends_at else None,
        } for b in boards]


def format_top_entry(entry: Dict) -> str:
    tier_emojis = {
        'bronze': '🥉', 'silver': '🥈', 'gold': '🏆', 'platinum': '💎',
        'diamond': '💠', 'master': '🌟', 'grandmaster': '👑', 'champion': '🏅'
    }
    emoji = tier_emojis.get(entry['tier'], '•')
    return f"  #{entry['rank']:3d} {emoji} {entry['player']:<20} {entry['score']:>10}"


def main():
    parser = argparse.ArgumentParser(
        description="Leaderboard Manager Agent - Gaming Leaderboards & Player Rankings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s create --name "Weekly FPS" --game "Halo" --type weekly
  %(prog)s create --name "Daily Race" --game "Forza" --type daily
  %(prog)s submit --board 1 --player "Player1" --score 1500
  %(prog)s top --board 1 --limit 10
  %(prog)s rank --board 1 --player "Player1"
  %(prog)s profile --player "Player1"
  %(prog)s tournament --board 1 --name "Spring Championship" --size 16
  %(prog)s join --tournament 1 --player "Player1"
  %(prog)s start --tournament 1
  %(prog)s list --active
  %(prog)s export --board 1 --output leaderboard.csv
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    create_parser = subparsers.add_parser("create", help="Create leaderboard")
    create_parser.add_argument("--name", "-n", required=True, help="Leaderboard name")
    create_parser.add_argument("--game", "-g", required=True, help="Game name")
    create_parser.add_argument("--type", "-t", required=True,
                              choices=[e.value for e in LeaderboardType],
                              help="Board type")
    create_parser.add_argument("--mode", "-m", default="solo",
                              choices=[e.value for e in GameMode])
    create_parser.add_argument("--storage", default="data/leaderboard_manager")

    submit_parser = subparsers.add_parser("submit", help="Submit a score")
    submit_parser.add_argument("--board", "-b", type=int, required=True, help="Board ID")
    submit_parser.add_argument("--player", "-p", required=True, help="Player username")
    submit_parser.add_argument("--score", "-s", type=int, required=True, help="Score value")
    submit_parser.add_argument("--skip-check", action="store_true",
                              help="Skip outlier detection")
    submit_parser.add_argument("--storage", default="data/leaderboard_manager")

    top_parser = subparsers.add_parser("top", help="Get top players")
    top_parser.add_argument("--board", "-b", type=int, required=True)
    top_parser.add_argument("--limit", "-l", type=int, default=10)
    top_parser.add_argument("--storage", default="data/leaderboard_manager")

    rank_parser = subparsers.add_parser("rank", help="Get player rank")
    rank_parser.add_argument("--board", "-b", type=int, required=True)
    rank_parser.add_argument("--player", "-p", required=True)
    rank_parser.add_argument("--storage", default="data/leaderboard_manager")

    profile_parser = subparsers.add_parser("profile", help="Get player profile")
    profile_parser.add_argument("--player", "-p", required=True)
    profile_parser.add_argument("--storage", default="data/leaderboard_manager")

    achievement_parser = subparsers.add_parser("achievement", help="Award achievement")
    achievement_parser.add_argument("--player", "-p", required=True)
    achievement_parser.add_argument("--name", "-n", required=True)
    achievement_parser.add_argument("--storage", default="data/leaderboard_manager")

    tournament_parser = subparsers.add_parser("tournament", help="Create tournament")
    tournament_parser.add_argument("--board", "-b", type=int, required=True)
    tournament_parser.add_argument("--name", "-n", required=True)
    tournament_parser.add_argument("--size", "-s", type=int, default=16)
    tournament_parser.add_argument("--storage", default="data/leaderboard_manager")

    join_parser = subparsers.add_parser("join", help="Join tournament")
    join_parser.add_argument("--tournament", "-t", type=int, required=True)
    join_parser.add_argument("--player", "-p", required=True)
    join_parser.add_argument("--storage", default="data/leaderboard_manager")

    start_parser = subparsers.add_parser("start", help="Start tournament")
    start_parser.add_argument("--tournament", "-t", type=int, required=True)
    start_parser.add_argument("--storage", default="data/leaderboard_manager")

    list_parser = subparsers.add_parser("list", help="List leaderboards")
    list_parser.add_argument("--active", action="store_true", default=True)
    list_parser.add_argument("--all", action="store_false", dest="active")
    list_parser.add_argument("--storage", default="data/leaderboard_manager")

    export_parser = subparsers.add_parser("export", help="Export leaderboard")
    export_parser.add_argument("--board", "-b", type=int, required=True)
    export_parser.add_argument("--output", "-o", required=True)
    export_parser.add_argument("--format", "-f", choices=["csv", "json"], default="csv")
    export_parser.add_argument("--storage", default="data/leaderboard_manager")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        storage = getattr(args, 'storage', 'data/leaderboard_manager')
        mgr = LeaderboardManager(storage)

        if args.command == "create":
            lb = mgr.create_leaderboard(
                name=args.name, game=args.game,
                board_type=args.type, mode=args.mode
            )
            print(f"\n✅ Leaderboard created!")
            print(f"   ID: {lb.id}")
            print(f"   Name: {lb.name}")
            print(f"   Game: {lb.game}")
            print(f"   Type: {lb.board_type.value}")
            print(f"   Ends: {lb.ends_at if lb.ends_at else 'Never'}")

        elif args.command == "submit":
            result = mgr.submit_score(
                args.board, args.player, args.score,
                skip_outlier_check=args.skip_check
            )
            if 'error' in result and result['error'] == 'outlier_detected':
                print(f"\n⚠️  WARNING: Outlier score detected!")
                print(f"   Score: {result['score']} may be flagged as suspicious")
            else:
                print(f"\n✅ Score submitted!")
                print(f"   Player: {result['player']}")
                print(f"   Score: {result['score']}")
                print(f"   Rank: #{result['rank']}")

        elif args.command == "top":
            entries = mgr.get_top(args.board, args.limit)
            print(f"\n🏆 TOP {len(entries)} on Board #{args.board}:")
            print("=" * 50)
            for entry in entries:
                print(format_top_entry(entry))
            print("=" * 50)

        elif args.command == "rank":
            result = mgr.get_player_rank(args.board, args.player)
            if not result:
                print(f"\n❌ Player '{args.player}' not found on board #{args.board}")
            else:
                print(f"\n👤 RANK for {result['player']} on Board #{args.board}:")
                print("=" * 50)
                print(f"  Rank: #{result['rank']}")
                print(f"  Score: {result['score']}")
                print(f"  Tier: {result['tier']}")
                print(f"  ELO: {result['elo']}")
                print(f"  Win Rate: {result['win_rate']:.1f}%")
                print(f"  Games: {result['games_played']}")
                print(f"  Streak: {result['streak']} wins")

        elif args.command == "profile":
            profile = mgr.get_player_profile(args.player)
            if not profile:
                print(f"\n❌ Player '{args.player}' not found")
            else:
                print(f"\n🎮 PLAYER PROFILE: {profile['username']}")
                print("=" * 50)
                print(f"  Tier: {profile['rank_tier']}")
                print(f"  ELO: {profile['elo']}")
                print(f"  Games Played: {profile['games_played']}")
                print(f"  Wins: {profile['wins']} | Losses: {profile['losses']} | Draws: {profile['draws']}")
                print(f"  Win Rate: {profile['win_rate']}%")
                print(f"  Highest Score: {profile['highest_score']}")
                print(f"  Average Score: {profile['average_score']}")
                print(f"  Current Streak: {profile['current_streak']}")
                print(f"  Best Streak: {profile['best_streak']}")
                if profile['achievements']:
                    print(f"  Achievements: {', '.join(profile['achievements'])}")

        elif args.command == "achievement":
            if mgr.award_achievement(args.player, args.name):
                print(f"\n🏅 Achievement '{args.name}' awarded to {args.player}!")
            else:
                print(f"\n❌ Player '{args.player}' not found")

        elif args.command == "tournament":
            t = mgr.create_tournament(args.name, args.board, args.size)
            print(f"\n🏆 Tournament created!")
            print(f"   ID: {t.id}")
            print(f"   Name: {t.name}")
            print(f"   Size: {t.size} players")
            print(f"   Board: #{t.board_id}")

        elif args.command == "join":
            mgr.add_tournament_participant(args.tournament, args.player)
            print(f"\n✅ {args.player} joined tournament #{args.tournament}")

        elif args.command == "start":
            brackets = mgr.start_tournament(args.tournament)
            print(f"\n🎮 Tournament #{args.tournament} started!")
            for round_matches in brackets:
                print(f"\n  Round {round_matches[0]['round']}:")
                for match in round_matches:
                    p1 = match['player1'] or "TBD"
                    p2 = match['player2'] or "BYE"
                    print(f"    Match {match['match']}: {p1} vs {p2}")

        elif args.command == "list":
            boards = mgr.list_leaderboards(active_only=args.active)
            print(f"\n📋 LEADERBOARDS ({len(boards)} found):")
            print("=" * 70)
            for b in boards:
                status = "🟢" if b['is_active'] else "⚫"
                print(f"  {status} #{b['id']:3d} | {b['name']:<25} | {b['game']:<15} | "
                      f"{b['type']:<10} | {b['player_count']:4d} players")
            print("=" * 70)

        elif args.command == "export":
            mgr.export_leaderboard(args.board, args.output, args.format)
            print(f"\n✅ Exported board #{args.board} to {args.output}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled")
        sys.exit(130)
    except Exception as e:
        log.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
