# Multi-Agent Orchestrator Skill

**Phase:** 6.5  
**Script:** `scripts/multi_agent_orchestrator.py`  
**Purpose:** Task delegation to specialized agents with fallback handling

## Architecture

```
Sir HazeClaw (Orchestrator)
    │
    ├── Health Agent ──────► System Health + Self-Healing
    ├── Research Agent ────► Web Search + Innovation Research
    ├── Data Agent ────────► Learning Loop + KG Maintenance
    │
    └── Sir HazeClaw (fallback) ──► If specialist unavailable
```

## Agents

| Agent | Script | Capabilities | Cooldown |
|-------|--------|--------------|----------|
| health_agent | health_agent.py | health_monitoring, backup | 60s |
| research_agent | research_agent.py | research, learning | 300s |
| data_agent | data_agent.py | data_analysis, learning | 300s |
| sir_hazeclaw | (orchestrator) | ALL | 0s |

## Usage

```bash
# Check status
python3 scripts/multi_agent_orchestrator.py --action status

# Delegate a task
python3 scripts/multi_agent_orchestrator.py --action delegate --task health_check
python3 scripts/multi_agent_orchestrator.py --action delegate --task research --topic "AI agents"
python3 scripts/multi_agent_orchestrator.py --action delegate --task learning_sync

# Aggregate results
python3 scripts/multi_agent_orchestrator.py --action aggregate --task_ids task_1,task_2
```

## Task Types

| Task | Agent | Description |
|------|-------|-------------|
| health_check | health_agent | Full system health check |
| research | research_agent | Topic research via web |
| data_analysis | data_agent | Analyze metrics/data |
| learning_sync | data_agent | Sync learning loop |
| backup | health_agent | Create backup |

## Output Files

- `memory/evaluations/orchestrator_state.json` - Delegation tracking

## Integration

- Orchestrates Health Agent, Research Agent, Data Agent
- Used by autonomous supervisor for delegation
- Fallback to Sir HazeClaw if agents unavailable
