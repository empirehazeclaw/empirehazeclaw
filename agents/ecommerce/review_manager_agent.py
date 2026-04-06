#!/usr/bin/env python3
"""
Review Manager Agent - OpenClaw Ecommerce Division
Manages product reviews: monitoring, response templates, sentiment analysis, alerts
Persona: CEO-mode - keep customers happy, protect reputation fast
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

AGENT_NAME = "ReviewManager"
BASE_DIR = Path("/home/clawbot/.openclaw/workspace")
DATA_DIR = BASE_DIR / "data" / "reviews"
LOG_DIR = BASE_DIR / "logs"
REVIEWS_FILE = DATA_DIR / "reviews.json"
TEMPLATES_FILE = DATA_DIR / "response_templates.json"
ALERTS_FILE = DATA_DIR / "alerts.json"
ANALYTICS_FILE = DATA_DIR / "analytics.json"

def setup_logging(verbose: bool = False) -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"review_manager_{datetime.now():%Y%m%d}.log"
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger(AGENT_NAME)
    logger.setLevel(level)
    if logger.handlers:
        logger.handlers.clear()
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = setup_logging()

def load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return default

def save_json(path: Path, data: dict | list) -> bool:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except IOError as e:
        logger.error(f"Failed to save: {e}")
        return False

def init_data():
    if not REVIEWS_FILE.exists():
        save_json(REVIEWS_FILE, {"reviews": []})
    if not TEMPLATES_FILE.exists():
        save_json(TEMPLATES_FILE, {"templates": [
            {"id": "thank_positive", "type": "positive", "subject": "Thank you!", "body": "Hi {customer_name},\n\nThank you for your wonderful review! We're thrilled to hear you had a great experience.\n\nBest,\nThe Team"},
            {"id": "respond_negative", "type": "negative", "subject": "We're sorry", "body": "Hi {customer_name},\n\nWe're truly sorry to hear about your experience. Please contact us at {support_email} so we can make this right.\n\nBest,\nThe Team"},
            {"id": "respond_neutral", "type": "neutral", "subject": "Thank you for feedback", "body": "Hi {customer_name},\n\nThank you for your feedback. If there's anything we can do to improve, let us know.\n\nBest,\nThe Team"},
            {"id": "request_review", "type": "request", "subject": "How was your experience?", "body": "Hi {customer_name},\n\nWe hope you're enjoying your purchase!\n\nWe'd love your feedback: {review_link}\n\nThank you!"}
        ]})
    if not ALERTS_FILE.exists():
        save_json(ALERTS_FILE, {"alerts": []})
    if not ANALYTICS_FILE.exists():
        save_json(ANALYTICS_FILE, {})
    logger.info("Review manager initialized")

POSITIVE_WORDS = {"love","great","excellent","amazing","perfect","awesome","fantastic","wonderful","best","happy","recommend","quality","fast","beautiful","delighted"}
NEGATIVE_WORDS = {"bad","terrible","awful","horrible","worst","hate","disappointed","broken","defective","poor","slow","damaged","refund","waste","useless","garbage"}

def analyze_sentiment(text: str) -> str:
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    if pos > neg: return "positive"
    elif neg > pos: return "negative"
    return "neutral"

def cmd_review_add(args) -> int:
    data = load_json(REVIEWS_FILE, {"reviews": []})
    review = {
        "id": f"REV_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "product_id": args.product_id or "unknown",
        "product_name": args.product_name or "Unknown Product",
        "customer_name": args.customer or "Anonymous",
        "customer_email": args.email or "",
        "rating": args.rating,
        "title": args.title or "",
        "text": args.text or "",
        "sentiment": analyze_sentiment(f"{args.title or ''} {args.text or ''}"),
        "source": args.source or "manual",
        "verified": args.verified,
        "status": "pending",
        "responded": False,
        "created_at": args.date or datetime.now().isoformat(),
        "added_at": datetime.now().isoformat()
    }
    data["reviews"].append(review)
    save_json(REVIEWS_FILE, data)
    icon = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[review["sentiment"]]
    print(f"✅ Review [{review['id']}] {icon} {args.rating}★ from {review['customer_name']}")
    print(f"   Sentiment: {review['sentiment']}")
    return 0

def cmd_review_list(args) -> int:
    data = load_json(REVIEWS_FILE, {"reviews": []})
    reviews = data.get("reviews", [])
    if args.product:
        reviews = [r for r in reviews if args.product.lower() in r.get("product_name","").lower()]
    if args.sentiment:
        reviews = [r for r in reviews if r.get("sentiment") == args.sentiment]
    if args.rating == 1:
        reviews = [r for r in reviews if r.get("rating", 5) == 1]
    if args.unanswered:
        reviews = [r for r in reviews if not r.get("responded")]
    if args.days:
        cutoff = (datetime.now() - timedelta(days=args.days)).isoformat()
        reviews = [r for r in reviews if r.get("created_at","") > cutoff]
    if not reviews:
        print("📝 No reviews match")
        return 0
    print(f"\n📝 Reviews ({len(reviews)}):")
    for r in reviews:
        stars = "★" * r.get("rating",0) + "☆" * (5 - r.get("rating",0))
        icon = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}.get(r.get("sentiment"),"❓")
        resp = "✅" if r.get("responded") else "❌"
        print(f"  [{r['id']}] {icon} {stars} {r.get('customer_name','Anon')} | {r.get('product_name','N/A')} | {resp}")
        if r.get("title"): print(f"     \"{r.get('title')}\"")
    return 0

def cmd_review_response(args) -> int:
    data = load_json(REVIEWS_FILE, {"reviews": []})
    templates = load_json(TEMPLATES_FILE, {"templates": []}).get("templates", [])
    for r in data["reviews"]:
        if r["id"] == args.review_id:
            review = r
            break
    else:
        print(f"❌ Review not found: {args.review_id}")
        return 1
    sentiment = review.get("sentiment", "neutral")
    template = next((t for t in templates if t["id"] == args.template_id), None) if args.template_id else next((t for t in templates if t["type"] == sentiment), None)
    if not template:
        print("❌ Template not found")
        return 1
    resp_text = template["body"]
    resp_text = resp_text.replace("{customer_name}", review.get("customer_name","Customer"))
    resp_text = resp_text.replace("{product_name}", review.get("product_name","our product"))
    resp_text = resp_text.replace("{support_email}", os.getenv("SUPPORT_EMAIL","support@example.com"))
    resp_text = resp_text.replace("{review_link}", args.review_link or "https://example.com/review")
    if args.generate_only:
        print(f"\n📧 Template: {template['id']}\nSubject: {template['subject']}\n{resp_text}")
        return 0
    review["responded"] = True
    review["response_at"] = datetime.now().isoformat()
    review["response_template"] = template["id"]
    save_json(REVIEWS_FILE, data)
    print(f"✅ Response sent to {review['id']}")
    return 0

def cmd_review_analytics(args) -> int:
    data = load_json(REVIEWS_FILE, {"reviews": []})
    reviews = data.get("reviews", [])
    if not reviews:
        print("📊 No review data")
        return 0
    total = len(reviews)
    s_pos = sum(1 for r in reviews if r.get("sentiment") == "positive")
    s_neg = sum(1 for r in reviews if r.get("sentiment") == "negative")
    s_neu = sum(1 for r in reviews if r.get("sentiment") == "neutral")
    r_responded = sum(1 for r in reviews if r.get("responded"))
    avg_rating = sum(r.get("rating",0) for r in reviews) / total
    r_counts = {i: sum(1 for r in reviews if r.get("rating",0) == i) for i in range(1,6)}
    print(f"""
╔══════════════════════════════════════════════════════╗
║           📊 REVIEW ANALYTICS                         ║
╚══════════════════════════════════════════════════════╝
  Total Reviews:   {total}
  Average Rating:  {avg_rating:.2f} ★
  Response Rate:   {r_responded}/{total} ({r_responded/total*100:.1f}%)
  🟢 Positive: {s_pos} ({s_pos/total*100:.1f}%)
  🟡 Neutral:  {s_neu} ({s_neu/total*100:.1f}%)
  🔴 Negative: {s_neg} ({s_neg/total*100:.1f}%)
  ★★★★★ ({r_counts.get(5,0)}) ★★★★☆ ({r_counts.get(4,0)}) ★★★☆☆ ({r_counts.get(3,0)}) ★★☆☆☆ ({r_counts.get(2,0)}) ★☆☆☆☆ ({r_counts.get(1,0)})
""")
    return 0

def cmd_alert(args) -> int:
    data = load_json(ALERTS_FILE, {"alerts": []})
    reviews = load_json(REVIEWS_FILE, {"reviews": []}).get("reviews", [])
    one_star = len([r for r in reviews if r.get("rating",5) == 1 and not r.get("responded")])
    neg_unanswered = len([r for r in reviews if r.get("sentiment") == "negative" and not r.get("responded")])
    if args.list:
        alerts = data.get("alerts", [])
        print(f"\n🔔 Alerts ({len(alerts)}):")
        for a in alerts: print(f"  [{a.get('type')}] {a.get('message','')[:60]}")
        return 0
    if args.clear:
        data["alerts"] = []
        save_json(ALERTS_FILE, data)
        print("✅ Alerts cleared")
        return 0
    print(f"\n🔔 Alert Summary:")
    print(f"  1-star unanswered: {one_star}")
    print(f"  Negative unanswered: {neg_unanswered}")
    if one_star > 0 or neg_unanswered > 0:
        print("⚠️  ACTION: review list --unanswered --sentiment negative")
    return 0

def cmd_template(args) -> int:
    data = load_json(TEMPLATES_FILE, {"templates": []})
    if args.add:
        tpl = {"id": f"TPL_{datetime.now().strftime('%H%M%S')}", "type": args.type or "neutral", "subject": args.subject or "", "body": args.body or ""}
        data["templates"].append(tpl)
        save_json(TEMPLATES_FILE, data)
        print(f"✅ Template '{tpl['id']}' added")
        return 0
    print(f"\n📋 Templates ({len(data.get('templates',[]))}):")
    for t in data.get("templates", []):
        print(f"  [{t['id']}] {t['type']} - {t.get('subject','(no subject)')}")
    return 0

def main():
    parser = argparse.ArgumentParser(description="📝 Review Manager Agent")
    sub = parser.add_subparsers(dest="command", required=True)
    
    rev_p = sub.add_parser("review", help="Manage reviews")
    rev_sub = rev_p.add_subparsers(dest="action")
    ra = rev_sub.add_parser("add", help="Add review")
    ra.add_argument("--product-id"); ra.add_argument("--product-name"); ra.add_argument("--customer")
    ra.add_argument("--email"); ra.add_argument("--rating", type=int, choices=[1,2,3,4,5], required=True)
    ra.add_argument("--title"); ra.add_argument("--text"); ra.add_argument("--source")
    ra.add_argument("--verified", action="store_true"); ra.add_argument("--date")
    ra.set_defaults(func=cmd_review_add)
    rl = rev_sub.add_parser("list", help="List reviews")
    rl.add_argument("--product"); rl.add_argument("--sentiment", choices=["positive","negative","neutral"])
    rl.add_argument("--rating", type=int, choices=[1,2,3,4,5]); rl.add_argument("--unanswered", action="store_true")
    rl.add_argument("--days", type=int)
    rl.set_defaults(func=cmd_review_list)
    rr = rev_sub.add_parser("respond", help="Respond to review")
    rr.add_argument("--review-id", required=True); rr.add_argument("--template-id")
    rr.add_argument("--review-link"); rr.add_argument("--generate-only", action="store_true")
    rr.set_defaults(func=cmd_review_response)
    rev_sub.add_parser("analytics", help="Show analytics").set_defaults(func=cmd_review_analytics)
    
    alert_p = sub.add_parser("alert", help="Manage alerts")
    alert_p.add_argument("--list", action="store_true"); alert_p.add_argument("--clear", action="store_true")
    alert_p.set_defaults(func=cmd_alert)
    
    tpl_p = sub.add_parser("template", help="Manage templates")
    tpl_p.add_argument("--add", action="store_true"); tpl_p.add_argument("--type"); tpl_p.add_argument("--subject"); tpl_p.add_argument("--body")
    tpl_p.set_defaults(func=cmd_template)
    
    args = parser.parse_args()
    init_data()
    try:
        return args.func(args)
    except Exception as e:
        logger.exception("Error")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
