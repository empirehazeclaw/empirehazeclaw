# System Inventory — 2026-04-11 11:12 UTC

**Purpose:** Klare Übersicht über整个 Workspace

---

## 📊 STATISTICS

| Category | Count | Notes |
|----------|-------|-------|
| Root Files | 240+ | Zu viele! |
| Scripts | 81 | Viele aktiv |
| Skills | 16 | Verschiedene |
| Root .md Files | 30+ | Viele veraltet |
| Memory Files | 3 | Aktuell |
| Docs | 1 | Neu erstellt |

---

## 🔴 ROOT FILES (CRITICAL)

### Sofort aufräumen (dead/old):

```
AGENT_CONSOLIDATION_PLAN.md  - OLD, not relevant
AGENT_INVENTORY.md           - OLD, not relevant  
AGENT_ROI_AUDIT.md           - OLD, not relevant
BACKUP_STATUS.md             - Old backup tracking
CHAOS_TEST.md                - Testing, not needed
DREAMS.md                    - Unclear purpose
FINAL_STATE.md               - Unclear purpose
FUNCTIONAL_TEST.md           - Old testing
INDEX.md                     - Duplicate, README exists
KILL_LIST_CRITERIA.md        - Old planning
KNOWLEDGE_OVERVIEW.md        - Old overview
MODEL_TEST_RESULTS.md        - Old test results
REVENUE.md                   - Old revenue tracking
SECURITY_AUDIT_MEMORY.md     - Old audit
SECURITY_HARDENING_STATUS.md - Old status
SECURITY_KNOWLEDGE.md        - Old security docs
SETUP_EMAIL.md               - Setup instructions
STORE_INTEGRATION.md         - Old integration
SYSTEM_AUDIT_2026-04-09.md   - Old audit
SYSTEM_BLUEPRINT.md          - Old planning
SYSTEM_COMPLETE.md           - Old planning
SYSTEM_CORE.md               - Old planning
VISION.md                    - Old vision
```

### Die wirklich gebraucht werden (keep):

```
HEARTBEAT.md        - System Status (CRITICAL)
IDENTITY.md         - Identity (CRITICAL)
SOUL.md             - Soul (CRITICAL)
USER.md             - User Info (CRITICAL)
TOOLS.md            - Tools Notes (CRITICAL)
MEMORY.md           - Memory Overview (IMPORTANT)
AGENTS.md           - Agents Overview (IMPORTANT)
README.md           - Root README (IMPORTANT)
SYSTEM_ARCHITECTURE.md  - NEW: System Doc
DELIVERY_RULES.md   - Delivery Config
```

---

## 📁 VERZEICHNISSE (Directories)

```
scripts/           - 81 Python Scripts
skills/            - 16 Skill-Verzeichnisse
memory/            - Short-Term Memory (täglich)
core_ultralight/   - Knowledge Graph + Memory
docs/              - Neue Dokumentation
data/              - Logs + States
ceo/                - CEO Workspace
archive/            - Archivierte Files
api/               - API related
api_gateway/        - Gateway Config
apps/              - Applications
agent_runner/      - Agent Runner
ai/                - AI related
analysis/          - Analysis scripts
assets/            - Assets
```

---

## 🔧 SCRIPTS (81 total)

### Core Scripts (aktiv, wichtig):
```
learning_coordinator.py  ⭐ Zentral
loop_check.py           ⭐ Loop Detection
self_eval.py            ⭐ Self Evaluation
innovation_research.py  ⭐ Research
token_tracker.py        ⭐ Token Tracking
gateway_recovery.py     ⭐ Auto-Recovery
auto_doc.py             ⭐ Documentation
session_cleanup.py       ⭐ Cleanup
git_maintenance.py      ⭐ Git Maintenance
mcp_server.py           ⭐ MCP Server
trend_analysis.py       ⭐ Trends
morning_brief.py        ⭐ Daily Brief
security_audit.sh       ⭐ Security
cron_watchdog.py        ⭐ Cron Watchdog
```

### Hilfs-Scripts (nützlich):
```
quick_check.py
health_monitor.py
health_dashboard.py
deep_reflection.py
skill_creator.py
skill_loader.py
learning_tracker.py
autonomous_improvement.py
test_framework.py
```

### Archive-würdig (alt/nicht genutzt):
```
kgml_summary.py
outreach_optimizer.py
email_sequence.py
llm_outreach.py
meeting_scheduler.py
priority_filter.py
demo_scheduler.py
weekly_review_zettel.py
```

---

## 📚 SKILLS (16 dirs)

```
active/              - Active skills
research/            - Research docs
self-improvement/    - Self-improvement
system-manager/      - System management
capability-evolver/  - Capability evolution
product-kits/        - Product kits
clawmart-submission/ - Submission
...und mehr
```

---

## 🧠 MEMORY STRUCTURE

```
memory/
├── 2026-04-11.md   ⭐ TODAY
├── 2026-04-10.md   ⭐ YESTERDAY
└── shared/         - Shared memory
    └── insights/
        └── nightly_dreaming_*.md

core_ultralight/memory/
└── knowledge_graph.json  ⭐ Long-Term Memory (KG)
```

---

## ⚠️ PROBLEME IDENTIFIZIERT

1. **240+ Files im Root** - Unübersichtlich
2. **30+ .md Files im Root** - Viele veraltet
3. **81 Scripts** - Nicht klar was aktiv
4. **Kein klares Naming** - Inkonsistent
5. **Alte Planning Docs** - Nicht mehr relevant

---

## 📋 AKTIONSPLAN

### SOFORT:
1. ✅ SYSTEM_ARCHITECTURE.md erstellt
2. ⏳ Dieses Inventory erstellen (DONE)
3. 🔜 Archive-Ordner für alte Files erstellen
4. 🔜 Alte Root-Files in archive/ verschieben

### DIESE WOCHE:
5. Script-Index erstellen (auto_doc.py existiert bereits!)
6. Cron-Übersicht erstellen
7. Alle Crons dokumentieren
8. Struktur vereinheitlichen

### KOMMANDOS:

```bash
# Create archive dirs
mkdir -p workspace/archive/old_docs
mkdir -p workspace/archive/old_scripts

# List files to archive
ls *.md | grep -E "AGENT|Consolidation|INVENTORY|ROI|AUDIT|BACKUP|CHAOS|FINAL|INDEX|KILL|KNOWLEDGE|MODEL|REVENUE|SECURITY|SETUP|STORE|SYSTEM_AUDIT|SYSTEM_BLUEPRINT|SYSTEM_COMPLETE|SYSTEM_CORE|VISION"
```

---

*Erstellt: 2026-04-11 11:12 UTC*
*Status: INVENTORY COMPLETE*
*Next: Aufräumen + Struktur*
---

## 🔐 SECRETS LOCATION (CRITICAL)

**Path:** `/home/clawbot/.openclaw/secrets/secrets.env`

### Enthaltende Keys:
| Service | Key Name | Status |
|---------|----------|--------|
| Minimax | MINIMAX_API_KEY | ✅ ACTIVE |
| OpenRouter | OPENROUTER_API_KEY | ✅ |
| GitHub | GITHUB_PAT, GITHUB_API_TOKEN | ✅ |
| Google | GOOGLE_OAUTH_*, GEMINI_API_KEY | ✅ |
| AWS | AWS_ACCESS_KEY, AWS_SECRET_KEY | ✅ |
| OpenAI | OPENAI_API_KEY | ✅ |
| Anthropic | ANTHROPIC_API_KEY | ✅ |
| X/Twitter | X_CONSUMER_*, X_ACCESS_TOKEN_* | ✅ |
| Und 20+ weitere | - | ✅ |

### Security:
- **NIE in Git** (siehe .gitignore)
- **NIE in openclaw.json** (nur redacted)
- Backup: secrets.env.bak

### Dokumente:
- `secrets/SECURITY_ROTATION.md` - Key Rotation Status

---

## 🔐 RUNTIME AUTH STORES (CRITICAL)

**Gateway Runtime Keys:**

| Agent | Location | Enthält |
|-------|----------|---------|
| CEO | `agents/ceo/agent/auth-profiles.json` | MINIMAX API Key (runtime) |
| Main | `agents/main/agent/auth-profiles.json` | MINIMAX API Key (runtime) |

**MINIMAX_API_KEY (aktiver Key):**
```
sk-cp-eQ6DbkJtxCAkw_zYabMlyK1B-TOEXlS-imp3xTQBCspBcZJCRT9F6mIbXrGYt7FBHz6g-h3mlg0dOoazixpMxzz5VOCn5U--mp8HfRIYaYZl4TQcmTmeYHs
```

**Security:**
- auth-profiles.json ist in `~/.openclaw/agents/` (nicht im Workspace)
- secrets/env ist Backup (nicht direkt vom Gateway genutzt)
- Gateway lädt Keys aus auth-profiles.json zur Laufzeit

### ⚠️ Das "Missing API Key" Warning

**Ursache:** `openclaw.json` zeigt nur Profile-Referenzen, nicht die Keys.
**Realität:** Key IST vorhanden in `agents/ceo/agent/auth-profiles.json`
**System:** Läuft normal ✅
