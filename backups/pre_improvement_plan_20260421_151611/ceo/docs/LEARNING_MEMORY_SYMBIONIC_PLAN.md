# Learning ↔ Memory Symbiosis Optimization Plan
## Sir HazeClaw — Phase 9: Closed-Loop Memory-Learning Integration

**Created:** 2026-04-21  
**Based on:** NeurIPS 2025 Research + Memory Systems Best Practices (Mem0, Letta, Claude Diary)  
**Status:** READY FOR IMPLEMENTATION

---

## Research Foundation

### Best Practices from Industry & Academia

#### 1. Three Memory Types (Tulving Taxonomy — adopted by Mem0, Letta, LangChain)

| Type | Description | Our Implementation |
|------|-------------|-------------------|
| **Semantic Memory** | Facts, knowledge, user preferences | KG (entities, relations) |
| **Episodic Memory** | Time-stamped events, past experiences | Event Bus + daily memory files |
| **Procedural Memory** | Skills, behaviors, automation | Learnings + Skills + Scripts |

**Key Insight:** Consolidation pathways between types:
```
Episodic → Semantic (generalization of patterns)
Semantic → Procedural (patterns → automated skills)
```

#### 2. Experience Replay Pattern (SiriuS, Self-Gen In-Context Examples)

```
Store successful trajectories → Reuse in future tasks
```
- Our case: Successful learning iterations stored as Learnings
- Reused via: `get_relevant_learnings(context=...)` for similar tasks

#### 3. Self-Reflection Loop (Reflexion, Self-Refine)

```
Action → Observe → Reflect → Adapt → Action
```
- Ralph Loop already implements this
- Learnings Service provides the "reflection" storage

#### 4. Claude Diary Pattern (fsck.com, rlancemartin)

```
Session → Observations → Pattern Analysis → Rules Update
```

**Our equivalent:**
```
Session → Event Bus → Learnings Service → KG Sync → Memory files
```

#### 5. Letta Benchmark Finding

> "Filesystem scores 74% on memory tasks, beating specialized vector-store memory libraries"

**Our implication:** Keep it simple. Markdown/JSON files > complex vector DBs for our scale.

---

## Current Architecture (Before)

```
┌─────────────────────────────────────────────────┐
│                  EVENT BUS                      │
│        (Episodic Memory — Events)               │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              LEARNINGS SERVICE                   │
│      (Structured Learnings — Procedural)        │
└────────────────────┬────────────────────────────┘
                     │ One-way: Learnings → KG
┌────────────────────▼────────────────────────────┐
│              KNOWLEDGE GRAPH                     │
│       (Semantic Memory — Facts/Knowledge)         │
└─────────────────────────────────────────────────┘
```

**Problems:**
1. KG → Learnings: NOT BIDIRECTIONAL
2. Learnings → Memory files: NO SYNC
3. No consolidation pathway: Episodic → Semantic → Procedural
4. No strategy effectiveness feedback into memory
5. Ralph/Meta/Other agents have separate learnings, not shared

---

## Target Architecture (After)

```
┌─────────────────────────────────────────────────────────────────┐
│                         MEMORY LAYER                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  EPISODIC    │  │  SEMANTIC    │  │  PROCEDURAL  │        │
│  │  (Events)    │→ │  (KG)        │→ │  (Learnings) │        │
│  │              │  │              │  │              │        │
│  │  Event Bus   │  │  Knowledge   │  │  Skills/     │        │
│  │  Daily Notes │  │  Graph       │  │  Strategies  │        │
│  │  Logs        │  │  Entities    │  │  Scripts     │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
│         │                  │                  │                 │
│         │    CONSOLIDATION PATHWAYS           │                 │
│         │         (Pattern Extraction)         │                 │
│         └──────────────────┼──────────────────┘                 │
│                            ↓                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LEARNINGS SERVICE (Hub)                     │   │
│  │                                                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │  Ralph     │  │   Meta     │  │  Evolver   │        │   │
│  │  │  Learning  │  │  Learning  │  │            │        │   │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘        │   │
│  │        │               │               │                │   │
│  │        └───────────────┼───────────────┘                │   │
│  │                        ↓                                 │   │
│  │              Unified Learnings Index                      │   │
│  │              (Strategy Effectiveness)                     │   │
│  │                        │                                 │   │
│  │                        ↓                                 │   │
│  │        ┌───────────────────────────────┐                │   │
│  │        │    DECISION ENGINE (NEW)       │                │   │
│  │        │    "What should I do next?"    │                │   │
│  │        └───────────────────────────────┘                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│         ┌──────────────────┼──────────────────┐                │
│         ↓                  ↓                  ↓                │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐          │
│  │ Ralph Loop │    │ Meta Ctrl  │    │ Evolver    │          │
│  │ (Decide)   │    │ (Adapt)    │    │ (Act)      │          │
│  └────────────┘    └────────────┘    └────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Bidirectional KG ↔ Learnings Sync

**Goal:** Learnings and KG stay in sync bidirectionally

| Step | Action | File |
|------|--------|------|
| 1.1 | Add `sync_to_kg()` method to LearningsService | `learnings_service.py` |
| 1.2 | Add `sync_from_kg()` method to read KG entities as learnings | `learnings_service.py` |
| 1.3 | Create KG→Learnings cron (hourly) | New cron |
| 1.4 | Add `kg_entity_created` event handler in LearningsService | `learnings_service.py` |
| 1.5 | Test bidirectional sync | Manual test |

**New Method Example:**
```python
def sync_from_kg(self):
    """Read KG entities and convert notable ones to learnings."""
    kg = load_kg()
    for entity in kg['entities'].values():
        if entity.get('type') == 'LearningPattern':
            self.record_learning(
                source="KG Consolidation",
                category="pattern",
                learning=f"Pattern: {entity.get('name')}",
                context="pattern_matching",
                outcome="success"
            )
```

---

### Phase 2: Consolidation Pathway Engine

**Goal:** Automatic pattern extraction from events → KG → Learnings

| Step | Action | File |
|------|--------|------|
| 2.1 | Create `consolidation_engine.py` | New file |
| 2.2 | Implement episodic→semantic: Events → KG entities | `consolidation_engine.py` |
| 2.3 | Implement semantic→procedural: KG patterns → Learnings | `consolidation_engine.py` |
| 2.4 | Add confidence scoring (from Letta research) | `consolidation_engine.py` |
| 2.5 | Add memory decay for old events | `consolidation_engine.py` |

**Consolidation Rules:**
```
IF event_pattern appears 3+ times in 24h:
    → Create KG entity for pattern
    → Record as learning
    
IF learning has outcome=success 5+ times for same context:
    → Elevate to "strategy"
    → Increase strategy effectiveness score
```

---

### Phase 3: Strategy Effectiveness Feedback Loop

**Goal:** Learnings influence strategy choices, outcomes feed back

| Step | Action | File |
|------|--------|------|
| 3.1 | Add `strategy_feedback()` method | `learnings_service.py` |
| 3.2 | Modify Ralph Learning to call `strategy_feedback()` after each iteration | `ralph_learning_loop.py` |
| 3.3 | Modify Meta Learning to query effective strategies | `meta_learning_controller.py` |
| 3.4 | Add "strategy recommendations" to agent context | `learnings_service.py` |
| 3.5 | Ralph uses recommended strategies in next iteration | `ralph_learning_loop.py` |

**Feedback Loop:**
```
Ralph iteration → strategy X used → outcome recorded
                                      ↓
                           Strategy effectiveness updated
                                      ↓
                           Next iteration → strategy X recommended
```

---

### Phase 4: Decision Engine API

**Goal:** Single API for "What should I do next?"

| Step | Action | File |
|------|--------|------|
| 4.1 | Create `decision_engine.py` | New file |
| 4.2 | Implement `get_next_action(context)` | `decision_engine.py` |
| 4.3 | Implement `get_strategy_for_task(task_type)` | `decision_engine.py` |
| 4.4 | Add to LearningsService as convenience method | `learnings_service.py` |
| 4.5 | Integrate with Sir HazeClaw (me) | `sir_hazeclaw_learnings.py` |

**API Example:**
```python
ctx = ls.get_agent_context("Sir HazeClaw")
next_action = ls.decide_next_action(
    context="system_optimization",
    available_strategies=["diversity", "adaptive_lr", "exploration"]
)
# Returns: {"strategy": "diversity", "reasoning": "Most effective in last 10 runs"}
```

---

### Phase 5: Memory Decay & Confidence Scoring

**Goal:** Old/outdated learnings lose weight, recent ones have priority

| Step | Action | File |
|------|--------|------|
| 5.1 | Add timestamp tracking to all learnings | `learnings_service.py` |
| 5.2 | Implement decay function (exponential) | `learnings_service.py` |
| 5.3 | Add confidence score to learning queries | `learnings_service.py` |
| 5.4 | Prune learnings older than 30 days | `learnings_service.py` |
| 5.5 | Add cron for periodic pruning | New cron |

**Decay Formula:**
```
confidence = base_score * exp(-lambda * days_since_learning)
lambda = 0.05 (5% decay per day)
```

---

### Phase 6: Cross-Agent Learning Federation

**Goal:** All agents share learnings, not siloed

| Step | Action | File |
|------|--------|------|
| 6.1 | Add agent registration to LearningsService | `learnings_service.py` |
| 6.2 | Implement `get_learning_for_agent(agent, context)` | `learnings_service.py` |
| 6.3 | Add Health Monitor learnings → all agents | `health_monitor.py` |
| 6.4 | Add Self-Improver learnings → all agents | `agent_self_improver.py` |
| 6.5 | Document federation pattern | `LEARNINGS_SERVICE.md` |

---

### Phase 7: Persistent Memory Consolidation

**Goal:** Daily memory files contain learnings summaries

| Step | Action | File |
|------|--------|------|
| 7.1 | Create `memory_consolidator.py` | New file |
| 7.2 | Daily cron: Extract learnings → MEMORY.md summary | New cron |
| 7.3 | Weekly:KG health report in memory | New cron |
| 7.4 | Monthly: Strategy effectiveness report | New cron |
| 7.5 | Archive old learnings to `memory/archive/` | `learnings_service.py` |

---

### Phase 8: Testing & Validation

**Goal:** Verify closed-loop learning works

| Step | Action | File |
|------|--------|------|
| 8.1 | Create `test_symbiosis.py` | New file |
| 8.2 | Test: KG→Learnings sync | `test_symbiosis.py` |
| 8.3 | Test: Learnings→KG sync | `test_symbiosis.py` |
| 8.4 | Test: Consolidation pathway | `test_symbiosis.py` |
| 8.5 | Test: Strategy feedback loop | `test_symbiosis.py` |
| 8.6 | Deep test (all systems) | Manual run |

---

## File清单

### New Files
| File | Purpose |
|------|---------|
| `SCRIPTS/automation/consolidation_engine.py` | Pattern extraction engine |
| `SCRIPTS/automation/decision_engine.py` | Action recommendation API |
| `SCRIPTS/automation/test_symbiosis.py` | Integration tests |
| `backups/pre_learning_symbiosis_20260421_130941/` | Backup (done) |

### Modified Files
| File | Changes |
|------|---------|
| `learnings_service.py` | Bidirectional KG sync, decay, confidence |
| `ralph_learning_loop.py` | Strategy feedback |
| `meta_learning_controller.py` | Query effective strategies |
| `health_monitor.py` | Federation learnings |
| `agent_self_improver.py` | Federation learnings |
| `sir_hazeclaw_learnings.py` | Use decision engine |
| `LEARNINGS_SERVICE.md` | Update docs |

### New Crons
| Cron | Schedule | Purpose |
|------|----------|---------|
| KG→Learnings Sync | Hourly | KG entities → Learnings |
| Memory Consolidator | Daily 23:00 | Daily summary to MEMORY.md |
| Learnings Pruner | Weekly | Remove old learnings |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Learnings utilized in decisions | >80% | Count decisions using learnings |
| Strategy accuracy | >70% | Recommended strategies succeed |
| KG-Learnings consistency | 100% | Bidirectional sync verified |
| Consolidation pathway active | Yes | Patterns extracted from events |
| Memory decay working | Yes | Old learnings have lower confidence |

---

## Timeline

| Phase | Estimated Time | Priority |
|-------|----------------|----------|
| Phase 1 | 30 min | P0 |
| Phase 2 | 45 min | P1 |
| Phase 3 | 30 min | P1 |
| Phase 4 | 30 min | P2 |
| Phase 5 | 20 min | P2 |
| Phase 6 | 20 min | P2 |
| Phase 7 | 30 min | P3 |
| Phase 8 | 30 min | P3 |

**Total estimated:** ~4 hours (can be done in 2 sessions)

---

## References

- NeurIPS 2025: Self-Improving Agents (Yohei Nakajima compilation)
- arXiv 2512.13564: Memory in the Age of AI Agents
- Mem0 Research (arXiv 2504.19413): Scalable Long-Term Memory
- Letta Blog: Benchmarking AI Agent Memory
- Claude Diary Pattern (rlancemartin.github.io)
- fsck.com: Fixing Claude Code's Amnesia
- Tulving 1972: Episodic and Semantic Memory taxonomy

---

_Last Updated: 2026-04-21 13:10 UTC_
