# Bug Hunter — Skill Documentation

## Was es macht

Scannt Logs automatisch alle 30 Minuten auf **echte** Bugs (nicht INFO-False-Positives).

## Filter-Logik

### False Positives (werden ignoriert)
- ❌ "Error: Starting..." (INFO-Messages)
- ❌ "Error: All models failed" (Log-Zeilen)
- ❌ Cron watchdog Status-Reports mit ❌
- ❌ Alle `[INFO] ... error ...` Logs

### Echte Fehler (werden erkannt)
- ✓ Python Tracebacks
- ✓ Connection refused/timeout
- ✓ Permission denied / OOM / Killed
- ✓ JavaScript TypeError/ReferenceError/SyntaxError
- ✓ OpenClaw gateway/session/tool errors

## Cron

- **Alle 30 Minuten** (`*/30 * * * *`)
- **Isolated Session** → kein Main-Session-Spam
- **Bei neuen Bugs**: Telegram-Alert mit Details

## Files

- Scanner: `skills/bug-hunter/bug_scanner.py`
- Bug Knowledge: `ceo/memory/notes/bug_knowledge.json`
- Alerts: `logs/bug_hunter/alerts.json`

## Usage

```bash
# Manual scan
python3 skills/bug-hunter/bug_scanner.py --scan

# Status anzeigen
python3 skills/bug-hunter/bug_scanner.py --status
```

## Integration

Neue Bugs werden automatisch in `bug_knowledge.json` gespeichert und fließen als Feedback in den Learning Loop ein.
