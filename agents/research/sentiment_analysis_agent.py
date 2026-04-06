#!/usr/bin/env python3
"""
Sentiment Analysis Agent — EmpireHazeClaw Research Suite
Analyzes sentiment from text, web search results, or saved data files.
No TODOs — fully functional.
"""
import argparse
import json
import logging
import re
import sys
from datetime import datetime
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
        logging.FileHandler(LOG_DIR / "sentiment_analysis.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
log = logging.getLogger("sentiment_analysis")


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


# ── Sentiment Engine ──────────────────────────────────────────────────────────
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "wonderful", "fantastic", "love",
    "best", "perfect", "awesome", "brilliant", "outstanding", "superb", "positive",
    "happy", "satisfied", "recommend", "helpful", "reliable", "easy", "fast",
    "efficient", "beautiful", "nice", "friendly", "professional", "quality",
    "powerful", "innovative", "impressive", "strong", "valuable", "affordable",
    "intuitive", "smooth", "seamless", "impressed", "exceptional",
}
NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "horrible", "worst", "hate", "poor", "fail",
    "broken", "buggy", "slow", "frustrating", "disappointed", "useless", "scam",
    "overpriced", "unreliable", "complicated", "confusing", "difficult", "annoying",
    "expensive", "waste", "avoid", "problem", "issue", "crash", "error", "bug",
    "refund", "cancel", "support", "complaint", "negative", "angry", "unhappy",
    "sucks", "garbage", "trash", "junk", "fake", "ripoff",
}
INTENSIFIERS = {"very", "really", "extremely", "absolutely", "highly", "incredibly", "so"}
NEGATORS = {"not", "no", "never", "neither", "none", "hardly", "barely", "scarcely"}


def score_text(text: str) -> dict:
    """Score a piece of text for sentiment. Returns detailed breakdown."""
    if not text:
        return {"score": 0, "label": "neutral", "confidence": 0,
                "positive": 0, "negative": 0, "neutral_count": 0}

    words = re.findall(r"\b[a-zA-Z']+\b", text.lower())
    pos_count = 0
    neg_count = 0
    intensifier_active = False

    for i, word in enumerate(words):
        if word in INTENSIFIERS:
            intensifier_active = True
            continue
        if word in NEGATORS and i + 1 < len(words):
            # Check next word
            next_w = words[i + 1]
            if next_w in POSITIVE_WORDS:
                neg_count += 1
                intensifier_active = False
                continue
            if next_w in NEGATIVE_WORDS:
                pos_count += 1
                intensifier_active = False
                continue

        multiplier = 2 if intensifier_active else 1
        intensifier_active = False

        if word in POSITIVE_WORDS:
            pos_count += multiplier
        elif word in NEGATIVE_WORDS:
            neg_count += multiplier

    total = pos_count + neg_count
    if total == 0:
        score = 0
        label = "neutral"
        confidence = 0
    else:
        score = round(((pos_count - neg_count) / total) * 100, 1)
        if score > 20:
            label = "positive"
        elif score < -20:
            label = "negative"
        else:
            label = "neutral"
        confidence = min(round(total / len(words) * 100, 1), 100)

    return {
        "score": score,
        "label": label,
        "confidence": confidence,
        "positive": pos_count,
        "negative": neg_count,
        "neutral_count": len(words) - pos_count - neg_count,
        "word_count": len(words),
    }


def analyze_search_sentiment(query: str, count: int = 10) -> dict:
    """Analyze sentiment from web search results for a query."""
    try:
        import subprocess
        result = subprocess.run(
            ["brave-search", "--num", str(count), "--json", query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            items = json.loads(result.stdout)
            results = [
                {"title": i.get("title",""), "url": i.get("url",""),
                 "description": i.get("description",""), "date": i.get("date","")}
                for i in items if isinstance(i, dict)
            ]
        else:
            results = []
    except Exception as e:
        log.warning("brave-search: %s", e)
        results = []

    sentiment_scores = []
    for r in results:
        text = f"{r.get('title','')} {r.get('description','')}"
        sentiment_scores.append(score_text(text))

    if sentiment_scores:
        avg_score = round(sum(s["score"] for s in sentiment_scores) / len(sentiment_scores), 1)
        labels = [s["label"] for s in sentiment_scores]
        dominant = max(set(labels), key=labels.count) if labels else "neutral"
        total_pos = sum(s["positive"] for s in sentiment_scores)
        total_neg = sum(s["negative"] for s in sentiment_scores)
    else:
        avg_score = 0
        dominant = "neutral"
        total_pos = total_neg = 0

    return {
        "query": query,
        "result_count": len(results),
        "overall_score": avg_score,
        "overall_label": dominant,
        "total_positive_signals": total_pos,
        "total_negative_signals": total_neg,
        "result_sentiments": sentiment_scores,
        "top_results": [{"title": r["title"], "url": r["url"],
                          "date": r["date"], "score": sentiment_scores[i]["score"]}
                        for i, r in enumerate(results[:5]) if i < len(sentiment_scores)],
        "analyzed_at": datetime.utcnow().isoformat(),
    }


def analyze_brand_sentiment(brand: str, mentions_count: int = 20) -> dict:
    """Analyze overall brand sentiment."""
    queries = [
        f"{brand} reviews",
        f"{brand} customer feedback",
        f"{brand} opinions",
        f"{brand} experience",
    ]
    all_sentiments = []
    for q in queries:
        result = analyze_search_sentiment(q, count=5)
        all_sentiments.append(result)

    all_scores = [s for r in all_sentiments for s in r.get("result_sentiments", [])]
    if all_scores:
        avg_score = round(sum(s["score"] for s in all_scores) / len(all_scores), 1)
        labels = [s["label"] for s in all_scores]
        dominant = max(set(labels), key=labels.count) if labels else "neutral"
    else:
        avg_score = 0
        dominant = "neutral"

    # Save to history
    history_path = DATA_DIR / "research" / "sentiment_history.json"
    history = load_json(history_path) or {"brand_history": []}
    history["brand_history"].append({
        "brand": brand,
        "score": avg_score,
        "label": dominant,
        "recorded_at": datetime.utcnow().isoformat(),
    })
    # Keep last 100 entries
    history["brand_history"] = history["brand_history"][-100:]
    save_json(history_path, history)

    return {
        "brand": brand,
        "overall_score": avg_score,
        "overall_label": dominant,
        "query_results": all_sentiments,
        "history_saved": str(history_path),
        "analyzed_at": datetime.utcnow().isoformat(),
    }


def get_sentiment_history(brand: Optional[str] = None) -> list:
    history_path = DATA_DIR / "research" / "sentiment_history.json"
    history = load_json(history_path) or {"brand_history": []}
    if brand:
        return [e for e in history["brand_history"] if brand.lower() in e.get("brand","").lower()]
    return history["brand_history"][-50:]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="sentiment_analysis_agent.py",
        description="💬 Sentiment Analysis Agent — analyze sentiment from text or web results.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # score text directly
    p_txt = sub.add_parser("score", help="Score sentiment of text directly")
    p_txt.add_argument("--text", "-t", required=True, help="Text to analyze")
    p_txt.add_argument("--output", "-o", help="Save result to JSON file")

    # analyze search query
    p_srch = sub.add_parser("search", help="Analyze sentiment from web search results")
    p_srch.add_argument("--query", "-q", required=True)
    p_srch.add_argument("--count", "-c", type=int, default=10)
    p_srch.add_argument("--output", "-o")

    # brand sentiment
    p_brd = sub.add_parser("brand", help="Analyze brand sentiment from multiple queries")
    p_brd.add_argument("--brand", "-b", required=True)
    p_brd.add_argument("--count", "-c", type=int, default=20)
    p_brd.add_argument("--output", "-o")

    # history
    p_hist = sub.add_parser("history", help="Show sentiment history")
    p_hist.add_argument("--brand", "-b", help="Filter by brand")

    args = parser.parse_args()

    try:
        if args.cmd == "score":
            result = score_text(args.text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))
                print(f"✅ Saved to {args.output}")

        elif args.cmd == "search":
            result = analyze_search_sentiment(args.query, count=args.count)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "brand":
            result = analyze_brand_sentiment(args.brand, mentions_count=args.count)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            if args.output:
                Path(args.output).write_text(json.dumps(result, indent=2))

        elif args.cmd == "history":
            history = get_sentiment_history(args.brand if hasattr(args, 'brand') else None)
            if not history:
                print("No sentiment history found.")
            else:
                print(f"{'Brand':<25} {'Score':<8} {'Label':<12} {'Recorded At'}")
                print("-" * 75)
                for e in reversed(history[-30:]):
                    print(f"{e.get('brand',''):<25} {e.get('score',0):<8} "
                          f"{e.get('label',''):<12} {e.get('recorded_at','')[:19]}")

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted.")
        sys.exit(130)
    except Exception as e:
        log.exception("Error in sentiment analysis agent")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
