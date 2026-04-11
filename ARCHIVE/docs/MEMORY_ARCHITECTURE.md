# 🧠 MEMORY ARCHITECTURE — OFFIZIELLE DOKUMENTATION

**Datum:** 2026-04-10 21:59 UTC
**Status:** ✅ VEREINFACHT

---

## ✅ WAS WIR GELÖSCHT HABEN (2026-04-10)

| File | Grund |
|------|-------|
| `memory/kg.json` | Falscher KG - verwirrend |
| `whisper_daemon.py` | Ungenutzt |
| `whisper_server.py` | Ungenutzt |
| `humanize_content.py` | Ungenutzt |
| `feature_router.py` | Ungenutzt |
| `transcribe.py` | Ungenutzt |
| `memory_vector_store.py` | Redundant (overlapped mit hybrid_search) |
| `dream_reflection.py` | Redundant (memory-core dreaming aktiv) |

**Ergebnis: 53 Scripts (vorher 60)**

---

## 📁 MEMORY VERZEICHNISSE

### 1. `/home/clawbot/.openclaw/memory/` — SYSTEM MEMORY (SQLite)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| main.sqlite | 380 MB | **SEMANTIC MEMORY** — Vector Embeddings + Text Chunks | ✅ |
| ceo.sqlite | 37 MB | CEO-spezifische Embeddings + Chunks | ✅ |
| data.sqlite | 80 KB | Allgemeine Daten | ✅ |

### 2. `/home/clawbot/.openclaw/workspace/memory/` — PERSÖNLICHE MEMORY

| File/Dir | Purpose | Status |
|----------|---------|--------|
| `2026-04-10.md` | Tägliche Session-Logs | ✅ |
| `notes/fleeting/` | Short-term Notes | ✅ |
| `vault.enc.json` | Verschlüsselte Secrets | ✅ |
| `.dreams/` | Traum/Reflexion Data | ✅ |

### 3. `/home/clawbot/.openclaw/workspace/core_ultralight/memory/` — **WICHTIGSTER KG**

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **knowledge_graph.json** | **1.7 MB** | **🎯 DER KNOWLEDGE GRAPH** | ✅ |
| semantic_index.json | 466 KB | Semantischer Such-Index | ✅ |
| MASTER_INDEX.json | 10 KB | Index aller Memory Files | ✅ |

---

## 🎯 DER RICHTIGE KNOWLEDGE GRAPH

```
DATEIPFAD: /home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json
```

| Metrik | Wert |
|--------|------|
| Entities | **173** |
| Relations | **4649** |
| Letztes Update | 2026-04-10 21:33 UTC |

---

## 🔧 AKTIVE MEMORY SCRIPTS (6)

| Script | Purpose | Status |
|--------|---------|--------|
| `kg_updater.py` | KG Entities hinzufügen | ✅ |
| `memory_cleanup.py` | KG pruning, notes cleanup | ✅ |
| `memory_hybrid_search.py` | Hybrid search (files + KG) | ✅ |
| `kgml_summary.py` | KG als Markdown exportieren | ✅ |
| `vault.py` | Secrets verschlüsseln | ✅ |

---

## 🧠 MEMORY-CORE PLUGIN (Built-in)

| Feature | Config | Status |
|---------|--------|--------|
| dreaming | enabled: true, frequency: 40 4 * * * | ✅ ACTIVE |
| semantic-index | 51 documents | ✅ |
| embeddings | 4203 total | ✅ |

---

## 📊 SYSTEM STATUS (21:59 UTC)

| Component | Status |
|-----------|--------|
| Knowledge Graph | ✅ 173 entities, 4649 relations |
| Semantic Index | ✅ 51 docs |
| main.sqlite | ✅ 771 chunks, 4024 embeddings |
| ceo.sqlite | ✅ 191 chunks, 179 embeddings |
| memory-core | ✅ Dreaming active (04:40 UTC) |
| Scripts | ✅ 53 (6 relevant) |

---

## 🚫 VERMEIDEN

| Path | Warum |
|------|-------|
| `/home/clawbot/.openclaw/memory/kg.json` | **GELÖSCHT** |
| `dream_reflection.py` | **GELÖSCHT** (redundant) |
| `memory_vector_store.py` | **GELÖSCHT** (redundant) |

---

*Sir HazeClaw — Memory Architecture Documentation*
*Letztes Update: 2026-04-10 21:59 UTC*