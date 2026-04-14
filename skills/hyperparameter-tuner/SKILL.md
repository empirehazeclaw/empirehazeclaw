# 🎛️ Hyperparameter Tuner Skill

Automated optimization of Learning Loop hyperparameters to maximize score.

## Target
- **Current Score:** ~0.69-0.76
- **Target Score:** 0.85+
- **Learning Loop:** `/home/clawbot/.openclaw/workspace/SCRIPTS/automation/learning_loop_v3.py`

## Tunable Hyperparameters

### 1. Epsilon Decay (Exploration Rate)
```python
epsilon = max(0.05, 0.3 - (iteration * 0.01))  # Decays 0.3 → 0.05
```
**What it does:** Controls random exploration vs exploitation
- High epsilon = more experimentation
- Low epsilon = use what works

**Tuning range:** 
- Start: 0.2-0.4
- Decay rate: 0.005-0.02 per iteration
- Min: 0.02-0.10

### 2. Error Delta Threshold
```python
ERROR_DELTA_THRESHOLD = 0.1  # Must improve or stay same
```
**What it does:** How much error increase is acceptable
- Lower = stricter validation
- Higher = more permissive

**Tuning range:** 0.05-0.20

### 3. Pattern Decay Rate
```python
decay_rate = 0.05  # 5% per day
```
**What it does:** Time-based confidence decay for old patterns
- Higher = patterns fade faster
- Lower = patterns persist longer

**Tuning range:** 0.03-0.10 per day

### 4. Thompson Sampling Priors
```python
prior_alpha = 2  # Success prior
prior_beta = 1   # Failure prior
```
**What it does:** Bayesian prior for reward estimation
- Higher alpha = trust successes more
- Higher beta = distrust failures more

**Tuning range:**
- alpha: 1-5
- beta: 0.5-3

### 5. Cross-Pattern Match Threshold
```python
# In find_cross_pattern_solution - similarity score threshold
```
**What it does:** How similar issues must be to apply cross-pattern
- Higher = stricter matching
- Lower = more generalization

### 6. Validation Depth
**What it does:** Number of validation tests required
- More tests = stricter
- Fewer tests = more permissive

## Tuning Strategy

### Grid Search
Test all combinations systematically:
```python
EPSILON_STARTS = [0.2, 0.25, 0.3, 0.35]
EPSILON_DECAYS = [0.005, 0.01, 0.015]
EPSILON_MINS = [0.03, 0.05, 0.08]
ERROR_DELTAS = [0.05, 0.1, 0.15]
DECAY_RATES = [0.03, 0.05, 0.07]
```

### Bayesian Optimization
Use past results to guide next experiment:
1. Track score for each hyperparameter combination
2. Fit Gaussian Process
3. Select next combination to try

### A/B Testing
Compare current vs new hyperparameters live:
1. Run 50% with current
2. Run 50% with tuned
3. Compare after N iterations

## Process

### 1. Collect Current State
```bash
# Current score
cat /home/clawbot/.openclaw/workspace/data/learning_loop_state.json

# Thompson rewards
cat /home/clawbot/.openclaw/workspace/data/thompson_rewards.json

# Validation log
cat /home/clawbot/.openclaw/workspace/data/learning_loop/validation_log.json

# Score history
python3 learning_loop_v3.py --status
```

### 2. Analyze Performance
- Which categories have low success rates?
- Is score plateauing?
- Are we exploring enough or too much?

### 3. Suggest Changes
```python
# Example suggestion
SUGGESTIONS = {
    "epsilon_start": {"current": 0.3, "suggested": 0.25, "reason": "Plateau detected"},
    "epsilon_decay": {"current": 0.01, "suggested": 0.008, "reason": "Want more exploration"},
    "error_delta": {"current": 0.1, "suggested": 0.08, "reason": "Stricter validation"}
}
```

### 4. Apply Changes
```bash
# Backup current
cp learning_loop_v3.py learning_loop_v3.py.backup

# Apply patch
sed -i 's/epsilon = max(0.05/epsilon = max(0.03/' learning_loop_v3.py

# Validate
python3 learning_loop_v3.py --validate
```

### 5. Monitor
- Watch score for 10+ iterations
- If improving: keep changes
- If degrading: rollback

## Output Format

```
## 🎛️ Hyperparameter Tuning Report

### Current Best Score
Score: 0.690 | Iteration: 85

### Issues Detected
- Epsilon too low (0.05) → Not enough exploration
- Error delta too strict (0.1) → Rejecting good changes
- Decay rate too high (0.05) → Losing good patterns

### Recommended Changes
| Parameter | Current | Suggested | Expected Impact |
|-----------|---------|-----------|----------------|
| epsilon_start | 0.3 | 0.35 | +0.02 score |
| epsilon_decay | 0.01 | 0.008 | +0.01 score |
| error_delta | 0.1 | 0.15 | +0.03 score |

### Validation Plan
1. Apply epsilon + error_delta changes
2. Run 10 iterations
3. If score improves > 0.02, keep changes
4. If not, rollback and try different combo
```
