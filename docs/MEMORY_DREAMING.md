# 🌙 MEMORY-CORE DREAMING — DOKUMENTATION

**Datum:** 2026-04-12 06:49 UTC
**Status:** ✅ AKTIV UND KONFIGURIERT

---

## 🎯 WAS IST DREAMING?

Dreaming ist OpenClaw's **integriertes Memory-Konsolidierungs-System**. Es bewegt kurze-term Signale automatisch in langlebigen Speicher.

---

## ⚙️ KONFIGURATION

```json
"plugins": {
  "entries": {
    "memory-core": {
      "config": {
        "dreaming": {
          "enabled": true,
          "frequency": "40 4 * * *"  // 04:40 UTC täglich
        }
      }
    }
  }
}
```

### Aktuelle Einstellungen:
| Parameter | Wert | Bedeutung |
|----------|------|-----------|
| `frequency` | `40 4 * * *` | 04:40 UTC täglich |
| `limit` | 10 | Max 10 Entries pro Promotion |
| `minScore` | 0.8 | Minimum Score zum Promoten |
| `minRecallCount` | 3 | Mindestens 3 Short-Term Recalls |
| `minUniqueQueries` | 3 | Mindestens 3 verschiedene Query-Kontexte |
| `recencyHalfLifeDays` | 14 | Recency Gewichtung |
| `maxAgeDays` | 30 | Max 30 Tage alte Entries |

---

## 🔄 PHASEN MODELL

Dreaming nutzt drei kooperative Phasen:

| Phase | Purpose | Durable Write |
|-------|---------|---------------|
| **Light** | Sortiert und staged recent signals | ❌ Nein |
| **REM** | Reflektiert über Themes und wiederkehrende Ideen | ❌ Nein |
| **Deep** | scored und promoted durable candidates | ✅ Ja (`MEMORY.md`) |

---

## 📁 OUTPUT STRUKTUR

### Memory Files:
```
~/.openclaw/workspace/ceo/
├── memory/
│   ├── .dreams/
│   │   ├── short-term-recall.json     # Recall Store (9 entries aktuell)
│   │   └── phase-signals.json         # Phase Signals
│   ├── dreaming/
│   │   ├── deep/YYYY-MM-DD.md         # Deep Phase Reports
│   │   └── rem/YYYY-MM-DD.md           # REM Phase Reports
│   └── sessions/                        # Session Transcripts
├── MEMORY.md                           # Long-term Memory Output
└── DREAMS.md                           # Dream Diary (human-readable)
```

### Recall Store Status:
```
Recall store: 9 entries · 0 promoted · 9 concept-tagged
```

---

## 🔍 STATUS PRÜFEN

```bash
openclaw memory status
openclaw memory status --deep
```

### Aktueller Status:
```
Provider: gemini (auto-detected)
Model: gemini-embedding-001
Indexed: 33/38 files · 191 chunks
Vector: ready ✅
FTS: ready ✅
Embedding cache: enabled (179 entries)
Dreaming: 04:40 UTC · limit=10 · minScore=0.8
Recall store: 9 entries · 0 promoted
```

---

## 🛠️ VERFÜGBARE COMMANDS

| Command | Purpose |
|---------|---------|
| `openclaw memory status` | Zeigt Memory Status |
| `openclaw memory status --deep` | Detaillierter Status mit Provider Check |
| `openclaw memory promote --apply` | Promote top candidates manuell |
| `openclaw memory promote --limit 5` | Preview top 5 candidates |
| `openclaw memory promote-explain "query"` | Erklärt warum ein Entry promoted würde |
| `openclaw memory rem-harness` | Preview REM ohne zu schreiben |
| `openclaw memory search "query"` | Memory durchsuchen |

---

## 🚨 TROUBLESHOOTING

### Problem: "No API key found for provider"
**Lösung:** Google API Key in auth-profiles.json:
```json
{
  "version": 1,
  "profiles": {
    "google:global": {
      "type": "api_key",
      "provider": "google",
      "key": "YOUR_API_KEY"
    }
  }
}
```

Pfad: `~/.openclaw/agents/ceo/agent/auth-profiles.json`

### Problem: Vector not ready
**Lösung:** Gedulde bis Provider API Key verfügbar ist. Keyword search funktioniert trotzdem.

---

## 📊 GESICHTSPUNKTE

### ✅ Vorteile:
- Automatische Memory Konsolidierung
- Deep Ranking mit 6 gewichteten Signalen
- Recency + Frequency + Relevance + Query Diversity
- Konzept-Tagging automatisch
- Dream Diary für Menschen lesbar

### ⚠️ Limitationen:
- Braucht Google API Key für Vector Embeddings
- Ohne API Key nur Keyword search
- Promotion Threshold relativ hoch (minScore 0.8)

---

## 🔗 Integration mit KG

Der Knowledge Graph und Memory-Core Dreaming sind **separat**:

| System | Pfad | Purpose |
|--------|------|---------|
| Knowledge Graph | `core_ultralight/memory/knowledge_graph.json` | Explizite Learnings & Entities |
| Memory-Core Dreaming | `memory/` + SQLite | Automatische Memory Konsolidierung |

---

*Letztes Update: 2026-04-12 06:49 UTC*
*Sir HazeClaw — Memory System Documentation*
