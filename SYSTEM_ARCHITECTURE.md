# System Architecture Documentation — 2026-04-11

**Erstellt:** 2026-04-11 11:10 UTC
**Zweck:** Klare Dokumentation der Systemstruktur + Plan für Vereinfachung

---

## 📁 SYSTEMÜBERSICHT

### Wo sind Konfigurationen?

| Datei/Ort |Zweck | Enthält |
|-----------|------|---------|
| `~/.openclaw/openclaw.json` | Haupt-Config | Models, Providers, Agents, Defaults |
| `~/.openclaw/agents/ceo/` | CEO Agent | Sessions, Agent-spezifische Config |
| `~/.openclaw/secrets/secrets.env` | **API Keys** | MINIMAX, OPENROUTER, GitHub, etc. ⚠️ |
| `~/.openclaw/workspace/` | Arbeitsbereich | Alle Scripts, Skills, Docs, Memory |
| Environment Variables | API Keys | Wird aus secrets.env geladen |

### ⚠️ WICHTIG: Secrets Location

**API Keys sind in:** `/home/clawbot/.openclaw/secrets/secrets.env`
- **MINIMAX_API_KEY** ✅ (System läuft damit)
- **OPENROUTER_API_KEY** ✅ (auch vorhanden)
- **Viele andere Keys** (GitHub, Google, etc.)

**NIE in openclaw.json committed!** (nur redacted)

### OpenClaw Secrets Management

**Wichtig:** OpenClaw unterstützt "SecretRefs" - API Keys müssen NICHT plaintext in Config sein.

**Aktueller Status:** 
- Keys in `secrets/secrets.env`
- System läuft mit MINIMAX_API_KEY
- Kein externes Vault (1Password, HashiCorp, etc.)

---

## 📊 WORKSPACE STRUKTUR (Aktuell)

```
/home/clawbot/.openclaw/workspace/
├── scripts/                    # 80+ Python Scripts
│   ├── learning_*.py          # Learning Loop Scripts
│   ├── *_tracker.py           # Tracking Scripts
│   ├── *_check.py             # Health Checks
│   ├── *_cleanup.py           # Cleanup Scripts
│   └── *.py                   # Andere
├── skills/                     # Skills (16+ Ordner)
│   ├── self-improvement/
│   ├── system-manager/
│   ├── research/
│   └── .../
├── memory/                      # Short-Term Memory
│   ├── 2026-04-*.md          # Tägliche Files
│   └── shared/
├── core_ultralight/
│   └── memory/
│       └── knowledge_graph.json  # KG (Long-Term)
├── docs/                        # Dokumentation
├── data/                        # Logs, States
│   ├── token_log.json
│   ├── learning_coordinator.json
│   └── tool_usage_analytics.json
├── ceo/                         # CEO Workspace
│   ├── HEARTBEAT.md
│   ├── IMPROVEMENT_TODO.md
│   ├── LEARNING_LOOP_ANALYSE.md
│   └── ...
└── ...                          # Viele andere Files
```

---

## ⚠️ PROBLEME (Current State)

### 1. Zu viele Files (>100 im Root)
Viele alte/dead Files die nicht mehr gebraucht werden:
- `AGENT_*.md` (Consolidation, ROI, Inventory) - veraltet
- `CLAW_*.md` - unclear purpose
- `DREAMS.md`, `FINAL_STATE.md` - unclear

### 2. Kein klares Naming Convention
- Manche Files: `Upper_Case.md`
- Manche: `lowercase.py`
- Inkonsistent

### 3. Scripts verteilt
- `scripts/` hat 80+ Files
- Nicht klar welche aktiv/inaktiv

### 4. Memory Fragmentation
- `memory/` = täglich
- `core_ultralight/memory/knowledge_graph.json` = KG
- Nicht klar wann was genutzt

---

## 📋 SYSTEMKLARHEITS-PLAN

### Phase 1: Inventarisierung (DIESE WOCHE)

**TASK:** Vollständige Inventarliste erstellen

```
1. Alle Scripts scan+status (aktiv/inaktiv/veraltet)
2. Alle Skills dokumentieren (wofür?)
3. Alle Memory Files alter+bereinigen
4. Alle Root-Files inventarisieren
```

### Phase 2: Struktur vereinheitlichen (DIESE WOCHE)

**TASK:** Klare Ordnerstruktur

```
workspace/
├── scripts/
│   ├── core/           # Aktive, wichtige Scripts
│   ├── tools/          # Hilfsscripts
│   ├── deprecated/      # Alte Scripts (nicht löschen, nur archivieren)
│   └── README.md       # Index aller Scripts
├── skills/
│   ├── active/         # Regelmäßig genutzt
│   ├── research/       # Research + Ideen
│   └── archived/       # Nicht mehr aktiv
├── memory/
│   ├── daily/          # Tägliche Files
│   └── archive/        # Archivierte
├── docs/               # Dokumentation
├── data/               # Logs + States
└── ceo/                # CEO Workspace
```

### Phase 3: Naming Convention (DIESE WOCHE)

**TASK:** Einheitliche Benennung

```
Regeln:
- Scripts: snake_case.py (learning_coordinator.py)
- Docs: Title-Case.md (Learning Loop Analyse.md)
- Variablen: camelCase
- Constants: UPPER_SNAKE_CASE
```

### Phase 4: Documentation (DIESE WOCHE)

**TASK:** Klare Dokumentation

```
1. SYSTEM_INDEX.md - Überblick über整个 System
2. CONFIGURATION.md - Wo ist was konfiguriert
3. SCRIPTS_INDEX.md - Alle Scripts mit Status
4. ACTIVE_CRONS.md - Alle Crons dokumentiert
```

---

## 🔍 WAS ICH GERADE MACHE

**TASK:** Memory Reranker implementieren

Das nutzt die bestehende `memory_hybrid_search.py` Struktur und fügt einen Reranking-Layer hinzu.

**Danach:** System-Klarheits-Inventarisierung

---

## 📊 PRIORITÄTEN

| Task | Priority | Status |
|------|----------|--------|
| Memory Reranker | 🟡 MED | OFFEN |
| System Inventarisierung | 🔴 HOCH | START NOW |
| Struktur-Vereinheitlichung | 🟡 MED | FOLGT |
| Documentation | 🟡 MED | FOLGT |

---

*Letztes Update: 2026-04-11 11:10 UTC*
*Status: RESEARCH DONE*
*Next: Memory Reranker → dann Inventarisierung*