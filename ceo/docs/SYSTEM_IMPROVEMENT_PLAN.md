# 🏥 SYSTEM IMPROVEMENT PLAN
## Sir HazeClaw — Basierend auf Best Practices

**Erstellt:** 2026-04-21  
**Backup:** `backups/pre_improvement_20260421_150547/`  
**Ziel:** System von 7/10 auf 9/10 verbessern

---

## Best Practices Recherche (Quellen)

### Learnings Feedback Loop
- **Agent Loop Pattern**: Observe → Decide → Act → Learn → (repeat)
- **Feedback Validation**: Separate performance measurement from business execution
- **Contextual Metadata**: Include confidence scores, task complexity, time spent
- **Dual-component Reflection**: Architecture die learning von execution trennt

### Event-Driven Architecture
- **Event-Carried State Transfer**: Events tragen alle nötigen Daten (keine extra calls)
- **Consumer Registry**: Alle wichtigen Event-Typen müssen konsumierte werden
- **Saga Pattern**: Für verteilte Transaktionen über Services
- **Event Aggregation**: Mehrere Events aggregieren zu einem Summary-Event

### Self-Improving Agents
- **Meta-Learning**: Agent lernt wie er lernen soll
- **Bayesian Optimization**: Unsicherheit umarmen, kontinuierlich verbessern
- **Feedback Loop**: Kontinuierliches Lernen von echten Resultaten
- **State Continuity**: Meta-Agent behält State über Iterationen

### Cron Best Practices
- **Lock Files**: Verhindern doppelte Runs
- **Heartbeat Monitoring**: Job "meldet sich" bei Monitoring Service
- **Structured Logging**: Zeitstempel, Script-Name, Status
- **Alerting**: Bei Failures automatisch alarmieren

### Knowledge Graph Maintenance
- **HARD DELETE**: Veraltete/dekategorisierte Daten physisch entfernen
- **SOFT DELETE**: Metadaten-Filtering (archived-Flag, Datum)
- **RETRIEVAL FILTERING**: Zur Query-Zeit irrelevante Ergebnisse filtern
- **Conservative Pruning**: Mit höherem Threshold starten, dann anpassen

---

## PHASE 1: Learnings Feedback Loop schliessen 🔴 CRITICAL

### Ziel
Learnings müssen AKTIV für Entscheidungen verwendet werden, nicht nur passiv gesammelt.

### Current Problem
```
Learnings schreiben → index.json (113 entries)
        ↓
   [NIEMAND liest sie aktiv]
        ↓
Decision Engine → "no learnings - default diversity"
Ralph → Recommendations nur geloggt, nicht verwendet
```

### Best Practice Solution
```
OBSERVE → DECIDE → ACT → LEARN → [FEEDBACK LOOP]
                              ↓
                    Learnings werden gelesen
                    und beeinflussen nächste Decision
```

### Tasks

#### 1.1 Decision Engine mit Learnings integrieren
```python
# decision_engine.py - BEFORE recommending strategy:
def get_strategy_for_task(self, task: str) -> dict:
    # Hole relevante Learnings VOR decision
    relevant = self.learnings.get_relevant_learnings(
        context=task, 
        limit=5
    )
    
    # Wenn Learnings existieren, nutze sie
    if relevant:
        # Baue Strategie-Empfehlung basierend auf Learnings
        strategy = self._learn_from_learnings(relevant)
        return {
            "strategy": strategy,
            "source": "learnings",
            "confidence": self._calculate_confidence(relevant)
        }
    
    # Fallback zu default
    return {"strategy": "diversity", "source": "default"}
```

#### 1.2 Ralph Loop Recommendations aktivieren
```python
# ralph_learning_loop.py - NACH jedem Run:
def after_iteration(self, result):
    # Check recommendations
    rec = self.learnings.get_recommended_strategy(
        context=self.pattern_source
    )
    
    # WENN recommendation exists, nutze sie für nächsten Run
    if rec.get('strategy'):
        self.next_strategy = rec['strategy']
    else:
        self.next_strategy = self.default_strategy
```

#### 1.3 Evolver Pre-Feed
```python
# evolver_signal_bridge.py - BEFORE evolver runs:
def before_evolver(self):
    # Hole Learnings VON relevanten Strategy-Erfolgen
    insights = self.learnings.get_relevant_learnings(
        context="evolution",
        limit=3
    )
    
    # Nutze für Gene-Selection
    for insight in insights:
        if insight['outcome'] == 'success':
            self.gene_weights[insight['strategy']] *= 1.2
    
    return self.gene_weights
```

#### 1.4 Test erstellen
```python
# test_learnings_feedback.py
def test_feedback_loop():
    # 1. Record learning with outcome
    ls.record_learning(
        source="Test",
        category="test",
        learning="Test strategy X worked for pattern Y",
        context="pattern_matching",
        outcome="success"
    )
    
    # 2. Query for relevant learnings
    relevant = ls.get_relevant_learnings(
        context="pattern_matching",
        limit=5
    )
    
    # 3. Verify Decision Engine uses them
    de = DecisionEngine()
    strategy = de.get_strategy_for_task("pattern_matching")
    
    assert strategy['source'] == 'learnings', "Decision Engine should use learnings!"
```

### Success Criteria
- [ ] Decision Engine nutzt Learnings für minimum 80% der Recommendations
- [ ] Ralph verwendet Strategie-Empfehlungen aktiv
- [ ] Evolver liest Learnings VOR Gene-Selection
- [ ] Test: 10 Test-Learings → Decision Engine verwendet sie

---

## PHASE 2: Event Bus Consumers aktivieren 🟡 HIGH

### Ziel
Alle wichtigen Event-Typen haben funktionierende Consumer.

### Current State
```
Event Types: 10+
Unconsumed: 8 (827+ events fliegen ins Leere)
Consumed: 4 (LearningIssues, Stagnation, MetaInsight, PatternWeight)
```

### Best Practice Solution
```
Producer → [Event Bus] → Consumer Registry → Action
                              ↓
                    Consumer订阅 für jeden Event-Type
```

### Tasks

#### 2.1 Consumer Registry implementieren
```python
# event_bus.py - Consumer Registry
class EventBus:
    def __init__(self):
        self._consumers = {}  # event_type -> [consumer]
    
    def register(self, event_type: str, consumer: EventConsumer):
        if event_type not in self._consumers:
            self._consumers[event_type] = []
        self._consumers[event_type].append(consumer)
    
    def publish(self, event: dict):
        # Store event
        self._store(event)
        
        # Notify consumers
        for consumer in self._consumers.get(event['type'], []):
            consumer.consume(event)
```

#### 2.2 Fehlende Consumer implementieren

**AgentCompletedConsumer**
```python
class AgentCompletedConsumer(EventConsumer):
    def handles(self) -> List[str]:
        return ["agent_completed"]
    
    def consume(self, event: dict) -> bool:
        # Extract learnings from agent completion
        agent_id = event['data'].get('agent_id')
        outcome = event['data'].get('outcome')
        
        if outcome == 'success':
            LearningsService().record_learning(
                source=f"agent_{agent_id}",
                category="agent_success",
                learning=f"Agent {agent_id} completed successfully",
                context="agent_execution",
                outcome="success"
            )
        return True
```

**LearningCycleConsumer**
```python
class LearningCycleConsumer(EventConsumer):
    def handles(self) -> List[str]:
        return ["learning_cycle_completed"]
    
    def consume(self, event: dict) -> bool:
        # Update Ralph mit neuem Score
        score = event['data'].get('score')
        RalphLoop().update_score(score)
        
        # Check für Meta-Learning
        MetaLearningController().record_meta_learning(
            pattern={"type": "learning_cycle", "score": score}
        )
        return True
```

**EvolverCompletedConsumer**
```python
class EvolverCompletedConsumer(EventConsumer):
    def handles(self) -> List[str]:
        return ["evolver_completed"]
    
    def consume(self, event: dict) -> bool:
        # Record evolver learnings
        gene = event['data'].get('selected_gene')
        outcome = event['data'].get('outcome')
        
        LearningsService().record_learning(
            source="Capability Evolver",
            category="gene",
            learning=f"Gene {gene} had outcome {outcome}",
            context="evolution",
            outcome=outcome
        )
        return True
```

#### 2.3 Consumer als Cron registrieren
```bash
# Event Bus Consumer Processor - läuft alle 5 min
python3 event_bus_consumer_processor.py
```

### Success Criteria
- [ ] `agent_completed` Events werden konsumiert
- [ ] `learning_cycle_completed` Events werden konsumiert
- [ ] `evolver_completed` Events werden konsumiert
- [ ] Consumer registrieren sich automatisch beim Start

---

## PHASE 3: Meta Learning Controller füllen 🔴 CRITICAL

### Ziel
Meta-Learning hat echte Daten und funktioniert nicht mehr blind.

### Current Problem
```
Patterns: 0
Tasks: 0
Meta-Learning läuft jede Stunde aber hat nichts zu verarbeiten
```

### Best Practice Solution
```
Phase 1: Data Collection → Pattern Recognition
Phase 2: Meta-Training → Gewichte anpassen
Phase 3: Meta-Testing → Patterns auf Tasks validieren
Phase 4: Deployment → Angepasste Patterns nutzen
```

### Tasks

#### 3.1 Meta-Learning Data Sources identifizieren
```python
# Meta-Learning braucht:
# 1. Task History (task_log/unified_tasks.json)
# 2. Pattern Performance (was hat funktioniert?)
# 3. Learning Signals (was hat der Loop gelernt?)

META_DATA_SOURCES = [
    "data/learning_loop_state.json",      # Score history
    "data/ralph_learning_state.json",    # Ralph iterations
    "ceo/memory/meta_learning/*.json",   # Pattern files
    "data/events/events.jsonl",          # Event stream
]
```

#### 3.2 meta_patterns.json befüllen
```python
# Script: meta_learning_data_loader.py
def load_patterns():
    """Lade echte Patterns aus dem System."""
    patterns = []
    
    # 1. Ralph Learnings → Patterns
    ralph_learnings = parse_markdown("ceo/memory/ralph_learnings.md")
    for l in ralph_learnings:
        patterns.append({
            "type": "ralph_learning",
            "content": l.learning,
            "category": l.category,
            "success_rate": calculate_success_rate(l.category)
        })
    
    # 2. Decision Engine Strategies → Patterns
    strategies = load_json("data/learnings/index.json")['by_strategy']
    for s, learnings in strategies.items():
        patterns.append({
            "type": "strategy",
            "name": s,
            "usage_count": len(learnings),
            "success_rate": calculate_strategy_success(s)
        })
    
    # 3. Event Patterns → Patterns
    event_patterns = ConsolidationEngine().extract_event_patterns(24)
    for pattern, count in event_patterns.items():
        patterns.append({
            "type": "event_pattern",
            "pattern": pattern,
            "frequency": count
        })
    
    save_json("ceo/memory/meta_learning/meta_patterns.json", {"patterns": patterns})
```

#### 3.3 unified_tasks.json befüllen
```python
# Script: meta_learning_task_builder.py
def build_task_log():
    """Baut Task-History aus vergangenen Läufen."""
    tasks = []
    
    # 1. Ralph Iterationen
    ralph_state = load_json("data/ralph_learning_state.json")
    for i, iteration in enumerate(ralph_state.get('iterations', [])):
        tasks.append({
            "id": f"ralph_iter_{i}",
            "type": "learning_optimization",
            "input": iteration.get('pattern'),
            "output": iteration.get('result'),
            "score": iteration.get('score'),
            "success": iteration.get('score', 0) >= 0.70
        })
    
    # 2. Learning Loop v3 History
    ll_state = load_json("data/learning_loop_state.json")
    for score_entry in ll_state.get('score_history', []):
        tasks.append({
            "id": f"ll_score_{score_entry['iteration']}",
            "type": "score_optimization",
            "input": score_entry.get('pattern'),
            "output": score_entry.get('score'),
            "success": score_entry.get('score', 0) >= 0.75
        })
    
    save_json("data/task_log/unified_tasks.json", {"tasks": tasks})
```

#### 3.4 Meta-Learning Controller Fix
```python
# meta_learning_controller.py - Fixed load_data()
def load_data(self):
    """Load ALL available meta-learning data sources."""
    # Load patterns from MULTIPLE sources
    all_patterns = []
    
    # Source 1: Ralph Learnings
    ralph = parse_markdown(MEMORY_DIR / "ralph_learnings.md")
    all_patterns.extend([{"source": "ralph", **r} for r in ralph])
    
    # Source 2: Strategy effectiveness
    ls = LearningsService()
    strategies = ls.index.get('strategy_effectiveness', {})
    all_patterns.extend([{"source": "strategy", "name": k, "score": v} 
                         for k, v in strategies.items()])
    
    # Source 3: Event consolidation patterns
    ce = ConsolidationEngine()
    event_patterns = ce.extract_event_patterns(24)
    all_patterns.extend([{"source": "event", "pattern": k, "count": v}
                          for k, v in event_patterns.items()])
    
    self.patterns = all_patterns
    
    # Load tasks from unified_tasks.json
    if TASK_LOG.exists():
        with open(TASK_LOG) as f:
            data = json.load(f)
            self.tasks = data.get('tasks', [])
    else:
        self.tasks = []
```

### Success Criteria
- [ ] `meta_patterns.json` hat minimum 50 Patterns
- [ ] `unified_tasks.json` hat minimum 100 Tasks
- [ ] Meta-Learning Controller zeigt geladene Daten in status()
- [ ] Meta-Learning passt Gewichte basierend auf echten Daten

---

## PHASE 4: Idle Crons reparieren 🟡 MEDIUM

### Ziel
5 Crons die nie laufen entweder fixen oder deaktivieren.

### Current State
```
Idle Crons:
- Sir HazeClaw Learnings Daily (target: isolated, kein agent)
- Memory Consolidator Daily (schedule: 23h)
- Memory Consolidator Weekly (schedule: Do 4h)
- Learnings Prune Weekly (schedule: So 3h)
- Memory Consolidator Monthly (schedule: 1st 5h)
```

### Best Practice Solution
```
Cron Job Checklist:
□ Job macht etwas Sinnvolles?
□ Hat es einen funktionierenden Exit-Code?
□ Gibt es Lock-Files um Overlaps zu verhindern?
□ Gibt es Logging?
□ Gibt es Error-Alerting?
```

### Tasks

#### 4.1 Idle Cron Diagnose
```python
# diagnose_idle_crons.py
IDLE_CRONS = [
    "sir-hazeclaw-learnings-daily",
    "memory-consolidate-daily",
    "memory-consolidate-weekly",
    "learnings-prune-weekly",
    "memory-consolidate-monthly"
]

for cron_id in IDLE_CRONS:
    cron = get_cron(cron_id)
    
    # Check 1: Existiert das Target-Script?
    script_path = cron.payload.get('script_path')
    if not Path(script_path).exists():
        print(f"❌ {cron_id}: Script fehlt {script_path}")
        continue
    
    # Check 2: Ist das Script ausführbar?
    if not os.access(script_path, os.X_OK):
        print(f"⚠️ {cron_id}: Script nicht ausführbar")
        # Fix: chmod +x
    
    # Check 3: Letzter Run vs Schedule
    if cron.last_run is None:
        print(f"⚠️ {cron_id}: Wurde NIE ausgeführt")
        print(f"   Schedule: {cron.schedule}")
        print(f"   Target: {cron.session_target}")
```

#### 4.2 Sir HazeClaw Learnings Daily Fix
```python
# Problem: target=isolated aber kein agent_id
# Fix: Entweder als isolated mit payload.agentTurn oder main mit systemEvent

# Option A: Als isolated agent
{
    "name": "Sir HazeClaw Learnings Daily",
    "schedule": {"kind": "cron", "expr": "0 9,18 * * *"},
    "sessionTarget": "isolated",
    "payload": {
        "kind": "agentTurn",
        "message": "Run sir_hazeclaw_learnings.py Analysis",
        "agentId": "ceo"
    }
}

# Option B: Deaktivieren wenn redundant
# (Ralph loop läuft schon 9,18h und schreibt learnings)
```

#### 4.3 Memory Consolidator Crons Fix
```python
# Problem: memory-consolidate-daily/weekly/monthly haben keine agentId
# Diese sollten als isolated scripts laufen, nicht als agentTurn

# Fix: Ändere zu Cron mit shell payload
{
    "name": "Memory Consolidator Daily",
    "schedule": {"kind": "cron", "expr": "0 23 * * *"},
    "sessionTarget": "isolated",
    "payload": {
        "kind": "agentTurn",  # This is wrong for shell scripts
        "message": "python3 memory_consolidator.py --daily"
    }
}

# Better: Use agentTurn correctly or create wrapper script
```

#### 4.4 Learnings Prune Weekly Fix
```python
# Check: Wird prune_old_learnings() irgendwo aufgerufen?
# LearningsService.prune_old_learnings() existiert aber wird nicht in Crons verwendet

# Fix: Prune in LearningsService integrieren (automatic) ODER
# einen dedizierten Cron erstellen der prune aufruft
```

### Success Criteria
- [ ] Alle 5 idle Crons sind entweder: fixed ODER explicitly disabled
- [ ] Keine Crons mit "idle" Status mehr
- [ ] Dokumentation warum jeder Cron existiert

---

## PHASE 5: KG Legacy aufräumen 🟢 MEDIUM

### Ziel
KG von 48% unaccessed entities auf <10% reduzieren.

### Current State
```
Total Entities: 623
Never Accessed: 302 (48%)
Orphaned: 131 (21%)
arxiv Legacy: 165 (komplett ungenutzt)
```

### Best Practice Solution
```
Step 1: Audit - Identifiziere stale entities
Step 2: Categorize - Hard delete vs Soft delete vs Keep
Step 3: Archive - Archiviere bevor delete
Step 4: Prune - Entferne mit Threshold
Step 5: Validate - Verifiziere KG Health bleibt 100%
```

### Tasks

#### 5.1 KG Audit Script
```python
# kg_audit.py
def audit_kg():
    kg = load_kg()
    entities = kg['entities']
    
    audit = {
        'never_accessed': [],
        'orphaned': [],
        'legacy_imports': [],
        'healthy': []
    }
    
    # Get linked entities from relations
    linked = set()
    for rel in kg['relations'].values():
        linked.add(rel['from'])
        linked.add(rel['to'])
    
    for name, entity in entities.items():
        # Check 1: Orphaned (never in any relation)
        if name not in linked:
            audit['orphaned'].append(name)
            continue
        
        # Check 2: Never accessed
        if entity.get('last_accessed') is None:
            # Check if it's legacy import
            if 'arxiv' in entity.get('type', '').lower():
                audit['legacy_imports'].append(name)
            else:
                audit['never_accessed'].append(name)
            continue
        
        # Check 3: Older than 30 days without access
        last_access = parse_date(entity['last_accessed'])
        if (now - last_access).days > 30:
            audit['stale'].append(name)
            continue
        
        audit['healthy'].append(name)
    
    return audit
```

#### 5.2 KG Prune Strategy
```python
# KG Prune mit drei Tiers:

TIER_1_HARD_DELETE = [
    'arxiv.*',           # Legacy imports
    'lrn_2026-0[1-3].*',  # Learnings older than March
]

TIER_2_SOFT_DELETE = [
    'Improvement_2026-04-1[0-5].*',  # April 10-15, accessed but old
]

TIER_3_KEEP = [
    'Learning-Loop.*',  # Hub entity
    'category_.*',       # Category hubs
    'system_.*',         # System entities
    '.*[Tt]oday.*',      # Recent
]

def prune_kg(dry_run=True):
    audit = audit_kg()
    
    # TIER 1: Hard delete legacy
    for pattern in TIER_1_HARD_DELETE:
        matches = [e for e in audit['legacy_imports'] if re.match(pattern, e)]
        if dry_run:
            print(f"Would hard delete {len(matches)} entities matching {pattern}")
        else:
            for name in matches:
                delete_entity(name)
    
    # TIER 2: Mark as archived (soft delete)
    for pattern in TIER_2_SOFT_DELETE:
        matches = [e for e in audit['stale'] if re.match(pattern, e)]
        for name in matches:
            archive_entity(name)  # Sets metadata.archived = True
    
    # TIER 3: Ensure healthy entities stay
    # (Already linked, recent access)
```

#### 5.3 Orphan Cleaner mit Threshold
```python
# kg_orphan_cleaner.py - Already exists, but threshold too high?
# Current: 80% threshold

# Better: Context-aware thresholds
ORPHAN_THRESHOLDS = {
    'learnings': 0.90,    # Learnings can be more orphaned
    'arxiv': 0.30,        # arxiv should be less orphaned
    'Improvement': 0.85,
    'default': 0.80
}

def should_delete(entity_type, orphan_rate):
    threshold = ORPHAN_THRESHOLDS.get(entity_type, 0.80)
    return orphan_rate > threshold
```

### Success Criteria
- [ ] Unaccessed entities < 15% (von 48%)
- [ ] Orphan rate < 10% (von 21%)
- [ ] arxiv entities auf 0 reduziert
- [ ] KG Health bleibt 100%

---

## PHASE 6: Script Duplication reduzieren 🟢 LOW

### Ziel
Von 210 auf <100 echte, genutzte Scripts.

### Current State
```
Learning Loop Variations: 9
Cron Health Scripts: 6
Backup Scripts: 4
Total: 210 scripts
```

### Best Practice Solution
```
Script Inventory:
1. Liste alle Scripts mit Purpose + Letzte Nutzung
2. Identifiziere Duplicates (ähnlicher Name/Function)
3. Markiere deprecated
4. Archiviere statt löschen
```

### Tasks

#### 6.1 Script Inventory erstellen
```python
# script_inventory.py
def inventory_scripts():
    inventory = []
    
    for script in Path('SCRIPTS').rglob('*.py'):
        # Skip __pycache__, tests, etc.
        if '__pycache__' in str(script):
            continue
        
        # Get metadata
        stat = script.stat()
        content = script.read_text()
        
        # Extract function names
        functions = re.findall(r'^def (\w+)', content, re.MULTILINE)
        
        inventory.append({
            'path': str(script),
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'functions': functions,
            'purpose': extract_purpose(content)  # From docstring
        })
    
    # Find duplicates
    clusters = find_duplicate_clusters(inventory)
    
    # Save inventory
    save_json('script_inventory.json', inventory)
    
    return clusters
```

#### 6.2 Duplicate Clusters analysieren
```python
# script_cleanup.py
DUPLICATE_CLUSTERS = {
    'learning_loop': [
        'learning_loop.py',         # OLD - zu behalten als reference
        'learning_loop_fix.py',     # FIX - zu löschen nach verify
        'learning_loop_v3.py',      # ACTUAL - läuft
        'learning_loop_v3_p1.py',   # PARTIAL - zu löschen
        'learning_loop_v3_p2.py',   # PARTIAL - zu löschen
        'learning_loop_integrated.py',  # INTEGRATED - prüfen
        'learning_coordinator.py',  # COORDINATOR - zu behalten
        'learning_coordinator_y.py',  # DUPLICATE - löschen
    ],
    'cron_health': [
        'cron_error_healer.py',    # ERROR_HEALER - zu behalten
        'cron_health_check.py',     # HEALTH_CHECK - zu behalten
        'cron_health_monitor.py',   # HEALTH_MONITOR - redundant
        'cron_monitor.py',          # MONITOR - redundant
        'cron_optimizer.py',        # OPTIMIZER - separat halten
        'cron_status_dashboard.py', # DASHBOARD - separat halten
        'cron_watchdog.py',         # WATCHDOG - redundant
    ]
}

def cleanup_cluster(name, scripts, strategy='archive'):
    """
    strategy:
    - 'keep_one': Behalte beste Script, archiviere rest
    - 'merge': Führe zusammen zu einem Script
    - 'archive_all': Alle archivieren, neu beginnen
    """
    # Verify which one is actually used by Crons
    used_by_crons = find_cron_references(scripts)
    
    if len(used_by_crons) == 0:
        print(f"WARNING: None of {name} scripts are used by Crons!")
        return
    
    # Keep the most complete one
    best = max(used_by_crons, key=lambda s: s['size'])
    
    for script in scripts:
        if script['path'] != best['path']:
            archive_script(script['path'])
            print(f"Archived: {script['path']}")
```

### Success Criteria
- [ ] Script Inventory existiert und ist aktuell
- [ ] Duplikat-Cluster sind analysiert
- [ ] Minimum 50% der Duplikate archiviert
- [ ] Alle Crons zeigen auf genau ein Script

---

## IMPLEMENTATION TIMELINE

```
Week 1:
├── Phase 1: Learnings Feedback Loop (3-4 Tage)
│   ├── Decision Engine Integration
│   ├── Ralph Recommendations aktivieren
│   └── Tests schreiben
│
Week 2:
├── Phase 2: Event Bus Consumers (2 Tage)
├── Phase 3: Meta Learning füllen (3 Tage)
│
Week 3:
├── Phase 4: Idle Crons (2 Tage)
├── Phase 5: KG Aufräumen (3 Tage)
│
Week 4:
├── Phase 6: Script Deduplication (5 Tage)
└── Finale Tests + Dokumentation
```

---

## SUCCESS METRICS

| Phase | Metric | Current | Target |
|-------|--------|---------|--------|
| 1 | Learnings-Usage in Decisions | 0% | 80%+ |
| 2 | Consumed Event Types | 4 | 10+ |
| 3 | Meta Patterns Loaded | 0 | 50+ |
| 4 | Idle Crons | 5 | 0 |
| 5 | KG Unaccessed | 48% | <15% |
| 6 | Scripts | 210 | <100 |

---

## ROLLBACK PLAN

Bei Problemen:
```bash
# Full rollback
cp -r backups/pre_improvement_20260421_150547/* .

# Selective rollback per Phase
cp backups/pre_improvement_20260421_150547/SCRIPTS/automation/learnings_service.py SCRIPTS/automation/
```

---

*Letzte Aktualisierung: 2026-04-21*
*Erstellt basierend auf: Subagent Deep Analysis + Web Research*
