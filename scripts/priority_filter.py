#!/usr/bin/env python3
"""
AI Priority Filter - Find the Most Important Items
Scoring based on: Business Impact, System Stability, Nico's Goals
"""

import re
import json
from datetime import datetime

# Priority criteria weights
CRITERIA = {
    'strategic_business': 2.0,      # Affects revenue/customers
    'personal_preference': 1.5,      # Nico's decisions/preferences
    'system_critical': 2.0,          # Critical fixes
    'turning_point': 1.8,            # Development milestones
    'revenue_impact': 2.0,           # Direct revenue impact
}

def score_item(text, category):
    """Score an item based on keyword analysis"""
    score = 5  # Base score
    
    # High impact keywords
    high_impact = [
        'revenue', 'kunde', 'customer', 'sale', 'verkauf', 'euro', '€',
        'critical', 'bug', 'fix', 'problem', 'crash', 'error',
        'entscheidung', 'decision', 'beschlossen', 'approval',
        'money', 'payment', 'stripe', 'checkout',
        'first', 'erste', 'kunden gewinnen',
        'security', 'hack', 'breach', 'token',
    ]
    
    # Medium impact keywords
    medium_impact = [
        'learning', 'learned', 'gelernt', 'erkenntnis',
        'verbessert', 'improved', 'optimized', 'optimiert',
        'automated', 'automatisiert', 'funktioniert',
        'implemented', 'implementiert', 'erstellt',
        'tested', 'getestet', 'funktioniert',
    ]
    
    # Low priority keywords
    low_priority = [
        'demo', 'test', 'testing', 'experiment',
        'maybe', 'perhaps', 'vielleicht', 'maybe',
        'duplicate', 'copied', 'same as',
    ]
    
    text_lower = text.lower()
    
    # Add score for high impact
    for keyword in high_impact:
        if keyword in text_lower:
            score += 1.5
    
    # Add score for medium impact
    for keyword in medium_impact:
        if keyword in text_lower:
            score += 0.5
    
    # Reduce score for low priority
    for keyword in low_priority:
        if keyword in text_lower:
            score -= 0.5
    
    # Cap at 1-10
    return max(1, min(10, score))

def extract_key_info(text):
    """Extract key information from text"""
    # Extract dates
    date_pattern = r'\[(\d{2}\.\d{2}\.\d{4})\]'
    dates = re.findall(date_pattern, text)
    
    # Extract sender
    sender_pattern = r'\[(Nico|Dev_bot|[A-Za-z_]+)\]'
    senders = re.findall(sender_pattern, text)
    sender = senders[0] if senders else 'Unknown'
    
    # Extract content (remove metadata)
    content = re.sub(r'\[Learning \[.*?\]\s*', '', text)
    content = re.sub(r'\[Decision \[.*?\]\s*', '', content)
    content = re.sub(r'\[.*?\]\s*', '', content)
    content = content.strip()
    
    return {
        'dates': dates,
        'sender': sender,
        'content': content[:500] if len(content) > 500 else content
    }

def main():
    # Load learnings
    try:
        with open('/home/clawbot/.openclaw/workspace/memory/learnings/2026-04-05-telegram-learnings.md', 'r') as f:
            learnings_raw = f.read()
    except:
        learnings_raw = ""
    
    try:
        with open('/home/clawbot/.openclaw/workspace/memory/decisions/2026-04-05-telegram-decisions.md', 'r') as f:
            decisions_raw = f.read()
    except:
        decisions_raw = ""
    
    # Parse learnings
    learnings = []
    learning_blocks = re.split(r'## Learning \[', learnings_raw)
    
    for block in learning_blocks[1:]:
        try:
            parts = block.split(']', 1)
            if len(parts) == 2:
                time = parts[0].strip()
                content = parts[1].strip()
                
                info = extract_key_info(content)
                score = score_item(content, 'learning')
                
                learnings.append({
                    'time': time,
                    'sender': info['sender'],
                    'content': info['content'],
                    'score': score,
                    'dates': info['dates']
                })
        except Exception as e:
            continue
    
    # Parse decisions
    decisions = []
    decision_blocks = re.split(r'## Decision \[', decisions_raw)
    
    for block in decision_blocks[1:]:
        try:
            parts = block.split(']', 1)
            if len(parts) == 2:
                time = parts[0].strip()
                content = parts[1].strip()
                
                info = extract_key_info(content)
                score = score_item(content, 'decision')
                
                decisions.append({
                    'time': time,
                    'sender': info['sender'],
                    'content': info['content'],
                    'score': score,
                    'dates': info['dates']
                })
        except Exception as e:
            continue
    
    # Sort by score
    learnings_sorted = sorted(learnings, key=lambda x: x['score'], reverse=True)
    decisions_sorted = sorted(decisions, key=lambda x: x['score'], reverse=True)
    
    # Remove duplicates (similar content)
    seen_content = set()
    unique_learnings = []
    for l in learnings_sorted:
        content_key = l['content'][:100].lower()
        if content_key not in seen_content:
            seen_content.add(content_key)
            unique_learnings.append(l)
    
    seen_content = set()
    unique_decisions = []
    for d in decisions_sorted:
        content_key = d['content'][:100].lower()
        if content_key not in seen_content:
            seen_content.add(content_key)
            unique_decisions.append(d)
    
    # Get top items
    top_decisions = unique_decisions[:20]
    top_learnings = unique_learnings[:20]
    
    return top_decisions, top_learnings

if __name__ == '__main__':
    decisions, learnings = main()
    print(f"Found {len(decisions)} high-priority decisions")
    print(f"Found {len(learnings)} high-priority learnings")
