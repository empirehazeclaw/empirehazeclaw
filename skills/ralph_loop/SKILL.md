# Ralph Loop Skill

## Overview
The Ralph Loop is an iteration pattern that ensures tasks complete properly by re-injecting the prompt when the stop hook detects incomplete work.

## Core Principle
```
Traditional Agent:  Observation → Reasoning → Acting → [LLM: fertig? → EXIT]
Ralph Loop:        Observation → Reasoning → Acting → [STOP HOOK: fertig? → NEIN → re-inject]
```

## Key Concepts

### Stop Hook
Intercepts exit attempts and re-injects the prompt if work is incomplete.

### Completion Promise
`<promise>COMPLETE</promise>` serves as the exit signal. The stop hook looks for this marker.

### Max-Iteration Safety
Always set max-iterations to prevent infinite loops.

### Learnings Persistence
Cross-iteration persistence via `memory/ralph_learnings.md`.

## Usage

```bash
# Check-only mode
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py check --check "python3 score_checker.py"

# Full Ralph Loop
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py loop <task_name> \
    --check "python3 score_checker.py" \
    --action "python3 learning_step.py" \
    --max-iterations 20

# Show learnings
python3 skills/ralph_loop/scripts/ralph_loop_adapter.py learnings
```

## Adapter Location
`/home/clawbot/.openclaw/workspace/skills/ralph_loop/scripts/ralph_loop_adapter.py`

## Learnings File
`/home/clawbot/.openclaw/workspace/ceo/memory/ralph_learnings.md`

## Status
- Stop Hook: Implemented
- Completion Promise: `<promise>COMPLETE</promise>`
- Max-Iteration Safety: 20 default
- Learnings: Persisted to ralph_learnings.md

**Created:** 2026-04-20