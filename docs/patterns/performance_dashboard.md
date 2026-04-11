# 📈 Performance Metric Dashboard
**Created:** 2026-04-11
**Category:** analysis
**Priority:** HIGH

## Purpose
Enhanced self-reflection for the Capability Evolver — track what works and what doesn't.

## For Evolver Self-Reflection

### Metrics to Track

| Metric | What It Measures | Good | Bad |
|--------|-----------------|------|-----|
| Success Rate | % Evolutions that succeeded | >80% | <50% |
| Blast Radius Accuracy | Estimate vs Actual | <1.5x | >3x |
| Gene Diversity | Same gene repeats | <3x | >5x |
| Innovation Score | New approaches tried | Growing | Stagnant |

### Dashboard Data Points

```json
{
  "success_rate": 0.75,
  "blast_radius_accuracy": 2.1,
  "gene_diversity": 4,
  "innovation_score": 0.6,
  "last_evolution": "2026-04-09",
  "stagnation_signals": ["stable_success_plateau"],
  "weak_areas": ["blast_radius_control"]
}
```

## Self-Reflection Questions

### Before Each Evolution:
1. Have I tried the same gene 3+ times? → Try different one
2. Is my blast radius estimate accurate? → Double-check
3. Am I stagnating? → Force innovation

### After Each Evolution:
1. Did it succeed? → Log success
2. Was blast radius accurate? → Log variance
3. What did I learn? → Update patterns

---

## Usage

```bash
# Show dashboard
python3 scripts/performance_dashboard.py

# Log evolution result
python3 scripts/performance_dashboard.py --log \
    --success true \
    --blast_actual 45 \
    --blast_estimated 30

# Check stagnation
python3 scripts/performance_dashboard.py --check
```

---

## Warning Signals

| Signal | Meaning | Action |
|--------|---------|--------|
| Same gene 5x+ | Stagnation | Force different gene |
| Blast drift 3x+ | Estimation problem | Retrain estimation |
| Success < 50% | Gene pool bad | Review gene pool |
| Innovation score flat | No new ideas | Research more |

---

*Sir HazeClaw — Performance Dashboard Master*
