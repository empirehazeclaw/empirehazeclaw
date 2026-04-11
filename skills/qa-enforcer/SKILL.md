# QA Enforcer Skill

**Version:** 1.0.0  
**Created:** 2026-04-11
**Status:** Active

## Purpose

**Quality Assurance für alle Sir HazeClaw Outputs.**

Dieser Skill stellt sicher, dass alle Scripts, Skills und Dokumentation den Qualitätsstandards entsprechen.

## 🎯 QA Standards

### Für Scripts:
- [ ] Keine `except: pass` (immer explizite Fehlerbehandlung)
- [ ] Keine `shell=True` wo nicht nötig
- [ ] Input validation
- [ ] Logging für Debugging
- [ ] Testbar (kann importiert werden)

### Für Skills:
- [ ] SKILL.md vorhanden
- [ ] Index.py vorhanden
- [ ] Version dokumentiert
- [ ] Usage dokumentiert
- [ ] Tests vorhanden

### Für Commits:
- [ ] Aussagekräftige Commit-Nachricht
- [ ] Keine "Checkpoint" oder "Update" Commits
- [ ] Max 1 Feature pro Commit
- [ ] Getestet bevor commit

## 🛠️ QA Tools

### Test Framework
```bash
python3 scripts/test_framework.py
```
58 tests, 89% coverage

### Fast Test
```bash
python3 scripts/fast_test.py
```
17 tests in 30s

### Loop Check
```bash
python3 scripts/loop_check.py
```
Prüft auf Loops

### Learning Tracker
```bash
python3 scripts/learning_tracker.py
```
Prüft auf Learning

## 📋 QA Checklist

### Vor jedem Commit:
1. [ ] Code funktioniert?
2. [ ] Tests bestanden?
3. [ ] Keine `except: pass`?
4. [ ] Aussagekräftige Nachricht?
5. [ ] Loop-Check bestanden?

### Nach jedem Commit:
1. [ ] Git push successful?
2. [ ] Score verbessert oder gleich?
3. [ ] Memory dokumentiert?

## 🔍 QA Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | >90% | 89% |
| Quality Score | 100/100 | 98/100 |
| Commits/Tag | >10 | 23 |
| Backup Ratio | <0.3 | 0.04 |

## 🎓 QA Patterns

### Pattern: Test First
```
1. Script schreiben
2. Test schreiben
3. Test laufen lassen
4. Fix bis test passed
5. Commit
```

### Pattern: Review Before Commit
```
Script → Review → Test → Commit
```

### Pattern: QA Loop
```
Implement → Test → Fix → Test → Deploy
```

---

*Last Updated: 2026-04-11*
*Part of: Sir HazeClaw Skills*
