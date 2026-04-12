# 📋 WORKSPACE RESTRUCTURING PLAN
## Saubere Organisation für Sir HazeClaw System
**Erstellt:** 2026-04-12 17:15 UTC
**Status:** PLANUNG

---

## 🔍 IST-ZUSTAND ANALYSE

### Zahlen & Fakten
| Kategorie | Anzahl | Problem |
|----------|--------|---------|
| MD-Dateien (Workspace) | **320** | Zu viele, verstreut |
| Python Scripts | **198** | Doppelte Funktionen |
| CEO-Ordner Dateien | **63** | Chaos durch Audio-Files |
| Root-Ordner Files | **~100** | Keine klare Struktur |
| Docs-Ordner | 20+ | Redundante Analyse-Dateien |

### 🗂️ Aktuelle Struktur (Problem)
```
workspace/
├── *.md (32+ root files)          ❌ Keine Übersicht
├── scripts/ (66 scripts)           ⚠️ Mix aus aktiv/archiv
├── ceo/                           ❌ Audio-Files, memory, logs gemischt
│   ├── audio*.json/srt/tsv/txt     ❌ ~40 Audio-Dateien
│   ├── file_*.json                ❌ Transkript-Reste
│   ├── memory/                    ⚠️ Sollte TEMPORARY sein
│   ├── docs/                      ✅ Gut sortiert
│   └── logs/                      ⚠️ Sollte TEMPORARY sein
├── docs/ANALYSIS/                  ❌ Redundante Dateien
├── docs/SCRIPTS/                   ❌ Sollte auf scripts/ zeigen
├── archive/                        ⚠️ Veraltet
├── skills/                         ⚠️ Viele ungenutzte Skills
└── memory/                         ⚠️ Sollte TEMPORARY sein
```

### 😅 Chaos-Quelle
- **Unkontrollierte Inputs** (audio files, transkripte, logs)
- **Keine klaren Grenzen** zwischen TEMPORARY und PERSISTENT
- **Viele "einmal" Projekte** die nie aufgeräumt wurden
- **Doppelte Dokumentation** (MEMORY.md + memory/*.md + HEARTBEAT.md)

---

## 🎯 ZIEL-STRUKTUR (Best Practice 2026)

### Principles from Research
1. **Modular Architecture** - Klare Trennung, lose Kopplung
2. **Tiered Memory** - Short-term (session) vs Long-term (persistent)
3. **Centralized Context** - Ein "Universal Context" für alle Agents
4. **Clear Boundaries** - TEMPORARY vs PERSISTENT Storage
5. **Human-in-the-loop** - Governance und klare Regeln

### ✅ Neue Struktur
```
workspace/
├── CONFIG/                    🆕 Zentrales Config-Verzeichnis
│   ├── openclaw.json         (Reference only!)
│   ├── AGENTS.md             (Identity & Soul)
│   ├── USER.md               (User context)
│   ├── TOOLS.md              (Local tools)
│   └── secrets.env           (Nicht in Git!)
│
├── CORE/                      🆕 System-Kern (minimal)
│   ├── MEMORY.md             (Curated long-term memory)
│   ├── HEARTBEAT.md          (Daily status)
│   └── CAPABILITY_EVOLVER/  (Self-improvement)
│
├── SCRIPTS/                   🆕 Konsolidierte Scripts
│   ├── automation/           (Cron-triggered)
│   ├── analysis/             (Auditing & monitoring)
│   ├── self_healing/         (Error recovery)
│   └── tools/                (Hilfs-Scripts)
│
├── DOCS/                      🆕 Strukturierte Dokumentation
│   ├── ARCHITECTURE.md        (System design)
│   ├── SCRIPTS.md            (Script inventory)
│   ├── CRONS.md              (Cron inventory)
│   ├── PATTERNS.md           (Best practices)
│   └── KNOWLEDGE/            (KG documentation)
│
├── TEMPORARY/                 🆕 Echte Temporary Files
│   ├── logs/                 (Session logs - auto-cleanup)
│   ├── memory/               (Daily notes - 30 Tage Retention)
│   ├── task_reports/         (Cron reports - 7 Tage Retention)
│   └── audio/                (Transkripte - 7 Tage Retention)
│
├── ARCHIVE/                   (Inaktive Projekte)
│   └── [alt, ungenutzt]
│
├── SKILLS/                    (OpenClaw Skills - minimal halten)
│
└── README.md                  (Navigation)
```

### Key Changes
| Was | Warum |
|-----|-------|
| **CEO/audio* → TEMPORARY/audio** | Audio-Files sind transient, nicht persistent |
| **CEO/memory/ → TEMPORARY/** | Daily notes sind temp, nur curierte Memories sind persistent |
| **Root *.md → DOCS/** | Klare Trennung Code vs Dokumentation |
| **scripts/ → SCRIPTS/** | Konsolidierung, keine Duplikate |
| **Neue CONFIG/** | Identity, User, Tools an einem Ort |

---

## 📋 RESTRUCTURING PHASEN

### Phase 1: TEMPORARY Struktur schaffen
- [ ] TEMPORARY/ Ordner erstellen
- [ ] Logs, memory, task_reports, audio verschieben
- [ ] Auto-Cleanup Cron für TEMPORARY/

### Phase 2: KONSOLIDIERUNG SCRIPTS
- [ ] Scripts analysieren (Duplikate finden)
- [ ] Aktive vs Archive Scripts trennen
- [ ] scripts/ → SCRIPTS/ mit Unterordnern
- [ ] scripts_index.md aktualisieren

### Phase 3: DOKUMENTATION AUFRÄUMEN
- [ ] Root *.md nach DOCS/ verschieben
- [ ] Redundante ANALYSEN löschen
- [ ] DOCS/README.md erstellen

### Phase 4: MEMORY SYSTEM FIXEN
- [ ] MEMORY.md curieren (das ist persistent!)
- [ ] HEARTBEAT.md behalten (tägliches Status)
- [ ] memory/YYYY-MM-DD als TEMPORARY markieren
- [ ] consolidate memory/ → MEMORY.md regelmäßig

### Phase 5: CEO BEREINIGEN
- [ ] Audio-Files in TEMPORARY/audio/
- [ ] Alte file_*.json löschen
- [ ] docs/ bleibt,logs/ → TEMPORARY/

### Phase 6: CLEANUP & VALIDIERUNG
- [ ] Git commit für jede Phase
- [ ] Tests laufen lassen
- [ ] README.md schreiben
- [ ] Pre-commit Hook für TEMPORARY/

---

## 🛠️ AUTO-CLEANUP IMPLEMENTIERUNG

### Retention Policy
```bash
# TEMPORARY Auto-Cleanup
- logs/: 14 Tage
- memory/: 30 Tage  
- task_reports/: 7 Tage
- audio/: 7 Tage (od. nach Whisper-Analyse)
```

### Cleanup Script
```python
#!/usr/bin/env python3
"""
cleanup_temporary.py - Auto-cleanup for TEMPORARY directory
Sir HazeClaw - 2026-04-12
"""

import shutil
from pathlib import Path
from datetime import datetime, timedelta

TEMPORARY = Path("/home/clawbot/.openclaw/workspace/TEMPORARY")
RETENTION = {
    "logs": 14,
    "memory": 30,
    "task_reports": 7,
    "audio": 7
}

def cleanup_folder(folder: Path, days: int):
    """Delete folders older than `days`."""
    cutoff = datetime.now() - timedelta(days=days)
    for item in folder.iterdir():
        if item.is_file():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            if mtime < cutoff:
                item.unlink()
                print(f"🗑️  Deleted: {item}")
```

---

## 📊 ZEITPLAN

| Phase | Aufwand | Ergebnis |
|-------|---------|----------|
| Phase 1 | 30 min | TEMPORARY Struktur |
| Phase 2 | 60 min | Saubere Scripts |
| Phase 3 | 30 min | DOCS sortiert |
| Phase 4 | 45 min | Memory konsolidiert |
| Phase 5 | 30 min | CEO aufgeräumt |
| Phase 6 | 60 min | Getestet & dokumentiert |

**Total: ~4-5 Stunden**

---

## 🎯 ERFOLGS-METRIKEN

Nach Restrukturierung:
- [ ] < 20 Dateien im Root
- [ ] < 5 Unterordner im Root
- [ ] 0 redundante MD-Dateien
- [ ] Klare TEMPORARY/ vs PERSISTENT Trennung
- [ ] Auto-Cleanup läuft
- [ ] README.md navigierbar

---

## 🔗 RESEARCH QUELLEN

1. **Modular Architecture**: https://onereach.ai/blog/best-practices-for-ai-agent-implementations/
2. **Tiered Memory**: https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/
3. **Centralized Context**: https://sendbridge.com/technology/why-a-unified-ai-workspace-is-the-key-to-scaling-digital-operations-in-2026
4. **AI Agent Memory**: https://vectorize.io/articles/best-ai-agent-memory-systems
5. **Shared Memory Layer**: https://www.roborhythms.com/how-to-stop-ai-agents-repeating-work-2026/

---
*Erstellt basierend auf Web Research + Current State Analysis*
*Sir HazeClaw - Continuous Improvement 🚀*
