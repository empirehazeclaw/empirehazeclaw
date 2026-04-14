---
name: code-review
description: Automated code review using MiniMax M2.7 for intelligent analysis. Reviews pull requests, identifies bugs, security issues, and suggests improvements. Use before merging PRs, after major changes, or for security audits.
tags: [code-review, pr, security, quality, ai]
---

# 🔍 Code Review Skill

Automated code review powered by MiniMax M2.7.

## When to Use
- Before merging pull requests
- After major code changes
- Security-sensitive code review
- Performance-critical code analysis
- Learning from new patterns
- Finding bugs before production

## Process

### 1. Collect Changes
```bash
# Review uncommitted changes
git diff

# Review staged changes
git diff --staged

# Review specific file
git diff <file-path>

# Review commit range
git diff <from-commit>..<to-commit>

# Review specific commit
git show <commit-sha>
```

### 2. AI Analysis Prompt
Send diff to MiniMax M2.7 with this prompt template:

```
Review this code diff. Identify and categorize:

## Critical (Must fix before merge)
- Security vulnerabilities
- Bugs that could cause crashes
- Data corruption risks
- Breaking changes

## Warnings (Should fix)
- Performance issues
- Code smells
- Missing error handling
- Unclear naming

## Suggestions (Nice to have)
- Code style improvements
- DRY violations
- Missing comments
- Alternative approaches

## Liked (What's good)
- Clean architecture
- Good naming
- Efficient solutions
- Best practices

Format: Markdown with headers
```

### 3. Report Format
```
## Code Review Report

### Files Changed
- `src/file1.js` (+50 lines, -10 lines)
- `src/file2.py` (+20 lines, -5 lines)

## Critical Issues
1. **[file1.js:45]** SQL injection vulnerability in query
   ```javascript
   // VULNERABLE: User input directly in query
   query = "SELECT * FROM users WHERE id = " + userId;
   ```
   **Fix:** Use parameterized queries

## Summary
- Total files: 2
- Critical: 1
- Warnings: 3
- Suggestions: 5
- Score: 8/10

**Recommendation:** Address critical issue before merging
```

## Supported Diff Sources
- `git diff` — unstaged changes
- `git diff --staged` — staged changes  
- `git diff main..feature` — branch comparison
- `git show <sha>` — specific commit
- GitHub PR via `gh pr diff <number>`

## Integration with GitHub
```bash
# Get PR diff via GitHub CLI
gh pr diff <PR-number>

# Get PR info
gh pr view <PR-number> --json title,body,state

# Comment on PR
gh pr comment <PR-number> --body "## Code Review..."
```

## Severity Levels

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| Critical | Security/Bug | Must fix before merge |
| Warning | Quality issue | Should fix |
| Suggestion | Improvement | Nice to have |
| Info | Comment | No action needed |

## Example Usage
```javascript
const cr = require('./skills/code-review');

// Review staged changes
const staged = cr.staged();
sendToMiniMax(staged, reviewPrompt);

// Review PR
const prDiff = execSync('gh pr diff 123', {encoding: 'utf8'});
sendToMiniMax(prDiff, reviewPrompt);
```

## Best Practices
1. Always review security-sensitive code first
2. Check for SQL injection, XSS, authentication issues
3. Verify error handling is present
4. Look for performance bottlenecks
5. Check naming consistency
