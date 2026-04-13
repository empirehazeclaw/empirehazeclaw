#!/usr/bin/env python3
"""
Telegram HTML Export Parser
Extrahiert Messages aus Telegram HTML Export

Usage:
  python3 telegram_parser.py <html-file> [output-json]
"""
import re
import sys
import json
from datetime import datetime
from pathlib import Path

def parse_telegram_html(html_path):
    """Parse Telegram HTML export and return list of messages"""
    
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = []
    
    # Pattern für Messages
    message_pattern = re.compile(
        r'<div class="message default clearfix"[^>]*id="message(\d+)"[^>]*>.*?'
        r'<div class="from_name">([^<]+)</div>.*?'
        r'<div class="text">([^<]+(?:</a>)?.*?)</div>.*?'
        r'<div class="pull_right date details"[^>]*title="([^"]+)"',
        re.DOTALL
    )
    
    # Datum Pattern
    date_pattern = re.compile(r'(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2})')
    
    # Service Messages (Dates)
    service_pattern = re.compile(r'<div class="message service"[^>]*>.*?<div class="body details">(\d+ \w+ \d{4})</div>', re.DOTALL)
    
    matches = message_pattern.findall(content)
    
    for msg_id, sender, text, date_str in matches:
        # Parse date
        date_match = date_pattern.search(date_str)
        if date_match:
            day, month, year, hour, minute, second = date_match.groups()
            timestamp = f"{year}-{month}-{day} {hour}:{minute}:{second}"
        else:
            timestamp = date_str
        
        # Clean text
        text = re.sub(r'<[^>]+>', '', text)
        text = text.strip()
        
        messages.append({
            'id': int(msg_id),
            'sender': sender.strip(),
            'text': text,
            'timestamp': timestamp
        })
    
    return messages

def categorize_message(msg):
    """Categorize a message for memory storage"""
    text = msg['text'].lower()
    sender = msg['sender']
    
    # Skip if from Dev_bot (our own messages)
    if 'dev_bot' in sender.lower():
        return None, None
    
    # Keywords for categorization
    decision_keywords = ['entscheidung', 'decision', 'beschlossen', 'beschlossen', 'wird so gemacht', ' approche']
    learning_keywords = ['gelernt', 'learning', ' lesson', 'merke', 'wichtig']
    api_keywords = ['api_key', 'apikey', 'password', 'token', 'secret', 'key:']
    task_keywords = ['todo', 'task', 'machen', 'erledigen', 'offen']
    
    for kw in decision_keywords:
        if kw in text:
            return 'decision', msg
    
    for kw in learning_keywords:
        if kw in text:
            return 'learning', msg
    
    for kw in api_keywords:
        if kw in text:
            return 'api_key', msg
    
    for kw in task_keywords:
        if kw in text:
            return 'task', msg
    
    return None, msg

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 telegram_parser.py <html-file> [output-json]")
        return 1
    
    html_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Parsing: {html_path}")
    messages = parse_telegram_html(html_path)
    
    print(f"Found {len(messages)} messages")
    
    # Categorize
    categorized = {'decision': [], 'learning': [], 'api_key': [], 'task': [], 'other': []}
    
    for msg in messages:
        category, _ = categorize_message(msg)
        if category:
            categorized[category].append(msg)
        else:
            categorized['other'].append(msg)
    
    # Print summary
    print("\n=== CATEGORIZED ===")
    for cat, msgs in categorized.items():
        print(f"{cat}: {len(msgs)}")
    
    # Save to JSON
    result = {
        'source': html_path,
        'parsed_at': datetime.now().isoformat(),
        'total_messages': len(messages),
        'messages': messages,
        'summary': {cat: len(msgs) for cat, msgs in categorized.items()}
    }
    
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nSaved to: {output_path}")
    
    return 0

if __name__ == "__main__":
    exit(main())
