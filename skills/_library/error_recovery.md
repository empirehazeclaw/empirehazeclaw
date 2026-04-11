# 🔧 Error Recovery Skill
**Created:** 2026-04-11
**Category:** debugging
**Priority:** HIGH

## Problem
Errors kommen vor — aber wie recovered man richtig?

## Golden Rule
**"Erst verstehen, dann fixen — nicht einfach retry!"**

## Error Recovery Workflow

### Step 1: Classify
```
Type A: Transient (vorübergehend)
  - Timeout (Netzwerk)
  - Connection refused (Server down)
  - "Killed" (System OOM)
  
Type B: Permanent (dauerhaft)
  - "Not found" (File existiert nicht)
  - "Permission denied" (Zugriff verweigert)
  - Syntax errors (Code ist falsch)
```

### Step 2: React
```
Type A (Transient):
  → Retry mit Backoff (1s, 2s, 4s)
  → Alternative Weg versuchen
  → Background mode für lange Tasks
  
Type B (Permanent):
  → Root Cause finden
  → Fix implementieren
  → Dokumentieren
  → NICHT einfach retry!
```

### Step 3: Prevent Future
- Nach Fix: Pattern dokumentieren
- Update Skill Library
- KG aktualisieren

---

## Timeout Recovery (SPECIAL CASE)

**Timeout = System-Limit, nicht Agent-Fehler!**

### Lösung 1: Background Mode
```bash
python3 long_task.py &
# oder
nohup python3 script.py &
```

### Lösung 2: Chunking
Große Task in kleine Stücke aufteilen.

### Lösung 3: Cron Job
Lange Scripts als Cron laufen lassen (längerer Timeout).

---

## Error Keywords Quick Reference

| Keyword | Type | Action |
|---------|------|--------|
| timeout | A | Background mode |
| connection refused | A | Retry + Wait |
| killed/sigterm | A | System-Ressource prüfen |
| not found | B | Pfad/Datei prüfen |
| permission denied | B | chmod/Ownership prüfen |
| exception/traceback | B | Code debuggen |
| crash | B | Logs analysieren |

---

## Anti-Patterns

❌ ** NICHT:
- Retry ohne Grund
- Gleichen Weg wiederholt
- Ohne Analyse direkt löschen

✅ ** SONDERN:
- Root Cause zuerst
- Alternative Wege
- Dokumentieren

---

## Workflow Checklist

- [ ] Error klasifiziert (A oder B)
- [ ] Root Cause identifiziert
- [ ] passende Lösung gewählt
- [ ] Fix getestet
- [ ] Pattern dokumentiert
- [ ] KG updated

---

*Sir HazeClaw — Error Recovery Master*
