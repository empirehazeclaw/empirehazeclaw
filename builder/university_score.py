#!/usr/bin/env python3
"""
📚 OpenClaw University — Gamification & Score Dashboard
=======================================================
Trackt Nico's Quiz-Fortschritt, Badges und Streaks.

Autor: Builder Agent
Datum: 2026-04-08
"""

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

# ============================================================================
# KONSTANTEN
# ============================================================================

STORAGE_DIR = "/home/clawbot/.openclaw/workspace/ceo/university"
QUIZ_RESULTS_FILE = os.path.join(STORAGE_DIR, "quiz_results.json")

# Default-Struktur für leere/neue Datei
DEFAULT_DATA = {
    "results": [],
    "total_quizzes_taken": 0,
    "average_score": 0,
    "streak_days": 0,
    "last_quiz_date": None,
    "badges": [],
    "weak_topics": {},
    "strong_topics": {}
}

# Badge-Definitionen
BADGES = {
    "perfect_score": {
        "name": "Perfect Score",
        "emoji": "🏅",
        "description": "100% bei einem Quiz",
        "condition": lambda d: any(r["percentage"] == 100 for r in d.get("results", []))
    },
    "streak_5": {
        "name": "5-Tage-Streak",
        "emoji": "🔥",
        "description": "5 Tage in Folge ein Quiz gemacht",
        "condition": lambda d: d.get("streak_days", 0) >= 5
    },
    "streak_7": {
        "name": "Consistency Master",
        "emoji": "👑",
        "description": "7+ Tage Streak",
        "condition": lambda d: d.get("streak_days", 0) >= 7
    },
    "speed_runner": {
        "name": "Speed Runner",
        "emoji": "⚡",
        "description": "Quiz in unter 10 Minuten",
        "condition": lambda d: any(r.get("time_taken_minutes", 999) < 10 for r in d.get("results", []))
    },
    "comeback_kid": {
        "name": "Comeback Kid",
        "emoji": "💪",
        "description": "Nach einer Pause zurückgekehrt",
        "condition": lambda d: _check_comeback(d)
    },
    "first_quiz": {
        "name": "Erste Schritte",
        "emoji": "🎯",
        "description": "Erstes Quiz abgeschlossen",
        "condition": lambda d: d.get("total_quizzes_taken", 0) >= 1
    },
    "five_quizzes": {
        "name": "Lernender",
        "emoji": "📚",
        "description": "5 Quizze abgeschlossen",
        "condition": lambda d: d.get("total_quizzes_taken", 0) >= 5
    },
    "ten_quizzes": {
        "name": "Quiz-Master",
        "emoji": "🎓",
        "description": "10 Quizze abgeschlossen",
        "condition": lambda d: d.get("total_quizzes_taken", 0) >= 10
    }
}

# Modul-Metadaten für Anzeige
MODULE_META = {
    "quiz_module_1": {"short": "Modul 1", "lesson": "lesson_1_1.md"},
    "quiz_module_2": {"short": "OWASP", "lesson": "lesson_2_1.md"},
    "quiz_module_3": {"short": "Tool-Val", "lesson": "lesson_3_2.md"},
    "quiz_module_4": {"short": "Modul 4", "lesson": "lesson_4_1.md"},
    "quiz_module_5": {"short": "Modul 5", "lesson": "lesson_5_1.md"},
    "quiz_module_6_1": {"short": "Modul 6.1", "lesson": "lesson_6_1.md"},
    "quiz_module_6_2": {"short": "Modul 6.2", "lesson": "lesson_6_2.md"},
    "quiz_module_7": {"short": "Modul 7", "lesson": "lesson_7_1.md"},
}


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def _check_comeback(data: dict) -> bool:
    """Prüft ob Nico nach einer Pause zurückgekehrt ist."""
    if len(data.get("results", [])) < 2:
        return False
    dates = [datetime.fromisoformat(r["date"].replace("Z", "+00:00")) for r in data["results"]]
    dates.sort()
    gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
    return any(g > 7 for g in gaps)


def _get_stars(percentage: int) -> str:
    """Wandelt Prozentsatz in Sterne um."""
    if percentage >= 95:
        return "⭐⭐⭐"
    elif percentage >= 80:
        return "⭐⭐"
    elif percentage >= 60:
        return "⭐"
    return ""


def _load_data() -> dict:
    """Lädt die Quiz-Ergebnisse aus der JSON-Datei."""
    if not os.path.exists(QUIZ_RESULTS_FILE):
        return DEFAULT_DATA.copy()
    try:
        with open(QUIZ_RESULTS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return DEFAULT_DATA.copy()
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[University] Fehler beim Laden: {e}")
        return DEFAULT_DATA.copy()


def _save_data(data: dict) -> bool:
    """Speichert die Quiz-Ergebnisse in die JSON-Datei."""
    try:
        os.makedirs(STORAGE_DIR, exist_ok=True)
        with open(QUIZ_RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"[University] Fehler beim Speichern: {e}")
        return False


def _update_stats(data: dict) -> dict:
    """Berechnet Statistiken neu."""
    results = data.get("results", [])
    if not results:
        return data

    # Basis-Stats
    data["total_quizzes_taken"] = len(results)
    data["average_score"] = round(sum(r["percentage"] for r in results) / len(results), 1)

    # Streak berechnen
    data["streak_days"] = _calculate_streak(results)

    # Badges aktualisieren
    data["badges"] = _calculate_badges(data)

    return data


def _calculate_streak(results: list) -> int:
    """Berechnet die aktuelle Streak (Tage in Folge mit Quiz)."""
    if not results:
        return 0

    dates = set()
    for r in results:
        dt = datetime.fromisoformat(r["date"].replace("Z", "+00:00"))
        dates.add(dt.date())

    if not dates:
        return 0

    today = datetime.now(timezone.utc).date()
    streak = 0
    check_date = today

    # Prüfe ob heute oder gestern ein Quiz war
    if today not in dates:
        check_date = today - timedelta(days=1)
        if check_date not in dates:
            return 0  # Streak unterbrochen

    # Zähle rückwärts
    while check_date in dates:
        streak += 1
        check_date -= timedelta(days=1)

    return streak


def _calculate_badges(data: dict) -> list:
    """Berechnet welche Badges freigeschaltet sind."""
    earned = []
    for badge_id, info in BADGES.items():
        try:
            if info["condition"](data):
                earned.append(badge_id)
        except Exception as e:
            print(f"[University] Badge-Check fehlgeschlagen {badge_id}: {e}")
    return earned


# ============================================================================
# API FUNKTIONEN (für CLI/Scripts)
# ============================================================================

def record_quiz_result(
    module: str,
    module_name: str,
    score: int,
    max_score: int,
    time_taken_minutes: float,
    weak_topics: list = None,
    strong_topics: list = None
) -> dict:
    """
    Speichert ein Quiz-Ergebnis.

    Args:
        module: Quiz-Modul-ID (z.B. "quiz_module_2")
        module_name: Anzeigename des Moduls
        score: Erzielte Punkte
        max_score: Maximale Punkte
        time_taken_minutes: Dauer in Minuten
        weak_topics: Liste schwacher Themen
        strong_topics: Liste starker Themen

    Returns:
        dict mit status und badge (falls neu)
    """
    data = _load_data()

    percentage = round((score / max_score) * 100, 1) if max_score > 0 else 0

    result = {
        "date": datetime.now(timezone.utc).isoformat(),
        "module": module,
        "module_name": module_name,
        "score": score,
        "max_score": max_score,
        "percentage": percentage,
        "time_taken_minutes": time_taken_minutes,
        "weak_topics": weak_topics or [],
        "strong_topics": strong_topics or []
    }

    data["results"].append(result)

    # Weak/Strong Topics akkumulieren
    for topic in (weak_topics or []):
        data["weak_topics"][topic] = data["weak_topics"].get(topic, 0) + 1
    for topic in (strong_topics or []):
        data["strong_topics"][topic] = data["strong_topics"].get(topic, 0) + 1

    data = _update_stats(data)

    # Prüfe auf neue Badges
    old_badges = set()
    old_data = _load_data()
    if "badges" in old_data:
        old_badges = set(old_data["badges"])

    new_badges = set(data["badges"]) - old_badges
    new_badge_info = []
    for nb in new_badges:
        if nb in BADGES:
            new_badge_info.append({
                "id": nb,
                "name": BADGES[nb]["name"],
                "emoji": BADGES[nb]["emoji"]
            })

    _save_data(data)

    return {
        "status": "recorded",
        "percentage": percentage,
        "new_badges": new_badge_info,
        "streak_days": data["streak_days"]
    }


def get_stats() -> dict:
    """Gibt das komplette Stats-Dashboard zurück."""
    data = _load_data()
    data = _update_stats(data)

    results = data.get("results", [])

    # Schwächstes Thema
    weak = data.get("weak_topics", {})
    weakest_topic = max(weak, key=weak.get) if weak else None

    # Modul-Statistiken
    module_stats = {}
    for r in results:
        mod = r["module"]
        if mod not in module_stats:
            module_stats[mod] = {
                "module_name": r["module_name"],
                "best_score": r["percentage"],
                "attempts": 0
            }
        module_stats[mod]["attempts"] += 1
        module_stats[mod]["best_score"] = max(module_stats[mod]["best_score"], r["percentage"])

    return {
        "total_quizzes": data["total_quizzes_taken"],
        "average_score": data["average_score"],
        "streak_days": data["streak_days"],
        "badges": [
            {
                "id": bid,
                "name": BADGES[bid]["name"],
                "emoji": BADGES[bid]["emoji"],
                "description": BADGES[bid]["description"]
            }
            for bid in data.get("badges", [])
            if bid in BADGES
        ],
        "module_stats": module_stats,
        "weakest_topic": weakest_topic,
        "weak_topics": weak
    }


def format_stats_message() -> str:
    """Formatiert das Stats-Dashboard als Telegram-Nachricht."""
    stats = get_stats()

    lines = []

    # Header
    lines.append("📊 OpenClaw University — Dein Score")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # Quiz-Historie
    lines.append("🎯 Quiz-Historie")
    module_lines = []
    for mod_id, info in stats["module_stats"].items():
        short = MODULE_META.get(mod_id, {}).get("short", mod_id)
        stars = _get_stars(info["best_score"])
        module_lines.append(
            f"│ {short:15} {info['best_score']:>5.1f}% {stars:5}"
        )

    if module_lines:
        lines.append("┌─────────────────────────────────┐")
        for ml in module_lines:
            lines.append(ml)
        lines.append("└─────────────────────────────────┘")
    else:
        lines.append("│ Noch keine Quizze gemacht.       │")
        lines.append("└─────────────────────────────────┘")
    lines.append("")

    # Statistik
    lines.append("📈 Statistik")
    lines.append(f"• Durchschnitt: {stats['average_score']:.1f}%")
    streak = stats["streak_days"]
    streak_fire = "🔥" * min(streak, 3) if streak > 0 else ""
    lines.append(f"• Streak: {streak} Tage {streak_fire}")
    lines.append(f"• Gesamt Quizze: {stats['total_quizzes']}")
    lines.append("")

    # Badges
    badges = stats["badges"]
    lines.append("🏆 Badges")
    if badges:
        badge_str = " ".join([f"{b['emoji']} {b['name']}" for b in badges])
        lines.append(f"• {badge_str}")
    else:
        lines.append("• Noch keine Badges — mach weiter! 💪")
    lines.append("")

    # Verbesserungs-Tipps
    lines.append("💡 Verbesserungs-Tipps")
    if stats["weakest_topic"]:
        meta = None
        for mod_id, m_info in MODULE_META.items():
            if stats["weakest_topic"] in m_info.get("lesson", ""):
                meta = m_info
                break
        lines.append(f"Schwächstes Thema: {stats['weakest_topic']}")
        if meta:
            lines.append(f"→ Wiederhole {meta['lesson']}")
        else:
            lines.append("→ Wiederhole die entsprechende Lesson")
    else:
        lines.append("• Alle Themen gleichmäßig — gut gemacht! 🎉")

    return "\n".join(lines)


def get_today_status() -> dict:
    """Prüft ob heute ein Quiz gemacht wurde."""
    data = _load_data()
    today = datetime.now(timezone.utc).date()

    for r in data.get("results", []):
        dt = datetime.fromisoformat(r["date"].replace("Z", "+00:00"))
        if dt.date() == today:
            return {"done_today": True, "result": r}

    return {"done_today": False}


# ============================================================================
# MAIN (CLI-Test)
# ============================================================================

if __name__ == "__main__":
    import sys

    print("[University] Score Dashboard geladen.")
    print(f"Storage: {QUIZ_RESULTS_FILE}")

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "stats":
            print(format_stats_message())
        elif cmd == "status":
            print(get_today_status())
        elif cmd == "record" and len(sys.argv) >= 5:
            result = record_quiz_result(
                module=sys.argv[2],
                module_name=sys.argv[3],
                score=int(sys.argv[4]),
                max_score=int(sys.argv[5]),
                time_taken_minutes=float(sys.argv[6]) if len(sys.argv) > 6 else 10
            )
            print(f"Result recorded: {result}")
        else:
            print(f"Usage: {sys.argv[0]} stats|status|record")
    else:
        data = _load_data()
        print(f"Geladene Daten: {len(data.get('results', []))} Ergebnisse")
        print(f"Badges: {data.get('badges', [])}")
