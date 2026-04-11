# 🚀 STRUCTURED IMPROVEMENT PLAN
## Sir HazeClaw — Based on System Analysis + Research
**Created:** 2026-04-11 21:25 UTC
**Updated:** 2026-04-11 21:30 UTC (Research from Production Patterns)

---

## 📊 CURRENT STATE ANALYSIS

### Scripts (83 total)
| Category | Count | Examples |
|----------|-------|----------|
| Learning/Improvement | 12 | learning_coordinator.py, meta_improver.py |
| Memory | 6 | memory_cleanup.py, MEMORY_API.py |
| Error Handling | 5 | error_reducer.py, cron_error_healer.py |
| Other | 60 | Various utilities |

### Active Crons: 20 | Cron Errors: 5 | Tests: 52 passed

---

## 🔬 RESEARCH FINDINGS (2026-04-11)

### Industry Best Practice: The Four-Stage Recovery Pattern
```
Detect → Diagnose → Heal → Verify
```

**Source:** Self-Healing Agent Pattern (DEV Community), Claude Lab Production Patterns

### 7 Error Categories & Optimal Recovery Strategies

| Category | Symptoms | Strategy |
|----------|----------|----------|
| **Transient API** | 429 Rate Limit, 500, 503 | Exponential backoff with jitter |
| **Context Overflow** | Token limit exceeded | Context compression → summary |
| **Tool Failure** | API timeout, auth expired | Alternative tool → fallback |
| **Malformed Output** | JSON parse, schema mismatch | Output repair prompt |
| **Reasoning Errors** | Hallucinations, contradictions | Self-verification loop |
| **Infinite Loops** | Repeated calls, no progress | Loop detection → state reset |
| **Cascade Failures** | Single failure spreading | Circuit breaker → graceful degradation |

### Our Error Distribution
| Category | % | Actionable? |
|---------|---|------------|
| exec_error | 46.4% | ❌ System limit (can't fix) |
| unknown | 43.4% | ❌ Telegram limits (extern) |
| timeout | 6.8% | ✅ CAN FIX |
| json_error | 1.4% | ✅ CAN FIX |
| permission | 1.3% | ✅ CAN FIX |
| not_found | 0.7% | ✅ CAN FIX |

---

## 🚨 CRITICAL FINDING: Why Our Error Recovery Fails

### The Problem
```
cron_error_healer.log shows:
   "HEALING: Would restart gateway"
   "HEALING: Would switch to silent mode"

→ Healing is DETECTED but NOT EXECUTED!
```

### Root Cause Analysis
1. **Detection works** — errors are identified
2. **Diagnosis works** — error type is classified  
3. **Healing says "Would"** — but doesn't execute!
4. **Verification missing** — no闭环 (closed loop)

### The Architecture Gap
```
Industry Standard (4-Stage):
   Detect → Diagnose → HEAL → VERIFY

Our System (Broken):
   Detect → Diagnose → (nothing) ← "Would" but no execution!
```

---

## 🎯 IMPROVEMENT PILLARS (UPDATED)

### PILLAR 1: SCRIPT CONSOLIDATION
**Goal:** 83 → ~40 scripts (50% reduction)

**Folders:**
```
scripts/
├── core/           # learning_coordinator, MEMORY_API
├── automation/     # morning_brief, evening_review
├── maintenance/    # memory_cleanup, kg_lifecycle
├── analysis/       # error_reducer, health_monitor
├── healing/       # NEW: error recovery system
├── experimental/  # one-offs, tests
└── archive/        # old, unused
```

**Timeline:** 2-3 days

---

### PILLAR 2: TEST COVERAGE
**Goal:** 52 → 100+ tests

**Add tests for:**
- MEMORY_API.py functions
- memory_cleanup.py logic
- error_reducer.py parsing
- **cron_error_healer.py execution** (currently broken!)

**Timeline:** 3-4 days

---

### PILLAR 3: SELF-HEALING ARCHITECTURE (PRIORITY!)

This is the MOST CRITICAL pillar based on research.

#### Phase 3.1: Fix cron_error_healer.py
**Current Issue:** Only logs "Would" instead of executing

```python
# Current (broken):
if not dry_run:
    execute_healing()  # This path exists but isn't reached!

# The "Would" comes from lines 251, 273, etc.
# Because dry_run=True OR the actual execution is blocked
```

**Fix Required:**
1. Enable actual execution (remove dry_run block)
2. Add Verify phase (check if healing worked)
3. Add Circuit Breaker pattern

#### Phase 3.2: Implement Full 4-Stage Loop
```python
class SelfHealingAgent:
    def run(self, task):
        for step in range(20):
            try:
                # Detect
                error = self.detect_errors()
                
                if error:
                    # Diagnose
                    diagnosis = self.diagnose(error)
                    
                    # Heal (was "Would", now REAL)
                    healing = self.heal(diagnosis)
                    
                    # Verify (NEW - missing!)
                    if not self.verify(healing):
                        # Circuit breaker
                        self.circuit_breaker.open()
                        return self.graceful_degrade()
                        
            except CriticalError:
                # Cascade failure prevention
                self.isolate()
```

#### Phase 3.3: Error Action Matrix (Based on Research)

```python
ERROR_ACTIONS = {
    # Category: (Strategy, MaxRetries, Timeout)
    "timeout >60s": ("move_to_background", 0, None),
    "timeout <60s": ("retry_exponential_backoff", 3, 30),
    "rate_limit": ("backoff_jitter", 5, 60),
    "permission_denied": ("add_path_verification", 0, None),
    "gateway_draining": ("restart_gateway", 3, 10),
    "telegram_api_limit": ("rate_limit_retry", 2, 120),
    "exec_preflight": ("flag_system_limit", 0, None),
    "unknown": ("classify_and_log", 0, None),  # Research: 43% unknown = need better classification
}
```

#### Phase 3.4: Add Verification Loop
```python
def verify(self, healing_action) -> bool:
    """Check if healing worked"""
    # Wait for next cycle
    time.sleep(10)
    
    # Check if error persists
    current_errors = self.get_current_errors()
    
    if healing_action.error in current_errors:
        # Healing failed
        if healing_action.attempts >= healing_action.max_attempts:
            return False  # Circuit breaker
        healing_action.attempts += 1
        return False
    
    # Healing worked
    return True
```

**Timeline:** 3-4 days (this is critical infrastructure)

---

### PILLAR 4: KG QUALITY & USAGE

**Current:** 209 entities, 4659 relations — but:
- No usage tracking
- No quality scoring
- No pruning

**Actions:**
- [ ] Add KG query tracking (when KG is searched)
- [ ] Entity quality score: relations + access frequency
- [ ] Prune stale: >30 days, no relations
- [ ] Research: "Agentic SRE" — KG as monitoring system

**Timeline:** 2-3 days

---

### PILLAR 5: SKILLS INTEGRATION

**Current:** 18 skills (fragmented)

**Target:** 8 active, documented

| Status | Skills |
|--------|--------|
| ✅ Active | capability-evolver (369 tests), self-improvement, qa-enforcer |
| ⚠️ Needs Review | backend-api, coding, semantic-search, system-manager |
| ❌ Archive | video-renderer, voice-agent, lead-intelligence |

**Timeline:** 1-2 days

---

### PILLAR 6: DASHBOARD / MISSION CONTROL

**Research Insight:** Industry uses "Agentic SRE" — agents as reliability engineers

**Create dashboard.py showing:**
```
┌─────────────────────────────────────────────┐
│  MISSION CONTROL — Sir HazeClaw            │
├─────────────────────────────────────────────┤
│  Error Rate: 1.41% [████████░░] Target    │
│  KG: 209 entities (quality: 73%)          │
│  Crons: 20 active, 5 errors                 │
│  Learning Loop: 97% validation              │
│  Self-Healing: [🔴 BROKEN]                 │
└─────────────────────────────────────────────┘
```

**Timeline:** 1-2 days

---

## 📅 EXECUTION PLAN (UPDATED)

### Week 1: CRITICAL FIRST (Self-Healing Focus)

| Day | Focus | Deliverable |
|-----|-------|-------------|
| **1** | **Fix cron_error_healer** | Real healing execution, not "Would" |
| **1** | **Add Verify phase** | 4-stage loop complete |
| **1** | **Add Circuit Breaker** | Cascade failure prevention |
| 2 | Error Action Matrix | All 7 categories mapped |
| 3 | Test Framework | 20+ tests for healing |
| 4 | Script Consolidation | Start folder reorganization |
| 5 | Dashboard | mission_control.py |

### Week 2: Quality & Scale

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | KG Quality | Usage tracking, entity scoring |
| 2 | Skills Audit | Archive unused, document active |
| 3 | Documentation | All READMEs updated |
| 4 | Integration | All pieces work together |
| 5 | Review | What else needs work? |

---

## 📈 SUCCESS METRICS

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Error Recovery | "Would" | **REAL EXECUTION** | ✅ |
| Healing Verification | ❌ None | ✅ 4-Stage Loop | ✅ |
| Circuit Breaker | ❌ None | ✅ Added | ✅ |
| Test Coverage | 52 | 100+ | ✅ +100% |
| Scripts | 83 | ~40 | ✅ 50% reduction |
| Scripts | 83 | ~40 | ✅ 50% reduction |
| KG Quality | Unknown | Scored | ✅ Tracked |

---

## 🚨 RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking healing | HIGH | Add tests FIRST, test on non-critical cron |
| Wrong healing action | HIGH | Circuit breaker + human fallback |
| False positive healing | MEDIUM | Verify phase before/after |

---

## 💡 QUICK WINS (Today)

1. **Fix cron_error_healer** — Enable real execution (30 min)
2. **Add Verify phase** — Check if healing worked (15 min)
3. **Test Error Action Matrix** — Map our errors to strategies (20 min)

---

## 📚 REFERENCES

- [Self-Healing Agent Pattern - DEV Community](https://dev.to/the_bookmaster/the-self-healing-agent-pattern-how-to-build-ai-systems-that-recover-from-failure-automatically-3945)
- [Claude API Self-Healing Patterns - Claude Lab](https://claudelab.net/en/articles/api-sdk/claude-api-self-healing-agent-production-patterns)
- [Agentic SRE - Unite.AI](https://www.unite.ai/agentic-sre-how-self-healing-infrastructure-is-redefining-enterprise-aiops-in-2026/)
- [Self-Corrective Agent Architecture - EmergentMind](https://www.emergentmind.com/topics/self-corrective-agent-architecture)

---

*Plan Version: 2.0 — Research-Informed*
*Next Update: After Pillar 3 Phase 1 complete*
