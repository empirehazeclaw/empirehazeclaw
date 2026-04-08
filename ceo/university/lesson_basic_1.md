# Lektion 1: OpenClaw System-Architektur

## 🎯 Lernziel
Verstehe die grundlegende Architektur von OpenClaw — Gateway, Sessions, Tools, Channels und Memory. Dies ist das Fundament für alle weiteren Themen.

---

## 1.1 Gateway — Das Herzstück

Der **OpenClaw Gateway** ist der zentrale Dienst, der alle Komponenten verbindet.

### Gateway-Port
```
Standard-Port: 18789
Config-Befehl: openclaw gateway status
Start/Stop:    openclaw gateway start|stop|restart
```

### Gateway-Architektur
```
┌─────────────────────────────────────────────┐
│              OPENCLAW GATEWAY               │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Sessions│  │  Tools   │  │  Channels  │ │
│  │ Manager │  │  Router  │  │  Plugin    │ │
│  └─────────┘  └──────────┘  └───────────┘ │
│                                             │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Memory  │  │   Auth   │  │  Cron      │ │
│  │ Service │  │  Manager │  │  Scheduler │ │
│  └─────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
         │                │
         ▼                ▼
    ┌────────┐      ┌────────┐
    │  Agent  │      │  User  │
    │ Sessions│      │ Sessions│
    └────────┘      └────────┘
```

### Gateway Config (openclaw.json)
```json
{
  "gateway": {
    "port": 18789,
    "bind": "loopback",        // loopback|0.0.0.0|IP
    "auth": {
      "mode": "token"          // none|token|open
    }
  },
  "agents": { ... },
  "channels": { ... }
}
```

---

## 1.2 Sessions — Isolierte Arbeitsumgebungen

### Session-Typen

| Typ | Beschreibung | Persistenz |
|-----|--------------|------------|
| `main` | Hauptsession des Agents | Bleibt aktiv |
| `isolated` | Isolierte Einmal-Session | Temporär |
| `subagent` | Child-Process für parallele Tasks | Wird beendet nach Task |
| `acp` | ACP-Harness (z.B. Codex, Claude Code) | Je nach Modus |

### Session Lifecycle
```
START ──► INIT ──► RUNNING ──► IDLE ──► END
              │                    │
              ▼                    ▼
           ERROR              TIMEOUT
```

### Session-Keys
Sessions werden über eindeutige Keys identifiziert:
```
Format: agent:{agentId}:{channel}:{direction}:{chatId}
Beispiel: agent:builder:telegram:direct:5392634979
```

### Session-Namespace
```
agent:ceo:telegram:direct:5392634979   → CEO Session
agent:builder:telegram:direct:5392634979 → Builder Session
agent:security:telegram:direct:5392634979 → Security Officer
agent:data:telegram:direct:5392634979 → Data Manager
```

---

## 1.3 Tools — Die Fähigkeiten des Systems

### Wichtige Tools

| Tool | Funktion | Wichtig für |
|------|----------|-------------|
| `exec` | Shell-Befehle ausführen | Alles |
| `read` / `write` | Datei-Operationen | Alle Agenten |
| `sessions_send` | Nachricht an andere Session senden | Delegation |
| `sessions_list` | Aktive Sessions anzeigen | Debugging |
| `cron` | Geplante Tasks verwalten | Automation |
| `message` | Nachrichten senden (Telegram etc.) | Kommunikation |
| `subagents` | Sub-Agenten verwalten | Parallelisierung |
| `memory_search` | MEMORY.md durchsuchen | Recall |

### Tool-Zugriff einschränken
```json
{
  "agents": {
    "builder": {
      "tools": {
        "allow": ["exec", "read", "write", "edit", "sessions_send"],
        "deny": ["dangerous_tool"]
      }
    }
  }
}
```

---

## 1.4 Channels — Kommunikationswege

Channels verbinden das Gateway mit externen Diensten.

### Unterstützte Channels
```
telegram, signal, discord, slack, whatsapp,
messenger, irc, mattermost, matrix, nostr,
feishu, googlechat, msteams, nextcloud-talk,
synology-chat, tlon, bluebubbles, line, zalo
```

### Channel-Config
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "env:TELEGRAM_BOT_TOKEN"
    }
  }
}
```

---

## 1.5 Memory — Das Gedächtnis des Systems

### Memory-Struktur
```
~/.openclaw/
├── memory/
│   ├── MEMORY.md           # Hauptgedächtnis (Kurzfassung)
│   └── archive/            # Archivierte Erinnerungen
├── agents/{agent}/memory/  # Agent-spezifisches Memory
└── skills/                 # Skill-Dokumentation
```

### Memory-Regeln
1. **MEMORY.md** ist die Quelle der Wahrheit — komprimiert und aktuell
2. **Archive** enthält historische Daten
3. **memory_search** sucht semantic durch Memory
4. **memory_get** holt gezielte Snippets

---

## 1.6 Routing — Wer macht was?

### Der CEO als Orchestrator
```
NICO ──► CEO ──┬─► SECURITY OFFICER (Security-Themen)
               ├─► DATA MANAGER (Data/Memory-Themen)
               ├─► BUILDER (Coding/Implementation)
               ├─► RESEARCH (Recherche/Analyse)
               └─► QC OFFICER (Qualitätskontrolle)
```

### Routing-Entscheidungen
| Anfrage-Typ | Route zu |
|-------------|----------|
| Security Audit / Audit | Security Officer |
| Datenbank / Memory / Indexierung | Data Manager |
| Code / Scripts / APIs | Builder |
| Recherche / Analyse / Trends | Research |
| Qualitätskontrolle / Validierung | QC Officer |
| Strategie / Koordination / Zusammenfassung | CEO (selbst) |

---

## 🔍 Deep Dive: Gateway Boot-Prozess

```
1. Gateway startet auf Port 18789
2. Liest openclaw.json Konfiguration
3. Lädt Channel-Plugins
4. Initialisiert Session-Manager
5. Startet Cron-Scheduler
6. Registriert Agent-Workspaces
7. Gateway ist bereit für Anfragen
```

---

## ⚠️ Häufige Fehler

### Port bereits belegt
```bash
# Prüfe ob Gateway läuft
openclaw gateway status

# Port-Belegung prüfen
ss -tlnp | grep 18789
```

### Config-Fehler
```bash
# Validiere Config
openclaw doctor --check

# Repariere automatisch
openclaw doctor --fix
```

---

## 📝 Zusammenfassung

| Komponente | Funktion | Key-Facts |
|------------|----------|-----------|
| Gateway | Zentraler Dienst | Port 18789, restartbar |
| Sessions | Isolierte Umgebungen | main, isolated, subagent |
| Tools | Fähigkeiten | exec, read, write, sessions_send |
| Channels | Kommunikation | Telegram, Discord, etc. |
| Memory | Gedächtnis | MEMORY.md, archive |
| Routing | Delegation | CEO orchestriert alle |

---

## ✅ Checkpoint

Bevor du zur nächsten Lektion gehst, stelle sicher dass du weißt:

- [ ] Welchen Port nutzt das Gateway standardmäßig?
- [ ] Was ist der Unterschied zwischen `main` und `isolated` Session?
- [ ] Welches Tool nutzt man um Nachrichten zwischen Agents zu senden?
- [ ] Wer ist der zentrale Orchestrator in der Flotte?
- [ ] Was ist die Haupt-Memory-Datei und wo liegt sie?

---

*Lektion 1 — System-Architektur — Version 1.0*
