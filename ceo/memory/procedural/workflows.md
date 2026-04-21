# WORKFLOWS — Standard Procedures

_Letzte Aktualisierung: 2026-04-13_

---

## 🔄 Daily Workflow

### Morning (nach Aufwachen)
1. Read MEMORY.md + HEARTBEAT.md
2. Check Gateway Status
3. Review active Crons
4. Execute Health Check

### During Day
1. Task kommt rein → check memory first
2. Execute task
3. If error → run self-healing
4. If major error → notify [NAME_REDACTED]

### Evening (vor Schlafen)
1. Save session notes
2. Update short_term
3. Log key decisions to episodes

---

## 🛠️ Task Workflows

### When [NAME_REDACTED] asks for something:
```
1. Check memory (facts, preferences)
2. Plan approach
3. Execute
4. Verify result
5. If success → document if important
   If failure → fix or escalate
```

### Error Handling Workflow:
```
1. Categorize error (transient, config, script, etc.)
2. Check healing rules (cron_error_healer.py)
3. Apply fix or escalate to [NAME_REDACTED]
4. Document resolution
```

### Learning Workflow:
```
1. Collect signals (sessions, crons, errors)
2. Analyze patterns
3. Execute improvements
4. Reflexion (did it work?)
5. Document learnings
```

---

## 📝 Documentation Workflow

### When to document:
- New learning (not just task completion)
- Pattern discovered
- Error fixed with new approach
- System change

### Where to document:
- `short_term/` — aktuelle Session
- `long_term/patterns.md` — neue Patterns
- `episodes/timeline.md` — wichtige Events
- `procedural/` — Workflow Änderungen

---

*Workflows should be followed consistently.*