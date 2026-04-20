# Event Bus Consumer Audit
**Date:** 2026-04-20 16:11 UTC

## Overview
The Event Bus (`data/events/events.jsonl`) has 1040 events across 20 types but NO active external consumers.

## Event Types (Produced)

| Type | Count | Producer |
|------|-------|----------|
| agent_completed | 827 | Agent Executor |
| evolver_completed | 59 | Evolver |
| cron_triggered | 30 | OpenClaw Cron |
| task_completed | 25 | Multi-Agent |
| learning_* | 56 | Learning Loop |
| health_check_passed | 8 | Health Agent |
| cron_failed | 4 | OpenClaw Cron |
| stagnation_escaped | 1 | Evolver |

## Consumer Analysis

**No external consumers detected.**

Internal consumers:
- `learning_to_kg_sync.py` - reads events and syncs to KG
- OpenClaw internal monitoring

**Issue:** Events are logged but not actively used for:
- Real-time monitoring
- Alert aggregation
- Cross-system coordination

## Recommendations

1. **Option A:** Connect Event Bus to real monitoring (Datadog, Grafana, etc.)
2. **Option B:** Implement internal consumer for health alerts
3. **Option C:** Reduce logging frequency (not every event needs logging)

## Current Action

Events are written to `events.jsonl` as append-only log.
No rotation/consolidation policy exists.

**Created:** 2026-04-20
