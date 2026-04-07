#!/bin/bash
# memory_compress.sh — Archiviert alte MEMORY.md Einträge (täglich via Cron)
# Führt Python-Skript aus, das:
#   1. Fact-Sections mit embedded Datum < 30 Tage → memory/archive/YYYY-MM.md
#   2. MEMORY.md auf recent entries komprimieren

MEMORY="/home/clawbot/.openclaw/workspace/MEMORY.md"
ARCHIVE="/home/clawbot/.openclaw/workspace/memory/archive"
PYTHON="/usr/bin/python3"

mkdir -p "$ARCHIVE"

$PYTHON << 'PYEOF'
import re, os, json
from collections import defaultdict
from datetime import datetime, timedelta

MEMORY = "/home/clawbot/.openclaw/workspace/MEMORY.md"
ARCHIVE = "/home/clawbot/.openclaw/workspace/memory/archive"
os.makedirs(ARCHIVE, exist_ok=True)

with open(MEMORY, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

first_fact = content.find('### Fact (Telegram')
if first_fact == -1:
    print("No fact sections found.")
    exit(0)

non_fact = content[:first_fact]
fact_sections = re.findall(
    r'(### Fact \(Telegram \d{4}-\d{2}-\d{2}\)\n\n)(.{10,500}?)(?=\n### Fact \(Telegram|\Z)',
    content, re.DOTALL
)

# 30 days ago
cutoff = (datetime(2026, 4, 6) - timedelta(days=30)).strftime('%Y-%m-%d')
cutoff = '%Y-%m-01'  # archive entire months older than current month

to_archive = []
to_keep = []

for header, body in fact_sections:
    m = re.search(r'\[(\d{2})\.(\d{2})\.(\d{4})\]', body)
    if m:
        ref_date = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
        if ref_date < cutoff:
            to_archive.append((header, body, ref_date))
        else:
            to_keep.append((header, body, ref_date))
    else:
        to_keep.append((header, body, None))

print(f"Archiving {len(to_archive)} sections, keeping {len(to_keep)} sections.")

by_month = defaultdict(list)
for h, b, d in to_archive:
    mk = d[:7] if d else "unknown"
    by_month[mk].append((h, b, d))

for month_key, sections in sorted(by_month.items()):
    archive_path = os.path.join(ARCHIVE, f"{month_key}.md")
    existing = []
    if os.path.exists(archive_path):
        with open(archive_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        existing = re.findall(
            r'(### Fact \(Telegram \d{4}-\d{2}-\d{2}\)\n\n)(.{10,500}?)(?=\n### Fact \(Telegram|\Z)',
            existing_content, re.DOTALL
        )
    with open(archive_path, 'w', encoding='utf-8') as f:
        f.write(f"# Archived Memory — {month_key}\n\n")
        f.write(f"*Last updated: {datetime.now().strftime('%Y-%m-%d')}*\n\n---\n\n")
        seen = set()
        for h, b, d in existing + sections:
            key = (h, b)
            if key not in seen:
                seen.add(key)
                f.write(h + b + "\n\n")
    print(f"  Wrote {archive_path}: {len(sections)} new sections")

# Rewrite MEMORY.md
with open(MEMORY, 'w', encoding='utf-8') as f:
    f.write(non_fact)
    for h, b, d in to_keep:
        f.write(h + b + "\n\n")

size_kb = os.path.getsize(MEMORY) / 1024
print(f"✅ MEMORY.md: {size_kb:.1f} KB")
PYEOF
