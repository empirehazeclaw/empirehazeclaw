# Learning Loop v3 — Plateau Breakthrough Plan
**Erstellt:** 2026-04-13 | **Status:** EVALUATION PHASE

---

## 🔍 Problem Analysis (Root Causes)

| Issue | Root Cause | Evidence |
|-------|-----------|----------|
| Score plateau at 0.615 | Score-Formel hat keinen Validation-Faktor | 29 Validations = 100%, aber Score = 0.615 |
| Cross-Pattern 0 Hits | Keine validierten Solutions zum Matchen | Loop lernt nur "Self-Improvement Pattern" |
| Iteration Drift | State-Sync-Problem zwischen Status/Runtime | Status=2, Runtime=3 |
| Keine Verbesserung | Steady-State erreicht ohne externe Störung | 10 Runs = keine Änderung |

### Research Key Insights

1. **OpenAI Cookbook**: Agentic systems reach plateau — need **repeatable retraining loop** with **measurable feedback signals** and **LLM-as-judge evals**

2. **Dolphin (Scientific Research Agent)**: Uses **ineffective-idea bank** + **embedding-based novelty checks** to mitigate stagnation

3. **Arxiv Survey**: Self-evolving agents need:
   - **Reward-based evolution** (textual feedback, internal/external rewards)
   - **Population-based methods** (evolutionary algorithms)
   - **Cross-agent demonstration learning**

4. **Key Principle**: "Provenance control mitigates stagnation and redundancy" — wir brauchen aktive Novelty-Injection!

---

## 🎯 Ziel

**Score: 0.615 → 0.85+ in 20 Iterationen**

---

## 📋 Phase 1: Score-Formel Fix (P0 — Critical)

### Problem
Validation-Erfolge werden nicht in Score übersetzt.

### Lösung
Score-Formel anpassen:

```python
# CURRENT (falsch):
score = base_score * (1 + validation_rate * 0.1)

# FIXED:
score = (
    base_score * 0.4 +                      # Foundation
    validation_success_rate * 0.3 +         # Validation Gewichtung
    novelty_factor * 0.2 +                   # Neues Lernenbonus
    pattern_quality * 0.1                    # Pattern Qualität
)
```

### Implementation
- `learning_loop_v3.py` → `calculate_score()` Funktion
- Validations zählen als separate Metrik
- Novelty-Faktor: +0.05 pro neuem Pattern, +0.02 pro Cross-Pattern Hit

---

## 📋 Phase 2: Novelty Injection (P0 — Critical)

### Problem
Loop konvergiert weil keine neuen Inputs kommen.

### Lösung — 3 Novelty-Quellen:

1. **Idea Bank (aus Dolphin)**
   - Implementiere `ineffective_idea_bank` —记录 was NICHT funktioniert hat
   - Embedding-basiertes Matching um ähnliche failed Ideas zu vermeiden

2. **Embedding-Based Novelty Check**
   - Prüfe ob neue Hypothesis zu ähnlich zu bestehenden ist
   - Threshold: cosine_similarity < 0.85 →新颖idea

3. **Exploration Bonus**
   - Zufällige Perturbation: 10% Chance pro Iteration
   - Mode-Shift alle 5 Iterationen: exploitation → exploration

### Implementation
- Neues Module: `novelty_engine.py`
- Funktionen: `is_novel()`, `add_to_idea_bank()`, `get_perturbation()`

---

## 📋 Phase 3: Cross-Pattern Activation (P1 — High)

### Problem
Cross-Pattern Matcher hat 0 Hits weil keine echten Errors.

### Lösung
1. **Error-Signal aktivieren**
   - Cron-Failures direkt in Cross-Pattern einspeisen
   - Real error patterns aus `cron_error_healer.py` lernen

2. **Solution Repository aufbauen**
   - Jede validierte Lösung als Pattern speichern mit:
     - Error-Signatur (Levenshtein-Hash)
     - Lösungsschritte
     - Success-Rate
     - Confidence-Score

3. **Matching-Schwelle anpassen**
   - Threshold: 0.15 → 0.30 (weniger noise)
   - Nur Matches mit confidence > 0.6 akzeptieren

### Implementation
- Pattern Schema erweitern: `error_signature`, `solution_embedding`
- Cross-Pattern matching verbessern

---

## 📋 Phase 4: Exploration/Exploitation Balance (P1 — High)

### Problem
Loop exploitet nur, explorieren nicht.

### Lösung — Dynamic Strategy Switching:

```python
STRATEGY_MODES = {
    "exploitation": {  # Low error rate, high score
        "focus": "Refine existing patterns",
        "mutation_rate": 0.05,
        "sample_from_idea_bank": False
    },
    "balanced": {  # Normal operation
        "focus": "Mix of exploitation and exploration",
        "mutation_rate": 0.15,
        "sample_from_idea_bank": True
    },
    "exploration": {  # High error rate or plateau
        "focus": "Discover new patterns",
        "mutation_rate": 0.40,
        "sample_from_idea_bank": True,
        "allow_perturbation": True
    }
}
```

### Switch Conditions:
- exploitation → balanced: Nach 3 verbesserten Iterationen
- balanced → exploration: Nach 5 plateau Iterationen ODER error_rate > 5%
- exploration → balanced: Nach neuem Cross-Pattern Hit

### Implementation
- `strategy_manager.py` — verwaltet current mode
- Automatische Transitions basierend auf Metriken

---

## 📋 Phase 5: Validation Gate 2.0 (P1 — High)

### Problem
Validation ist zu lenient — "Apply Self-Improvement Pattern" passed immer.

### Lösung — Strengere Gates:

1. **Error-Rate Gate**
   - Prüfe: Hat sich error_rate tatsächlich verbessert?
   - Delta < -0.1% → PASS, sonst → FAIL

2. **Cron-Health Gate**
   - Prüfe: Cron success rate verbessert?
   - Wenn Cron-Failures behoben → Bonus

3. **External Validation**
   - Nach jedem Loop: Mini-Test ausführen
   - z.B. Health-Check, Gateway-Probe

### Implementation
- `validation_gate_v2.py` mit echten Metriken
- Nicer output: Zeige konkrete before/after Metriken

---

## 📋 Phase 6: RLHF-Inspired Reward Model (P2 — Medium)

### Problem
Score basiert nur auf internen Metriken — keine echte Reward-Signal.

### Lösung — Human-in-the-Loop Reward:

1. **Nico Feedback als Reward**
   - Positive/Negative explicit Feedback
   - Einbauen in Score: `reward = human_signal * 0.3 + auto_metric * 0.7`

2. **Preference Learning**
   - Wenn Nico bestimmte Actions bevorzugt → Pattern verstärken
   - Feedback Queue priorisiert Nico's Signale

3. **Constitutional AI Elements**
   - Principles definieren die Score beeinflussen
   - z.B. "Error reduction > Pattern creation"

### Implementation
- Feedback Queue Gewichtung anpassen
- `reward_model.py` mit Nico's Preference History

---

## 🚀 Implementation Order

```
WOCHE 1 (April 14-19):
├── Phase 1: Score-Formel Fix     [Tag 1] — CRITICAL
├── Phase 2: Novelty Injection    [Tag 1-2] — CRITICAL
└── Phase 5: Validation Gate 2.0  [Tag 2] — HIGH

WOCHE 2 (April 20-26):
├── Phase 3: Cross-Pattern        [Tag 3-4]
├── Phase 4: Strategy Manager     [Tag 4-5]
└── Phase 6: Reward Model        [Tag 5-6]

WOCHE 3 (April 27-30):
└── Integration + Testing + Tune
```

---

## 📊 Erfolgsmessung

| Metrik | Aktuell | Ziel (Phase 1-3) | Ziel (Phase 4-6) |
|--------|---------|-------------------|-------------------|
| Loop Score | 0.615 | 0.70+ | 0.85+ |
| Score Movement | 0.615 static | Movement > 0 | Stable improve |
| Cross-Pattern Hits | 0 | 3+ | 10+ |
| Validation Real-Effect | None | Error-Rate Delta | Full Integration |
| Novelty Injections | 0 | 5+ | 15+ |

---

## 🔬 Test Plan

1. **Benchmark Run** — 10 Iterationen vor Änderungen (done: 0.615)
2. **Phase 1+2 Test** — 10 Iterationen nach Score+Novelty Fix
3. **Phase 3+4 Test** — 10 Iterationen nach Cross-Pattern+Strategy
4. **Integration Test** — Full v3.1 mit allen Phasen
5. **Stress Test** — 50 Iterationen, check for oscillation

---

## ⚠️ Risiken und Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Score inflation | Medium | Low | Cap bei 0.95 |
| Oscillation | Medium | High | Damping factor in score |
| Over-engineering | High | Medium | Iterate slowly |
| Nico feedback fatigue | Low | Medium | Auto-remind only on significant changes |

---

## 📝 Notes

- Score-Formel: `min(0.95, base * factors)` — nie über 0.95
- Novelty-Injection: Max 1 pro Iteration um chaos zu vermeiden
- Cross-Pattern: Minimum 3验证te Solutions bevor matching startet

---

*Plan Version: 1.0 — Evaluation pending Nico's feedback*
