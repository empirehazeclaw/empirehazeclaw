# DEEP SYSTEM AUDIT — 2026-04-18
## Ziel: Lean, Functional, Stable — Tiefenanalyse

---

## PHASE 1: CRON AUDIT (33 Crons)

### Prüfkriterien pro Cron:
1. **Script exist?** (`ls`)
2. **Letzter Run OK?** (Status prüfen)
3. **Output relevant?** (Log greppen nach echten Ergebnissen)
4. **Redundancy?** (Andere Cron macht dasselbe?)
5. **Keep/Kill?** (Entscheidung + Begründung)

### Checkliste:
```
[ ] Unified Task Logger (15min)
[ ] Agent Delegation Cron (15min)
[ ] Autonomy Supervisor (5min)
[ ] Agent Executor Cron (5min)
[ ] Gateway Recovery (15min)
[ ] Failure Logger (hourly)
[ ] Bug Hunter (30min)
[ ] Bug Fix Pipeline (hourly) — DELETED
[ ] Learning Core Hourly (hourly)
[ ] Smart Evolver Hourly (hourly)
[ ] Meta Learning Pipeline (hourly) — DELETED
[ ] Integration Health Check (3h)
[ ] KG Access Updater (4h)
[ ] Goal Alerts Daily (daily)
[ ] Agent Self-Improver (daily 18:00)
[ ] Evening Capture (21:00) — DELETED
[ ] REM Feedback Integration (8h, 20h)
[ ] GitHub Backup (23:00)
[ ] Token Budget Tracker (00:00)
[ ] Weekly Maintenance (Sunday 04:00)
[ ] CEO Weekly Review (Monday 10:00) — DELETED
[ ] + alle anderen
```

---

## PHASE 2: KG ENTITY AUDIT

### Prüfkriterien:
1. **Entity-Typen zählen** (Wie viele pro Typ?)
2. **wertvolle Entities** (Tatsächlich genutzt?)
3. **Trash Entities** (Veraltet, test, _temp?)
4. **Orphan Rate** — Ist sie wirklich ein Problem?

### Befehl:
```bash
python3 -c "
import json
kg = json.load(open('memory/kg/knowledge_graph.json'))
types = {}
for eid, ent in kg['entities'].items():
    t = ent.get('type', 'unknown')
    types[t] = types.get(t, 0) + 1
print(json.dumps(types, indent=2))
"
```

---

## PHASE 3: LEARNING LOOP AUDIT

### Prüfkriterien:
1. **Läuft seit wann?** (Erste Evidenz in Logs)
2. **Was hat sich geändert?** (Score-Verlauf)
3. **Echte Verbesserungen oder nur Palaver?**
4. **Werden Learnings angewendet oder nur gesammelt?**

### Befehle:
```bash
tail -20 logs/learning_core.log
cat data/learning_loop_signal.json | python3 -m json.tool | grep -E '"score"|"pattern"|"learning"'
```

---

## PHASE 4: REDUNDANZ-MATRIX

### Overlap-Check:
| System A | System B | Overlap? | Wer gewinnt? |
|----------|----------|----------|---------------|
| Learning Core | Learning Coordinator | Beide learnings | Learning Core (hourly) behalten |
| Smart Evolver | Mad-Dog | Beide evolver | Smart Evolver behalten |
| Bug Hunter | Bug Fix Pipeline | Beide bug-finding | Bug Hunter (30min) behalten |
| Integration Health | System Maintenance | Beide health | System Maintenance (6h) behalten |
| KG Access Updater | KG Auto-Prune | Beide KG | KG Access Updater behalten |
| Goal Alerts | ? | Unklar | Prüfen |

---

## PHASE 5: SCRIPT INVENTUR

### Prüfkriterien:
1. **Wird Script von Cron verwendet?**
2. **Wird Script von anderem Script verwendet?**
3. **Oder steht es nur rum?**

### Befehl:
```bash
grep -r "script_name.py" /workspace --include="*.py" --include="*.sh" --include="*.md" | grep -v "backups" | grep -v ".pyc"
```

---

## ENTSCHEIDUNGS-MATRIX (Final)

| Item | Status | Begründung |
|------|--------|------------|
| Crons | X active | Nach Audit |
| KG Entities | X value, Y trash | Nach Audit |
| Scripts | X used, Y orphan | Nach Audit |
| Redundancy | X overlaps resolved | Nach Audit |

---

## OUTPUT:
- Crons: `docs/DEEP_AUDIT_CRON_STATUS.md`
- KG: `docs/DEEP_AUDIT_KG_STATUS.md`
- Scripts: `docs/DEEP_AUDIT_SCRIPT_INVENTORY.md`
- Final: `MEMORY.md` + `HEARTBEAT.md` updated

**Start:** 2026-04-18 13:35 UTC
