# AUTONOMY ENGINE — LEVEL 4 PLAN
*Based on research + best practices 2025/2026*

---

## 📊 RESEARCH INSIGHTS (from web research)

### Key Patterns Found:

| Pattern | Source | What it means |
|---------|--------|---------------|
| **VIGIL Framework** | Medium/Dec 2025 | Sibling supervisor agent (out-of-band) watches primary agent |
| **Actor-Critic Loop** | LangGraph pattern | Actor attempts → Critic validates → Loop if failed |
| **Error-as-Prompt** | Self-healing agents | Feed errors back as context for retry |
| **Affective Profiling** | VIGIL/EmoBank | Detect "soft failures" via emotional logs (anxiety=delay) |
| **Decision Layer Guardrails** | Galileo/NIST | Proactive constraints at reasoning level, not output filtering |
| **Staged Autonomy** | AWS Security Matrix | Autonomy scales with control maturity |
| **Dual-Control** | ITSM.tools | Destructive ops need human approval |
| **Selective Rollback** | Rubrik Agent Rewind | Trace agent actions to specific state |

---

## 🎯 ARCHITECTURE: SIR HAZECLAW AUTONOMY ENGINE

### Core Pattern: VIGIL-Inspired Sibling Supervisor

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMY ENGINE (v1)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐         ┌──────────────┐                │
│  │ PRIMARY AGENT│         │  SUPERVISOR   │                │
│  │  (Sir Hazel) │◄────────│  (Watcher)    │                │
│  └──────┬───────┘         └───────┬──────┘                │
│         │                         │                        │
│         │  Actions + Logs         │  Observes + Decides    │
│         ▼                         ▼                        │
│  ┌─────────────────────────────────────────────┐          │
│  │           OBSERVABILITY LAYER                │          │
│  │  • Action Log (what was done)               │          │
│  │  • Error Log (what failed)                  │          │
│  │  • Affective State (soft failure detection) │          │
│  │  • Rollback Snapshots                       │          │
│  └─────────────────────────────────────────────┘          │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────┐          │
│  │           DECISION MATRIX                   │          │
│  │  Category → Backup → Test → Approval        │          │
│  └─────────────────────────────────────────────┘          │
│                           │                                │
│                           ▼                                │
│  ┌─────────────────────────────────────────────┐          │
│  │           EXECUTION ENGINE                   │          │
│  │  • Auto-execute (small/medium)               │          │
│  │  • Ask [NAME_REDACTED] (large/critical)                 │          │
│  │  • Rollback on failure                      │          │
│  └─────────────────────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 IMPLEMENTATION PHASES

### Phase 1: Foundation (Day 1)

**1.1 Observability Layer**
```
Components:
├── Action Log:     /workspace/ceo/memory/autonomy/action_log.md
├── Error Log:      /workspace/ceo/memory/autonomy/error_log.md  
├── Affective State: /workspace/ceo/memory/autonomy/affective_state.json
└── Rollback Store:  /workspace/ceo/backups/ (git snapshots)
```

**1.2 Decision Matrix (Heartbeat Decision Engine)**
```
Check → Categorize → Act → Verify → Report

TINY (no backup):
- Temp file cleanup
- Log rotation
→ Execute, log, done

SMALL (auto-backup):
- KG updates
- Memory edits
- Minor script fixes
→ Backup → Execute → Verify → Log

MEDIUM (test required):
- Cron changes
- Script modifications
- New configurations
→ Snapshot → Test → Execute → Verify → Log

LARGE (ask first):
- New systems
- Core config changes
- Security updates
→ Full backup → Test → Ask [NAME_REDACTED] → Execute if approved

CRITICAL (dual control):
- Gateway changes
- External communications
- Financial/destructive ops
→ Full backup + Full test → Explicit [NAME_REDACTED] approval required
```

**1.3 Heartbeat Integration**
```
Heartbeat receives signal
    ↓
Supervisor analyzes (5-30s)
    ↓
Decision: TINY/SMALL/MEDIUM/LARGE/CRITICAL
    ↓
Action based on category
    ↓
Result: Executed / Rolled back / Escalated
    ↓
Report only if: new error, fix succeeded, or needs attention
```

---

### Phase 2: Self-Healing (Day 2-3)

**2.1 Error-as-Prompt Pattern**
```
When error detected:
1. Capture error context (what, where, when)
2. Format as structured prompt
3. Feed to Learning Loop for retry
4. If retry succeeds → apply fix
5. If retry fails → rollback + alert
```

**2.2 Affective State Tracking (Soft Failure Detection)**
```
Track patterns like:
- "success but took 97s longer than expected" → anxiety
- "completed without errors but result seems off" → confusion
- "same error 3x in a row" → escalating concern

Rules (deterministic, NOT LLM):
- Error rate > 10% → critical
- Response time > 5s → warning
- Same error 3x → alert
- Cron fails 2x → auto-retry once
```

**2.3 Auto-Retry with Exponential Backoff**
```
Attempt 1: Immediate
Attempt 2: 30s wait
Attempt 3: 2min wait
Attempt 4: Escalate to [NAME_REDACTED]
```

---

### Phase 3: Advanced Autonomy (Day 4-5)

**3.1 Sibling Supervisor Pattern**
```
Primary Agent ([NAME_REDACTED]):
- Does the actual work
- Produces behavioral logs

Supervisor Agent ([NAME_REDACTED]-Observer):
- Watches from outside
- Analyzes patterns
- Proposes fixes as "artifacts"
- NEVER touches live system
- Can trigger rollbacks

This is the VIGIL pattern adapted for [NAME_REDACTED].
```

**3.2 Actor-Critic Loop for Learning**
```
Actor ([NAME_REDACTED]):
- Attempts task
- Generates code/config/etc

Critic (Learning Loop):
- Validates output against criteria
- Checks: does it work? is it safe? is it better?

If approved → proceed
If rejected → feedback + retry (up to 3x)
```

**3.3 Knowledge Graph Integration**
```
Every autonomous action:
1. Log to KG: what was done, why, result
2. Create causal link: trigger → action → outcome
3. Use KG to detect patterns: "issue X happened 5x, always before Y"
```

---

## 🛡️ SAFETY ARCHITECTURE

### Backup Strategy

| Change Size | Backup Method | Retention |
|-------------|--------------|-----------|
| TINY | None (reversible) | - |
| SMALL | Copy to `/backups/small/` | 24h |
| MEDIUM | Git snapshot + copy | 7 days |
| LARGE | Full system snapshot + git | 30 days |
| CRITICAL | Full backup + verified snapshot | Until confirmed |

### Rollback Triggers

```
Automatic rollback if:
- Exit code != 0 (command failed)
- Gateway unreachable > 60s
- Error rate increases after change
- Metrics show degradation
- User explicitly requests rollback
```

### Rollback Procedure

```bash
1. Detect failure
2. Identify last good state (from snapshots)
3. Restore from snapshot
4. Verify system health
5. Alert: "Rolled back automatically. Details: ..."
6. Log: what failed, what was restored, why
```

---

## 📊 DECISION MATRIX (Detailed)

### TINY (Execute without backup)
- Log cleanup < 100 files
- Temp file removal
- Memory consolidation (read-only ops)
- Health check pings

### SMALL (Backup then execute)
- KG entity add/update (non-critical)
- Memory file edits (learnings, notes)
- Script fixes (known patterns)
- Cron re-trigger (same job)
- Threshold updates in config

### MEDIUM (Snapshot + Test + Execute)
- New cron job creation
- Script modifications (code changes)
- Config value changes
- New tool/skill registration
- Dependency updates

### LARGE (Full backup + Test + Ask [NAME_REDACTED])
- New systems/services
- Architecture changes
- Multiple script changes at once
- External integrations
- Security policy changes

### CRITICAL (Full backup + Full test + Explicit approval)
- Gateway config changes
- User-facing communications
- Financial transactions
- Destructive operations (delete, truncate)
- Permission changes

---

## 🚀 IMPLEMENTATION CHECKLIST

### Day 1 - Foundation
- [ ] Create `/workspace/ceo/memory/autonomy/` directory structure
- [ ] Create `action_log.md` template
- [ ] Create `error_log.md` template
- [ ] Create `affective_state.json` with initial state
- [ ] Create `decision_matrix.py` script
- [ ] Create `backup_manager.py` script
- [ ] Create `rollback_executor.py` script
- [ ] Integrate into HEARTBEAT.md

### Day 2 - Self-Healing
- [ ] Implement error-as-prompt pattern
- [ ] Create soft failure detection rules
- [ ] Create auto-retry logic
- [ ] Add exponential backoff
- [ ] Test error recovery

### Day 3 - Actor-Critic Loop
- [ ] Connect Learning Loop as critic
- [ ] Implement validation checks
- [ ] Create retry-with-feedback loop
- [ ] Add to decision matrix

### Day 4-5 - Advanced
- [ ] Implement Supervisor agent pattern
- [ ] Create artifact generation for fixes
- [ ] Add KG pattern detection
- [ ] Test full autonomy cycle

---

## 📈 SUCCESS METRICS

| Metric | Target | How to Measure |
|--------|--------|---------------|
| Mean Time To Recovery (MTTR) | < 60s | Time from error to fix |
| False Positive Rate | < 5% | Unnecessary rollbacks |
| Autonomous Fix Rate | > 80% | Fixes without [NAME_REDACTED] |
| Rollback Accuracy | 100% | Failed rollbacks = 0 |
| Silent Healing | > 90% | Issues fixed before alert |

---

## 🔄 EVALUATION FRAMEWORK

After each autonomous action, evaluate:
1. **Was the action correct?** (Validator check)
2. **Was backup sufficient?** (Could we rollback?)
3. **Was the category right?** (Appropriate autonomy level?)
4. **What would we do different?** (Learning)

Store evaluations in `autonomy/evaluation_log.md`

---

*Plan created: 2026-04-13*
*Research-based improvements from: VIGIL framework, LangGraph patterns, NIST AI RMF, AWS Security Matrix, Rubrik Agent Rewind*