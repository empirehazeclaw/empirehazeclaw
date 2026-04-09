# 📊 memorX System Architecture - Diagnostic Report

*Erstellt: 2026-04-05 15:06 UTC*
*System: OpenClaw Workspace / EmpireHazeClaw*

---

## 1. IST-ZUSTAND DER ARCHITEKTUR

### Speicherschichten (Hierarchisch)

| Schicht | Path | Typ | Größe | Status |
|---------|------|-----|-------|--------|
| **Core Identity** | SOUL.md, IDENTITY.md, USER.md | Markdown | ~8KB | ✅ Aktiv |
| **Operations Memory** | MEMORY.md | Markdown | ~3KB | ✅ Aktiv (bereinigt) |
| **System State** | SYSTEM_CORE.md | Markdown | ~8KB | ⚠️ Veraltet (März) |
| **Knowledge Graph** | memory/knowledge_graph.py | JSON | 0 Bytes | ❌ Leer |
| **Daily Notes** | memory/YYYY-MM-DD.md | Markdown | 3 Files | ⚠️ Letzter: 05.04 |
| **Decisions** | memory/decisions/ | Markdown | 1 File | ✅ |
| **Learnings** | memory/learnings/ | Markdown | 2 Files | ✅ |
| **Vektor Store** | vector_store/corpus.txt | Text | ~1KB | ❌ Kaum genutzt |
| **Session Memory** | memory/sessions/ | JSON | 0 Files | ❌ Nicht aktiv |

### OpenClaw Memory Integration

```json
"hooks": {
  "internal": {
    "session-memory": { "enabled": true }
  }
}
"agents": {
  "defaults": {
    "memorySearch": {
      "provider": "gemini",
      "model": "gemini-embedding-exp-03-07"
    }
  }
}
"compaction": {
  "mode": "safeguard"
}
```

### LCM (Lossless-Claw) Plugin

```json
"lossless-claw": {
  "enabled": true,
  "config": {
    "contextThreshold": 0.8  // ↑ wurde von 0.7 erhöht
  }
}
```

---

## 2. DATENFLUSS-MECHANIK

### Wie OpenClaw Memory nutzt:

```
[Telegram/Nico] 
       ↓
[OpenClaw Gateway] → Lädt MEMORY.md, SOUL.md, USER.md (Project Context)
       ↓
[Session Start] → memory_search() → Vektor-Suche über memory/*.md
       ↓
[LCM Compaction] → Trigger bei 80% Context-Füllung → Zusammenfassung
       ↓
[Session-Ende] → session-memory Hook → Speichert in memory/sessions/
```

### Manueller Memory-Flow:

```
[Automatisch]
- Cron: memory_backup.py (täglich) → Git Commit
- Cron: autosync_v2.js (täglich) → MEMORY.md aktualisieren
- Cron: daily_summary.py (23:00) → memory/YYYY-MM-DD.md

[Manuell via Agent]
- memory_search(query) → semantische Suche
- memory_get(path, lines) →Snippet laden
- autosync_v2.js --type decision → Entscheidungen speichern
```

---

## 3. SCHWACHSTELLEN-ANALYSE

### 🔴 KRITISCH

| # | Problem | Auswirkung |
|---|---------|------------|
| 1 | **knowledge_graph.json ist leer (0 Bytes)** | PARA-Methode funktioniert nicht, Fakten werden nicht strukturiert gespeichert |
| 2 | **Session Memory Hook schreibt keine Sessions** | Keine Persistenz zwischen Sessions |
| 3 | **autosync_v2.js Cron NICHT aktiv** | MEMORY.md wird nicht automatisch synchronisiert |
| 4 | **SYSTEM_CORE.md veraltet (März)** | Agent sieht alten State |

### 🟡 MITTEL

| # | Problem | Auswirkung |
|---|---------|------------|
| 1 | **Vektor Store (vector_store/) kaum genutzt** | memorySearch mit Gemini funktioniert, aber Korpus ist fast leer |
| 2 | **memory/sessions/ existiert nicht** | Session-übergreifende Kontextspeicherung fehlt |
| 3 | **Daily Notes nur 3 Einträge** | Historische Datenlücke |
| 4 | **MEMORY_CONSOLIDATION_RULES.md definiert Regeln, aber wird nicht aktiv genutzt** | Kein automatisches Sorting |

### 🟢 MINOR

| # | Problem | Auswirkung |
|---|---------|------------|
| 1 | **Log-Dateien existieren jetzt (gerade erstellt)** | Cron-Jobs können endlich loggen |
| 2 | **Memory Auto-Sync Cron fehlt** | Manuell oder gar nicht |

---

## 4. TOKEN-EFFIZIENZ (Ist vs. Ziel)

| Metric | Aktuell | Ziel | Status |
|--------|---------|------|--------|
| **MEMORY.md geladen** | ~3KB (128 Zeilen) | <5KB | ✅ Gut |
| **SOUL.md geladen** | ~2.5KB | <2KB | ⚠️ OK |
| **USER.md geladen** | ~2KB | <2KB | ✅ Gut |
| **Workspace Context** | 11,631 Files | Nur aktive | ❌ Zu viel |
| **memory_search Ergebnisse** | variiert | Top 3-5 Snippets | ⚠️ OK |

**Problem:** Workspace mit 11,631 Files → viel irrelevanten Context beim Session-Start laden.

---

## 5. BEKANNTE FEHLER (aus Chat-History)

1. **Timeout Errors (08:00-11:00)**
   - 4x "Request timed out" durch LCM Compaction
   - LCM hängt bei 80% Threshold
   - MiniMax M2.7 antwortet zu langsam für Compaction

2. **Memory Decay nicht aktiv**
   - knowledge_graph.py hat DECAY_RATE definiert, aber wird nie aufgerufen
   - Alte Fakten verbleiben ewig

3. **Session Memory schreibt nicht**
   - Hook ist enabled, aber memory/sessions/ bleibt leer

---

## 6. KONKRETE OPTIMIERUNGsvorschläge

### SOFORT (dieser Session)

```bash
# 1. Session Memory aktivieren
mkdir -p /home/clawbot/.openclaw/workspace/memory/sessions

# 2. Autosync Cron aktivieren
crontab -e
# Add: 0 23 * * * node /home/clawbot/.openclaw/workspace/scripts/autosync_v2.js --sync

# 3. Knowledge Graph initialisieren
cd /home/clawbot/.openclaw/workspace
python3 -c "
from memory.knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()
kg.save()
print('✅ Knowledge Graph initialized')
"
```

### KURZFRISTIG (diese Woche)

| # | Änderung | Config-Datei |
|---|----------|--------------|
| 1 | **LCM Threshold erhöhen** (0.8 → 0.85) um weniger Compaction | openclaw.json |
| 2 | **Compaction Timeout setzen** (LCM hängt) | LCM Plugin hat kein timeout config → Workaround: Model auf GPT-4o-mini für Compaction |
| 3 | **Workspace Files reduzieren** - alte Scripts archivieren | Manuell |
| 4 | **Session Memory Hook debuggen** | Logs prüfen |

### MITTELFRISTIG (nächste Woche)

| # | Änderung | Beschreibung |
|---|----------|-------------|
| 1 | **Vector Store befüllen** | Wichtige Docs in vector_store/corpus.txt extrahieren |
| 2 | **Daily Notes automatisieren** | autonomous_loop.py → tägliche Notes |
| 3 | **Memory Cleanup Cron** | Alte memory/*.md > 30 Tage archivieren |
| 4 | **SYSTEM_CORE.md auto-update** | Bei jedem Session-Start refresh |

---

## 7. CONFIG-DIFF (Was ändern)

### openclaw.json - LCM Config
```json
// VON:
"contextThreshold": 0.8
// ZU:
"contextThreshold": 0.85
```

### session-memory Hook debuggen
```bash
# Prüfen ob Hook wirklich läuft:
grep -r "session-memory" /home/clawbot/.openclaw/logs/
cat /home/clawbot/.openclaw/logs/session-memory.log 2>/dev/null || echo "No log"
```

---

## 8. ZUSAMMENFASSUNG

| Kategorie | Status | Note |
|-----------|--------|------|
| **Core Memory (MEMORY.md)** | ✅ Gesund | Bereinigt auf 3KB |
| **System State** | ⚠️ Veraltet | März-Stand |
| **Session Persistenz** | ❌ Kaputt | Keine Sessions gespeichert |
| **Knowledge Graph** | ❌ Leer | PARA nicht aktiv |
| **LCM Compaction** | ⚠️ Hängt | Timeout Errors |
| **Auto-Sync** | ❌ Fehlt | Cron nicht aktiv |
| **Logging** | ✅ Jetzt OK | Gerade erstellt |

**Top 3 Actions:**
1. ✅ Logs erstellt (just done)
2. ⏳ Autosync Cron aktivieren
3. ⏳ LCM Threshold auf 0.85 erhöhen
4. ⏳ Session Memory debuggen

---

*Report erstellt von: 🦞 ClawMaster*
*Basierend auf: Chat-History + System-Scan*