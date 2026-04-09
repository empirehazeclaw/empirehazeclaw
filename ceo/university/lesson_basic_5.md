# Lektion 5: Memory & Context Management

## 🎯 Lernziel
Verstehe wie das Memory-System funktioniert und wie du Context Splitting vermeidest. Lerne memory_search, memory_get und die Recall-Pipeline.

---

## 5.1 Das OpenClaw Memory-System

### Architektur

```
┌─────────────────────────────────────────────────┐
│              OPENCLAW MEMORY                     │
│                                                  │
│  ┌─────────────┐    ┌────────────────────────┐ │
│  │ MEMORY.md   │◄───│ memory_search (semantic)│ │
│  │ (Kurzform)  │    └────────────────────────┘ │
│  └─────────────┘                               │
│         │                                       │
│         ▼                                       │
│  ┌─────────────┐    ┌────────────────────────┐ │
│  │ memory/     │◄───│ memory_get (snippet)   │ │
│  │ archive/    │    └────────────────────────┘ │
│  └─────────────┘                               │
└─────────────────────────────────────────────────┘
```

### Memory-Struktur
```
~/.openclaw/
├── memory/
│   ├── MEMORY.md              # Hauptgedächtnis (komprimiert)
│   └── archive/
│       └── HEARTBEAT-history.md  # Historische Heartbeats
├── agents/{agent}/
│   ├── memory/               # Agent-spezifisches Memory
│   └── notes/
└── skills/                   # Skill-Dokumentation
```

---

## 5.2 MEMORY.md — Die Hauptdatenbank

### Prinzip: Komprimiert & Aktuell

Die MEMORY.md ist:
- **Komprimiert** — Nur das Wesentliche
- **Maximal einige KB** — Nicht 500KB+
- **Maschinell durchsuchbar** — Semantic Search
- **Von Menschen lesbar** — Markdown

### Beispiel: Gut komprimiert
```markdown
# MEMORY.md — EmpireHazeClaw Flotte

## Aktive Agenten
| Agent | Workspace | Status |
|-------|-----------|--------|
| CEO | /workspace/ceo | Aktiv |
| Builder | /workspace/builder | Aktiv |
| Security | /workspace/security | Aktiv |

## Offene Tasks
- [ ] Security Key Rotation (Buffer, Leonardo) — BLOCKIERT: Manuell
- [ ] GitHub Backup — Wartet auf Secrets-Key

## Letzte Entscheidungen
- 2026-04-08: MetaClaw entfernt (Proxy-Probleme)
- 2026-04-08: Builder auf MiniMax-M2.7 umgestellt

## System-Config
- Gateway Port: 18789
- Model: MiniMax-M2.7 (Primary)
- Cron Jobs: 11 aktiv
```

---

## 5.3 memory_search — Semantische Suche

### Grundsyntax
```javascript
memory_search({
  query: "Security Key Rotation",
  maxResults: 5
})
```

### Wann nutzen?
- Bevor du eine Frage beantwortest
- Bei Unklarheit über vergangene Entscheidungen
- Bei Recovery nach Context Splitting

### Pipeline
```
1. memory_search({ query: "..." })
         │
         ▼
2. Bekomme Top-Snippets mit Quelle (path#line)
         │
         ▼
3. memory_get({ path: "...", from: X, lines: Y })
         │
         ▼
4. Lese nur relevante Zeilen
         │
         ▼
5. Fakten in Antwort einbetten
```

---

## 5.4 memory_get — Gezieltes Lesen

### Grundsyntax
```javascript
memory_get({
  path: "MEMORY.md",
  from: 10,
  lines: 20
})
```

### Parameter

| Parameter | Beschreibung |
|-----------|--------------|
| `path` | Pfad zur Memory-Datei |
| `from` | Start-Zeile (optional) |
| `lines` | Anzahl Zeilen (optional) |

### Wichtig
- memory_get kommt NACH memory_search
- Lese nur die Snippets die du brauchst
- Cache nicht alles — lies gezielt

---

## 5.5 Context Splitting — Der Feind

### Was ist Context Splitting?

```
Kontext-Fenster: 200K Tokens
          │
          ▼
   ┌──────────────┐
   │ Alter Kontext │
   │ wird entfernt │
   └──────────────┘
          │
          ▼
   Wichtige Infos sind WEG!
          │
          ▼
   Agent "vergisst" was vorher war
```

### Symptome
- Agent versteht Frage nicht mehr
- "Was war die letzte Entscheidung?"
- Antwortet widersprüchlich
- Derselbe Fehler wird wiederholt

---

## 5.6 Checkpoint-System

### Das Prinzip

```
BEVOR Context-Splitting passiert:

1. Schreibe Checkpoint
         │
         ▼
2. Speichere: Was läuft gerade?
         │
         ▼
3. Bei Recovery: Checkpoint lesen
         │
         ▼
4. Weiter wo du aufgehört hast
```

### Checkpoint erstellen
```javascript
write({
  path: "/home/clawbot/.openclaw/workspace/ceo/checkpoint.md",
  content: `## Checkpoint — ${new Date().toISOString()}

### Laufender Task
- Task: Backup-Script erstellen
- Delegiert an: Builder
- Erwartete Antwort: Ca. 17:30 UTC
- Status: WARTEND

### Letzter Stand
- Builder hat Script gestartet
- Mei: Backup nach /opt/backups
- Deadline: 18:00 UTC

### Nächste Aktion
- Warten auf Builder-Report
- Bei Timeout: Erinnerung senden
`
})
```

### Recovery aus Checkpoint
```javascript
// 1. Checkpoint lesen
const checkpoint = read({ path: "checkpoint.md" })

// 2. Verstehen was lief
// "Task: Backup-Script, Delegiert an Builder"

// 3. Entscheiden was zu tun ist
if (checkpoint.includes("WARTEND")) {
  // Builder-Ergebnis checken
  // oder nochmal anfragen
}
```

---

## 5.7 Recall-Pipeline bei OpenClaw

### Die offizielle Pipeline

```
FRAGE ZU VERGANGENEM
         │
         ▼
memory_search({ query: "..." })
         │
         ▼
memory_get({ path: "...", lines: N })
         │
         ▼
Fakten extrahieren
         │
         ▼
In Antwort einbetten mit Citation: "Quelle: MEMORY.md#45"
```

### Wann nutzen?

| Situation | memory_search? |
|-----------|---------------|
| "Was war nochmal das Passwort?" | ✅ Ja |
| "Welche Entscheidung haben wir getroffen?" | ✅ Ja |
| "Wer ist der Data Manager?" | ✅ Ja |
| "Was sind die aktuellen Crons?" | ✅ Ja |
| Berechne 2+2 | ❌ Nein |
| Schreibe Python-Code | ❌ Nein |

---

## 5.8 LCM — Long-term Context Memory (Advanced)

### Das Problem bei komprimiertem Kontext

Wenn MEMORY.md zu groß wird (>500KB), wird sie komprimiert. Dabei gehen möglicherweise Details verloren.

### LCM Tools

| Tool | Nutzen |
|------|--------|
| `lcm_grep` | Regex/Fulltext-Suche |
| `lcm_describe` | Summary inspizieren |
| `lcm_expand_query` | Deep Recall (sub-agent) |

### lcm_expand_query Beispiel
```javascript
lcm_expand_query({
  query: "Database Migration Entscheidung",
  prompt: "Was wurde über die Database-Migration entschieden?"
})
```

---

## 5.9 Workspace Memory

### Agent-spezifisches Memory

Jeder Agent hat seinen eigenen Memory-Bereich:

```
~/.openclaw/agents/
├── ceo/
│   ├── memory/
│   │   ├── notes/          # Persönliche Notizen
│   │   ├── decisions/      # getroffene Entscheidungen
│   │   └── learnings/     # Lektionen
│   └── sessions/
├── builder/
│   └── memory/
└── security/
    └── memory/
```

### Memory-Dateien

| Verzeichnis | Inhalt |
|-------------|--------|
| `notes/` | Ad-hoc Notizen |
| `decisions/` | Wichtige Entscheidungen |
| `learnings/` | Fehler und Lektionen |

---

## 5.10 Best Practices

### DO's
```markdown
✅ IMPFE memory_search BEVOR du über Vergangenes redest
✅ SCHREIBE Checkpoints bei laufenden Tasks
✅ KOMPRIMIERE MEMORY.md wenn >500KB
✅ BENUTZE memory_get für gezielte Snippets
✅ PRÜFE memory/archive bei Recovery
```

### DON'Ts
```markdown
❌ ANTWORTE NICHT über Vergangenes ohne memory_search
❌ SPEICHERE nicht alles in MEMORY.md (nur das Wesentliche)
❌ IGNORIERE Checkpoints nicht bei laufenden Tasks
❌ DUPPLIZIERE nicht Informationen (once and only once)
```

---

## 📝 Zusammenfassung

| Konzept | Beschreibung |
|---------|--------------|
| MEMORY.md | Komprimierte Hauptgedächtnis-Datei |
| memory_search | Semantische Suche im Memory |
| memory_get | Gezielte Snippet-Lesung |
| Context Splitting | Verlust von Kontext bei langen Sessions |
| Checkpoint | Lösung gegen Context Splitting |
| LCM | Long-term Context Memory für Archive |

---

## ✅ Checkpoint

- [ ] Wie groß sollte MEMORY.md maximal sein?
- [ ] Was ist die richtige Pipeline BEVOR du über vergangene Events redest?
- [ ] Was ist Context Splitting und wie vermeidest du es?
- [ ] Was ist ein Checkpoint und wann schreibst du einen?
- [ ] Wie heißt das Tool für semantische Memory-Suche?

---

*Lektion 5 — Memory & Context Management — Version 1.0*
