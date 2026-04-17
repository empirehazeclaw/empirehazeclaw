# Evaluation Framework Skill

**Phase:** 6.3  
**Script:** `scripts/evaluation_framework.py`  
**Purpose:** LNEW Metrics + Anti-Pattern Detection

## What It Does

### LNEW Metrics
- **L**atency (p50, p95, p99)
- **N**umber of Errors (error rate)
- **E**fficiency (tokens per task)
- **W**orth (cost per successful task)

### Anti-Pattern Detection
Scans for bad patterns in prompts:
- `filler_words` - "Great question", "I'd be happy"
- `over_confirmation` - "Soll ich?" when action is allowed
- `hallucination` - "Ich denke", "I assume" without evidence
- `status_infodump` - Excessive status dumps
- `indecision` - "Schwierig zu sagen"

## Usage

```bash
# Full evaluation report
python3 scripts/evaluation_framework.py --action report

# Collect metrics only
python3 scripts/evaluation_framework.py --action collect_metrics

# Run anti-pattern tests
python3 scripts/evaluation_framework.py --action run_tests

# Integrate with Learning Loop
python3 scripts/evaluation_framework.py --action integrate
```

## Output Files

- `memory/evaluations/lnew_metrics.json` - LNEW metrics
- `memory/evaluations/antipattern_tests.json` - Anti-pattern results
- `memory/evaluations/learning_loop_signal.json` - LL integration signal

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Task Success Rate | 76.3% | 80%+ |
| Error Rate | 3.0% | <5% |
| Efficiency | 186 tokens/task | <300 |
| Anti-Patterns (HIGH) | 0 | 0 |
| Anti-Patterns (MED) | 0 | 0 |

**Note:** Anti-Pattern filter was improved to exclude false positives (e.g., "Skip 'Great question'" pattern in rules).

## Integration

- Part of Prompt Benchmark Weekly Cron
- evaluation_to_learning_loop.py syncs to Learning Loop
- Results feed into goal tracking
