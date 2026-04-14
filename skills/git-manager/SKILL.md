---
name: git-manager
description: Intelligent Git operations for agents. Handles branching, commits, PRs, and merge conflict resolution with context awareness. Use when creating branches, committing changes, managing PRs, or resolving conflicts.
tags: [git, version-control, vcs, github, gitlab]
---

# 🌿 Git Manager Skill

Intelligent Git operations for autonomous agents. Manages branches, commits, PRs, and merge conflicts.

## When to Use
- Creating feature branches
- Committing changes with meaningful messages
- Managing PRs and code reviews
- Resolving merge conflicts
- Git history analysis and cleanup
- Syncing with remote repositories

## Commands

### Status & Info
```bash
# Check working tree status
git status --short

# Show current branch
git branch --show-current

# Show recent commits
git log --oneline -10
```

### Branching
```bash
# Create and switch to new branch
git checkout -b feature/<name>

# Switch to existing branch
git checkout <branch-name>

# List all branches (local)
git branch -a

# Delete merged branch
git branch -d <branch-name>
```

### Committing
```bash
# Stage all changes
git add -A

# Commit with message (conventional commits)
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update README"

# Amend last commit (if message needs change)
git commit --amend -m "new message"

# Uncommit (move changes back to staging)
git reset --soft HEAD~1
```

### Syncing
```bash
# Pull latest changes
git pull origin <branch>

# Push to remote
git push origin <branch>

# Force push (use carefully!)
git push --force-with-lease origin <branch>
```

### Diff & History
```bash
# Show staged changes
git diff --staged

# Show unstaged changes
git diff

# Show changes for specific file
git diff <file-path>

# Show commit details
git show <commit-sha>

# Search commit history
git log --grep="search-term"
```

### Merge Conflicts
1. Identify conflicts: `git status`
2. Open conflicted file, look for `<<<<<<<`, `=======`, `>>>>>>>`
3. Keep desired code, remove markers
4. Stage resolved file: `git add <file>`
5. Complete merge: `git commit`

### Tags & Releases
```bash
# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Version 1.0.0"

# Push tags
git push --tags
```

## Best Practices

### Commit Messages (Conventional Commits)
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting, no code change
- `refactor:` Code change, no feature/fix
- `test:` Adding tests
- `chore:` Maintenance

### Branch Naming
- `feature/<description>` - New features
- `fix/<description>` - Bug fixes
- `hotfix/<description>` - Urgent fixes
- `release/<version>` - Release branches

### Safety Rules
1. Always `git pull` before creating branches
2. Use `--force-with-lease` instead of `--force`
3. Never force push to `main`/`master`
4. Keep commits atomic (one logical change per commit)

## Integration
This skill uses Node.js `child_process` to execute git commands.
The `status()` and `branch()` functions return git output as strings.
