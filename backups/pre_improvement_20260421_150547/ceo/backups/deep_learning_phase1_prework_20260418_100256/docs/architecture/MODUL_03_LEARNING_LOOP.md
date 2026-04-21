# MODUL 03: Learning Loop System

**Modul:** Learning Loop v3
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 3.1 OVERVIEW

Der Learning Loop ist das **Selbst-Lern-System** von Sir HazeClaw. Er:
- Generiert Signale aus dem Systembetrieb
- Erstellt Hypothesen für Verbesserungen
- Validiert Hypothesen gegen Realität
- Lernt aus Erfolgen und Fehlern

### Aktuelle Stats

| Metric | Wert |
|--------|------|
| Score | 0.764 (Plateau) |
| Signale | ~9-12 pro Run |
| Hypothesen | ~5 pro Run |
| Validation Rate | 97.5% (200/205) |
| Dauer | ~2-35s |

---

## 3.2 LEARNING LOOP v3 ARCHITECTUR

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP v3                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ SIGNALS  │───►│HYPOTHESES│───►│VALIDATION│              │
│  │ Collector│    │ Generator│    │  Engine  │              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
│       │               │               │                      │
│       ▼               ▼               ▼                      │
│  ┌─────────────────────────────────────────┐               │
│  │           PATTERN DETECTOR               │               │
│  │  (Actor-Critic, Q-Learning, Stats)       │               │
│  └────────────────────┬────────────────────┘               │
│                       │                                     │
│                       ▼                                     │
│  ┌─────────────────────────────────────────┐               │
│  │         KNOWLEDGE GRAPH OUTPUT           │               │
│  │  (Patterns → KG Sync)                    │               │
│  └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.3 SCRIPT STRUKTUR

### Haupt-Script

```
/workspace/scripts/learning_loop_v3.py
```

### Unter-Scripts

| Script | Zweck |
|--------|-------|
| `learning_collector.py` | Signale sammeln |
| `learning_analyzer.py` | Signale analysieren |
| `learning_executor.py` | Hypothesen ausführen |
| `learning_feedback.py` | Feedback verarbeiten |
| `learning_coordinator.py` | Koordiniert alles |
| `decision_tracker_integration.py` | Decision Tracking |

### Konfiguration

```python
# learning_loop_v3.py Key Parameters
SIGNAL_COLLECTION_INTERVAL = 3600  # 1 hour
MIN_CONFIDENCE = 0.7
VALIDATION_THRESHOLD = 0.6
FORCED_NOVELTY_INTERVAL = 10  # inject novelty if stuck
```

---

## 3.4 DER CYCLUS

### Phase 1: Signal Collection

**Was:** Sammelt Signale aus:
- Script Outputs (errors, successes)
- Cron Results
- Decision Outcomes
- Memory Patterns
- KG Insights

**Output:** ~9-12 Signale pro Run

### Phase 2: Hypothesis Generation

**Was:** Erstellt Verbesserungs-Hypothesen basierend auf:
- Actor-Critic Bewertung
- Q-Learning (Reward-Estimation)
- Statistical Analysis
- Pattern Recognition

**Output:** ~5 Hypothesen pro Run

### Phase 3: Validation

**Was:** Validiert Hypothesen gegen:
- Erwartete vs. tatsächliche Outcomes
- Statistical Significance
- Cross-Domain Consistency

**Output:** 3-4/4 Validierungen erfolgreich (97.5% Rate)

### Phase 4: Pattern Detection

**Was:** Erkennt:
- Wiederkehrende Patterns
- Stability Plateaus
- Improvement Opportunities

### Phase 5: Knowledge Output

**Was:** Schreibt Results in:
- Knowledge Graph
- Learning Log
- Memory

---

## 3.5 LEARNING LOOP CRON

```json
{
  "name": "Learning Loop Hourly",
  "schedule": "0 * * * *",
  "stagger": "+5 min random",
  "enabled": true,
  "timeout": 180,
  "lastRun": {
    "status": "ok",
    "score": 0.764,
    "duration": 34855
  }
}
```

**Auch:**
```json
{
  "name": "Learning Coordinator (2x/day)",
  "schedule": "0 9,18 * * *",
  "enabled": true
}
```

---

## 3.6 SCORE SYSTEM

### Score Bedeutung

| Score | Status | Interpretation |
|-------|--------|----------------|
| 0.0 - 0.3 | 🔴 Schlecht | System hat Probleme |
| 0.3 - 0.5 | 🟡 Durchschnitt | Normales Lernen |
| 0.5 - 0.7 | 🟢 Gut | Gesundes Lernen |
| 0.7 - 0.9 | 🟢 Sehr gut | Optimiert, Plateau möglich |
| 0.9+ | 🟣 Excellent | Near-Maximum |

### Aktueller Score: 0.764

**Interpretation:** Das System ist in einem **Plateau**. Score ist stabil aber verbessert sich nicht mehr wesentlich.

### Mögliche Ursachen

1. **Local Optimum:** System optimiert sich innerhalb enger Grenzen
2. **Signal Degradation:** Gleiche Signale → gleiche Hypothesen
3. **Novelty Mangel:** Zu wenig neue Inputs

---

## 3.7 RECENT LEARNING LOOP RUNS

| Run | Time | Score | Signals | Issues | Validation |
|-----|------|-------|---------|--------|------------|
| 128 | 05:04 | 0.764 | 9 | 1 | 3/4 ✅ |
| 127 | 04:04 | 0.764 | 12 | 1 | 4/4 ✅ |
| 126 | 03:04 | 0.764 | 10 | 0 | 4/4 ✅ |
| 125 | 02:04 | 0.764 | 11 | 2 | 3/4 ✅ |

**Beobachtung:** Score seit ~20 Runs stabil bei 0.764

---

## 3.8 INTEGRATION: LEARNING LOOP → KG

### Script

```bash
python3 /workspace/scripts/learning_to_kg_sync.py --apply
```

### Was es tut

1. Liest Learning Loop Outputs
2. Transformiert Patterns zu KG Entities
3. Fügt Relations hinzu
4. Validiert KG Integrity

### Cron

```json
{
  "name": "Learning Loop → KG Sync",
  "schedule": "10 * * * *",
  "enabled": true
}
```

---

## 3.9 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| Score Plateau (0.764) | ⚠️ | Seit ~20 Runs keine Verbesserung |
| Stagnation Loop | ⚠️ | Evolver Signal Bridge aktiviert |
| Novelty Injection | ✅ | Forced novelty bei local optimum |

---

## 3.10 VERBESSERUNGS-OPTIONEN

1. **Novelty Injection** — bereits aktiv bei Detektion
2. **Cross-Domain Learning** — von anderen Domains lernen
3. **Forced Gene Diversity** — Evolver Stagnation Breaker
4. **External Signals** — mehr externe Inputs
5. **Reset Strategy** — Score teilweise zurücksetzen

---

*Modul 03 — Learning Loop | Sir HazeClaw 🦞*
