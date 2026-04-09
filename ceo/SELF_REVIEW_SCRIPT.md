# CEO Self-Review Script
*Erstellt: 2026-04-09 19:49 UTC*

---

## 🎯 Ziel

Jeden Montag 09:00 UTC: Automatischer Self-Review der Flotte.
Resultate → Discord Channel `#ceo` + `/workspace/ceo/SELF_REVIEW_WEEKLY.md`

---

## 📋 Review Kategorien

### 1. Task-Performance
```
- Wie viele Tasks diese Woche?
- Erfolgsrate (DONE vs. FAILED)?
- Durchschnittliche Zeit pro Task?
```

### 2. Agent-Auslastung
```
- Welche Agenten waren idle?
- Warum? (keine Tasks? fehlende Skills?)
-->-> Verbesserungsvorschläge
```

### 3. Security-Score
```
- Neue Vulnerabilities?
- Blockierte Threats?
- Security-Events diese Woche?
```

### 4. System-Gesundheit
```
- Cron-Job Erfolgsrate?
- Memory/Disk OK?
- Gateway Stability?
```

### 5. Learnings
```
- Was haben wir diese Woche gelernt?
- Neue Patterns erkannt?
- Skills erstellt?
```

### 6. Nächste Woche
```
- Prioritäten?
- Neue Opportunities?
- Offene Blockers?
```

---

## 🔄 Output Format

```markdown
# Self-Review — Woche [X]
**Datum:** [Datum]
**CEO:** ClawMaster

## Zusammenfassung
[Kurz-Überblick]

## Task-Performance
| Agent | Tasks | Success Rate |
|-------|-------|---------------|
| Security | 5 | 100% |
| Builder | 8 | 75% |
...

## Highlights
- [Positiv]

## Issues
- [Problem] → [Lösung]

## Nächste Woche
1. [Priorität 1]
2. [Priorität 2]
```

---

## ⏰ Schedule

**Cron:** Jeden Montag 09:00 UTC
**Session:** `isolated`
**Report:** Discord `#ceo` (Channel ID: `1491780122057900133`)

---

*Erstellt: 2026-04-09 — CEO Self-Review v1*