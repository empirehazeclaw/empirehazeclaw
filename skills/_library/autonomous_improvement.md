# 🔄 Autonomous Improvement Skill
**Created:** 2026-04-11
**Category:** learning
**Priority:** HIGH

## Problem
Ich soll mich selbst verbessern aber wie?

## Lösung
**Der Autonomous Improvement Loop**

```
┌─────────────────────────────────────────────────────────────┐
│                    IMPROVEMENT LOOP                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   DETECT ──── ANALYZE ──── ACT ──── DOCUMENT ──── VERIFY   │
│      ↑                                              │       │
│      └────────────────────────┘                      │       │
│                          (Feedback Loop)                  │       │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: DETECT (Erkennen)

**Was ist das Problem?**
- Error Rate gestiegen?
- Friction Events?
- Skill Score gefallen?
- Cron Errors?

**Tools:**
```bash
# Morning Metrics
python3 scripts/session_analyzer.py --days 1

# Skill Check
python3 scripts/skill_tracker.py --report

# Cron Health
openclaw cron list
```

---

## Step 2: ANALYZE (Analysieren)

**Warum ist es passiert?**
- Root Cause finden
- Similar past issues? (KG check)
- Was sind die Daten?

**Fragen:**
1. Wann ist das passiert?
2. Warum ist es passiert?
3. Wie kann ich es verhindern?
4. Was habe ich ähnliches schon?

---

## Step 3: ACT (Handeln)

**Was tue ich jetzt?**
- Quick Fix: Sofort implementieren
- Medium Fix: Sprint ansetzen
- Long Fix: Capability Evolver nutzen

**Regel:** 
```
Minimal First → Test → Verify → Dokumentieren
```

---

## Step 4: DOCUMENT (Dokumentieren)

**Was habe ich gelernt?**
- Pattern in Skill Library
- KG Update (neue entity)
- Memory Log
- AUTONOMOUS_LEARNING_PLAN.md updaten wenn nötig

---

## Step 5: VERIFY (Prüfen)

**Hat es funktioniert?**
- Nächste Session: Error Rate besser?
- Skill Score höher?
- Master Feedback?

**Wenn Ja:** → Loop continue
**Wenn Nein:** → Step 2 zurück

---

## Priorisierung

| Severity | Definition | Action Time |
|----------|------------|-------------|
| CRITICAL | System down | SOFORT |
| HIGH | Error Rate > 30% | Heute |
| MEDIUM | < 20% Error | Diese Woche |
| LOW | Optimization | Sprint |

---

## Quick Protocol

```
MORNING (06:00):
  → session_analyzer.py
  → skill_tracker.py --report
  → If error > 20% → HIGH priority

AFTER ANY SUCCESS:
  → pattern_extractor.py
  → KG update

AFTER ANY ERROR:
  → Root Cause
  → Fix oder Document
  → Skill Library update

EVENING:
  → Review was ich heute verbessert habe
  → Memory Log
```

---

## Success Metrics

| Metric | Baseline | Target | Week |
|--------|----------|--------|------|
| Error Rate | 28% | <15% | 4 |
| Friction | 43 | <20 | 4 |
| First-Attempt | ? | >80% | 4 |
| Skills | 8 new | 15 total | 4 |

---

*Sir HazeClaw — Autonomous Improver*
