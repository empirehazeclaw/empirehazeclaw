# System Integration Plan — CEO Multi-Agent Architecture
**Erstellt:** 2026-04-16 | **Status:** In Evaluation

---

## 🎯 Ziel
Die CEO-Systeme (Learning Loop, KG, Capability Evolver, Memory Sync, Autonomy Supervisor) zu einem **koordiniertenMAS** (Multi-Agent System) verbinden, nicht nur isolierte Silos.

---

## 📊 IST-ZUSTAND (vor Integration)

| System | Data Source | Problem |
|--------|-------------|---------|
| Learning Loop | `data/learning_loop/` | Schreibt Patterns → KEIN anderes System liest sie |
| KG (core_ultralight) | `core_ultralight/memory/kg/` | 364 entities, 523 relations, **15 orphans** |
| KG (CEO) | `ceo/memory/kg/` | 354 entities, 516 relations, 0 orphans |
| Capability Evolver | `skills/capability-evolver/memory/` | Black Box, keine Sync mit KG oder Loop |
| Memory Sync | `memory/` | Läuft, aber kein defined output für andere Systeme |
| Autonomy Supervisor | `data/autonomy/` | State lokal, nicht geteilt |

**Kernproblem:** Jedes System hat seinen eigenen Datastore. Keine geteilte Wissensbasis.

---

## 🔬 BEST PRACTICES (aus Research)

### Von IBM Multi-Agent Collaboration:
1. **Shared Memory** — Agents müssen über shared memory kommunizieren
2. **Message Passing** — Definierte Kommunikationsprotokolle
3. **Role Assignment** — Klar definierte Rollen wer was tut
4. **Fault Tolerance** — Systeme dürfen nicht gegenseitig crashen

### Von LangGraph/Multi-Agent Frameworks:
1. **Single Source of Truth** — EINE zentrale Knowledge Base
2. **Dependency Graph** — Wer hängt von wem ab
3. **State Synchronization** — Regelmäßige Sync-Zyklen
4. **Conflict Resolution** — Bei widersprüchlichen Daten: newest wins oder human-in-loop

### Konkret für uns:
- **Single KG** statt zwei KG-Dateien
- **Learning Loop Output → KG Update** als fester Schritt
- **Capability Evolver** soll KG-Events als Signale nutzen
- **Memory Sync** als Hub für alle State-Änderungen

---

## 📋 PHASES

### Phase 1: KG Consolidation ✅ COMPLETED 2026-04-16
**Ziel:** Single Source of Truth für Knowledge
- [x] Backup beider KG-Dateien erstellen → `backups/integration_backup_20260416_185449/`
- [x] Orphan Relations in core_ultralight KG fixen (11 fixed, 12 deleted)
- [x] CEO KG mit core_ultralight KG gemergt (10 entities + 7 relations hinzugefügt)
- [x] Alle Scripts auf CEO KG-Pfad umgestellt → `ceo/memory/kg/`
- [x] Verify: alle Scripts lesen/schreiben gleiche KG

**Final State:**
- Entities: 364 | Relations: 516 | Orphans: 0 ✅
- Alle 20+ Scripts nutzen jetzt `ceo/memory/kg/knowledge_graph.json`

### Phase 2: Learning Loop → KG Integration ✅ COMPLETED 2026-04-16
**Ziel:** Learning Loop wird KG-Updater
- [x] Bridge script `learning_to_kg_sync.py` erstellt
  - Liest patterns und improvements aus Learning Loop
  - Fügt sie als KG-Entities hinzu (LearningPattern, Improvement types)
  - Erstellt Relations zwischen Loop und neuen Entities
  - State tracking (nur neue werden gesynct)
- [x] Erster Sync durchgeführt:
  - **18 Patterns** als LearningPattern entities
  - **50 Improvements** als Improvement entities
  - **68 Relations** hinzugefügt
- [x] Learning-Loop Hub-Entity erstellt
- [x] Cron Job erstellt: `Learning Loop → KG Sync` (10min nach jeder vollen Stunde)

**KG State nach Sync:**
- Entities: 364 → **432** (+68)
- Relations: 516 → **612** (+96)

**Nächster Schritt:** Capability Evolver soll KG-Änderungen als Signale nutzen (Phase 4)

### Phase 3: Cross-System Communication Layer ✅ COMPLETED 2026-04-16
**Ziel:** Definierte Protokolle für Agent-Kommunikation
- [x] Event Bus (`event_bus.py`) erstellt
  - JSONL-basiert mit Index
  - Event Types: `kg_update`, `integration_phase`, `system_heartbeat`, etc.
  - Pub/Sub für alle Systeme
- [x] Stagnation Detector (`stagnation_detector.py`) erstellt
  - Checkt: Evolver, Learning Loop, KG Growth, Event Diversity
  - Reportet nur bei Problemen (sonst silent)
- [x] Erste Events publiziert (4 Events)
- [x] Cron Job: `Stagnation Detector` alle 6h
- [x] Integration in `learning_to_kg_sync.py` (publiziert Events nach Sync)

**Event Bus State:**
- 4 Events, 2 Types (kg_update, integration_phase)
- Sources: system_integration, learning_to_kg_sync

**Cron Jobs hinzugefügt:**
- `Learning Loop → KG Sync` (hourly @10min)
- `Stagnation Detector` (every 6h)

### Phase 4: Capability Evolver Integration ✅ COMPLETED 2026-04-16
**Ziel:** Evolver nutzt echte System-Signale statt nur interne
- [x] Signal Bridge (`evolver_signal_bridge.py`) erstellt
  - Liest Event Bus, KG State, Learning Loop State
  - Generiert Signale basierend auf realen Systemdaten
  - `capability_gap` wenn KG neue Types hat
  - `evolution_stagnation_detected` wenn Gene sich wiederholen
  - `perf_bottleneck` wenn Learning Loop Score < 0.7
- [x] Stagnation Breaker (`evolver_stagnation_breaker.py`) erstellt
  - Trackt Gene-Selection History
  - Detektiert wenn gleiches Gene 3x+ gewählt
  - Empfiehlt/executed Strategy-Switch (innovate ↔ repair)
- [x] Smart Evolver Run Script (`run_smart_evolver.sh`) erstellt
  - Analysiert System State
  - Wählt Strategy basierend auf Stagnation
  - `repair` wenn stagniert, `innovate` sonst
  - Postet Results zum Event Bus
- [x] Cron Job: `Smart Evolver Run` täglich 03:00 UTC

**Stagnation Detection V2:**
```
Event Bus → stagnation_detector.py (alle 6h)
  ↓ Wenn stagniert
run_smart_evolver.sh (täglich 03:00)
  ↓ mit fresh signals
Capability Evolver → gene_gep_repair_from_errors (wenn stagniert)
```

### Phase 5: Monitoring & Validation ✅ COMPLETED 2026-04-16
**Ziel:** Sichtbarkeit über System-Gesundheit
- [x] Integration Dashboard (`integration_dashboard.py`)
  - Zeigt: KG Health, Event Bus Activity, System Connections, Cross-Reference Checks
  - Terminal-UI mit Farben
  - Schnell-Check Modus für Cron Jobs
- [x] Cross-Reference Check
  - Prüft ob alle Scripts gleiche KG nutzen (keine core_ultralight refs)
  - Prüft ob Event Bus aktiv ist
  - Prüft ob Learning Loop Sync State existiert
- [x] Cron Job: `Integration Health Check` (8:00 + 20:00 UTC)

**Dashboard Commands:**
```bash
python3 scripts/integration_dashboard.py          # Full dashboard
python3 scripts/integration_dashboard.py --check  # Quick health check
python3 scripts/integration_dashboard.py --kg     # KG only
python3 scripts/integration_dashboard.py --events # Event Bus only
```

---

## ⚖️ EVALUATION KRITERIEN

| Kriterium | Metrik | Ziel |
|-----------|--------|------|
| KG Konsistenz | Beide KG identisch | ✅ 100% |
| Orphan Relations | Anzahl | 0 |
| System-Sync | Learning Loop → KG writes | Nach jedem Run |
| Communication | Events pro Tag | ≥ 10 |
| Stagnation | Evolver wiederholt gleiche Gene | < 3x hintereinander |
| Latenz | Sync-Zeit zwischen Systemen | < 60s |

---

## 🚨 RISIKEN

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| KG Merge Data Loss | Mittel | Backup + Test-Read vor Merge |
| Script-Breaking (Pfade) | Hoch | Erst Test-Read, dann umstellen |
| Evolver in Stagnation | Hoch | Gene-Diversität erhöhen |
| Performance-Impact (Sync) | Niedrig | Async wo möglich |

---

## ✅ COMPLETION SUMMARY (2026-04-16)

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 1 | ✅ DONE | Single KG, 434 entities, 0 orphans, 20+ scripts migrated |
| Phase 2 | ✅ DONE | learning_to_kg_sync.py, 18 patterns + 50 improvements → KG |
| Phase 3 | ✅ DONE | Event Bus, Stagnation Detector, 6 events |
| Phase 4 | ✅ DONE | Signal Bridge, Stagnation Breaker, Smart Evolver |
| Phase 5 | ✅ DONE | Integration Dashboard, Health Check Cron |

**New Scripts Created:**
- `learning_to_kg_sync.py` — Bridge Learning Loop → KG
- `event_bus.py` — Cross-system event pub/sub
- `stagnation_detector.py` — Monitor stagnation patterns
- `evolver_signal_bridge.py` — Feed real signals to Evolver
- `evolver_stagnation_breaker.py` — Force gene diversity
- `run_smart_evolver.sh` — Smart Evolver orchestration
- `integration_dashboard.py` — Unified monitoring

**New Cron Jobs:**
- `Learning Loop → KG Sync` (hourly @10min)
- `Stagnation Detector` (every 6h)
- `Smart Evolver Run` (daily 03:00 UTC)
- `Integration Health Check` (8:00 + 20:00 UTC)

**Integration Architecture:**
```
Learning Loop
    ↓ (patterns.json, improvements.json)
learning_to_kg_sync.py
    ↓ (sync every hour)
CEO KG (central) ← EVENT BUS → Capability Evolver
    ↑                              ↓ (Signal Bridge)
evolver_signal_bridge.py    fresh signals
    ↑
event_bus.py ← stagnation_detector.py
```

---

## 📝 NOTIZEN

- Capability Evolver ist in Stagnation (gene_gep_innovate_from_opportunity 6x)
- Unsere "Systeme" sind eher Scripts als echte Agents — das ist okay für Phase 1
- Budget: kostenlos, keine neuen Tools

