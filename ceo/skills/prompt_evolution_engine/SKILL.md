# Prompt Evolution Engine Skill

**Phase:** 6.2  
**Script:** `scripts/prompt_evolution_engine.py`  
**Purpose:** Inventory, benchmark, and evolve system prompts

## What It Does

1. **Prompt Inventory** - Scans all prompt files (SOUL.md, AGENTS.md, etc.)
2. **Benchmark Testing** - Tests prompts against known test cases
3. **A/B Variant Testing** - Creates and tracks prompt variants
4. **Automated Evolution** - Generates improved prompt versions based on learnings

## Usage

```bash
# Inventory all prompts
python3 scripts/prompt_evolution_engine.py --action inventory

# Run benchmarks
python3 scripts/prompt_evolution_engine.py --action benchmark

# Evolve a specific prompt
python3 scripts/prompt_evolution_engine.py --action evolve --prompt_type soul

# Get status
python3 scripts/prompt_evolution_engine.py --action status
```

## Output Files

- `memory/prompts/prompt_inventory.json` - All prompts indexed
- `memory/prompts/benchmark_results.json` - Test results
- `memory/prompts/prompt_evolution_state.json` - Variant tracking

## Prompt Types Covered

| Type | File | Tokens |
|------|------|--------|
| soul | SOUL.md | ~775 |
| agents | AGENTS.md | ~2136 |
| user | USER.md | ~595 |
| identity | IDENTITY.md | ~269 |
| memory | MEMORY.md | ~1367 |
| tools | TOOLS.md | ~682 |
| heartbeat | HEARTBEAT.md | ~222 |
| prompt_coach | PROMPT_COACH.md | ~1593 |
| decision_framework | DECISION_FRAMEWORK.md | ~1479 |
| dreams | DREAMS.md | ~1542 |

## Integration

- Weekly Cron: `Prompt Benchmark Weekly` (Sunday 11:00 UTC)
- Feeds into evaluation_framework.py for quality scoring
- Part of Learning Loop prompt optimization
