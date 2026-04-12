# 🎯 SIR HAZECLAW — DETAILED EXECUTION PLAN
**Research Date:** 2026-04-12
**Based on:** Deep Audit + 2026 Agent Architecture Research
**Status:** APPROVED — Ready to Execute
**Storage:** `docs/EXECUTION_PLAN.md` (Git committed)

---

## 📚 RESEARCH INSIGHTS (2026 Best Practices)

### From Claude Code Architecture Leak (March 2026)
Key lessons for Sir HazeClaw:

1. **Modular Tool Registry** — 40 tools in plugin architecture with hooks
   - Sir HazeClaw should group scripts by domain (health, learning, memory, etc.)
   - Each domain should have a unified entry point

2. **Cache-Aware Prompt Boundaries** — Stable content cached, dynamic refreshed
   - Sir HazeClaw's memory architecture already does this (KG = stable, session = dynamic)
   - Can optimize by marking more content as stable

3. **Permission Enforcement** — Every action validated before execution
   - Sir HazeClaw has this via exec security modes
   - Could be tighter: explicit permission per script category

4. **Error Recovery Loop** — Structured errors fed back for retry
   - Sir HazeClaw's self-healing v2 does this
   - Could add "recovery context" so next attempt knows what failed

5. **KAIROS Concept** — Autonomous daemon mode with opportune moments
   - Sir HazeClaw already has this via continuous_improver
   - Gap: doesn't decide *when* to act autonomously yet

### From Agentic AI Papers (ArXiv, 2026)

1. **AutoRefine Pattern** — Extract reusable expertise from execution histories
   - Sir HazeClaw's KG captures learnings but doesn't extract "skill patterns"
   - Could auto-generate new skills from repeated patterns

2. **Meta-Agent Framework** — Hierarchical orchestration for self-improvement
   - Sir HazeClaw has: meta_improver + continuous_improver + autonomous_improvement
   - Could consolidate into single meta-orchestrator

3. **Optimizing Agentic Workflows via Meta-tools** — Bundle recurring tool sequences
   - Sir HazeClaw has cron jobs bundling sequences
   - Could identify new meta-tools from recurring patterns

4. **Trace-Driven Debugging** — observe-analyze-repair loop
   - Sir HazeClaw's cron_error_healer already does this
   - Could extend to script-level, not just cron-level

---

## 🎯 EXECUTION PHASES

### PHASE 1: CRITICAL FIXES (Immediate)
**Time:** Today
**Goal:** Fix broken things, stabilize system

| # | Task | Action | Verification |
|---|------|--------|-------------|
| 1.1 | CEO Daily Briefing | ✅ FIXED — delivery mode=none → announce | Run at 11:00 UTC today |
| 1.2 | 3 Disabled Crons | ✅ FIXED — re-enabled with correct config | Check cron list |
| 1.3 | error_reducer loop | NOT NEEDED — archived script issue | error_reduction.log shows 0 fixes now |

### PHASE 2: SCRIPT CONSOLIDATION (This Week)
**Time:** 2-3 days
**Goal:** 99 scripts → ~40 scripts

#### 2.1 Consolidate Error Scripts (4 → 1)
**Files:**
- `error_reducer.py` ← KEEP (main engine)
- `error_rate_monitor.py` ← MERGE into error_reducer (--monitor flag)
- `error_reduction_plan.py` ← MERGE into error_reducer (--plan flag)
- `error_reduction_strategy.py` ← ARCHIVE (in _archive/phase1 already)

**Action:** Add `--monitor` and `--plan` modes to error_reducer.py

#### 2.2 Consolidate Token Scripts (2 → 1)
**Files:**
- `token_tracker.py` ← KEEP (main)
- `token_budget_tracker.py` ← MERGE into token_tracker (--budget flag)

**Action:** Add `--budget` mode to token_tracker.py

#### 2.3 Consolidate KG Scripts (4 → 1)
**Files:**
- `kg_updater.py` ← KEEP (main)
- `kg_enhancer.py` ← MERGE into kg_updater (--enhance flag)
- `kg_lifecycle_manager.py` ← MERGE into kg_updater (--lifecycle flag)
- `kg_relation_cleaner.py` ← MERGE into kg_updater (--clean-relations flag)

**Action:** Add `--enhance`, `--lifecycle`, `--clean-relations` modes to kg_updater.py

#### 2.4 Consolidate Memory Scripts (3 → 1)
**Files:**
- `memory_cleanup.py` ← KEEP (main)
- `memory_freshness.py` ← MERGE into memory_cleanup (--freshness flag)
- `stale_memory_cleanup.py` ← MERGE into memory_cleanup (--stale flag)

**Action:** Add `--freshness` and `--stale` modes to memory_cleanup.py

#### 2.5 Consolidate Cron Scripts (2 → 1)
**Files:**
- `cron_watchdog.py` ← KEEP (main)
- `cron_monitor.py` ← MERGE into cron_watchdog (--monitor flag)

**Action:** Add `--monitor` mode to cron_watchdog.py

#### 2.6 Archive Unused Scripts
**Safe to Archive:**
```
blast_radius_estimator.py      # Never referenced
openrouter_monitor.py          # Never referenced
performance_dashboard.py       # Never referenced
reflection_loop.py             # Replaced by deep_reflection.py
session_analyzer.py            # Likely replaced
trend_analysis.py              # Overlaps with quality_metrics
```

**Action:** Move to `scripts/_archive/phase2/`

#### 2.7 Update Cron References
After consolidating, update any crons pointing to old script names.

---

### PHASE 3: DOCS SIMPLIFICATION (This Week)
**Time:** 1 day
**Goal:** Clear, minimal documentation

| # | Task | Action |
|---|------|--------|
| 3.1 | docs/STRUCTURED_IMPROVEMENT_PLAN.md | Delete (outdated, superseded by this plan) |
| 3.2 | docs/RESTRUCTURE_PLAN.md | Delete (superseded by DEEP_AUDIT.md) |
| 3.3 | docs/CONSOLIDATION_REPORT.md | Keep (reference for what was done) |
| 3.4 | docs/SCRIPTS/ | Delete entire directory (empty/integrated) |
| 3.5 | Update SYSTEM_ARCHITECTURE.md | Update script count: 97 → ~40 |
| 3.6 | Update CRON_INDEX.md | Remove disabled crons from active list |
| 3.7 | Create docs/SCRIPT_INDEX.md | One-page list of all scripts with purpose |

---

### PHASE 4: KG INTEGRATION (Next Week)
**Time:** 2-3 days
**Goal:** KG actually gets queried (access_count = 0 is embarrassing)

#### 4.1 Fix KG Retrieval
**Problem:** `memory_hybrid_search.py` never queries KG — access_count = 0 for all entities

**Fix:**
1. Modify `memory_hybrid_search.py` to always query KG first
2. Update `MEMORY_API.py` to expose KG search as primary
3. Add KG warmup on startup (pre-load frequently accessed entities)

#### 4.2 Fix Relation Quality
**Problem:** 68.7% of relations are "shares_category" (low quality spam)

**Fix:**
1. Run `kg_relation_cleaner.py` (now integrated into kg_updater)
2. Add relation quality scoring in KG updater
3. Only create relations with confidence > 0.7

#### 4.3 KG-Centric Memory Loop
**New Pattern:** Think → Lookup KG → Act → Update KG

**Implementation:**
- Every learning coordinator run should query KG before generating new ideas
- Every autonomous improvement should check KG for existing patterns first
- KG entities should auto-update access_count on retrieval

---

### PHASE 5: SELF-IMPROVEMENT ORCHESTRATION (Ongoing)
**Time:** Continuous
**Goal:** Single meta-orchestrator instead of 3 separate scripts

**Current Scripts:**
- `continuous_improver.py` — hourly autonomous improvements
- `autonomous_improvement.py` — overnight experiments
- `meta_improver.py` — learning extraction
- `learning_coordinator.py` — hourly learning loop

**Problem:** Overlapping concerns, no single source of truth

**Fix:** Create `SELF_IMPROVEMENT_ORCHESTRATOR.py`

```python
# Single entry point for all self-improvement
# Modes:
#   --hourly     : Learning Coordinator + Continuous Improver combined
#   --overnight  : Autonomous Improvement experiments
#   --weekly     : Meta-Improver experience extraction
#   --full       : All of the above
```

**Pattern from Research:**
- Meta-Agent Framework: hierarchical orchestration
- AutoRefine: extract reusable expertise from execution histories

---

### PHASE 6: OPTIONAL ENHANCEMENTS (Future)
**Time:** When needed
**Priority:** Low

| # | Enhancement | Description |
|---|-------------|-------------|
| 6.1 | KAIROS-style daemon | Decide autonomously when to act, not just cron schedules |
| 6.2 | Meta-tools | Bundle recurring tool sequences into single commands |
| 6.3 | Permission tiers | Explicit permissions per script category |
| 6.4 | KG auto-extraction | Auto-generate new skills from repeated patterns |
| 6.5 | Cache-aware prompts | Mark more content as stable for prompt caching |

---

## 📅 EXECUTION TIMELINE

```
Day 1 (Today, 2026-04-12):
  ✅ Phase 1: Critical Fixes (done)
  ⬜ Start Phase 2.1: Consolidate error scripts
  
Day 2 (2026-04-13):
  ⬜ Finish Phase 2.1: error scripts
  ⬜ Phase 2.2: token scripts
  ⬜ Phase 2.3: kg scripts
  
Day 3 (2026-04-14):
  ⬜ Phase 2.4: memory scripts
  ⬜ Phase 2.5: cron scripts
  ⬜ Phase 2.6: archive unused
  
Day 4 (2026-04-15):
  ⬜ Phase 3: Documentation cleanup
  ⬜ Phase 2.7: Update cron references
  
Day 5-7:
  ⬜ Phase 4: KG Integration
  ⬜ Commit all changes
  
Ongoing:
  ⬜ Phase 5: Self-Improvement Orchestration
```

---

## ✅ VERIFICATION CHECKLIST

After each phase, verify:

- [ ] `openclaw status` — Gateway still healthy
- [ ] `openclaw tasks` — No new issues
- [ ] `cron list` — All expected crons active
- [ ] `python3 scripts/health_check.py --full` — No errors
- [ ] Git commit with changes

---

## 🛡️ ROLLBACK PLAN

If something breaks:

1. **Git rollback:**
   ```bash
   cd /home/clawbot/.openclaw/workspace
   git revert HEAD
   git stash
   ```

2. **Full workspace rollback:**
   ```bash
   cd /home/clawbot/.openclaw/workspace
   git checkout backup_pre_consolidation_20260412
   ```

3. **Test suite:**
   ```bash
   python3 scripts/capability-evolver/test_framework.py
   ```

**Backup exists at:** `rollback/consolidation_20260412/workspace_backup_20260412.bundle`

---

## 📊 SUCCESS METRICS

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Scripts | 99 | 99 | ~40 |
| Active Crons | 17 | 20 | 15-17 |
| Disabled Crons | 28 | 25 | ~10 |
| KG access_count | 0 | >100 | >500 |
| Error Rate | 1.48% | <1% | <0.5% |
| Documentation | 20+ docs | 10 docs | 8 docs |

---

## 📝 CHANGE LOG

| Date | Changes |
|------|---------|
| 2026-04-12 07:50 | Created from Deep Audit + Research |
| 2026-04-12 07:45 | Phase 1 fixes completed |

---

*Plan stored in docs/EXECUTION_PLAN.md*
*Research sources: VoltAgent/awesome-ai-agent-papers, DigitalApplied Claude Code leak analysis, ArXiv 2026 agent papers*
