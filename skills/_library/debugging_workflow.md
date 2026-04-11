# 🧠 Debugging Workflow Skill
**Created:** 2026-04-11
**Category:** debugging
**Times Used:** 0

## When to Use
When encountering errors, crashes, or unexpected behavior.

## Workflow
```
1. IDENTIFY - Was genau geht schief?
2. LOCATE - Wo im Code/Config?
3. UNDERSTAND - Warum passiert es?
4. FIX - Lösung implementieren
5. TEST - Verify fix works
6. DOCUMENT - Learnings speichern
```

## Common Patterns

### Pattern: Exec Timeout
```
Symptom: Command wird nach ~60s gekillt
Lösung: Background mode oder Cron
```

### Pattern: Path Not Found
```
Symptom: Cannot find module '/path/...'
Lösung: Pfad prüfen, Datei existiert?
```

## Anti-Patterns (Vermeiden)
- ❌ Nicht zehn Varianten durchprobieren
- ❌ Nicht bei erstem Anschein aufgeben
- ❌ Nicht ohne Test deployen

## Success Criteria
- [ ] Fehler ist verstanden
- [ ] Fix funktioniert
- [ ] Learnings dokumentiert
