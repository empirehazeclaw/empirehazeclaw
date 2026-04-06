# Memory Stabilization Plan

## Aktueller Status

| Component | Status | Details |
|-----------|--------|---------|
| Memory Plugin | ⚠️ Empty | Keine Sessions gespeichert |
| main.sqlite | ⚠️ 0 rows | Meta/Chunks sind leer |
| dev.sqlite | ⚠️ 0 rows | - |
| researcher.sqlite | ⚠️ 0 rows | - |

## Problem

Memory Search ist aktiviert aber die Datenbanken sind leer. Das bedeutet:
- Keine Konversationen werden gespeichert
- Kein Context zwischen Sessions

## Lösungen

### 1. Gateway neustarten (löscht evtl. Probleme)
```bash
systemctl --user restart openclaw-gateway.service
```

### 2. Memory-DBs neu initialisieren
```bash
# Backup erstellen
cp ~/.openclaw/memory/*.sqlite ~/.openclaw/backups/memory/

# Gateway stoppen, DBs löschen, neu starten
systemctl --user stop openclaw-gateway.service
rm ~/.openclaw/memory/*.sqlite
systemctl --user start openclaw-gateway.service
```

### 3. Ollama Embeddings prüfen
Memory nutzt Embeddings für Suche. Prüfen:
```bash
curl http://127.0.0.1:11434/api/tags
```

## Script erstellt

- `~/scripts/memory_stabilizer.py` - Backup & Check Tool

---

*Stand: 2026-03-03*
