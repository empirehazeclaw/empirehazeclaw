# ✅ Verification Workflow Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** MEDIUM

## Problem
Ich mache Steps fertig aber teste nicht → Fehler werden spät entdeckt.

## Golden Rule
**"Test after every step — not at the end!"**

## Verification Framework

### Type 1: Code Verification
```python
# Nach jedem Code-Step:
python3 script.py
# Erwartet: kein Error
# Wenn Error → Sofort fixen
```

### Type 2: File Verification
```bash
# Nach jedem File-Step:
ls -la /path/to/file
# Erwartet: File existiert
cat /path/to/file | head
# Erwartet: richtiger Inhalt
```

### Type 3: State Verification
```python
# Nach jedem State-Step:
# Prüfe: Was hat sich geändert?
# Ist das Ergebnis wie erwartet?
```

---

## Verification Checklist

### Before Submitting (Final Check)
- [ ] Code compiliert/kein Syntax Error
- [ ] Alle Tests bestanden
- [ ] File am richtigen Ort
- [ ] Berechtigungen korrekt
- [ ] Keine "TODO" oder "FIXME" offengelassen

### Before Every Commit
- [ ] Scripts laufen ohne Error
- [ ] Docs aktuell
- [ ] Changes minimal (nicht mehr als nötig)
- [ ] Commit Message klar

---

## Anti-Patterns

❌ ** NICHT:
- "Ich committe schnell, kann ich später testen"
- "Das File ist wahrscheinlich richtig"
- "Lass mich erst nochwas machen"

✅ ** SONDERN:
- Erst testen, dann committen
- Jeder Step verifiziert
- Kleine Commits, häufig

---

## Workflow

```
1. Step machen
2. Sofort testen
3. Wenn Error → Fix → Test → Next
4. Am Ende: Final Check
5. Commit
```

---

## Metrics

**Verification Success Rate:**
```
(Steps ohne späte Fehler / Total Steps) × 100
```

Ziel: > 95%

---

*Sir HazeClaw — Verification Master*
