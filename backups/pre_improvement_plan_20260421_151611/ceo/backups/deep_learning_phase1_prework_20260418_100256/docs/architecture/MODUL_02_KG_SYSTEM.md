# MODUL 02: Knowledge Graph System

**Modul:** Knowledge Graph (KG)
**Status:** ✅ Dokumentiert
**Letztes Update:** 2026-04-17

---

## 2.1 OVERVIEW

Der Knowledge Graph ist das **Langzeit-Gedächtnis** des Systems. Er speichert:
- Fakten über Nico
- System-Konfiguration
- Lern-Erkenntnisse
- Skills und Capabilities
- Script-Katalog
- Decision Patterns

### Aktuelle Stats

| Metric | Wert |
|--------|------|
| Entities | 444 |
| Relations | 628 |
| Orphans | 0 ✅ |
| Datei | `ceo/memory/kg/knowledge_graph.json` |

---

## 2.2 STRUKTUR

### Entity Types

Der KG enthält verschiedene Entity-Typen:

| Type | Beschreibung | Beispiel |
|------|-------------|----------|
| `user` | Nico's Profile | Name, Preferences, Background |
| `script` | Scripts | Name, Pfad, Status, Purpose |
| `skill` | Skills | Name, Category, Capabilities |
| `learning` | Learnings | Pattern, Context, Source |
| `decision` | Decisions | Choice, Rationale, Outcome |
| `system` | System-Komponenten | Gateway, Crons, Memory |
| `project` | Projekte | Status, Notes |
| `pattern` | Verhaltensmuster | Recognition, Response |
| `cron` | Cron Jobs | Name, Schedule, Status |
| `file` | Wichtige Files | Path, Purpose |

### Relations Types

| Relation | Beschreibung |
|----------|--------------|
| `uses` | Script verwendet Skill |
| `depends_on` | Abhängigkeiten |
| `part_of` | Komponenten eines Systems |
| `learned_from` | Learning Quelle |
| `scheduled_by` | Cron triggert Script |
| `connected_to` | System-Verbindungen |
| `precedes` | Lern-Reihenfolge |

---

## 2.3 KG CONSOLIDATION (2026-04-16)

**Datum:** 2026-04-16

### Was gemacht wurde

1. **2 KGs → 1 KG** gemergt
   - Alte KG: `core_ultralight/memory/knowledge_graph.json`
   - CEO KG: `ceo/memory/kg/knowledge_graph.json`
   - Ergebnis: `ceo/memory/kg/knowledge_graph.json`

2. **Alle Scripts umgestellt** auf CEO KG

3. **Validation:** 0 Orphans (alle Entities haben Relationships)

### Vorher/Nacher

| Metric | Vorher | Nachher |
|--------|--------|---------|
| Entities | ~360 | 434 |
| Relations | ~500 | 614 |
| Orphans | 12 | 0 |

---

## 2.4 KG SCRIPTS

### Haupt-Scripts

| Script | Zweck |
|--------|-------|
| `kg_access_updater.py` | KG Zugriffe tracken & aktualisieren |
| `kg_access_updater_optimized.py` | Optimierte Version |
| `kg_auto_curator.py` | Automatische KG-Pflege |
| `kg_updater.py` | KG manuell updaten |
| `learning_to_kg_sync.py` | Learning Loop → KG Sync |

### KG Update Cron

```json
{
  "name": "KG Access Updater",
  "schedule": "0 */4 * * *",
  "enabled": true,
  "lastRun": "OK",
  "nextRun": "+4 hours"
}
```

---

## 2.5 KG NUTZUNG

### Wie der KG aktualisiert wird

1. **Learning Loop → KG Sync** (stündlich)
   ```bash
   python3 /workspace/scripts/learning_to_kg_sync.py --apply
   ```

2. **KG Access Updater** (alle 4h)
   ```bash
   python3 /workspace/scripts/kg_access_updater_optimized.py
   ```

3. **Manuell**
   ```bash
   python3 /workspace/scripts/kg_updater.py
   ```

### Wie der KG gelesen wird

```python
import json
kg = json.load(open('/home/clawbot/.openclaw/workspace/ceo/memory/kg/knowledge_graph.json'))
entities = kg['entities']
relations = kg['relations']
```

---

## 2.6 KG QUALITY METRICS

| Metric | Wert | Status |
|--------|------|--------|
| Entity Count | 444 | ✅ Gut |
| Relation Count | 628 | ✅ Gut |
| Orphan Count | 0 | ✅ Perfekt |
| Entity Types | 10+ | ✅ Divers |
| Freshness | Täglich | ✅ OK |

---

## 2.7 BEKANNTE ISSUES

| Issue | Status | Notes |
|-------|--------|-------|
| KG Access Updater Timeout | ⚠️ 2x | Cron meldet timeout, Script selbst OK |
| Stale KG Backups | 🗑️ | Alte core_ultralight KG备份 können gelöscht werden |

---

## 2.8 BACKUP

| Backup | Location |
|--------|----------|
| CEO KG | `ceo/memory/kg/knowledge_graph.json` |
| Integration Backup | `backups/integration_backup_20260416_185449/kg/` |
| Post-Integration | `backups/post_integration_20260416_210413/kg/` |

---

*Modul 02 — Knowledge Graph | Sir HazeClaw 🦞*
