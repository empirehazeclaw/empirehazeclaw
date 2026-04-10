# CHRONOLOGY.md — System-Evolution
**Stand:** 2026-04-10

---

## 📜 Geschichte: Von LCM zu EmpireHazeClaw

Dieses Dokument fasst die evolutionäre Entwicklung des Systems zusammen, damit eine neue KI die historische Tiefe versteht.

---

## 🔬 Phase 1: LCM Era (Frühjahr 2026)

| Zeit | Event |
|------|-------|
| 2026-02/03 | **LosslessClaw Manager (LCM)** installiert |
| 2026-02/03 | Erste Agenten: telegram-gpt-subagent, gpt-assistant |
| 2026-03 | Self-Healing, Capability Evolver aktiv |
| 2026-03 | 21 Agenten, 48 individuelle Scripts |
| 2026-03 | lcm.db als zentrale Datenbank |

### LCM-Probleme
- LCM Database (lcm.db) war 0 bytes → keine Tables
- Viele LCM-abhängige Scripts
- Komplexes, undokumentiertes System

---

## 🔄 Phase 2: Evakuierung & Neuanfang (2026-04-09/10)

| Zeit | Event |
|------|-------|
| 2026-04-09 | **Evakuierungs-Manifest Prompt** empfangen |
| 2026-04-09 | RBAC aktiviert, Safe Profiles erstellt |
| 2026-04-09 | OpenClaw v2026.4.9 installiert (CVE gepatcht) |
| 2026-04-09 | evening_capture cron (21:00 UTC) eingerichtet |
| 2026-04-10 | **LCM Altlasten entfernt** |

### Was wurde entfernt (LCM Evakuierung)
- `lcm.db` → gelöscht (0 bytes, keine Tables)
- `lossless-claw.bak/` → gelöscht (361KB)
- `lcm_memory_sync.py` → gelöscht
- `memory_cleanup.py` → gelöscht
- `lcm_wiki_sync.py` → gelöscht
- 3 LCM-Crons → disabled

### Was wurde behalten
- Knowledge Graph (157 entities, 4623 relations)
- Semantic Index (81 chunks)
- alle SOUL.md, learnings, insights
- evening_capture.py, nightly_dreaming.py (keine LCM-Abhängigkeit)

---

## 🏢 Phase 3: EmpireHazeClaw Flotte (Aktuell)

### Architektur
```
[USER] ([USER])
    └── [SYSTEM-ORCHESTRATOR] (System-Orchestrator)
            ├── Builder
            ├── Security Officer
            ├── Data Manager (CDO)
            ├── QC Officer
            ├── Research
            └── (Weitere Agenten)
```

### Aktuelle Crons
| Zeit | Agent | Session |
|------|-------|---------|
| 10:30 UTC | Security Officer | security-daily |
| 11:00 UTC | Data Manager | data-daily |
| 11:30 UTC | Research | research-daily |
| 15:00 UTC | Builder | builder-daily |
| 17:30 UTC | QC Officer | qc-daily |

### Wichtige System-Komponenten
| Komponente | Status | Pfad |
|------------|--------|------|
| Knowledge Graph | ✅ 157 entities | memory/knowledge_graph.json |
| Semantic Index | ✅ 81 chunks | memory/semantic_index.json |
| MEMORY.md | ✅ Zentral | memory/MEMORY.md |
| Evening Capture | ✅ Aktiv | scripts/evening_capture.py |
| Nightly Dreaming | ✅ Aktiv | system/nightly_dreaming.py |
| OpenClaw Dreaming | ✅ Aktiv | 02:00 UTC |

---

## 🎯 Lehren aus der Evolution

### LCM → OpenClaw
1. **Eigenständige DB ist riskant** → jetzt nur noch JSON + Dateien
2. **Zu viele Agenten** → 21 → 8 konsolidiert
3. **Zu viele Scripts** → 48 → wenige fokussierte
4. **Tool-Logik verankert** → durch abstrakte Beschreibungen ersetzt

### Für Version 2.0
- Knowledge Graph ist das Herzstück
- Keine Abhängigkeit von proprietären DBs
- Alle Scripts nutzen nur Stdlib
- Portable Pakete für Migration ready

---

*Erstellt: 2026-04-10 | Universal Memory Portability*
