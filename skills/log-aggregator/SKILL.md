# 📊 Log Aggregator Skill

Centralized log collection and analysis for the Sir HazeClaw system.

## Purpose

Collect, parse, and analyze logs from all system sources to:
- Detect error patterns early
- Feed insights to Learning Loop
- Provide unified debugging interface
- Track system health over time

## Log Sources

### OpenClaw Logs
```
~/.openclaw/logs/
├── openclaw.log          # Main gateway log
├── error.log             # Error-only log
├── commands.log          # Command history
└── *.log                 # Various cron/script logs
```

### Learning Loop Logs
```
~/.openclaw/workspace/
├── memory/logs/          # Memory system logs
├── data/learning_loop/    # Learning loop state & logs
└── SCRIPTS/automation/*.log  # Script execution logs
```

### System Logs
```
/var/log/syslog           # System messages
/var/log/auth.log         # Authentication (if accessible)
```

## Aggregation Strategy

### 1. Collection
```bash
# Collect all log files
AGGREGATED_DIR=~/.openclaw/workspace/memory/logs/aggregated/
mkdir -p $AGGREGATED_DIR

# Copy recent logs with timestamps
for log in ~/.openclaw/logs/*.log; do
    if [ -f "$log" ]; then
        cat "$log" >> $AGGREGATED_DIR/daily_$(date +%Y%m%d).log
    fi
done
```

### 2. Parsing
Extract structured data:
- **Timestamp**: When the event occurred
- **Level**: ERROR, WARN, INFO, DEBUG
- **Source**: Which component generated it
- **Message**: The actual log content
- **Context**: Stack traces, session IDs, etc.

### 3. Pattern Detection
```python
ERROR_PATTERNS = [
    "ECONNREFUSED",
    "ENOENT", 
    "EACCES",
    "Timeout",
    "JSON.parse",
    "spawn.*ENOENT",
    "Cannot find module",
    "Permission denied",
    "Cron list timeout"
]

# Group by pattern
pattern_counts = {}
for error in errors:
    for pattern in ERROR_PATTERNS:
        if re.search(pattern, error.message):
            pattern_counts[pattern] += 1
```

### 4. Trend Analysis
- Daily error counts
- Error rate changes over time
- Correlation with system events (deploys, restarts)

## Usage

### Basic Log Query
```bash
# Get all errors from today
log-aggregator --errors --today

# Get errors from specific source
log-aggregator --source openclaw --level ERROR

# Get errors in time range
log-aggregator --from "2026-04-13" --to "2026-04-14"
```

### Aggregated Report
```bash
# Generate daily summary
log-aggregator --report daily

# Generate error trend
log-aggregator --trend 7d
```

### Feed to Learning Loop
```bash
# Export errors for learning loop analysis
log-aggregator --export learning_loop

# This creates:
# ~/.openclaw/workspace/data/learning_loop/errors_for_analysis.json
```

## Output Formats

### JSON (for machines)
```json
{
  "date": "2026-04-14",
  "total_errors": 23,
  "by_pattern": {
    "ECONNREFUSED": 5,
    "ENOENT": 3,
    "Timeout": 7
  },
  "by_source": {
    "openclaw": 12,
    "cron": 8,
    "scripts": 3
  },
  "new_patterns": ["CustomError: specific message"],
  "trending_up": ["Timeout"],
  "trending_down": ["ECONNREFUSED"]
}
```

### Markdown (for humans)
```
## 📊 Log Summary - 2026-04-14

### Errors: 23 (↑ 5 from yesterday)

### Top Patterns
1. Timeout: 7 (↑ 3)
2. ECONNREFUSED: 5 (↓ 2)
3. ENOENT: 3 (→)

### New Patterns
- None

### Recommendations
- Investigate Timeout spike (possible service degradation)
- Monitor ECONNREFUSED (may indicate startup timing issue)
```

## Integration

### With Learning Loop
```python
# In learning_loop_v3.py
def analyze_logs():
    errors = run_log_aggregator(['--errors', '--format', 'json'])
    insights = extract_insights(errors)
    return insights
```

### With Debug Helper
```bash
# When debug-helper finds issues, log them
debug-helper --analyze | log-aggregator --record

# This builds pattern library over time
```

## Configuration

```json
{
  "sources": [
    "~/.openclaw/logs/*.log",
    "~/.openclaw/workspace/memory/logs/*.log",
    "/tmp/openclaw*.log"
  ],
  "error_patterns": [
    "ECONNREFUSED",
    "ENOENT",
    "EACCES",
    "Timeout",
    "Error:",
    "Exception",
    "FAILED"
  ],
  "aggregation_interval": 3600,
  "retention_days": 30
}
```

## Benefits

1. **Single Source of Truth**: All logs in one place
2. **Pattern Detection**: Automatically find recurring issues
3. **Trend Analysis**: See if problems are getting better or worse
4. **Learning Loop Integration**: Feed insights automatically
5. **Faster Debugging**: Query logs instead of grep through files
