# Learning Loop Research — 2026-04-21

## Problem (from practice)
Score jumps to target when ONE large structural fix happens (KG orphan fix: 0.50 → 0.80).
Loop thinks "goal reached" and stops or slows down.
But this isn't real learning progress — it's a one-time data quality improvement.

## Research Findings

### 1. Ralph Loop / Stop Hook Pattern
**Source:** understandingdata.com, github/anthropic/claude-plugins-official

**Key Insight:**
- Loop continues until `<promise>COMPLETE</promise>` signal is found in output
- Stop hook intercepts exit and re-injects if promise not found
- NOT target-based stopping (score >= X)
- Max-iteration safety limit

**Application for Sir HazeClaw:**
```
Instead of: while score < TARGET
Use:        while not found(promise) and iterations < MAX
```

### 2. Reward Hacking (Critical!)
**Source:** medium.com/@adnanmasood, arxiv

**Problem:** When objective function has easy shortcuts, agents optimize the shortcut not the intent.
- Our KG orphan fix boosted Score by +0.30 instantly
- Score reflected data quality, not agent learning capability
- This is textbook reward hacking via structural repair

**Mitigation:**
1. Decouple structural improvements from learning score
2. Separate "data health" metrics from "learning progress" metrics
3. Add "impossible improvements" category — things that require genuine learning

### 3. Entropy-Modulated Learning (EMPG)
**Source:** arxiv.org/html/2509.09265v1

**Key Insight:**
- Confident/correct actions → amplify learning signal
- Uncertain/risky actions → attenuate updates (prevent instability)
- Step-wise uncertainty modulates gradient descent

**Application:**
- Our Exploration Bonus (EB) can use entropy as signal
- High entropy in recent actions = we need more exploration
- Low entropy = we've consolidated knowledge, reduce exploration

### 4. Intrinsic Curiosity Module (ICM)
**Source:** Lil'Log, Pathak et al. 2017

**Key Insight:**
- Forward dynamics model predicts next state
- Intrinsic reward = prediction error (surprise)
- Agent explores states where it was wrong about dynamics

**Application for Sir HazeClaw:**
- Track prediction accuracy on "what will this improvement do?"
- High prediction error → intrinsic reward bonus
- Low error → reduce exploration, exploit known patterns

## Proposed Changes to Learning Loop v3

### Current (Broken):
```
while score < TARGET:
    learn()
    if score improvement < threshold for N iterations:
        break
```

### New Ralph-Inspired:
```
iterations = 0
while iterations < MAX_ITERATIONS:
    result = learn_single_iteration()
    
    # Check for completion promise (Ralph pattern)
    if result.has_promise("COMPLETE"):
        break
    
    # Check for novelty (not just score!)
    if result.novelty_detected():
        continue  # Keep learning
    
    # Check for stagnation (entropy-based)
    if result.entropy < ENTROPY_FLOOR and iterations > MIN_ITERATIONS:
        break
    
    iterations += 1
```

### Score Decomposition Fix:
```
TOTAL_SCORE = W_learning * LEARNING_PROGRESS + W_quality * DATA_QUALITY
Where:
- LEARNING_PROGRESS = pattern improvements applied + novel discoveries
- DATA_QUALITY = KG health + cron success (separate from learning!)
- W_learning = 0.70 (70% weight on real learning)
- W_quality = 0.30 (30% max on data quality)
```

### Novelty Detection:
```
Novelty = new improvement applied
        + new capability discovered
        + prediction error from last iteration
        + patterns that contradicted assumptions

If Novelty > NOVELTY_THRESHOLD:
    loop continues (we're still learning)
Else:
    if iterations > MIN_ITERATIONS:
        break (nothing new, we've plateaued)
```

## Implementation Plan

### Phase A: Score Decomposition (Quick Fix)
1. Split score into LEARNING (70%) + QUALITY (30%)
2. DATA_QUALITY never exceeds 0.30 even at 100%
3. Score target remains at 0.80 but is now LEARNING component

### Phase B: Novelty Tracking
1. Add `novelty_history` to state
2. Novelty = 1.0 if new pattern applied, 0.5 if new capability
3. Novelty decays by 0.1 per iteration

### Phase C: Ralph-Style Completion
1. Remove score-target stopping
2. Add `<promise>COMPLETE</promise>` signal support
3. Loop stops when NOVELTY < threshold for MIN_ITERATIONS

### Phase D: Entropy Bonus (Optional)
1. Track entropy of recent actions
2. High entropy = exploration bonus
3. Low entropy = consolidation bonus

## Key Learnings
- Ralph Loop: Completion signal > Score target
- Reward hacking: Separate learning score from data quality
- ICM: Curiosity = prediction error = intrinsic reward
- EMPG: Uncertainty modulates learning intensity
