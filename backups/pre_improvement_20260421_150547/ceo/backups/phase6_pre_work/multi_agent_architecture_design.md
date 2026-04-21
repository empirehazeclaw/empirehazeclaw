# Multi-Agent Architecture Design

**Erstellt:** 2026-04-17 18:18 UTC  
**Status:** DESIGN_PLAN — Ready for Implementation  
**Author:** Sir HazeClaw 🦞

---

## 🎯 Warum Multi-Agent?

**Aktuelles Problem:**
- Sir HazeClaw macht ALLES: Monitoring, Learning, Research, Maintenance, Communication
- Bei komplexen Tasks wird es eng im Context Window
- Manche Tasks blockieren andere (z.B. Web Research dauert lange)

**Lösung:**
- Spezialisierte Agents für verschiedene Task-Typen
- Orchestrator koordiniert, führt nicht alles selbst aus
- Parallelisierung von unabhängigen Tasks

---

## 🏗️ Architektur

### Option A: Hierarchical (Recommended)

```
┌─────────────────────────────────────────────┐
│         Sir HazeClaw (Orchestrator)          │
│              🦞 Chief of Staff               │
│                                              │
│  • Goal Management                           │
│  • Decision Making                          │
│  • User Communication                        │
│  • Task Delegation                          │
└─────────────────────────────────────────────┘
           │                    │
           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐
│   Data Agent      │  │  Research Agent  │
│  📊 Analyst      │  │  🔍 Investigator │
│                  │  │                  │
│  • KG Updates    │  │  • Web Search    │
│  • Pattern Anal. │  │  • arXiv/HN      │
│  • Metrics Coll. │  │  • Fact Checking │
│  • Learning Sync │  │  • Knowledge     │
└──────────────────┘  └──────────────────┘
           │
           ▼
┌──────────────────┐
│ Maintenance Agent│
│  🔧 Technician   │
│                  │
│  • Health Checks │
│  • Cleanup       │
│  • Error Healing │
│  • Backups       │
└──────────────────┘
```

### Option B: Functional (Simpler)

```
Sir HazeClaw (Generalist + Orchestrator)
├── Health Agent (dedicated monitoring)
├── Research Agent (web + knowledge)
└── Data Agent (analysis + KG)
```

**Empfehlung:** Option B für Phase 1 — simpler zu implementieren, weniger Komplexität.

---

## 📋 Agent Spezifikationen

### 1. Sir HazeClaw (Orchestrator) — EXISTS

**Role:** Chief of Staff  
**Responsibilities:**
- Primary decision maker
- User communication (Telegram)
- Goal tracking und Priorisierung
- Task delegation an Specialists
- Final quality assurance

**Already implemented:**
- Learning Loop (self-improvement)
- Goal Tracker
- Memory System
- Event Bus publishing

**Gap to fill:**
- Task delegation mechanism
- Result aggregation von Agents

---

### 2. Health Agent (NEW)

**Role:** Dedicated Monitoring + Self-Healing  
**Trigger:** Cron (alle 5-15 min) + Event-basiert

**Responsibilities:**
- System health monitoring (Process, Memory, Disk, Network)
- Error detection und auto-healing
- Cron job monitoring
- Gateway availability
- Alert escalation wenn self-healing fehlschlägt

**Inputs:**
- Event Bus: `system.error`, `cron.failed`
- Direct checks: health_check.py, enhanced_self_healing.py

**Outputs:**
- Event Bus: `health.alert`, `health.recovered`
- Telegram alerts bei Critical

**Implementation:**
```python
# Pseudo-code
class HealthAgent:
    def run_health_check():
        results = enhanced_self_healing.check_all_layers()
        if results.has_issues():
            for issue in results.issues:
                if self.can_heal(issue):
                    self.heal(issue)
                else:
                    self.escalate(issue)
    
    def on_event(event):
        if event.type in ['process.crash', 'gateway.down']:
            self.run_health_check()
```

---

### 3. Research Agent (NEW)

**Role:** Dedicated Web Research + Knowledge Gathering  
**Trigger:** Cron (stündlich/täglich) + Event-basiert

**Responsibilities:**
- Innovation research (arXiv, HN)
- Web search für Fakten
- KG population ( neue entities + relations)
- Learning hypotheses generieren

**Inputs:**
- Event Bus: `research.requested`, `kg.needs_update`
- Topic suggestions vom Orchestrator

**Outputs:**
- Event Bus: `research.completed` (mit findings)
- KG updates mit hoher confidence

**Implementation:**
```python
# Pseudo-code
class ResearchAgent:
    def run_daily_research():
        topics = innovation_research.get_top_topics()
        for topic in topics:
            findings = web_search.deep_search(topic)
            hypotheses = self.generate_hypotheses(findings)
            kg.add_research(topic, hypotheses)
        
        self.publish_event('research.completed', count=len(hypotheses))
    
    def on_event(event):
        if event.type == 'research.requested':
            self.run_focused_research(event.topic)
```

---

### 4. Data Agent (NEW)

**Role:** Analytics + Learning Support  
**Trigger:** Cron (stündlich) + Event-basiert

**Responsibilities:**
- Learning Loop ausführung
- Pattern detection und analysis
- KG quality maintenance (orphan cleanup, consistency)
- Metrics aggregation für dashboard

**Inputs:**
- Learning feedback (von anderen Agents)
- Execution results
- KG stats

**Outputs:**
- KG updates (patterns, learnings)
- Learning Loop improvements
- Metrics für dashboard

**Implementation:**
```python
# Pseudo-code
class DataAgent:
    def run_learning_cycle():
        experiences = learning_collector.collect()
        patterns = learning_analyzer.find_patterns(experiences)
        improvements = learning_executor.apply(patterns)
        
        kg.sync_learning(patterns, improvements)
        self.update_metrics()
    
    def maintain_kg_quality():
        orphans = kg.find_orphans()
        for orphan in orphans:
            if kg.can_merge(orphan):
                kg.merge(orphan)
            elif kg.can_delete(orphan):
                kg.delete(orphan)
```

---

## 🔌 Kommunikation

### Event Bus (bereits vorhanden)

**Aktuelle Events:**
| Event | Source | Purpose |
|-------|--------|---------|
| `learning.completed` | Learning Loop | Pattern gefunden |
| `kg_update` | KG Sync | Entity update |
| `anomaly.detected` | Anomaly Detector | Issue erkannt |

**Erweiterung für Multi-Agent:**

| Event | Source | Purpose |
|-------|--------|---------|
| `health.check` | Health Agent | Health Check gestartet |
| `health.alert` | Health Agent | Alert escalation |
| `research.completed` | Research Agent | Research fertig |
| `research.requested` | Orchestrator | Research anfordern |
| `kg.updated` | Data Agent | KG wurde aktualisiert |
| `task.assigned` | Orchestrator | Task delegation |
| `task.completed` | Specialist | Task result |

### Direkte Messages (für Sync Tasks)

```python
# Synchronous task delegation
result = agents.send_message(
    to='health_agent',
    message={'task': 'full_health_check'},
    timeout=30
)
```

---

## 🗄️ Shared Knowledge

### Knowledge Graph (bereits vorhanden)

**Aktueller State:**
- 274 entities
- 634 relations
- Hybrid search verfügbar

**Multi-Agent Nutzung:**
- Alle Agents schreiben zu shared KG
- Entity ownership: Wer hat was hinzugefügt?
- Confidence scoring für Qualität

**KG Update Protocol:**
```python
# Jeder Agent muss beim KG Update:
# 1. Source markieren (welcher Agent)
# 2. Confidence setzen
# 3. Timestamp aktualisieren
kg.update(entity, {
    'source': 'health_agent',  # or 'research_agent', 'data_agent'
    'confidence': 0.85,
    'updated_at': datetime.now().isoformat()
})
```

---

## 📊 Implementation Phasen

### Phase 1: Health Agent (Einfachster Start)

**Warum zuerst Health?**
- Bringt sofortigen Nutzen (better monitoring)
- Script bereits vorhanden (enhanced_self_healing.py)
- Leicht zu testen (alle 5 min health check)
- Keine externen Dependencies (kein Web)

**Tasks:**
1. Health Agent Script erstellen
2. Event Bus integration
3. Telegram alerting bei Critical
4. Cron job: alle 5 min health check

**Timeline:** 1-2 Tage

---

### Phase 2: Research Agent

**Voraussetzung:** Phase 1 fertig

**Warum?**
- Entlastet Sir HazeClaw von Web Research
- Stündliche Innovation Research möglich
- Knowledge growth automatisiert

**Tasks:**
1. Research Agent Script erstellen
2. Web search integration
3. Hypothesis generation
4. KG population workflow

**Timeline:** 2-3 Tage

---

### Phase 3: Data Agent

**Voraussetzung:** Phase 1 + 2

**Warum?**
- Learning Loop auslagern
- KG quality maintenance
- Metrics aggregation

**Tasks:**
1. Data Agent Script erstellen
2. Learning Loop integration
3. KG maintenance workflows
4. Dashboard metrics feeding

**Timeline:** 2-3 Tage

---

## ⚠️ Risiken & Mitigations

| Risiko | Impact | Probability | Mitigation |
|--------|--------|-------------|------------|
| Over-engineering | MED | HIGH | Start with Health Agent only, prove value |
| Token Budget | HIGH | MED | Strict event filtering, no redundant tasks |
| Agent Confusion | MED | MED | Clear role definition, no overlap |
| KG Fragmentation | MED | MED | Entity ownership + confidence scoring |
| Circular Events | HIGH | LOW | Event depth limit, kill switch |

---

## 🧪 Test Plan

### Health Agent Tests
1. Simulate process crash → Agent detects und alerts
2. Simulate gateway down → Agent restarts gateway
3. Run health check every 5 min → No spam, smart escalation

### Research Agent Tests
1. Daily research run → Results in KG
2. Research request via event → Correct topic researched
3. No duplicate KG entries for same topic

### Data Agent Tests
1. Learning cycle runs → Patterns in KG
2. KG quality maintained → No orphans increase
3. Metrics fed to dashboard → Real-time updates

---

## 🚦 Start Signal

**Bereit für Phase 1 (Health Agent)?**

Checklist:
- [x] Design dokumentiert
- [x] Scripts identifiziert (enhanced_self_healing.py)
- [x] Event Bus vorhanden
- [x] Telegram integration vorhanden

**Nächster Schritt:** Health Agent Script erstellen

---

_Letzte Aktualisierung: 2026-04-17 18:18 UTC_
_Basierend auf: industry best practices, system context_
