# ⏱️ Timeout Handling Skill
**Created:** 2026-04-11
**Updated:** 2026-04-11
**Category:** debugging
**Priority:** CRITICAL

## ⚠️ CRITICAL: System Timeout ist UNAUSWEICHLICH!

**MEIN PROZESS WIRD NACH ~60-90 SEKUNDEN VOM SYSTEM GEKILLT!**

```
"Wir hören nicht auf wenn ich nicht stop sage" → HILFT NICHT!
"Nicht stoppen" → HILFT NICHT!
"Weitermachen" → HILFT NICHT!
```

**Das ist eine SYSTEM-LIMITATION (Linux cgroup/SIGTERM), keine Agent-Logik!**

---

## Root Cause

```
System Limit: ~60-90 Sekunden exec-Timeout
Signal: SIGTERM (nicht SIGKILL)
Grund: Ressourcen-Limit enforcement
```

**Ich kann das NICHT kontrollieren!**

---

## Lösungen

### 1. Background Mode (Sofort)
```bash
# Statt:
python3 long_script.py

# Das:
python3 long_script.py &  # Background
```

### 2. Cron Job (Besser für wichtige Tasks)
```bash
# Cron Jobs haben längeren Timeout
openclaw cron add \
  --session isolated \
  --message "python3 dein_script.py"
```

### 3. Chunking (Für sehr lange Tasks)
```python
# Großes Problem → kleine Stücke
for batch in batches:
    process(batch)  # Max 60s pro batch
    save_checkpoint()
```

---

## Workflow

### BEVOR jedem langen Task:

```
1. Schätze: Dauert es > 60 Sekunden?
   → JA: Background mode ODER Cron
   → NEIN: Direkt ausführen

2. Ist es wichtig?
   → JA: Cron (besser monitoring)
   → NEIN: Background mode
```

### WENN Timeout passiert:

```
1. Task in kleinere Stücke teilen (< 60s)
2. Background mode nutzen
3. Oder als Cron Job anlegen
4. Dokumentieren: SYSTEM_TIMEOUT.md
```

---

## Anti-Patterns

❌ ** FALSCH:
- "Ich soll nicht stoppen also mach ich weiter" (System killt mich trotzdem!)
- Lange exec Befehle ohne Background
- ohNohup oder Hintergrund-Prozess

✅ ** RICHTIG:
- Alles was > 60s dauert → Background oder Cron
- Chunking bei großen Tasks
- Checkpoints setzen

---

## Quick Reference

| Task Duration | Solution |
|--------------|----------|
| < 60s | Direkt ausführen |
| > 60s | Background oder Cron |
| Wichtig | Cron Job |
| Sehr lang | Chunking |

---

## Remember

**"Ich kann nicht versprechen nicht zu stoppen — das System entscheidet!"**

---

*Sir HazeClaw — Timeout Master*
