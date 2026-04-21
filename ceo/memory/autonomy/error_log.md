# ERROR LOG — [NAME_REDACTED] Autonomy Engine

*Alle Fehler werden hier protokolliert für Mustererkennung*

## Format
```
[TIMESTAMP] | [ERROR_ID] | [CATEGORY] | [ERROR_TYPE] | [MESSAGE] | [RESOLVED]
```

## Error ID Format
```
ERR-{YYYYMMDD}-{HHMM}-{TYPE}-{SEQ}
Beispiel: ERR-20260413-2353-RUNTIME-001
```

## Error Types
- RUNTIME (Code execution error)
- TIMEOUT (Execution exceeded limit)
- CONFIG (Configuration error)
- PERMISSION (Access denied)
- NETWORK (Connection issues)
- MEMORY (Memory/resource issues)
- VALIDATION (Output not valid)
- UNKNOWN (Undefined)

---

## Entry Template
```markdown
### ERR-{ID}
- **Timestamp:** YYYY-MM-DD HH:MM:SS UTC
- **Type:** ERROR_TYPE
- **Category:** CATEGORY (if applicable)
- **Error Message:** Was ist schiefgelaufen
- **Context:** Wo/bei was es passiert ist
- **Attempted Fix:** Was wurde versucht
- **Result:** RESOLVED / ESCALATED / ROLLED_BACK
- **Related Action:** Transaction ID der zugehörigen Aktion
```

---

## Soft Failure Detection (Affective State)

Diese Errors werden als "soft failures" getrackt und fließen in den Affective State ein:

```json
{
  "delay_anxiety": { "threshold": ">60s", "score": 0.7 },
  "delay_concern": { "threshold": ">120s", "score": 0.9 },
  "repetitive_error": { "threshold": "3x same", "score": 0.8 },
  "degraded_performance": { "threshold": "metric drop >10%", "score": 0.6 }
}
```

---

## Beispiele

### Hard Error (RESOLVED)
```markdown
### ERR-20260413-2353-RUNTIME-001
- **Timestamp:** 2026-04-13 23:53:00 UTC
- **Type:** RUNTIME
- **Error Message:** SyntaxError: invalid syntax in cron_watchdog.py line 42
- **Context:** Script execution during autonomous fix
- **Attempted Fix:** Auto-rollback triggered, original state restored
- **Result:** ROLLED_BACK
- **Related Action:** AUTONOMY-20260413-2353-MEDIUM-001
```

### Soft Error (TRACKED)
```markdown
### ERR-20260413-2200-TIMEOUT-001
- **Timestamp:** 2026-04-13 22:00:00 UTC
- **Type:** TIMEOUT
- **Error Message:** Script exceeded 60s timeout
- **Context:** Evening Capture cron job
- **Attempted Fix:** Timeout increased to 300s
- **Result:** RESOLVED
- **Affective Impact:** delay_anxiety = 0.7
```

---

## Statistik (auto-generated)

| Error Type | Count | Resolved | Escalated | Rolled Back |
|------------|-------|----------|-----------|-------------|
| RUNTIME | 0 | 0 | 0 | 0 |
| TIMEOUT | 0 | 0 | 0 | 0 |
| CONFIG | 0 | 0 | 0 | 0 |
| PERMISSION | 0 | 0 | 0 | 0 |
| NETWORK | 0 | 0 | 0 | 0 |
| MEMORY | 0 | 0 | 0 | 0 |
| VALIDATION | 0 | 0 | 0 | 0 |

*Letzte Aktualisierung: 2026-04-13 23:53 UTC*