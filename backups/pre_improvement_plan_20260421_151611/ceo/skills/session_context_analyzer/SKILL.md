# Session Context Analyzer Skill

**Phase:** 6.1.1  
**Script:** `scripts/session_context_analyzer.py`  
**Purpose:** Analyze session context for token waste and efficiency

## What It Does

1. **Session Size Analysis** - Measures session file size and token estimate
2. **Token Waste Detection** - Identifies repetitive patterns, redundant status checks
3. **Message Pattern Analysis** - Counts messages, avg length, tool calls
4. **Context Relevance Scoring** - Rates how relevant current context is (0-1)
5. **Recommendations** - Suggests pruning/optimization actions

## Usage

```bash
python3 scripts/session_context_analyzer.py
python3 scripts/session_context_analyzer.py --verbose
```

## Output Files

- `memory/short_term/session_analysis_latest.json` - Latest analysis results

## Key Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Session Size | <200KB | 200-500KB | >500KB |
| Context Relevance | >80% | 50-80% | <50% |
| Token Waste | 0 | 100-500 | >500 |

## Integration

- Called by Phase 6.1 (Session Lifecycle Management)
- Results feed into evaluation_framework.py
- Part of continuous self-improvement cycle
