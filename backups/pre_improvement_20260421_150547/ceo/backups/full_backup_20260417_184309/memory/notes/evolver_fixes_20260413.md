# Evolver Fixes — 2026-04-13

## Task
Fixed all bare `except:` clauses in 12 scripts. Replaced with proper specific exception handling.

## Scripts Fixed

### 1. error_rate_monitor.py
- **Line 39**: `subprocess.CalledProcessError, OSError` — subprocess.run for error_reducer.py
- Comment added: "Subprocess or file operation failed - fallback to metrics file"

### 2. evening_review.py
- **Line 68**: `IOError, OSError` — file read operations in session stats
- Comment added: "File read failed - skip this session"

### 3. heartbeat_updater.py
- **Line 48**: `Exception` — check_health service call
- **Line 62**: `OSError, PermissionError` — count_scripts directory access
- **Line 66**: `OSError, PermissionError` — count_memory_files directory access
- **Line 73**: `IOError, json.JSONDecodeError` — KG file read/JSON parse
- Comments added explaining each context

### 4. daily_summary.py
- **Line 88**: `OSError, ConnectionError` — socket connection for gateway check
- **Line 92-96**: Added try/except for `os.getloadavg()` with `OSError, AttributeError`
- Comment added: "getloadavg not available on this platform"

### 5. cron_watchdog.py
- **Line 134**: `ValueError, TypeError` — datetime.fromisoformat parsing
- Comment added: "datetime parsing failed - return truncated original"

### 6. evening_summary.py
- **Line 49**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — git log (get_today_commits)
- **Line 68**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — git log (get_yesterday_commits)
- **Line 90**: `IOError, json.JSONDecodeError` — KG JSON load
- **Line 107**: `OSError, ConnectionError` — socket operations

### 7. learning_analyzer.py
- **Line 176**: `IOError, json.JSONDecodeError` — state file read
- Comment added: "File read or JSON parse failed - use empty state"

### 8. morning_brief.py
- **Line 43**: `OSError, ConnectionError` — socket gateway check
- **Line 154**: `IOError, json.JSONDecodeError` — cron_status.json load
- **Line 201**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — git commits
- **Line 273**: `subprocess.CalledProcessError, OSError` — learning_tracker.py

### 9. weekly_review.py
- **Line 151**: `OSError, ConnectionError` — socket gateway check
- Comment added: "Socket operations failed"

### 10. gateway_recovery.py
- **Line 66**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — curl health check
- **Line 81**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — openclaw gateway restart
- **Line 92**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — systemctl restart
- **Line 106**: `subprocess.CalledProcessError, OSError, FileNotFoundError` — openclaw message send

### 11. common_issues_check.py
- **Line 39**: `OSError, FileNotFoundError` — os.path.getsize for empty file check
- **Line 72**: `IOError, json.JSONDecodeError` — cron jobs.json load

### 12. kg_updater.py
- **Line 319**: `ValueError, TypeError` — datetime.fromisoformat in age_kg
- Comment added: "datetime parsing failed - skip this entity"

## Exception Type Guidelines Used

| Context | Exception Type |
|---------|---------------|
| File operations (read/write/exists) | `IOError, OSError` |
| JSON parsing | `json.JSONDecodeError` |
| Subprocess commands | `subprocess.CalledProcessError, OSError, FileNotFoundError` |
| Socket/network | `OSError, ConnectionError` |
| Datetime parsing | `ValueError, TypeError` |
| Directory listing/glob | `OSError, PermissionError` |
| Generic/unknown | `Exception` (with explanatory comment) |

## Verification
All 12 scripts passed `python3 -c "import py_compile; py_compile.compile(...)"` without errors.

---
*Fixed by subagent evolver — 2026-04-13*
