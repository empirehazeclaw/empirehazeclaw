# System Deep Dive — Learnings & Master Execution Plan
**Datum:** 2026-04-20 15:47 UTC
**Autor:** Sir HazeClaw (Basierend auf 10 Subagent-Analysen)

---

## 📚 WAS WIR GELERNT HABEN

### 1. CRON SYSTEM

**Problem:** 7/8 User Crontab-Einträge zeigen auf nicht-existente Scripts
- `sqlite_vacuum.sh` — Script gelöscht
- `session_cleanup.py` — nicht gefunden
- `kg_auto_populate.py` — Pfad falsch (`memory/scripts/` existiert nicht)
- `semantic_search.py` — nicht gefunden
- `github_backup.sh` — nicht gefunden
- `weekly_review_zettel.py` — nicht gefunden

**Dual-System-Problem:** Backup/Maintenance Tasks existieren BOTH in User Crontab UND OpenClaw — beide kaputt.

**Insight:** OpenClaw's interner Scheduler ist besser — User Crontab ist Legacy-Refresh der nicht mehr gepflegt wird.

---

### 2. MEMORY SYSTEM

**SQLite DBs:**
| DB | Größe | Problem |
|----|-------|---------|
| `main.sqlite` | 372 MB | 86% embeddings (320MB+), MEMORY.md allein 4MB |
| `ceo.sqlite` | 84 MB | ✅ Effizient, weniger Duplikate |
| `data.sqlite` | 72 KB | 🔴 **LEER** — 0 rows, komplett ungenutzt |
| `events.sqlite` | 20 KB | 🔴 **LEER** — 1 test event, ungenutzt |

**QMD:**
- Index 20MB, FTS funktioniert, vector via vec0
- Query Expansion Model war in `.ipull` — unvollständiger Download, aber BM25 fallback funktioniert

**Memory Struktur:**
- `short-term-recall.json` ist LEER (`entries: {}`)
- Backups zeigen Datenverlust von 3.1MB → 533KB über 5 Tage
- 118 recall events geloggt

---

### 3. KNOWLEDGE GRAPH

**Statistik:**
- 307 entities, 646 relations
- Orphan Rate: 8.1% (25 entities)
- Avg connectedness: 4.21/entity

**Probleme:**
- **80 junk entities** — auto-extracted garbage mit `Source: [internal-path]`
- **25 orphan research entities** — `research_*` Typ, nie connected
- **4 stale entities** — `last_accessed: ""` seit Apr 10
- **`kg_auto_populate.py` CRASHT** — Script nicht gefunden (File not found × 10)

---

### 4. DREAMING / SHORT-TERM RECALL

**Aktueller Status:**
- `short-term-recall.json` = **LEER**
- 6 Backups vorhanden (täglich ~06:00 UTC)
- Session Corpus ~1.1MB über 11 Tage
- `phase-signals.json` tracked lightHits vs remHits

**Kritisch:** Backup-Größe fiel von 3.1MB (Apr 15) → 533KB (Apr 20). Möglicher Datenverlust oder bewusste Reduktion?

---

### 5. SKILLS SYSTEM

**Inventar:** 29 Skills
| Status | Count |
|--------|-------|
| ✅ Active | 8 |
| 🟡 Medium | 12 |
| 🔴 Unused | 4 |
| ❌ Missing | 1 (Ralph Loop existiert nicht als Skill) |

**Probleme:**
- `SKILLS_INDEX.md` ist veraltet — listet nur 17, tatsächlich 29 vorhanden
- `ralph_loop` in TOOLS.md dokumentiert aber Verzeichnis fehlt
- `_library` ist deprecated
- Clawhub fast ungenutzt

---

### 6. AGENT SYSTEM

**Architektur:** CEO → Orchestrator → Executor → Specialized Agents

| Agent | SR | Funktion |
|-------|-----|----------|
| `health_agent` | 95% | 6-Layer Health + Self-healing |
| `data_agent` | 90% | KG quality, script health, doc audit |
| `research_agent` | 85% | arXiv, HN, Brave API |
| `sir_hazeclaw` | 85% | Orchestrator |

**Queue-System:** `orchestrator_state.json`, 60s timeout, task types: health_check, research, learning_sync, data_analysis

---

### 7. LEARNING LOOP

**Aktueller Status:**
- Iteration 213, Score **0.765** (target 0.80)
- LR: Adaptive (30% Reduktion bei Plateau, floor 0.005)
- Plateau Detection: <1% Variation triggert LR-Reduktion + novelty boost
- Validation Gate v2: 2/3 tests, ±0.1% error threshold
- Cross-Pattern: 50 hits, 0 misses ✅

**Problem:** Score stuck bei 0.765 — "Reduce KG orphans" Verbesserungen scheitern wiederholt.

**Meta Learning:** `task_embeddings.json` = 2.06 MB (6 tasks × 384-dim vectors)

**Ralph Loop:** Stop hook sucht `<promise>COMPLETE</promise>`, Learnings in `memory/ralph_learnings.md`

---

### 8. CAPABILITY & EVOLVER

**Capability Probe (02:00 UTC):**
- Checkt KG + Learning Loop + Mini-Benchmark
- Generiert synthetische Signale wenn alles green
- Thresholds: ORPHAN 40%, GROWTH 5%, SCORE 0.6

**Evolver System:**
- Node.js, GEP Protocol (Gene/Capsule/Event)
- 4 Gene Typen: repair, innovate, optimize, auto
- Signal Bridge: Event Bus → stagnation signals
- Stagnation Breaker: Erzwingt Gene diversity

**Phase 5 Self-Modification:** `learning_rule_modifier.py` — ADVANCED, Disabled für Safety

---

### 9. WORKSPACE ORGANIZATION

**Erkenntnisse:**
- 62 orphan root-level scripts (alle vom 2026-03-28, keine cron references)
- 7 learning_loop variants (nur v3 aktiv)
- ~15 near-empty directories
- Nur 6 Scripts werden tatsächlich via cron genutzt
- `backups/` enthält 283MB daily tar.gz + ceo_backup

**Quick Wins:**
1. 62 orphan root scripts löschen
2. `core_ultralight/` + `TEMPORARY/` entfernen
3. Nur `learning_loop_v3.py` behalten

---

## 🔍 BEST PRACTICES RESEARCH

> **Hinweis:** Web Search nicht verfügbar (Brave API Key kompromittiert). Praktische Best Practices basierend auf System-Know-how:

### Cron System Best Practices
1. **Single Source of Truth** — Entweder User Crontab ODER systemd timers, nicht beides
2. **Health Monitoring** — Jeder Cron braucht Log-File + Error-Tracking
3. **Idempotenz** — Crons müssen mehrfach laufen können ohne Schaden
4. **Dead Script Detection** — Automatisiertes Checken auf fehlende Scripts

### Memory System Best Practices
1. **Embedding Deduplication** — Bei 86% Embedding-Anteil braucht man dedup strategy
2. **TTL für alte embeddings** — Nicht alle ewig behalten
3. **Separate hot/warm/cold** — Aktuelle Sessions vs. Archiv
4. **Regular vacuum** — Nicht warten bis DB bloated

### Knowledge Graph Best Practices
1. **Orphan < 10%** — 8.1% ist akzeptabel aber sollte监控 werden
2. **Entity lifecycle** — created, accessed, stale Flags
3. **Junk cleanup** — Auto-extract noise sollte gefiltert werden
4. **Periodic re-synthesis** — Nicht nur wachsen lassen, auch konsolidieren

### Learning System Best Practices
1. **Plateau Detection** — Multi-Signal (score + entropy + novelty)
2. **LR Scheduling** — Warm restarts, cosine annealing
3. **Validation before commit** — Never improve on unvalidated metrics
4. **Diversity maintenance** — Gene pool diversity ist kritisch gegen stagnation

### Workspace Best Practices
1. **Single level of abstraction** — Nicht 5 Levels deep
2. **Explicit ownership** — Jeder Ordner hat einen "owner" (System)
3. **Dead inventory quarterly** — Einmal pro Quartal aufräumen
4. **Script count metric** — Nicht mehr Scripts als man tracken kann

---

## 📋 MASTER EXECUTION PLAN

### Phase 1: CRITICAL FIXES (Diese Woche)

| # | Action | Effort | Impact | Risk |
|---|--------|--------|--------|------|
| 1.1 | User Crontab aufräumen — 7 kaputte Entries löschen | LOW | HIGH | LOW |
| 1.2 | `kg_auto_populate.py` Cron deaktivieren oder Script wiederherstellen | MEDIUM | HIGH | MEDIUM |
| 1.3 | `memory_kg_cleaner.py` ausführen (80 junk entities) | LOW | MEDIUM | LOW |
| 1.4 | Orphan research entities fixen/entfernen (25 entities) | MEDIUM | MEDIUM | MEDIUM |

### Phase 2: SYSTEM OPTIMIZATION (Diese Woche)

| # | Action | Effort | Impact | Risk |
|---|--------|--------|--------|------|
| 2.1 | `data.sqlite` + `events.sqlite` entfernen (leer + ungenutzt) | LOW | LOW | LOW |
| 2.2 | `short-term-recall.json` analysieren — warum leer? | MEDIUM | HIGH | MEDIUM |
| 2.3 | 62 orphan root scripts löschen | LOW | MEDIUM | LOW |
| 2.4 | `core_ultralight/` + `TEMPORARY/` entfernen | LOW | LOW | LOW |
| 2.5 | Nur `learning_loop_v3.py` behalten (7 variants → 1) | LOW | LOW | LOW |

### Phase 3: DOCUMENTATION UPDATE (Nächste Woche)

| # | Action | Effort | Impact | Risk |
|---|--------|--------|--------|------|
| 3.1 | `SYSTEM_ARCHITECTURE.md` updaten (Event Bus, Dashboard, Cleanup) | MEDIUM | HIGH | LOW |
| 3.2 | `SKILLS_INDEX.md` aktualisieren (29 skills, nicht 17) | MEDIUM | MEDIUM | LOW |
| 3.3 | `docs/ANALYSIS/` archivieren (3 alte files) | LOW | LOW | LOW |
| 3.4 | `docs/README.md` fixen (patterns/ reference) | LOW | LOW | LOW |

### Phase 4: LEARNING LOOP OPTIMIZATION (Laufend)

| # | Action | Effort | Impact | Risk |
|---|--------|--------|--------|------|
| 4.1 | Score 0.765 → 0.80 — Alternative patterns für orphan reduction | HIGH | HIGH | MEDIUM |
| 4.2 | Meta Learning efficiency — `task_embeddings.json` wächst ewig | MEDIUM | MEDIUM | MEDIUM |
| 4.3 | Ralph Loop adapter testen + dokumentieren | MEDIUM | MEDIUM | MEDIUM |

### Phase 5: ARCHITECTURE IMPROVEMENTS (Diesen Monat)

| # | Action | Effort | Impact | Risk |
|---|--------|--------|--------|------|
| 5.1 | OpenClaw Scheduler als single source für Crons | MEDIUM | HIGH | MEDIUM |
| 5.2 | Event Bus monitoring verbessern (1040 events, aber 0 genutzt?) | HIGH | HIGH | MEDIUM |
| 5.3 | Agent success rate monitoring (95/90/85% → Ziel 98%+) | MEDIUM | HIGH | MEDIUM |
| 5.4 | Backup strategy konsolidieren (2GB+ Backups, Retention?) | MEDIUM | MEDIUM | MEDIUM |

---

## 🎯 PRIORITY SEQUENCE

```
WOCHE 1 (Diese Woche):
├── Tag 1: User Crontab aufräumen + kg_auto_populate fix
├── Tag 2: Junk KG cleanup + orphan research entities
├── Tag 3: Workspace cleanup (62 scripts + leere dirs)
└── Tag 4-5: Documentation update

WOCHE 2:
├── Learning Loop optimization (plateau escape)
├── Event Bus Integration testen
└── Skills registry fix

WOCHE 3-4:
├── Backup strategy implementieren
├── Memory embedding deduplication
└── Ralph Loop full integration
```

---

## 📊 SUCCESS METRICS

| System | Current | Target | Date |
|--------|---------|--------|------|
| User Crontab Health | 12% | 100% | Woche 1 |
| KG Orphan Rate | 8.1% | <5% | Woche 2 |
| Learning Score | 0.765 | 0.80 | Woche 3 |
| Skills Index Accuracy | 58% (17/29) | 100% | Woche 1 |
| Workspace Orphan Scripts | 62 | 0 | Woche 1 |
| Documentation Freshness | 9 days stale | <3 days | Woche 2 |

---

## ⚠️ BLOCKERS

1. **Brave API Key** — Web Search down, muss rotiert werden
2. **`short-term-recall.json` leer** — Möglicher Datenverlust oder Bug
3. **Mad-Dog Evolver Controller** — Im error state seit unbestimmter Zeit
4. **Ralph Loop Skill** — Existiert nicht obwohl dokumentiert

---

## 📁 OUTPUT FILES VON ANALYSEN

| File | Beschreibung |
|------|-------------|
| `/tmp/cron_analysis.md` | Vollständige Cron-Inventur |
| `/tmp/memory_analysis.md` | Memory System Deep Dive |
| `/tmp/kg_analysis.md` | KG Analyse + orphan report |
| `/tmp/dreaming_analysis.md` | Dreaming System |
| `/tmp/skills_analysis.md` | Skills Inventar |
| `/tmp/agent_analysis.md` | Agent System Architektur |
| `/tmp/learning_analysis.md` | Learning Loop Status |
| `/tmp/evolver_analysis.md` | Capability/Evolver |
| `/tmp/architecture_analysis.md` | Documentation Audit |
| `/tmp/workspace_analysis.md` | Workspace Organization |

---

**Erstellt:** 2026-04-20 15:47 UTC
**Version:** 1.0
**Status:** Ready for Execution