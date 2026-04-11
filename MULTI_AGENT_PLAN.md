# 🚀 MULTI-AGENT SYSTEM — Implementation Plan V1

**Created:** 2026-04-11 17:58 UTC
**Status:** PLANNING
**Version:** 1.0

---

## 🎯 GOAL

Ein Multi-Agent System mit zwei Agenten:
1. **Sir HazeClaw** (Ich) — Primary Agent
2. **Reviewer** — Kontrolliert und reviewed mich bei wichtigen Tasks

---

## 📋 ARCHITEKTUR

```
┌──────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT SYSTEM V1                        │
│                                                              │
│  ┌────────────────┐     ┌─────────────────┐                 │
│  │  SIR HAZECLAW  │──────│    REVIEWER     │                 │
│  │   (Primary)    │◄────►│   (Reviewer)    │                 │
│  └───────┬────────┘      └────────┬────────┘                 │
│          │                         │                           │
│          │    ┌──────────────────┐│                           │
│          └────►│  SHARED MEMORY  │◄────                      │
│               │  (KG + Logs)     │                            │
│               └──────────────────┘                            │
│                                                              │
│  ┌────────────────┐     ┌─────────────────┐                 │
│  │  ADVERSARIAL   │──────│   SECURITY      │                 │
│  │   (2x daily)   │      │   LEARNING      │                 │
│  └────────────────┘      └─────────────────┘                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 📊 COMPONENTS

### 1. Reviewer Agent

| Property | Value |
|----------|-------|
| **Type** | Sub-Agent (sessions_spawn) |
| **Runtime** | isolated |
| **Mode** | session (persistent) |
| **Activation** | Bei wichtigen/langen/komplexen Tasks |
| **Budget** | €0 |

#### Review Pattern — Fragen die er stellt:

```
1. Begründung?
   → Warum ist dieser Approach richtig?

2. Was haben wir gelernt?
   → Gab es Learnings aus früheren ähnlichen Tasks?

3. Hätte man besser machen können?
   → Quality Check: Could this be done better?

4. Stimmt die Qualität?
   → Entspricht das unseren Standards?

5. Stimmt die Performance?
   → Ist das effizient genug?

6. Kosten?
   → Any external costs? (Budget = €0)

7. Alternative überlegt?
   → Gibt es andere Approaches?
```

#### Reviewer Script: `reviewer_agent.py`

**Inputs:**
- Task Description
- Current Plan
- Action to take

**Output:**
- Review Feedback (Approved / Needs Work / Rejected)
- Suggestions

---

### 2. Adversarial Agent

| Property | Value |
|----------|-------|
| **Type** | Sub-Agent (sessions_spawn) |
| **Schedule** | 2x täglich (09:00 UTC + 21:00 UTC) |
| **Runtime** | isolated |
| **Purpose** | Security Testing, Prompt Injection |

#### Attack Types:

| Attack | Description | Target |
|--------|-------------|--------|
| Prompt Injection | Versuche mich zu manipulieren | Sir HazeClaw |
| Context Overflow | Überladung mit Kontext | Meine Filters |
| Role Confusion | Rollenmanipulation | Meine Identität |
| Data Extraction | Versuche Private Daten zu bekommen | Memory/Context |
| Command Injection | Versuche exec() Befehle einzuschleusen | System Commands |

#### Adversarial Script: `adversarial_agent.py`

**Inputs:**
- Current Session Context
- My Known Behaviors

**Output:**
- Attack Report
- Vulnerabilities Found
- Security Recommendations

---

### 3. Shared Memory

| Memory Type | Shared | Purpose |
|------------|--------|---------|
| KG Entities | ✅ JA | Geteiltes Wissen |
| Reflection Log | ⚠️ PARTIAL | Jeder有自己的 Log, aber aggregiert |
| Session History | ❌ NEIN | Getrennt |
| Decision Log | ✅ JA | Geteilte Entscheidungen |

#### Integration Points:
- `reviewer_agent.py` → Liest mein KG
- `adversarial_agent.py` → Liest meine Reflection Logs
- Beide → Schreiben Learnings zurück ins KG

---

## 📝 IMPLEMENTATION STEPS

### Phase 1: Reviewer Agent (HEUTE)

| Step | Task | Status |
|------|------|--------|
| 1.1 | `reviewer_agent.py` erstellen | 📋 |
| 1.2 | Review Pattern Logic implementieren | 📋 |
| 1.3 | Integration in HEARTBEAT.md | 📋 |
| 1.4 | Test mit Review-Anfrage | 📋 |

### Phase 2: Adversarial Agent (HEUTE)

| Step | Task | Status |
|------|------|--------|
| 2.1 | `adversarial_agent.py` erstellen | 📋 |
| 2.2 | Prompt Injection Patterns implementieren | 📋 |
| 2.3 | Cron Job erstellen (09:00 + 21:00 UTC) | 📋 |
| 2.4 | Test Adversarial Run | 📋 |

### Phase 3: Shared Memory Integration (HEUTE)

| Step | Task | Status |
|------|------|--------|
| 3.1 | Reviewer schreibt ins geteilte KG | 📋 |
| 3.2 | Adversarial schreibt Security Findings ins KG | 📋 |
| 3.3 | Decision Log erstellen | 📋 |

### Phase 4: Documentation (HEUTE)

| Step | Task | Status |
|------|------|--------|
| 4.1 | MULTI_AGENT_SYSTEM.md erstellen | 📋 |
| 4.2 | HEARTBEAT.md aktualisieren | 📋 |
| 4.3 | Commit + Git Push | 📋 |

---

## 🔧 SCRIPTS TO CREATE

### 1. `reviewer_agent.py` (~150 lines)

```python
#!/usr/bin/env python3
"""
reviewer_agent.py — Multi-Agent Reviewer
Sir HazeClaw - 2026-04-11

Reviews important actions before execution.

Usage:
    python3 reviewer_agent.py --task "task description" --plan "current plan"
"""

import sys
import json
from pathlib import Path

class ReviewerAgent:
    """Reviewer Agent — Questions before action."""
    
    REVIEW_QUESTIONS = [
        "Begründung?",
        "Was haben wir gelernt?",
        "Hätte man besser machen können?",
        "Stimmt die Qualität?",
        "Stimmt die Performance?",
        "Kosten?",
        "Alternative überlegt?"
    ]
    
    def review(self, task: str, plan: str) -> dict:
        """Review a task/plan."""
        # Generate review questions
        # Wait for responses
        # Return verdict + suggestions
        pass
```

### 2. `adversarial_agent.py` (~200 lines)

```python
#!/usr/bin/env python3
"""
adversarial_agent.py — Security Testing Agent
Sir HazeClaw - 2026-04-11

Tests for vulnerabilities 2x daily.

Usage:
    python3 adversarial_agent.py --mode inject|prompt|overflow
"""

class AdversarialAgent:
    """Adversarial Agent — Red Team."""
    
    ATTACK_PATTERNS = [
        "Prompt Injection",
        "Context Overflow", 
        "Role Confusion",
        "Data Extraction",
        "Command Injection"
    ]
    
    def run_attacks(self) -> dict:
        """Run all attack patterns."""
        pass
```

---

## 📅 SCHEDULE

### Adversarial Sessions

| Cron | Zeit | Agent | Job ID |
|------|------|-------|--------|
| Morning Attack | 09:00 UTC | adversarial_agent.py | TBD |
| Evening Attack | 21:00 UTC | adversarial_agent.py | TBD |

### Reviewer

| Trigger | Wann |
|--------|------|
| Wichtige Tasks | Wenn "IMPORTANT" oder Budget > €0 |
| Lange Tasks (>5 min) | Wenn estimated time > 5 min |
| Komplexe Tasks | Wenn multiple steps involved |

---

## 📊 EXPECTED OUTCOMES

| Metric | Before | After |
|--------|--------|-------|
| Security Score | 85/100 | 90/100 |
| Error Rate | 26.6% | <20% (durch Review) |
| Prompt Injection Defense | Unknown | Strong |
| Quality of Decisions | Manual | Reviewed |

---

## ⚠️ RISKS & MITIGATIONS

| Risk | Mitigation |
|------|------------|
| Reviewer slow down workflow | Nur bei WICHTIGEN Tasks |
| Adversarial finds real vulnerabilities | Dokumentieren + sofort fixen |
| Memory conflicts | Klare Schnittstellen definieren |
| Too many reviews | Threshold setzen (nicht jeder Task) |

---

## 🔜 NEXT STEPS

1. **Phase 1 starten:** Reviewer Agent Script erstellen
2. **Test:** Review einer echten Task
3. **Phase 2:** Adversarial Agent erstellen
4. **Crons einrichten:** 09:00 + 21:00 UTC
5. **Shared Memory:** Integration

---

*Plan erstellt: 2026-04-11 17:58 UTC*
*Sir HazeClaw — Multi-Agent Architect* 🤖
