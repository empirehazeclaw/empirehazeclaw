# 📋 Todo Manager Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** MEDIUM

## Purpose
Sync code TODOs to actionable tasks.

## Problem
TODOs in code are often forgotten and never become tasks.

## Solution
```
TODOs in code → Task list → Action items → Done
```

## Workflow

### 1. Extract TODOs
```bash
grep -rn "TODO\|FIXME\|XXX\|HACK" --include="*.py" .
```

### 2. Parse and Categorize
```
TODO: [category] [priority] description
FIXME: [category] [priority] description
```

### 3. Create Task List
```bash
python3 scripts/todo_manager.py --sync
```

### 4. Track Progress
```
| TODO | Status | Priority |
|------|--------|----------|
| Fix timeout | Open | HIGH |
| Add tests | Open | MEDIUM |
```

## Priority Levels

| Level | Meaning | Action Time |
|-------|---------|-------------|
| HIGH | Breaking / Security | Today |
| MEDIUM | Important / Usability | This week |
| LOW | Nice to have | This month |

## Categories

- `bug` — Something broken
- `feature` — New functionality
- `refactor` — Code improvement
- `docs` — Documentation
- `test` — Testing

## Anti-Patterns

❌ **WRONG:**
- `TODO: Fix later` (no priority!)
- `TODO: Stuff` (no category!)
- `XXX: asdf` (unclear)

✅ **RIGHT:**
- `TODO: bug high Fix login timeout on line 42`
- `FIXME: feature medium Add user profile endpoint`

---

*Sir HazeClaw — Todo Master*
