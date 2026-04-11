# 🚀 STRUCTURED IMPROVEMENT PLAN
## Sir HazeClaw — Based on System Analysis
**Created:** 2026-04-11 21:25 UTC

---

## 📊 CURRENT STATE ANALYSIS

### Scripts (83 total)
| Category | Count | Examples |
|----------|-------|----------|
| Learning/Improvement | 12 | learning_coordinator.py, meta_improver.py, self_play_improver.py |
| Memory | 6 | memory_cleanup.py, MEMORY_API.py, kg_updater.py |
| Error Handling | 5 | error_reducer.py, cron_error_healer.py |
| Daily Operations | 8 | morning_brief.py, evening_summary.py, daily_summary.py |
| Health/Status | 4 | health_monitor.py, self_check.py |
| Communication | 3 | llm_outreach.py, email_sequence.py |
| Other | 45 | Various utilities |

### Skills (18 total)
```
backend-api, backup-advisor, capability-evolver, coding,
content-creator, email-outreach, frontend, lead-intelligence,
loop-prevention, qa-enforcer, research, self-improvement,
semantic-search, system-manager, video-renderer, voice-agent
```

### Active Crons: 20
### Cron Errors: 5
### Tests: 52 passed (0 failed)

---

## 🎯 IMPROVEMENT PILLARS

### PILLAR 1: SCRIPT CONSOLIDATION (83 → ~40)
**Goal:** Reduce chaos, increase maintainability

**Action Items:**
- [ ] Categorize all 83 scripts into folders:
  ```
  scripts/
  ├── core/          # Critical (learning_coordinator, memory_api, etc.)
  ├── automation/    # Crons (morning_brief, evening_review, etc.)
  ├── maintenance/   # Cleanup (memory_cleanup, kg_lifecycle, etc.)
  ├── analysis/      # Tools (error_reducer, health_monitor, etc.)
  ├── experimental/  # One-offs, tests
  └── archive/       # Old, unused scripts
  ```
- [ ] Create `scripts/README.md` with index
- [ ] Identify 40+ scripts that can be archived
- [ ] Document core scripts with docstrings

**Timeline:** 2-3 days

---

### PILLAR 2: TEST COVERAGE
**Goal:** Confidence in changes

**Current:** 52 tests (all in capability-evolver)
**Missing:** Tests for memory_scripts, error_handling, core automation

**Action Items:**
- [ ] Create `test_core_scripts.py`:
  ```python
  # Test MEMORY_API.py
  # Test memory_cleanup.py
  # Test error_reducer.py
  # Test cron_error_healer.py
  ```
- [ ] Add tests to CI/CD pipeline
- [ ] Target: 100+ tests for core functionality

**Timeline:** 3-4 days

---

### PILLAR 3: ERROR RECOVERY DEEPEN
**Goal:** System heals itself, not just detects

**Current State:**
- cron_error_healer.py exists
- But Error Rate still 1.41%
- 43.4% "unknown" errors remain unknown

**Action Items:**
- [ ] Audit cron_error_healer — why isn't it healing?
  ```bash
  cat logs/cron_healer.log
  cat logs/cron_healer_live.log
  ```
- [ ] Categorize "unknown" errors:
  - Telegram API limits (extern, can't fix)
  - exec preflight (system security, can't fix)
  - timeout (can fix with background/cron)
  - permission denied (can fix with path checks)
- [ ] Create "Error Action Matrix":
  ```python
  ERROR_ACTIONS = {
      "timeout >60s": "move to background_cron",
      "permission denied": "add path verification",
      "Telegram API limit": "rate_limit + retry",
      "exec preflight": "flag as system_limit"
  }
  ```

**Timeline:** 2 days

---

### PILLAR 4: KG QUALITY & USAGE
**Goal:** Make KG valuable, not just big

**Current:** 209 entities, 4659 relations — but are they used?

**Action Items:**
- [ ] Add KG usage tracking:
  ```python
  # Track when KG is queried
  def query_kg(pattern):
      track("kg_query", pattern)
  ```
- [ ] Prune stale entities (>30 days, no relations)
- [ ] Add "entity quality score" based on:
  - Relation count
  - Query frequency
  - Last accessed
- [ ] Create KG dashboard metrics

**Timeline:** 2-3 days

---

### PILLAR 5: SKILLS INTEGRATION
**Goal:** 18 skills → 8 active, documented

**Action Items:**
- [ ] Audit each skill:
  - Is it used?
  - Is it integrated?
  - Does it have docs?
- [ ] Create `skills/INDEX.md`:
  ```
  ## Active Skills
  - capability-evolver ✅ (369 tests)
  - self-improvement ✅ (integrated)
  - qa-enforcer ✅ (used)
  
  ## Inactive Skills
  - video-renderer ❌ (not used)
  - voice-agent ❌ (not integrated)
  ```
- [ ] Archive unused skills

**Timeline:** 1-2 days

---

### PILLAR 6: DASHBOARD / MISSION CONTROL
**Goal:** One view of system health

**Action Items:**
- [ ] Create `dashboard.py`:
  ```python
  # Shows:
  # - Error Rate (current vs target)
  # - KG Stats (entities, relations, size)
  # - Cron Health (active, errors)
  # - Learning Loop Status (validation rate)
  # - Memory Systems (health check)
  ```
- [ ] Run via: `python3 dashboard.py`
- [ ] Make it Telegram-friendly for reporting

**Timeline:** 1-2 days

---

## 📅 EXECUTION PLAN

### Week 1: Foundation (This Week)
| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | Script Categorization | scripts/ organized into folders |
| 2 | Test Framework | test_core_scripts.py with 20+ tests |
| 3 | Error Deepen | Error Action Matrix, cron_healer audit |
| 4 | KG Quality | Prune stale, usage tracking |
| 5 | Dashboard | mission_control.py |

### Week 2: Consolidation
| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | Skills Audit | skills/INDEX.md, archive unused |
| 2 | Documentation | Update all READMEs |
| 3 | CI/CD | GitHub actions for tests |
| 4 | Integration | All pieces work together |
| 5 | Review | What's missing? |

---

## 📈 SUCCESS METRICS

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Scripts | 83 | ~40 | ✅ 50% reduction |
| Active Skills | 18 | 8 | ✅ Documented |
| Test Coverage | 52 | 100+ | ✅ +100% |
| Error Recovery | 0% | 80% | ✅ "Heals" |
| KG Quality | Unknown | Scored | ✅ Tracked |

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking something | HIGH | Add tests FIRST |
| Losing track of scripts | MEDIUM | Commit after each folder move |
| Time investment | HIGH | Focus on Pillar 1+2 first |

---

## 💡 QUICK WINS (Today)

1. **Archive 20+ unused scripts** — 5 min
2. **Add docstrings to top 10 scripts** — 15 min
3. **Audit cron_error_healer logs** — 10 min
4. **Create scripts/README.md** — 10 min

---

*Plan Version: 1.0*
*Next Update: After Week 1 completion*
