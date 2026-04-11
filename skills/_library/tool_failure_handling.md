# 🔧 Tool Failure Handling Skill
**Created:** 2026-04-11
**Category:** debugging
**Priority:** HIGH

## Problem
Manche Tools schlagen fehl:
- `exec: Tool exec not found` → Script existiert nicht
- `write: validation failed` → File-Operation Problem
- `read: path escapes sandbox` → Path-Traversal Schutz

## Erkennung

| Error | Was es bedeutet |
|-------|----------------|
| `exec: Tool exec not found` | Script nicht vorhanden oder typo |
| `write: validation failed` | File existiert bereits + andere Issues |
| `read: path escapes sandbox` | Sicherheitsblock |
| `Tool not found` | Falscher tool name |

## Lösungen

### 1. Script not found
```bash
# Erst prüfen ob file existiert
ls -la /path/to/script.py

# Oder korrekten pfad finden
find /home/clawbot/.openclaw/workspace -name "script.py"
```

### 2. Validation failed (write)
```python
# Case 1: File existiert
# Lösung: Erst lesen, dann editieren ODER create=False

# Case 2: Path ist falsch
# Lösung: Absolute pfade nutzen
```

### 3. Sandbox escape
```python
# NICHT: read("/home/clawbot/../../../etc/passwd")
# SONDERN: Nur workspace-pfade erlauben
```

## Prevention

- ✅ Immer erst `ls` oder `find` bevor exec
- ✅ Exakte Pfade nutzen (keine `~` expansion)
- ✅ Absolute Pfade für alle tools
- ✅ Existiert-Check vor write

## Workflow Checklist

- [ ] Error message genau lesen
- [ ] Root Cause identifizieren
- [ ] Fix implementieren
- [ ] Prevention measure dokumentieren

---

*Sir HazeClaw — Tool Failure Master*
