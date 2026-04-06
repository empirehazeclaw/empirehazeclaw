#!/usr/bin/env python3
"""
Brand Monitor Agent — EmpireHazeClaw Research Suite
Monitors brand mentions, sentiment, and visibility over time.
No TODOs — fully functional.
"""
import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
LOG_DIR  = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"

LOG_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "research").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "brand_monitor.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("brand_monitor")


def load_json(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception as e:
            log.warning("Could not read %s: %s", path, e)
    return None


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info("Saved %s", path)


POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "love", "best", "awesome",
    "recommend", "helpful", "happy", "satisfied", "perfect", "wonderful",
    "fantastic", "brilliant", "outstanding", "impressive",
}
NEGATIVE_WORDS = {
    "bad", "terrible", "hate", "worst", "awful", "horrible", "disappointed",
    "broken", "scam", "fail", "overpriced", "useless", "avoid", "problem",
    "refund", "complaint", "angry", "unhappy", "junk",
}


def score_sentiment(text: str) -> dict:
    if not text:
        return {"score": 0, "label": "neutral"}
    words = set(re.findall(r"\b[a-zA-Z']+\b", text.lower()))
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return {"score": 0, "label": "neutral"}
    score = round(((pos - neg) / total) * 100, 1)
    label = "positive" if score > 20 else "negative" if score < -20 else "neutral"
    return {"score": score, "label": label, "positive": pos, "negative": neg}


def search_web(query: str, count: int = 10) -> list[dict]:
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


# ── Brand Registry ────────────────────────────────────────────────────────────
def get_registry_path() -> Path:
    return DATA_DIR / "research" / "brand_monitor_registry.json"


def load_registry() -> dict:
    return load_json(get_registry_path()) or {"brands": [], "mentions": []}


def save_registry(data: dict):
    save_json(get_registry_path(), data)


def register_brand(name: str, industry: str = "", competitors: list = None,
                   keywords: list = None) -> dict:
    """Register a brand for monitoring."""
    registry = load_registry()
    existing = next((b for b in registry["brands"] if b["name"].lower() == name.lower()), None)
    entry = {
        "name": name,
        "industry": industry,
        "competitors": competitors or [],
        "keywords": keywords or [],
        "registered_at": datetime.utcnow().isoformat(),
        "last_scan": None,
        "mention_count": 0,
    }
    if existing:
        idx = registry["brands"].index(existing)
        entry["last_scan"] = existing.get("last_scan")
        entry["mention_count"] = existing.get("mention_count", 0)
        registry["brands"][idx] = entry
        log.info("Updated brand: %s", name)
    else:
        registry["brands"].append(entry)
        log.info("Registered brand: %s", name)
    save_registry(registry)
    return entry


def unregister_brand(name: str) -> bool:
    registry = load_registry()
    original = len(registry["brands"])
    registry["brands"] = [
        b for b in registry["brands"] if b["name"].lower() != name.lower()
    ]
    if len(registry["brands"]) < original:
        save_registry(registry)
        return True
    return False


def list_brands() -> list[dict]:
    return load_registry().get("brands", [])


# ── Mention Scanning ──────────────────────────────────────────────────────────
def scan_brand_mentions(brand_name: str, days_back: int = 30) -> dict:
    """Scan for brand mentions across the web."""
    log.info("Scanning mentions for: %s", brand_name)
    queries = [
        f'"{brand_name}"',
        f'"{brand_name}" reviews',
        f'"{brand_name}" news',
        f'"{brand_name}" opinions',
    ]
    date_limit = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    all_mentions = []
    for q in queries:
        results = search_web(q, count=10)
        for r in results:
            r["query"] = q
            all_mentions.append(r)

    # Deduplicate by URL
    seen = set()
    unique = []
    for m in all_mentions:
        url = m.get("url","")
        if url and url not in seen:
            seen.add(url)
            unique.append(m)

    # Filter to date range
    recent = [m for m in unique if m.get("date","") >= date_limit]

    # Sentiment analysis
    sentiments = []
    for m in recent:
        text = f"{m.get('title','')} {m.get('description','')}"
        sentiments.append(score_sentiment(text))

    pos_count = sum(1 for s in sentiments if s["label"] == "positive")
    neg_count = sum(1 for s in sentiments if s["label"] == "negative")
    neu_count = len(sentiments) - pos_count - neg_count

    # Determine reach by source
    source_breakdown = defaultdict(int)
    for m in recent:
        url = m.get("url","")
        if "twitter" in url or "x.com" in url:
            source_breakdown["twitter/x"] += 1
        elif "linkedin" in url:
            source_breakdown["linkedin"] += 1
        elif "reddit" in url:
            source_breakdown["reddit"] += 1
        elif "news" in url or "article" in url:
            source_breakdown["news"] += 1
        else:
            source_breakdown["other"] += 1

    scan_result = {
        "brand": brand_name,
        "scanned_at": datetime.utcnow().isoformat(),
        "days_back": days_back,
        "total_mentions": len(recent),
        "sentiment": {
            "positive": pos_count,
            "negative": neg_count,
            "neutral": neu_count,
            "overall_label": "positive" if pos_count > neg_count else "negative" if neg_count > pos_count else "neutral",
        },
        "source_breakdown": dict(source_breakdown),
        "mentions": [
            {"title": m["title"], "url": m["url"], "date": m["date"],
             "description": m["description"][:200]}
            for m in recent[:30]
        ],
    }

    # Update registry
    registry = load_registry()
    for brand in registry["brands"]:
        if brand["name"].lower() == brand_name.lower():
            brand["last_scan"] = scan_result["scanned_at"]
            brand["mention_count"] = len(recent)
            break
    save_registry(registry)

    # Save mention history
    history_path = DATA_DIR / "research" / f"mentions_{brand_name.lower().replace(' ','_')}_{datetime.utcnow().strftime('%Y-%m-%d')}.json"
    save_json(history_path, scan_result)

    return scan_result


def get_mention_history(brand_name: str) -> list[dict]:
    """Get all historical scans for a brand."""
    pattern = f"mentions_{brand_name.lower().replace(' ','_')}_*.json"
    research_dir = DATA_DIR / "research"
    files = sorted(research_dir.glob(pattern), reverse=True)
    history = []
    for f in files:
        data = load_json(f)
        if data:
            history.append(data)
    return history


def generate_alert(brand_name: str, threshold: int = 5) -> dict:
    """Generate an alert if negative mentions spike."""
    history = get_mention_history(brand_name)
    if len(history) < 2:
        return {"alert": False, "reason": "Insufficient history"}

    latest = history[0]
    previous = history[1] if len(history) > 1 else None

    alert = False
    reason = ""
    if latest["sentiment"]["negative"] >= threshold:
        alert = True
        reason = f"High negative mentions: {latest['sentiment']['negative']} negative"
    elif previous and latest["sentiment"]["negative"] > previous["sentiment"]["negative"] * 2:
        alert = True
        reason = f"Negative spike: {previous['sentiment']['negative']} → {latest['sentiment']['negative']}"

    return {
        "alert": alert,
        "reason": reason,
        "latest_scan": latest["scanned_at"],
        "negative_count": latest["sentiment"]["negative"],
        "positive_count": latest["sentiment"]["positive"],
    }


# ── Competitor Monitoring ──────────────────────────────────────────────────────
def monitor_competitors(brand_name: str) -> dict:
    """Monitor brand vs competitors mentioned together."""
    log.info("Monitoring competitors for: %s", brand_name)
    registry = load_registry()
    brand_entry = next((b for b in registry["brands"]
                        if b["name"].lower() == brand_name.lower()), None)
    competitors = brand_entry.get("competitors", []) if brand_entry else []

    if not competitors:
        return {"brand": brand_name, "competitors": [], "note": "No competitors registered"}

    results = {}
    for comp in competitors:
        mentions = scan_brand_mentions(comp, days_back=14)
        results[comp] = {
            "total_mentions": mentions["total_mentions"],
            "sentiment": mentions["sentiment"],
            "last_scan": mentions["scanned_at"],
        }

    return {
        "brand": brand_name,
        "competitor_data": results,
        "compared_at": datetime.utcnow().isoformat(),
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="brand_monitor_agent.py",
        description="📡 Brand Monitor Agent — track brand mentions, sentiment, and alerts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # register
    p_reg = sub.add_parser("register", help="Register a brand for monitoring")
    p_reg.add_argument("--name", "-n", required=True)
    p_reg.add_argument("--industry", "-i", default="")
    p_reg.add_argument("--competitors", "-c", nargs="*", default=[])
    p_reg.add_argument("--keywords", "-k", nargs="*", default=[])

    # unregister
    p_un = sub.add_parser("unregister", help="Remove a brand from monitoring")
    p_un.add_argument("--name", "-n", required=True)

    # list
    sub.add_parser("list", help="List all registered brands")

    # scan
    p_scan = sub.add_parser("scan", help="Scan for brand mentions")
    p_scan.add_argument("--brand", "-b", required=True)
    p_scan.add_argument("--days", "-d", type=int, default=30)
    p_scan.add_argument("--output", "-o")

    # history
    p_hist = sub.add_parser("history", help="Show mention history for a brand")
    p_hist.add_argument("--brand", "-b", required=True)

    # alert
    p_alert = sub.add_parser("alert", help="Check for alerts on a brand")
    p_alert.add_argument("--brand", "-b", required=True)
    p_alert.add_argument("--threshold", "-t", type=int, default=5)

    # competitors
    p_comp = sub.add_parser("competitors", help="Monitor brand vs competitors")
    p_comp.add_argument("--brand", "-b", required=True)

    args = parser.parse_args()

    try:
        if args.cmd == "register":
            result = register_brand(args.name, industry=args.industry,
                                   competitors=args.competitors, keywords=args.keywords)
            print(f"✅ Registered: {result['name']}")

        elif args.cmd == "unregister":
            ok = unregister_brand(args.name)
            print(f"{'✅ Removed' if ok else '❌ Not found'}: {args.name}")

        elif args.cmd == "list":
            brands = list_brands()
            if not brands:
                print("No brands registered. Run: brand_monitor_agent.py register --name <brand>")
            else:
                print(f"{'Brand':<25} {'Industry':<20} {'Mentions':<9} {'Last Scan'}")
                print("-" * 75)
                for b in brands:
                    print(f"{b['name']:<25} {b.get('industry',''):<20} "
                          f"{b.get('mention_count',0):<9} {str(b.get('last_scan','Never'))[:19]}")

        elif args.cmd == "scan":
            result = scan_brand_mentions(args.brand, days_back=args.days)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "history":
            history = get_mention_history(args.brand)
            if not history:
                print(f"No history for '{args.brand}'. Run a scan first.")
            else:
                print(f"{'Date':<20} {'Total':<7} {'Positive':<9} {'Negative':<9} {'Label'}")
                print("-" * 65)
                for h in history[:20]:
                    s = h.get("sentiment", {})
                    print(f"{h.get('scanned_at','')[:19]:<20} "
                          f"{h.get('total_mentions',0):<7} "
                          f"{s.get('positive',0):<9} "
                          f"{s.get('negative',0):<9} "
                          f"{s.get('overall_label','?')}")

        elif args.cmd == "alert":
            result = generate_alert(args.brand, threshold=args.threshold)
            if result["alert"]:
                print(f"🚨 ALERT: {result['reason']}")
                print(f"   Negative: {result['negative_count']} | Positive: {result['positive_count']}")
            else:
                print(f"✅ No alert: {result.get('reason', 'All clear')}")

        elif args.cmd == "competitors":
            result = monitor_competitors(args.brand)
            print(json.dumps(result, indent=2, ensure_ascii=False))

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in brand monitor agent")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
