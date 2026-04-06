# Example 3: Daily Notes & Query System

## Layer 2: Daily Notes (Chronologische Timeline)

Tägliche Notizen erfassen alle Ereignisse chronologisch - gegliedert nach Tageszeit.

### Heute: 2026-03-05

```markdown
# Daily Notes - 2026-03-05

## Morning (00:00 - 12:00)
- 08:30 - Gestartet: Memory System Skill vorbereiten
- 09:15 - ClawMart Submission geplant
- 10:00 - BI Council Meeting vorbereitet

## Afternoon (12:00 - 18:00)
- 13:00 - Gespräch: "Ich heiße Nico und will €100/Monat mit POD verdienen"
- 14:30 - Fakten automatisch extrahiert und in Knowledge Graph gespeichert
- 16:00 - Priority neu berechnet für "Master" → CRITICAL

## Evening (18:00 - 24:00
- [Noch keine Einträge]
```

---

## Layer 3: Tacit Knowledge (User Patterns)

Stilles Wissen über den Benutzer - automatisch gelernt:

```markdown
# Tacit Knowledge - Master

## Preferences
- Language: German (Deutsch)
- Communication: Direct, concise, no filler
- Tone: Professional but friendly

## Patterns
- Morning person (arbeitet meistens morgens)
- Short messages bevorzugt
- Schätzt klare Bestätigungen ("✅ Erledigt")

## Lessons Learned
- [2026-03-04] "€100/Monat" Ziel ist wichtig - nicht vergessen!
- [2026-03-03] POD Business = aktuelles Hauptprojekt

## Style
- Emoji: Minimal - nur für Betonung
- Format: [Bestätigung] → [Antwort] → [Signal]
```

---

## Query System mit Priority Filtering

### Beispiel-Queries

```
┌─────────────────────────────────────────────────────────────┐
│ QUERY: "Geld"                                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Suchfilter: priority=HIGH                                   │
│                                                             │
│ Results:                                                   │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ [CRITICAL] Master                                   │   │
│ │   Fact: "will €100 pro Monat mit POD verdienen"    │   │
│ │   Score: 0.90 × 1.0 (recency) = 0.90               │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ [HIGH] POD-Business                                 │   │
│ │   Fact: "Ziel: €100/Monat"                         │   │
│ │   Score: 0.80 × 0.95 (recency) = 0.76              │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Query mit verschiedenen Filtern

```
# Filter: ALL (alle Prioritäten)
memory.query("POD")
→ Returns: CRITICAL, HIGH, MEDIUM, LOW

# Filter: CRITICAL (nur Persönliches)
memory.query("Name", priority_filter="CRITICAL")
→ Returns: Nur "Master" entity

# Filter: project (nur Projekte)
memory.query("Business", category="Projects")
→ Returns: Nur POD-Business, Etsy-Integration, etc.
```

---

## Komplettes Memory Flow Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPLETE MEMORY FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  USER MESSAGE                                              │
│       │                                                    │
│       ▼                                                    │
│  ┌─────────────────────────────────────────┐               │
│  │ 1. FACT EXTRACTION                     │               │
│  │    • Parse: preference, goal, pattern   │               │
│  │    • Calculate confidence (0.6 - 0.9)   │               │
│  │    • Assign initial priority            │               │
│  └──────────────────┬──────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ 2. KNOWLEDGE GRAPH UPDATE               │               │
│  │    • Add to correct PARA category       │               │
│  │    • Apply memory decay                 │               │
│  │    • Update entity priority             │               │
│  └──────────────────┬──────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ 3. DAILY NOTES                          │               │
│  │    • Determine time block (M/A/E)       │               │
│  │    • Log raw event                      │               │
│  └──────────────────┬──────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ 4. TACIT KNOWLEDGE                      │               │
│  │    • Extract user patterns              │               │
│  │    • Update preferences                 │               │
│  │    • Learn communication style          │               │
│  └──────────────────┬──────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ 5. SAVE STATE                           │               │
│  │    • knowledge_graph.json               │               │
│  │    • daily/YYYY-MM-DD.md                │               │
│  │    • tacit.md                           │               │
│  └─────────────────────────────────────────┘               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
