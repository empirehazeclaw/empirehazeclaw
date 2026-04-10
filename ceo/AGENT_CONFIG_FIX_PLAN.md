# Agent Configuration Fix — Rollback-Plan

*Erstellt: 2026-04-08 21:58 UTC*
*Backup: /home/clawbot/.openclaw/rollback/pre-agent-config-fix/openclaw.json*

---

## 📋 SITUATIONSANALYSE

### Problem 1: Fehlende Workspaces
| Agent | Workspace Status |
|-------|-----------------|
| CEO | ✅ /workspace/ceo |
| Security Officer | ✅ /workspace/security |
| Builder | ✅ /workspace/builder |
| Data Manager | ❌ Workspace fehlt |
| Research | ❌ Workspace fehlt |
| QC Officer | ❌ Workspace fehlt |

### Problem 2: Session Configuration
- `sessions: {}` ist leer
- Cross-agent communication via `sessions_send` → "forbidden"
- Agent Crons laufen als "isolated" (nicht persistent)

### Problem 3: Git Submodule Konflikt
- `examiner/`, `uni-examiner/`, `uni-curriculum/`, `uni-research/` sind Submodules
- Können nicht mit `git add` committed werden

---

## 🔄 ROLLBACK PUNKTE

| Phase | Rollback Datei |
|-------|---------------|
| Backup vor ANY | `/home/clawbot/.openclaw/rollback/pre-agent-config-fix/openclaw.json` |
| Nach Phase 1 | `/home/clawbot/.openclaw/rollback/phase1-workspaces/openclaw.json` |
| Nach Phase 2 | `/home/clawbot/.openclaw/rollback/phase2-session/openclaw.json` |

**Rollback Befehl:**
```bash
cp /home/clawbot/.openclaw/rollback/phaseX/openclaw.json /home/clawbot/.openclaw/openclaw.json
```

---

## 📊 PHASISCHER PLAN

### PHASE 1: Workspaces einrichten (SICHER)
**Risiko:** 🟢 NIEDRIG — Nur Dateien erstellen, keine Config-Änderungen

1. **Data Manager Workspace erstellen**
   ```
   /workspace/data/
   ├── SOUL.md
   ├── AGENTS.md
   ├── HEARTBEAT.md
   ├── IDENTITY.md
   ├── TOOLS.md
   ├── USER.md
   └── task_reports/
   ```

2. **Research Workspace erstellen**
   ```
   /workspace/research/
   ├── SOUL.md (existiert bereits)
   ├── AGENTS.md
   ├── HEARTBEAT.md
   ├── IDENTITY.md
   ├── TOOLS.md
   ├── USER.md
   └── task_reports/
   ```

3. **QC Officer Workspace erstellen**
   ```
   /workspace/qc/
   ├── SOUL.md
   ├── AGENTS.md
   ├── HEARTBEAT.md
   ├── IDENTITY.md
   ├── TOOLS.md
   ├── USER.md
   └── task_reports/
   ```

4. **Test:** GitHub Backup läuft durch, keine Config-Änderungen

**Rollback Phase 1:**
```bash
rm -rf /workspace/data /workspace/research /workspace/qc
```

---

### PHASE 2: openclaw.json Agent Config erweitern (MEDIUM)
**Risiko:** 🟡 MITTEL — Config-Änderung, kann System brechen

1. **Backup erstellen:**
   ```bash
   cp /home/clawbot/.openclaw/openclaw.json /home/clawbot/.openclaw/rollback/phase1-workspaces/openclaw.json
   ```

2. **Agents List erweitern mit Workspaces:**
   ```json
   {
     "id": "data_manager",
     "name": "Data Manager (CDO)",
     "workspace": "/home/clawbot/.openclaw/workspace/data",
     "sessionKey": "agent:data:telegram:direct:5392634979"
   },
   {
     "id": "research",
     "name": "Research Agent",
     "workspace": "/home/clawbot/.openclaw/workspace/research",
     "sessionKey": "agent:research:telegram:direct:5392634979"
   },
   {
     "id": "qc_officer",
     "name": "QC Officer",
     "workspace": "/home/clawbot/.openclaw/workspace/qc",
     "sessionKey": "agent:qc:telegram:direct:5392634979"
   }
   ```

3. **Test:** Gateway startet, Cron-Jobs laufen

**Rollback Phase 2:**
```bash
cp /home/clawbot/.openclaw/rollback/phase1-workspaces/openclaw.json /home/clawbot/.openclaw/openclaw.json
```

---

### PHASE 3: Session Config verbessern (HOCH)
**Risiko:** 🔴 HOCH — Kann Cross-Agent Communication brechen

1. **Backup erstellen**
2. **Session Config hinzufügen:**
   ```json
   "sessions": {
     "dmScope": "per-channel-peer",
     "visibility": "all"
   }
   ```
3. **Test:** `sessions_send` zu anderen Agents funktioniert

**Rollback Phase 3:**
```bash
cp /home/clawbot/.openclaw/rollback/phase2-session/openclaw.json /home/clawbot/.openclaw/openclaw.json
```

---

## ⚠️ VORAUSSETZUNGEN FÜR JEDE PHASE

| Phase | Voraussetzung |
|-------|---------------|
| Phase 1 | GitHub Backup läuft durch |
| Phase 2 | Gateway restartiert erfolgreich |
| Phase 3 | sessions_send funktioniert |

---

## 🧪 TEST-PROZEDUR NACH JEDER PHASE

### Phase 1 Tests:
```bash
# 1. Check workspaces existieren
ls -la /workspace/data /workspace/research /workspace/qc

# 2. GitHub Backup läuft
bash /home/clawbot/.openclaw/workspace/scripts/github_backup.sh

# 3. Gateway Status
openclaw gateway status
```

### Phase 2 Tests:
```bash
# 1. Gateway restart
systemctl --user restart openclaw-gateway

# 2. Gateway Status
openclaw gateway status

# 3. Cron Jobs listbar
openclaw cron list
```

### Phase 3 Tests:
```bash
# 1. Sessions list
openclaw sessions list

# 2. Test sessions_send (vom CEO)
# sessions_send an security agent
```

---

## 📝 COMMANDS FÜR ROLLBACK

```bash
# Rollback zu Backup (vor ANY changes)
cp /home/clawbot/.openclaw/rollback/pre-agent-config-fix/openclaw.json /home/clawbot/.openclaw/openclaw.json

# Rollback zu Phase 1
cp /home/clawbot/.openclaw/rollback/phase1-workspaces/openclaw.json /home/clawbot/.openclaw/openclaw.json

# Rollback zu Phase 2
cp /home/clawbot/.openclaw/rollback/phase2-session/openclaw.json /home/clawbot/.openclaw/openclaw.json

# Danach Gateway restart
systemctl --user restart openclaw-gateway
```

---

## 🎯 ERFOLGSKRITERIEN

| Phase | Kriterium |
|-------|-----------|
| Phase 1 | Alle 6 Agents haben Workspace mit SOUL.md |
| Phase 2 | Gateway startet, alle Cron Jobs laufen |
| Phase 3 | sessions_send zu allen Agents funktioniert |

---

*Zuletzt aktualisiert: 2026-04-08 21:58 UTC*
*Erstellt von: CEO Sir HazeClaw*