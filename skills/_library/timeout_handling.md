# ⚠️ Timeout Handling Skill
**Created:** 2026-04-11
**Category:** debugging
**Priority:** HIGH

## Problem
Exec Commands werden nach ~60-90s vom System gekillt (SIGTERM).

## Lösungen

### Lösung 1: Background Mode
```bash
python3 script.py &
# oder
nohup python3 script.py &
```

### Lösung 2: Cron Job
Lange Scripts als Cron laufen lassen (hat längeren Timeout).
```bash
openclaw cron add --session isolated --message "python3 script.py"
```

### Lösung 3: Chunking
Große Tasks in kleinere Teile aufteilen.

## Anti-Patterns
- ❌ exec mit langen timeouts direkt starten
- ❌ Auf Ergebnis warten bei langen Prozessen

## Workflow Checklist
- [ ] Erkennung: "timeout" in output
- [ ] Root Cause: System-Limit (nicht OpenClaw)
- [ ] Fix: Background mode oder Cron
- [ ] Test: Script läuft durch

## Related
- LEARNING_LOOP.md Rule #5
