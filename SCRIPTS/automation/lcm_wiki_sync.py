#!/usr/bin/env python3
"""
📚 LCM Wiki-Sync — Konvertiert LCM-Summaries zu Wiki Permanent Notes

Liest von: wiki_sync_queue.json
Schreibt nach: memory/notes/permanent/

Hybrid-Lösung Teil 2:
- evening_capture.py → fleeting notes + sync queue
- lcm_wiki_sync.py → permanent wiki notes aus queue

Pattern: Karpathy LLM Wiki — persistente, kumulierende Wissensbasis
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
WIKI_DIR = WORKSPACE / "memory/notes/permanent"
WIKI_INDEX = WORKSPACE / "memory/wiki-index.md"
WIKI_SYNC_QUEUE = WORKSPACE / "data/wiki_sync_queue.json"
LEARNINGS_DIR = WORKSPACE / "memory/learnings"

# Wiki Permanent Note Template
PERMANENT_TEMPLATE = """---
title: "{title}"
date: {date}
category: {category}
agent: {agent}
tags: [{tags}]
---

# {title}

**Datum:** {date}
**Agent:** {agent}
**Kategorie:** {category}

---

## 🎯 Zusammenfassung

{summary}

---

## 💡 Key Learnings

{learnings}

---

## 🔜 Nächste Actions

{next_actions}

---

## 📊 Metriken

- Total Tokens: {tokens:,}
- Model: {model}
- Topics: {topics}

---

## 🔗 Verwandte Notes

{related_notes}

---

*Erstellt: {created_at}*
*LCM Wiki-Sync — Hybrid System v1*
"""

# Category keywords mapping
CATEGORY_KEYWORDS = {
    'System': ['system', 'gateway', 'server', 'cron', 'process', 'memory', 'disk', 'ram', 'load'],
    'Security': ['security', 'secret', 'api_key', 'token', 'auth', 'password', 'vulnerability', 'audit'],
    'Training': ['training', 'university', 'lesson', 'quiz', 'certificate', 'zertifikat', 'learning'],
    'Agents': ['agent', 'builder', 'ceo', 'security', 'data', 'research', 'flotte', 'fleet'],
    'Coding': ['code', 'script', 'python', 'javascript', 'api', 'function', 'implement', 'bug', 'fix'],
    'Memory': ['memory', 'wiki', 'knowledge', 'graph', 'note', 'context', 'semantic'],
    'Operations': ['operations', 'daily', 'briefing', 'report', 'status', 'metrics'],
    'Infrastructure': ['infrastructure', 'docker', 'server', 'deployment', 'backup', 'nginx'],
}

def categorize(topics, learnings):
    """Kategorisiert basierend auf Topics und Learnings."""
    text = ' '.join(topics + learnings).lower()
    
    scores = defaultdict(int)
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[category] += 1
    
    if scores:
        return max(scores, key=scores.get)
    return 'Operations'

def extract_summary(content, max_len=300):
    """Extrahiert erste aussagekräftige Sätze."""
    if not content:
        return "No content available"
    
    # Remove thinking blocks
    content = re.sub(r'<thinking>.*?</thinking>', '', content, flags=re.DOTALL)
    content = re.sub(r'\[.*?\]', '', content)  # Remove tool calls
    
    sentences = re.findall(r'[^.!?\n]{30,}[.!?]', content)
    if sentences:
        summary = sentences[0][:max_len]
        if len(sentences[0]) > max_len:
            summary += "..."
    else:
        summary = content[:max_len] + "..." if len(content) > max_len else content
    
    # Cleanup
    summary = re.sub(r'\s+', ' ', summary)
    summary = re.sub(r'[a-zA-Z0-9]{20,}', '[REDACTED]', summary)
    
    return summary.strip()

def format_learnings(learnings):
    """Formatiert Learnings als Markdown Liste."""
    if not learnings:
        return "- No specific learnings recorded"
    
    formatted = []
    for i, learning in enumerate(learnings[:10], 1):
        # Clean up
        learning = re.sub(r'\s+', ' ', learning).strip()
        if len(learning) > 100:
            learning = learning[:100] + "..."
        formatted.append(f"{i}. {learning}")
    
    return '\n'.join(formatted)

def format_next_actions(learnings, topics):
    """Leitet mögliche nächste Actions aus Learnings/Topics ab."""
    actions = []
    
    # Pattern für explizite Actions
    action_patterns = [
        r'(?:nächste|next|todo|action|task)[:\s]+([^\n]+)',
        r'\[ \]\s*([^\n]+)',
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, ' '.join(learnings), re.IGNORECASE)
        for m in matches:
            if m.strip():
                actions.append(m.strip())
    
    # Themen-basiert (wenn nichts explizites)
    if not actions and topics:
        actions.append(f"Explore {topics[0]} topic further")
    
    if not actions:
        actions.append("Review and integrate learnings")
    
    return '\n'.join([f"- [ ] {a}" for a in actions[:5]])

def find_related_notes(topics, existing_notes):
    """Findet verwandte Notes basierend auf Topics."""
    if not topics or not existing_notes:
        return "- No related notes found"
    
    related = []
    topics_lower = [t.lower() for t in topics]
    
    for note in existing_notes:
        note_lower = note.lower()
        for topic in topics_lower[:3]:
            if topic in note_lower and note not in related:
                related.append(note)
                break
    
    if not related:
        return "- No related notes found"
    
    return '\n'.join([f"- [[{n}]]" for n in related[:5]])

def load_queue():
    """Lädt die Wiki-Sync-Queue."""
    if not WIKI_SYNC_QUEUE.exists():
        print(f"⚠️  Queue not found: {WIKI_SYNC_QUEUE}")
        return []
    
    try:
        with open(WIKI_SYNC_QUEUE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading queue: {e}")
        return []

def get_existing_notes():
    """Listet existierende Permanent Notes."""
    if not WIKI_DIR.exists():
        return []
    
    notes = []
    for f in WIKI_DIR.glob("*.md"):
        # Skip template files
        if f.name.startswith("."):
            continue
        # Extract title from filename or content
        name = f.stem
        notes.append(name)
    
    return notes

def update_wiki_index(new_note_entry):
    """Updated die wiki-index.md mit neuer Note."""
    
    # Parse date for proper sorting
    date_str = new_note_entry.get('date', datetime.now().strftime("%Y-%m-%d"))
    title = new_note_entry.get('title', f'LCM-Sync {date_str}')
    category = new_note_entry.get('category', 'Operations')
    summary = new_note_entry.get('summary', '')[:80]
    topics = new_note_entry.get('topics', [])
    
    if topics:
        summary = f"{topics[0]}: {summary[:60]}..."
    
    # Build new row
    relative_path = f"notes/permanent/{date_str}-lcm-wiki.md"
    new_row = f"| [{title}](../{relative_path}) | {summary} | {category} | {date_str} |"
    
    # Check if index exists
    if not WIKI_INDEX.exists():
        # Create minimal index
        index_content = f"""# Wiki Index — EmpireHazeClaw Knowledge Base

> **Zweck:** Catalog aller Wiki-Seiten. LLM liest dies zuerst um relevante Pages zu finden.
> **Prinzip:** Karpathy LLM Wiki Pattern – persistent, compounding knowledge base.

---

## 📁 Permanent Notes (Langlebiges Wissen)

| Page | Summary | Category | Last Updated |
|------|---------|----------|-------------|
{new_row}

---

*Erstellt: {datetime.now().strftime('%Y-%m-%d')} via LCM Wiki-Sync*
"""
        WIKI_INDEX.parent.mkdir(parents=True, exist_ok=True)
        with open(WIKI_INDEX, 'w') as f:
            f.write(index_content)
        print(f"✅ Created wiki-index.md")
        return
    
    # Append to existing index
    with open(WIKI_INDEX, 'r') as f:
        content = f.read()
    
    # Find table and append
    if '## 📁 Permanent Notes' in content:
        # Check if already exists
        if title.replace(' ', '-').lower() in content.lower():
            print(f"⏭️  Note already in index: {title}")
            return
        
        # Insert before closing of permanent notes section or at end of table
        lines = content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if '|------|' in line or '|-----|' in line:
                insert_idx = i + 1
                break
        
        if insert_idx:
            lines.insert(insert_idx, new_row)
            content = '\n'.join(lines)
    
    with open(WIKI_INDEX, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated wiki-index.md")

def create_permanent_note(entry):
    """Erstellt eine Permanent Note aus Queue-Entry."""
    
    date_str = entry.get('date', datetime.now().strftime("%Y-%m-%d"))
    agent = entry.get('agent', 'Unknown')
    model = entry.get('model', 'unknown')
    tokens = entry.get('tokens', 0)
    topics = entry.get('topics', [])
    learnings = entry.get('learnings', [])
    content = entry.get('content', '')
    
    # Determine category
    category = categorize(topics, learnings)
    
    # Build title
    title = f"{date_str} LCM-Sync"
    if topics:
        title = f"{date_str} — {' / '.join(topics[:2])}"
    
    # Extract summary
    summary = extract_summary(content)
    
    # Get existing notes for related notes
    existing_notes = get_existing_notes()
    
    # Format
    note_content = PERMANENT_TEMPLATE.format(
        title=title,
        date=date_str,
        category=category,
        agent=agent,
        tags=', '.join(topics[:5]) if topics else 'uncategorized',
        summary=summary,
        learnings=format_learnings(learnings),
        next_actions=format_next_actions(learnings, topics),
        tokens=tokens,
        model=model,
        topics=', '.join(topics[:5]) if topics else 'none',
        related_notes=find_related_notes(topics, existing_notes),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    )
    
    # Write file
    filename = WIKI_DIR / f"{date_str}-lcm-wiki.md"
    if filename.exists():
        # Append if exists
        with open(filename, 'a') as f:
            f.write(f"\n\n---\n\n## Additional Entry ({datetime.now().strftime('%H:%M')})\n\n")
            f.write(f"- Agent: {agent}\n")
            f.write(f"- Topics: {', '.join(topics[:5])}\n")
            f.write(f"- Learnings: {len(learnings)}\n")
        print(f"📝 Appended to: {filename.name}")
    else:
        WIKI_DIR.mkdir(parents=True, exist_ok=True)
        with open(filename, 'w') as f:
            f.write(note_content)
        print(f"✅ Created: {filename.name}")
    
    return {
        'title': title,
        'date': date_str,
        'category': category,
        'summary': summary[:80],
        'topics': topics
    }

def save_to_learnings(entry):
    """Speichert отдельный Learning in learnings/- директор."""
    learnings = entry.get('learnings', [])
    if not learnings:
        return
    
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    date_str = entry.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    for i, learning in enumerate(learnings[:5]):
        filename = LEARNINGS_DIR / f"{date_str}-learning-{i+1}.md"
        
        content = f"""---
title: "Learning: {learning[:50]}..."
date: {date_str}
type: learning
agent: {entry.get('agent', 'unknown')}
tags: [{', '.join(entry.get('topics', [])[:3])}]
---

# Learning — {date_str}

## {learning[:100]}{'...' if len(learning) > 100 else ''}

**Source:** {entry.get('agent', 'unknown')}
**Topics:** {', '.join(entry.get('topics', [])[:5])}

---

*Auto-captured via LCM Wiki-Sync*
"""
        
        with open(filename, 'w') as f:
            f.write(content)
    
    print(f"📚 Saved {min(len(learnings), 5)} learnings to {LEARNINGS_DIR}")

def main():
    """Hauptfunktion."""
    print(f"📚 LCM Wiki-Sync — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Load queue
    queue = load_queue()
    print(f"📋 Queue size: {len(queue)} entries")
    
    if not queue:
        print("⚠️  No entries in queue. Run evening_capture.py first.")
        return
    
    # Process entries
    processed = 0
    for entry in queue:
        # Create permanent note
        note_entry = create_permanent_note(entry)
        
        # Update index
        update_wiki_index(note_entry)
        
        # Save individual learnings
        save_to_learnings(entry)
        
        processed += 1
    
    # Clear queue
    with open(WIKI_SYNC_QUEUE, 'w') as f:
        json.dump([], f)
    
    print(f"\n✅ Processed {processed} entries")
    print(f"📁 Permanent notes: {WIKI_DIR}/")
    print(f"📚 Learnings: {LEARNINGS_DIR}/")
    print(f"📋 Wiki index: {WIKI_INDEX}")

if __name__ == "__main__":
    main()