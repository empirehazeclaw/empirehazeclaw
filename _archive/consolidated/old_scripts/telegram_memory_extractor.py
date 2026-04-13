#!/usr/bin/env python3
"""
📥 Telegram Chat History Extractor & Memory Integrator v2
=======================================================
Extrahiert relevante Informationen aus Telegram Chat Exports
und integriert sie ins EmpireHazeClaw Memory System.

Usage:
    python3 scripts/telegram_memory_extractor.py <html_file> [--dry-run]
"""

import re
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Config
WORKSPACE = "/home/clawbot/.openclaw/workspace"
MEMORY_DIR = f"{WORKSPACE}/memory"
DECISIONS_DIR = f"{MEMORY_DIR}/decisions"
LEARNINGS_DIR = f"{MEMORY_DIR}/learnings"
TODOS_FILE = f"{WORKSPACE}/todos/current.md"
MEMORY_FILE = f"{WORKSPACE}/MEMORY.md"

# Categories
CATEGORY_DECISION = "DECISION"
CATEGORY_LEARNING = "LEARNING"
CATEGORY_FACT = "FACT"
CATEGORY_TASK = "TASK"
CATEGORY_CODE = "CODE"
CATEGORY_SYSTEM = "SYSTEM"
CATEGORY_DISCARD = "DISCARD"

def parse_telegram_html(filepath: str) -> List[Dict]:
    """Parse Telegram HTML export and extract messages."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    messages = []
    
    # Split by message containers
    blocks = re.split(r'<div class="message service"', content)
    
    for block in blocks:
        # Extract date
        date_match = re.search(r'<div class="pull_right date details" title="([^"]+)">', block)
        if not date_match:
            continue
        date_str = date_match.group(1).split(' ')[0]  # Get just date part
        
        # Extract sender
        sender_match = re.search(r'<div class="from_name">\s*([^<]+)\s*</div>', block)
        sender = sender_match.group(1).strip() if sender_match else "Unknown"
        
        # Extract text (multiple text divs possible)
        texts = re.findall(r'<div class="text">(.+?)</div>', block, re.DOTALL)
        
        for text in texts:
            # Clean HTML
            clean = re.sub(r'<[^>]+>', ' ', text).strip()
            clean = re.sub(r'\s+', ' ', clean).strip()
            if clean and len(clean) > 5:
                messages.append({
                    'date': date_str,
                    'sender': sender,
                    'text': clean
                })
    
    return messages

def categorize_message(msg: Dict) -> Tuple[str, str]:
    """Categorize a message and return (category, summary)."""
    text = msg['text']
    text_lower = text.lower()
    sender = msg['sender']
    
    # === DECISION: Only if it's a clear directive or commitment ===
    # "wir machen", "ich will", "starten wir", "stoppen", "deaktivieren"
    # Must be from Nico or explicit Dev_bot acceptance
    decision_patterns = [
        r'\bwir (machen|starten|stoppen|deaktivieren|aktivieren)\b',
        r'\bich (will|möchte|lasse)\b',
        r'\blaust uns\b',
        r'\b(ok|okay|ja) (wir|machen|starten)\b',
        r'\bEntscheidung:\s*\w+',
        r'\bSTOPPEN\b',
        r'\bSTARTEN\b',
        r'\bdeaktiviere\b',
        r'\baktiviere\b',
        r'\bentferne\b',
        r'\breboot\b',
        r'\bzurücksetzen\b',
        r'\bspeichere\b',
        r'\baktualisiere\b',
    ]
    
    for pattern in decision_patterns:
        if re.search(pattern, text_lower):
            # Must have significant content
            if len(text) > 15:
                return CATEGORY_DECISION, f"[{msg['date']}] [{sender}] {text[:300]}"
    
    # === LEARNING: Something that was figured out or discovered ===
    learning_patterns = [
        r'funk.t|funktioniert\b.*jetzt',
        r'behoben|gelöst|gef..?ixt',
        r'\bgelernt\b',
        r'\bproblem\s+war\b',
        r'\bneuer\s+ansatz\b',
        r'\bverbessert\b',
        r'\bjetzt\s+l..uft\b',
        r'warum.*weil',
        r'\bfehler.*behoben\b',
        r'\bder\s+fix\b',
        r'\bworkaround\b',
        r'\bdas\s+war\b',
    ]
    
    for pattern in learning_patterns:
        if re.search(pattern, text_lower):
            if len(text) > 20:
                return CATEGORY_LEARNING, f"[{msg['date']}] [{sender}] {text[:300]}"
    
    # === FACT: Technical info, API keys, links, configs ===
    fact_patterns = [
        r'api[_-]?key',
        r'token\s*=',
        r'password',
        r'https?://[^\s]+',
        r'\b(ip|port|server|domain):\s*\w',
        r'\bconfig\b',
        r'\bsetup\b',
        r'\binstalliert\b',
        r'\bversion\b',
        r'\bplugin\b',
        r'\bskill\b',
        r'\.env',
        r'\.json',
        r'\bsudo\b',
        r'\b cron\b',
    ]
    
    for pattern in fact_patterns:
        if re.search(pattern, text_lower):
            if len(text) > 15:
                return CATEGORY_FACT, f"[{msg['date']}] [{sender}] {text[:300]}"
    
    # === TASK: Explicit tasks or todos ===
    task_patterns = [
        r'\bto[- ]?do\b',
        r'\bnext\b.*action',
        r'\bsollte[n]?\s+\w+',
        r'\bmache\s+ich\b',
        r'\berledige\b',
        r'\baufgabe\b',
        r'\btask\b',
        r'\bjob\b',
        r'\bbrauche\s+\w+\s+\w+',
        r'\bneeds\s+\w+',
        r'\bmust\s+\w+',
        r'\bwerde\b.*\b(eventual|effective|immediately)\b',
    ]
    
    for pattern in task_patterns:
        if re.search(pattern, text_lower):
            if len(text) > 15:
                return CATEGORY_TASK, f"[{msg['date']}] [{sender}] {text[:300]}"
    
    # === CODE: Contains code blocks or commands ===
    if '```' in text or '$ ' in text or ('python' in text_lower and ('script' in text_lower or 'code' in text_lower)):
        return CATEGORY_CODE, f"[{msg['date']}] [{sender}] {text[:300]}"
    
    # === SYSTEM: Dev_bot status updates ===
    if sender == "Dev_bot" and any(k in text_lower for k in ['gestartet', 'abgeschlossen', 'läuft', 'status', 'fertig', 'erfolgreich', 'subagent', 'agent']):
        if 'subagent' in text_lower or 'gestartet' in text_lower or 'abgeschlossen' in text_lower or 'fertig' in text_lower:
            return CATEGORY_SYSTEM, f"[{msg['date']}] {text[:200]}"
    
    return CATEGORY_DISCARD, None

def write_decision(content: str):
    """Write a decision to memory/decisions/"""
    os.makedirs(DECISIONS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{DECISIONS_DIR}/{today}-telegram-decisions.md"
    
    with open(filepath, 'a') as f:
        f.write(f"## Decision [{datetime.now().strftime('%H:%M')}]\n\n")
        f.write(f"{content}\n\n")
    print(f"  📝 Decision saved")

def write_learning(content: str):
    """Write a learning to memory/learnings/"""
    os.makedirs(LEARNINGS_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filepath = f"{LEARNINGS_DIR}/{today}-telegram-learnings.md"
    
    with open(filepath, 'a') as f:
        f.write(f"## Learning [{datetime.now().strftime('%H:%M')}]\n\n")
        f.write(f"{content}\n\n")
    print(f"  📚 Learning saved")

def write_fact(content: str):
    """Append facts to MEMORY.md"""
    with open(MEMORY_FILE, 'a') as f:
        f.write(f"\n### Fact (Telegram {datetime.now().strftime('%Y-%m-%d')})\n\n")
        f.write(f"{content}\n\n")
    print(f"  📌 Fact appended")

def write_task(content: str):
    """Add task to todos/current.md"""
    with open(TODOS_FILE, 'a') as f:
        f.write(f"- [ ] {content}\n")
    print(f"  ✅ Task added")

def process_file(filepath: str, dry_run: bool = False):
    """Process a single HTML file."""
    print(f"\n📥 Processing: {filepath}")
    
    # Parse
    messages = parse_telegram_html(filepath)
    print(f"   Found {len(messages)} messages")
    
    # Categorize and save
    stats = {CATEGORY_DECISION: 0, CATEGORY_LEARNING: 0, CATEGORY_FACT: 0, 
             CATEGORY_TASK: 0, CATEGORY_CODE: 0, CATEGORY_SYSTEM: 0, CATEGORY_DISCARD: 0}
    
    for msg in messages:
        category, summary = categorize_message(msg)
        stats[category] = stats.get(category, 0) + 1
        
        if category != CATEGORY_DISCARD and summary and not dry_run:
            if category == CATEGORY_DECISION:
                write_decision(summary)
            elif category == CATEGORY_LEARNING:
                write_learning(summary)
            elif category == CATEGORY_FACT:
                write_fact(summary)
            elif category == CATEGORY_TASK:
                write_task(summary)
            elif category == CATEGORY_CODE:
                # Save code snippets separately
                pass
    
    print(f"\n📊 Stats:")
    for cat, count in stats.items():
        if count > 0:
            print(f"   {cat}: {count}")
    
    return stats

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    filepath = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be written\n")
    
    stats = process_file(filepath, dry_run)
    
    print("\n✅ Processing complete!")
    print(f"   Total messages: {sum(stats.values())}")
    print(f"   Processed: {sum(v for k,v in stats.items() if k != CATEGORY_DISCARD)}")
    print(f"   Skipped: {stats[CATEGORY_DISCARD]}")

if __name__ == "__main__":
    main()