# Phase 7: Meta Learning Integration Plan
**Datum:** 2026-04-21
**Status:** Research Complete → Implementation Planning

---

## 📊 Research Summary (Best Practices aus NeurIPS 2025 + arXiv)

### Key Papers
| Paper | Year | Core Finding |
|-------|------|-------------|
| **MetaAgent** | 2025 | Meta tool learning - builds persistent knowledge base from tool-use history |
| **SiriuS** | NeurIPS 2025 | Experience library + bootstrapped reasoning for multi-agent |
| **Self-Challenging Agents** | NeurIPS 2025 | Self-generated tasks + test-based rewards |
| **Reflexion** | 2023 | Natural language reflections stored and reused |
| **SICA** | 2025 | Self-Improving Coding Agent - skill library for persistent improvement |

### Best Practices Pattern
```
1. EXPERIENCE REPLAY: Store successful trajectories, reuse in-context
2. SELF-GENERATED CURRICULA: Agent creates own training data
3. HIERARCHICAL META-LEARNING: Meta-level learns from lower-level performance
4. BIDIRECTIONAL FEEDBACK: Lower-level → Meta → Lower-level闭环
5. PERSISTENT KNOWLEDGE BASE: Incremental learning without weight updates
```

---

## 🎯 Architecture: Three-Level Self-Improving System

```
┌─────────────────────────────────────────────────────────────────┐
│                         META LEARNING LAYER                      │
│                   (meta_learning_controller.py)                 │
│                                                                 │
│  Pattern Weights ←── Feedback ───────────────────────────────┐ │
│         │                   │                                  │ │
│         │              ┌────▼────┐                             │ │
│         │              │  KG +   │                             │ │
│         │              │ Events  │                             │ │
│         │              └────┬────┘                             │ │
│         │                   │                                  │ │
│         ▼                   ▼                                  │ │
│  ┌─────────────────────────────────────────────────────────┐   │ │
│  │              LEARNING LOOP LAYER                        │   │ │
│  │                  (learning_loop_v3.py)                  │   │ │
│  │                                                          │   │ │
│  │  Pattern Selection ←── Pattern Weights ─────────────┐  │   │ │
│  │         │                                            │  │   │ │
│  │         ▼                                            │  │   │ │
│  │  Hypotheses ──→ Validation Gate ──→ Score Update    │  │   │ │
│  │         │                         │                   │  │   │ │
│  │         │                    Events to Bus            │  │   │ │
│  │         ▼                         │                   │  │   │ │
│  └────────┼─────────────────────────┼───────────────────┘  │   │ │
│            │                         │                      │   │ │
│            │     ┌───────────────────┘                      │   │ │
│            │     ▼                                          │   │ │
│  ┌─────────▼─────────────────────────────────────────────┐ │   │ │
│  │              CAPABILITY EVOLVER LAYER                   │ │   │ │
│  │                (run_smart_evolver.sh)                  │ │   │ │
│  │                                                            │ │   │
│  │  Gene Selection ←── Stagnation Signals ←────────────┐ │ │   │ │
│  │         │                                          │ │ │   │ │
│  │         ▼                                          │ │ │   │ │
│  │  Mutation → Validation → Success/Failure ──→ Event │ │ │   │ │
│  │                                               │      │ │ │   │ │
│  └───────────────────────────────────────────────┼──────┼─┘ │   │ │
│                                                  │      │    │ │
│                                                  ▼      │    │ │
│                    ┌─────────────────────────────┐      │    │ │
│                    │         EVENT BUS           │◄─────┘    │ │
│                    │   (events.jsonl + signals) │           │ │
│                    └─────────────────────────────┘           │ │
└──────────────────────────────────────────────────────────────┘ │
                                                                   │
                    ▲                        ▲                    │
                    │                        │                    │
              ┌─────┴────────────────────────┴─────┐              │
              │         KNOWLEDGE GRAPH             │              │
              │       (kg_entities + relations)   │              │
              │                                    │              │
              │  Entities: 467  Relations: 994      │              │
              └────────────────────────────────────┘              │
```

---

## 🔧 Implementation Phases

### Phase 7.1: Event Bus Enhancement für Meta Learning
** Ziel:** Meta Learning Controller bekommt eigene Events

**Events hinzufügen:**
```
learning_meta_feedback        # Loop → Meta mit pattern performance
meta_pattern_weights_updated  # Meta → Loop mit neuen weights
meta_insight_generated        # Meta → KG/EventBus mit erkenntnissen
```

**Files to modify:**
- `learning_loop_v3.py`: Emit `learning_meta_feedback` event
- `event_bus.py`: Handle new event types

### Phase 7.2: Meta Learning Controller Integration
**Ziel:** Meta Controller liest Loop Events und passt weights an

**Changes in `meta_learning_controller.py`:**
```python
# New: Read from Event Bus
def read_learning_loop_feedback():
    events = read_events('learning_meta_feedback', last_n=10)
    for evt in events:
        pattern_id = evt['data']['pattern_id']
        success_rate = evt['data']['success_rate']
        # Update pattern weight accordingly
        
# New: Write back to Event Bus
def emit_pattern_weights():
    weights = calculate_new_weights()
    emit_event('meta_pattern_weights_updated', weights)
```

### Phase 7.3: Learning Loop verwendet Meta Weights
**Ziel:** Loop liest `meta_pattern_weights_updated` und nutzt weights

**Changes in `learning_loop_v3.py`:**
```python
# In pattern selection phase:
meta_weights = read_meta_pattern_weights()
if meta_weights:
    # Adjust pattern selection probability by meta weights
    for pattern in candidates:
        base_score = pattern['score']
        meta_adjustment = meta_weights.get(pattern['id'], 1.0)
        adjusted_score = base_score * meta_adjustment
```

### Phase 7.4: KG Integration
**Ziel:** Meta Insights werden in KG gespeichert

**Changes:**
```python
# Meta learning insights → KG
def emit_meta_insight(insight_type, content):
    kg_entity = {
        'type': 'meta_insight',
        'insight_type': insight_type,
        'content': content,
        'confidence': confidence,
        'source': 'meta_learning_controller'
    }
    add_to_kg(kg_entity)
    emit_event('meta_insight_generated', kg_entity)
```

### Phase 7.5: Closed-Loop Validation
**Ziel:** System validiert ob Meta-Änderungen actually helfen

```
Loop Score BEFORE meta change
        ↓
Meta changes pattern weights
        ↓
Loop runs with new weights
        ↓
Loop Score AFTER meta change
        ↓
Meta learns: improved/declined → adjust strategy
```

---

## 📋 Implementation Checklist

### Phase 7.1: Event Bus Enhancement
- [ ] Add `meta_feedback` event type to event_bus.py
- [ ] Add `meta_pattern_weights` event type to event_bus.py
- [ ] Test event publishing for meta events

### Phase 7.2: Meta Controller Integration  
- [ ] Add `read_learning_loop_feedback()` to meta_learning_controller.py
- [ ] Add `emit_pattern_weights()` to meta_learning_controller.py
- [ ] Add state fields: `last_meta_update`, `meta_weight_history`
- [ ] Run integration test

### Phase 7.3: Learning Loop uses Meta Weights
- [ ] Add `read_meta_pattern_weights()` to learning_loop_v3.py
- [ ] Add meta weight adjustment in pattern selection
- [ ] Log meta adjustment impact

### Phase 7.4: KG Integration
- [ ] Add `emit_meta_insight()` function
- [ ] KG stores meta_insight entities
- [ ] KG Sync with meta events

### Phase 7.5: Closed-Loop Validation
- [ ] Track score delta before/after meta changes
- [ ] Meta controller learns from validation results
- [ ] Confidence scoring for meta decisions

---

## 🧪 Test Plan

### Integration Test Sequence
```bash
# 1. Run Learning Loop → should emit meta feedback
python3 SCRIPTS/automation/learning_loop_v3.py

# 2. Run Meta Controller → should read feedback, emit weights
python3 scripts/meta_learning_controller.py

# 3. Run Learning Loop again → should use meta weights
python3 SCRIPTS/automation/learning_loop_v3.py

# 4. Verify score improvement (or record baseline)
# 5. Run Capability Evolver → test multi-level integration
bash SCRIPTS/automation/run_smart_evolver.sh

# 6. Full system test
```

### Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Meta feedback events | ≥1 per Loop run | Event count |
| Pattern weight updates | ≥1 per hour | State diff |
| Loop score improvement | >0 when meta active | Score delta |
| KG meta_insight entities | Growing | KG count |
| Closed-loop accuracy | >70% | Meta decision validation |

---

## 📁 Files to Modify

| File | Changes |
|------|---------|
| `SCRIPTS/automation/event_bus.py` | New event types |
| `SCRIPTS/automation/learning_loop_v3.py` | Meta event emit + consume |
| `ceo/scripts/meta_learning_controller.py` | Event Bus read/write |
| `SCRIPTS/automation/ralph_maintenance_loop.py` | Include meta sync |
| `data/learning_loop_state.json` | New meta fields |

---

## 🔗 Reference: MetaAgent Architecture (aus arXiv 2508.00271)

> "MetaAgent incrementally refines its reasoning and tool-use strategies, without changing model parameters or requiring further post-training."

Our implementation mirrors this:
- **Incremental refinement** → Pattern weights adjust over time
- **No parameter changes** → All via state/logs/KG
- **Tool-use history** → Events provide trajectory data
- **Persistent knowledge** → KG stores meta_insights

---

_Erstellt: 2026-04-21 | Research: NeurIPS 2025 + arXiv | Status: Ready for Implementation_