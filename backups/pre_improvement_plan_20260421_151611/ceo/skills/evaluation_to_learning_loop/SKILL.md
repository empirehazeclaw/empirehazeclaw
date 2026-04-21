# Evaluation to Learning Loop Integration Skill

**Phase:** Integration (Post-Phase 6)  
**Script:** `scripts/evaluation_to_learning_loop.py`  
**Purpose:** Bridge between Evaluation Framework and Learning Loop

## What It Does

1. **Collects** all evaluation data (metrics, antipatterns, memory health)
2. **Generates** learning signals from evaluation results
3. **Syncs** to Learning Loop signal file
4. **Updates** KG with evaluation metrics

## Usage

```bash
# Sync to Learning Loop
python3 scripts/evaluation_to_learning_loop.py --action sync

# Check status
python3 scripts/evaluation_to_learning_loop.py --action status
```

## Input Data

From `memory/evaluations/`:
- `lnew_metrics.json` - LNEW metrics
- `antipattern_tests.json` - Anti-pattern findings
- `memory_analysis.json` - Memory health

## Output Data

- `memory/evaluations/learning_loop_signal.json` - Signal for Learning Loop
- `memory/short_term/evaluation_for_kg.json` - KG update data

## Generated Learnings

Based on evaluation data:
- `performance_gap` - Task success below target
- `error_pattern` - Error rate above threshold
- `efficiency` - Token usage too high
- `anti_pattern` - High severity anti-patterns found
- `system_health` - Memory/system clean

## Integration

- Part of Prompt Benchmark Weekly Cron
- Feeds into Learning Coordinator
- Updates KG with current metrics
