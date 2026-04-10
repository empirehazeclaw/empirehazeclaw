# 🧠 MEMORY ARCHITECTURE — OFFIZIELLE DOKUMENTATION

**Datum:** 2026-04-10 21:40 UTC
**Status:** ✅ ANALYSIERT & DOKUMENTIERT

---

## ⚠️ KRITISCHE FINDING (2026-04-10)

**MEHRERE SCRIPTS ZEIGTEN AUF DEN FALSCHEN KNOWLEDGE GRAPH!**

| Script | Alte KG Path | Status |
|--------|--------------|--------|
| kg_updater.py | `/home/clawbot/.openclaw/memory/kg.json` | ❌ WRONG |
| dream_reflection.py | `workspace/memory/knowledge_graph.json` | ❌ NON-EXISTENT |
| memory_cleanup.py | `workspace/memory/knowledge_graph.json` | ❌ NON-EXISTENT |
| memory_hybrid_search.py | `workspace/memory/knowledge_graph.json` | ❌ NON-EXISTENT |
| memory_vector_store.py | `workspace/memory/knowledge_graph.json` | ❌ NON-EXISTENT |
| kgml_summary.py | `knowledge_graph.json` (relative) | ❌ WRONG |

**ALLE SCRIPTS WURDEN FIXED → zeigen jetzt auf den RICHTIGEN KG.**

---

## 📁 MEMORY VERZEICHNISSE

### 1. `/home/clawbot/.openclaw/memory/` — SYSTEM MEMORY (SQLite)

| File | Size | Purpose | Status |
|------|------|---------|--------|
| main.sqlite | 380 MB | **HAUPT-SEMANTISCHE MEMORY** — Vector Embeddings + Text Chunks | ✅ ACTIVE |
| ceo.sqlite | 37 MB | CEO-spezifische Embeddings + Chunks | ✅ ACTIVE |
| data.sqlite | 80 KB | Allgemeine Daten | ✅ ACTIVE |
| kg.json | 16 KB | **VERALTET** — Falscher KG (Skill-Tracking) | ❌ IGNORIEREN |

### 2. `/home/clawbot/.openclaw/workspace/memory/` — PERSÖNLICHE MEMORY

| File/Dir | Purpose | Status |
|----------|---------|--------|
| `2026-04-10.md` | Tägliche Session-Logs | ✅ ACTIVE |
| `notes/fleeting/` | Short-term Notes | ✅ ACTIVE |
| `notes/permanent/` | Permanenta Notizen | ✅ ACTIVE |
| `vault.enc.json` | Verschlüsselte Secrets | ✅ ACTIVE |
| `.dreams/` | Traum/Reflexion Data | ✅ ACTIVE |
| `.vault-key` | Vault Passkey | 🔒 SECURE |

### 3. `/home/clawbot/.openclaw/workspace/core_ultralight/memory/` — **WICHTIGSTER KG**

| File | Size | Purpose | Status |
|------|------|---------|--------|
| **knowledge_graph.json** | **1.7 MB** | **🎯 DER ECHTE KNOWLEDGE GRAPH** | ✅ **ACTIVE** |
| semantic_index.json | 466 KB | Semantischer Such-Index (51 Docs) | ✅ ACTIVE |
| MASTER_INDEX.json | 10 KB | Index aller Memory Files | ✅ ACTIVE |
| MEMORY_ANONYMIZED.md | 24 KB | Anonymisiertes Schema | 📖 REFERENCE |
| META_SCHEMA_ANONYMIZED.md | 9 KB | Meta-Schema | 📖 REFERENCE |
| CHRONOLOGY_ANONYMIZED.md | 3 KB | Chronologie | 📖 REFERENCE |

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

### Entity Types:
```
topic: 48 | subtopic: 18 | note: 15 | sales: 11 | concept: 11+
marketing: 6 | product: 5 | usecase: 5 | system: 5 | pattern: 3
```

### Beispiel Entities:
- **EmpireHazeClaw** (HIGH PRIORITY) — Business
- **KI-Mitarbeiter** (HIGH PRIORITY) — Produkt
- **Zielgruppe-KMU** (HIGH PRIORITY) — Business
- **Solo Fighter Mode** — Sir HazeClaw Architektur
- **skill_loop_prevention** — Self-created Skill

---

## 📊 ANDERE SYSTEM-DATENBANKEN

| Database | Path | Purpose |
|----------|------|---------|
| tasks/runs.sqlite | `/home/clawbot/.openclaw/tasks/runs.sqlite` | Task Execution History |
| flows/registry.sqlite | `/home/clawbot/.openclaw/flows/registry.sqlite` | Flow/Automation Registry |
| agents/ceo/qmd/index.sqlite | `/home/clawbot/.openclaw/agents/ceo/qmd/xdg-cache/qmd/index.sqlite` | QMD Agent Index |

---

## 🔧 SCRIPT KG-REFERENCES (JETZT ALLE FIXED)

| Script | Korrigierte KG Path |
|--------|---------------------|
| kg_updater.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| dream_reflection.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| kgml_summary.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| memory_cleanup.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| memory_hybrid_search.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |
| memory_vector_store.py | `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json` |

---

## ⚠️ VERMEIDEN: DIESE PATHS

| Path | Warum |
|------|-------|
| `/home/clawbot/.openclaw/memory/kg.json` | **FALSCH** — Skill-Tracking, nicht der echte KG |
| `/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json` | **EXISTIERT NICHT** — wurde nie erstellt |

---

## 🛠️ KG OPERATIONEN

### Lesen:
```bash
python3 -c "
import json
kg = json.load(open('/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json'))
print(f'Entities: {len(kg[\"entities\"])}, Relations: {len(kg[\"relations\"])}')
"
```

### Suchen:
```bash
grep -i "Suchbegriff" /home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json
```

### KG updaten (nach Merging):
```bash
python3 /home/clawbot/.openclaw/workspace/scripts/kg_updater.py add \
  --type skill \
  --name "New Skill" \
  --content "Description"
```

### Backup:
```bash
cp /home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json \
   /home/clawbot/.openclaw/backups/kg_backup_$(date +%Y%m%d_%H%M).json
```

---

## 📋 MEMORY TYPES ÜBERSICHT

| Type | Speicherort | Format | Usage |
|------|-------------|--------|-------|
| **Semantic Memory** | main.sqlite / ceo.sqlite | SQLite + Embeddings | Volltextsuche |
| **Knowledge Graph** | core_ultralight/memory/ | JSON | Beziehungen |
| **Episodic Memory** | workspace/memory/2026-*.md | Markdown | Sessions |
| **Procedural Memory** | workspace/scripts/ | Python | Automatisierung |
| **Fleeting Notes** | workspace/memory/notes/fleeting/ | Markdown | Kurzzeit |
| **Permanent Notes** | workspace/memory/notes/permanent/ | Markdown | Langzeit |
| **Encrypted Secrets** | workspace/memory/vault.enc.json | JSON (encrypted) | Secrets |

---

## 🔄 MEMORY FLOW

```
[User Input]
     ↓
[Memory Core Plugin] → main.sqlite (embeddings)
     ↓
[Knowledge Graph] → core_ultralight/memory/knowledge_graph.json
     ↓
[Episodic Memory] → workspace/memory/YYYY-MM-DD.md
     ↓
[Skills] → workspace/skills/*/
     ↓
[Output]
```

---

## 📝 REGELN FÜR ZUKUNFT

1. **KG IMMER an diesem Pfad:**
   `/home/clawbot/.openclaw/workspace/core_ultralight/memory/knowledge_graph.json`

2. **NIE diese Paths verwenden:**
   - `/home/clawbot/.openclaw/memory/kg.json`
   - `/home/clawbot/.openclaw/workspace/memory/knowledge_graph.json`

3. **Bei neuen Scripts:**
   - Immer zuerst prüfen welcher KG verwendet wird
   - DIESE DOKUMENTATION lesen

4. **Bei Unsicherheit:**
   - `MEMORY_ARCHITECTURE.md` konsultieren
   - or `KNOWLEDGE_GRAPH.md` für KG-spezifische Fragen

---

*Sir HazeClaw — Memory Architecture Documentation*
*Letztes Update: 2026-04-10 21:40 UTC*
*Grund: Tiefenanalyse enthüllte falsche KG-Referenzen in 6 Scripts — alle korrigiert*