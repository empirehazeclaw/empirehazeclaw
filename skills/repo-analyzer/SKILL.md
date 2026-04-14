---
name: repo-analyzer
description: Analyzes code repositories structure, dependencies, complexity, and health. Identifies refactoring opportunities, security issues, and optimization targets. Use when understanding new codebases, planning refactoring, or auditing projects.
tags: [analysis, complexity, refactoring, security, audit]
---

# 🗂️ Repo Analyzer Skill

Deep repository analysis for intelligent refactoring and auditing.

## When to Use
- Understanding new codebases
- Planning refactoring projects
- Finding dead code
- Dependency analysis
- Security audits
- Identifying technical debt
- Pre-acquisition code review

## Analysis Dimensions

### 1. Structure Analysis
Understand the project layout:
```
/
├── src/           # Source code
├── tests/         # Test files  
├── docs/          # Documentation
├── scripts/       # Build/deploy scripts
├── config/        # Configuration files
└── README.md      # Project overview
```

### 2. Complexity Metrics

| Metric | What it measures | Healthy range |
|--------|------------------|---------------|
| Lines per file | File size | < 300 lines |
| Nesting depth | Code complexity | < 4 levels |
| Cyclomatic complexity | Branch complexity | < 10 |
| Response time | Function size | < 50 lines |

### 3. Dependency Analysis

```bash
# Python dependencies
pip3 freeze > requirements.txt
pip3 list --outdated  # Check for updates

# Node.js dependencies  
npm list --depth=2
npm audit  # Security issues

# Go dependencies
go list -m all
```

### 4. Health Indicators

| Indicator | Good | Warning | Critical |
|-----------|------|---------|----------|
| Test coverage | > 80% | 50-80% | < 50% |
| Documentation | Complete | Partial | Missing |
| Naming consistency | Consistent | Some issues | Chaotic |
| Code smells | None | Some | Many |

## Commands

### Quick Scan
```bash
# Get project structure
find . -maxdepth 2 -type d | head -30

# Count files by type
find . -type f -name "*.py" | wc -l
find . -type f -name "*.js" | wc -l

# Get file sizes
find . -type f -exec wc -l {} + | sort -n | tail -20
```

### Detailed Analysis
```bash
# Lines of code (if cloc available)
cloc --include-lang=Python,JavaScript,TypeScript .

# Count lines per extension
find . -type f \( -name "*.py" -o -name "*.js" \) -exec wc -l {} +

# Find large files
find . -type f -size +100k -name "*.py" -o -name "*.js"
```

### Dependency Tree
```bash
# Show dependency graph (Node.js)
npm list --all --json | jq '.dependencies'

# Find circular dependencies
npm ls --depth=10 | grep -E "^[└├]─"

# Unused dependencies
depcheck  # (if depcheck installed)
```

## Output Format

### Summary Report
```markdown
## Repository Analysis: <project-name>

### Structure
- Total directories: X
- Main modules: src/, tests/, docs/
- Key files: package.json, requirements.txt

### Complexity
- Total files: 123
- Python: 45 files
- JavaScript: 78 files
- Total lines: 45,230
- Avg file size: 367 lines

### Dependencies
- Python packages: 23
- Node packages: 156
- Outdated: 12
- Security issues: 3

### Recommendations
1. **[Critical]** Security vulnerabilities in package X
2. **[High]** Replace deprecated API in file Y
3. **[Medium]** Add tests for module Z
4. **[Low]** Improve documentation

### Health Score
- Complexity: 7/10
- Security: 8/10
- Coverage: 6/10
- Documentation: 9/10
**Overall: 7.5/10**
```

## Integration
This skill uses Node.js `child_process` to execute analysis commands.
Use `analyze()` for a quick overview.
Use individual methods for detailed reports.

## Git Integration
```javascript
const ra = require('./skills/repo-analyzer');

// Get git info
const info = ra.gitInfo();
console.log('Branch:', info.branch);
console.log('Last commit:', info.lastCommit);

// Check for uncommitted changes
const status = ra.gitInfo().status;
if (status) console.log('Uncommitted changes!');
```

## Common Issues

### Code Smells
- Long functions (> 50 lines)
- Deep nesting (> 4 levels)
- Duplicate code
- Dead code (unused functions)
- Magic numbers

### Security Risks
- Hardcoded secrets
- SQL injection points
- Insecure dependencies
- Missing input validation
- Weak encryption

### Performance
- N+1 query problems
- Missing indexes
- Memory leaks
- Inefficient loops
