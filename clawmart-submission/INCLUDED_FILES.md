# ClawMart Submission - Memory System Skill

## Enthaltene Dateien

### Haupt-Skill Dateien
```
memory-skill/
├── SKILL.md              # Vollständige technische Dokumentation
├── README.md             # Professionelle Übersicht (diese Datei)
├── config.json           # v3.1 Konfiguration
└── scripts/
    └── __init__.py       # Import-Datei für Agenten
```

### Beispiele & Screenshots
```
examples/
├── example-1-knowledge-graph.md     # PARA Struktur + Auto-Extraktion
├── example-2-memory-decay.md       # Decay Visualisierung
├── example-3-daily-notes-query.md  # Timeline + Query System
└── real-data/
    ├── knowledge_graph.json         # Echt-Beispiel: Wissensgraph
    └── 2026-03-05.md               # Echt-Beispiel: Tagesnotizen
```

### Marketplace Submission
```
├── clawmart-description.md  # Marketplace Beschreibung (DE, <200 Wörter)
└── README.md               # Haupt-README für Marketplace
```

---

## Wie zu verwenden

1. **Repository-Struktur kopieren:**
   ```
   cp -r memory-skill/ /dein/projekt/
   ```

2. **Memory System importieren:**
   ```python
   from scripts.memory import MemorySystem
   
   memory = MemorySystem("/workspace")
   memory.process_message("Deine Nachricht hier")
   ```

3. **Konfiguration anpassen:**
   ```json
   // config.json bearbeiten
   {
     "memory": {
       "decay_rate": 0.9,
       "auto_extraction": true
     }
   }
   ```

---

## Version

- **Memory System:** v3.1.0
- **ClawMart Submission:** 2026-03-05
