# 🎯 Unified Learning Architecture - KONSOLIDIERT ✅
**Erstellt:** 2026-04-18  
**Status:** ALL PHASES COMPLETE ✅  
**Version:** 2.0 (Consolidated)

---

## 📊 Research Insights (from Web Search)

### Best Practices 2026:
1. **Unified Context Layer** (Atlan): "Single source of truth - Every AI agent draws from the same context, governed by the same policies, using the same canonical definitions"
2. **Graphiti Temporal Graphs**: Track how facts change over time, maintain provenance, support learned ontology
3. **HyperAgents (Meta)**: Autonomous self-improvement, break "maintenance wall"
4. **Knowledge Graph + Vectors**: Hybrid search (BM25 + fuzzy vectors + KG structure)
5. **Agentic Memory Tiers**: Short-term, episodic, semantic, procedural (LIFE framework)

### Key Architecture Principles:
- **Single Source of Truth** - One KG, not multiple overlapping systems
- **Event-Driven** - Events flow between components, not polling
- **Temporal Tracking** - All changes timestamped, auditable
- **Unified Context** - Same definitions across all agents

---

## 🔴 PROBLEM STATEMENT

**Aktuell haben wir 3+ partially overlapping Systems:**

| System | Problem |
|--------|---------|
| **Learning Loop** | `learning_core.py` fehlt, nutzt veraltete Dateien |
| **Deep Learning (Phases 1-6)** | 17 separate Scripts, keine zentrale Steuerung |
| **Evolver** | Separater Workflow, nicht mit KG integriert |
| **KG** | 407 entities aber nicht optimal als zentrale DB |

**Symptome:**
- TSR wird in 2 Systemen getrackt
- Failure patterns redundant
- Exploration Budget nicht mit Evolver verbunden
- Keine klare Datenstruktur (relations als dict statt list)

---

## 🎯 ZIEL-ARCHITEKTUR

```
┌──────────────────────────────────────────────────────────────────┐
│                    UNIFIED LEARNING ARCHITECTURE                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              CENTRAL KNOWLEDGE GRAPH (KG)              │     │
│  │         Single Source of Truth - 407 entities          │     │
│  │         + Temporal tracking (Graphiti-style)           │     │
│  └─────────────────────────────────────────────────────────┘     │
│                              ▲                                    │
│                              │                                    │
│         ┌────────────────────┼────────────────────┐              │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ SHORT-TERM  │    │   EPISODIC  │    │  SEMANTIC    │        │
│  │   memory    │    │   memory    │    │   memory     │        │
│  │ (session)   │    │ (failures)  │    │   (KG sync)  │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│         │                    │                    │              │
│         └────────────────────┼────────────────────┘              │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │              UNIFIED LEARNING CONTROLLER                  │     │
│  │                   learning_unified.py                     │     │
│  └─────────────────────────────────────────────────────────┘     │
│                              ▲                                    │
│                              │                                    │
│         ┌────────────────────┼────────────────────┐              │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   TASK      │    │   EVAL      │    │   STRATEGY  │        │
│  │  EXECUTOR   │    │  + LEARN    │    │   MUTATOR   │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📋 PHASE 1: Data Model Consolidation

### 1.1 KG Schema Fixes
```python
# Current (PROBLEMATIC):
kg["relations"] = { "0": {...}, "1": {...} }  # dict of dicts

# Target (CLEAN):
kg["relations"] = [{ "from": "...", "to": "...", "type": "...", ... }]
```

### 1.2 Unified Learning Entity Types
```
Entity Types in KG:
├── learning              # Meta-learnings (priority, observation, action)
├── task_result          # Task executions (success/failure, duration)
├── failure_pattern      # Causal failure chains
├── strategy             # Exploration strategies
├── exploration_run      # Exploration vs exploitation decisions
├── experience           # Dynamic experience memory entries
└── slo_status           # SLO compliance tracking
```

### 1.3 Event Schema
```
Events:
├── task_completed        # → Updates task_result, triggers evaluation
├── failure_detected     # → Logs to failure_logger, updates KG
├── exploration_triggered # → Logs exploration_run, updates budget
├── strategy_mutated     # → Creates strategy mutation, logs to KG
└── slo_breached         # → Triggers SRE Culture, updates KG
```

---

## 📋 PHASE 2: Script Consolidation

### 2.1 Replace Multiple Scripts with Unified Controller

**Current (17 scripts):**
```
failure_logger.py           → merged into learning_unified.py
meta_learning_core.py       → merged into learning_unified.py
learning_to_learn.py        → merged into learning_unified.py
dynamic_experience_memory.py → merged into learning_unified.py
cross_domain_miner.py       → merged into learning_unified.py
sre_culture.py              → merged into learning_unified.py
exploration_budget.py       → merged into learning_unified.py
strategy_mutator.py         → merged into learning_unified.py
kg_learning_integrator.py   → merged into learning_unified.py
... (plus 8 more phase scripts)
```

**Target (3 core scripts):**
```
learning_unified.py     # Main controller - ONE ENTRY POINT
learning_events.py      # Event bus + handlers
learning_config.json    # Central configuration
```

### 2.2 API Design for learning_unified.py
```python
# Commands:
python3 learning_unified.py --task-complete <id>     # Log task result
python3 learning_unified.py --failure "<desc>"       # Log failure
python3 learning_unified.py --analyze                # Run analysis cycle
python3 learning_unified.py --sync-kg               # Sync to KG
python3 learning_unified.py --report                # Full report
python3 learning_unified.py --status                # Quick status
```

### 2.3 Remove/Deprecate Scripts
```
DEPRECATED (remove after migration):
├── phase1_integrator.py
├── phase2_integrator.py
├── phase3_integrator.py
├── phase4_integrator.py
├── phase5_integrator.py
├── phase6_integrator.py
├── learning_core.py (never existed)
├── kg_learning_integrator.py (merged)
└── [5 more redundant scripts]
```

---

## 📋 PHASE 3: Event-Driven Architecture

### 3.1 Event Bus Implementation
```python
# learning_events.py
class LearningEventBus:
    def publish(self, event_type, data):
        """Publish event to all subscribers"""
        
    def subscribe(self, event_type, handler):
        """Subscribe handler to event type"""
        
# Event Types:
TASK_COMPLETED = "task_completed"
FAILURE_DETECTED = "failure_detected"
EXPLORATION_TRIGGERED = "exploration_triggered"
STRATEGY_MUTATED = "strategy_mutated"
SLO_BREACHED = "slo_breached"
META_LEARNED = "meta_learned"
```

### 3.2 Event Handlers
```
Handler Pipeline:
1. task_completed → evaluation_to_learning.py → updates learning_signal
2. failure_detected → failure_logger.py → kg_causal_updater.py
3. exploration_triggered → exploration_budget.py → strategy_mutator.py
4. strategy_mutated → kg_learning_integrator.py → KG update
5. slo_breached → sre_culture.py → incident logging
```

---

## 📋 PHASE 4: Knowledge Graph Optimization

### 4.1 KG Restructure
```python
# Clean schema:
{
    "entities": { "entity_id": { "type": "...", "properties": {...} } },
    "relations": [ { "from": "...", "to": "...", "type": "...", "weight": 0.9 } ],
    "updated_at": "ISO timestamp",
    "version": "2.0"
}
```

### 4.2 Temporal Tracking (Graphiti-style)
```python
# Each entity has temporal properties:
{
    "created_at": "2026-04-18T...",
    "last_accessed": "2026-04-18T...",
    "version_history": [
        { "timestamp": "...", "changes": {...} }
    ],
    "provenance": "source_system"
}
```

### 4.3 Indexes for Fast Query
```python
# Pre-computed indexes:
kg["indexes"] = {
    "by_type": { "learning": ["id1", "id2"], "task_result": [...] },
    "by_timestamp": { "2026-04-18": ["id1", "id2"] },
    "by_source": { "failure_logger": ["id1"], "meta_learning": [...] }
}
```

---

## 📋 PHASE 5: Evolver Integration

### 5.1 Current Evolver Flow (ISOLATED)
```
prompt_evolution_engine.py → strategy_mutations.json (standalone)
evolver_signal_bridge.py → reads KG, writes back
mad_dog_controller.sh → separate process
```

### 5.2 Target Evolver Flow (INTEGRATED)
```
learning_unified.py
    │
    ├── triggers evolver on stagnation
    ├── reads KG for strategy candidates
    ├── validates mutations against KG
    └── applies mutations with rollback
```

### 5.3 Evolver Triggers
```
Trigger Conditions:
├── Exploration stagnation (5+ failed runs)
├── TSR below threshold (< 0.75)
├── Meta-learning score plateau
├── New failure patterns detected
└── Manual trigger via learning_unified.py --evolve
```

---

## 📋 PHASE 6: Migration Path

### Step 1: Create learning_unified.py (NEW)
```bash
# Create unified script
touch scripts/learning_unified.py
```

### Step 2: Run parallel with existing
```bash
# Both systems run, compare outputs
python3 learning_unified.py --status  # NEW
python3 failure_logger.py --stats     # OLD (for comparison)
```

### Step 3: Migrate data
```python
# Migrate learning_loop_state.json → KG entities
# Migrate exploration_budget.json → KG exploration_run entities
# Migrate strategy_mutations.json → KG strategy entities
```

### Step 4: Deprecate old scripts
```bash
# After 1 week validation, remove phase integrators
rm scripts/phase*_integrator.py
```

---

## 📊 IMPLEMENTATION TIMELINE

| Phase | Task | Duration | Risk |
|-------|------|----------|------|
| 1 | KG Schema Fix | 1h | LOW |
| 2 | learning_unified.py | 3h | MEDIUM |
| 3 | learning_events.py | 2h | MEDIUM |
| 4 | KG Optimization | 2h | MEDIUM |
| 5 | Evolver Integration | 2h | HIGH |
| 6 | Migration + Testing | 3h | HIGH |

**Total: ~13 hours** (spread over 2-3 days)

---

## ✅ ACCEPTANCE CRITERIA

After consolidation:
1. **Single Entry Point** - `python3 learning_unified.py` does everything
2. **No Data Loss** - All existing data migrated to KG
3. **Event-Driven** - Events flow through event bus
4. **TSR Improved** - From 0.763 → 0.80+
5. **No Redundancy** - Each piece of info stored once
6. **Evolver Connected** - Evolver reads from/writes to KG

---

## 🚨 RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Data loss during migration | Backup before migration, run parallel |
| Evolver breaks during integration | Keep evolver_signal_bridge.py as fallback |
| TSR drops during transition | Gradual rollout, monitor closely |
| Learning Loop breaks | Keep learning_loop_state.json as backup |

---

## 📁 FILES TO CREATE

```
scripts/learning_unified.py       # Main unified controller
scripts/learning_events.py        # Event bus + handlers
scripts/learning_migrator.py      # Data migration tool
config/learning_config.json       # Central config
```

## 📁 FILES TO DEPRECATE (after migration)

```
scripts/phase1_integrator.py
scripts/phase2_integrator.py
scripts/phase3_integrator.py
scripts/phase4_integrator.py
scripts/phase5_integrator.py
scripts/phase6_integrator.py
scripts/learning_core.py (doesn't exist)
scripts/kg_learning_integrator.py (merged)
scripts/failure_logger.py (merged)
scripts/meta_learning_core.py (merged)
... (10 more redundant scripts)
```

---

*Dieser Plan basiert auf: Atlan Unified Context Layer, Graphiti Temporal Graphs, Meta HyperAgents, LIFE Memory Framework*