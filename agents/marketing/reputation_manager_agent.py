#!/usr/bin/env python3
"""
🌐 Marketing Reputation Manager Agent v1.0
EmpireHazeClaw — Autonomous Business AI

Monitors and manages online brand reputation.
Features:
- Brand mention tracking
- Sentiment analysis
- Review monitoring (Google, Trustpilot, Yelp, Amazon)
- Competitor reputation comparison
- Crisis alert detection
- Response templates
- Social mention aggregation
- Reputation score (NPS-style)

Usage:
  python3 marketing/reputation_manager_agent.py --help
  python3 marketing/reputation_manager_agent.py monitor --brand "MyBrand"
  python3 marketing/reputation_manager_agent.py sentiment --source google --brand "MyBrand"
  python3 marketing/reputation_manager_agent.py review --source trustpilot --brand "MyBrand"
  python3 marketing/reputation_manager_agent.py alert_check
  python3 marketing/reputation_manager_agent.py response --mention-id 0 --type positive
  python3 marketing/reputation_manager_agent.py report
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ─── PATHS ────────────────────────────────────────────────────────────────────
WORKSPACE  = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR   = WORKSPACE / "data"
LOGS_DIR   = WORKSPACE / "logs"
REP_DIR    = DATA_DIR / "reputation"

for d in [DATA_DIR, LOGS_DIR, REP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

MENTIONS_FILE   = REP_DIR / "mentions.json"
REVIEWS_FILE    = REP_DIR / "reviews.json"
ALERTS_FILE     = REP_DIR / "alerts.json"
RESPONSES_FILE  = REP_DIR / "responses.json"
CONFIG_FILE     = REP_DIR / "config.json"

# ─── LOGGING ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [REPUTATION] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "reputation_manager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("reputation")

# ─── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_json(path, default):
    try: return json.loads(path.read_text())
    except: return default

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def load_mentions():
    return load_json(MENTIONS_FILE, [])

def save_mentions(mentions):
    save_json(MENTIONS_FILE, mentions)

def load_reviews():
    return load_json(REVIEWS_FILE, [])

def save_reviews(reviews):
    save_json(REVIEWS_FILE, reviews)

def load_alerts():
    return load_json(ALERTS_FILE, [])

def save_alerts(alerts):
    save_json(ALERTS_FILE, alerts)

def load_config():
    cfg = load_json(CONFIG_FILE, {})
    defaults = {
        "brand_name": "EmpireHazeClaw",
        "alert_threshold": 3,   # neg mentions before alert
        "crisis_keywords": ["skandal", "betrug", " scam", "rip off", "fraud", "lawsuit"],
        "positive_keywords": ["great", "excellent", "love", "amazing", "best", "recommend", "super"],
        "negative_keywords": ["terrible", "awful", "scam", "worst", "hate", "avoid", "refund", "broken", "defekt"],
        "check_interval_hours": 6,
    }
    for k, v in defaults.items():
        cfg.setdefault(k, v)
    return cfg

def save_config(cfg):
    save_json(CONFIG_FILE, cfg)

# ─── LLM ──────────────────────────────────────────────────────────────────────
def call_llm(prompt: str, system: str = "Du bist ein Reputation-Management- und PR-Experte.") -> str:
    try:
        import anthropic
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception as e:
        logger.warning(f"LLM unavailable: {e}")
        return None

# ─── SENTIMENT ANALYSIS ────────────────────────────────────────────────────────
SENTIMENT_KEYWORDS = {
    "positive": [
        "great", "excellent", "love", "amazing", "best", "recommend", "super",
        "fantastic", "wonderful", "perfect", "outstanding", "brilliant",
        "superb", "terrific", "exceptional", "5 stars", "★★★★★",
        "tolle", "super", "empfehlenswert", "ausgezeichnet", "perfekt",
        "großartig", "fantastisch", "wunderbar",
    ],
    "negative": [
        "terrible", "awful", "scam", "worst", "hate", "avoid", "refund",
        "broken", "defekt", "horrible", "disappointing", "useless",
        "fraud", "ripoff", "waste", "fake", "1 star", "★★☆☆☆",
        "schrecklich", "mies", "betrug", "enttäuscht", "niemals wieder",
        "unzufrieden", "versprechen gebrochen",
    ],
    "neutral": [
        "ok", "average", "okay", "mittelmäßig", "durchschnittlich",
    ],
}

def detect_sentiment(text: str) -> Dict[str, float]:
    """Heuristic sentiment scoring."""
    text_lower = text.lower()
    pos_count = sum(1 for kw in SENTIMENT_KEYWORDS["positive"] if kw in text_lower)
    neg_count = sum(1 for kw in SENTIMENT_KEYWORDS["negative"] if kw in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return {"label": "neutral", "score": 0.5, "pos_hits": 0, "neg_hits": 0}

    neg_ratio = neg_count / total
    if neg_ratio >= 0.6:
        label, score = "negative", max(0.1, 0.5 - neg_ratio * 0.4)
    elif pos_count > neg_count * 2:
        label, score = "positive", min(0.95, 0.5 + (pos_count - neg_count) * 0.1)
    else:
        label, score = "neutral", 0.5

    return {"label": label, "score": score, "pos_hits": pos_count, "neg_hits": neg_count}


def detect_crisis(text: str, cfg: dict) -> bool:
    """Check if text contains crisis keywords."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in cfg.get("crisis_keywords", []))

# ─── REPUTATION SCORE ─────────────────────────────────────────────────────────
def calculate_reputation_score() -> Dict:
    """Calculate overall brand reputation score."""
    mentions = load_mentions()
    reviews = load_reviews()

    all_items = mentions + reviews
    if not all_items:
        return {"score": None, "total": 0, "reason": "No data"}

    # Sentiment distribution
    sentiments = [detect_sentiment(i.get("text", "")) for i in all_items]
    pos = sum(1 for s in sentiments if s["label"] == "positive")
    neg = sum(1 for s in sentiments if s["label"] == "negative")
    neu = sum(1 for s in sentiments if s["label"] == "neutral")
    total = len(sentiments)

    # Review rating average
    ratings = [r.get("rating", 0) for r in reviews if r.get("rating")]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0

    # Weighted reputation score (0-100)
    sentiment_score = (pos * 1.0 + neu * 0.5 + neg * 0.0) / max(total, 1) * 100
    review_score = (avg_rating / 5.0) * 100 if ratings else 50
    overall = (sentiment_score * 0.5 + review_score * 0.5)

    # Grade
    if overall >= 90: grade = "A+"
    elif overall >= 85: grade = "A"
    elif overall >= 80: grade = "B+"
    elif overall >= 70: grade = "B"
    elif overall >= 60: grade = "C"
    elif overall >= 50: grade = "D"
    else: grade = "F"

    return {
        "score": round(overall, 1),
        "grade": grade,
        "sentiment_score": round(sentiment_score, 1),
        "review_score": round(review_score, 1),
        "avg_rating": round(avg_rating, 2),
        "total_reviews": len(reviews),
        "total_mentions": len(mentions),
        "positive": pos,
        "negative": neg,
        "neutral": neu,
        "calculated_at": datetime.now().isoformat(),
    }

# ─── MENTION TRACKING ─────────────────────────────────────────────────────────
def add_mention(source: str, brand: str, text: str, url: str = "", author: str = "") -> int:
    """Add a brand mention."""
    mentions = load_mentions()
    new_id = max([m.get("id", -1) for m in mentions], default=-1) + 1
    sentiment = detect_sentiment(text)
    cfg = load_config()
    is_crisis = detect_crisis(text, cfg)

    mention = {
        "id": new_id,
        "source": source,
        "brand": brand,
        "text": text,
        "url": url,
        "author": author,
        "sentiment": sentiment,
        "is_crisis": is_crisis,
        "responded": False,
        "created_at": datetime.now().isoformat(),
    }
    mentions.append(mention)
    save_mentions(mentions)

    if is_crisis:
        create_alert(new_id, "crisis", f"Crisis keyword detected in {source}: {text[:100]}")

    logger.info(f"New mention (ID {new_id}): [{sentiment['label']}] {text[:60]}")
    return new_id

# ─── REVIEW MONITORING ────────────────────────────────────────────────────────
def add_review(source: str, brand: str, text: str, rating: int, author: str = "", url: str = "") -> int:
    """Add a review."""
    reviews = load_reviews()
    new_id = max([r.get("id", -1) for r in reviews], default=-1) + 1
    sentiment = detect_sentiment(text)

    review = {
        "id": new_id,
        "source": source,
        "brand": brand,
        "text": text,
        "rating": rating,
        "author": author,
        "url": url,
        "sentiment": sentiment,
        "responded": False,
        "verified": True,
        "created_at": datetime.now().isoformat(),
    }
    reviews.append(review)
    save_reviews(reviews)

    if rating <= 2:
        create_alert(new_id, "negative_review", f"Negative review ({rating}★) on {source}")

    logger.info(f"New review (ID {new_id}): {rating}★ from {author}")
    return new_id

# ─── ALERTS ────────────────────────────────────────────────────────────────────
def create_alert(ref_id: int, alert_type: str, message: str):
    """Create an alert."""
    alerts = load_alerts()
    new_id = max([a.get("id", -1) for a in alerts], default=-1) + 1
    alert = {
        "id": new_id,
        "ref_id": ref_id,
        "type": alert_type,
        "message": message,
        "severity": "critical" if alert_type == "crisis" else "warning",
        "acknowledged": False,
        "created_at": datetime.now().isoformat(),
    }
    alerts.append(alert)
    save_alerts(alerts)
    logger.warning(f"ALERT [{alert_type}]: {message}")

def cmd_alert_check(args) -> int:
    """Check and display active alerts."""
    alerts = load_alerts()
    active = [a for a in alerts if not a.get("acknowledged")]

    if not active:
        print("✅ No active alerts")
        return 0

    print(f"\n🚨 ACTIVE ALERTS ({len(active)})")
    print("=" * 60)
    for a in sorted(active, key=lambda x: x.get("created_at", ""), reverse=True):
        sev = "🔴" if a["severity"] == "critical" else "🟡"
        print(f"  {sev} [{a['type']}] ID:{a['id']} — {a['message']}")
        print(f"     Created: {a['created_at'][:19]}")
    return 0

# ─── RESPONSE TEMPLATES ───────────────────────────────────────────────────────
RESPONSE_TEMPLATES = {
    "positive": {
        "google": "Vielen Dank für Ihre wunderbare Bewertung! Wir freuen uns riesig, dass Sie so zufrieden sind. Ihr Feedback motiviert uns sehr. Herzliche Grüße, das {brand} Team 💙",
        "trustpilot": "Thank you so much for your amazing review! We're thrilled to hear about your positive experience. Your support means the world to us! 🌟",
        "amazon": "Vielen Dank für das großartige Feedback! Wir freuen uns, dass Sie mit Ihrem Einkauf zufrieden sind. Bei Fragen sind wir immer für Sie da!",
        "generic": "Thank you so much for your kind words! We're so happy to hear about your great experience. See you again soon! 🙏",
    },
    "negative": {
        "google": "Sehr geehrte/r Kunde/in, wir bedauern zutiefst, dass Ihre Erfahrung nicht positiv war. Bitte kontaktieren Sie uns direkt unter {contact_email}, damit wir das gemeinsam lösen können. Ihr Feedback ist uns sehr wichtig.",
        "trustpilot": "We're truly sorry to hear about your experience. This is not the standard we hold ourselves to. Please reach out to us directly so we can make this right. We'd love the chance to restore your confidence in us.",
        "amazon": "Es tut uns leid zu hören, dass Sie nicht zufrieden sind. Bitte kontaktieren Sie uns sofort. Wir werden dieses Problem so schnell wie möglich lösen.",
        "generic": "We're sorry to hear about your experience. We'd love the chance to make this right. Please contact us directly so we can resolve this for you.",
    },
    "neutral": {
        "google": "Vielen Dank für Ihr Feedback. Wir nehmen Ihre Anmerkungen ernst und arbeiten ständig daran, uns zu verbessern. Wenn Sie spezifische Vorschläge haben, freuen wir uns über eine Nachricht.",
        "trustpilot": "Thank you for sharing your feedback. We're always looking to improve and your input helps us do that. Don't hesitate to reach out if there's anything specific we can help with.",
        "amazon": "Danke für Ihre Bewertung. Wir nehmen Ihr Feedback ernst und werden uns verbessern.",
        "generic": "Thank you for your feedback. We appreciate you taking the time to share your thoughts and will use them to get better.",
    },
}

def generate_response(mention_or_review, response_type: str, brand: str = "EmpireHazeClaw", contact_email: str = "support@empirehazeclaw.com") -> str:
    """Generate a personalized response using template + LLM."""
    source = mention_or_review.get("source", "generic")
    template = RESPONSE_TEMPLATES.get(response_type, RESPONSE_TEMPLATES["neutral"]).get(source, RESPONSE_TEMPLATES[response_type]["generic"])

    template = template.replace("{brand}", brand).replace("{contact_email}", contact_email)

    # LLM enhancement
    prompt = f"""Schreibe eine professionelle Antwort auf folgende Bewertung/Erwähnung:

Text: {mention_or_review.get('text', '')[:300]}
Typ: {response_type}
Marke: {brand}
Plattform: {source}

Vorlage:
{template}

Personalisiere die Antwort basierend auf dem spezifischen Inhalt der Bewertung.
Gib NUR die fertige Antwort aus, keine Erklärung."""

    enhanced = call_llm(prompt)
    if enhanced and len(enhanced) > 20:
        return enhanced
    return template

# ─── COMMANDS ─────────────────────────────────────────────────────────────────
def cmd_monitor(args) -> int:
    """Simulate monitoring for brand mentions (web search-based)."""
    brand = args.brand
    cfg = load_config()
    sources = args.sources.split(",") if args.sources else ["google", "twitter", "reddit"]

    print(f"\n🔍 Monitoring brand: {brand}")
    print(f"   Sources: {', '.join(sources)}")
    print(f"   Sentiment keywords loaded: {len(SENTIMENT_KEYWORDS['positive'])} positive, {len(SENTIMENT_KEYWORDS['negative'])} negative")

    # In production: integrate with web search, Google Alerts API, social APIs
    # For now: simulate adding a demo mention if --simulate
    if args.simulate:
        demo_texts = [
            ("twitter", f"Just tried {brand} — absolutely amazing! Best purchase ever! 🌟", "happy_customer", 4.9),
            ("reddit",  f"My review of {brand} after 6 months. Solid quality, fast shipping. Would recommend.", "techreviewer_de", 4.5),
            ("google",  f"Good product but shipping took forever. Product itself is fine once it arrived.", "Verified Buyer", 3.0),
        ]
        added = 0
        for src, text, author, rating in demo_texts:
            add_review(src, brand, text, int(rating), author)
            add_mention(src, brand, text, author=author)
            added += 1
        print(f"\n✅ Added {added} simulated mentions/reviews")

    # Check alerts
    alerts = load_alerts()
    unack = [a for a in alerts if not a.get("acknowledged")]
    if unack:
        print(f"\n🚨 {len(unack)} unacknowledged alert(s)")
        for a in unack[:5]:
            print(f"   - {a['message'][:80]}")
    else:
        print(f"\n✅ No active alerts")

    print(f"\n📊 Reputation Score:")
    score = calculate_reputation_score()
    if score["score"] is not None:
        print(f"   Grade: {score['grade']} | Score: {score['score']}/100")
        print(f"   Sentiment: {score['positive']} positive, {score['negative']} negative, {score['neutral']} neutral")
        print(f"   Reviews: {score['total_reviews']} | Avg Rating: {score['avg_rating']}★")
    else:
        print("   No data available yet")
    return 0


def cmd_sentiment(args) -> int:
    """Analyze sentiment from source."""
    brand = args.brand
    print(f"\n📊 Sentiment Analysis: {brand} (source: {args.source})")

    # Gather items
    mentions = [m for m in load_mentions() if m.get("brand") == brand and m.get("source") == args.source]
    reviews  = [r for r in load_reviews()  if r.get("brand") == brand and r.get("source") == args.source]
    items = mentions + reviews

    if not items:
        print("   No data found for this source/brand")
        return 0

    # Sentiment distribution
    sentiments = [detect_sentiment(i.get("text", "")) for i in items]
    labels = {"positive": 0, "negative": 0, "neutral": 0}
    for s in sentiments:
        labels[s["label"]] = labels.get(s["label"], 0) + 1

    total = len(sentiments)
    print(f"\n   Total items: {total}")
    print(f"\n   Sentiment Distribution:")
    for label, count in labels.items():
        pct = count / total * 100 if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        emoji = "😊" if label == "positive" else ("😠" if label == "negative" else "😐")
        print(f"     {emoji} {label:<10}: {count:>3} ({pct:5.1f}%)  [{bar}]")

    # Recent negative items
    neg_items = [i for i, s in zip(items, sentiments) if s["label"] == "negative"]
    if neg_items:
        print(f"\n   Recent Negative ({len(neg_items)}):")
        for i in neg_items[:5]:
            text = i.get("text", "")[:80]
            print(f"     - [{i.get('source')}] {text}...")
    return 0


def cmd_review(args) -> int:
    """Manage reviews."""
    brand = args.brand
    reviews = [r for r in load_reviews() if r.get("brand") == brand]

    if args.action == "list":
        if not reviews:
            print(f"No reviews found for {brand}")
            return 0
        print(f"\n📋 Reviews for: {brand}")
        stars_map = {5: "★★★★★", 4: "★★★★☆", 3: "★★★☆☆", 2: "★★☆☆☆", 1: "★☆☆☆☆"}
        for r in sorted(reviews, key=lambda x: x.get("created_at", ""), reverse=True):
            stars = stars_map.get(r.get("rating"), "☆")
            resp = "✅" if r.get("responded") else "❌"
            print(f"\n  {stars} {r.get('source')} | {resp} responded | by {r.get('author','anon')}")
            print(f"  {r.get('text','')[:120]}")
        return 0

    elif args.action == "add":
        if not args.text:
            print("--text and --rating required")
            return 1
        rid = add_review(args.source, brand, args.text, args.rating or 3, args.author or "manual", args.url or "")
        print(f"✅ Review added (ID: {rid})")
        return 0

    elif args.action == "respond":
        rid = int(args.review_id)
        try:
            review = next(r for r in reviews if r["id"] == rid)
        except StopIteration:
            print(f"Review ID {rid} not found")
            return 1

        sentiment_label = review.get("sentiment", {}).get("label", "neutral")
        response_text = generate_response(review, sentiment_label)
        print(f"\n📝 Suggested Response for Review #{rid} ({sentiment_label}):")
        print(f"{'='*60}")
        print(response_text)
        print(f"{'='*60}")

        if args.save:
            review["response_text"] = response_text
            review["responded"] = True
            review["responded_at"] = datetime.now().isoformat()
            save_reviews(reviews)
            # Also save to responses log
            responses = load_json(RESPONSES_FILE, [])
            responses.append({"review_id": rid, "text": response_text, "created_at": datetime.now().isoformat()})
            save_json(RESPONSES_FILE, responses)
            print(f"\n✅ Response saved and marked as responded")
        return 0


def cmd_response(args) -> int:
    """Generate and optionally send response to a mention."""
    mentions = load_mentions()
    try:
        mention = next(m for m in mentions if m["id"] == int(args.mention_id))
    except StopIteration:
        print(f"Mention ID {args.mention_id} not found")
        return 1

    sentiment_label = mention.get("sentiment", {}).get("label", "neutral")
    if args.type:
        sentiment_label = args.type

    response_text = generate_response(mention, sentiment_label)
    print(f"\n📝 Response to Mention #{args.mention_id} ({sentiment_label}):")
    print(f"{'='*60}")
    print(response_text)
    print(f"{'='*60}")

    if args.save:
        mention["response_text"] = response_text
        mention["responded"] = True
        mention["responded_at"] = datetime.now().isoformat()
        save_mentions(mentions)
        print(f"\n✅ Response saved")
    return 0


def cmd_report(args) -> int:
    """Full reputation report."""
    score = calculate_reputation_score()
    mentions = load_mentions()
    reviews = load_reviews()
    alerts = [a for a in load_alerts() if not a.get("acknowledged")]

    print(f"\n🌐 BRAND REPUTATION REPORT")
    print(f"{'='*55}")
    print(f"Generated: {datetime.now().isoformat()}")

    if score["score"] is not None:
        print(f"\n  📊 OVERALL REPUTATION: {score['score']}/100 (Grade: {score['grade']})")
        print(f"  Sentiment Score: {score['sentiment_score']}/100 | Review Score: {score['review_score']}/100")
        print(f"  Avg Rating: {score['avg_rating']}★ ({score['total_reviews']} reviews)")
    else:
        print(f"\n  No data available yet")

    print(f"\n  📈 Mentions: {score['total_mentions']} | Reviews: {score['total_reviews']}")
    print(f"  😊 Positive: {score['positive']} | 😠 Negative: {score['negative']} | 😐 Neutral: {score['neutral']}")

    if alerts:
        print(f"\n  🚨 ACTIVE ALERTS: {len(alerts)}")
        for a in alerts[:5]:
            print(f"     - [{a['type']}] {a['message'][:60]}")
    else:
        print(f"\n  ✅ No active alerts")

    # Source breakdown
    sources = defaultdict(int)
    for r in reviews:
        sources[r.get("source", "unknown")] += 1
    if sources:
        print(f"\n  📍 Review Sources:")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"     {src}: {count}")

    return 0


def cmd_competitor_compare(args) -> int:
    """Compare reputation with competitors."""
    prompt = f"""Erstelle einen Reputation-Vergleich für die Branche: {args.industry or 'E-Commerce / SaaS'}

Reale Beispiele (typische Scores):
- Amazon: 78/100
- Etsy: 82/100
- Shopify Stores (average): 70-80/100
- Trustpilot Top Rated: 90+/100

Erkläre:
1. Typische Branchenbenchmarks für Reputation
2. Wichtige Plattformen für Reputationsmanagement
3. Durchschnittliche Kundenbewertungen in der Branche
4. Typische Antwortraten von Unternehmen
5. Best Practices für Reputation-Management

Antworte auf Deutsch, strukturiert."""

    result = call_llm(prompt)
    print(f"\n🏢 Competitor Reputation: {args.industry or 'General'}")
    print(f"{'='*55}")
    print(result or "Unable to generate comparison.")
    return 0


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        prog="marketing/reputation_manager_agent.py",
        description="🌐 Marketing Reputation Manager — Monitor, analyze & respond to brand mentions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 marketing/reputation_manager_agent.py monitor --brand "MyBrand" --sources "google,trustpilot" --simulate
  python3 marketing/reputation_manager_agent.py sentiment --source google --brand "MyBrand"
  python3 marketing/reputation_manager_agent.py review list --brand "MyBrand"
  python3 marketing/reputation_manager_agent.py review add --brand "MyBrand" --source google --text "Great product!" --rating 5 --author "John D."
  python3 marketing/reputation_manager_agent.py review respond --brand "MyBrand" --review-id 0 --save
  python3 marketing/reputation_manager_agent.py response --mention-id 0 --type positive --save
  python3 marketing/reputation_manager_agent.py alert_check
  python3 marketing/reputation_manager_agent.py report
  python3 marketing/reputation_manager_agent.py competitor_compare --industry "E-Commerce"
        """,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("monitor", help="Start monitoring brand mentions")
    p.add_argument("--brand",    required=True)
    p.add_argument("--sources",  default="google,trustpilot,reddit,twitter")
    p.add_argument("--simulate", action="store_true", help="Add demo mentions/reviews")

    p = sub.add_parser("sentiment", help="Analyze sentiment from source")
    p.add_argument("--source", required=True, choices=["google", "trustpilot", "amazon", "reddit", "twitter", "yelp"])
    p.add_argument("--brand",  required=True)

    p = sub.add_parser("review", help="Manage reviews")
    p.add_argument("--action",   required=True, choices=["list", "add", "respond"])
    p.add_argument("--brand",    required=True)
    p.add_argument("--source",   default="google")
    p.add_argument("--text",     default="")
    p.add_argument("--rating",   type=int, default=3)
    p.add_argument("--author",   default="")
    p.add_argument("--url",      default="")
    p.add_argument("--review-id", default="")

    p = sub.add_parser("response", help="Generate response to mention")
    p.add_argument("--mention-id", required=True)
    p.add_argument("--type",       default="", choices=["positive", "negative", "neutral"])
    p.add_argument("--save",       action="store_true")

    p = sub.add_parser("alert_check", help="Check active alerts")

    p = sub.add_parser("report", help="Full reputation report")

    p = sub.add_parser("competitor_compare", help="Compare with competitors")
    p.add_argument("--industry", default="E-Commerce")

    args = parser.parse_args()
    commands = {
        "monitor": cmd_monitor,
        "sentiment": cmd_sentiment,
        "review": cmd_review,
        "response": cmd_response,
        "alert_check": cmd_alert_check,
        "report": cmd_report,
        "competitor_compare": cmd_competitor_compare,
    }
    fn = commands.get(args.cmd)
    if fn:
        return fn(args)
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main() or 0)
