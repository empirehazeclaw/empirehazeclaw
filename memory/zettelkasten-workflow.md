# 🧠 Zettelkasten Workflow — EmpireHazeClaw

*Etabliert: 2026-04-07*

---

## 📋 TÄGLICHER WORKFLOW

### Abend (21:00 UTC) — Evening Capture
```
1. Öffne memory/notes/fleeting/
2. Schreibe 3 Insights aus dem Tag
3. Nutze fleeting-template.md
4. Tag + Thema + Quelle vermerken
```

### Struktur einer Fleeting Note:
```
---
title: "Insight: [Kurzform]"
created: 2026-04-07
type: fleeting
tags: [business, decision, learning]
---

# Insight: [Titel]

## Was ist passiert?
> Kurze Beschreibung des Tagesereignisses

## Warum wichtig?
> Connection zu bestehendem Wissen

## Nächste Action
- [ ] Konkretes To-Do

## Quelle
- [[Telegram Chat]] / Meeting / Research
```

---

## 🔄 WOCHENTLICH (Sonntag) — Weekly Review

```
1. Öffne memory/notes/fleeting/
2. Lese alle Notes der Woche
3. Für jede Note:
   - Ist sie noch relevant? → BEHALTEN
   - Zu einem Concept verdichten? → CONCEPT
   - Wichtige Entscheidung? → DECISION
   - Nicht mehr wichtig? → LÖSCHEN
4. Lösche irrelevante Notes
5. Update Knowledge Graph
```

---

## 📊 MONATLICH — Knowledge Extraction

```
1. Öffne memory/notes/permanent/
2. Extrahiere neue Entities für knowledge_graph.json
3. Reviews für learnings/ schreiben
4. Wichtige Decisions in decisions/ archivieren
```

---

## 🏗️ STRUKTUR

```
notes/
├── fleeting/     # Rohe Insights (täglich neu)
│   └── YYYY-MM-DD-*.md
├── concepts/     # Verdichtete Konzepte (dauerhaft)
│   └── YYYY-MM-DD-*.md
├── ideas/        # Kreative Ideen
│   └── YYYY-MM-DD-*.md
├── insights/     # Besondere Erkenntnisse
│   └── YYYY-MM-DD-*.md
└── permanent/    # Wichtigste Notes (Archiv)
    └── YYYY-MM-DD-*.md
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

---

## 🤖 AUTO-TRIGGER

| Zeit | Action | Cron |
|------|--------|------|
| 21:00 UTC | Evening Reminder | `0 21 * * *` |
| Sonntag 22:00 | Weekly Review | `0 22 * * 0` |

---
*Zuletzt aktualisiert: 2026-04-07*
