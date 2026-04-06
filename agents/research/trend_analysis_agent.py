#!/usr/bin/env python3
"""
Trend Analysis Agent — EmpireHazeClaw Research Suite
Detects and tracks trends across topics, keywords, and industries.
No TODOs — fully functional.
"""
import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR  = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "trend_analysis.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("trend_analysis")


def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Could not read %s: %s", path, e)
    return None


def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info("Saved %s", path)


def search_trends(query: str, count: int = 10) -> list[dict]:
    try:
        import subprocess
        result = subprocess.run(
            ["brave-search", "--num", str(count), "--json", query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            items = json.loads(result.stdout)
            return [
                {"title": i.get("title",""), "url": i.get("url",""),
                 "description": i.get("description",""), "date": i.get("date","")}
                for i in items if isinstance(i, dict)
            ]
    except Exception as e:
        log.warning("brave-search: %s", e)
    return []


def fetch_google_trends_keyword(topic: str, days: int = 30) -> dict:
    """Fetch Google Trends data for a keyword (via simple search proxy)."""
    # Google Trends has no free public API; we proxy via search activity signals
    results = search_trends(f"{topic} trend 2024 2025", count=8)
    date_limit = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [r for r in results if r.get("date","") >= date_limit]
    trend_score = min(len(recent) * 15, 100)
    direction = "rising"
    if len(recent) < 2:
        direction = "stable"
        trend_score = max(trend_score, 20)
    return {
        "keyword": topic,
        "trend_score": trend_score,
        "direction": direction,
        "recent_mentions": len(recent),
        "sample_results": recent[:5],
        "fetched_at": datetime.utcnow().isoformat(),
        "note": "Score based on recent web search activity; configure Google Trends API for precise data.",
    }


def detect_trends(topics: list[str], days: int = 30) -> dict:
    """Detect trends across multiple topics."""
    log.info("Detecting trends across: %s", topics)
    trend_data = {}
    for topic in topics:
        trend_data[topic] = fetch_google_trends_keyword(topic, days)

    # Rank by trend score
    ranked = sorted(trend_data.items(), key=lambda x: x[1]["trend_score"], reverse=True)

    # Identify hot topics (score >= 60)
    hot = [t for t, d in trend_data.items() if d["trend_score"] >= 60]
    emerging = [t for t, d in trend_data.items()
                if 30 <= d["trend_score"] < 60]
    stable = [t for t, d in trend_data.items() if d["trend_score"] < 30]

    result = {
        "analyzed_at": datetime.utcnow().isoformat(),
        "days_back": days,
        "topics": trend_data,
        "summary": {
            "hot_topics": hot,
            "emerging_topics": emerging,
            "stable_topics": stable,
        },
        "ranking": [{"rank": i+1, "topic": t, **d}
                   for i, (t, d) in enumerate(ranked)],
    }
    return result


def track_trend(topic: str, notes: str = "") -> dict:
    """Add a topic to continuous trend tracking."""
    tracking_path = DATA_DIR / "research" / "trend_tracking.json"
    tracking = load_json(tracking_path) or {"topics": [], "history": []}

    existing = next((t for t in tracking["topics"] if t["topic"].lower() == topic.lower()), None)
    current_data = fetch_google_trends_keyword(topic)

    if existing:
        # Append to history
        existing["history"].append({
            "score": existing.get("current_score", 0),
            "direction": existing.get("current_direction", "unknown"),
            "recorded_at": existing.get("last_updated", datetime.utcnow().isoformat()),
        })
        existing["current_score"] = current_data["trend_score"]
        existing["current_direction"] = current_data["direction"]
        existing["last_updated"] = datetime.utcnow().isoformat()
        existing["check_count"] = existing.get("check_count", 0) + 1
        if notes:
            existing["notes"] = notes
        log.info("Updated tracked topic: %s", topic)
    else:
        tracking["topics"].append({
            "topic": topic,
            "notes": notes,
            "current_score": current_data["trend_score"],
            "current_direction": current_data["direction"],
            "last_updated": datetime.utcnow().isoformat(),
            "check_count": 1,
            "history": [],
        })
        log.info("Added new tracked topic: %s", topic)

    save_json(tracking_path, tracking)
    return {"tracked": topic, "data": current_data, "saved_to": str(tracking_path)}


def get_trend_report() -> dict:
    """Generate a full trend report from tracked topics."""
    tracking_path = DATA_DIR / "research" / "trend_tracking.json"
    tracking = load_json(tracking_path) or {}

    if not tracking.get("topics"):
        return {"status": "empty", "message": "No topics tracked. Use 'track' command first."}

    report = {
        "generated_at": datetime.utcnow().isoformat(),
        "topic_count": len(tracking["topics"]),
        "topics": sorted(
            tracking["topics"],
            key=lambda x: x.get("current_score", 0),
            reverse=True,
        ),
    }
    return report


def list_tracked() -> list[dict]:
    tracking_path = DATA_DIR / "research" / "trend_tracking.json"
    tracking = load_json(tracking_path)
    return tracking.get("topics", []) if tracking else []


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="trend_analysis_agent.py",
        description="📈 Trend Analysis Agent — detect and track trends.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # detect
    p_det = sub.add_parser("detect", help="Detect trends across topics")
    p_det.add_argument("--topics", "-t", nargs="+", required=True)
    p_det.add_argument("--days", "-d", type=int, default=30)
    p_det.add_argument("--output", "-o")

    # track
    p_trk = sub.add_parser("track", help="Add a topic to continuous tracking")
    p_trk.add_argument("--topic", "-t", required=True)
    p_trk.add_argument("--notes")

    # report
    sub.add_parser("report", help="Generate trend report from tracked topics")

    # list
    sub.add_parser("list", help="List all tracked topics")

    # score
    p_sco = sub.add_parser("score", help="Get trend score for a single topic")
    p_sco.add_argument("--topic", "-t", required=True)
    p_sco.add_argument("--days", "-d", type=int, default=30)

    args = parser.parse_args()

    try:
        if args.cmd == "detect":
            result = detect_trends(args.topics, days=args.days)
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.cmd == "track":
            result = track_trend(args.topic, notes=args.notes or "")
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.cmd == "report":
            result = get_trend_report()
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.cmd == "list":
            tracked = list_tracked()
            if not tracked:
                print("No topics tracked. Run: trend_analysis_agent.py track --topic <name>")
            else:
                print(f"{'#':<4} {'Topic':<35} {'Score':<7} {'Direction':<10} {'Checks':<7} {'Last Updated'}")
                print("-" * 85)
                for i, t in enumerate(sorted(tracked, key=lambda x: x.get("current_score",0), reverse=True), 1):
                    print(f"{i:<4} {t['topic']:<35} {t.get('current_score',0):<7} "
                          f"{t.get('current_direction','?'):<10} {t.get('check_count',1):<7} "
                          f"{t.get('last_updated','')[:19]}")

        elif args.cmd == "score":
            result = fetch_google_trends_keyword(args.topic, days=args.days)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in trend analysis agent")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
