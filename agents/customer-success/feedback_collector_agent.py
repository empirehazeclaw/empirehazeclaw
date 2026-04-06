#!/usr/bin/env python3
"""
Feedback Collector Agent
=========================
Collects, analyzes, and manages customer feedback across multiple channels.
Tracks sentiment, categorizes feedback, and identifies trends.
"""

import argparse
import json
import sys
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import Counter

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FEEDBACK - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "feedback_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/customer-success")
DATA_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_FILE = DATA_DIR / "feedback.json"
SURVEYS_FILE = DATA_DIR / "surveys.json"
RESPONSES_FILE = DATA_DIR / "survey_responses.json"


def load_json(filepath: Path, default: dict = None) -> dict:
    """Load JSON file or return default."""
    if default is None:
        default = {}
    try:
        if filepath.exists():
            return json.loads(filepath.read_text())
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
    return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save data to JSON file."""
    try:
        filepath.write_text(json.dumps(data, indent=2, default=str))
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def init_data_files():
    """Initialize data files if they don't exist."""
    if not FEEDBACK_FILE.exists():
        save_json(FEEDBACK_FILE, {"feedback": []})
    
    if not SURVEYS_FILE.exists():
        save_json(SURVEYS_FILE, {"surveys": []})
    
    if not RESPONSES_FILE.exists():
        save_json(RESPONSES_FILE, {"responses": []})


def analyze_sentiment(text: str) -> str:
    """Simple keyword-based sentiment analysis."""
    text_lower = text.lower()
    
    positive_words = ['great', 'excellent', 'amazing', 'love', 'fantastic', 'awesome', 
                      'wonderful', 'perfect', 'best', 'happy', 'satisfied', 'recommend',
                      'helpful', 'good', 'nice', 'thank', 'thanks', 'impressed']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'poor',
                      'disappointed', 'frustrating', 'annoying', 'useless', 'broken',
                      'slow', 'confusing', 'difficult', 'problem', 'issue', 'bug', 'fail',
                      'waste', 'refund', 'cancel']
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"


def cmd_dashboard(args) -> int:
    """Show feedback dashboard overview."""
    logger.info("Showing feedback dashboard...")
    
    feedback = load_json(FEEDBACK_FILE)
    surveys = load_json(SURVEYS_FILE)
    responses = load_json(RESPONSES_FILE)
    
    all_feedback = feedback.get('feedback', [])
    all_surveys = surveys.get('surveys', [])
    all_responses = responses.get('responses', [])
    
    # Calculate metrics
    total_feedback = len(all_feedback)
    positive = len([f for f in all_feedback if f.get('sentiment') == 'positive'])
    negative = len([f for f in all_feedback if f.get('sentiment') == 'negative'])
    neutral = total_feedback - positive - negative
    
    positive_rate = (positive / total_feedback * 100) if total_feedback > 0 else 0
    
    # Recent feedback
    recent = sorted(all_feedback, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
    
    print("\n" + "="*60)
    print("💬 FEEDBACK COLLECTOR DASHBOARD")
    print("="*60)
    print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("-"*60)
    
    print("\n📊 FEEDBACK OVERVIEW")
    print(f"   Total Feedback: {total_feedback}")
    print(f"   Positive: {positive} ({positive_rate:.1f}%)")
    print(f"   Negative: {negative}")
    print(f"   Neutral: {neutral}")
    
    print("\n📋 SURVEYS")
    print(f"   Total: {len(all_surveys)}")
    active_surveys = len([s for s in all_surveys if s.get('status') == 'active'])
    print(f"   Active: {active_surveys}")
    print(f"   Responses: {len(all_responses)}")
    
    if recent:
        print("\n📅 RECENT FEEDBACK:")
        for fb in recent:
            sentiment_icon = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(
                fb.get('sentiment', 'neutral'), "❓")
            print(f"   {sentiment_icon} {fb.get('message', '')[:50]}...")
    
    print("\n" + "="*60)
    return 0


def cmd_submit_feedback(args) -> int:
    """Submit new feedback."""
    logger.info(f"Submitting feedback from {args.source}")
    
    feedback = load_json(FEEDBACK_FILE)
    
    # Analyze sentiment
    sentiment = analyze_sentiment(args.message)
    
    fb_entry = {
        "id": str(uuid.uuid4())[:8],
        "message": args.message,
        "source": args.source or "direct",
        "category": args.category or "general",
        "sentiment": sentiment,
        "rating": int(args.rating) if args.rating else None,
        "customer_email": args.email,
        "status": "new",
        "created_at": datetime.now().isoformat(),
        "tags": args.tags.split(',') if args.tags else []
    }
    
    feedback['feedback'].append(fb_entry)
    save_json(FEEDBACK_FILE, feedback)
    
    print(f"✅ Feedback submitted!")
    print(f"   ID: {fb_entry['id']}")
    print(f"   Sentiment: {sentiment}")
    return 0


def cmd_list_feedback(args) -> int:
    """List feedback with filters."""
    logger.info("Listing feedback...")
    
    feedback = load_json(FEEDBACK_FILE)
    all_feedback = feedback.get('feedback', [])
    
    # Apply filters
    if args.sentiment:
        all_feedback = [f for f in all_feedback if f.get('sentiment') == args.sentiment]
    if args.category:
        all_feedback = [f for f in all_feedback if f.get('category') == args.category]
    if args.source:
        all_feedback = [f for f in all_feedback if f.get('source') == args.source]
    if args.status:
        all_feedback = [f for f in all_feedback if f.get('status') == args.status]
    
    if not all_feedback:
        print("No feedback found matching criteria.")
        return 0
    
    print(f"\n💬 Feedback ({len(all_feedback)} items):")
    print("-"*70)
    for fb in sorted(all_feedback, key=lambda x: x.get('created_at', ''), reverse=True):
        sentiment_icon = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(
            fb.get('sentiment', 'neutral'), "❓")
        rating = f"⭐{fb.get('rating')}" if fb.get('rating') else ""
        print(f"   {sentiment_icon} [{fb.get('sentiment', '?')}] {rating} {fb.get('message', '')[:60]}")
        print(f"       Source: {fb.get('source', '?')} | Category: {fb.get('category', '?')} | {fb.get('created_at', '')[:10]}")
    
    return 0


def cmd_create_survey(args) -> int:
    """Create a new survey."""
    logger.info(f"Creating survey: {args.name}")
    
    surveys = load_json(SURVEYS_FILE)
    
    # Parse questions
    questions = []
    if args.questions:
        for i, q in enumerate(args.questions.split(';'), 1):
            parts = q.split('|')
            questions.append({
                "id": i,
                "text": parts[0].strip(),
                "type": parts[1].strip() if len(parts) > 1 else "rating"
            })
    
    survey = {
        "id": str(uuid.uuid4())[:8],
        "name": args.name,
        "description": args.description or "",
        "questions": questions,
        "status": "draft",
        "target": args.target or "all",
        "created_at": datetime.now().isoformat(),
        "closes_at": args.closes_at
    }
    
    surveys['surveys'].append(survey)
    save_json(SURVEYS_FILE, surveys)
    
    print(f"✅ Survey created: {args.name} (ID: {survey['id']})")
    return 0


def cmd_list_surveys(args) -> int:
    """List all surveys."""
    logger.info("Listing surveys...")
    
    surveys = load_json(SURVEYS_FILE)
    all_surveys = surveys.get('surveys', [])
    
    if args.status:
        all_surveys = [s for s in all_surveys if s.get('status') == args.status]
    
    if not all_surveys:
        print("No surveys found.")
        return 0
    
    print(f"\n📋 Surveys ({len(all_surveys)}):")
    print("-"*70)
    for survey in sorted(all_surveys, key=lambda x: x.get('created_at', ''), reverse=True):
        status_icon = {"draft": "📝", "active": "🚀", "closed": "🔒"}.get(
            survey.get('status', 'draft'), "❓")
        print(f"   {status_icon} {survey.get('name', 'Untitled')} (ID: {survey.get('id', '?')})")
        print(f"       Questions: {len(survey.get('questions', []))} | Status: {survey.get('status', '?')}")
    
    return 0


def cmd_activate_survey(args) -> int:
    """Activate a survey."""
    logger.info(f"Activating survey: {args.survey_id}")
    
    surveys = load_json(SURVEYS_FILE)
    
    for survey in surveys.get('surveys', []):
        if survey.get('id') == args.survey_id:
            survey['status'] = 'active'
            survey['activated_at'] = datetime.now().isoformat()
            save_json(SURVEYS_FILE, surveys)
            print(f"✅ Survey activated!")
            return 0
    
    print(f"❌ Survey {args.survey_id} not found.")
    return 1


def cmd_submit_response(args) -> int:
    """Submit a survey response."""
    logger.info(f"Submitting survey response for survey: {args.survey_id}")
    
    surveys = load_json(SURVEYS_FILE)
    responses = load_json(RESPONSES_FILE)
    
    # Verify survey exists
    survey = None
    for s in surveys.get('surveys', []):
        if s.get('id') == args.survey_id:
            survey = s
            break
    
    if not survey:
        print(f"❌ Survey {args.survey_id} not found.")
        return 1
    
    if survey.get('status') != 'active':
        print(f"⚠️  Survey is not active (status: {survey.get('status')})")
        return 1
    
    # Parse answers
    answers = []
    if args.answers:
        for ans in args.answers.split(';'):
            answers.append(ans.strip())
    
    response = {
        "id": str(uuid.uuid4())[:8],
        "survey_id": args.survey_id,
        "respondent_email": args.email,
        "answers": answers,
        "submitted_at": datetime.now().isoformat()
    }
    
    responses['responses'].append(response)
    save_json(RESPONSES_FILE, responses)
    
    print(f"✅ Response submitted for survey {args.survey_id}!")
    return 0


def cmd_analyze(args) -> int:
    """Analyze feedback and generate insights."""
    logger.info("Analyzing feedback...")
    
    feedback = load_json(FEEDBACK_FILE)
    all_feedback = feedback.get('feedback', [])
    
    if not all_feedback:
        print("No feedback to analyze.")
        return 0
    
    # Sentiment distribution
    sentiments = Counter(f.get('sentiment', 'neutral') for f in all_feedback)
    
    # Category distribution
    categories = Counter(f.get('category', 'general') for f in all_feedback)
    
    # Source distribution
    sources = Counter(f.get('source', 'unknown') for f in all_feedback)
    
    # Rating stats (if ratings exist)
    ratings = [f.get('rating', 0) for f in all_feedback if f.get('rating')]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Category-sentiment breakdown
    cat_sentiment = {}
    for f in all_feedback:
        cat = f.get('category', 'general')
        sent = f.get('sentiment', 'neutral')
        if cat not in cat_sentiment:
            cat_sentiment[cat] = {'positive': 0, 'negative': 0, 'neutral': 0}
        cat_sentiment[cat][sent] += 1
    
    print("\n" + "="*60)
    print("📊 FEEDBACK ANALYSIS")
    print("="*60)
    print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total Feedback: {len(all_feedback)}")
    print("-"*60)
    
    print("\n😊 SENTIMENT DISTRIBUTION")
    total = sum(sentiments.values())
    for sent, count in sentiments.most_common():
        pct = (count / total * 100) if total > 0 else 0
        bar = "█" * int(pct / 5)
        print(f"   {sent.capitalize():<10} {count:>4} ({pct:>5.1f}%) {bar}")
    
    print("\n📂 CATEGORY BREAKDOWN")
    for cat, count in categories.most_common():
        pct = (count / len(all_feedback) * 100)
        print(f"   {cat:<15} {count:>4} ({pct:>5.1f}%)")
    
    print("\n📡 SOURCE BREAKDOWN")
    for src, count in sources.most_common():
        pct = (count / len(all_feedback) * 100)
        print(f"   {src:<15} {count:>4} ({pct:>5.1f}%)")
    
    if ratings:
        print(f"\n⭐ AVERAGE RATING: {avg_rating:.2f}/5 ({len(ratings)} ratings)")
    
    print("\n📊 CATEGORY-SENTIMENT MATRIX")
    for cat, sent_counts in cat_sentiment.items():
        total_cat = sum(sent_counts.values())
        pos_pct = sent_counts['positive'] / total_cat * 100 if total_cat > 0 else 0
        neg_pct = sent_counts['negative'] / total_cat * 100 if total_cat > 0 else 0
        print(f"   {cat:<15} Positive: {pos_pct:>5.1f}% | Negative: {neg_pct:>5.1f}%")
    
    print("\n" + "="*60)
    return 0


def cmd_trends(args) -> int:
    """Show feedback trends over time."""
    logger.info("Analyzing feedback trends...")
    
    feedback = load_json(FEEDBACK_FILE)
    all_feedback = feedback.get('feedback', [])
    
    if not all_feedback:
        print("No feedback to analyze.")
        return 0
    
    # Group by date
    days = int(args.days) if args.days else 30
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_feedback = [f for f in all_feedback 
                       if datetime.fromisoformat(f.get('created_at', '2020-01-01')) > cutoff]
    
    if not recent_feedback:
        print(f"No feedback in the last {days} days.")
        return 0
    
    # Calculate daily stats
    daily_stats = {}
    for f in recent_feedback:
        date = f.get('created_at', '')[:10]
        if date not in daily_stats:
            daily_stats[date] = {'total': 0, 'positive': 0, 'negative': 0, 'neutral': 0}
        daily_stats[date]['total'] += 1
        daily_stats[date][f.get('sentiment', 'neutral')] += 1
    
    print(f"\n📈 Feedback Trends (Last {days} days)")
    print("-"*60)
    print(f"{'Date':<12} {'Total':>6} {'Positive':>9} {'Negative':>9} {'Neutral':>8}")
    print("-"*60)
    
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        print(f"{date:<12} {stats['total']:>6} {stats['positive']:>9} {stats['negative']:>9} {stats['neutral']:>8}")
    
    # Calculate trends
    dates = sorted(daily_stats.keys())
    if len(dates) >= 2:
        first_week = [daily_stats[d]['total'] for d in dates[:7] if d in daily_stats]
        last_week = [daily_stats[d]['total'] for d in dates[-7:] if d in daily_stats]
        
        avg_first = sum(first_week) / len(first_week) if first_week else 0
        avg_last = sum(last_week) / len(last_week) if last_week else 0
        
        change = ((avg_last - avg_first) / avg_first * 100) if avg_first > 0 else 0
        
        print(f"\n📊 TREND:")
        if change > 0:
            print(f"   Feedback volume is INCREASING (+{change:.1f}% week-over-week)")
        elif change < 0:
            print(f"   Feedback volume is DECREASING ({change:.1f}% week-over-week)")
        else:
            print(f"   Feedback volume is STABLE")
    
    print("\n" + "="*60)
    return 0


def cmd_export(args) -> int:
    """Export feedback data."""
    logger.info("Exporting feedback...")
    
    feedback = load_json(FEEDBACK_FILE)
    all_feedback = feedback.get('feedback', [])
    
    # Filter if specified
    if args.sentiment:
        all_feedback = [f for f in all_feedback if f.get('sentiment') == args.sentiment]
    if args.category:
        all_feedback = [f for f in all_feedback if f.get('category') == args.category]
    
    output_file = Path(args.output) if args.output else DATA_DIR / f"feedback_export_{datetime.now().strftime('%Y%m%d')}.json"
    
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "count": len(all_feedback),
        "feedback": all_feedback
    }
    
    save_json(Path(output_file), export_data)
    
    print(f"✅ Exported {len(all_feedback)} feedback entries to {output_file}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="💬 Feedback Collector Agent - Customer Feedback Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s dashboard                    Show feedback dashboard
  %(prog)s submit --message "Great service!" --source website --rating 5
  %(prog)s list-feedback --sentiment negative --category support
  %(prog)s create-survey --name "Q1 NPS" --questions "How satisfied are you?|rating;Any comments?|text"
  %(prog)s list-surveys --status active
  %(prog)s activate-survey --survey-id abc123
  %(prog)s submit-response --survey-id abc123 --email user@example.com --answers "5;Great product"
  %(prog)s analyze                      Generate feedback analysis
  %(prog)s trends --days 30             Show feedback trends
  %(prog)s export --output feedback.json
        """
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Dashboard
    subparsers.add_parser('dashboard', help='Show feedback dashboard')
    
    # Feedback commands
    fb_parser = subparsers.add_parser('submit', help='Submit new feedback')
    fb_parser.add_argument('--message', required=True, help='Feedback message')
    fb_parser.add_argument('--source', help='Source (website, email, app, etc.)')
    fb_parser.add_argument('--category', help='Category (product, service, support, etc.)')
    fb_parser.add_argument('--rating', help='Rating 1-5')
    fb_parser.add_argument('--email', help='Customer email')
    fb_parser.add_argument('--tags', help='Comma-separated tags')
    
    list_fb_parser = subparsers.add_parser('list-feedback', help='List feedback')
    list_fb_parser.add_argument('--sentiment', choices=['positive', 'negative', 'neutral'])
    list_fb_parser.add_argument('--category', help='Filter by category')
    list_fb_parser.add_argument('--source', help='Filter by source')
    list_fb_parser.add_argument('--status', help='Filter by status')
    
    # Survey commands
    survey_parser = subparsers.add_parser('create-survey', help='Create a new survey')
    survey_parser.add_argument('--name', required=True, help='Survey name')
    survey_parser.add_argument('--description', help='Description')
    survey_parser.add_argument('--questions', help='Questions separated by semicolons (text|type)')
    survey_parser.add_argument('--target', help='Target audience')
    survey_parser.add_argument('--closes-at', help='Close date (YYYY-MM-DD)')
    
    list_survey_parser = subparsers.add_parser('list-surveys', help='List surveys')
    list_survey_parser.add_argument('--status', choices=['draft', 'active', 'closed'])
    
    act_parser = subparsers.add_parser('activate-survey', help='Activate a survey')
    act_parser.add_argument('--survey-id', required=True, help='Survey ID')
    
    resp_parser = subparsers.add_parser('submit-response', help='Submit survey response')
    resp_parser.add_argument('--survey-id', required=True, help='Survey ID')
    resp_parser.add_argument('--email', required=True, help='Respondent email')
    resp_parser.add_argument('--answers', required=True, help='Answers separated by semicolons')
    
    # Analysis commands
    subparsers.add_parser('analyze', help='Generate feedback analysis')
    
    trends_parser = subparsers.add_parser('trends', help='Show feedback trends')
    trends_parser.add_argument('--days', help='Number of days to analyze')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export feedback data')
    export_parser.add_argument('--output', help='Output file path')
    export_parser.add_argument('--sentiment', choices=['positive', 'negative', 'neutral'])
    export_parser.add_argument('--category', help='Filter by category')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize data files
    init_data_files()
    
    # Route to command handler
    commands = {
        'dashboard': cmd_dashboard,
        'submit': cmd_submit_feedback,
        'list-feedback': cmd_list_feedback,
        'create-survey': cmd_create_survey,
        'list-surveys': cmd_list_surveys,
        'activate-survey': cmd_activate_survey,
        'submit-response': cmd_submit_response,
        'analyze': cmd_analyze,
        'trends': cmd_trends,
        'export': cmd_export
    }
    
    try:
        return commands[args.command](args)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
