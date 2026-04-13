#!/usr/bin/env python3
"""
Auto Session Capture — Zettelkasten Daily Reminder v2
Erfüllt: Erstellt eine fleeting Note MIT Inhalt (nicht nur ein Template)

分析: Liest Session-Transcripts und extrahiert Key-Takeaways
"""
import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

# Config
WORKSPACE = Path("/home/clawbot/.openclaw/workspace")
NOTES_DIR = WORKSPACE / "memory/notes/fleeting"
SESSIONS_DIR = Path("/home/clawbot/.openclaw/agents")
DAYS_BACK = 1  # Nur letzte 24h

TEMPLATE = """---
title: "{title}"
created: {date}
type: fleeting
source: auto-capture
tags: [auto-capture,insight,daily]
---

# {title}

## 🎯 Zusammenfassung
{summary}

## 💡 Key Learnings
{learnings}

## 🔜 Offene Tasks
{open_tasks}

## 📂 Referenzierte Files
{files}

---

*Auto-generiert: {timestamp}*
*Quelle: Session-Analyse der letzten 24h*
"""

def find_recent_sessions():
    """Findet Session-Dateien der letzten 24 Stunden."""
    sessions = []
    cutoff = datetime.now() - timedelta(days=DAYS_BACK)
    
    # Durchsuche alle Agent-Session-Verzeichnisse
    for agent_dir in SESSIONS_DIR.iterdir():
        if not agent_dir.is_dir():
            continue
        session_dir = agent_dir / "sessions"
        if not session_dir.exists():
            continue
            
        for session_file in session_dir.glob("*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                if mtime > cutoff:
                    sessions.append(session_file)
            except:
                continue
    
    return sessions

def extract_content_from_session(session_file):
    """Extrahiert Text-Content aus einer Session-JSONL Datei."""
    content_parts = []
    
    try:
        with open(session_file, 'r') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    # Extrahiere nur assistant messages (nicht tool_calls)
                    if entry.get('role') == 'assistant':
                        content = entry.get('content', [])
                        if isinstance(content, list):
                            for part in content:
                                if part.get('type') == 'text':
                                    content_parts.append(part.get('text', ''))
                        elif isinstance(content, str):
                            content_parts.append(content)
                except:
                    continue
    except Exception as e:
        print(f"Error reading {session_file}: {e}")
    
    return '\n'.join(content_parts)

def analyze_content(content):
    """Analysiert Content und extrahiert Learnings, Tasks, Files."""
    
    # Pattern für Learnings (Typ: "gelernt", "learned", "wichtig", etc.)
    learning_patterns = [
        r'(?:gelernt|learned|wichtig|important|key learning)[:\s]+([^\n]+)',
        r'(?:pattern|insight|erkenntnis)[:\s]+([^\n]+)',
        r'→\s*([^\n]+)',  # Pfeil-Markierungen
    ]
    
    # Pattern für Files
    file_patterns = [
        r'([/\w]+\.(?:md|py|js|json|sh|txt))',
        r'`([^`]+\.(?:md|py|js|json|sh))`',
    ]
    
    # Pattern für Tasks
    task_patterns = [
        r'\[ \]\s*([^\n]+)',
        r'(?:todo|task|nächste)[:\s]+([^\n]+)',
        r'(?:open|pending)[:\s]+([^\n]+)',
    ]
    
    learnings = []
    files = []
    tasks = []
    
    for pattern in learning_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        learnings.extend([m.strip() for m in matches if m.strip()])
    
    for pattern in file_patterns:
        matches = re.findall(pattern, content)
        files.extend([m.strip() for m in matches if m.strip()])
    
    for pattern in task_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        tasks.extend([m.strip() for m in matches if m.strip()])
    
    # Dedupliziere
    learnings = list(dict.fromkeys(learnings))[:10]
    files = list(dict.fromkeys(files))[:20]
    tasks = list(dict.fromkeys(tasks))[:5]
    
    return learnings, files, tasks

def create_summary(content, learnings, files, tasks):
    """Erstellt eine kurze Zusammenfassung."""
    
    # Einfache Heuristik: Nimm erste 200 Zeichen die nach einem Satz aussehen
    sentences = re.findall(r'[.!?]+\s+[A-Z]', content)
    if len(sentences) > 3:
        summary = content[:300] + "..."
    else:
        summary = content[:200] + "..." if len(content) > 200 else content
    
    # Ersetze potentielle Secrets
    summary = re.sub(r'[a-zA-Z0-9_]{20,}', '[REDACTED]', summary)
    
    return summary[:300]

def create_daily_note():
    """Hauptfunktion: Erstellt die tägliche Auto-Capture Note."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_ts = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    filename = NOTES_DIR / f"{today}-auto-insight.md"
    
    # Check ob bereits existiert
    if filename.exists():
        print(f"⏭️  Note für {today} existiert bereits: {filename}")
        return None
    
    print(f"🔍 Suche Sessions der letzten {DAYS_BACK} Tag(e)...")
    
    # Finde Sessions
    sessions = find_recent_sessions()
    print(f"   Gefunden: {len(sessions)} Session-Dateien")
    
    if not sessions:
        print("⚠️  Keine Sessions gefunden — erstelle leere Note")
        learnings = ["Keine Sessions in den letzten 24h gefunden"]
        files = []
        tasks = []
        summary = "Keine Session-Aktivität in den letzten 24h."
    else:
        # Extrahiere Content
        all_content = []
        for session in sessions:
            content = extract_content_from_session(session)
            if content:
                all_content.append(content)
        
        combined = '\n\n'.join(all_content)
        print(f"   Verarbeitet: {len(combined)} Zeichen Content")
        
        # Analysiere
        learnings, files, tasks = analyze_content(combined)
        summary = create_summary(combined, learnings, files, tasks)
        
        print(f"   Learnings: {len(learnings)}")
        print(f"   Files: {len(files)}")
        print(f"   Tasks: {len(tasks)}")
    
    # Formatiere Learnings
    learnings_str = '\n'.join([f"- {l}" for l in learnings]) if learnings else "- (keine extrahiert)"
    
    # Formatiere Files
    files_str = '\n'.join([f"- `{f}`" for f in files]) if files else "- (keine referenziert)"
    
    # Formatiere Tasks
    tasks_str = '\n'.join([f"- [ ] {t}" for t in tasks]) if tasks else "- (keine offen)"
    
    # Erstelle Note
    content = TEMPLATE.format(
        title=f"Auto-Capture {today}",
        date=today,
        summary=summary,
        learnings=learnings_str,
        open_tasks=tasks_str,
        files=files_str,
        timestamp=today_ts
    )
    
    # Schreibe File
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Erstellt: {filename}")
    print(f"📝 {len(learnings)} Learnings, {len(files)} Files, {len(tasks)} Tasks")
    
    return str(filename)

if __name__ == "__main__":
    result = create_daily_note()
    if result:
        print(f"\n💡 Nächste Schritte:")
        print(f"   1. Note prüfen und ggf. anreichern")
        print(f"   2. Wiki-index.md updaten")
        print(f"   3. Wiki-log.md appenden")
