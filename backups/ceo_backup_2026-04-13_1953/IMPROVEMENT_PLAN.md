# 🎯 MASTER IMPROVEMENT PLAN — "Make Everything Better"
**Erstellt:** 2026-04-12 18:22 UTC
**Status:** IN PROGRESS

---

## 📊 SYSTEM STATUS (Baseline)

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| Sessions | 477 | <50 | 🔴 -427 |
| Task Issues | 88 | 0 | 🔴 -88 |
| Audit Errors | 65 | 0 | 🔴 -65 |
| Audit Warnings | 321 | <50 | 🟡 -271 |
| Docs | 42 | <20 | 🟡 -22 |
| Crons Active | 21/46 | 25-30 | 🟡 |
| Failed Crons | 4 | 0 | 🔴 -4 |
| KG Entities | 331 | 500+ | 🟡 |

---

## 🔴 PHASE 1: CRITICAL FIXES (Sofort)

### C1: Session Explosion
```
Problem: 477 Sessions akkumuliert — Ressourcenverschwendung
Lösung:
1. Alte Sessions bereinigen (>7 Tage inaktiv)
2. Session-Total reduzieren auf ~50 max
3. Automatische Cleanup-Crons aktivieren

Commands:
- openclaw sessions cleanup --all-agents
- Sessions nach nextRunAtMs older als 7 days = delete

Impact: Gateway performs faster, weniger RAM
```

### C2: Failed Crons final fix
```
Problem: CEO Daily Briefing, Token Budget, Session Cleanup, KG Lifecycle
         — diese 4 Crons haben history von failures

Lösung:
1. CEO Daily Briefing: bereits announce→none geändert ✓
2. Token Budget: delivery mode prüfen
3. Session Cleanup: delivery mode prüfen  
4. KG Lifecycle: delivery mode prüfen

Alle müssen mode:none sein (nicht announce)
```

### C3: Task Issues bereinigen
```
Problem: 88 Issues, 65 Errors im Task-Backlog
Lösung:
- openclaw tasks maintenance --apply (already done)
- Verify: check if 0 issues remaining

Falls noch issues: 
- task ID rausschreiben
- Issue-Beschreibung verifizieren
- Fix oder Close
```

---

## 🟡 PHASE 2: DOCUMENTATION CONSOLIDATION

### D1: Docs aufräumen
```
Problem: 42 Docs, viele veraltet/duplikat
Lösungs:
1. DOCS/README.md erstellen (Master-Index)
2. Duplikate finden und löschen
3. Nur aktuelle Docs behalten

Target: 42 → ~15 Docs

Aktuelle Docs (42):
- ANALYSIS/ (2 files)
- SCRIPTS/ (5 files)
- RESEARCH/ (2 files)
- SKILLS/ (1 file)
- patterns/ (?)
- Root: 30+ files

Action: Alle Docs durchgehen, obsolete löschen
```

### D2: README.md verbessern
```
Problem: docs/README.md existiert, aber nicht vollständig
Lösung:
- Write complete navigation
- Every significant doc linked
- Status for each
```

---

## 🟢 PHASE 3: SYSTEM OPTIMIZATION

### S1: Cron Health Dashboard
```
Problem: Crons failing ohne klare Übersicht
Lösung:
- Cron Status JSON erstellen: /workspace/logs/cron_status.json
- Automatisch updaten alle 6h
- CEO Daily Briefing liest dieses JSON für Status
```

### S2: KG Growth Acceleration
```
Problem: KG bei 331 entities, Ziel 500+
Lösung:
- 3 neue Topics täglich zu KG hinzufügen
- Innovation Research → KG
- Learning Coordinator → KG
- Target: +50 entities/week
```

### S3: Skills Inventory
```
Problem: Skills existieren, kein Überblick
Lösung:
- /workspace/skills/ inventarisieren
- SKILLS_INDEX.md erstellen
- Quality Score pro Skill
- Ungenutzte Skills identifizieren
```

---

## 🔵 PHASE 4: AUTOMATION ENHANCEMENT

### A1: Context Compressor aktivieren
```
Problem: Sessions bei ~205k tokens (max)
Lösung:
- Context Compressor Cron: komprimiert sessions >100k tokens
- Automatisch alle 4h
- Input: Session Size, Output: Komprimierte Version
```

### A2: Memory Flush optimieren
```
Problem: Memory könnte mehr Nutzen aus flush ziehen
Lösung:
- HEARTBEAT.md erweitern mit daily metrics
- Automatic memory consolidation
- Learning extraction automation
```

---

## 📋 EXECUTION TRACKER

### Phase 1: Critical
- [ ] C1: Session Cleanup (477 → ~50)
- [ ] C2: Cron Fixes verifizieren
- [ ] C3: Task Issues auf 0

### Phase 2: Documentation
- [ ] D1: DOCS/ bereinigen (42 → ~15)
- [ ] D2: README.md als Master-Index

### Phase 3: Optimization
- [ ] S1: Cron Status Dashboard
- [ ] S2: KG Growth (331 → 500+)
- [ ] S3: Skills Inventory

### Phase 4: Automation
- [ ] A1: Context Compressor Cron
- [ ] A2: Memory Flush optimieren

---

## 📈 SUCCESS METRICS

| Metric | Start | Target | Current |
|--------|-------|--------|---------|
| Sessions | 477 | <50 | — |
| Task Issues | 88 | 0 | — |
| Audit Errors | 65 | 0 | — |
| Docs | 42 | <20 | — |
| KG Entities | 331 | 500+ | — |
| Failed Crons | 4 | 0 | — |
| Error Rate | 1.5% | <1% | — |

---

## 🎯 NÄCHSTE SCHRITTE

1. **C1 starten** — Session Cleanup
2. **C2 verifizieren** — Alle 4 failed Crons auf mode:none?
3. **D1 planen** — Docs Bereinigung
4. **Weekly Review Cron** — wieder aktivieren (war disabled)

---

*Letztes Update: 2026-04-12 18:22 UTC*
*Sir HazeClaw — Master Improvement Plan*