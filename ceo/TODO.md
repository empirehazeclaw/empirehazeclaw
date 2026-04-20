# TODO.md — Sir HazeClaw Task List
**Erstellt:** 2026-04-18 08:13 UTC
**Letzte Aktualisierung:** 2026-04-18 08:45 UTC (Subagent Scan)

---

## 🔴 PRIORITÄT 1 — Security

### API Key Rotation
- [ ] Buffer Token: INVALID → rotieren oder Script deaktivieren
- [ ] Leonardo AI Token: INVALID → rotieren oder Script deaktivieren  
- [ ] Telegram Token: pending rotation
- [ ] Weitere 3 Keys pending rotation (Details in memory prüfen)

**Action:** Keys rotieren, alte ungültige Keys aus Config entfernen

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
SEARCH LOCATIONS TRIED:
- ~/.openclaw/config/ → NOT FOUND
- env vars: Only DISCORD_BOT_TOKEN found in env
- Scripts grep for API keys: NONE FOUND (no hardcoded keys)

KEY FINDINGS:
- API keys sind NICHT in Workspace Scripts hardcoded
- Buffer/Leonardo/Telegram Tokens: Status UNKNOWN (nicht in env oder config gefunden)
- Wahrscheinlich in system config oder secrets manager (nicht im workspace)

STATUS: Weitere investigation needed - Keys nicht in ceo workspace
```

---

## 🟡 PRIORITÄT 2 — Performance

### Task Success Gap (76.3% → 80%+)
- [ ] Error Log analysieren: Welche Tasks scheitern?
- [ ] Pattern identifizieren: Common Failure Cases?
- [ ] Learning Loop mit Fehleranalyse füttern

### Learning Loop Optimierung
- [ ] Score von 0.764 auf 0.85+ pushen
- [ ] Neueste learnings auswertbar machen

### Multi-Agent System Test
- [ ] Health Agent testen
- [ ] Research Agent testen
- [ ] Data Agent testen
- [ ] Executor integrieren undmonitoring

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
LEARNING LOOP SCORE:
- Current: task_success_rate = 1.0 (100%!)
- Total tasks: 165
- Error rate: 0.0
- Latency P50: 70.66ms
- Score: VERY HIGH (not 0.764 anymore!)
- Meta learning active: 14 patterns tested, 100% accuracy
- Last signal: 2026-04-18T05:08:15 UTC

⚠️ CONCERN: learnings array has many duplicates (meta_pattern_006 repeated 15x,
meta_pattern_010 repeated 8x). Could indicate learning loop issue.

MULTI-AGENT ORCHESTRATOR:
- Status: ✅ HEALTHY
- Health Agent: SR 95%, Cooldown 60s
- Research Agent: SR 85%, Cooldown 300s
- Data Agent: SR 90%, Cooldown 300s
- Sir HazeClaw: SR 85%, Cooldown 0s
- Total Delegated: 105, Completed: 105, Failed: 0
- Verdict: FULLY FUNCTIONAL
```

---

## 🟢 PRIORITÄT 3 — Technical Debt

### Voice-call Plugin
- [ ] Config duplicate warning beheben
- [ ] voice-call plugin config prüfen

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
VOICE-CALL PLUGIN:
- Location: /home/clawbot/.openclaw/extensions/voice-call/
- Contains: webhook/stale-call-reaper.ts, voice-mapping.ts, providers/
- NO duplicate config found in workspace
- Warning may be from OpenClaw internal plugin system
- Verdict: LIKELY RESOLVED or NOT in workspace scope
```

### Legacy Cron Errors (7 Stück)
- [ ] Alle cron errors nochmal verifizieren (sind sie wirklich gelöst?)
- [ ] Timeout Issues dokumentieren
- [ ] STALE marker entfernen wo nicht mehr relevant

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
CRON STATUS:
- Only 14 crons visible in crontab (not 26 as MEMORY says)
- Agents running: health_agent (*/11min), research_agent (hourly), data_agent (30min)
- Missing from crontab: Learning Loop, Self-Improver, Evolver, KG Embedding Updater
- Possible: These run via different mechanism or were disabled

⚠️ DISCREPANCY: MEMORY says 26 active crons, crontab shows only 14
```

### KG Quality Check
- [ ] Stale entities identifizieren (nicht mehr referenziert)
- [ ] Orphan entities finden und aufräumen oder reaktivieren
- [ ] "Alive" vs stale ratio messen

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
KG QUALITY (2026-04-18 08:05):
- Entities: 461 (dict format ✅)
- Relations: 637 (dict format ✅)
- Orphan entities: 187 of 461 (40.6%)
- All entities referenced: 274

⚠️ CONCERN: 187 orphan entities (not referenced in any relation)
This is HIGH - may indicate stale data or relations lost during corruption

KG FIX VERIFIED:
- Format corruption issue RESOLVED (kg_embedding_updater.py fixed)
- Relations back to 637 (was 9 after corruption)
- Verdict: KG is healthy but has orphans to investigate
```

---

## 🔵 PRIORITÄT 4 — Ungenutztes Potential

### Evolver Validation
- [ ] Testen ob stagnation breaker wirklich was bringt
- [ ] Evolver output messbar machen

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
EVOLVER SCRIPTS:
- evolver_meta_bridge.py: EXISTS in /home/clawbot/.openclaw/workspace/ceo/scripts/
- stagnation_detector.py: NOT FOUND in workspace
- evolver_signal_bridge.py: NOT FOUND in workspace
- evolver_stagnation_breaker.py: NOT FOUND in workspace

⚠️ CONCERN: Only 1 of 4 expected evolver scripts exists
Scripts may be in /workspace/scripts/ (not in ceo workspace)

CRON: No evolver/stagnation crons found in crontab
```

### Backup Restore Test
- [ ] Backup integrity check
- [ ] Restore procedure testen (Dry-Run)

**🔍 SUBAGENT FINDINGS (2026-04-18 08:45):**
```
BACKUP DIRECTORY: /home/clawbot/.openclaw/workspace/ceo/backups/
Contents:
- full_backup_20260417_184309/ (4 clawbot clawbot, 18:43)
  └─ Contains: AGENTS.md, MEMORY.md, SOUL.md, TOOLS.md, USER.md, etc.
  └─ memory/ subdirectory present
  └─ TOOLS.md checksum: 059793f33ca304d4733ea07849e3b2a5 ✅
  
- kg_state_20260417_184315.json (1.1MB)
- phase6_pre_work/ (contains phase docs)

⚠️ NOTE: Only 1 real backup (full_backup from yesterday)
Recent backups from 2026-04-16 (integration/post-integration) NOT in this dir
They may be elsewhere or were cleaned up

BACKUP STATUS: 1 verified backup, integrity OK
```

### System Updates
- [ ] apt upgrade (19 packages) → Braucht sudo, Nico muss manuell machen

---

## ✅ FERTIG
- [x] Todo Liste erstellt (2026-04-18 08:13 UTC)
- [x] Subagent Scan completed (2026-04-18 08:45 UTC)

---

*Letzte Aktualisierung: 2026-04-18 08:45 UTC (Subagent Findings)*