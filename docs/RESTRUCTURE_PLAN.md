# 📋 WORKSPACE RESTRUKTURIERUNG — PLAN
**Datum:** 2026-04-11 12:43 UTC
**Status:** GEPLANT (nicht gestartet)

---

## 📊 STATUS QUO

```
workspace/
├── SOUL.md, IDENTITY.md, USER.md, AGENTS.md, TOOLS.md, MEMORY.md  (6 System)
├── HEARTBEAT.md, MASTER_TODO.md, RESEARCH_TODO.md, etc.           (5 Root)
├── ceo/                                                              (19 Docs)
├── scripts/                                                          (55 Scripts)
├── skills/                                                           (16 Skills)
├── docs/                                                             (3 Docs)
└── archive/
```

**Problem:** unnötig tief verschachtelt, Double Locations

---

## 🎯 ZIEL-STRUKTUR

```
workspace/
├── SOUL.md, IDENTITY.md, USER.md, AGENTS.md, TOOLS.md, MEMORY.md  (6 System)
├── HEARTBEAT.md, MASTER_TODO.md, LEARNING_LOOP.md                  (3 Status)
├── SCRIPTS/                                                         (55 Scripts)
├── SKILLS/                                                          (16 Skills)
├── docs/ANALYSIS/                                                   (Analysen)
├── docs/SCRIPTS/                                                    (Script Docs)
├── docs/SKILLS/                                                     (Skill Docs)
├── docs/RESEARCH/                                                   (Research)
├── memory/                                                          (Daily Memories)
└── ARCHIVE/                                                         (Archivierte)
```

---

## 📋 AKTIONSPLAN

### Phase 1: Vorbereitung ✅
- [x] Backup: workspace_restructuring_20260411_1243.tar.gz
- [x] Git Rollback Point: pre_restructuring_20260411
- [x] Plan dokumentiert

### Phase 2: docs/ Strukturieren ⏳
- [ ] docs/ANALYSIS/ erstellen
- [ ] docs/SCRIPTS/ erstellen
- [ ] docs/SKILLS/ erstellen
- [ ] docs/RESEARCH/ erstellen

### Phase 3: CEO Files Zusammenführen
- [ ] ceo/2DAY_REFLECTION.md → docs/ANALYSIS/
- [ ] ceo/DEEP_SYSTEM_ANALYSIS.md → docs/ANALYSIS/
- [ ] ceo/DUAL_LAYER_ANALYSIS.md → docs/ANALYSIS/
- [ ] ceo/LEARNING_LOOP_OPTIMIZATION.md → LEARNING_LOOP.md
- [ ] ceo/SIMPLIFIED_LEARNING_LOOP.md → mergen
- [ ] ceo/SCRIPTS_*.md → docs/SCRIPTS/
- [ ] ceo/SKILLS_INVENTORY.md → docs/SKILLS/
- [ ] ceo/KNOWLEDGE_GRAPH.md → docs/RESEARCH/
- [ ] ceo/RESEARCH_TODO.md → docs/RESEARCH/
- [ ] ceo/Daily_Review.md → memory/
- [ ] ceo/HEARTBEAT.md → root (überschreiben)
- [ ] ceo/MASTER_TODO.md → root (überschreiben)

### Phase 4: CEO Verzeichnis auflösen
- [ ] ceo/ löschen (wenn leer)

### Phase 5: Root Docs bereinigen
- [ ] RESEARCH_TODO.md → docs/RESEARCH/

### Phase 6: TESTEN
- [ ] Gateway Status
- [ ] Cron Jobs
- [ ] Learning Coordinator
- [ ] Memory Search
- [ ] Scripts ausführbar

---

## 🔄 ROLLBACK

```bash
# Backup
tar -xzf /home/clawbot/.openclaw/backups/workspace_restructuring_20260411_1243.tar.gz

# Git
git reset --hard pre_restructuring_20260411
```

---

*Erstellt: 2026-04-11 12:43 UTC*
