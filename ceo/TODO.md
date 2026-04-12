# 📋 TODO — Sir HazeClaw
**Created:** 2026-04-12 08:57 UTC
**Updated:** 2026-04-12 09:37 UTC

---

## 🎯 IMPACT PRIORITY (Höchster Impact zuerst)

| # | Task | Impact | Effort | Status |
|---|------|--------|--------|--------|
| **P1** | **Modal Token erneuern (GLM-5.1)** | 🔴 HOCH | Niedrig | ⚠️ NICO |
| **P2** | **Modelle inventarisieren + OpenRouter testen** | 🔴 HOCH | Mittel | 🔴 OFFEN |
| **P3** | Skills Inventory erstellen | 🟡 MED | Mittel | 🔴 OFFEN |
| **P4** | Workspace aufräumen (Archive) | 🟡 MED | Hoch | 🔴 OFFEN |
| **P5** | KG retrieval fix (access_count=0) | 🟡 MED | Mittel | 🔴 OFFEN |
| **P6** | MCP Inventory | 🟢 NIEDRIG | Mittel | 🔴 OFFEN |

---

## 🟡 WEEK 2 VORBEREITUNG (2026-04-13 bis 2026-04-19)

### Documentation (heute abschließen)
- [x] SECRETS_MANAGEMENT.md — ✅ FERTIG
- [x] SCRIPT_INDEX.md — ✅ FERTIG
- [x] CRON_INDEX.md — ✅ FERTIG
- [x] KG_INDEX.md — ✅ FERTIG
- [x] DOCUMENTATION_STATUS.md — ✅ FERTIG
- [ ] ~~MODELS_INVENTORY.md~~ → **P2 verschoben**
- [ ] ~~SKILLS_INDEX.md~~ → **P3 verschoben**

### Week 2 Consolidation
- [ ] Scripts: 62 → ~40 (Konsolidierung)
- [ ] Crons: 45 → ~30 (25 disabled review)
- [ ] KG: 260 → 500 entities (quality + growth)
- [ ] KG retrieval fix (access_count = 0)

---

## 🔴 HIGH IMPACT TASKS (Starten mit P1)

### P1: MODAL TOKEN (Impact: HOCH) ⚠️ NICO AKTION
```
Problem: Modal Token "invalid" — GLM-5.1 nicht nutzbar
Lösung: Nico muss neuen Token generieren
URL: modal.com/glm-5-endpoint
Status: WARTET AUF NICO
```

### P2: MODELS INVENTORY (Impact: HOCH)
```
Warum: System hat keine vollständige Model-Doku
Problem: OpenRouter Keys funktionieren aber nicht voll getestet
         qwen3-coder:free ist rate-limited
         nemotron-3-super:free funktioniert ✅
         
Aufgaben:
  [ ] OpenRouter Modelle durchtesten
  [ ] MiniMax Backup dokumentieren
  [ ] Google Gemini als Fallback prüfen
  [ ] MODELS_INVENTORY.md erstellen
  
Impact: Wir wissen genau welche Modelle funktionieren
```

---

## 🟡 MEDIUM IMPACT TASKS

### P3: SKILLS INVENTORY (Impact: MED)
```
Warum: Skills existieren aber kein zentrales Inventory
Problem: Quality > Quantity Regel nicht messbar
Aufgaben:
  [ ] Alle Skills in workspace/skills/ inventarisieren
  [ ] Quality Score für jeden Skill
  [ ] SKILLS_INDEX.md erstellen
  [ ] Ungenutzte Skills identifizieren
```

### P4: WORKSPACE AUFRÄUMEN (Impact: MED)
```
Warum: Archive, Checkpoints, ungenutzte Ordner
Problem: 102 Docs, viele veraltet/duplikat
Aufgaben:
  [ ] workspace/archive/ bereinigen
  [ ] workspace.checkpoints/ aufräumen
  [ ] Duplikate zusammenführen
  [ ] DOC_INDEX.md als Master-Index
```

### P5: KG RETRIEVAL FIX (Impact: MED)
```
Problem: access_count = 0 für ALLE entities
Bedeutet: KG retrieval ist kaputt
Aufgaben:
  [ ] memory_hybrid_search.py debuggen
  [ ] KG update mechanismus prüfen
  [ ] MEMORY_API.py KG priority fixen
  [ ] Testen mit bekannten entities
```

### P6: MCP INVENTORY (Impact: NIEDRIG)
```
Warum: MCP Server könnten nützlich sein
Problem: Kein Inventory, MCP_EVALUATION.md veraltet
Aufgaben:
  [ ] MCP Server inventarisieren
  [ ] Nutzen evaluieren
  [ ] MCP_INVENTORY.md erstellen
```

---

## 📊 KPI TRACKER (Daily)

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Error Rate | 1.4% | <1% | 🟡 Close |
| KG Entities | 260 | 500+ | 🔴 |
| Scripts | 62 | <40 | 🟡 |
| Active Crons | 20 | <30 | ✅ |
| Security Score | 85 | 90+ | 🟡 |
| Session Size | 10KB | 200B | 🔴 |
| Docs (Total) | 102 | <50 | 🔴 |
| Modelle funktional | 1 | 3+ | 🔴 |

---

## ✅ COMPLETED (2026-04-12)

- [x] Secrets konsolidiert (35 Keys, 600 permissions, redacted)
- [x] SECRETS_MANAGEMENT.md ✅
- [x] API_KEYS_INVENTORY.md ✅
- [x] SECRETS_DOCUMENTATION_SUMMARY.md ✅
- [x] DOCUMENTATION_STATUS.md ✅
- [x] .gitignore erweitert (*.env, secrets/)
- [x] OPENROUTER_API_KEY_2 entfernt (invalid)
- [x] MODAL_API_KEY als ungültig markiert
- [x] OpenRouter Key 1 getestet → FUNKTIONIERT ✅

---

## 🚨 KNOWN ISSUES

| # | Issue | Priority | Owner | Status |
|---|-------|----------|-------|--------|
| I1 | Modal Token ungültig | 🔴 HIGH | Nico | ⚠️ WARTET |
| I2 | KG retrieval broken | 🟡 MED | Sir HazeClaw | Week 2 |
| I3 | Workspace unübersichtlich | 🟡 MED | Sir HazeClaw | Week 2 |
| I4 | Modelle nicht getestet | 🔴 HIGH | Sir HazeClaw | P2 |
| I5 | Skills kein Inventory | 🟡 MED | Sir HazeClaw | P3 |

---

## 📅 WOCHE 2 PLAN (2026-04-13 bis 2026-04-19)

| Tag | Focus | Tasks |
|-----|-------|-------|
| **So** | Documentation ✅ | Secrets, Docs Status |
| **Mo** | P2: Models | Modelle inventarisieren |
| **Di** | P3: Skills | Skills Index erstellen |
| **Mi** | P5: KG Fix | KG retrieval reparieren |
| **Do** | P4: Workspace | Aufräumen |
| **Fr** | P6: MCP | MCP evaluieren |
| **Sa** | Review | Week 2 retrospektive |

---

*Letztes Update: 2026-04-12 09:37 UTC*
*Sir HazeClaw — Todo mit Impact Priority*
