#!/usr/bin/env python3
"""
Dreaming Promotion Reporter
============================
Reads phase-signals.json, extracts qualified promotions (remHits >= minRecallCount),
reads the actual content, and writes a visible promotion report to MEMORY.md.

This makes the invisible memory-core promotion visible to the user.
"""

import json
import re
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("/home/clawbot/.openclaw/workspace/ceo/memory")
PHASE_SIGNALS = MEMORY_DIR / ".dreams" / "phase-signals.json"
MEMORY_MD = Path("/home/clawbot/.openclaw/workspace/ceo/MEMORY.md")

# Promotion criteria (must match memory-core.short-term-promotion config)
MIN_RECALL_COUNT = 3
MIN_SCORE = 0.800

def load_phase_signals():
    """Load the phase-signals.json tracking file."""
    if not PHASE_SIGNALS.exists():
        return {"entries": {}}
    with open(PHASE_SIGNALS) as f:
        return json.load(f)

def parse_key(key):
    """Parse a phase-signal key like 'memory:memory/ARCHIVE/2026-04-12.md:1:33'"""
    # Format: memory:<path>:<start_line>:<end_line>
    match = re.match(r'memory:memory/(.+):(\d+):(\d+)', key)
    if match:
        filepath = match.group(1)
        start_line = int(match.group(2))
        end_line = int(match.group(3))
        return str(MEMORY_DIR / filepath), start_line, end_line
    return None, None, None

def read_content_at_lines(filepath, start_line, end_line):
    """Read specific line range from a file."""
    try:
        with open(filepath) as f:
            lines = f.readlines()
            # Convert to 0-indexed
            start_idx = max(0, start_line - 1)
            end_idx = min(len(lines), end_line)
            return ''.join(lines[start_idx:end_idx]).strip()
    except Exception as e:
        return f"[Error reading: {e}]"

def extract_key_insight(content, max_chars=300):
    """Extract the key insight from content."""
    # Clean up and truncate
    content = content.strip()
    if len(content) > max_chars:
        return content[:max_chars] + "..."
    return content

def generate_promotion_report(phase_signals):
    """Generate a promotion report from phase signals."""
    entries = phase_signals.get('entries', {})
    
    # Find qualifying entries (remHits >= MIN_RECALL_COUNT)
    promotions = []
    for key, data in entries.items():
        rem_hits = data.get('remHits', 0)
        if rem_hits >= MIN_RECALL_COUNT:
            filepath, start_line, end_line = parse_key(key)
            if filepath:
                content = read_content_at_lines(filepath, start_line, end_line)
                promotions.append({
                    'key': key,
                    'remHits': rem_hits,
                    'lastRemAt': data.get('lastRemAt', 'unknown'),
                    'filepath': filepath,
                    'lines': f"{start_line}-{end_line}",
                    'content': extract_key_insight(content)
                })
    
    # Sort by remHits descending
    promotions.sort(key=lambda x: x['remHits'], reverse=True)
    
    return promotions

def format_report(promotions):
    """Format the promotion report as markdown."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    
    if not promotions:
        report = f"""## 🌙 DREAMING REPORT — {timestamp}

*No promotions qualifying this cycle (minRecallCount={MIN_RECALL_COUNT})*

"""
    else:
        promo_items = []
        for p in promotions:
            # Extract filename for display
            filename = Path(p['filepath']).name
            promo_items.append(f"- **{filename}** lines {p['lines']} — {p['remHits']} recall hits\n  → {p['content'][:150]}...")

        report = f"""## 🌙 DREAMING REPORT — {timestamp}

### ✅ Promotions (qualifying entries)

{chr(10).join(promo_items)}

---
*Memory-core short-term-promotion criteria: minScore={MIN_SCORE}, minRecallCount={MIN_RECALL_COUNT}*

"""
    return report

def update_memory_md(report):
    """Append promotion report to MEMORY.md."""
    with open(MEMORY_MD) as f:
        content = f.read()
    
    # Remove existing "DREAMING REPORT" section if present
    pattern = r'\n## 🌙 DREAMING REPORT.*?(?=\n## |\Z)'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Append new report before the RECALL INDEX section
    recall_index_match = re.search(r'\n## 📊 RECALL INDEX', content)
    if recall_index_match:
        insert_pos = recall_index_match.start()
        content = content[:insert_pos] + "\n" + report + content[insert_pos:]
    else:
        content = content + "\n" + report
    
    with open(MEMORY_MD, 'w') as f:
        f.write(content)

def main():
    print(f"[Dreaming Reporter] Reading phase-signals.json...")
    phase_signals = load_phase_signals()
    
    print(f"[Dreaming Reporter] Generating promotion report...")
    promotions = generate_promotion_report(phase_signals)
    print(f"[Dreaming Reporter] Found {len(promotions)} qualifying promotions")
    
    report = format_report(promotions)
    print(f"[Dreaming Reporter] Report:\n{report}")
    
    print(f"[Dreaming Reporter] Updating MEMORY.md...")
    update_memory_md(report)
    
    print(f"[Dreaming Reporter] Done!")

if __name__ == "__main__":
    main()