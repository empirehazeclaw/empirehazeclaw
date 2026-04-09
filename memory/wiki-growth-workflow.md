# Wiki Growth Workflow — Hybrid Wiki-Sync (v4)

**Erstellt:** 2026-04-07
**Status:** ✅ AKTIV
**Letzte Aktualisierung:** 2026-04-09

---

## 🎯 Das Problem (v1-v2 waren defekt)

- v1-v2: `evening_capture.py` erstellte nur leere Templates
- Niemand füllte sie aus → Wiki wuchs nicht
- v3: LCM-Sync kam hinzu, aber `extract_insights()` war zu eng

---

## ✅ Die Lösung: Zwei-Wege-Hybrid-Automatisierung

### Weg 1: Nach jeder Session → Agent erstellt Note

```
WANN:  Nach jeder delegierten Task ODER längerer Arbeits-Session
WER:   Der Agent der gerade gearbeitet hat
WAS:
  1. Erstelle Note in notes/permanent/ oder notes/fleeting/
  2. Format: YYYY-MM-DD-{topic}.md
  3. Inhalt: Was wurde gemacht, Learnings, Nächste Schritte
  4. Wiki-index.md updaten
```

### Weg 2: Tägliches Auto-Capture (v4 — verbessert)

```
WANN:  21:00 UTC (evening_capture.py)
WAS:
  - LCM Session-Files der letzten 24h analysieren
  - Echte Inhalte extrahieren (不再是 leere Templates)
  - fleeting Note erstellen MIT echtem Inhalt
  - Wiki-Sync-Queue befüllen für lcm_wiki_sync.py

CRON:  0 21 * * * /home/clawbot/.openclaw/workspace/scripts/evening_capture.py
```

---

## 🔄 Auto-Capture Pipeline (v4)

```
┌─────────────────────────────────────────────────────────┐
│  evening_capture.py (21:00 UTC)                        │
│  1. Findet LCM-Files der letzten 24h                   │
│  2. Parst Sessions → extrahiert ECHTE Inhalte          │
│  3. Erstellt fleeting Note MIT Inhalt                   │
│  4. Befüllt wiki_sync_queue.json                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  lcm_wiki_sync.py (manuell oder Cron)                  │
│  1. Liest wiki_sync_queue.json                          │
│  2. Erstellt Permanent Notes in memory/notes/permanent/ │
│  3. Updated wiki-index.md                              │
│  4. Speichert einzelne Learnings in memory/learnings/  │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Wiki-Struktur

```
memory/
├── wiki-index.md              # Hauptindex — LLM liest dies ZUERST
├── notes/
│   ├── fleeting/             # Kurzlebige Gedanken (werden zu Permanent)
│   │   └── YYYY-MM-DD-insight.md
│   └── permanent/             # Langlebige Notes (Karpathy Pattern)
│       ├── 2026-04-09-lcm-wiki.md
│       └── 2026-04-08-wiki-growth-workflow.md
├── learnings/                 # Individualisierte Learnings
│   └── YYYY-MM-DD-learning-N.md
└── concepts/                  # Konzepte & Ideen
```

---

## 📝 Permanent Note Template

```markdown
---
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

## 📂 Referenzierte Files & Topics
{files}

---

*Erstellt: {created_at}*
*LCM Wiki-Sync — Hybrid System v4*
```

---

## 🔧 extract_insights() Verbesserungen (v4)

**NEU in v4:**
- Bullet points `•` und `-` werden als Learnings erkannt
- Nummerierte Listen `1.` `2.` werden extrahiert
- Code-blocks mit Resultaten werden erfasst
- Emoji-Starts `✅` `❌` `⚠️` als Status-Indikatoren
- Headers `#` `##` werden als Topics erkannt
- Längere Textblöcke (>50 Zeichen) ohne Keyword werden trotzdem erfasst

---

## 📊 Erfolg-Metriken

| Metrik | Ziel | Aktuell |
|--------|------|---------|
| Notes/Tag (fleeting) | ≥1 | ✅ |
| Permanent Notes/Tag | ≥2 | ✅ |
| Wiki-index Pages | Wachsend | ✅ |
| wiki-sync_queue gefüllt | >0 Items | ⚠️ (leer nach Sync) |

---

## 🚀 Integration

### Cron Setup:
```bash
# Evening Capture (21:00 UTC)
0 21 * * * cd /home/clawbot/.openclaw/workspace && python3 scripts/evening_capture.py >> logs/evening_capture.log 2>&1

# Wiki Sync (22:00 UTC)
0 22 * * * cd /home/clawbot/.openclaw/workspace && python3 scripts/lcm_wiki_sync.py >> logs/lcm_wiki_sync.log 2>&1
```

### Agent SOUL.md Wiki-Pflege:
```markdown
## 📝 Wiki-Pflege
Nach jeder Task:
1. Erstelle Note in /workspace/memory/notes/{category}/
2. Update wiki-index.md (neue Page hinzufügen)
3. Report an CEO mit Note-Pfad
```

---

## 🐛 Known Issues

| Issue | Status | Lösung |
|-------|--------|--------|
| LCM-Pfad in evening_capture.py | ✅ Fixed | `/home/clawbot/.openclaw/lcm-files` |
| extract_insights() zu eng | ✅ Fixed v4 | Neue Patterns |
| fleeting Note leer | ✅ Fixed v4 | Echter Content statt Template |

---

*Hybrid Wiki-Sync v4 — Letzte Aktualisierung: 2026-04-09*
