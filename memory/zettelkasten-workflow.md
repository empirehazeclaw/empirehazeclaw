# 🧠 Zettelkasten + LLM Wiki Workflow — EmpireHazeClaw

*Etabliert: 2026-04-07 | Basierend auf Karpathys LLM Wiki Pattern*

---

## 🎯 Das Prinzip

> **RAG vs. Wiki:** Normales RAG entdeckt Wissen bei jeder Query neu. Unser Wiki **baut und pflegt** persistent Wissen, das sich gegenseitig referenziert und aktualisiert wird.
>
> Der LLM macht das Maintenance-Work. Der Mensch kuratiert Sources und stellt Fragen.

---

## 🏗️ 3-LAYER ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RAW SOURCES (unveränderlich)                      │
│  memory/data/, memory/archive/, memory/learnings/            │
│  → Echte Sources: Chats, Docs, Research, Logs               │
└─────────────────────────────┬───────────────────────────────┘
                              │ LLM liest & extrahiert
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: WIKI (LLM-generiert, LLM-gepflegt)               │
│  memory/notes/concepts/, memory/notes/permanent/             │
│  memory/wiki-index.md, memory/wiki-log.md                    │
│  → Entity Pages, Concept Pages, Summaries, Cross-Refs       │
└─────────────────────────────┬───────────────────────────────┘
                              │ LLM & Mensch
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: SCHEMA (Konfiguration)                           │
│  memory/zettelkasten-workflow.md (dieses File)             │
│  AGENTS.md, SOUL.md                                         │
│  → Sagt dem LLM WIE die Wiki gepflegt wird                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 DREI OPERATIONEN

### 1. INGEST — Neue Source integrieren

```
WHEN: Neue Information kommt rein (Research, Chat, Reading)
THEN:
  1. Source in raw/ speichern
  2. LLM liest Source
  3. LLM diskutiert Key Takeaways
  4. LLM schreibt Summary in wiki/
  5. LLM updated index.md (neue Page hinzufügen)
  6. LLM updated log.md (## [DATE] ingest | Description)
  7. LLM updated relevante Entity/Concept Pages (bis zu 15 Files!)
```

**Ingest Checkliste:**
- [ ] Source gespeichert in raw/
- [ ] Summary Page erstellt
- [ ] index.md updated
- [ ] log.md appended
- [ ] Cross-Refs zu bestehenden Pages

---

### 2. QUERY — Frage an Wiki stellen

```
WHEN: Mensch oder Agent stellt Frage
THEN:
  1. LLM liest index.md zuerst
  2. LLM findet relevante Pages
  3. LLM liest relevante Pages
  4. LLM synthetisiert Antwort
  5. LLM bietet an: "Soll ich das als neue Page speichern?"
```

**Query Output Formate:**
- Markdown Page
- Comparison Table
- Slide Deck (Marp)
- Chart (matplotlib)

---

### 3. LINT — Wiki Health Check

```
WHEN: Wöchentliches Review (Sonntag) ODER monatlich
THEN:
  1. LLM prüft auf Widersprüche zwischen Pages
  2. LLM findet veraltete Claims (neue Sources haben aktualisiert)
  3. LLM findet Orphan Pages (keine inbound links)
  4. LLM findet wichtige Konzepte ohne eigene Page
  5. LLM schlägt neue Cross-Refs vor
  6. LLM schlägt neue Questions/Sources vor
  7. LLM updated log.md (## [DATE] lint | Findings)
```

**Lint Checkliste:**
- [ ] Widersprüche gefunden? → Markiert
- [ ] Veraltete Claims? → Aktualisiert
- [ ] Orphan Pages? → Link vorgeschlagen
- [ ] Fehlende Pages? → Erstellt
- [ ] Fehlende Cross-Refs? → Hinzugefügt

---

## 📁 SPEZIELLE FILES

### wiki-index.md (Content Catalog)

```
Zweck: Schneller Überblick über alle Wiki-Pages
Lese: Bei jeder Query zuerst
Update: Nach jedem Ingest
Format: Table mit Link + One-Line-Summary + Metadata
```

### wiki-log.md (Chronik)

```
Zweck: Timeline der Wiki-Evolution
Format: ## [YYYY-MM-DD] type | description
Types: ingest, query, lint, decision, learning, setup
Parsebar via: grep "^## \[" wiki-log.md
```

---

## 📋 TÄGLICHER WORKFLOW

### Abend (21:00 UTC) — Evening Capture

```
1. Öffne memory/notes/fleeting/
2. Schreibe 3 Insights aus dem Tag
3. Nutze fleeting-template.md
4. Tag + Thema + Quelle vermerken
5. Prüfe: Braucht eine Note Ingest in die Wiki?
```

### Struktur einer Fleeting Note:

```markdown
---
title: "Insight: [Kurzform]"
created: 2026-04-07
type: fleeting
tags: [business, decision, learning]
---

# Insight: [Titel]

## Was ist passiert?
> Kurze Beschreibung

## Warum wichtig?
> Connection zu bestehendem Wissen

## Nächste Action
- [ ] Konkretes To-Do

## Quelle
- [[Telegram]] / Meeting / Research
```

---

## 🔄 WOCHENTLICH (Sonntag) — Wiki Review

```
1. Öffne memory/notes/fleeting/
2. Lese alle Notes der Woche
3. Für jede Note:
   - Ist sie noch relevant? → BEHALTEN
   - Zu einem Concept verdichten? → CONCEPT
   - Wichtige Entscheidung? → DECISION
   - Nicht mehr wichtig? → LÖSCHEN
4. Führe LINT durch (siehe oben)
5. Update Knowledge Graph
6. Append zu wiki-log.md
```

---

## 📊 MONATLICH — Knowledge Extraction

```
1. Öffne memory/notes/permanent/
2. Extrahiere neue Entities für knowledge_graph.json
3. Reviews für learnings/ schreiben
4. Wichtige Decisions in decisions/ archivieren
5. Prüfe: Welche Pages brauchen Merge/Split?
```

---

## 🏗️ VERZEICHNIS-STRUKTUR

```
memory/
├── wiki-index.md          # Catalog aller Pages (NEU)
├── wiki-log.md            # Chronik (NEU)
├── zettelkasten-workflow.md
├── notes/
│   ├── fleeting/          # Rohe Insights (täglich)
│   │   └── YYYY-MM-DD-*.md
│   ├── concepts/          # Verdichtete Konzepte
│   │   └── YYYY-MM-DD-*.md
│   ├── permanent/         # Wichtige Notes
│   │   └── YYYY-MM-DD-*.md
│   └── research/          # Research Results
│       └── *.md
├── learnings/             # Gelernte Lektionen
├── archive/               # Archiviert
└── data/                  # Rohdaten, Exports
```

---

## ⚡ REGELN

| Regel | Beschreibung |
|-------|--------------|
| Atomic | Eine Note = ein Insight |
| Link | Immer zu anderen Notes verlinken |
| Tag | Mindestens 1 Tag pro Note |
| Source | Quelle immer vermerken |
| Review | Wöchentlich aufräumen |
| **Ingest** | Source zuerst speichern, dann Wiki updaten |
| **Lint** | Monatlich Health-Check durchführen |
| **Index** | Nach jedem Ingest updaten |
| **Log** | Append-only Chronik pflegen |

---

## 🤖 AUTO-TRIGGER

| Zeit | Action | Cron |
|------|--------|------|
| 21:00 UTC | Evening Capture Reminder | `0 21 * * *` |
| 22:00 Sun | Weekly Review + Lint | `0 22 * * 0` |
| 06:00 UTC | KG Auto-Populate | `0 6 * * *` |

---

## 🔍 PARSE COMMANDS

```bash
# Letzte 5 Wiki-Einträge
grep "^## \[" memory/wiki-log.md | tail -5

# Alle Ingest-Einträge
grep "ingest" memory/wiki-log.md

# Orphan Pages finden (keine Links)
grep -L "link" memory/notes/concepts/*.md

# Alle Tags
grep "^tags:" memory/notes/**/*.md
```

---

## 📚 QUELLEN

- Karpathy LLM Wiki Pattern: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Vannevar Bush's Memex (1945) – Inspiration für persönliche Knowledge Stores

---

*Zuletzt aktualisiert: 2026-04-07 | CEO ClawMaster*
