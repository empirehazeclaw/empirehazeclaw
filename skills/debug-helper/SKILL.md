# 🐛 Debug Helper Skill

Automated failure analysis and debugging assistant.

## When to Use
- Exception stack traces appear
- Cron jobs fail
- Scripts exit with non-zero codes
- OpenClaw shows errors
- Learning loop reports failures
- Unknown error messages appear

## Process

### 1. Collect Error Information
```bash
# Get last 50 lines of openclaw logs
tail -50 ~/.openclaw/logs/openclaw.log 2>/dev/null || tail -50 /tmp/openclaw*.log 2>/dev/null

# Check recent cron failures
openclaw tasks --failed 2>/dev/null | head -30

# Get last error from learning loop
tail -30 ~/.openclaw/workspace/memory/logs/learning_loop.log 2>/dev/null

# Run diagnostic
cat ~/.openclaw/logs/error.log 2>/dev/null | tail -20
```

### 2. AI Analysis Prompt
Send error to MiniMax M2.7 with this template:

```
Analyze this error/failure. Identify root cause and suggest fixes.

## Error Output
```
<ERROR_OUTPUT_HERE>
```

## Context
- Where: <location/context>
- When: <timestamp if known>
- Previous behavior: <what was expected>

## Analysis

### Root Cause (Most Likely)
<explanation of what's happening>

### Similar Known Issues
<any patterns from memory that match>

### Suggested Fixes (Priority Order)
1. **Quick Fix**: <immediate action to try>
2. **Proper Fix**: <complete solution>
3. **Prevention**: <how to avoid this in future>

### Files to Check
- <relevant config/source files>

### Commands to Verify
```bash
<verification commands>
```

Format: Markdown with headers
```

### 3. Learning Loop Integration
After fixing, record the issue:
- Add to `memory/YYYY-MM-DD.md`: Error type, root cause, fix applied
- Update pattern library if novel issue
- Feed insights to learning loop for future prevention

## Pattern Library

Common errors and fixes:

| Error Pattern | Root Cause | Fix |
|--------------|------------|-----|
| `ECONNREFUSED` | Service not running | `systemctl restart <service>` |
| `ENOENT` | File/path not found | Check paths, create if needed |
| `EACCES` | Permission denied | `chmod`/`chown` or run elevated |
| `TIMEOUT` | Service unresponsive | Check resource usage, increase timeout |
| `JSON.parse` fail | Malformed config | Validate JSON syntax |
| `Permission denied` (socket) | Wrong socket owner | `chown clawbot:clawbot /socket/path` |

## Output Format

```
## 🐛 Debug Report

### Error Summary
<one-line description>

### Root Cause
<explanation>

### Fix Applied
<what was done>

### Verification
<how we confirmed it works>

### Prevention
<how to avoid in future>

### Related Issues
<links to memory/known issues>
```
