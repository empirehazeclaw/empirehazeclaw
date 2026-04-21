# MODUL 06: Memory System

**Modul:** Memory System — Option C (Workspace-local)
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 6.1 OVERVIEW

Das Memory System ist das **Gedächtnis** von Sir HazeClaw. Es nutzt Option C (workspace-local) mit:

- **Workspace Memory:** 564 KB
- **Global DB:** 448 MB
- **Hybrid Search:** Gemini Embeddings
- **Backup:** tar.gz Archive

### Struktur

```
ceo/memory/
├── short_term/          # Aktuelle Sessions, fleeting notes
├── long_term/           # Persistente Fakten
├── episodes/            # Erlebnisse, Events
├── procedural/          # Skills, Workflows
├── kg/                  # Knowledge Graph (JSON)
├── search/              # Such-Indices
├── notes/               # Permanent Notes
├── ARCHIVE/             # Archivierte Memories
└── 2026-04-*.md        # Daily Notes
```

---

## 6.2 MEMORY TYPES

### 6.2.1 Short-Term Memory

**Zweck:** Aktuelle Session-Daten

**Inhalt:**
- Aktive Tasks
- Letzte Decisions
- Aktuelle Context

**Location:** `ceo/memory/short_term/`

**Auto-Cleanup:** Session Cleanup Cron (daily)

---

### 6.2.2 Long-Term Memory

**Zweck:** Persistente Fakten über Nico und System

**Inhalt:**
- Fakten über Nico
- Preferences
- System-Konfiguration
- Learnings

**Location:** `ceo/memory/long_term/`

**Dateien:**
- `facts.md`
- `preferences.md`
- `patterns.md`

---

### 6.2.3 Episodic Memory

**Zweck:** Erlebnisse und Events

**Inhalt:**
- Vergangene Sessions
- Significant Events
- Entscheidungs-Episoden

**Location:** `ceo/memory/episodes/`

---

### 6.2.4 Procedural Memory

**Zweck:** Skills und Workflows

**Inhalt:**
- Skill Definitions
- Workflows
- How-To Knowledge

**Location:** `ceo/memory/procedural/`

**Dateien:**
- `skills.md`
- `workflows.md`

---

### 6.2.5 Knowledge Graph

**Siehe:** MODUL_02_KG_SYSTEM.md

---

### 6.2.6 Search Memory

**Zweck:** Hybrid Search Index

**Inhalt:**
- Embeddings
- Search Indices
- Query Logs

**Tool:** Gemini Embeddings

---

## 6.3 MEMORY SCRIPTS

### Scripts

| Script | Zweck |
|--------|-------|
| `memory_sync.py` | Memory synchronisieren |
| `memory_integrity_check.py` | Memory Integrity prüfen |
| `memory_log_analyzer.py` | Memory Logs analysieren |
| `session_cleanup.py` | Session Cleanup |
| `session_context_manager.py` | Context Manager |
| `context_compressor.py` | Context komprimieren |
| `memory_sanitizer/` | Security Sanitizer |

### Daily Memory

**Dateien:** `memory/2026-04-*.md`

**Inhalt:**
- Learning Loop Runs
- System Status
- Crons Status
- Issues

---

## 6.4 MEMORY COORDINATION

### Cron Jobs

| Cron | Schedule | Script |
|------|----------|--------|
| Memory Sync | 5 min nach jeder Stunde | `memory_sync.py` |
| Session Cleanup | Daily 03:00 | `session_cleanup.py` |
| Context Manager | Daily 03:00 | `session_context_manager.py` |
| Memory Dreaming | Daily 04:40 | Promotion Cron |
| Context Compressor | Every 6h | `context_compressor.py` |

---

## 6.5 MEMORY DREAMING (Promotion)

**Cron:** `Memory Dreaming Promotion`
**Schedule:** `40 4 * * *`

**Was es tut:**
1. Analysiert Short-Term Memory
2. Bewertet nach Weighting (recency, frequency, uniqueness)
3. Promote stabile Memories zu Long-Term
4. Update MEMORY.md

**Kriterien:**
- minScore: 0.800
- minRecallCount: 3
- minUniqueQueries: 3
- recencyHalfLifeDays: 14
- maxAgeDays: 30

---

## 6.6 EMBEDDINGS & SEARCH

### Hybrid Search

**Konfiguration:**
- Embedding Model: Gemini
- Index: lokaler Vector Index
- FTS: Full-Text Search

### Search Scripts

| Script | Zweck |
|--------|-------|
| `semantic_search/` | Semantic Search Skill |

---

## 6.7 MEMORY BACKUP

### Backup Archive

```
ceo/memory_*.tar.gz
├── memory_SANITIZED_20260414_163533.tar.gz
└── memory_export_20260414_162156.tar.gz
```

### Backup Scripts

| Script | Zweck |
|--------|-------|
| `auto_backup.py` | Daily Backup |
| `backup_manager.py` | Backup Management |
| `backup_verifier.py` | Backup Verifizierung |

---

## 6.8 MEMORY INTEGRITY

### Check Script

```bash
python3 /SCRIPTS/automation/memory_integrity_check.py
```

**Was es prüft:**
- File Corruption
- Consistency
- Orphan Detection
- Size Anomalies

---

## 6.9 MEMORY STATS

| Metric | Wert |
|--------|------|
| Workspace Memory | 564 KB |
| Global DB | 448 MB |
| Memory Chunks | 334 |
| Sessions | 544 |
| Sources | memory, plugin memory-core |

---

## 6.10 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| Memory Sanitizer | ✅ | Entfernt sensible Daten |
| Session Overflow | 👀 | 544 Sessions — Context Compressor hilft |

---

## 6.11 SESSION MANAGEMENT

### Session Context Manager

**Script:** `/SCRIPTS/automation/session_context_manager.py`

**Was es tut:**
1. Identifiziert stale Sessions
2. Promote wichtige Context zu Long-Term
3. Archiviert/abstrahlt alte Sessions

---

*Modul 06 — Memory System | Sir HazeClaw 🦞*
