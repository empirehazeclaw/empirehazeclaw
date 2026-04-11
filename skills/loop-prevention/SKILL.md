# Loop Prevention Skill

**Version:** 1.1.0  
**Created:** 2026-04-10  
**Updated:** 2026-04-11
**Status:** Active

## Purpose

**Erkennt und verhindert repetitive Loops ohne echten Fortschritt.**

Dies ist ein kritischer Skill für Self-Improvement - Loops kosten Zeit und bringen keine Ergebnisse.

## 🔍 Loop Detection

### Known Bad Loops

| Loop | Erkennung | Aktion |
|------|-----------|--------|
| "Ich fahre fort" | >3x ohne Änderung | STOPPEN |
| Backup-Paranoia | >8 Backups, <5 Commits | Weniger Backups |
| Task-Hopping | Viele kleine Tasks | Eine tief machen |
| Planungs-Paranoia | Viele Plans, keine Actions | Action > Plan |
| Triviales KG-Füllen | Nutzlose Nodes | Nur echtes Wissen |

### Erkennungs-Kriterien

**BAD Signs:**
- Exec Commands wiederholen sich
- "Nothing to commit" öfter als 3x
- Backup Ratio > 0.5
- Commits < 5 in letzter Stunde
- Script läuft > 10x ohne Änderung

**GOOD Signs:**
- Echte Änderungen in jedem Commit
- Backup Ratio < 0.3
- 5+ Commits pro Stunde
- Tests bestanden

## ⚡ Loop Prevention Rules

### Rule 1: Max 3 Iterations
```
Wenn Task >3x wiederholt ohne Erfolg → STOP
Master fragen: "Was soll ich tun?"
```

### Rule 2: Backup-Regel
```
Backup wenn: Backups < Commits
NICHT: Backups > Commits
```

### Rule 3: Action > Plan
```
Plan ist max 10% der Zeit
Action ist min 90% der Zeit
```

### Rule 4: Test vor "Fertig"
```
Script nicht getestet = NICHT fertig
Commit ohne Test = BAD practice
```

## 🛠️ Tools

### Loop Check
```bash
python3 scripts/loop_check.py
```
Prüft auf aktive Loops.

### Learning Tracker
```bash
python3 scripts/learning_tracker.py
```
Zeigt ob genug gelernt wurde.

### Self-Evaluation
```bash
python3 scripts/self_eval.py
```
Trackt Quality Score.

## 📊 Loop Metrics

| Metric | OK | Warning | Critical |
|--------|----|---------|----------|
| Backup Ratio | < 0.3 | 0.3 - 0.5 | > 0.5 |
| Commits/Hour | > 5 | 2-5 | < 2 |
| Loop Iterations | < 3 | 3-5 | > 5 |
| Test Coverage | > 90% | 80-90% | < 80% |

## 🔄 Improvement vs Loop

```
IMPROVEMENT LOOP (GUT):
├── Beobachte
├── Lerne
├── Anwende
├── Reflect
└── Verbessere
    ↑
    └─ Zurück wenn nötig

BAD LOOP (SCHLECHT):
├── Mache gleiches
├── Kein Erfolg
├── Mache gleiches
├── Kein Erfolg
└── ... (endlos)
```

## 🎯 Daily Loop Check

### Morning:
- [ ] Backup Ratio OK?
- [ ] Commits on track?
- [ ] Loop-Patterns vermieden?

### Evening:
- [ ] Heute echte Fortschritte?
- [ ] Loops erkannt und gestoppt?
- [ ] Patterns gelernt?

## 📝 Known Anti-Patterns

1. **"Ich fahre fort"** → Stattdessen: Ergebnis zeigen
2. **"Erst planen"** → Stattdessen: Action → Reflection
3. **Backup-Paranoia** → Stattdessen: Commit nach echter Änderung
4. **Task-Hopping** → Stattdessen: Eine Sache tief machen
5. **Warten auf Input** → Stattdessen: Annahmen machen + weitermachen

## 🔗 Integration

- **learning_tracker.py** - Trackt ob gelernt wurde
- **self_eval.py** - Quality Score trackt Loops
- **HEARTBEAT.md** - Loop-Warner wenn Patterns erkannt

---

*Last Updated: 2026-04-11*
*Part of: Sir HazeClaw Skills*
