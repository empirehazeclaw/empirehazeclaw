# 🔄 Retry Loop Prevention Skill
**Created:** 2026-04-11
**Category:** workflow
**Priority:** HIGH

## Problem
Agent versucht dieselbe Aufgabe mehrfach (Loop/Retry Pattern).

## Erkennung
```
- "retry" oder "again" im Output
- Loop in Session Logs
- Gleiche Fehlermeldung mehrfach
```

## Lösungen

### 1. Bewährten Weg wiederholen
```
REGEL: Wenn Task bereits funktioniert hat →
       Dieselbe Methode nochmal verwenden
```

### 2. Fehlerquelle fixen statt wiederholen
```
Bevor Retry:
1. Root Cause identifizieren
2. Fix implementieren
3. Dann nochmal versuchen
```

### 3. Stopp-Bedingung setzen
```
Nach 3 Versuchen: STOPPEN + Dokumentieren + Master fragen
```

## Workflow Checklist
- [ ] Error Pattern erkannt?
- [ ] Root Cause gefunden?
- [ ] Fix implementiert?
- [ ] Stopp-Bedingung gesetzt?

## Golden Rule
**"Erst verstehen, dann wiederholen — nicht umgekehrt."**
