# META_SCHEMA.md — Knowledge Graph Rosetta Stone
**Stand:** 2026-04-10 | **Version:** 1.0

---

## 🎯 Zweck

Diese Datei ist der "Rosetta-Stein" für das Knowledge-Graph-System. Sie erklärt einer neuen KI-Architektur ohne Vorkenntnisse:
- Wie der Knowledge Graph aufgebaut ist
- Was die Relationstypen bedeuten
- Wie semantische Embeddings funktionieren
- Wie das System "denkt"

---

## 📊 knowledge_graph.json — Schema

**Pfad:** `memory/knowledge_graph.json`
**Größe:** ~953KB | **Entities:** 157 | **Relations:** 4623

### Top-Level Struktur

```json
{
  "entities": { ... },      // Dictionary: EntityName → EntityData
  "relations": [ ... ],     // Liste aller Beziehungen
  "relationships": [ ... ], // Alias für relations (identisch)
  "created": "ISO timestamp",
  "last_updated": "ISO timestamp"
}
```

### Entity-Schema

```json
{
  "EntityName": {
    "type": "string",       // Entity-Typ (siehe unten)
    "category": "string",   // Kategorie innerhalb des Typs
    "facts": [
      {
        "content": "string", // Fakt-Text
        "confidence": 0.0-1.0, // Confidence-Score (optional, default 0.5)
        "source": "string"    // Quelle (optional)
      }
    ],
    "confidence": 0.0-1.0,   // Gesamt-Confidence
    "last_updated": "ISO timestamp"
  }
}
```

### Relation-Schema

```json
{
  "from": "EntityName",     // Start-Entity
  "to": "EntityName",       // Ziel-Entity
  "type": "string",         // Relationstyp
  "weight": 0.0-1.0,        // Gewichtung (optional)
  "created_at": "ISO timestamp"
}
```

---

## 🔗 Relationstypen (Bedeutung)

| Type | Bedeutung | Beispiel |
|------|----------|---------|
| `shares_category` | Beide Entities teilen eine Kategorie | EmpireHazeClaw → Zielgruppe-KMU |
| `is_part_of` | Entity ist Teil eines Ganzen | KI-Mitarbeiter → EmpireHazeClaw |
| `learned_from` | Wissen wurde von Quelle abgeleitet | System → [USER] |
| `conflict_with` | Widerspruch zu anderer Entität | Annahme A ↔ Annahme B |
| `depends_on` | Abhängigkeit zwischen Entities | Trading Bot → Binance API |
| `uses` | Entity nutzt andere Resource | Builder → OpenClaw API |
| `created_by` | Wurde erstellt von | Blog Post → Content Agent |
| `synced_to` | Synchronisiert nach außen | Memory → MEMORY.md |

**Hinweis:** Aktuell ist nur `shares_category` aktiv in Verwendung. Weitere Typen können bei Bedarf hinzugefügt werden.

---

## 🧠 Embedding-Modell (Semantic Search)

**Modell:** `all-MiniLM-L6-v2`
**Dimensionen:** 384
**Provider:** Gemini (gemini-embedding-001)

### Kompatibilität sichern

Für Version 2.0 (oder Migration auf anderen Vector Store):
- Embedding-Dimension muss 384 sein
- Modell ist Sentence-Transformers basiert
- Alle Sprachen werden unterstützt (multilingual)
- Chunks werden in `memory/semantic_index.json` gespeichert

### Index-Struktur

```json
{
  "chunks": [
    {
      "id": "chunk_001",
      "text": "Chunk Text...",
      "embedding": [0.123, -0.456, ...],  // 384 dimensions
      "metadata": {
        "source": "MEMORY.md",
        "position": 0
      }
    }
  ]
}
```

---

## 🏗️ Architektur-Übersicht (Wie das System "denkt")

```
                    ┌─────────────────────┐
                    │  Knowledge Graph    │
                    │  (157 entities,     │
                    │   4623 relations)   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
       ┌────────────┐   ┌────────────┐   ┌────────────┐
       │ Semantic   │   │ Permanent  │   │  Learnings │
       │ Index      │   │ Notes (8)  │   │  (10)      │
       │ (81 chunks)│   │            │   │            │
       └────────────┘   └────────────┘   └────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │    MEMORY.md        │
                    │  (Central Hub +     │
                    │   Recent Decisions) │
                    └─────────────────────┘
```

---

## 📁 Memory-Ordner Struktur

```
memory/
├── knowledge_graph.json    # Haupt-Graf (957KB, 157 entities)
├── semantic_index.json    # Vektor-Embeddings (81 chunks)
├── MEMORY.md              # Zentraler Hub + Entscheidungen
├── SOUL.md                # System-Persona Definition
├── META_SCHEMA.md         # DIESE DATEI (Rosetta Stone)
├── wiki-index.md          # Wiki-Verzeichnis
├── wiki-log.md            # Wiki-Änderungslog
├── self-heal-*.json       # Self-Healing Status
├── engagement_config.json # Engagement-Regeln
├── social_config.json    # Social-Media Config
│
├── notes/
│   ├── fleeting/          # 5 fleeting notes (täglich, unstrukturiert)
│   │   └── YYYY-MM-DD-insight.md
│   └── permanent/         # 8 permanent notes (verarbeitet, verlinkt)
│       └── YYYY-MM-DD-*.md
│
├── learnings/             # 10 learnings (Agent-Logs, historisch)
│   └── YYYY-MM-DD*.md
│
├── shared/
│   ├── insights/          # 5 geteilte Insights
│   └── (insights werden hier generiert)
│
├── concepts/             # Konzepte-Dokumente
├── research/             # Recherche-Ergebnisse
│
├── archive/              # Archivierte Dateien
│   └── HEARTBEAT-history.md
│
└── scripts/              # Memory-Scripts (NICHT mehr LCM-abhängig)
    ├── kg_quick_add.py   # Schnell etwas zum KG hinzufügen
    ├── kg_auto_populate.py
    ├── suggest_links.py
    └── ... (weitere)
```

---

## 🔄 Typische Workflows

### 1. Neuen Fakt hinzufügen
```
Builder/Agent erkennt neues Wissen
    ↓
kg_quick_add.py ausführen (Fakt → Entity oder Relation)
    ↓
Knowledge Graph aktualisiert
    ↓
semantic_index wird neu gebaut (bei Bedarf)
```

### 2. Evening Capture (Tägliche Reflexion)
```
Cron: 21:00 UTC
    ↓
evening_capture.py erstellt fleeting note
    ↓
[USER] füllt 3 Insights des Tages ein
    ↓
Notes werden verarbeitet → permanent oder archiviert
```

### 3. Nightly Dreaming (Automatische Konsolidierung)
```
Cron: 02:00 UTC
    ↓
nightly_dreaming.py analysiert KG + Memory
    ↓
Generiert Insights in shared/insights/
    ↓
OpenClaw Dreaming: Deep Phase schreibt nach memory/dreaming/
```

### 4. Semantic Search (RAG)
```
Anfrage kommt
    ↓
Embedding via all-MiniLM-L6-v2 (384 Dim)
    ↓
Ähnlichste Chunks aus semantic_index.json
    ↓
Kontext wird dem LLM injiziert
    ↓
Antwort generiert
```

---

## ⚠️ Wichtige Hinweise für Migration

1. **LCM-Altlasten (ENTFERNT 2026-04-10)**
   - `lcm.db` existiert NICHT mehr
   - `lossless-claw.bak` gelöscht
   - LCM-Sync-Crons sind disabled
   - Knowledge Graph: `LCM-Compaction` Entity + 5 Relations entfernt

2. **Script-Referenzen ersetzt**
   - Statt `Run evening_capture.py` → "Prozess zur Abend-Zusammenfassung einleiten"
   - Statt `Run nightly_dreaming.py` → "Nächtliche Wissens-Konsolidierung"

3. **Confidence Scores**
   - Alle Entities haben optionale Confidence (0.0-1.0)
   - Default wenn nicht angegeben: 0.5
   - Niemals Null-Werte für Confidence

4. **Bidirektionale Relations**
   - Relations sind gerichtet (from → to)
   - Für bidirektionale Suche: beide Richtungen prüfen
   - `relationships` ist Alias für `relations` (identische Daten)

---

## 📦 Portable Pakete (Ready for Migration)

### Paket 1: Core Memory
```
memory/MEMORY.md                    # Zentraler Hub
memory/SOUL.md                      # System-Persona
memory/META_SCHEMA.md               # DIESE DATEI
memory/knowledge_graph.json         # Haupt-Wissensgraph
memory/semantic_index.json         # Vektor-Index
```

### Paket 2: Notes
```
memory/notes/fleeting/*.md          # 5 fleeting notes
memory/notes/permanent/*.md          # 8 permanent notes
```

### Paket 3: Learnings & Insights
```
memory/learnings/*.md               # 10 learnings
memory/shared/insights/*.md         # 5 insights
```

### Paket 4: Scripts (Dependency-Frei)
```
workspace/scripts/evening_capture.py      # Nur stdlib
workspace/scripts/nightly_dreaming.py     # Nur stdlib
workspace/requirements_retention.txt      # Minimal dependencies
```

### Paket 5: Agent Souls
```
workspace/*/SOUL.md                  # Alle Agent-Personas
```

---

*Erstellt: 2026-04-10 | Für Universal Memory Portability*
