# Learning Loop v3 — Master Plan (2026-04-21)

## Status: ALL PHASES 1-4 COMPLETE | PHASE 5 IN PROGRESS

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

## PHASE 2: Novelty Tracking (✅ COMPLETE)

**Commit:** `2c82140`

**Goal:** Loop continues based on NOVELTY, not score target

**Key Insight (from Ralph Loop research):**
```
Ralph Loop:   while not found(promise) and iterations < MAX
Old Loop:     while score < TARGET
New Loop:     while novelty > NOVELTY_FLOOR and iterations < MAX
```

**What counts as novelty:**
1. New improvement pattern applied → +0.1 novelty
2. Validation failure → -0.15 novelty
3. Natural decay → -0.05 per iteration

**State fields added:**
- `novelty_score` — 1.0 max, +0.1 on success, -0.15 on failure
- `novelty_history[]` — last 20 iterations
- `consecutive_novelty_low` — count when novelty < 0.30

---

## PHASE 3: Ralph-Style Completion (✅ COMPLETE)

**Commit:** `829c676`

**Goal:** Replace score-target stopping with completion promise

**Dual-path completion:**
1. **Score Path:** Score ≥ 0.80 stable for 3 runs
2. **Novelty Path:** Novelty < 0.30 for 3 consecutive runs

**Ralph state tracks:**
- `stable_runs` — consecutive runs at target
- `low_novelty_streak` — consecutive low-novelty runs
- `completed` — boolean flag

---

## PHASE 4: ICM Curiosity Bonus (✅ COMPLETE)

**Commit:** `a7a22bb`

**Goal:** Intrinsic reward for prediction errors (curiosity = surprise)

**Implementation:**
```python
prediction_error = |predicted_impact - actual_outcome|
curiosity_bonus = min(prediction_error, 1.0) * 0.30
EB_total = ideas_score + cross_score + novel_score + curiosity_bonus
```

**New state fields:**
- `prediction_history[]` — last 20 predictions
- `prediction_error` — current prediction error magnitude

**Effect:** When agent is surprised by outcome (high error delta vs expected), it gets bonus curiosity.

---

## PHASE 5: External Feedback Integration (IN PROGRESS)

**Goal:** Make Nico's direct feedback a first-class score input

**Problem:** Feedback queue is rarely used. "direct" source has only 2 old entries from 2026-04-13.

**Solution:** Enhance feedback collection + add feedback component to score

**Key insight (from research):**
> "Business outcome metrics from document processing speed and customer data accuracy feed back into objective evaluation"
> — Datagrid.com

Direct feedback from Nico = highest weight signal. Must flow into score.

**Planned implementation:**
1. Add Telegram polling for direct messages to Sir HazeClaw
2. Track `feedback_rate` = signals collected / iteration
3. Add `feedback_score` to multi-dim score (weight: 5%)

**Metrics to track:**
- `feedback_rate` — how much feedback per iteration
- `feedback_signals_total` — cumulative signals processed

---

## Research Sources

| Pattern | Source | Applied |
|---------|--------|---------|
| Ralph Loop | understandingdata.com | Phase 3 ✅ |
| Reward Hacking Fix | arxiv/medium | Phase 1A ✅ |
| ICM (Intrinsic Curiosity) | Pathak et al. 2017 | Phase 4 ✅ |
| EMPG (Entropy-Modulated) | arxiv 2509.09265 | Phase 4 ✅ |
| Dual-Component Reflection | Datagrid.com | Phase 5 |

---

## Learnings

1. **Structural fixes ≠ learning** — DQ must be capped
2. **Ralph pattern** — completion signal > score target
3. **Novelty > Score** — loop should continue while learning, not while score low
4. **ICM pattern** — curiosity as intrinsic reward
5. **External feedback** — direct input from human = highest trust signal

---

_Last updated: 2026-04-21 10:31 UTC_
