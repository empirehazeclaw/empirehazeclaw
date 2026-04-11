# 📊 Code Stats Skill
**Created:** 2026-04-11
**Category:** analysis
**Priority:** MEDIUM

## Purpose
Visualize repository complexity and health metrics.

## What It Measures

### 1. File Count by Type
```bash
find . -type f -name "*.py" | wc -l  # Python files
find . -type f -name "*.js" | wc -l  # JS files
```

### 2. Code Complexity Indicators
- Lines of Code per file
- Function count
- Import complexity

### 3. Repository Health
- Test coverage
- Documentation ratio
- Comment ratio

## Usage

```bash
python3 scripts/code_stats.py
```

## Output Example

```
📊 CODE STATS
================================
Files: 66 Python, 12 JS
Lines: 12,450 total
Functions: 340
Comments: 1,240 (10%)

🟢 Health: Good
🟡 Complexity: Medium
🔴 Risk: High (deep nesting)
```

## Metrics to Track

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Comment Ratio | >10% | 5-10% | <5% |
| Function Length | <50 lines | 50-100 | >100 |
| Nesting Depth | <4 | 4-6 | >6 |
| File Length | <500 lines | 500-1000 | >1000 |

---

*Sir HazeClaw — Code Stats Master*
