# Learning Loop v3 — Master Plan (2026-04-21)

## Status: PHASE 1A COMPLETE | PHASE 2 IN PROGRESS

---

## PROBLEM STATEMENT

The Learning Loop had a **reward hacking** vulnerability:
- One KG orphan fix (186 entities) jumped Score 0.50 → 0.80
- Loop thought "goal reached" and stopped optimizing
- Score reflected **data quality**, not **learning progress**

---

## PHASE 1A: Score Decomposition (✅ COMPLETE)

**Commit:** `2dc4938`

**Solution:** Split score into LEARNING (80%) + DATA_QUALITY (20% CAPPED)

```
Formula: TSR*0.35 + LPR*0.25 + EB*0.15 + DF*0.10 + DQ*0.20

DQ capped at 0.50 → max contribution = 0.10 (10% of total)
- Before: KG fix added +0.30 to score
- After:  KG fix adds +0.01 to score
```

**Result:**
| Metric | Before | After |
|--------|--------|-------|
| Score | 0.80 (vanity) | 0.788 (real) |
| DQ impact | +0.19 uncapped | +0.10 capped |
| KG fix boost | +0.30 | +0.01 |

---

## PHASE 2: Novelty Tracking (IN PROGRESS)

**Goal:** Loop continues based on NOVELTY, not score target

**Key Insight (from Ralph Loop research):**
```
Ralph Loop:   while not found(promise) and iterations < MAX
Old Loop:     while score < TARGET
New Loop:     while novelty > NOVELTY_FLOOR and iterations < MAX
```

**What counts as novelty:**
1. New improvement pattern applied
2. New capability discovered
3. Prediction error from last iteration (ICM pattern)
4. Cross-pattern match found

**Implementation:**
- `novelty_history[]` — tracks novelty per iteration
- `novelty_decay` — novelty decreases 0.1 per iteration
- `NOVELTY_FLOOR` — stop if novelty < 0.1 for 3 iterations
- `<promise>COMPLETE</promise>` signal support

**Metrics to track:**
- `novelty_score`: 1.0 for new pattern, 0.5 for new capability
- `prediction_error`: how wrong was our last prediction
- `entropy`: uncertainty of recent actions

---

## PHASE 3: Ralph-Style Completion (PLANNED)

**Goal:** Replace score-target stopping with completion promise

```
Stop conditions (OR):
1. `<promise>COMPLETE</promise>` found in output
2. Max iterations reached
3. Novelty < FLOOR for MIN_ITERATIONS
```

---

## PHASE 4: ICM-Inspired Curiosity Bonus (FUTURE)

**Goal:** Intrinsic reward for prediction errors

```
curiosity = |predicted_outcome - actual_outcome|
if curiosity > THRESHOLD:
    add EXLORATION_BONUS
```

---

## Research Sources

| Pattern | Source | Applied |
|---------|--------|---------|
| Ralph Loop | understandingdata.com | Phase 3 |
| Reward Hacking Fix | arxiv/medium | Phase 1A ✅ |
| ICM (Intrinsic Curiosity) | Pathak et al. 2017 | Phase 4 |
| EMPG (Entropy-Modulated) | arxiv 2509.09265 | Phase 4 |

---

## Learnings

1. **Structural fixes ≠ learning** — DQ must be capped
2. **Ralph pattern** — completion signal > score target
3. **Novelty > Score** — loop should continue while learning, not while score low
4. **ICM pattern** — curiosity as intrinsic reward

---

_Last updated: 2026-04-21 09:37 UTC_
