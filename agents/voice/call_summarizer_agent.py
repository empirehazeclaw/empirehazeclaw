#!/usr/bin/env python3
"""
Call Summarizer Agent
====================
Summarize call transcripts, extract key points, action items, and sentiment.

Usage:
    python3 call_summarizer_agent.py --summarize --transcript-id <id>
    python3 call_summarizer_agent.py --text "Call text here..."
    python3 call_summarizer_agent.py --file transcript.txt
    python3 call_summarizer_agent.py --list
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Setup logging
LOG_DIR = Path("/home/clawbot/.openclaw/workspace/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "call_summarizer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Data paths
DATA_DIR = Path("/home/clawbot/.openclaw/workspace/data/agents/voice")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SUMMARIES_FILE = DATA_DIR / "call_summaries.json"
TRANSCRIPTS_FILE = DATA_DIR / "transcripts.json"


def load_json(filepath: Path, default: dict = {}) -> dict:
    """Load JSON data from file."""
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        return default


def save_json(filepath: Path, data: dict) -> bool:
    """Save JSON data to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving {filepath}: {e}")
        return False


def extract_action_items(text: str) -> List[Dict]:
    """Extract action items from call text using keyword patterns."""
    action_items = []
    
    # Patterns for action items
    patterns = [
        r"(?:TODO|TODO:|Action:|Action Item:)\s*(.+?)(?:\n|$)",
        r"(?:Will|Velvet|Will do)\s+(?:need to|must|should|going to)\s+(.+?)(?:\n|$)",
        r"(?:I'll|I will)\s+(.+?)(?:\n|$)",
        r"(?:Please|Send|Könnten Sie|Bitte)\s+(?:you\s+)?(.+?)(?:\n|$)",
        r"(?:Schedule|Book|Booken|Plan)\s+(?:a|an|some)\s+(.+?)(?:\n|$)",
        r"(?:Follow up|Follow-up|Nachverfolgen)\s+(?:on|with)?\s*(.+?)(?:\n|$)",
        r"(?:Review|Überprüfen)\s+(?:the\s+)?(.+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            item_text = match.group(1).strip()
            if item_text and len(item_text) > 3:
                action_items.append({
                    "text": item_text,
                    "pattern_matched": pattern[:30],
                    "extracted_at": datetime.now().isoformat()
                })
    
    # Deduplicate
    seen = set()
    unique_items = []
    for item in action_items:
        if item["text"] not in seen:
            seen.add(item["text"])
            unique_items.append(item)
    
    return unique_items[:10]  # Limit to 10 items


def extract_decision_points(text: str) -> List[str]:
    """Extract decision points from call text."""
    decisions = []
    
    patterns = [
        r"(?:Decision:|Entscheidung:|We decided:|Wir haben entschieden:)\s*(.+?)(?:\n|$)",
        r"(?:Agreed|Agreement|Einigung):\s*(.+?)(?:\n|$)",
        r"(?:Will proceed|Machen wir|Let's go with):\s*(.+?)(?:\n|$)",
        r"(?:Final|Finally|Endlich):\s*(.+?)(?:\n|$)",
        r"(?:Confirmed|Bestätigt):\s*(.+?)(?:\n|$)",
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            decision = match.group(1).strip()
            if decision and len(decision) > 3:
                decisions.append(decision)
    
    return list(set(decisions))[:5]


def extract_key_topics(text: str) -> List[str]:
    """Extract key topics from call text."""
    # Common business topics to look for
    topic_keywords = {
        "Pricing": ["price", "pricing", "kosten", "preis", "cost", "quote", "offer"],
        "Timeline": ["deadline", "timeline", "schedule", "when", "date", "timeline", "fertig"],
        "Technical": ["technical", "technical issue", "bug", "feature", "integration", "api"],
        "Support": ["support", "help", "assistance", "problem", "issue", "support"],
        "Contract": ["contract", "agreement", "legal", "terms", "vertrag", "rechtlich"],
        "Meeting": ["meeting", "call", "discussion", "besprechung", "anruf"],
        "Deliverable": ["deliverable", "deliver", "交付", "output", "result"],
        "Quality": ["quality", "standard", "excellence", "qualität"],
    }
    
    text_lower = text.lower()
    found_topics = []
    
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if topic not in found_topics:
                    found_topics.append(topic)
                break
    
    return found_topics


def analyze_sentiment(text: str) -> Dict:
    """Simple keyword-based sentiment analysis."""
    positive_words = [
        "good", "great", "excellent", "amazing", "wonderful", "fantastic", "perfect",
        "happy", "pleased", "satisfied", "excited", "love", "like", "appreciate",
        "gute", "super", "wunderbar", "toll", "zufrieden", "gerne"
    ]
    negative_words = [
        "bad", "poor", "terrible", "awful", "horrible", "disappointed", "frustrated",
        "upset", "angry", "annoyed", "hate", "problem", "issue", "wrong",
        "schlecht", "probleme", "enttäuscht", "frustriert", "schade"
    ]
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    total = positive_count + negative_count
    
    if total == 0:
        return {"sentiment": "neutral", "score": 50, "positive": 0, "negative": 0}
    
    score = (positive_count / total) * 100
    
    if score >= 70:
        sentiment = "positive"
    elif score <= 30:
        sentiment = "negative"
    else:
        sentiment = "mixed"
    
    return {
        "sentiment": sentiment,
        "score": round(score, 1),
        "positive": positive_count,
        "negative": negative_count
    }


def detect_speaker_changes(text: str) -> List[Dict]:
    """Detect speaker changes in transcript."""
    # Common patterns indicating speaker changes
    patterns = [
        r"(?:Speaker\s*\d*:|S\d+:|Person\s*\d*:)",
        r"(?:Agent:|Customer:|Kunde:|Agent:)",
        r"(?:Caller:|Callee:|Anrufer:)",
    ]
    
    segments = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            segments.append({
                "position": match.start(),
                "speaker_label": match.group(0).strip()
            })
    
    return sorted(segments, key=lambda x: x["position"])[:20]


def summarize_call(text: str, source: str = "direct_input", 
                   participants: Optional[List[str]] = None) -> Dict:
    """Generate a comprehensive call summary."""
    
    # Basic stats
    word_count = len(text.split())
    char_count = len(text)
    
    # Extract components
    action_items = extract_action_items(text)
    decisions = extract_decision_points(text)
    topics = extract_key_topics(text)
    sentiment = analyze_sentiment(text)
    
    # Generate summary (simple extractive)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
    
    # Take first 3 sentences as summary
    summary_sentences = sentences[:3] if sentences else ["No clear summary available."]
    summary = ". ".join(summary_sentences)
    
    # If summary is too short, use more sentences
    if len(summary) < 100 and len(sentences) > 3:
        summary_sentences = sentences[:5]
        summary = ". ".join(summary_sentences)
    
    summary_obj = {
        "id": f"SUM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "source": source,
        "created_at": datetime.now().isoformat(),
        "stats": {
            "word_count": word_count,
            "char_count": char_count,
            "duration_estimate_minutes": round(word_count / 150, 1)  # ~150 words/minute speaking
        },
        "summary": summary,
        "sentiment": sentiment,
        "topics": topics,
        "action_items": action_items,
        "decisions": decisions,
        "participants": participants or ["Unknown"]
    }
    
    return summary_obj


def save_summary(summary: Dict) -> bool:
    """Save summary to file."""
    summaries = load_json(SUMMARIES_FILE)
    
    if "summaries" not in summaries:
        summaries["summaries"] = []
    
    summaries["summaries"].append(summary)
    summaries["last_updated"] = datetime.now().isoformat()
    
    return save_json(SUMMARIES_FILE, summaries)


def get_summaries(limit: Optional[int] = None) -> List[Dict]:
    """Get all summaries."""
    summaries = load_json(SUMMARIES_FILE)
    result = summaries.get("summaries", [])
    
    if limit:
        result = result[-limit:]
    
    return result


def get_summary_by_id(summary_id: str) -> Optional[Dict]:
    """Get a specific summary by ID."""
    summaries = load_json(SUMMARIES_FILE)
    
    for s in summaries.get("summaries", []):
        if s["id"] == summary_id:
            return s
    
    return None


def display_summary(summary: Dict):
    """Display a summary nicely."""
    sentiment_emoji = {
        "positive": "😊",
        "negative": "😞",
        "neutral": "😐",
        "mixed": "😐"
    }
    emoji = sentiment_emoji.get(summary["sentiment"]["sentiment"], "😐")
    
    print("\n" + "=" * 70)
    print(f"📋 CALL SUMMARY: {summary['id']}")
    print("=" * 70)
    
    print(f"\n📊 STATS:")
    print(f"  Source: {summary['source']}")
    print(f"  Words: {summary['stats']['word_count']}")
    print(f"  Est. Duration: {summary['stats']['duration_estimate_minutes']} minutes")
    print(f"  Participants: {', '.join(summary['participants'])}")
    
    print(f"\n{emoji} SENTIMENT: {summary['sentiment']['sentiment'].upper()}")
    print(f"  Score: {summary['sentiment']['score']}/100 (Pos: {summary['sentiment']['positive']}, Neg: {summary['sentiment']['negative']})")
    
    print(f"\n📌 TOPICS:")
    if summary["topics"]:
        for topic in summary["topics"]:
            print(f"   • {topic}")
    else:
        print("   • No specific topics detected")
    
    print(f"\n📝 SUMMARY:")
    print("-" * 70)
    print(f"   {summary['summary']}")
    print("-" * 70)
    
    if summary.get("action_items"):
        print(f"\n✅ ACTION ITEMS ({len(summary['action_items'])}):")
        for i, item in enumerate(summary["action_items"], 1):
            print(f"   {i}. {item['text']}")
    
    if summary.get("decisions"):
        print(f"\n✅ DECISIONS ({len(summary['decisions'])}):")
        for i, decision in enumerate(summary["decisions"], 1):
            print(f"   {i}. {decision}")
    
    print("\n" + "=" * 70)
    print(f"Created: {summary['created_at'][:19].replace('T', ' ')}")


def main():
    parser = argparse.ArgumentParser(
        description="Call Summarizer Agent - Summarize call transcripts with key points and action items",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --text "This is a call about the new project..."
  %(prog)s --file ./call_transcript.txt
  %(prog)s --list
  %(prog)s --list --latest 5
  %(prog)s --view SUM-20240115103045
        """
    )
    
    parser.add_argument("--text", type=str, help="Call transcript text to summarize")
    parser.add_argument("--file", type=str, help="File containing transcript text")
    parser.add_argument("--source", type=str, default="direct_input", help="Source identifier")
    parser.add_argument("--participants", type=str, nargs="+", help="Participant names")
    parser.add_argument("--summarize", action="store_true", help="Summarize a transcript by ID")
    parser.add_argument("--transcript-id", type=str, help="Transcript ID from voice_transcriber")
    parser.add_argument("--list", action="store_true", help="List all summaries")
    parser.add_argument("--latest", type=int, help="Show latest N summaries")
    parser.add_argument("--view", type=str, help="View a specific summary by ID")
    
    args = parser.parse_args()
    
    try:
        if args.text:
            summary = summarize_call(args.text, args.source, args.participants)
            save_summary(summary)
            print(f"\n✅ Summary created: {summary['id']}")
            display_summary(summary)
            return
        
        if args.file:
            if not os.path.exists(args.file):
                print(f"❌ File not found: {args.file}")
                sys.exit(1)
            
            with open(args.file, 'r') as f:
                text = f.read()
            
            summary = summarize_call(text, args.file, args.participants)
            save_summary(summary)
            print(f"\n✅ Summary created: {summary['id']}")
            display_summary(summary)
            return
        
        if args.summarize:
            if not args.transcript_id:
                parser.error("--summarize requires --transcript-id")
            
            transcripts = load_json(TRANSCRIPTS_FILE)
            transcript = None
            
            for t in transcripts.get("transcripts", []):
                if t["id"] == args.transcript_id:
                    transcript = t
                    break
            
            if not transcript:
                print(f"\n❌ Transcript not found: {args.transcript_id}")
                sys.exit(1)
            
            summary = summarize_call(
                transcript["text"],
                f"transcript:{args.transcript_id}",
                args.participants
            )
            save_summary(summary)
            print(f"\n✅ Summary created: {summary['id']}")
            display_summary(summary)
            return
        
        if args.list:
            summaries = get_summaries(limit=args.latest)
            if not summaries:
                print("\nNo summaries found.")
                return
            
            print(f"\n📋 CALL SUMMARIES (showing {len(summaries)}):")
            print("-" * 70)
            for s in summaries:
                sentiment = s["sentiment"]["sentiment"].upper()
                topics = ", ".join(s["topics"][:2]) if s["topics"] else "None"
                print(f"  {s['id']} | {s['source'][:30]} | {sentiment:8} | {topics}")
            print("-" * 70)
            return
        
        if args.view:
            summary = get_summary_by_id(args.view)
            if summary:
                display_summary(summary)
            else:
                print(f"\n❌ Summary not found: {args.view}")
                sys.exit(1)
            return
        
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
