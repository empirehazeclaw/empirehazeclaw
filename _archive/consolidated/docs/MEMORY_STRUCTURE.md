# MEMORY STRUKTUR — Semantic vs Episodic

**Erstellt:** 2026-04-10
**Basierend auf:** MongoDB Agent Memory Guide + DeepLearning.AI Course

---

## 🎯 WARUM

AI Agents brauchen verschiedene Memory-Typen:
- **Semantic Memory:** Fakten, Wissen, Konzepte (strukturiert)
- **Episodic Memory:** Erfahrungen, Events, vergangene Situationen
- **Procedural Memory:** Wie man Dinge tut (Skills, Workflows)

Bisher haben wir alles gemischt. Das führt zu:
- Chaos bei der Suche
- Doppelte Informationen
- Keine klare Struktur

---

## 📊 AKTUELLER STAND

Unser Memory:
```
memory/
├── knowledge_graph.json    # Semantic (teilweise)
├── semantic_index.json    # Semantic
├── notes/
│   ├── fleeting/          # Roh, unstrukturiert
│   ├── permanent/         # Wichtige Notes
│   └── research/          # Recherchen
├── learnings/             # Gemischt
└── decisions/             # Gemischt
```

---

## 🏗️ NEUE STRUKTUR

```
memory/
├── semantic/                    # FAKTEN & WISSEN
│   ├── facts/                   # Harte Fakten
│   │   └── YYYY-MM-DD_fact.md
│   ├── concepts/                # Konzepte & Definitionen
│   │   └── concept_NAME.md
│   ├── knowledge_graph/          # KG Structure
│   │   └── kg_SCHEMA.md
│   └── indices/                # Such-Indizes
│       └── semantic_index.json
│
├── episodic/                    # ERFAHRUNGEN & EVENTS
│   ├── events/                 # Vergangene Events
│   │   └── YYYY-MM-DD_event.md
│   ├── reflections/             # Reflexionen (nach Fehlern)
│   │   └── YYYY-MM-DD_reflection.md
│   ├── evaluations/             # Self-Evaluations
│   │   └── YYYY-MM-DD_evaluation.md
│   └── patterns/                # Erkannte Patterns
│       └── PATTERN_NAME.md
│
├── procedural/                 # SKILLS & WORKFLOWS
│   ├── workflows/              # How-to's
│   │   └── workflow_NAME.md
│   ├── skills/                # Scripts & Tools
│   │   └── skill_NAME.md
│   └── procedures/            # Standard Procedures
│       └── procedure_NAME.md
│
├── daily/                     # TÄGLICHE NOTIZEN
│   └── YYYY-MM-DD.md
│
└── archive/                   # ARCHIV (altes Zeug)
    └── YYYY-MM.md
```

---

## 📝 TYP-DEFINITIONEN

### Semantic Memory (Fakten)
- **Was:** Wissen über die Welt, Fakten, Konzepte
- **Beispiele:** "API Keys rotieren", "Gateway läuft auf Port 18789"
- **Speichern:** In `concepts/` oder als KG entities
- **Abrufen:** Wenn ich Fakten brauche

### Episodic Memory (Erfahrungen)
- **Was:** Vergangene Events, Erfahrungen, Reflexionen
- **Beispiele:** "Gestern habe ich HEARTBEAT überladen", "Vor 2 Tagen war Gateway down"
- **Speichern:** In `events/`, `reflections/`, `evaluations/`
- **Abrufen:** Bei ähnlichen Situationen

### Procedural Memory (Skills)
- **Was:** Wie man Dinge tut, Workflows, Procedures
- **Beispiele:** "So erstelle ich ein Backup", "Security Audit läuft so"
- **Speichern:** In `workflows/`, `skills/`, `procedures/`
- **Abrufen:** Wenn ich etwas machen soll das ich schon mal gemacht habe

---

## 🛠️ MIGRATION

### Schritt 1: Aktuelle Files analysieren
```bash
ls memory/learnings/
ls memory/notes/fleeting/
ls memory/notes/permanent/
```

### Schritt 2: Kategorisieren
- Facts → semantic/
- Events → episodic/
- Workflows → procedural/

### Schritt 3: Neue Struktur erstellen
```bash
mkdir -p memory/{semantic/{facts,concepts,indices},episodic/{events,reflections,evaluations,patterns},procedural/{workflows,skills,procedures},daily,archive}
```

### Schritt 4: Files verschieben
```bash
mv memory/learnings/* reflection/  # wenn Learnings
mv memory/notes/permanent/* concepts/  # wenn Konzepte
```

---

## 📋 VERWENDUNG

### Semantic abfragen:
```bash
grep -r "concept" memory/semantic/concepts/
cat memory/semantic/knowledge_graph/kg_SCHEMA.md
```

### Episodic abfragen:
```bash
ls memory/episodic/reflections/
cat memory/episodic/events/YYYY-MM-DD_event.md
```

### Procedural abfragen:
```bash
cat memory/procedural/workflows/SECURITY_AUDIT_WORKFLOW.md
```

---

## 🎯 ZIEL

Bis alle Memory-Files in der richtigen Kategorie sind:
- **Semantic:** ~20% (Konzepte, Fakten)
- **Episodic:** ~30% (Erfahrungen, Reflexionen)
- **Procedural:** ~20% (Workflows, Skills)
- **Daily:** ~20% (Tägliche Notes)
- **Archive:** ~10% (Altes Zeug)

---

## 📅 TIMELINE

| Wann | Was |
|------|-----|
| Heute | Konzept dokumentiert |
| Diese Woche | Neue Struktur aufsetzen |
| Nächste Woche | Migration der bestehenden Files |

---

*Erlernt aus: MongoDB Agent Memory Guide + DeepLearning.AI Agent Memory Course*
