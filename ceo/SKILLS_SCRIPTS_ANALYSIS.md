# Skills & Scripts Analyse — Sir HazeClaw
**Generated:** 2026-04-17
**Author:** Subagent Analysis

---

## 📊 Inventory Overview

| Category | Count | Path |
|----------|-------|------|
| Skills (directories) | 28 | `workspace/skills/` |
| _Library Patterns | 27 | `skills/_library/` |
| Total Scripts | 147 | `workspace/SCRIPTS/` |
| → Automation | 70 | `SCRIPTS/automation/` |
| → Analysis | 46 | `SCRIPTS/analysis/` |
| → Tools | 18 | `SCRIPTS/tools/` |
| → Self-Healing | 8 | `SCRIPTS/self_healing/` |
| → Archive | 5 | `SCRIPTS/_ARCHIVE/` |

---

## 🔍 Skill Architecture Analyse

### Skill Breakdown (28 total)

```
Active (3):
  ├── prompt-coach      — NEW, coaching for all inputs
  ├── semantic-search   — KG integration, read+write
  └── capability-evolver — Recent activity (2026-04-12)

Medium Usage (9):
  ├── _library          — 27 reusable patterns (passive)
  ├── backup-advisor
  ├── coding
  ├── content-creator
  ├── frontend
  ├── loop-prevention
  ├── qa-enforcer
  ├── research
  └── system-manager

Unused (2):
  ├── backend-api
  └── voice-agent

Other (14):
  ├── INDEX.md, README.md, SKILLS_TEST_REPORT.md (docs)
  ├── bug-hunter, code-review, debug-helper, git-manager
  ├── guardrails, hyperparameter-tuner, log-aggregator
  ├── memory-sanitizer, repo-analyzer, test-generator, youtube-transcript
```

### Skills Problems

| Problem | Evidence |
|---------|----------|
| **Passive documentation** | Skills are markdown files, no active invocation. No orchestrator routes requests to skills. |
| **Thin skills** | Many skills are 1-2 files with minimal content. E.g., `backup-advisor`, `frontend`, `content-creator` likely need real implementations. |
| **No skill hierarchy** | All skills are flat. No meta-skills or orchestration layer to decide which skill to use for a given task. |
| **_library not integrated** | 27 patterns exist but scripts don't import/use them — they're documentation, not code. |
| **Duplicate patterns** | `loop_detection.md` and `retry_loop_prevention.md` overlap significantly. `self_correction.md` + `self_evaluation.md` also overlap. |

---

## 🔍 Script Architecture Analyse

### 70 Automation Scripts — Problem Areas

**Duplicate/Near-Duplicate Files:**
```
backup_verify.py      ≈  backup_verifier.py    (likely same purpose)
kg_access_updater.py  vs  kg_access_updater_optimized.py  (optimized replaces original)
context_compressor.py (tools/)  vs  context_compressor.py (automation/)  (different versions)
learning_coordinator.py (analysis/)  vs  learning_coordinator.py (automation/)
```

**Learning Loop Cluster (7 scripts, highly overlapping):**
```
learning_analyzer.py
learning_collector.py
learning_coordinator.py    ← duplicates with analysis/
learning_executor.py
learning_feedback.py
learning_loop_v3.py        ← MAIN script (2334 lines!)
learning_to_kg_sync.py
```
Plus 5 old versions in `_ARCHIVE/` that are stale.

**KG Cluster (4 scripts):**
```
kg_access_updater.py       (old, slow)
kg_access_updater_optimized.py  (replacement)
kg_auto_curator.py
kg_updater.py              (581 lines, large)
```

**Cron Cluster (6 scripts, similar purpose):**
```
cron_error_healer.py    (776 lines — largest cron script)
cron_monitor.py
cron_optimizer.py
cron_status_dashboard.py
cron_watchdog.py
cron_error_healer.py    ← heavy overlap with cron_watchdog + cron_monitor
```

**Health Cluster (3 scripts):**
```
health_check.py
health_monitor.py
health_alert.py
```
→ Likely could be one `health.py` with mode flags.

### Script Size Distribution

| Lines | Scripts |
|-------|---------|
| >500 | `learning_loop_v3.py` (2334), `autonomy_supervisor.py` (615), `agent_self_improver.py` (703), `learning_coordinator.py` (730) |
| 300-500 | `cron_error_healer.py` (776), `lcm_wiki_sync.py` (431), `morning_brief.py` (410), `graceful_degradation.py` (389), `kg_auto_curator.py` (381), `memory_log_analyzer.py` (379) |
| 100-300 | ~15 scripts |
| <100 | ~40 scripts (small utilities) |

### No Shared Infrastructure

All scripts independently import:
```
datetime, pathlib, json, os, subprocess, sys
```
**No `lib/` directory** with shared utilities for:
- Logging
- Error handling
- Path constants
- KG access
- Config management

This means copy-paste code everywhere and no centralized fixes.

---

## ⚠️ Critical Issues

### 1. Massive Feature Drift
The 70 automation scripts grew organically without a clear plan. Multiple scripts do similar things (e.g., 6 cron-related scripts). No single source of truth.

### 2. Scripts vs Skills Separation is Artificial
**Skills** = markdown docs (passive)
**Scripts** = Python executables (active)
But they reference each other inconsistently. The `capability-evolver` skill is active but doesn't orchestrate other skills — it just runs its own logic.

### 3. _ARCHIVE is Cluttered
5 old learning_loop versions occupy space but serve no purpose. The active version in `automation/learning_loop_v3.py` is what's used.

### 4. No Testing / Fitness Tracking
`skills_fitness_tracker.py` exists but there's no evidence it's integrated into any workflow. Scripts run via cron but fitness isn't measured systematically.

### 5. Skill-Script Mapping is Unclear
Which skill governs which script? No clear ownership. For example:
- `loop-prevention` skill ↔ which script enforces this?
- `guardrails` skill — where's the enforcement code?

---

## 💡 Best Practices (Researched)

### Skill Orchestration
1. **Skill registry** with activation conditions (not just documentation)
2. **Skill chaining** — skills should invoke sub-skills when needed
3. **Quality gates** — skills should have fitness metrics, not just presence
4. **Lazy loading** — skills activate on-demand, not all at startup
5. **Circuit breakers** — if a skill fails repeatedly, route around it

### Script Modularity
1. **Shared `lib/` directory** — common utils, path constants, KG access, logging
2. **Single Responsibility** — each script does one thing well
3. **Facade pattern** — big scripts (like `learning_loop_v3.py`) should delegate to smaller focused modules
4. **Plugin architecture** — scripts should register themselves, not be hardcoded

### Code Reuse
1. **Extract common patterns** — datetime handling, path resolution, JSON read/write, subprocess calls → `lib/common.py`
2. **Template inheritance** — scripts should use a base class/skeleton
3. **Configuration vs code** — paths, thresholds, constants should be in config, not hardcoded

### Automation Patterns
1. **Idempotency** — all scripts must be safe to run multiple times
2. **Graceful degradation** — when one component fails, system continues
3. **Health signals** — all scripts should emit status/metrics
4. **Scheduled vs event-driven** — separate these concerns clearly

---

## 🎯 Consolidation & Optimization Recommendations

### Phase 1: Quick Wins (1-2 hours)

| Action | Impact | Effort |
|--------|--------|--------|
| **Delete `_ARCHIVE/` scripts** (5 files) | Clean up stale code | 5 min |
| **Delete `kg_access_updater.py`** (keep `_optimized`) | Remove duplicate | 5 min |
| **Merge `backup_verify.py` + `backup_verifier.py`** → `backup_check.py` | Reduce duplication | 15 min |
| **Move `context_compressor.py` (tools/) → tools/context_compressor_v2.py**, keep automation version as main | Clarify which is used | 10 min |
| **Create `SCRIPTS/lib/` with path constants** | Foundation for reuse | 30 min |

### Phase 2: Medium Refactor (half-day)

| Action | Impact | Effort |
|--------|--------|--------|
| **Create `skills/_orchestrator.py`** — reads skills, activates based on context | Bridge skills↔execution | 2-3 hours |
| **Refactor `learning_loop_v3.py`** — extract sub-modules (collector, analyzer, executor, feedback) | Reduce 2334-line monster | 3-4 hours |
| **Merge `health_check.py` + `health_monitor.py` + `health_alert.py` → `health.py`** with `--check/--monitor/--alert` modes | Single health system | 1 hour |
| **Merge 6 cron scripts → 2: `cron_scheduler.py` + `cron_healer.py`** | Reduce complexity | 2 hours |
| **Create `lib/logging.py`** — all scripts import from here | Consistent logging | 1 hour |

### Phase 3: Architecture (1 day)

| Action | Impact | Effort |
|--------|--------|--------|
| **Skill registry** — JSON-based registry with activation conditions, fitness scores | Skills become active | 4-6 hours |
| **Script plugin system** — scripts auto-register with capabilities | No hardcoded routing | 3-4 hours |
| **Shared `lib/kg.py`** — common KG read/write patterns | Centralized KG access | 2 hours |
| **Merge overlapping _library patterns** (loop_detection + retry_loop_prevention → loop_prevention.md) | Cleaner library | 1 hour |
| **Deprecate unused skills** (`backend-api`, `voice-agent`) — move to _archive | Less maintenance | 30 min |

---

## 📋 Priority Order

```
1. [IMMEDIATE] Create SCRIPTS/lib/ — path constants, common imports
2. [IMMEDIATE] Delete stale _ARCHIVE files
3. [THIS WEEK] Merge health_* scripts into single health.py
4. [THIS WEEK] Merge cron_* scripts to 2 files max
5. [THIS WEEK] Extract sub-modules from learning_loop_v3.py
6. [THIS WEEK] Build skill registry (JSON-based)
7. [NEXT SPRINT] Skill orchestrator with activation conditions
8. [NEXT SPRINT] Plugin system for script auto-registration
```

---

## 📈 Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Scripts | 147 | ~90 (40% reduction) |
| Duplicate script families | 6+ | 0 |
| Skill activation | Passive (docs) | Active (orchestrated) |
| Shared utilities | None | `lib/` with 5+ modules |
| Archive clutter | 5 stale files | Clean |
| Monolithic scripts (>500 lines) | 4 | 0 (all refactored) |

---

*Report by Subagent — Skills/Scripts Analysis Task*